import os
import time
import random
import string
from seleniumbase import SB

def generate_random_name():
    """生成随机 8 位玩家名"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def run_renew():
    TARGET_URL = "https://game4free.net/myplay"
    RANDOM_NAME = generate_random_name()
    # 必须使用绝对路径加载插件
    EXT_DIR = os.path.abspath("captcha_solver")
    
    print(f"🎲 [Step 1] 随机玩家名: {RANDOM_NAME}")
    print(f"🧩 [Step 1] 插件路径: {EXT_DIR}")

    # 【重要配置】headless=False 配合 xvfb 才能加载扩展
    with SB(uc=True, 
            headless=False, 
            proxy="127.0.0.1:8080", 
            extension_dir=EXT_DIR) as sb:
        try:
            # 1. 访问并填名
            print(f"🔗 [Step 2] 正在打开页面: {TARGET_URL}")
            sb.uc_open_with_reconnect(TARGET_URL, 6)
            sb.sleep(5)
            sb.save_screenshot("01_page_load.png")
            
            print(f"✍️ [Step 2] 正在填入名字...")
            sb.type("input[placeholder*='Username']", RANDOM_NAME)

            # 2. 触发 Checkbox
            print("🛡️ [Step 3] 触发 reCAPTCHA 复选框...")
            sb.switch_to_frame('iframe[title*="reCAPTCHA"]')
            sb.click(".recaptcha-checkbox-border")
            sb.switch_to_default_content()
            sb.sleep(4)

            # 3. 处理挑战框 (Buster 破解)
            print("📸 [Step 4] 检查挑战框...")
            # 匹配各种可能的挑战框标识
            challenge_frame = 'iframe[title*="挑战"], iframe[title*="challenge"], iframe[src*="bframe"]'
            
            if sb.is_element_present(challenge_frame):
                print("⚡ 发现挑战框！切换到语音模式触发 Buster...")
                sb.switch_to_frame(challenge_frame)
                sb.sleep(2)
                
                # 点击语音验证按钮
                audio_btn = "#recaptcha-audio-button"
                if sb.is_element_visible(audio_btn):
                    sb.click(audio_btn)
                    sb.sleep(3)
                
                # 点击 Buster 破解按钮
                # v3.1.0 常用选择器：solver-button 或 .solver-button
                buster_btn = "button#solver-button, .solver-button, [title*='Solve']"
                if sb.is_element_visible(buster_btn):
                    print("🚀 成功找到破解按钮，启动 Hash 比对...")
                    sb.click(buster_btn)
                    # 语音破解较慢，给足 35 秒时间
                    sb.sleep(35)
                else:
                    print("⚠️ 挑战框内未找到 Buster 按钮，请查看截图 02_frame_error.png")
                    sb.save_screenshot("02_frame_error.png")
                
                sb.switch_to_default_content()
            else:
                print("✨ 未弹出挑战框，可能已自动通过")

            sb.save_screenshot("03_captcha_result.png")

            # 4. 点击最终续费按钮
            print("🔥 [Step 5] 正在检测“Complete Verification”按钮...")
            submit_btn = "button:contains('Complete Verification')"
            
            for i in range(15):
                if sb.is_element_enabled(submit_btn):
                    print(f"✅ 验证通过！按钮已激活，正在提交 (尝试 {i+1})...")
                    sb.click(submit_btn)
                    sb.sleep(5)
                    sb.save_screenshot("04_final_success.png")
                    print("🎉 续期任务圆满完成！")
                    return
                
                # 检查是否被谷歌判定为频繁查询
                if sb.is_text_visible("automated queries"):
                    print("❌ [Blocked] 代理 IP 被谷歌拦截 (Automated queries)")
                    return
                
                print(f"   ...等待中 ({i+1}/15)")
                sb.sleep(3)
            
            print("❌ [Failed] 最终未能激活续费按钮")
            sb.save_screenshot("04_final_failed.png")

        except Exception as e:
            print(f"💥 [Error] 运行崩溃: {e}")
            sb.save_screenshot("error_crash.png")

if __name__ == "__main__":
    run_renew()
