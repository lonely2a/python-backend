"""认证API - 处理用户登录登出"""
from fastapi import APIRouter, HTTPException, Response
from app.models.schemas import LoginRequest, LoginResponse, LogoutResponse
from app.services.mt5_service import mt5_service
from app.core.security import create_access_token
from loguru import logger

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, response: Response):
    """
    登录并连接MT5账户

    Args:
        request: 登录请求(账号、密码、服务器)
        response: FastAPI响应对象（用于设置Cookie）

    Returns:
        LoginResponse: 登录结果
    """
    try:
        # 连接MT5账户
        account_info = await mt5_service.connect(
            login=request.login,
            password=request.password,
            server=request.server
        )

        # 生成JWT Token
        token_data = {
            "sub": str(request.login),
            "server": request.server
        }
        access_token = create_access_token(data=token_data)

        # 设置httpOnly Cookie（更安全，防止XSS攻击）
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,      # JavaScript无法读取
            secure=False,       # 开发环境设为False，生产环境设为True（需要HTTPS）
            samesite="lax",     # 防止CSRF攻击
            max_age=86400,      # 24小时过期
            path="/api"         # 只在/api路径下发送Cookie
        )

        logger.info(f"用户登录成功: {request.login}")

        return LoginResponse(
            success=True,
            session_token=access_token,  # 仍然返回token供前端调试
            message="登录成功",
            account_info=account_info
        )

    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout", response_model=LogoutResponse)
async def logout(login: int):
    """
    断开MT5连接

    Args:
        login: MT5账号

    Returns:
        LogoutResponse: 登出结果
    """
    try:
        success = await mt5_service.disconnect(login)

        if success:
            return LogoutResponse(
                success=True,
                message="已断开连接"
            )
        else:
            return LogoutResponse(
                success=False,
                message="账户未连接"
            )

    except Exception as e:
        logger.error(f"登出失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
