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
            # UC模式下，sb.open会自动尝试处理Cloudflare等待页
            sb.open("https://panel.freegamehost.xyz/auth/login")
            time.sleep(10) # 留足时间让页面和验证码加载

            # 2. 输入账号密码
            if sb.is_element_visible('input[name="username"]'):
                logger.info("正在输入账号密码...")
                sb.type('input[name="username"]', USER_EMAIL)
                sb.type('input[name="password"]', USER_PASS)
                
                # 使用 uc_click (模拟真人点击) 替代普通 click，防止被识别
                login_btn = 'button[type="submit"]'
                if sb.is_element_visible(login_btn):
                    logger.info("点击登录按钮...")
                    sb.uc_click(login_btn)
                else:
                    # 如果找不到按钮，尝试回车登录
                    sb.press_keys('input[name="password"]', '\n')
                
                time.sleep(15) # 登录跳转通常比较慢

            # --- 验证是否登录成功 ---
            current_url = sb.get_current_url()
            logger.info(f"当前页面URL: {current_url}")
            
            if "login" in current_url:
                logger.warning("⚠️ 仍然在登录页面，尝试第二次强制登录...")
                sb.save_screenshot("login_retry.png")
                sb.type('input[name="password"]', USER_PASS)
                sb.click('button[type="submit"]')
                time.sleep(10)

            # 3. 跳转到服务器控制台
            console_url = f"https://panel.freegamehost.xyz/server/{SERVER_ID}"
            sb.open(console_url)
            logger.info(f"正在跳转到控制台: {console_url}")
            time.sleep(15) # 翼龙面板后台数据加载较慢

            # 保存一张控制台的截图，确认是否进去了
            sb.save_screenshot("console_page.png")

            # 4. 检查续费逻辑
            timer_selector = "div[class*='RenewBox__TimerDigits']"
            renew_btn = "button:contains('Renew')"
            cooldown_text = "RENEWAL COOLDOWN"

            # 尝试抓取倒计时
            if sb.is_element_visible(timer_selector):
                time_val = sb.get_text(timer_selector)
                logger.info(f"⏳ 成功识别倒计时: {time_val}")

            # 寻找并点击续费
            if sb.is_element_visible(renew_btn):
                logger.info("🎯 发现 Renew 按钮，开始点击...")
                sb.uc_click(renew_btn) # 使用模拟真人点击
                time.sleep(5)
                
                # 检查确认弹窗
                if sb.is_text_visible("Confirm", "button"):
                    sb.click("button:contains('Confirm')")
                    time.sleep(3)
                
                logger.info("✅ 续费流程已触发！")
                sb.save_screenshot("success_final.png")
            elif sb.is_text_visible(cooldown_text):
                logger.info("ℹ️ 状态提示：仍在冷却中 (Cooldown)，无需续费。")
            else:
                logger.warning("⚠️ 状态不明：既没看到按钮也没看到冷却文字。")

        except Exception as e:
            logger.error(f"❌ 运行报错: {str(e)}")
            sb.save_screenshot("critical_error.png")

if __name__ == "__main__":
    run_test()
