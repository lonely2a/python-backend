"""测试MT5登录脚本"""
import asyncio
from app.services.mt5_service import mt5_service

async def test_login():
    """测试登录功能"""
    print("=" * 50)
    print("MT5登录测试")
    print("=" * 50)
    
    # 请输入你的测试账户信息
    login = input("MT5账号: ")
    password = input("交易密码: ")
    server = input("服务器 (例如 Exness-Real16): ")
    
    try:
        login_num = int(login)
    except ValueError:
        print("❌ 错误：MT5账号必须是数字")
        return
    
    print(f"\n正在连接 {login} @ {server} ...")
    
    try:
        result = await mt5_service.connect(
            login=login_num,
            password=password,
            server=server
        )
        
        print("\n✅ 登录成功！")
        print(f"账户余额: ${result['balance']:.2f}")
        print(f"账户净值: ${result['equity']:.2f}")
        print(f"杠杆比例: 1:{result['leverage']}")
        
    except Exception as e:
        print(f"\n❌ 登录失败: {str(e)}")
        print("\n可能的原因:")
        print("1. MT5终端未安装或未启动")
        print("2. 服务器名称填写错误")
        print("3. 密码错误（注意：需要使用交易密码，不是投资者密码）")
        print("4. 网络连接问题")

if __name__ == "__main__":
    asyncio.run(test_login())
