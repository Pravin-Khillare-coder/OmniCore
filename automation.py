# automation.py
"""Desktop and browser automation for OmniCore.
Supports: open/close apps, browser navigation, typing, keyboard shortcuts,
scrolling, screenshots, and volume control.
"""
import os
import re
import subprocess
import time
import atexit
from typing import List, Dict

# Optional pyautogui for keyboard/mouse actions
try:
    import pyautogui
    pyautogui.FAILSAFE = False
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

# Selenium Chrome driver
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

_driver = None


def _init_driver() -> "webdriver.Chrome":
    """Return a shared Selenium Chrome WebDriver, creating it if needed."""
    global _driver
    if not HAS_SELENIUM:
        raise RuntimeError("selenium / webdriver_manager not installed")
    if _driver is None:
        options = Options()
        options.add_argument("--start-maximized")
        options.add_experimental_option("detach", True)   # keep browser open
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        service = Service(ChromeDriverManager().install())
        _driver = webdriver.Chrome(service=service, options=options)
    return _driver


# ─── Application control ──────────────────────────────────────────────────────

def open_application(app_name: str) -> str:
    """Open a Windows application by name or executable."""
    app = app_name.strip().lower()

    # Map friendly names to known executables
    EXE_MAP = {
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "notepad": "notepad.exe",
        "calc": "calc.exe",
        "mspaint": "mspaint.exe",
        "explorer": "explorer.exe",
        "cmd": "cmd.exe",
        "powershell": "powershell.exe",
        "code": "code",
        "taskmgr": "taskmgr.exe",
        "wordpad": "wordpad.exe",
        "snippingtool": "snippingtool.exe",
    }

    exe = EXE_MAP.get(app, app)

    try:
        subprocess.Popen(exe, shell=True)
        time.sleep(0.1)
        return f"Opened: {app_name}"
    except Exception as e:
        try:
            subprocess.Popen(["cmd", "/c", "start", "", exe], shell=True)
            time.sleep(0.1)
            return f"Opened via shell: {app_name}"
        except Exception as e2:
            return f"Failed to open {app_name}: {e2}"


def close_application(app_name: str) -> str:
    """Kill a running application by its process name."""
    PROC_MAP = {
        "chrome": "chrome.exe",
        "notepad": "notepad.exe",
        "calc": "Calculator.exe",
        "mspaint": "mspaint.exe",
        "explorer": "explorer.exe",
        "cmd": "cmd.exe",
        "code": "Code.exe",
        "spotify": "Spotify.exe",
        "discord": "Discord.exe",
        "vlc": "vlc.exe",
        "powershell": "powershell.exe",
    }
    proc = PROC_MAP.get(app_name.lower(), app_name + ".exe")
    try:
        subprocess.run(["taskkill", "/f", "/im", proc], capture_output=True)
        return f"Closed: {app_name}"
    except Exception as e:
        return f"Failed to close {app_name}: {e}"


# ─── Browser navigation ───────────────────────────────────────────────────────

def navigate(url: str) -> str:
    """Navigate the shared Chrome window to a URL (opens Chrome if not open)."""
    try:
        driver = _init_driver()
        driver.get(url)
        time.sleep(0.1)
        return f"Navigated to {url}"
    except Exception as e:
        # Fallback: open via OS default browser
        import webbrowser
        webbrowser.open(url)
        return f"Opened {url} in default browser (Selenium unavailable: {e})"


# ─── Keyboard / mouse actions ─────────────────────────────────────────────────

def type_text(text: str) -> str:
    """Type text into the currently active window."""
    if HAS_PYAUTOGUI:
        time.sleep(0.1)
        pyautogui.write(text, interval=0.005)
        return f"Typed: {text}"
    # Fallback: try Selenium active element
    try:
        driver = _init_driver()
        active = driver.switch_to.active_element
        active.send_keys(text)
        return f"Typed via Selenium: {text}"
    except Exception as e:
        return f"Failed to type: {e}"


def press_key(key: str) -> str:
    """Press a keyboard key by name (e.g. 'enter', 'escape', 'ctrl+c')."""
    key = key.lower().strip()
    if HAS_PYAUTOGUI:
        try:
            if '+' in key:
                parts = [k.strip() for k in key.split('+')]
                pyautogui.hotkey(*parts)
            else:
                pyautogui.press(key)
            return f"Pressed key: {key}"
        except Exception as e:
            return f"Failed to press key {key}: {e}"
    # Fallback: Selenium
    KEY_MAP = {
        "enter": Keys.ENTER, "escape": Keys.ESCAPE, "tab": Keys.TAB,
        "backspace": Keys.BACKSPACE, "delete": Keys.DELETE,
        "space": Keys.SPACE, "up": Keys.ARROW_UP, "down": Keys.ARROW_DOWN,
        "left": Keys.ARROW_LEFT, "right": Keys.ARROW_RIGHT,
    }
    try:
        driver = _init_driver()
        active = driver.switch_to.active_element
        active.send_keys(KEY_MAP.get(key, key))
        return f"Pressed: {key}"
    except Exception as e:
        return f"Failed to press {key}: {e}"


def scroll(direction: str) -> str:
    """Scroll the active browser window up or down."""
    try:
        driver = _init_driver()
        amount = -600 if direction == "up" else 600
        driver.execute_script(f"window.scrollBy(0, {amount});")
        return f"Scrolled {direction}"
    except Exception as e:
        if HAS_PYAUTOGUI:
            scroll_amount = 5 if direction == "up" else -5
            pyautogui.scroll(scroll_amount)
            return f"Scrolled {direction} via pyautogui"
        return f"Failed to scroll: {e}"


def take_screenshot() -> str:
    """Take a screenshot and save to the Desktop."""
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(desktop, f"screenshot_{timestamp}.png")
    if HAS_PYAUTOGUI:
        pyautogui.screenshot(path)
        return f"Screenshot saved: {path}"
    try:
        driver = _init_driver()
        driver.save_screenshot(path)
        return f"Screenshot saved: {path}"
    except Exception as e:
        return f"Failed to take screenshot: {e}"


def control_volume(direction: str) -> str:
    """Adjust system volume using pyautogui or keyboard keys."""
    if HAS_PYAUTOGUI:
        if direction == "up":
            pyautogui.press("volumeup")
        elif direction == "down":
            pyautogui.press("volumedown")
        elif direction == "mute":
            pyautogui.press("volumemute")
        return f"Volume {direction}"
    return "pyautogui not available for volume control"


def open_folder(path: str) -> str:
    """Open a local folder on Windows."""
    try:
        os.startfile(path)
        return f"Opened folder: {path}"
    except Exception as e:
        return f"Failed to open folder: {e}"


def click_element(text: str) -> str:
    """Find and click a visible web element matching the text description in Selenium."""
    try:
        driver = _init_driver()
        # Single combined XPath querying self-element text, placeholder, or aria-label
        # Reduces wait overheads and potential sequential failures to one lookup
        xpath = (
            f"//*[self::a or self::button or self::span or self::div or @placeholder or @aria-label]"
            f"[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}') "
            f"or contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}') "
            f"or contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
        )
        try:
            element = WebDriverWait(driver, 2.5).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
        except Exception:
            element = None

        if element:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.1)
            element.click()
            return f"Clicked: '{text}'"
        else:
            return f"Element '{text}' not found or not clickable"
    except Exception as e:
        return f"Failed to click element: {e}"


def browser_back() -> str:
    try:
        driver = _init_driver()
        driver.back()
        return "Navigated back"
    except Exception as e:
        return f"Failed to go back: {e}"


def browser_forward() -> str:
    try:
        driver = _init_driver()
        driver.forward()
        return "Navigated forward"
    except Exception as e:
        return f"Failed to go forward: {e}"


def browser_refresh() -> str:
    try:
        driver = _init_driver()
        driver.refresh()
        return "Refreshed page"
    except Exception as e:
        return f"Failed to refresh: {e}"


def close_tab() -> str:
    try:
        driver = _init_driver()
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[-1])
            return "Closed tab"
        else:
            driver.get("about:blank")
            return "Reset to blank tab"
    except Exception as e:
        return f"Failed to close tab: {e}"


def new_tab() -> str:
    try:
        driver = _init_driver()
        driver.execute_script("window.open('about:blank', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])
        return "Opened new tab"
    except Exception as e:
        return f"Failed to open tab: {e}"


# ─── Step executor ────────────────────────────────────────────────────────────

def execute_steps(steps: List[Dict]) -> List[str]:
    """Execute a list of step dicts from the planner."""
    results = []
    for step in steps:
        action = step.get("step")
        if action == "open_application":
            results.append(open_application(step.get("app", "")))
        elif action == "navigate":
            results.append(navigate(step.get("url", "")))
        elif action == "open_folder":
            results.append(open_folder(step.get("path", "")))
        elif action == "close_application":
            results.append(close_application(step.get("app", "")))
        elif action == "click_element":
            results.append(click_element(step.get("text", "")))
        elif action == "type_query":
            results.append(type_text(step.get("query", "")))
        elif action == "press_key":
            results.append(press_key(step.get("key", "")))
        elif action == "press_enter":
            results.append(press_key("enter"))
        elif action == "scroll":
            results.append(scroll(step.get("direction", "down")))
        elif action == "screenshot":
            results.append(take_screenshot())
        elif action == "volume":
            results.append(control_volume(step.get("direction", "up")))
        elif action == "browser_back":
            results.append(browser_back())
        elif action == "browser_forward":
            results.append(browser_forward())
        elif action == "browser_refresh":
            results.append(browser_refresh())
        elif action == "close_tab":
            results.append(close_tab())
        elif action == "new_tab":
            results.append(new_tab())
        elif action == "fallback":
            results.append(step.get("message", "Unknown command"))
        else:
            results.append(f"Unhandled step: {step}")
    return results


def close_browser() -> str:
    global _driver
    if _driver is not None:
        try:
            _driver.quit()
            _driver = None
            return "Browser closed"
        except Exception as e:
            return f"Failed to close browser: {e}"
    return "No browser was open"


atexit.register(close_browser)
