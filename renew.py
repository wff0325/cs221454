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
            print(f"✍️ 已填名: {RANDOM_PLAYER_NAME}")

            # 3. 处理验证码
            print("🛡️ 触发验证码 Checkbox...")
            sb.switch_to_frame('iframe[title*="reCAPTCHA"]')
            sb.click(".recaptcha-checkbox-border")
            sb.sleep(5)
            
            # 4. 尝试寻找挑战框并启动 Buster
            sb.switch_to_default_content()
            
            # 查找挑战框的多种可能 ID/Title
            challenge_iframes = ['iframe[title*="验证码挑战"]', 'iframe[title*="recaptcha challenge"]', 'iframe[src*="bframe"]']
            
            for frame in challenge_iframes:
                if sb.is_element_present(frame):
                    print(f"📸 发现挑战框: {frame}，启动 Buster 破解...")
                    sb.switch_to_frame(frame)
                    
                    # Buster 插件会在验证码底部生成一个按钮
                    # 尝试点击它的 ID：solver-button
                    if sb.is_element_visible("button#solver-button"):
                        sb.click("button#solver-button")
                        print("⚡ Buster 已介入，正在进行语音识别...")
                        sb.sleep(20) # 语音 Hash 破解需要较长时间
                    break
            
            sb.switch_to_default_content()
            sb.save_screenshot("02_captcha_result.png")

            # 5. 等待按钮激活
            submit_btn = "button:contains('Complete Verification')"
            for i in range(15):
                if sb.is_element_enabled(submit_btn):
                    print(f"✅ 验证成功！(第{i+1}次检查)")
                    sb.click(submit_btn)
                    sb.sleep(5)
                    sb.save_screenshot("03_final_success.png")
                    print("🎉 续期完成！")
                    return
                sb.sleep(3)

            print("❌ 无法通过验证，按钮未激活。")
            sb.save_screenshot("03_final_failed.png")

        except Exception as e:
            print(f"💥 异常: {e}")
            sb.save_screenshot("error_crash.png")

if __name__ == "__main__":
    run_renew()
