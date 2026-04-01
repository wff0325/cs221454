import os
import time
import random
import string
from seleniumbase import SB

def generate_random_name():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def run_renew():
    TARGET_URL = "https://game4free.net/myplay"
    RANDOM_NAME = generate_random_name()
    EXT_DIR = os.path.abspath("captcha_solver")
    
    print(f"🎲 [步骤 1] 随机生成玩家名: {RANDOM_NAME}")
    print(f"🧩 [步骤 1] 插件绝对路径: {EXT_DIR}")

    with SB(uc=True, 
            headless=False, 
            proxy="127.0.0.1:8080", 
            extension_dir=EXT_DIR,
            chromium_arg="--load-extension={}".format(EXT_DIR)) as sb:
        try:
            # 1. 打开并填名
            sb.uc_open_with_reconnect(TARGET_URL, 6)
            sb.sleep(5)
            sb.type("input[placeholder*='Username']", RANDOM_NAME)
            print(f"✍️ [步骤 2] 已填入名字")

            # 2. 触发 Checkbox
            sb.switch_to_frame('iframe[title*="reCAPTCHA"]')
            sb.click(".recaptcha-checkbox-border")
            sb.switch_to_default_content()
            sb.sleep(4)

            # 3. 挑战框处理
            challenge_frame = 'iframe[title*="挑战"], iframe[title*="challenge"], iframe[src*="bframe"]'
            if sb.is_element_present(challenge_frame):
                print("📸 [步骤 4] 发现挑战框，进入破解逻辑...")
                sb.switch_to_frame(challenge_frame)
                sb.sleep(2)
                
                # 切换到语音验证
                if sb.is_element_visible("#recaptcha-audio-button"):
                    sb.click("#recaptcha-audio-button")
                    print("🎧 已切换到语音验证模式")
                    sb.sleep(5) # 给插件时间注入图标
                
                # 检查插件按钮是否存在 (Buster 的 ID 是 solver-button)
                buster_btn = "#solver-button"
                if not sb.is_element_visible(buster_btn):
                    print("⚠️ 插件图标未出现，尝试点击刷新验证码以强制插件加载...")
                    sb.click("#recaptcha-reload-button")
                    sb.sleep(5)
                
                if sb.is_element_visible(buster_btn):
                    for attempt in range(2):
                        print(f"🚀 点击 Buster 破解按钮 (尝试 {attempt+1})...")
                        sb.click(buster_btn)
                        sb.sleep(25) # 等待语音 Hash 比对结果
                        
                        # 如果识别成功，Verify 按钮应该会变成可点击或者自动消失
                        if not sb.is_element_visible(buster_btn):
                            print("✅ 破解成功，插件按钮已消失")
                            break
                        sb.sleep(5)
                else:
                    print("❌ [严重错误] 插件图标依然未出现。请检查 03_no_buster_icon.png")
                    sb.save_screenshot("03_no_buster_icon.png")

                sb.switch_to_default_content()
            
            sb.save_screenshot("03_captcha_solved.png")

            # 4. 提交
            submit_btn = "button:contains('Complete Verification')"
            for i in range(15):
                if sb.is_element_enabled(submit_btn):
                    print(f"✅ 验证通过！点击提交...")
                    sb.click(submit_btn)
                    sb.sleep(5)
                    sb.save_screenshot("04_final_success.png")
                    print("🎉 任务完成！")
                    return
                # 检测红字拦截
                if sb.is_text_visible("automated queries") or sb.is_text_visible("自动查询"):
                    print("❌ [Blocked] Google 拦截了语音请求 (Automated queries)")
                    return
                sb.sleep(3)
            
            print("❌ [Failed] 未能点击到续费按钮")

        except Exception as e:
            print(f"💥 [Error] 运行崩溃: {e}")
            sb.save_screenshot("error_crash.png")

if __name__ == "__main__":
    run_renew()
