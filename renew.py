import os
import time
import random
import string
from seleniumbase import SB

def generate_random_name(length=8):
    """生成指定长度的随机字母数字组合"""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choices(letters_and_digits, k=length))

def run_debug():
    LOCAL_GOST_PROXY = "127.0.0.1:8080"
    TARGET_URL = "https://game4free.net/myplay"
    
    # 随机生成一个玩家名，例如: rX9aB2zL
    RANDOM_PLAYER_NAME = generate_random_name(8)
    
    print(f"🎲 本次生成的随机玩家名: {RANDOM_PLAYER_NAME}")
    print(f"🌐 流量出口: 127.0.0.1:8080 (GOST)")

    with SB(uc=True, 
            headless=True, 
            proxy=LOCAL_GOST_PROXY, 
            chromium_arg="--no-sandbox,--disable-dev-shm-usage") as sb:
        
        try:
            # 1. 访问目标
            print(f"🔗 正在访问: {TARGET_URL}")
            sb.uc_open_with_reconnect(TARGET_URL, 6)
            sb.sleep(5)
            sb.save_screenshot("01_load_page.png")

            # 2. 填写随机生成的玩家名
            print(f"✍️ 正在填入随机名: {RANDOM_PLAYER_NAME}")
            username_field = "input[placeholder*='Username']"
            if sb.is_element_visible(username_field):
                sb.type(username_field, RANDOM_PLAYER_NAME)
            else:
                print("❌ 未找到输入框，可能是页面加载失败")

            # 3. 验证码处理
            print("🛡️ 正在尝试触发验证码...")
            # 检查是否有配额超限报错 (防止白费力气)
            if sb.is_text_visible("exceeded quota"):
                print("⚠️ 警告：检测到 reCAPTCHA 免费配额已耗尽，按钮可能无法点击")

            captcha_iframe = 'iframe[title*="reCAPTCHA"]'
            if sb.is_element_present(captcha_iframe):
                sb.switch_to_frame(captcha_iframe)
                sb.click(".recaptcha-checkbox-border")
                sb.switch_to_default_content()
                print("🖱️ 已点击验证码 Checkbox，等待 30 秒...")
                sb.sleep(30) # 给破解预留时间
                sb.save_screenshot("02_captcha_status.png")
            
            # 4. 点击最终提交
            submit_btn = "button:contains('Complete Verification')"
            if sb.is_element_enabled(submit_btn):
                print("✅ 按钮已激活，正在提交续费请求...")
                sb.click(submit_btn)
                sb.sleep(5)
                sb.save_screenshot("03_final_result.png")
                print("🎉 任务执行完毕，请检查截图 03_final_result.png")
            else:
                print("❌ 提交按钮仍是禁用状态，验证码没过。")
                sb.save_screenshot("03_failed_state.png")

        except Exception as e:
            print(f"💥 脚本异常: {str(e)}")
            sb.save_screenshot("error_log.png")

if __name__ == "__main__":
    run_debug()
