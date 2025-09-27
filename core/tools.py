# core/tools.py - CONSOLIDATED VERSION

from langchain_core.tools import tool
from google import genai
from google.genai import types
from pathlib import Path
import subprocess
import platform
import json
import os
import webbrowser
import urllib.parse
import psutil

# =====================================================
# GROUP 1: INFORMATION & RESEARCH (Keep as-is - 3 tools)
# =====================================================

@tool
def web_search(query: str) -> str:
    """Search the web using Google's native search through Gemini. Perfect for current information, news, prices, versions, documentation, and recent events."""
    try:
        print(f"🌐 Searching for: {query}")
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Search for and provide detailed information about: {query}",
            config=types.GenerateContentConfig(tools=[grounding_tool])
        )
        
        print(f"✅ Google Search completed")
        result = response.text
        
        if hasattr(response, 'grounding_metadata') and response.grounding_metadata:
            sources = []
            if hasattr(response.grounding_metadata, 'grounding_chunks'):
                for chunk in response.grounding_metadata.grounding_chunks[:3]:
                    if hasattr(chunk, 'web') and chunk.web:
                        sources.append(f"• {chunk.web.uri}")
                
                if sources:
                    result += f"\n\nSources:\n" + "\n".join(sources)
        
        return result
        
    except Exception as e:
        print(f"❌ Google Search error: {str(e)}")
        return f"Web search encountered an error: {str(e)}. I'll answer based on my knowledge."

@tool
def read_documentation(url: str) -> str:
    """Read and analyze full documentation from a specific URL. Perfect for reading framework docs, API references, guides, and tutorials. Provide the direct URL to the documentation page."""
    try:
        print(f"📖 Reading documentation from: {url}")
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        url_tool = types.Tool(url_context=types.UrlContext())
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Read and provide a comprehensive summary of the documentation at: {url}. Focus on key features, usage examples, and important details for developers.",
            config=types.GenerateContentConfig(tools=[url_tool], max_output_tokens=1000)
        )
        
        print(f"✅ Documentation reading completed")
        return f"Documentation Summary from {url}:\n\n{response.text}"
        
    except Exception as e:
        print(f"❌ Documentation reading error: {str(e)}")
        return f"Failed to read documentation from {url}: {str(e)}"

@tool
def search_and_read_docs(framework_or_topic: str) -> str:
    """Search for official documentation and then read it. Perfect when you need to find and read docs for a specific framework, library, or topic. Example: 'Next.js deployment', 'React 19 features', 'FastAPI tutorial'."""
    try:
        print(f"🔍📖 Finding and reading docs for: {framework_or_topic}")
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        
        search_tool = types.Tool(google_search=types.GoogleSearch())
        url_tool = types.Tool(url_context=types.UrlContext())
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Find the official documentation for '{framework_or_topic}' and read the most relevant documentation page. Provide a comprehensive summary with key information, examples, and usage details.",
            config=types.GenerateContentConfig(tools=[search_tool, url_tool], max_output_tokens=1200)
        )
        
        print(f"✅ Documentation search and reading completed")
        return response.text
        
    except Exception as e:
        print(f"❌ Documentation search error: {str(e)}")
        return f"Failed to find and read documentation for {framework_or_topic}: {str(e)}"

# =====================================================
# GROUP 2: FILE & TERMINAL OPERATIONS (1 focused tool)
# =====================================================

@tool
def file_operations(action: str, path: str = "", content: str = "") -> str:
    """File and terminal operations. 
    
    FILE ACTIONS: 'create', 'read', 'update', 'list', 'mkdir'
    TERMINAL: 'run' (provide command in path parameter)
    
    Examples:
    - file_operations('create', 'app.js', 'console.log("hi")')  
    - file_operations('read', 'package.json')
    - file_operations('list', 'src/')
    - file_operations('run', 'npm install')
    """
    
    try:
        if action == "create":
            return _create_file(path, content)
        elif action == "read":
            return _read_file(path)
        elif action == "update":
            return _update_file(path, content)
        elif action == "list":
            return _list_directory(path or ".")
        elif action == "mkdir":
            return _create_directory(path)
        elif action == "run":
            return _run_terminal_command(path)  # path contains the command
        else:
            return "❌ Invalid action. Use: create, read, update, list, mkdir, run"
            
    except Exception as e:
        return f"❌ File operation failed: {str(e)}"

# =====================================================
# GROUP 3: GIT OPERATIONS (1 focused tool)
# =====================================================

@tool
def git_operations(action: str, message_or_files: str = "") -> str:
    """Git version control operations.
    
    ACTIONS: 'status', 'add', 'commit', 'push', 'pull', 'log'
    
    Examples:
    - git_operations('status')
    - git_operations('add', '.')  
    - git_operations('commit', 'Added new feature')
    - git_operations('push')
    """
    
    try:
        if action == "status":
            return _run_terminal_command("git status")
        elif action == "add":
            files = message_or_files or "."
            return _run_terminal_command(f"git add {files}")
        elif action == "commit":
            if not message_or_files:
                return "❌ Commit message required"
            return _run_terminal_command(f'git commit -m "{message_or_files}"')
        elif action == "push":
            return _run_terminal_command("git push")
        elif action == "pull":
            return _run_terminal_command("git pull")
        elif action == "log":
            return _run_terminal_command("git log --oneline -10")
        else:
            return "❌ Invalid action. Use: status, add, commit, push, pull, log"
            
    except Exception as e:
        return f"❌ Git operation failed: {str(e)}"

# =====================================================
# GROUP 4: SYSTEM CONTROLLER (1 consolidated tool)
# =====================================================

@tool
def system_controller(action: str, target: str = "", query: str = "") -> str:
    """Complete system and application control.
    
    APP ACTIONS: 'open', 'close', 'list'
    WEB ACTIONS: 'search' (target=platform, query=search_term), 'website' (target=url)
    SYSTEM: 'lock', 'sleep', 'volume_up', 'volume_down', 'mute'
    
    Examples:
    - system_controller('open', 'chrome')
    - system_controller('search', 'youtube', 'Python tutorials')  
    - system_controller('website', 'https://github.com')
    - system_controller('lock')
    """
    
    try:
        # App control
        if action == "open":
            return _open_application(target)
        elif action == "close":
            return _close_application(target)
        elif action == "list":
            return _list_user_applications()
            
        # Web control  
        elif action == "search":
            return _search_and_open_web(target, query)
        elif action == "website":
            return _open_website(target)
            
        # System control
        elif action in ["lock", "sleep", "volume_up", "volume_down", "mute"]:
            return _system_control(action)
        else:
            return "❌ Invalid action. Use: open, close, list, search, website, lock, sleep, volume_up, volume_down, mute"
            
    except Exception as e:
        return f"❌ System operation failed: {str(e)}"

# =====================================================
# HELPER FUNCTIONS (Internal - not tools)
# =====================================================

def _create_file(file_path: str, content: str) -> str:
    """Internal function to create files."""
    try:
        print(f"📝 Creating file: {file_path}")
        project_root = Path.cwd()
        full_path = project_root / file_path
        
        if not str(full_path.resolve()).startswith(str(project_root.resolve())):
            return "❌ File path must be within project directory"
        
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"✅ Created file: {file_path}"
    except Exception as e:
        return f"❌ Failed to create file: {str(e)}"

def _read_file(file_path: str) -> str:
    """Internal function to read files."""
    try:
        project_root = Path.cwd()
        full_path = project_root / file_path
        
        if not full_path.exists():
            return f"❌ File not found: {file_path}"
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"📄 Contents of {file_path}:\n{content}"
    except Exception as e:
        return f"❌ Failed to read file: {str(e)}"

def _update_file(file_path: str, content: str) -> str:
    """Internal function to update files."""
    try:
        project_root = Path.cwd()
        full_path = project_root / file_path
        
        if not str(full_path.resolve()).startswith(str(project_root.resolve())):
            return "❌ File path must be within project directory"
        
        if not full_path.exists():
            return f"❌ File not found: {file_path}"
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"✅ Updated file: {file_path}"
    except Exception as e:
        return f"❌ Failed to update file: {str(e)}"

def _list_directory(dir_path: str) -> str:
    """Internal function to list directories."""
    try:
        project_root = Path.cwd()
        full_path = project_root / dir_path
        
        if not full_path.exists():
            return f"❌ Directory not found: {dir_path}"
        
        items = []
        for item in sorted(full_path.iterdir()):
            if item.is_dir():
                items.append(f"📁 {item.name}/")
            else:
                size = item.stat().st_size
                items.append(f"📄 {item.name} ({size} bytes)")
        
        return f"Contents of {dir_path}:\n" + "\n".join(items)
    except Exception as e:
        return f"❌ Failed to list directory: {str(e)}"

def _create_directory(dir_path: str) -> str:
    """Internal function to create directories."""
    try:
        project_root = Path.cwd()
        full_path = project_root / dir_path
        
        if not str(full_path.resolve()).startswith(str(project_root.resolve())):
            return "❌ Directory path must be within project directory"
        
        full_path.mkdir(parents=True, exist_ok=True)
        return f"✅ Created directory: {dir_path}"
    except Exception as e:
        return f"❌ Failed to create directory: {str(e)}"

def _run_terminal_command(command: str) -> str:
    """Internal function to run terminal commands."""
    safe_commands = {
        'Windows': [
            'dir', 'copy', 'move', 'del', 'type', 'mkdir', 'rmdir', 'cd', 'md', 'rd',
            'findstr', 'where', 'tree', 'attrib', 'xcopy', 'robocopy',
            'npm', 'npx', 'node', 'python', 'pip', 'git', 'curl', 'code', 'notepad',
            'whoami', 'date', 'time', 'echo', 'set', 'path', 'ver',
            'choco', 'winget', 'powershell', 'cmd'
        ],
        'Darwin': [
            'ls', 'cp', 'mv', 'rm', 'cat', 'touch', 'mkdir', 'rmdir', 'cd', 'pwd',
            'head', 'tail', 'grep', 'find', 'which', 'tree', 'chmod', 'chown',
            'npm', 'node', 'python', 'pip', 'git', 'curl', 'wget', 'code', 'vim', 'nano',
            'whoami', 'date', 'echo', 'env', 'ps', 'top', 'kill', 'killall',
            'brew', 'open', 'pbcopy', 'pbpaste'
        ],
        'Linux': [
            'ls', 'cp', 'mv', 'rm', 'cat', 'touch', 'mkdir', 'rmdir', 'cd', 'pwd',
            'head', 'tail', 'grep', 'find', 'which', 'tree', 'chmod', 'chown',
            'npm', 'node', 'python', 'pip', 'git', 'curl', 'wget', 'code', 'vim', 'nano',
            'whoami', 'date', 'echo', 'env', 'ps', 'top', 'kill', 'killall',
            'apt', 'yum', 'systemctl'
        ]
    }
    
    current_os = platform.system()
    if current_os not in safe_commands:
        return f"❌ Unsupported operating system: {current_os}"
    
    cmd_parts = command.strip().split()
    if not cmd_parts:
        return "❌ Empty command"
    
    base_command = cmd_parts[0]
    allowed_commands = safe_commands[current_os]
    
    if base_command not in allowed_commands:
        return f"❌ Command '{base_command}' not allowed on {current_os}."
    
    try:
        print(f"💻 Executing: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, cwd=Path.cwd())
        output = result.stdout if result.stdout else result.stderr
        return f"💻 [{current_os}] {command}\n{output.strip()}"
    except subprocess.TimeoutExpired:
        return "❌ Command timed out (30 seconds)"
    except Exception as e:
        return f"❌ Command failed: {str(e)}"

def _analyze_project_structure(path: str) -> str:
    """Analyze project structure and provide insights."""
    try:
        project_path = Path.cwd() / path
        structure = []
        
        for item in project_path.rglob('*'):
            if item.is_file() and len(structure) < 50:  # Limit output
                rel_path = item.relative_to(project_path)
                structure.append(str(rel_path))
        
        return f"📊 Project Structure Analysis:\n" + "\n".join(f"• {item}" for item in sorted(structure))
    except Exception as e:
        return f"❌ Failed to analyze structure: {str(e)}"

def _detect_framework(path: str) -> str:
    """Detect framework used in project."""
    try:
        project_path = Path.cwd() / path
        frameworks = []
        
        # Check for common framework files
        if (project_path / "package.json").exists():
            frameworks.append("Node.js/JavaScript project")
        if (project_path / "requirements.txt").exists():
            frameworks.append("Python project")
        if (project_path / "next.config.js").exists():
            frameworks.append("Next.js")
        if (project_path / "src/App.js").exists():
            frameworks.append("React")
        if (project_path / "angular.json").exists():
            frameworks.append("Angular")
        
        if frameworks:
            return f"🔍 Detected frameworks: {', '.join(frameworks)}"
        else:
            return "❓ No specific framework detected"
            
    except Exception as e:
        return f"❌ Failed to detect framework: {str(e)}"

# Your existing helper functions for system operations
def _open_application(app_name: str) -> str:
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
    """Windows-specific application launcher with multiple strategies."""
    
    # Strategy 1: Try common full paths for popular applications
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
        'vscode': ['code'],  # Usually in PATH
        'code': ['code'],
        'notepad': ['notepad.exe'],
        'calculator': ['calc.exe'],
        'spotify': [
            r'%APPDATA%\Spotify\Spotify.exe',
            'spotify:'  # Protocol handler
        ],
        'figma': [
            r'%LOCALAPPDATA%\Figma\Figma.exe'
        ],
        'photoshop': [
            r'C:\Program Files\Adobe\Adobe Photoshop 2024\Photoshop.exe',
            r'C:\Program Files\Adobe\Adobe Photoshop 2020\Photoshop.exe',
            r'C:\Program Files (x86)\Adobe\Adobe Photoshop 2024\Photoshop.exe'
        ],
        'whatsapp': [
            r'%APPDATA%\Whatsapp\Whatsapp.exe',
            'whatsapp:'  # Protocol handler
            ],
        'word': ['winword.exe'],
        'excel': ['excel.exe'],
        'powerpoint': ['powerpnt.exe'],
        'teams': [
            r'%LOCALAPPDATA%\Microsoft\Teams\Update.exe --processStart "Teams.exe"'
        ]
    }
    
    app_lower = app_name.lower()
    
    # Strategy 1: Try known paths
    if app_lower in common_paths:
        for path in common_paths[app_lower]:
            try:
                # Expand environment variables
                expanded_path = os.path.expandvars(path)
                
                if path.endswith(':'):  # Protocol handler (like spotify:)
                    os.startfile(path)
                    return f"✅ Opened {app_name} via protocol"
                elif os.path.exists(expanded_path):
                    subprocess.Popen([expanded_path], shell=False)
                    return f"✅ Opened {app_name}"
                elif not expanded_path.startswith(('C:', '%')):  # Simple command
                    subprocess.Popen(path, shell=True)
                    return f"✅ Opened {app_name}"
            except Exception as e:
                continue
    
    # Strategy 2: Try Windows Start Menu search
    try:
        # Use PowerShell to search and launch via Start Menu
        powershell_cmd = f'''
        $app = Get-StartApps | Where-Object {{$_.Name -like "*{app_name}*"}} | Select-Object -First 1
        if ($app) {{
            Start-Process "shell:AppsFolder\\$($app.AppID)"
            Write-Output "Found: $($app.Name)"
        }} else {{
            Write-Output "Not found"
        }}
        '''
        
        result = subprocess.run(
            ['powershell', '-Command', powershell_cmd],
            capture_output=True,
            text=True,
            shell=True
        )
        
        if "Found:" in result.stdout:
            return f"✅ Opened {app_name} via Start Menu"
            
    except Exception as e:
        pass
    
    # Strategy 3: Try simple command (might work for some apps)
    try:
        subprocess.Popen(app_name, shell=True)
        return f"✅ Opened {app_name} (simple command)"
    except Exception:
        pass
    
    # Strategy 4: Try with .exe extension
    try:
        subprocess.Popen(f"{app_name}.exe", shell=True)
        return f"✅ Opened {app_name}.exe"
    except Exception:
        pass
    
    return f"❌ Could not find {app_name}. Try using the full application name or check if it's installed."

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
    pass

def _close_application(app_name: str) -> str:
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
        'file explorer': 'explorer.exe',
        'explorer': 'explorer.exe'
    }
    
    # Get the actual process name
    target_process = app_mappings.get(app_name.lower(), f"{app_name.lower()}.exe")
    
    closed_count = 0
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() == target_process.lower():
                proc.terminate()
                closed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if closed_count > 0:
        return f"✅ Closed {closed_count} instance(s) of {_get_friendly_app_name(app_name.lower())}"
    else:
        return f"❌ No running instances of {_get_friendly_app_name(app_name.lower())} found"

    pass

def _list_user_applications() -> str:
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
 
    pass

def _search_and_open_web(platform: str, query: str) -> str:
    try:
        print(f"🔍 Searching '{query}' on {platform}...")
        
        # URL patterns for different platforms
        search_urls = {
            'youtube': 'https://www.youtube.com/results?search_query={}',
            'google': 'https://www.google.com/search?q={}',
            'github': 'https://github.com/search?q={}',
            'stackoverflow': 'https://stackoverflow.com/search?q={}',
            'reddit': 'https://www.reddit.com/search/?q={}',
            'twitter': 'https://twitter.com/search?q={}',
            'linkedin': 'https://www.linkedin.com/search/results/all/?keywords={}',
            'medium': 'https://medium.com/search?q={}',
            'dev': 'https://dev.to/search?q={}',
            'npm': 'https://www.npmjs.com/search?q={}',
            'pypi': 'https://pypi.org/search/?q={}',
            'mdn': 'https://developer.mozilla.org/en-US/search?q={}'
        }
        
        platform_lower = platform.lower()
        if platform_lower not in search_urls:
            available = ', '.join(search_urls.keys())
            return f"❌ Platform '{platform}' not supported. Available: {available}"
        
        # Encode the query for URL
        encoded_query = urllib.parse.quote_plus(query)
        search_url = search_urls[platform_lower].format(encoded_query)
        
        # Open in default browser
        webbrowser.open(search_url)
        
        return f"✅ Opened {platform} search for '{query}'"
        
    except Exception as e:
        return f"❌ Failed to search {platform}: {str(e)}"
    pass

def _open_website(url: str) -> str:
    """Open any website URL in the default browser."""
    try:
        print(f"🌐 Opening website: {url}")
        
        # Add https:// if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        webbrowser.open(url)
        return f"✅ Opened {url}"
        
    except Exception as e:
        return f"❌ Failed to open website: {str(e)}"

    pass

def _system_control(action: str) -> str:
    try:
        os_type = platform.system()
        
        commands = {
            'Windows': {
                'lock': 'rundll32.exe user32.dll,LockWorkStation',
                'sleep': 'rundll32.exe powrprof.dll,SetSuspendState 0,1,0',
                'shutdown': 'shutdown /s /t 60',  # 60 second delay for safety
                'restart': 'shutdown /r /t 60',
                'volume_up': 'powershell -c "(New-Object -comObject WScript.Shell).SendKeys([char]175)"',
                'volume_down': 'powershell -c "(New-Object -comObject WScript.Shell).SendKeys([char]174)"',
                'mute': 'powershell -c "(New-Object -comObject WScript.Shell).SendKeys([char]173)"'
            },
            'Darwin': {
                'lock': 'pmset displaysleepnow',
                'sleep': 'pmset sleepnow',
                'shutdown': 'sudo shutdown -h +1',  # 1 minute delay
                'restart': 'sudo shutdown -r +1',
                'volume_up': 'osascript -e "set volume output volume (output volume of (get volume settings) + 10)"',
                'volume_down': 'osascript -e "set volume output volume (output volume of (get volume settings) - 10)"',
                'mute': 'osascript -e "set volume with output muted"'
            },
            'Linux': {
                'lock': 'gnome-screensaver-command -l',
                'sleep': 'systemctl suspend',
                'shutdown': 'shutdown +1',  # 1 minute delay
                'restart': 'shutdown -r +1',
                'volume_up': 'pactl set-sink-volume @DEFAULT_SINK@ +10%',
                'volume_down': 'pactl set-sink-volume @DEFAULT_SINK@ -10%',
                'mute': 'pactl set-sink-mute @DEFAULT_SINK@ toggle'
            }
        }
        
        os_commands = commands.get(os_type, {})
        command = os_commands.get(action.lower())
        
        if not command:
            available = ', '.join(os_commands.keys())
            return f"❌ Action '{action}' not available on {os_type}. Available: {available}"
        
        # Safety confirmation for destructive actions
        if action.lower() in ['shutdown', 'restart']:
            return f"⚠️ {action.title()} scheduled in 1 minute. Use 'shutdown -a' (Windows) or 'sudo shutdown -c' (Unix) to cancel."
        
        subprocess.run(command, shell=True)
        return f"✅ Executed {action}"
        
    except Exception as e:
        return f"❌ System control failed: {str(e)}"    

    pass
