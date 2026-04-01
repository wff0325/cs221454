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
    # 必须是绝对路径
    EXT_PATH = os.path.abspath("captcha_solver/buster.xpi")
    
    print(f"🎲 [步骤 1] 随机玩家名: {RANDOM_NAME}")
    print(f"🧩 [步骤 1] 待加载插件路径: {EXT_PATH}")

    # 启动 Firefox
    # extension_dir 在 Firefox 下有时不生效，我们会使用内部 install_addon 确保加载
    with SB(browser="firefox",
            headless=False, # 必须为 False 配合 xvfb
            proxy="127.0.0.1:8080") as sb:
        
        try:
            # --- 【修正：火狐插件加载关键步】 ---
            print("🧩 正在向 Firefox 注入 Buster 插件...")
            sb.driver.install_addon(EXT_PATH, temporary=True)
            sb.sleep(2)

            # 1. 访问网页
            print(f"🔗 [步骤 2] 打开页面...")
            sb.open(TARGET_URL)
            sb.sleep(6)
            
            # 2. 填写名字
            print(f"✍️ [步骤 3] 填入名字...")
            sb.type("input[placeholder*='Username']", RANDOM_NAME)
            sb.save_screenshot("01_after_typing_name.png")

            # 3. 触发验证码
            print("🛡️ [步骤 4] 触发复选框...")
            sb.switch_to_frame('iframe[title*="reCAPTCHA"]')
            sb.click(".recaptcha-checkbox-border")
            sb.switch_to_default_content()
            sb.sleep(5)

            # 4. 破解逻辑
            challenge_frame = 'iframe[title*="挑战"], iframe[title*="challenge"], iframe[src*="bframe"]'
            if sb.is_element_present(challenge_frame):
                print("📸 [步骤 5] 发现挑战框，尝试启动破解...")
                sb.switch_to_frame(challenge_frame)
                sb.sleep(3)
                
                # 切换到语音验证
                audio_btn = "#recaptcha-audio-button"
                if sb.is_element_visible(audio_btn):
                    sb.click(audio_btn)
                    print("🎧 已进入语音模式，等待插件图标...")
                    sb.sleep(6)
                
                # 寻找 Buster 图标
                # 火狐下选择器与 Chrome 一致
                buster_btn = "button#solver-button, .solver-button, .help-button-holder"
                
                if sb.is_element_visible(buster_btn):
                    print("🚀 [SUCCESS] 成功找到 Buster 图标！正在执行 Hash 破解...")
                    sb.click(buster_btn)
                    # 语音破解大约需要 30 秒
                    sb.sleep(35)
                else:
                    print("⚠️ [Error] 依旧没看到图标。请检查 02_no_icon.png")
                    sb.save_screenshot("02_no_icon.png")
                
                sb.switch_to_default_content()
            
            sb.save_screenshot("03_captcha_state.png")

            # 5. 点击提交
            submit_btn = "button:contains('Complete Verification')"
            for i in range(15):
                if sb.is_element_enabled(submit_btn):
                    print(f"✅ 验证码打勾成功！正在点击提交...")
                    sb.click(submit_btn)
                    sb.sleep(6)
                    sb.save_screenshot("04_final_success.png")
                    print("🎉 任务圆满完成！")
                    return
                print(f"   ...等待验证结果 ({i+1}/15)")
                sb.sleep(3)
            
            print("❌ [Failed] 最终未能点击到续费按钮")
            sb.save_screenshot("04_final_failed.png")

        except Exception as e:
            print(f"💥 异常: {e}")
            sb.save_screenshot("error_crash.png")

if __name__ == "__main__":
    run_renew()
