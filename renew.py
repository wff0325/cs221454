import os
import time
import logging
from seleniumbase import SB

# 日志设置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 明文配置区 ---
PROXY_ADDRESS = "127.0.0.1:8080" # 对应上面YAML里启动的本地转发
MY_ACCOUNT = "vbfgh@431234.xyz"
MY_PASSWORD = "Qwer123456"
SERVER_ID = "f715280f"
# ----------------

def run_fgh_test():
    logger.info(f"🚀 开始测试续费脚本 - 账号: {MY_ACCOUNT}")

    # 使用 UC 模式绕过 Cloudflare 检测
    with SB(uc=True, headless=True, proxy=PROXY_ADDRESS) as sb:
        try:
            # 1. 登录
            sb.open("https://panel.freegamehost.xyz/auth/login")
            logger.info("页面已打开，正在检测登录框...")
            time.sleep(5)
            
            if sb.is_element_visible('input[name="username"]'):
                sb.type('input[name="username"]', MY_ACCOUNT)
                sb.type('input[name="password"]', MY_PASSWORD)
                sb.click('button[type="submit"]')
                logger.info("已点击登录，等待跳转...")
                time.sleep(10)
            
            # 2. 进入控制台
            target_url = f"https://panel.freegamehost.xyz/server/{SERVER_ID}"
            sb.open(target_url)
            logger.info(f"正在跳转到服务器控制台: {target_url}")
            time.sleep(12) # 网页加载较慢

            # 3. 检查倒计时 (截图确认)
            timer_selector = "div[class*='RenewBox__TimerDigits']"
            if sb.is_element_visible(timer_selector):
                logger.info(f"⏳ 成功读取倒计时: {sb.get_text(timer_selector)}")
            
            # 4. 续费点击逻辑
            renew_btn = "button:contains('Renew')"
            cooldown_text = "RENEWAL COOLDOWN"

            if sb.is_element_visible(renew_btn):
                logger.info("🎯 发现 Renew 按钮！正在执行点击...")
                sb.click(renew_btn)
                time.sleep(3)
                
                # 如果有弹窗确认按钮
                if sb.is_text_visible("Confirm", "button"):
                    sb.click("button:contains('Confirm')")
                    time.sleep(2)
                
                logger.info("✅ 续费指令发送完毕！")
                sb.save_screenshot("test_success.png")
            elif sb.is_text_visible(cooldown_text):
                logger.info("ℹ️ 状态: 处于冷却期 (Cooldown)，无法续费，属于正常现象。")
                sb.save_screenshot("test_cooldown.png")
            else:
                logger.warning("⚠️ 状态不明: 既没看到按钮也没看到冷却文字。")
                sb.save_screenshot("test_unknown_check_me.png")

        except Exception as e:
            logger.error(f"❌ 运行中发生错误: {str(e)}")
            sb.save_screenshot("test_error.png")

if __name__ == "__main__":
    run_fgh_test()
