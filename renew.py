import os
import time
import random
import string
from seleniumbase import SB

def generate_random_name():
    """生成 8 位随机玩家名"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def run_renew():
    TARGET_URL = "https://game4free.net/myplay"
    RANDOM_NAME = generate_random_name()
    EXT_PATH = os.path.abspath("captcha_solver/buster.xpi")
    
    print(f"🎲 [步骤 1] 随机玩家名: {RANDOM_NAME}")

    with SB(browser="firefox", headless=False, proxy="127.0.0.1:8080") as sb:
        try:
            print("🧩 正在向 Firefox 注入 Buster 插件...")
            sb.driver.install_addon(EXT_PATH, temporary=True)
            sb.sleep(2)

            print(f"🔗 [步骤 2] 打开页面...")
            sb.open(TARGET_URL)
            sb.sleep(6)
            
            print(f"✍️ [步骤 3] 填入名字...")
            sb.type("input[placeholder*='Username']", RANDOM_NAME)
            sb.save_screenshot("01_after_typing_name.png")

            print("🛡️ [步骤 4] 触发复选框...")
            sb.switch_to_frame('iframe[title*="reCAPTCHA"]')
            sb.click(".recaptcha-checkbox-border")
            sb.switch_to_default_content()
            sb.sleep(5)

            # --- 🔍 新增：检测 IP 是否已被谷歌硬拉黑 ---
            challenge_frame = 'iframe[title*="挑战"], iframe[title*="challenge"], iframe[src*="bframe"]'
            if sb.is_element_present(challenge_frame):
                sb.switch_to_frame(challenge_frame)
                sb.sleep(2)

                # 检查有没有 "Try again later" 或 "automated queries" 文字
                page_text = sb.get_text("body")
                if "Try again later" in page_text or "automated queries" in page_text:
                    print("❌ [严重警告] 谷歌已拉黑此代理 IP，并提示 'Try again later'！继续运行没有意义，请更换 SOCKS5 住宅 IP。")
                    sb.save_screenshot("02_ip_blocked_hard.png")
                    return # 发现被拉黑，直接退出，节省 Actions 额度

                # 切换到语音验证
                audio_btn = "#recaptcha-audio-button"
                if sb.is_element_visible(audio_btn):
                    sb.click(audio_btn)
                    print("🎧 已进入语音模式，等待插件图标...")
                    sb.sleep(6)
                
                buster_btn = "button#solver-button, .solver-button, .help-button-holder"
                if sb.is_element_visible(buster_btn):
                    print("🚀 [SUCCESS] 成功找到 Buster 图标！正在执行 Hash 破解...")
                    sb.click(buster_btn)
                    sb.sleep(35)
                else:
                    print("⚠️ [Error] 没看到图标。")
                    sb.save_screenshot("02_no_icon.png")
                
                sb.switch_to_default_content()
            
            sb.save_screenshot("03_captcha_state.png")

            # 5. 点击提交
            submit_btn = "button:contains('Complete Verification')"
            for i in range(10):
                if sb.is_element_enabled(submit_btn):
                    print(f"✅ 验证码打勾成功！正在点击提交...")
                    sb.click(submit_btn)
                    sb.sleep(6)
                    sb.save_screenshot("04_final_success.png")
                    print("🎉 任务完成！")
                    return
                sb.sleep(3)
            
            print("❌ [Failed] 验证码未过，无法点击续期按钮")
            sb.save_screenshot("04_final_failed.png")

        except Exception as e:
            print(f"💥 异常: {e}")
            sb.save_screenshot("error_crash.png")

if __name__ == "__main__":
    run_renew()
