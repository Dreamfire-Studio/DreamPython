from __future__ import annotations
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib3
import time, random, os, shutil, tempfile
from typing import Optional
from urllib.parse import urlparse


class SeleniumControllerBuilder:
    def __init__(self):
        # sensible defaults
        self._full_screen: bool = False
        self._headless: bool = False
        self._page_load_timeout: int = 20
        self._profile_path: Optional[str] = None
        self._profile_directory: Optional[str] = None
        self._copy_profile_to_temp: bool = True
        self._chrome_binary: Optional[str] = None
        self._allow_fallback_fresh_profile: bool = True
        self._import_cookies: bool = False
        self._attach_to_debugger: bool = False
        self._debugger_address: Optional[str] = "127.0.0.1:9222"

    # -------- chainable setters --------
    def full_screen(self, value: bool=True): self._full_screen = value; return self
    def headless(self, value: bool=True): self._headless = value; return self
    def page_load_timeout(self, seconds: int): self._page_load_timeout = seconds; return self
    def profile_path(self, path: str): self._profile_path = path; return self
    def profile_directory(self, name: str): self._profile_directory = name; return self
    def copy_profile_to_temp(self, value: bool=True): self._copy_profile_to_temp = value; return self
    def chrome_binary(self, path: str): self._chrome_binary = path; return self
    def allow_fallback_fresh_profile(self, value: bool=True): self._allow_fallback_fresh_profile = value; return self
    def import_cookies(self, value: bool=True): self._import_cookies = value; return self
    def attach_to_debugger(self, value: bool=True): self._attach_to_debugger = value; return self
    def debugger_address(self, addr: str): self._debugger_address = addr; return self

    # build -> controller
    def build(self) -> "SeleniumController":
        return SeleniumController(
            full_screen=self._full_screen,
            headless=self._headless,
            page_load_timeout=self._page_load_timeout,
            profile_path=self._profile_path,
            profile_directory=self._profile_directory,
            copy_profile_to_temp=self._copy_profile_to_temp,
            chrome_binary=self._chrome_binary,
            allow_fallback_fresh_profile=self._allow_fallback_fresh_profile,
            import_cookies=self._import_cookies,
            attach_to_debugger=self._attach_to_debugger,
            debugger_address=self._debugger_address,
        )


class SeleniumController:
    def __init__(
        self,
        *,
        full_screen: bool = False,
        headless: bool = False,
        page_load_timeout: int = 20,
        profile_path: Optional[str] = None,
        profile_directory: Optional[str] = None,
        copy_profile_to_temp: bool = True,
        chrome_binary: Optional[str] = None,
        allow_fallback_fresh_profile: bool = True,
        import_cookies: bool = False,
        attach_to_debugger: bool = False,
        debugger_address: Optional[str] = "127.0.0.1:9222",
    ):
        urllib3.disable_warnings()

        self._tmp_profile_dir = None
        self._cookies_imported_for: set[str] = set()
        self._import_cookies = import_cookies
        self._cookie_profile_path = profile_path
        self._cookie_profile_directory = profile_directory
        self.chrome_driver = None

        def build_options(user_data_dir: Optional[str]) -> Options:
            opts = Options()
            # when attaching, avoid headless and extra stealth flags; let real Chrome be itself
            if headless and not attach_to_debugger: opts.add_argument("--headless=new")

            if not attach_to_debugger:
                opts.add_argument("--disable-gpu")
                opts.add_argument("--no-sandbox")
                opts.add_argument("--disable-dev-shm-usage")
                opts.add_argument("--disable-blink-features=AutomationControlled")
                opts.add_argument("--window-size=1366,800")
                opts.add_argument("--disable-extensions")
                opts.add_argument("--disable-features=Translate,PreloadMediaEngagementData,MediaRouter")
                opts.add_argument("--no-first-run")
                opts.add_argument("--no-default-browser-check")
                opts.add_argument("--remote-debugging-port=0")
                opts.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
                opts.add_experimental_option("useAutomationExtension", False)
                opts.add_argument(
                    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
                )
                if user_data_dir:
                    opts.add_argument(f"--user-data-dir={user_data_dir}")
                    if profile_directory:
                        opts.add_argument(f"--profile-directory={profile_directory}")
            else:
                if debugger_address:
                    opts.debugger_address = debugger_address  # <-- attach

            if chrome_binary and os.path.isfile(chrome_binary):
                opts.binary_location = chrome_binary

            if not attach_to_debugger:
                opts.add_argument("--webrtc-ip-handling-policy=default_public_interface_only")
                opts.add_argument("--force-webrtc-ip-handling-policy=default_public_interface_only")

            return opts

        def copy_profile(src_path: str) -> str:
            tmp_root = tempfile.mkdtemp(prefix="df-chrome-prof-")
            dst = os.path.join(tmp_root, "User Data")
            def _ignore(dir, names):
                ignore_names = {"Cache", "Code Cache", "Service Worker", "GrShaderCache", "ShaderCache", "DawnCache"}
                return [n for n in names if n in ignore_names]
            shutil.copytree(src_path, dst, dirs_exist_ok=True, ignore=_ignore)
            self._tmp_profile_dir = tmp_root
            return dst

        launch_profile_dir = None
        if profile_path and not attach_to_debugger:
            abs_profile = os.path.abspath(profile_path)
            if copy_profile_to_temp:
                try:
                    launch_profile_dir = copy_profile(abs_profile)
                    print(f"[SeleniumController] Using TEMP copy of profile: {launch_profile_dir}")
                except Exception as e:
                    print(f"[SeleniumController] Failed to copy profile, launching directly: {e}")
                    launch_profile_dir = abs_profile
            else:
                launch_profile_dir = abs_profile
                print(f"[SeleniumController] Using LIVE profile (may be locked): {launch_profile_dir}")

        last_err = None
        for attempt in (1, 2):
            try:
                options = build_options(launch_profile_dir)
                self.chrome_driver = webdriver.Chrome(options=options, service=Service())
                self.chrome_driver.set_page_load_timeout(page_load_timeout)
                if full_screen and not headless and not attach_to_debugger:
                    try: self.chrome_driver.maximize_window()
                    except Exception: pass
                break
            except Exception as e:
                last_err = e
                print(f"[SeleniumController] Launch attempt {attempt} failed: {e}")
                if attach_to_debugger:
                    raise
                if not allow_fallback_fresh_profile or attempt == 2: raise
                try:
                    tmp_root = tempfile.mkdtemp(prefix="df-chrome-fresh-")
                    fresh_ud = os.path.join(tmp_root, "User Data")
                    os.makedirs(fresh_ud, exist_ok=True)
                    launch_profile_dir = fresh_ud
                    self._tmp_profile_dir = tmp_root
                    print(f"[SeleniumController] Falling back to FRESH temp profile: {launch_profile_dir}")
                except Exception as ce:
                    print(f"[SeleniumController] Failed to prepare fresh profile: {ce}")
                    raise e

        if self.chrome_driver is None and last_err:
            raise last_err

    @classmethod
    def from_builder(cls, builder: SeleniumControllerBuilder) -> "SeleniumController":
        return builder.build()

    # --------------- cookies ---------------
    def _load_chrome_cookies(self, domain: str):
        try:
            import browser_cookie3 as bc3
        except Exception as e:
            print(f"[SeleniumController] browser-cookie3 not installed: {e}")
            return []

        cookie_file = None
        if self._cookie_profile_path:
            base = os.path.abspath(self._cookie_profile_path)
            prof_dir = self._cookie_profile_directory or "Default"
            candidate = os.path.join(base, prof_dir, "Network", "Cookies")
            if os.path.exists(candidate): cookie_file = candidate
            else:
                candidate = os.path.join(base, prof_dir, "Cookies")
                if os.path.exists(candidate): cookie_file = candidate

        try:
            cj = bc3.chrome(domain_name=domain, cookie_file=cookie_file) if cookie_file else bc3.chrome(domain_name=domain)
        except Exception as e:
            print(f"[SeleniumController] Failed reading Chrome cookies for {domain}: {e}")
            return []

        cookies = []
        for c in cj:
            try:
                cookies.append({
                    "name": c.name,
                    "value": c.value,
                    "domain": c.domain,
                    "path": c.path or "/",
                    "secure": bool(getattr(c, "secure", False)),
                    **({"expiry": int(c.expires)} if getattr(c, "expires", None) else {}),
                })
            except Exception:
                continue
        return cookies

    def _inject_cookies_for_domain(self, url: str):
        if not hasattr(self, "_import_cookies") or not self._import_cookies: return
        parsed = urlparse(url)
        domain = (parsed.netloc or "").split(":")[0]
        if not domain or domain in self._cookies_imported_for: return
        base = f"{parsed.scheme}://{domain}/" if parsed.scheme else f"https://{domain}/"
        try:
            self.chrome_driver.get(base)
            cookies = self._load_chrome_cookies(domain)
            if not cookies:
                print(f"[SeleniumController] No cookies imported for {domain}")
                self._cookies_imported_for.add(domain); return
            try: self.chrome_driver.delete_all_cookies()
            except Exception: pass
            added = 0
            for ck in cookies:
                try:
                    if domain.endswith(ck.get("domain", "").lstrip(".")) or ck.get("domain", "").lstrip(".").endswith(domain):
                        self.chrome_driver.add_cookie(ck)
                        added += 1
                except Exception:
                    continue
            self._cookies_imported_for.add(domain)
            print(f"[SeleniumController] Imported {added} cookies for {domain}")
        except Exception as e:
            print(f"[SeleniumController] Cookie injection failed for {domain}: {e}")

    # --------------- helpers ---------------
    def _human_delay(self, base: float=0.6, jitter: float=0.5):
        time.sleep(base + random.random() * jitter)

    def return_webpage(self, webpage_url: str, sleep: float=1.0):
        self._inject_cookies_for_domain(webpage_url)
        self.chrome_driver.get(webpage_url)
        self._human_delay(sleep, 0.8)
        return self.update_webpage()

    def return_element(self, class_name: Optional[str]=None, id_name: Optional[str]=None):
        if class_name: return self.chrome_driver.find_element(By.CLASS_NAME, class_name)
        return self.chrome_driver.find_element(By.ID, id_name)

    def click_element(self, class_name: Optional[str]=None, id_name: Optional[str]=None, sleep: float=1.0):
        self.return_element(class_name, id_name).click()
        self._human_delay(sleep, 0.7)
        return self.update_webpage()

    def send_keys_to_element(self, input_value: str, class_name: Optional[str]=None, id_name: Optional[str]=None, sleep: float=1.0):
        el = self.return_element(class_name, id_name)
        el.send_keys(input_value)
        self._human_delay(sleep, 0.7)
        return self.update_webpage()

    def clear_element(self, class_name: Optional[str]=None, id_name: Optional[str]=None, sleep: float=1.0):
        el = self.return_element(class_name, id_name)
        el.clear()
        self._human_delay(sleep, 0.7)
        return self.update_webpage()

    def update_webpage(self):
        return BeautifulSoup(self.chrome_driver.page_source, "html.parser")

    def scroll_to_bottom(self):
        self.chrome_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self._human_delay(0.5, 0.6)

    def quit(self):
        try:
            if self.chrome_driver: self.chrome_driver.quit()
        finally:
            if self._tmp_profile_dir and os.path.isdir(self._tmp_profile_dir):
                try: shutil.rmtree(self._tmp_profile_dir, ignore_errors=True)
                except Exception: pass