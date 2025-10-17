import bcrypt

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload
from sqlalchemy_crud_plus import CRUDPlus

from backend.app.admin.model.user import User
from backend.app.admin.schema.user import UserListQueryParams, UserRegisterParams, UserUpdateParams
from backend.common.security.jwt import get_hash_password
from backend.utils.timezone import timezone


class UserCRUD(CRUDPlus[User]):
    async def get(self, db: AsyncSession, pk: int) -> User | None:
        """根据 pk 获取用户详情"""
        return await self.select_model(db, pk)

    async def get_by_column(self, db: AsyncSession, column: str, value: str):
        """根据指定列名和值获取 详情"""
        return await self.select_model_by_column(db, **{column: value})  # type: ignore

    async def register_by_username(self, db: AsyncSession, params: UserRegisterParams):
        """根据用户名、密码创建用户"""
        salt = bcrypt.gensalt()
        params.password = get_hash_password(params.password, salt)

        dict_params = params.model_dump()
        dict_params.update({'username': params.username, 'nickname': params.username, 'salt': salt})

        user = self.model(**dict_params)
        db.add(user)

    async def get_list_select(self, params: UserListQueryParams) -> Select:
        """获取用户列表"""
        filters = {}

        for field in ['username', 'nickname', 'email']:
            value = getattr(params, field, None)
            if value:
                filters[f'{field}__like'] = f'%{value}%'

        for field in ['phone', 'is_verified', 'gender', 'is_staff']:
            value = getattr(params, field, None)
            if value is not None:
                filters[field] = value

        # 使用 noload 避免自动加载关系字段，防止 greenlet 错误
        stmt = await self.select_order('id', 'asc', **filters)
        return stmt.options(noload(User.socials))

    async def delete(self, db: AsyncSession, pk: int) -> int:
        """删除用户"""
        return await self.delete_model(db, pk)

    async def update(self, db: AsyncSession, pk: int, params: UserUpdateParams) -> int:
        """更新用户信息"""
        # 获取需要更新的字段，排除 None 值
        update_data = {}

        # 定义允许更新的字段
        updateable_fields = [
            'username',
            'nickname',
            'email',
            'phone',
            'realname',
            'avatar',
            'gender',
            'birth_date',
            'status',
            'is_verified',
            'is_multi_login',
            'is_staff',
        ]

        for field in updateable_fields:
            value = getattr(params, field, None)
            if value is not None:
                update_data[field] = value

        # 处理密码更新
        if params.password is not None:
            salt = bcrypt.gensalt()
            hashed_password = get_hash_password(params.password, salt)
            update_data['password'] = hashed_password
            update_data['salt'] = salt

        if not update_data:
            return 0

        return await self.update_model(db, pk, update_data)

    async def update_login_time(self, db: AsyncSession, username: str) -> int:
        """
        更新用户最后登录时间

        :param db: 数据库会话
        :param username: 用户名
        :return:
        """
        return await self.update_model_by_column(db, {'last_login_time': timezone.now()}, username=username)


user_crud = UserCRUD(User)
