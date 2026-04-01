import os
import time
import logging
from seleniumbase import SB

# 日志设置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_renewal():
    # 获取变量: "email#password#serverid"
    account_data = os.getenv("FGH_ACCOUNT")
    gost_proxy = os.getenv("GOST_PROXY")
    
    if not account_data:
        logger.error("❌ 错误: 未设置 FGH_ACCOUNT Secret")
        return

    # 如果配置了 GOST，使用本地映射的 8080 端口
    proxy = "127.0.0.1:8080" if gost_proxy else None
    accounts = account_data.split(",")

    # 使用 UC 模式 (Undetected Chromedriver) 绕过 CF 验证
    with SB(uc=True, headless=True, proxy=proxy) as sb:
        for entry in accounts:
            try:
                if "#" not in entry: continue
                email, password, server_id = entry.split("#")
                
                logger.info(f"--- 启动任务: {email} (ID: {server_id}) ---")

                # 1. 登录
                sb.open("https://panel.freegamehost.xyz/auth/login")
                time.sleep(3)
                
                if sb.is_element_visible('input[name="username"]'):
                    sb.type('input[name="username"]', email)
                    sb.type('input[name="password"]', password)
                    sb.click('button[type="submit"]')
                    time.sleep(6)
                
                # 2. 直接访问服务器控制台
                sb.open(f"https://panel.freegamehost.xyz/server/{server_id}")
                logger.info("正在加载控制台页面...")
                time.sleep(10) # 翼龙面板加载数据较慢

                # 3. 检查倒计时 (针对你提供的 HTML class)
                timer_el = "div[class*='RenewBox__TimerDigits']"
                if sb.is_element_visible(timer_el):
                    current_time = sb.get_text(timer_el)
                    logger.info(f"⏳ 当前剩余时间: {current_time}")

                # 4. 续费逻辑
                # 寻找包含 "Renew" 字样的按钮 (XPath 或 CSS)
                renew_btn = "button:contains('Renew')"
                cooldown_msg = "RENEWAL COOLDOWN"

                if sb.is_element_visible(renew_btn):
                    logger.info("🎯 发现续费按钮，开始点击...")
                    sb.click(renew_btn)
                    time.sleep(3)
                    
                    # 检查是否有确认弹窗 (Confirm)
                    if sb.is_text_visible("Confirm", "button"):
                        sb.click("button:contains('Confirm')")
                        time.sleep(2)
                    
                    logger.info("✅ 续费操作已完成！")
                    sb.save_screenshot(f"success_{server_id}.png")
                elif sb.is_text_visible(cooldown_msg):
                    logger.info("ℹ️ 提示: 续费尚在冷却中，跳过本次执行。")
                else:
                    logger.warning("⚠️ 未识别到续费按钮，请检查截图。")
                    sb.save_screenshot(f"check_{server_id}.png")

            except Exception as e:
                logger.error(f"❌ 运行异常: {str(e)}")
                sb.save_screenshot(f"error_{server_id}.png")

if __name__ == "__main__":
    run_renewal()
