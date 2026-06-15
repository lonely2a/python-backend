"""API测试脚本 - 用于验证后端接口功能"""
import httpx
import asyncio


# API基础URL
BASE_URL = "http://localhost:8000"


def test_health_check():
    """测试健康检查接口"""
    print("\n=== 测试健康检查 ===")
    response = httpx.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print(f"✅ 健康检查通过: {response.json()}")


def test_root():
    """测试根路径"""
    print("\n=== 测试根路径 ===")
    response = httpx.get(f"{BASE_URL}/")
    assert response.status_code == 200
    print(f"✅ 根路径访问成功: {response.json()}")


async def test_login_and_trade(login: int, password: str, server: str):
    """
    测试完整的交易流程

    Args:
        login: MT5账号
        password: MT5密码
        server: Exness服务器
    """
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        try:
            # 1. 登录
            print("\n=== 测试登录 ===")
            login_response = await client.post(
                "/api/auth/login",
                json={
                    "login": login,
                    "password": password,
                    "server": server
                }
            )
            assert login_response.status_code == 200
            login_data = login_response.json()
            assert login_data["success"] == True
            token = login_data["session_token"]
            print(f"✅ 登录成功, Token: {token[:50]}...")
            print(f"   账户信息: {login_data['account_info']}")

            # 2. 获取账户信息
            print("\n=== 测试获取账户信息 ===")
            account_response = await client.get(
                "/api/account/info",
                params={"login": login},
                headers={"Authorization": f"Bearer {token}"}
            )
            assert account_response.status_code == 200
            account_info = account_response.json()
            print(f"✅ 账户信息获取成功:")
            print(f"   余额: {account_info['balance']}")
            print(f"   净值: {account_info['equity']}")
            print(f"   杠杆: 1:{account_info['leverage']}")

            # 3. 获取持仓列表
            print("\n=== 测试获取持仓 ===")
            positions_response = await client.get(
                "/api/account/positions",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert positions_response.status_code == 200
            positions_data = positions_response.json()
            print(f"✅ 持仓列表获取成功, 当前持仓数: {len(positions_data['positions'])}")

            # 4. 获取品种列表
            print("\n=== 测试获取品种列表 ===")
            symbols_response = await client.get("/api/market/symbols")
            assert symbols_response.status_code == 200
            symbols_data = symbols_response.json()
            print(f"✅ 品种列表获取成功, 可交易品种数: {len(symbols_data['symbols'])}")
            if symbols_data['symbols']:
                print(f"   第一个品种: {symbols_data['symbols'][0]['name']}")

            # 5. 获取实时报价
            print("\n=== 测试获取报价 ===")
            quote_response = await client.get("/api/market/quote/EURUSD")
            assert quote_response.status_code == 200
            quote_data = quote_response.json()
            print(f"✅ EURUSD报价获取成功:")
            print(f"   Bid: {quote_data['bid']}")
            print(f"   Ask: {quote_data['ask']}")

            # 6. 执行买入操作 (可选,需要确认是否真的下单)
            print("\n=== 测试下单功能 ===")
            print("⚠️  注意: 这将实际执行交易操作!")
            confirm = input("是否在Demo账户执行测试下单? (yes/no): ")
            
            if confirm.lower() == "yes":
                order_response = await client.post(
                    "/api/trade/place-order",
                    json={
                        "symbol": "EURUSD",
                        "type": "BUY",
                        "volume": 0.01,
                        "sl_points": 50,
                        "tp_points": 100,
                        "comment": "Test Order"
                    },
                    headers={"Authorization": f"Bearer {token}"}
                )
                assert order_response.status_code == 200
                order_data = order_response.json()
                print(f"✅ 下单成功:")
                print(f"   Order ID: {order_data['order_id']}")
                print(f"   Deal ID: {order_data['deal_id']}")
                print(f"   价格: {order_data['price']}")
                
                # 7. 平仓 (如果下单成功)
                print("\n=== 测试平仓功能 ===")
                close_response = await client.post(
                    "/api/trade/close-position",
                    json={"ticket": order_data['order_id']},
                    headers={"Authorization": f"Bearer {token}"}
                )
                assert close_response.status_code == 200
                close_data = close_response.json()
                print(f"✅ 平仓成功: {close_data['message']}")
            else:
                print("️  跳过下单测试")

            # 8. 登出
            print("\n=== 测试登出 ===")
            logout_response = await client.post(
                "/api/auth/logout",
                params={"login": login},
                headers={"Authorization": f"Bearer {token}"}
            )
            assert logout_response.status_code == 200
            print(f"✅ 登出成功")

            print("\n" + "=" * 50)
            print("🎉 所有测试通过!")
            print("=" * 50)

        except AssertionError as e:
            print(f"\n❌ 测试失败: {str(e)}")
            raise
        except Exception as e:
            print(f"\n❌ 测试异常: {str(e)}")
            raise


if __name__ == "__main__":
    import sys
    
    print("=" * 50)
    print("Exness Trading Backend API 测试工具")
    print("=" * 50)
    
    # 先运行基础测试
    try:
        test_health_check()
        test_root()
    except Exception as e:
        print(f"\n❌ 基础服务未启动,请先运行: python main.py")
        sys.exit(1)
    
    # 询问是否进行完整测试
    print("\n是否进行完整的API测试? (需要Exness Demo账户)")
    print("提示: 请在 .env 文件中配置正确的MT5环境")
    
    run_full_test = input("开始完整测试? (yes/no): ")
    
    if run_full_test.lower() == "yes":
        print("\n请输入Exness Demo账户信息:")
        login = int(input("账号 (login): "))
        password = input("密码 (password): ")
        server = input("服务器 (如 Exness-Demo): ")
        
        print("\n开始测试...")
        asyncio.run(test_login_and_trade(login, password, server))
    else:
        print("\n✅ 基础测试完成,跳过完整测试")
