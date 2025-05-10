import os
import re
import time
from urllib.parse import urlparse
import keyboard
import undetected_chromedriver as uc

OUTPUT_DIR = os.path.join('data', 'images')
PROFILE_DIR = os.path.abspath('chrome_profile')  # Persistent Chrome profile directory
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PROFILE_DIR, exist_ok=True)

def get_domain(url):
    parsed = urlparse(url)
    if parsed.scheme == 'file':
        return os.path.splitext(os.path.basename(parsed.path))[0]
    domain = parsed.netloc
    # Ensure domain is a string
    if isinstance(domain, bytes):
        domain = domain.decode('utf-8', errors='ignore')
    domain = str(domain)
    domain = domain.replace('.', '_')
    return domain if domain else 'screenshot'

def get_next_filename(domain):
    existing = [f for f in os.listdir(OUTPUT_DIR) if f.startswith(domain)]
    nums = [int(re.findall(rf'{re.escape(domain)}(\d+)\.png', f)[0]) for f in existing if re.findall(rf'{re.escape(domain)}(\d+)\.png', f)]
    next_num = max(nums) + 1 if nums else 1
    return os.path.join(OUTPUT_DIR, f"{domain}{next_num}.png")

def main(width=1920, height=5000):
    options = uc.ChromeOptions()
    options.add_argument(f'--window-size={width},{height}')
    options.add_argument(f'--user-data-dir={PROFILE_DIR}')  # Use persistent profile
    driver = uc.Chrome(options=options)
    driver.get('about:blank')
    time.sleep(1)

    print("\n[INFO] Chrome launched (undetected, persistent profile). Browse to any page.\nPress [ at any time to take a screenshot. Press Ctrl+C to exit.\n")

    def take_screenshot():
        # Switch to the last tab before taking a screenshot
        driver.switch_to.window(driver.window_handles[-1])
        url = driver.current_url
        domain = get_domain(url)
        filename = get_next_filename(domain)
        driver.save_screenshot(filename)
        print(f"[Screenshot] Saved: {filename} (URL: {url})")

    # Use '[' as the screenshot hotkey
    keyboard.add_hotkey('[', take_screenshot, suppress=False)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Exiting and closing Chrome...")
        driver.quit()
        keyboard.unhook_all_hotkeys()
        print("[INFO] Done.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Global hotkey full-page screenshot tool (undetected-chromedriver, persistent profile)')
    parser.add_argument('--width', type=int, default=1920, help='Window width')
    parser.add_argument('--height', type=int, default=5000, help='Window height (increase for longer pages)')
    args = parser.parse_args()
    main(args.width, args.height) 