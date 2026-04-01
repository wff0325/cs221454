import time
import random
import logging
from seleniumbase import SB

# 日志设置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 明文配置 ---
PROXY_ADDR = "127.0.0.1:8080"
USER_EMAIL = "vbfgh@431234.xyz"
USER_PASS  = "Qwer123456"
SERVER_ID  = "f715280f"
# ---------------

def human_delay(min_s=1.0, max_s=3.0):
    """随机停顿，模拟思考时间"""
    time.sleep(random.uniform(min_s, max_s))

def run_fgh_human():
    logger.info("🎬 启动拟人化续费脚本...")

    # uc=True 开启 Undetected Chromedriver 模式
    with SB(uc=True, headless=True, proxy=PROXY_ADDR) as sb:
        try:
            # 1. 访问并观察页面
            sb.open("https://panel.freegamehost.xyz/auth/login")
            logger.info("已打开页面，模拟观察中...")
            human_delay(5, 8) # 模拟人加载页面的等待

            # 2. 清理可能的遮挡物
            sb.execute_script("document.querySelectorAll('iframe:not([src*=\"google.com\"])').forEach(el => el.remove());")
            
            # 3. 模拟人工输入账号
            if sb.is_element_visible('input[name="username"]'):
                logger.info("正在输入账号...")
                # delay=0.1 模拟每秒打10个字，带有随机波动
                sb.type('input[name="username"]', USER_EMAIL, delay=random.uniform(0.1, 0.25))
                human_delay(1, 2.5) # 输入完账号停一下

                logger.info("正在输入密码...")
                sb.type('input[name="password"]', USER_PASS, delay=random.uniform(0.1, 0.3))
                human_delay(2, 4) # 输入完密码思考一下

            # 4. 触发并破解验证码
            # 这是逻辑核心：音频挑战破解
            logger.info("🛡️ 正在检测并尝试音频破解 reCAPTCHA...")
            try:
                # 这个函数会模拟移动鼠标到验证码框，点击，若有图片挑战则切换到音频破解
                sb.solve_re_captcha()
                logger.info("✅ 验证码破解尝试结束。")
                human_delay(2, 5) # 破解完等一会儿，别秒点登录
            except Exception as e:
                logger.warning(f"⚠️ 自动破解识别器提示: {e}")
                # 即使报错，可能也已经打钩了，继续尝试

            # 5. 点击登录按钮
            login_btn = 'button[type="submit"]'
            if sb.is_element_visible(login_btn):
                logger.info("正在模拟点击登录按钮...")
                # uc_click 会模拟鼠标移动到按钮坐标的轨迹
                sb.uc_click(login_btn)
                logger.info("已提交，正在等待仪表盘加载...")
                human_delay(10, 15)

            # 6. 跳转控制台
            current_url = sb.get_current_url()
            if "login" in current_url:
                logger.error("❌ 登录失败，可能验证码未过或IP被风控。")
                sb.save_screenshot("login_failed.png")
                # 尝试强制跳转，看是否已经有Session
            
            sb.open(f"https://panel.freegamehost.xyz/server/{SERVER_ID}")
            logger.info(f"正在加载服务器 {SERVER_ID} 的控制台...")
            human_delay(12, 18)

            # 7. 续费逻辑
            timer_el = "div[class*='RenewBox__TimerDigits']"
            renew_btn = "button:contains('Renew')"
            
            if sb.is_element_visible(timer_el):
                logger.info(f"⏳ 发现倒计时，当前剩余: {sb.get_text(timer_el)}")
                human_delay(2, 4)

            if sb.is_element_visible(renew_btn):
                logger.info("🎯 发现续费按钮，准备执行拟人化点击...")
                sb.uc_click(renew_btn)
                human_delay(2, 3.5)
                
                # 确认弹窗
                if sb.is_text_visible("Confirm", "button"):
                    logger.info("点击确认按钮...")
                    sb.click("button:contains('Confirm')")
                    human_delay(3, 5)
                
                logger.info("✨ 续费指令发送完毕！")
                sb.save_screenshot("success_final.png")
            else:
                logger.info("ℹ️ 页面未发现续费按钮，可能尚未到期。")
                sb.save_screenshot("dashboard_check.png")

        except Exception as e:
            logger.error(f"❌ 运行过程中崩溃: {str(e)}")
            sb.save_screenshot("crash_debug.png")

if __name__ == "__main__":
    run_fgh_human()
