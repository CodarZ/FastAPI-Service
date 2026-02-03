import bcrypt

from sqlalchemy import select

from backend.app.admin.model import SysRole, SysUser
from backend.common.log import log
from backend.common.security.password import get_hashed_password
from backend.core.config import settings
from backend.database.postgresql import async_session


async def init_superuser() -> None:
    """创建初始超级管理员用户

    检查逻辑：
    1. 如果配置的用户名已存在，跳过创建
    2. 如果不存在，创建新的超级管理员用户
    3. 自动创建"超级管理员"角色并关联
    """
    try:
        async with async_session() as db:
            # 检查用户是否已存在
            stmt = select(SysUser).where(SysUser.username == settings.INIT_SUPERUSER_USERNAME)
            result = await db.execute(stmt)
            existing_user = result.scalar_one_or_none()

            if existing_user:
                log.info(f'✅ 初始超级管理员已存在: {settings.INIT_SUPERUSER_USERNAME} (ID: {existing_user.id})')
                return

            # 检查或创建超级管理员角色
            SUPER_ROLE_CODE = 'super_admin'
            role_stmt = select(SysRole).where(SysRole.code == SUPER_ROLE_CODE)
            role_result = await db.execute(role_stmt)
            superadmin_role = role_result.scalar_one_or_none()

            if not superadmin_role:
                # 创建超级管理员角色
                superadmin_role = SysRole(
                    name='超级管理员',
                    code=SUPER_ROLE_CODE,
                    data_scope=0,  # 全部数据权限
                    status=1,
                    remark='系统默认超级管理员角色，拥有所有权限',
                )
                db.add(superadmin_role)
                await db.flush()
                log.info(f'✅ 创建超级管理员角色: {SUPER_ROLE_CODE} (ID: {superadmin_role.id})')

            # 生成密码盐和哈希密码
            salt = bcrypt.gensalt()
            hashed_password = get_hashed_password(settings.INIT_SUPERUSER_PASSWORD, salt)

            # 创建超级管理员用户
            superuser = SysUser(
                username=settings.INIT_SUPERUSER_USERNAME,
                password=hashed_password,
                salt=salt,
                nickname=settings.INIT_SUPERUSER_NICKNAME,
                realname=None,
                email=settings.INIT_SUPERUSER_EMAIL,
                phone=settings.INIT_SUPERUSER_PHONE,
                avatar=None,
                gender=None,
                birth_date=None,
                dept_id=None,
                status=1,
                is_superuser=True,
                is_admin=True,
                is_multi_login=True,
                remark='系统初始化创建的超级管理员账号',
            )

            # 关联超级管理员角色
            superuser.roles.append(superadmin_role)

            db.add(superuser)
            await db.commit()
            await db.refresh(superuser)

            log.success(f'✅ 初始超级管理员创建成功: {settings.INIT_SUPERUSER_USERNAME} (ID: {superuser.id})')
            log.info(
                f'📌 登录凭据 (请尽快修改默认密码！) \n'
                f'👉 用户名: {settings.INIT_SUPERUSER_USERNAME}, '
                f'🔒 密码: {settings.INIT_SUPERUSER_PASSWORD} '
            )

    except Exception as e:
        log.error(f'❌ 初始超级管理员创建失败: {e}')
        # 不阻断应用启动，仅记录错误
        raise


async def init_database_data() -> None:
    """初始化数据库数据（应用启动时调用）"""
    log.info('🚀 开始初始化数据库数据...')

    try:
        # 创建初始超级管理员
        await init_superuser()

        # 这里可以添加其他初始化数据的函数
        # await init_default_menus()
        # await init_default_depts()

        log.success('✅ 数据库数据初始化完成')
    except Exception as e:
        log.error(f'❌ 数据库数据初始化失败: {e}')
        # 根据需要决定是否抛出异常阻断启动
        # raise
