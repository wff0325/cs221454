import time
import logging
from seleniumbase import SB

# 日志设置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 明文配置区 ---
PROXY_ADDR = "127.0.0.1:8080"
USER_EMAIL = "vbfgh@431234.xyz"
USER_PASS  = "Qwer123456"
SERVER_ID  = "f715280f"
# ------------------

def run_test():
    logger.info(f"🚀 开始执行续费脚本: {USER_EMAIL}")

    # 使用 UC 模式
    with SB(uc=True, headless=True, proxy=PROXY_ADDR) as sb:
        try:
            # 1. 访问登录页
            sb.open("https://panel.freegamehost.xyz/auth/login")
            time.sleep(10)

            # 2. 检测并尝试解决 reCAPTCHA
            # 如果页面上有 reCAPTCHA 框架，尝试自动破解
            if sb.is_element_visible('iframe[src*="recaptcha"]'):
                logger.info("🛡️ 发现 reCAPTCHA 验证码，尝试破解...")
                try:
                    sb.activate_recaptcha_solver()
                    logger.info("✅ 验证码识别尝试完成")
                    time.sleep(5)
                except Exception as ex:
                    logger.warning(f"⚠️ 验证码识别器报错 (可能IP被锁): {ex}")

            # 3. 输入账号密码
            if sb.is_element_visible('input[name="username"]'):
                logger.info("正在输入账号密码...")
                sb.type('input[name="username"]', USER_EMAIL)
                sb.type('input[name="password"]', USER_PASS)
                
                # 点击登录
                sb.click('button[type="submit"]')
                logger.info("已提交登录，正在等待跳转...")
                time.sleep(15)

            # 4. 再次检查是否被验证码卡住
            if "login" in sb.get_current_url():
                logger.warning("仍然在登录页，可能需要第二次处理验证码挑战...")
                sb.save_screenshot("login_challenge.png")
                # 如果出现了图片挑战框，尝试再次调用 solver
                try:
                    sb.activate_recaptcha_solver()
                    time.sleep(5)
                    sb.click('button[type="submit"]')
                    time.sleep(10)
                except:
                    pass

            # 5. 跳转控制台
            console_url = f"https://panel.freegamehost.xyz/server/{SERVER_ID}"
            sb.open(console_url)
            time.sleep(15)
            sb.save_screenshot("after_login_attempt.png")

            # 6. 续费逻辑
            timer_selector = "div[class*='RenewBox__TimerDigits']"
            renew_btn = "button:contains('Renew')"
            cooldown_text = "RENEWAL COOLDOWN"

            if sb.is_element_visible(timer_selector):
                logger.info(f"⏳ 剩余时间: {sb.get_text(timer_selector)}")

            if sb.is_element_visible(renew_btn):
                logger.info("🎯 发现 Renew 按钮，执行续费...")
                sb.uc_click(renew_btn)
                time.sleep(5)
                if sb.is_text_visible("Confirm", "button"):
                    sb.click("button:contains('Confirm')")
                    time.sleep(3)
                logger.info("✅ 续费操作成功！")
                sb.save_screenshot("renew_ok.png")
            elif sb.is_text_visible(cooldown_text):
                logger.info("ℹ️ 状态: 冷却中，无需操作。")
            else:
                logger.warning("⚠️ 无法识别状态。")

        except Exception as e:
            logger.error(f"❌ 错误: {str(e)}")
            sb.save_screenshot("error_final.png")

if __name__ == "__main__":
    run_test()
