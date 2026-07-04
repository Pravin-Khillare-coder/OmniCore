# engine_automation.py - Automation Module using Playwright & PyAutoGUI
import os
import subprocess
import time
import atexit
from playwright.sync_api import sync_playwright

# Optional pyautogui support for keyboard/mouse actions
try:
    import pyautogui
    pyautogui.FAILSAFE = False
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

# Global Playwright session containers to keep the browser instance alive
_playwright_ctx = None
_browser = None
_page = None

def _get_page() -> "Page":
    """Initialize and retrieve the shared Playwright browser instance."""
    global _playwright_ctx, _browser, _page
    if _page is None:
        try:
            _playwright_ctx = sync_playwright().start()
            # Try to launch standard Google Chrome, fallback to bundled Chromium
            try:
                _browser = _playwright_ctx.chromium.launch(
                    headless=False,
                    channel="chrome",
                    args=["--start-maximized"]
                )
            except Exception:
                _browser = _playwright_ctx.chromium.launch(
                    headless=False,
                    args=["--start-maximized"]
                )
            # Create a context with viewport size matching maximize behavior
            context = _browser.new_context(no_viewport=True)
            _page = context.new_page()
        except Exception as e:
            raise RuntimeError(f"Playwright initialization failed: {e}")
    return _page

def close_playwright_browser():
    """Tear down browser session cleanly on process exit."""
    global _playwright_ctx, _browser, _page
    try:
        if _page:
            _page.close()
            _page = None
        if _browser:
            _browser.close()
            _browser = None
        if _playwright_ctx:
            _playwright_ctx.stop()
            _playwright_ctx = None
    except Exception:
        pass

atexit.register(close_playwright_browser)

# ─── Playwright Browser Actions ────────────────────────────────────────────────
def navigate(url: str) -> str:
    """Navigate the active browser tab to a URL."""
    try:
        page = _get_page()
        page.goto(url, wait_until="load", timeout=12000)
        return f"Successfully navigated to {url}"
    except Exception as e:
        return f"Navigation failed: {e}. Trying system fallback browser."

def click_element(text: str) -> str:
    """Search and click a button, link, or label containing matching text."""
    try:
        page = _get_page()
        # Search by text matching (case insensitive) or inputs matching labels
        selectors = [
            f"text={text}",
            f"button:has-text('{text}')",
            f"a:has-text('{text}')",
            f"[placeholder='{text}']",
            f"[aria-label*='{text}']"
        ]
        clicked = False
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                if locator.is_visible() and locator.is_enabled():
                    locator.scroll_into_view_if_needed()
                    locator.click(timeout=1500)
                    clicked = True
                    break
            except Exception:
                continue
        if clicked:
            return f"Clicked element matching '{text}'"
        else:
            # Fallback: try clicking center of screen if visually identified (PyAutoGUI helper)
            return f"Element '{text}' not clickable in Playwright viewport."
    except Exception as e:
        return f"Click element failed: {e}"

def type_text(query: str) -> str:
    """Type text query into the currently focused input field."""
    try:
        page = _get_page()
        # Find active element or look up standard input tags
        inputs = page.locator("input[type='text'], input:not([type]), textarea, [contenteditable='true']")
        count = inputs.count()
        typed = False
        for i in range(count):
            inp = inputs.nth(i)
            if inp.is_visible() and inp.is_editable():
                inp.fill(query)
                inp.press("Enter")
                typed = True
                break
        if typed:
            return f"Typed '{query}' in active input."
        else:
            # Fallback: key press typing via PyAutoGUI
            if HAS_PYAUTOGUI:
                pyautogui.write(query, interval=0.005)
                pyautogui.press("enter")
                return f"Typed '{query}' via system keyboard."
            return "No input field ready to receive text."
    except Exception as e:
        if HAS_PYAUTOGUI:
            pyautogui.write(query, interval=0.005)
            pyautogui.press("enter")
            return f"Typed '{query}' via system keyboard."
        return f"Failed to type: {e}"

def scroll(direction: str) -> str:
    try:
        page = _get_page()
        amount = -600 if direction == "up" else 600
        page.evaluate(f"window.scrollBy(0, {amount});")
        return f"Scrolled page {direction}"
    except Exception:
        if HAS_PYAUTOGUI:
            scroll_amt = 400 if direction == "up" else -400
            pyautogui.scroll(scroll_amt)
            return f"Scrolled desktop window {direction}"
        return "Scroll target unavailable"

def browser_back() -> str:
    try:
        _get_page().go_back()
        return "Navigated back"
    except Exception as e:
        return f"Back failed: {e}"

def browser_forward() -> str:
    try:
        _get_page().go_forward()
        return "Navigated forward"
    except Exception as e:
        return f"Forward failed: {e}"

def browser_refresh() -> str:
    try:
        _get_page().reload()
        return "Refreshed page"
    except Exception as e:
        return f"Refresh failed: {e}"

# ─── OS & Desktop Control ──────────────────────────────────────────────────────
def open_application(app: str) -> str:
    """Launch Windows applications."""
    EXE_MAP = {
        "chrome": "chrome.exe",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "explorer": "explorer.exe",
        "vs code": "code",
        "vscode": "code",
        "spotify": "spotify.exe"
    }
    target = EXE_MAP.get(app.lower(), app)
    try:
        subprocess.Popen(target, shell=True)
        return f"Launched application: {app}"
    except Exception as e:
        try:
            # Fallback startup helper
            subprocess.Popen(["cmd", "/c", "start", "", target], shell=True)
            return f"Launched via terminal link: {app}"
        except Exception as e2:
            return f"Failed to open {app}: {e2}"

def close_application(app: str) -> str:
    """Kill application processes on Windows."""
    PROC_MAP = {
        "chrome": "chrome.exe",
        "notepad": "notepad.exe",
        "calculator": "Calculator.exe",
        "paint": "mspaint.exe",
        "explorer": "explorer.exe",
        "spotify": "Spotify.exe"
    }
    target = PROC_MAP.get(app.lower(), app + ".exe")
    try:
        subprocess.run(["taskkill", "/f", "/im", target], capture_output=True)
        return f"Closed process: {app}"
    except Exception as e:
        return f"Failed to close process: {e}"

def press_key(key: str) -> str:
    """Press system key or combination."""
    if not HAS_PYAUTOGUI:
        return "PyAutoGUI offline, keypress bypassed."
    try:
        clean_key = key.lower().strip()
        if "+" in clean_key:
            parts = [p.strip() for p in clean_key.split("+")]
            pyautogui.hotkey(*parts)
        else:
            pyautogui.press(clean_key)
        return f"Pressed key combination: {key}"
    except Exception as e:
        return f"Keypress failed: {e}"

# ─── Step Executor Loop ────────────────────────────────────────────────────────
def execute_steps(steps: list) -> list:
    """Run steps list mapped from PlannerEngine."""
    results = []
    for step in steps:
        action = step.get("step")
        if action == "open_application":
            results.append(open_application(step.get("app", "")))
        elif action == "navigate":
            results.append(navigate(step.get("url", "")))
        elif action == "click_element":
            results.append(click_element(step.get("text", "")))
        elif action == "type_query":
            results.append(type_text(step.get("query", "")))
        elif action == "press_key":
            results.append(press_key(step.get("key", "")))
        elif action == "scroll":
            results.append(scroll(step.get("direction", "down")))
        elif action == "browser_back":
            results.append(browser_back())
        elif action == "browser_forward":
            results.append(browser_forward())
        elif action == "browser_refresh":
            results.append(browser_refresh())
        elif action == "wait_time":
            time.sleep(step.get("seconds", 1.0))
            results.append(f"Waited {step.get('seconds')}s")
        else:
            results.append(f"Unresolved helper command: {step}")
    return results
