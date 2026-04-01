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
    logger.info(f"🚀 开始登录流程: {USER_EMAIL}")

    # 使用 SeleniumBase UC 模式
    with SB(uc=True, headless=True, proxy=PROXY_ADDR) as sb:
        try:
            # 1. 访问登录页
            sb.open("https://panel.freegamehost.xyz/auth/login")
            time.sleep(8) # 等待 Cloudflare 和 验证码加载
            
            # 尝试处理可能存在的验证码 (UC模式特有)
            if sb.is_captcha_present():
                logger.info("发现验证码，尝试自动绕过...")
                sb.uc_gui_click_captcha()
                time.sleep(5)

            # 输入账号密码
            if sb.is_element_visible('input[name="username"]'):
                logger.info("正在输入账号密码...")
                sb.type('input[name="username"]', USER_EMAIL)
                sb.type('input[name="password"]', USER_PASS)
                
                # 点击登录并等待
                sb.click('button[type="submit"]')
                logger.info("已点击登录，等待跳转至仪表盘...")
                time.sleep(15) # 登录跳转通常比较慢

            # --- 关键：验证是否真的登录成功了 ---
            # 检查 URL 是否还包含 /login，或者是否存在登出按钮
            current_url = sb.get_current_url()
            if "login" in current_url:
                logger.error("❌ 登录失败！仍然停留在登录页面。")
                sb.save_screenshot("login_failed_stayed_at_login.png")
                # 尝试再次强制点击一下登录（有时候第一次点击无效）
                if sb.is_element_visible('button[type="submit"]'):
                    sb.click('button[type="submit"]')
                    time.sleep(10)
            
            # 2. 只有登录成功才跳转控制台
            console_url = f"https://panel.freegamehost.xyz/server/{SERVER_ID}"
            sb.open(console_url)
            logger.info(f"正在跳转到服务器控制台: {console_url}")
            time.sleep(15) # 翼龙面板加载后端数据非常慢

            # 再次检查是否被踢回登录页
            if "login" in sb.get_current_url():
                logger.error("❌ 跳转失败！被重定向回了登录页，可能是Session未生效。")
                sb.save_screenshot("redirected_back_to_login.png")
                return

            # 3. 检查续费按钮
            timer_selector = "div[class*='RenewBox__TimerDigits']"
            renew_btn = "button:contains('Renew')"
            cooldown_text = "RENEWAL COOLDOWN"

            if sb.is_element_visible(timer_selector):
                logger.info(f"⏳ 成功识别倒计时: {sb.get_text(timer_selector)}")

            if sb.is_element_visible(renew_btn):
                logger.info("🎯 发现 Renew 按钮，开始点击...")
                sb.click(renew_btn)
                time.sleep(5)
                
                # 检查确认弹窗
                if sb.is_text_visible("Confirm", "button"):
                    sb.click("button:contains('Confirm')")
                    time.sleep(3)
                
                logger.info("✅ 续费流程已触发！")
                sb.save_screenshot("success_renew.png")
            elif sb.is_text_visible(cooldown_text):
                logger.info("ℹ️ 状态提示：仍在冷却中 (Cooldown)。")
                sb.save_screenshot("cooldown_status.png")
            else:
                logger.warning("⚠️ 状态不明：没看到按钮也没看到冷却文字。")
                sb.save_screenshot("unknown_status_debug.png")

        except Exception as e:
            logger.error(f"❌ 运行报错: {str(e)}")
            sb.save_screenshot("critical_error.png")

if __name__ == "__main__":
    run_test()
