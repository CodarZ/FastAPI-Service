from fastapi import BackgroundTasks, Request, Response
from fastapi.security import HTTPBasicCredentials
from starlette.background import BackgroundTask

from backend.app.admin.crud.user import user_crud
from backend.app.admin.model.user import User
from backend.app.admin.schema.login_log import LoginLogCreateParams
from backend.app.admin.schema.token import AuthLoginParams, AuthLoginToken
from backend.app.admin.schema.user import UserDetail
from backend.app.admin.service.login_log import login_log_service
from backend.common.enum.custom import LoginLogStatusEnum
from backend.common.exception import errors
from backend.common.log import log
from backend.common.response.code import CustomErrorCode
from backend.common.security.jwt import create_access_token, create_refresh_token, verify_password
from backend.core.config import settings
from backend.database.postgresql import AsyncSession, async_db_session
from backend.database.redis import redis_client
from backend.utils.timezone import timezone


class AuthService:
    @staticmethod
    async def user_verify(db: AsyncSession, username: str, password: str) -> User:
        user = await user_crud.get_by_column(db, 'username', username)

        if not user:
            raise errors.NotFoundError(msg='用户不存在')

        if user.password is None:
            raise errors.AuthorizationError(msg='该用户没有设置密码')
        if not verify_password(password, user.password):
            raise errors.AuthorizationError(msg='用户名或密码有误')

        if not user.status:
            raise errors.AuthorizationError(msg='用户已被锁定, 请联系统管理员')

        return user

    async def swagger_login(self, *, params: HTTPBasicCredentials) -> tuple[str, User]:
        async with async_db_session.begin() as db:
            user = await self.user_verify(db, params.username, params.password)
            await user_crud.update_login_time(db, params.username)
            access_token = await create_access_token(
                user.id,
                multi_login=user.is_multi_login,
                # extra info
                swagger=True,
            )
            return access_token.access_token, user

    async def login(
        self, *, request: Request, response: Response, params: AuthLoginParams, background_tasks: BackgroundTasks
    ) -> AuthLoginToken:
        async with async_db_session.begin() as db:
            user = None

            try:
                user = await self.user_verify(db, params.username, params.password)

                # 验证码
                captcha_code = await redis_client.get(f'{settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{params.uuid}')
                if not captcha_code:
                    raise errors.RequestError(msg='验证码已经过期')
                if captcha_code.lower() != params.captcha.lower():
                    raise errors.CustomError(error=CustomErrorCode.CAPTCHA_ERROR)
                await redis_client.delete(f'{settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{params.uuid}')

                await user_crud.update_login_time(db, user.username)
                await db.refresh(user)
                access_token = await create_access_token(
                    user.id,
                    multi_login=user.is_multi_login,
                    # extra info
                    username=user.username,
                    nickname=user.nickname,
                    last_login_time=timezone.to_str(user.last_login_time) if user.last_login_time else None,
                    # ip=request.state.ip if request.state.ip else None,
                    os=request.state.os,
                    browser=request.state.browser,
                    device=request.state.device,
                )

                refresh_token = await create_refresh_token(
                    access_token.session_uuid,
                    user.id,
                    multi_login=user.is_multi_login,
                )

                response.set_cookie(
                    key=settings.COOKIE_REFRESH_TOKEN_KEY,
                    value=refresh_token.refresh_token,
                    max_age=settings.COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS,
                    expires=timezone.to_utc(refresh_token.expire_time),
                    httponly=True,
                )
            except Exception as e:
                # 根据异常类型记录不同的错误信息
                if isinstance(e, errors.NotFoundError):
                    error_msg = e.msg if e.msg else '用户不存在'
                elif isinstance(e, (errors.RequestError, errors.CustomError)):
                    error_msg = e.msg if e.msg else '用户密码错误'
                elif isinstance(e, (errors.AuthorizationError)):
                    error_msg = e.msg if e.msg else '用户未授权'
                else:
                    log.error(f'登陆未知错误: {e}')
                    error_msg = '登录失败，请稍后重试'

                # 统一创建登录日志记录任务
                task_params = LoginLogCreateParams(
                    username=params.username,
                    user_uuid=user.uuid if user else None,
                    status=LoginLogStatusEnum.FAIL,
                    ip=request.state.ip,
                    country=request.state.country,
                    region=request.state.region,
                    city=request.state.city,
                    user_agent=request.state.user_agent if request.state.user_agent else None,
                    browser=request.state.browser if request.state.browser else None,
                    os=request.state.os if request.state.os else None,
                    device=request.state.device if request.state.device else None,
                    login_time=timezone.now(),
                    msg=error_msg,
                )
                task = BackgroundTask(login_log_service.create, params=task_params)

                # 根据异常类型抛出相应的错误
                if isinstance(e, errors.NotFoundError):
                    raise errors.NotFoundError(msg=error_msg, background=task)
                elif isinstance(e, (errors.RequestError, errors.CustomError)):
                    raise errors.RequestError(msg=error_msg, background=task)
                else:
                    # 对于其他未知异常，使用 RequestError 并带上 task
                    raise errors.RequestError(msg=error_msg, background=task)

            else:
                task_params = LoginLogCreateParams(
                    username=params.username,
                    user_uuid=user.uuid,
                    status=LoginLogStatusEnum.SUCCESS,
                    ip=request.state.ip,
                    country=request.state.country,
                    region=request.state.region,
                    city=request.state.city,
                    user_agent=request.state.user_agent if request.state.user_agent else None,
                    browser=request.state.browser if request.state.browser else None,
                    os=request.state.os if request.state.os else None,
                    device=request.state.device if request.state.device else None,
                    login_time=timezone.now(),
                    msg='登录成功！',
                )
                background_tasks.add_task(login_log_service.create, params=task_params)

                data = AuthLoginToken(
                    access_token=access_token.access_token,
                    expire_time=access_token.expire_time,
                    session_uuid=access_token.session_uuid,
                    user=UserDetail.model_validate(user),
                )
                return data

    @staticmethod
    async def logout(*, request: Request, response: Response):
        pass


auth_service: AuthService = AuthService()
