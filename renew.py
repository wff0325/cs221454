import os
import time
import random
import string
from seleniumbase import SB

def generate_random_name():
    # 生成随机 8 位名字
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def run_renew():
    TARGET_URL = "https://game4free.net/myplay"
    RANDOM_NAME = generate_random_name()
    EXT_DIR = os.path.abspath("captcha_solver")
    
    print(f"🎲 [步骤 1] 准备填入随机名: {RANDOM_NAME}")

    # 启动浏览器，挂载代理和 Buster 插件
    with SB(uc=True, headless=True, proxy="127.0.0.1:8080", extension_dir=EXT_DIR) as sb:
        try:
            # 1. 打开网页并填名字
            print(f"🔗 正在打开页面...")
            sb.uc_open_with_reconnect(TARGET_URL, 6)
            sb.sleep(5)
            
            print(f"✍️ 正在填入用户名...")
            sb.type("input[placeholder*='Username']", RANDOM_NAME)
            sb.save_screenshot("step1_named.png")

            # 2. 点击谷歌验证码复选框
            print("🛡️ [步骤 2] 正在触发谷歌验证码复选框...")
            # 进入验证码的小方框 iframe
            sb.switch_to_frame('iframe[title*="reCAPTCHA"]')
            sb.click(".recaptcha-checkbox-border")
            sb.switch_to_default_content()
            sb.sleep(4)

            # 3. 处理可能弹出的挑战图片 (通过 Buster 破解)
            print("📸 [步骤 3] 正在检查是否弹出图片挑战...")
            # 查找挑战图片所在的 iframe
            challenge_frame = 'iframe[title*="挑战"], iframe[title*="challenge"], iframe[src*="bframe"]'
            
            if sb.is_element_present(challenge_frame):
                print("⚡ 发现图片挑战！正在调用 Buster 插件破解...")
                sb.switch_to_frame(challenge_frame)
                
                # 关键：先点一下语音按钮，Buster 插件才会出现
                if sb.is_element_visible("#recaptcha-audio-button"):
                    sb.click("#recaptcha-audio-button")
                    sb.sleep(3)
                
                # 点击 Buster 破解按钮 (ID 为 solver-button)
                if sb.is_element_visible("#solver-button"):
                    sb.click("#solver-button")
                    print("🚀 插件已开始 Hash 破解，请耐心等待 30 秒...")
                    # 语音识别和 Hash 匹配比较耗时
                    sb.sleep(30)
                else:
                    print("⚠️ 未找到 Buster 按钮，请检查插件加载状态")
                
                sb.switch_to_default_content()
            else:
                print("✨ 未弹出挑战图片，可能直接通过了")

            sb.save_screenshot("step3_captcha_solved.png")

            # 4. 点击最终的续费按钮
            print("🔥 [步骤 4] 正在尝试点击“Complete Verification”续费按钮...")
            submit_btn = "button:contains('Complete Verification')"
            
            # 循环检测按钮是否从“灰色”变成“可点击”
            success = False
            for i in range(15):
                if sb.is_element_enabled(submit_btn):
                    print(f"✅ 验证码已通过，按钮激活！正在点击提交 (尝试 {i+1})...")
                    sb.click(submit_btn)
                    sb.sleep(5)
                    sb.save_screenshot("step4_final_success.png")
                    print("🎉 续费流程已完成！")
                    success = True
                    break
                else:
                    print(f"⏳ 验证码尚未过，等待中... ({i+1}/15)")
                    sb.sleep(3)
            
            if not success:
                print("❌ 最终未能激活续费按钮，验证码破解失败。")
                sb.save_screenshot("step4_failed.png")

        except Exception as e:
            print(f"💥 运行异常: {e}")
            sb.save_screenshot("crash_debug.png")

if __name__ == "__main__":
    run_renew()
