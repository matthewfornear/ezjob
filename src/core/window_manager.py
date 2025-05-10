import pygetwindow as gw
import pyautogui
from PIL import Image
import time

class WindowManager:
    def __init__(self, window_title="Chrome"):
        self.window_title = window_title
        self._window = None

    def _find_window(self):
        # Try to find Chrome window
        windows = gw.getWindowsWithTitle(self.window_title)
        if not windows:
            raise RuntimeError(f"Chrome window not found. Please make sure Chrome is running.")
        
        # Find the most recently active Chrome window
        chrome_windows = [w for w in windows if "Chrome" in w.title]
        if not chrome_windows:
            raise RuntimeError("No Chrome windows found.")
        
        self._window = chrome_windows[0]
        return self._window

    def take_screenshot(self):
        window = self._find_window()
        # Bring window to front
        window.activate()
        # Small delay to ensure window is in front
        time.sleep(0.5)
        
        # Get window position and size
        x, y, width, height = window.left, window.top, window.width, window.height
        
        # Take screenshot of the window region
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        
        # Convert to PIL Image if not already
        if not isinstance(screenshot, Image.Image):
            screenshot = Image.fromarray(screenshot)
        return screenshot

    def get_window_position(self):
        window = self._find_window()
        return (window.left, window.top)

    def get_window_size(self):
        window = self._find_window()
        return (window.width, window.height)

    def get_active_tab_title(self):
        """Get the title of the currently active Chrome tab."""
        window = self._find_window()
        return window.title 