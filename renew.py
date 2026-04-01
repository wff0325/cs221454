import os
import time
import random
import string
from seleniumbase import SB

def generate_random_name(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def run_renew():
    LOCAL_GOST_PROXY = "127.0.0.1:8080"
    TARGET_URL = "https://game4free.net/myplay"
    RANDOM_PLAYER_NAME = generate_random_name(8)
    # 获取插件的绝对路径
    EXT_DIR = os.path.abspath("captcha_solver")
    
    print(f"🎲 随机名: {RANDOM_PLAYER_NAME} | 🧩 插件路径: {EXT_DIR}")

    with SB(uc=True, headless=True, proxy=LOCAL_GOST_PROXY, extension_dir=EXT_DIR) as sb:
        try:
            # 1. 访问
            sb.uc_open_with_reconnect(TARGET_URL, 6)
            sb.sleep(5)
            
            # 2. 填名
            sb.type("input[placeholder*='Username']", RANDOM_PLAYER_NAME)
            print("✍️ 已填名")

            # 3. 核心：处理验证码
            print("🛡️ 正在触发验证码...")
            sb.switch_to_frame('iframe[title*="reCAPTCHA"]')
            sb.click(".recaptcha-checkbox-border")
            sb.sleep(4) # 等待是否弹出挑战框
            
            # 4. 尝试触发 Buster 破解插件
            # 切换回主页面，寻找可能弹出的图片挑战 iframe
            sb.switch_to_default_content()
            
            # 谷歌验证码的挑战框通常在另一个 iframe 里
            challenge_iframe = 'iframe[title*="验证码挑战"]'
            if not sb.is_element_present(challenge_iframe):
                challenge_iframe = 'iframe[title*="recaptcha challenge"]'

            if sb.is_element_present(challenge_iframe):
                print("📸 发现图片挑战，启动 Buster 破解...")
                sb.switch_to_frame(challenge_iframe)
                
                # 点击 Buster 插件的小图标（那个黄色的小人/人头图标）
                # 插件加载后，在验证码挑战框底部会出现一个按钮
                buster_button = "button#solver-button"
                if sb.is_element_visible(buster_button):
                    sb.click(buster_button)
                    print("⚡ 已点击 Buster 破解按钮，等待语音 Hash 比对...")
                    sb.sleep(20) # 插件破解需要时间
                else:
                    print("⚠️ 未找到 Buster 插件按钮，尝试硬等...")
                    sb.sleep(20)
            
            sb.switch_to_default_content()
            sb.save_screenshot("02_after_solver.png")

            # 5. 检查提交按钮
            submit_btn = "button:contains('Complete Verification')"
            
            # 循环检查 10 次，每次等 3 秒，看验证码是否通过（按钮变绿）
            for i in range(10):
                if sb.is_element_enabled(submit_btn):
                    print(f"✅ 验证通过！(第{i+1}次尝试)")
                    sb.click(submit_btn)
                    sb.sleep(5)
                    sb.save_screenshot("03_success.png")
                    return
                print(f"⏳ 正在等待验证码校验完成... ({i+1}/10)")
                sb.sleep(3)

            print("❌ 验证码未能通过，按钮仍处于禁用状态。")
            sb.save_screenshot("03_final_failed.png")

        except Exception as e:
            print(f"💥 异常: {e}")
            sb.save_screenshot("crash.png")

if __name__ == "__main__":
    run_renew()
