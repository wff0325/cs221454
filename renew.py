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
    # 插件绝对路径
    EXT_DIR = os.path.abspath("captcha_solver")
    
    print(f"🎲 [步骤 1] 随机生成玩家名: {RANDOM_NAME}")
    print(f"🧩 [步骤 1] 插件加载路径: {EXT_DIR}")

    # 检查插件是否解压成功
    if not os.path.exists(os.path.join(EXT_DIR, "manifest.json")):
        print("❌ 错误：插件路径下未找到 manifest.json，插件加载将失效！")

    # 使用 SB 启动，增加强迫加载插件的参数
    with SB(uc=True, 
            headless=False, # 必须为 False 配合 xvfb，否则插件不工作
            proxy="127.0.0.1:8080", 
            extension_dir=EXT_DIR,
            chromium_arg="--no-sandbox,--disable-dev-shm-usage,--disable-extensions-except={},--load-extension={}".format(EXT_DIR, EXT_DIR)) as sb:
        try:
            # 1. 访问并填名
            print(f"🔗 [步骤 2] 正在打开页面: {TARGET_URL}")
            sb.uc_open_with_reconnect(TARGET_URL, 6)
            sb.sleep(5)
            sb.save_screenshot("01_page_load.png")
            
            print(f"✍️ [步骤 2] 正在填入名字...")
            sb.type("input[placeholder*='Username']", RANDOM_NAME)

            # 2. 触发 Checkbox
            print("🛡️ [步骤 3] 正在触发 reCAPTCHA 复选框...")
            sb.switch_to_frame('iframe[title*="reCAPTCHA"]')
            sb.click(".recaptcha-checkbox-border")
            sb.switch_to_default_content()
            sb.sleep(4)

            # 3. 处理挑战框 (Buster 核心逻辑)
            print("📸 [步骤 4] 检查挑战框是否弹出...")
            challenge_frame = 'iframe[title*="挑战"], iframe[title*="challenge"], iframe[src*="bframe"]'
            
            if sb.is_element_present(challenge_frame):
                print("⚡ 发现挑战框！切换到语音模式以触发 Buster 插件...")
                sb.switch_to_frame(challenge_frame)
                sb.sleep(2)
                
                # 点击语音验证按钮 (这是触发 Buster 插件的前提)
                audio_btn = "#recaptcha-audio-button"
                if sb.is_element_visible(audio_btn):
                    sb.click(audio_btn)
                    print("🎧 已切换到语音模式，等待插件图标注入...")
                    sb.sleep(5) # 给插件更多时间显示图标
                
                # 点击 Buster 破解按钮 (包含多个可能选择器)
                # v3.1.0 按钮通常位于 .help-button-holder 内部
                buster_btn = "button#solver-button, .solver-button, .help-button-holder"
                
                if sb.is_element_visible(buster_btn):
                    print("🚀 [Success] 找到 Buster 图标，开始执行 Hash 破解...")
                    sb.click(buster_btn)
                    # 语音识别+Hash比对较慢，等待 35 秒
                    sb.sleep(35)
                else:
                    print("⚠️ [Error] 依然没找到 Buster 图标，请检查 02_no_icon.png")
                    sb.save_screenshot("02_no_icon.png")
                
                sb.switch_to_default_content()
            else:
                print("✨ 未弹出挑战框，可能已自动过码")

            sb.save_screenshot("03_captcha_solved.png")

            # 4. 点击最终续费按钮
            print("🔥 [步骤 5] 正在检测“Complete Verification”按钮状态...")
            submit_btn = "button:contains('Complete Verification')"
            
            for i in range(15):
                if sb.is_element_enabled(submit_btn):
                    print(f"✅ 验证通过，按钮已激活！正在点击提交 (尝试 {i+1})...")
                    sb.click(submit_btn)
                    sb.sleep(5)
                    sb.save_screenshot("04_final_success.png")
                    print("🎉 续期流程已全部完成！")
                    return
                
                # 检查是否被谷歌屏蔽
                if sb.is_text_visible("automated queries"):
                    print("❌ [Blocked] 谷歌拦截了自动化请求 (Automated queries)，请更换代理 IP")
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
