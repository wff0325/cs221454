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
    # Firefox 插件通常是一个 .xpi 文件
    EXT_PATH = os.path.abspath("captcha_solver/buster.xpi")
    
    print(f"🎲 [Step 1] 随机玩家名: {RANDOM_NAME}")
    print(f"🧩 [Step 1] Firefox 插件路径: {EXT_PATH}")

    # 使用 SB 启动 Firefox 模式
    # 注意：browser="firefox"
    with SB(browser="firefox",
            headless=False, # xvfb 环境下设为 False 以加载插件
            proxy="127.0.0.1:8080") as sb:
        
        try:
            # 1. 访问网页
            print(f"🔗 [Step 2] 正在通过 Firefox 打开页面: {TARGET_URL}")
            sb.open(TARGET_URL)
            sb.sleep(6)
            
            # 【Firefox 特色】手动注入插件 (Firefox 自动加载 XPI 有时不稳定)
            # SeleniumBase 会处理大部分情况，如果不行我们可以通过下面的步骤
            
            # 2. 填写玩家名
            print(f"✍️ [Step 3] 填入名字...")
            sb.type("input[placeholder*='Username']", RANDOM_NAME)
            sb.save_screenshot("01_after_typing_name.png")

            # 3. 触发验证码
            print("🛡️ [Step 4] 点击 reCAPTCHA 复选框...")
            sb.switch_to_frame('iframe[title*="reCAPTCHA"]')
            sb.click(".recaptcha-checkbox-border")
            sb.switch_to_default_content()
            sb.sleep(5)

            # 4. 破解逻辑
            challenge_frame = 'iframe[title*="挑战"], iframe[title*="challenge"], iframe[src*="bframe"]'
            if sb.is_element_present(challenge_frame):
                print("📸 [Step 5] 发现挑战框，尝试加载 Buster...")
                sb.switch_to_frame(challenge_frame)
                sb.sleep(2)
                
                # 切换到语音验证
                if sb.is_element_visible("#recaptcha-audio-button"):
                    sb.click("#recaptcha-audio-button")
                    print("🎧 已切换到语音模式，等待插件图标...")
                    sb.sleep(6)
                
                # 寻找 Buster 图标
                buster_btn = "button#solver-button, .solver-button, .help-button-holder"
                
                if sb.is_element_visible(buster_btn):
                    print("🚀 [SUCCESS] Firefox 下发现 Buster 图标！执行破解...")
                    sb.click(buster_btn)
                    sb.sleep(35)
                else:
                    print("⚠️ [Error] Firefox 依然没看到图标。")
                    sb.save_screenshot("02_no_buster_icon.png")
                
                sb.switch_to_default_content()
            else:
                print("✨ 未发现挑战框，可能已自动通过")

            sb.save_screenshot("03_captcha_state.png")

            # 5. 点击续费按钮
            print("🔥 [Step 6] 检测续费按钮状态...")
            submit_btn = "button:contains('Complete Verification')"
            
            for i in range(15):
                if sb.is_element_enabled(submit_btn):
                    print(f"✅ 验证通过！点击提交 (尝试 {i+1})...")
                    sb.click(submit_btn)
                    sb.sleep(6)
                    sb.save_screenshot("04_final_success.png")
                    print("🎉 Firefox 续期任务完成！")
                    return
                
                print(f"   ...等待验证通过中 ({i+1}/15)")
                sb.sleep(3)
            
            print("❌ [Failed] 最终未能点击到续费按钮")
            sb.save_screenshot("04_final_failed.png")

        except Exception as e:
            print(f"💥 异常: {e}")
            sb.save_screenshot("error_crash.png")

if __name__ == "__main__":
    run_renew()
