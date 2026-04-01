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

    with SB(uc=True, 
            headless=False, 
            proxy="127.0.0.1:8080", 
            extension_dir=EXT_DIR,
            chromium_arg="--disable-extensions-except={},--load-extension={}".format(EXT_DIR, EXT_DIR)) as sb:
        try:
            # 1. 访问
            sb.uc_open_with_reconnect(TARGET_URL, 6)
            sb.sleep(5)
            sb.type("input[placeholder*='Username']", RANDOM_NAME)
            print(f"✍️ [步骤 2] 已填入名字")

            # 2. 触发 Checkbox
            sb.switch_to_frame('iframe[title*="reCAPTCHA"]')
            sb.click(".recaptcha-checkbox-border")
            sb.switch_to_default_content()
            sb.sleep(4)

            # 3. 挑战框破解逻辑
            challenge_frame = 'iframe[title*="挑战"], iframe[title*="challenge"], iframe[src*="bframe"]'
            if sb.is_element_present(challenge_frame):
                print("📸 [步骤 4] 发现挑战框，尝试破解...")
                sb.switch_to_frame(challenge_frame)
                sb.sleep(2)
                
                # 切换到语音验证
                if sb.is_element_visible("#recaptcha-audio-button"):
                    sb.click("#recaptcha-audio-button")
                    sb.sleep(4)
                
                # 检查是否被谷歌红字拦截
                if sb.is_text_visible("automated queries") or sb.is_text_visible("计算机或网络"):
                    print("❌ [严重错误] Google 拦截了语音请求：检测到自动化查询。此代理 IP 已被标记，请更换 SOCKS5 代理！")
                    sb.save_screenshot("02_ip_blocked.png")
                    return

                # 尝试点击 Buster 按钮并加入重试
                buster_btn = "button#solver-button, .solver-button, .help-button-holder"
                for attempt in range(2):
                    if sb.is_element_visible(buster_btn):
                        print(f"🚀 点击 Buster 按钮 (尝试 {attempt+1})...")
                        sb.click(buster_btn)
                        sb.sleep(20) # 等待识别
                        
                        # 检查验证码输入框是否有值了
                        val = sb.get_attribute("#audio-response", "value")
                        if val:
                            print(f"✅ 插件已填入识别结果: {val}，尝试点击 VERIFY 确认...")
                            sb.click("#recaptcha-verify-button")
                            sb.sleep(5)
                            break
                    sb.sleep(5)

                sb.switch_to_default_content()
            
            sb.save_screenshot("03_captcha_solved.png")

            # 4. 点击最终续费按钮
            submit_btn = "button:contains('Complete Verification')"
            for i in range(15):
                # 再次检查是否有全局红字拦截
                if sb.is_text_visible("automated queries"):
                    print("❌ [Blocked] 最终阶段检测到谷歌拦截。")
                    return

                if sb.is_element_enabled(submit_btn):
                    print(f"✅ 验证通过！正在点击提交...")
                    sb.click(submit_btn)
                    sb.sleep(5)
                    sb.save_screenshot("04_final_success.png")
                    print("🎉 续期流程已全部完成！")
                    return
                sb.sleep(3)
            
            print("❌ [Failed] 最终未能激活续费按钮，请检查 03_captcha_solved.png 确认验证码是否打勾。")

        except Exception as e:
            print(f"💥 [Error] 运行崩溃: {e}")
            sb.save_screenshot("error_crash.png")

if __name__ == "__main__":
    run_renew()
