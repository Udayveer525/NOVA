"""System Agent Tools."""

from langchain_core.tools import tool
import subprocess
import psutil
import webbrowser
import platform
import os
import winreg
from pathlib import Path


@tool
def system_controller(action: str, target: str = "", query: str = "") -> str:
    """Complete system and application control.
    
    Actions: 'open', 'close', 'list', 'search', 'website', 'lock', 'volume_up', 'volume_down', 'mute'
    
    Examples:
    - system_controller('open', 'chrome')
    - system_controller('search', 'youtube', 'React tutorials')
    - system_controller('website', 'https://github.com')
    """
    try:
        if action == "open":
            return _open_application(target)
        elif action == "close":
            return _close_application(target)
        elif action == "list":
            return _list_user_applications()
        elif action == "search":
            return _search_and_open_web(target, query)
        elif action == "website":
            return _open_website(target)
        elif action in ["lock", "sleep", "volume_up", "volume_down", "mute"]:
            return _system_control(action)
        else:
            return "❌ Invalid action"
    except Exception as e:
        return f"❌ System error: {str(e)}"


# Helper functions - Use your existing implementations from tools.py
def _find_app_in_registry(app_name: str) -> str:
    """Find application executable path from Windows Registry (FAST & RELIABLE)."""
    
    # Registry locations where Windows stores installed apps
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
    ]
    
    if(app_name.lower().endswith('.exe')):
        app_name.strip('.exe')
    
    # Try common executable name variations
    possible_names = [
        f"{app_name}.exe",
        f"{app_name.lower()}.exe",
        f"{app_name.capitalize()}.exe",
    ]
    
    for root_key, sub_key_path in registry_paths:
        for exe_name in possible_names:
            try:
                # Try to open the registry key for this app
                app_key_path = f"{sub_key_path}\\{exe_name}"
                key = winreg.OpenKey(root_key, app_key_path)
                
                # Read the default value (the executable path)
                exe_path, _ = winreg.QueryValueEx(key, "")
                winreg.CloseKey(key)
                
                # Verify the file actually exists
                if exe_path and Path(exe_path).exists():
                    return exe_path
                    
            except (FileNotFoundError, OSError):
                continue
            except Exception:
                continue
    
    return None

def _find_app_via_powershell(app_name: str) -> str:
    """Use PowerShell's Get-Command to find executables in PATH."""
    try:
        ps_command = f'(Get-Command {app_name} -ErrorAction SilentlyContinue).Source'
        
        result = subprocess.run(
            ['powershell', '-Command', ps_command],
            capture_output=True,
            text=True,
            timeout=5,
            shell=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            exe_path = result.stdout.strip()
            if Path(exe_path).exists():
                return exe_path
            
        return None
        
    except Exception:
        return None

def _open_via_start_menu(app_name: str) -> bool:
    """Open app using Windows Start Menu search (comprehensive coverage)."""
    try:
        ps_command = f'''
        $app = Get-StartApps | Where-Object {{$_.Name -like "*{app_name}*"}} | Select-Object -First 1
        if ($app) {{
            Start-Process "shell:AppsFolder\\$($app.AppID)"
            Write-Output "Success"
        }}
        '''
        
        result = subprocess.run(
            ['powershell', '-Command', ps_command],
            capture_output=True,
            text=True,
            timeout=10,
            shell=True
        )
        
        return "Success" in result.stdout
        
    except Exception:
        return False

def _get_common_app_paths(app_name: str) -> list:
    """Get list of common paths for popular applications (instant fallback)."""
    
    common_paths = {
        'chrome': [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe'
        ],
        'brave': [
            r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe',
            r'C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe',
            r'%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe'
        ],
        'edge': [
            r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
        ],
        'firefox': [
            r'C:\Program Files\Mozilla Firefox\firefox.exe',
            r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe'
        ],
        'vscode': ['code'],
        'code': ['code'],
        'notepad': ['notepad.exe'],
        'calculator': ['calc.exe'],
        'spotify': [
            r'%APPDATA%\Spotify\Spotify.exe',
        ],
        'discord': [
            r'%LOCALAPPDATA%\Discord\Update.exe --processStart Discord.exe',
        ],
        'figma': [
            r'%LOCALAPPDATA%\Figma\Figma.exe'
        ],
        'photoshop': [
            r'C:\Program Files\Adobe\Adobe Photoshop 2024\Photoshop.exe',
            r'C:\Program Files\Adobe\Adobe Photoshop 2025\Photoshop.exe',
        ],
        'word': ['winword.exe'],
        'excel': ['excel.exe'],
        'powerpoint': ['powerpnt.exe'],
    }
    
    return common_paths.get(app_name.lower(), [])


def _open_application(app_name: str) -> str:
    """Open application using your existing Windows app launcher logic."""
    try:
        print(f"🚀 Opening {app_name}...")
        
        os_type = platform.system()
        
        if os_type == 'Windows':
            return _open_windows_app(app_name)
        elif os_type == 'Darwin':
            return _open_macos_app(app_name)
        else:
            return _open_linux_app(app_name)
            
    except Exception as e:
        return f"❌ Failed to open {app_name}: {str(e)}"


def _open_windows_app(app_name: str) -> str:
    """
    Enhanced Windows application launcher with multi-strategy approach.
    Tries methods in order of speed and reliability.
    """
    
    app_lower = app_name.lower()
    print(f"🔍 Searching for {app_name}...")
    
    if("powerpoint" in app_name.lower().strip()):
        app_name = "powerpnt"
    elif("word" in app_name.lower().strip()):
        app_name = "winword"
    
    # ============================================
    # STRATEGY 1: Windows Registry (FASTEST & MOST RELIABLE)
    # ============================================
    print("  → Checking Windows Registry...")
    registry_path = _find_app_in_registry(app_name)
    if registry_path:
        try:
            subprocess.Popen([registry_path], shell=False)
            print(f"  ✅ Found in registry: {registry_path}")
            return f"✅ Opened {app_name}"
        except Exception as e:
            print(f"  ⚠️ Registry path found but failed to launch: {e}")
    
    # ============================================
    # STRATEGY 2: Common Known Paths (INSTANT FALLBACK)
    # ============================================
    print("  → Checking common installation paths...")
    common_paths = _get_common_app_paths(app_name)
    for path in common_paths:
        try:
            # Expand environment variables like %APPDATA%, %LOCALAPPDATA%
            expanded_path = os.path.expandvars(path)
            
            # Handle simple commands (like 'code', 'notepad.exe')
            if not expanded_path.startswith(('C:', 'D:', '%')):
                subprocess.Popen(path, shell=True)
                print(f"  ✅ Launched via command: {path}")
                return f"✅ Opened {app_name}"
            
            # Check if file exists at this path
            if os.path.exists(expanded_path):
                subprocess.Popen([expanded_path], shell=False)
                print(f"  ✅ Found at: {expanded_path}")
                return f"✅ Opened {app_name}"
                
        except Exception as e:
            continue
    
    # ============================================
    # STRATEGY 3: PowerShell Get-Command (QUICK PATH LOOKUP)
    # ============================================
    print("  → Using PowerShell Get-Command...")
    ps_path = _find_app_via_powershell(app_name)
    if ps_path:
        try:
            subprocess.Popen([ps_path], shell=False)
            print(f"  ✅ Found via PowerShell: {ps_path}")
            return f"✅ Opened {app_name}"
        except Exception as e:
            print(f"  ⚠️ PowerShell found path but launch failed: {e}")
    
    # ============================================
    # STRATEGY 4: Windows Start Menu (COMPREHENSIVE)
    # ============================================
    print("  → Searching Windows Start Menu...")
    if _open_via_start_menu(app_name):
        print(f"  ✅ Launched via Start Menu")
        return f"✅ Opened {app_name} via Start Menu"
    
    # ============================================
    # STRATEGY 5: Simple Command Attempts (LAST RESORT)
    # ============================================
    print("  → Trying simple command...")
    for attempt in [app_name, f"{app_name}.exe", app_lower, f"{app_lower}.exe"]:
        try:
            # FIRST: Check if command exists using 'where'
            check_result = subprocess.run(
                f'where {attempt}',
                capture_output=True,
                text=True,
                shell=True,
                timeout=3
            )
            
            # Only try to launch if 'where' found the command
            if check_result.returncode == 0 and check_result.stdout.strip():
                exe_path = check_result.stdout.strip().split('\n')[0]
                print(f"  → Found command at: {exe_path}")
                subprocess.Popen([exe_path], shell=False)
                print(f"  ✅ Launched: {attempt}")
                return f"✅ Opened {app_name}"
            
        except subprocess.TimeoutExpired:
            print(f"  ⏱️ Command check timed out for: {attempt}")
            continue
        except Exception as e:
            continue
    
    # ============================================
    # ALL STRATEGIES FAILED
    # ============================================
    print(f"  ❌ Could not find {app_name}")
    return f"❌ Could not find '{app_name}'. Please verify:\n  • The application is installed\n  • The name is spelled correctly\n  • Try using the full application name (e.g., 'Google Chrome' instead of 'chrome')"

def _open_macos_app(app_name: str) -> str:
    """macOS application launcher."""
    app_mappings = {
        'chrome': 'Google Chrome',
        'firefox': 'Firefox',
        'safari': 'Safari',
        'brave': 'Brave Browser',
        'edge': 'Microsoft Edge',
        'vscode': 'Visual Studio Code',
        'code': 'Visual Studio Code',
        'figma': 'Figma',
        'photoshop': 'Adobe Photoshop 2024',
        'spotify': 'Spotify',
        'discord': 'Discord'
    }
    
    app_to_open = app_mappings.get(app_name.lower(), app_name)
    command = f'open -a "{app_to_open}"'
    
    try:
        subprocess.Popen(command, shell=True)
        return f"✅ Opened {app_name}"
    except Exception as e:
        return f"❌ Failed to open {app_name}: {str(e)}"

def _open_linux_app(app_name: str) -> str:
    """Linux application launcher."""
    app_mappings = {
        'chrome': 'google-chrome',
        'firefox': 'firefox',
        'brave': 'brave-browser',
        'edge': 'microsoft-edge',
        'vscode': 'code',
        'code': 'code',
        'figma': 'figma-linux',
        'spotify': 'spotify',
        'discord': 'discord'
    }
    
    app_command = app_mappings.get(app_name.lower(), app_name.lower())
    
    try:
        subprocess.Popen([app_command])
        return f"✅ Opened {app_name}"
    except Exception as e:
        return f"❌ Failed to open {app_name}: {str(e)}"



def _close_application(app_name: str) -> str:
    """Close application safely."""
    # Map common names to process names
    app_mappings = {
        'chrome': 'chrome.exe',
        'browser': 'chrome.exe',
        'edge': 'msedge.exe',
        'firefox': 'firefox.exe',
        'brave': 'brave.exe',
        'vscode': 'code.exe',
        'code': 'code.exe',
        'discord': 'discord.exe',
        'teams': 'teams.exe',
        'slack': 'slack.exe',
        'spotify': 'spotify.exe',
        'photoshop': 'photoshop.exe',
        'figma': 'figma.exe',
        'word': 'winword.exe',
        'excel': 'excel.exe',
        'powerpoint': 'powerpnt.exe',
        'notepad': 'notepad.exe',
        'calculator': 'calc.exe',
        # SPECIAL HANDLING FOR EXPLORER
        'file explorer': 'explorer.exe',
        'explorer': 'explorer.exe'
    }
    
    app_lower = app_name.lower()
    
    # SAFETY CHECK: Never close explorer.exe
    if app_name.lower() in ['explorer', 'file explorer']:
        return "⚠️ Cannot close File Explorer - it's essential for Windows desktop. Use Windows key + E to open new windows instead."
    
    # Regular application closing for other apps
    target_process = app_mappings.get(app_lower, f"{app_lower}.exe")
    
    closed_count = 0
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() == target_process.lower():
                proc.terminate()
                closed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if closed_count > 0:
        return f"✅ Closed {closed_count} instance(s) of {_get_friendly_app_name(app_lower)}"
    else:
        return f"❌ No running instances of {_get_friendly_app_name(app_lower)} found"


def _list_user_applications() -> str:
    """List running user applications."""
    # Known user applications (common ones people actually use)
    user_apps = {
        # Browsers
        'chrome.exe', 'msedge.exe', 'firefox.exe', 'brave.exe', 'opera.exe', 'safari',
        
        # Development
        'code.exe', 'devenv.exe', 'pycharm64.exe', 'idea64.exe', 'sublime_text.exe',
        'notepad++.exe', 'atom.exe', 'webstorm64.exe', 'phpstorm64.exe',
        
        # Communication
        'discord.exe', 'teams.exe', 'slack.exe', 'zoom.exe', 'skype.exe', 'whatsapp.exe',
        'telegram.exe',
        
        # Media & Design
        'spotify.exe', 'vlc.exe', 'photoshop.exe', 'illustrator.exe', 'figma.exe',
        'canva.exe', 'obs64.exe', 'audacity.exe',
        
        # Office & Productivity
        'winword.exe', 'excel.exe', 'powerpnt.exe', 'notepad.exe', 'calc.exe',
        'onenote.exe', 'notion.exe', 'obsidian.exe',
        
        # Gaming & Entertainment
        'steam.exe', 'epicgameslauncher.exe', 'uplay.exe', 'origin.exe',
        
        # File Management
        'explorer.exe', 'totalcmd.exe', '7zfm.exe', 'winrar.exe',
        
        # System Tools (user-facing ones)
        'taskmgr.exe', 'cmd.exe', 'powershell.exe', 'windowsterminal.exe',
        'perfmon.exe', 'regedit.exe'
    }
    
    # Get running processes
    user_running_apps = []
    seen_apps = set()
    
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            print(f"🔍 Inspecting process: {proc.info['name']}")
            proc_name = proc.info['name'].lower()
            
            # Filter 1: Must be in our known user apps list
            if proc_name not in user_apps:
                continue
            
            # Filter 2: Avoid duplicates (same app name)
            clean_name = proc_name.replace('.exe', '')
            if clean_name in seen_apps:
                continue
            
            # Filter 3: Try to get window title for GUI apps (Windows only)
            if platform.system() == 'Windows':
                try:
                    import win32gui
                    import win32process
                    
                    def enum_windows_callback(hwnd, results):
                        if win32gui.IsWindowVisible(hwnd):
                            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                            if found_pid == proc.info['pid']:
                                window_title = win32gui.GetWindowText(hwnd)
                                if window_title.strip():  # Has a window title
                                    results.append((clean_name, window_title))
                                else:
                                    results.append((clean_name, ""))
                    
                    results = []
                    win32gui.EnumWindows(enum_windows_callback, results)
                    
                    if results:
                        seen_apps.add(clean_name)
                        app_display_name = _get_friendly_app_name(clean_name)
                        if results[0][1]:  # Has window title
                            user_running_apps.append(f"🪟 {app_display_name} - {results[0][1][:50]}...")
                        else:
                            user_running_apps.append(f"📱 {app_display_name}")
                    
                except ImportError:
                    # Fallback if win32gui not available
                    seen_apps.add(clean_name)
                    app_display_name = _get_friendly_app_name(clean_name)
                    user_running_apps.append(f"📱 {app_display_name}")
                    
            else:
                # Non-Windows systems
                seen_apps.add(clean_name)
                app_display_name = _get_friendly_app_name(clean_name)
                user_running_apps.append(f"📱 {app_display_name}")
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
            continue
    
    if not user_running_apps:
        return "🖥️ No major user applications currently running"
    
    # Sort and format nicely
    user_running_apps.sort()
    return f"🖥️ Currently running applications:\n" + "\n".join(user_running_apps)

def _get_friendly_app_name(proc_name: str) -> str:
    """Convert process names to friendly display names."""
    friendly_names = {
        'chrome': 'Google Chrome',
        'msedge': 'Microsoft Edge', 
        'firefox': 'Mozilla Firefox',
        'brave': 'Brave Browser',
        'code': 'VS Code',
        'devenv': 'Visual Studio',
        'discord': 'Discord',
        'teams': 'Microsoft Teams',
        'slack': 'Slack',
        'spotify': 'Spotify',
        'photoshop': 'Adobe Photoshop',
        'figma': 'Figma',
        'winword': 'Microsoft Word',
        'excel': 'Microsoft Excel',
        'powerpnt': 'PowerPoint',
        'explorer': 'File Explorer',
        'notepad': 'Notepad',
        'calc': 'Calculator',
        'cmd': 'Command Prompt',
        'powershell': 'PowerShell',
        'windowsterminal': 'Windows Terminal',
        'taskmgr': 'Task Manager'
    }
    
    return friendly_names.get(proc_name, proc_name.title())


def _search_and_open_web(platform_name: str, query: str) -> str:
    """Search on web platforms (YouTube, GitHub, etc.)."""
    platforms = {
        'youtube': f'https://www.youtube.com/results?search_query={query.replace(" ", "+")}',
        'github': f'https://github.com/search?q={query.replace(" ", "+")}',
        'stackoverflow': f'https://stackoverflow.com/search?q={query.replace(" ", "+")}',
        'google': f'https://www.google.com/search?q={query.replace(" ", "+")}',
        'stackoverflow': f'https://stackoverflow.com/search?q={query.replace(" ", "+")}',
        'reddit': f'https://www.reddit.com/search/?q={query.replace(" ", "+")}',
        'twitter': f'https://twitter.com/search?q={query.replace(" ", "+")}',
        'linkedin': f'https://www.linkedin.com/search/results/all/?keywords={query.replace(" ", "+")}',
        'medium': f'https://medium.com/search?q={query.replace(" ", "+")}',
        'dev': f'https://dev.to/search?q={query.replace(" ", "+")}',
        'npm': f'https://www.npmjs.com/search?q={query.replace(" ", "+")}',
        'pypi': f'https://pypi.org/search/?q={query.replace(" ", "+")}',
        'mdn': f'https://developer.mozilla.org/en-US/search?q={query.replace(" ", "+")}'
    }
    
    url = platforms.get(platform_name.lower())
    if url:
        webbrowser.open(url)
        return f"✅ Opened {platform_name} search: {query}"
    else:
        return f"❌ Unknown platform: {platform_name}"


def _open_website(url: str) -> str:
    """Open website in browser."""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    webbrowser.open(url)
    return f"✅ Opened {url}"


def _system_control(action: str) -> str:
    """Execute system control actions."""
    os_type = platform.system()
    
    if os_type == 'Windows':
        commands = {
            'lock': 'rundll32.exe user32.dll,LockWorkStation',
            'sleep': 'rundll32.exe powrprof.dll,SetSuspendState 0,1,0',
            'volume_up': 'powershell -c "(New-Object -comObject WScript.Shell).SendKeys([char]175)"',
            'volume_down': 'powershell -c "(New-Object -comObject WScript.Shell).SendKeys([char]174)"',
            'mute': 'powershell -c "(New-Object -comObject WScript.Shell).SendKeys([char]173)"',
        }
        
        command = commands.get(action.lower())
        if command:
            subprocess.run(command, shell=True)
            return f"✅ Executed {action}"
    
    return f"❌ Action {action} not supported on {os_type}"

