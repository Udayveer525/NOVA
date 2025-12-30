"""Development Agent Tools."""

from langchain_core.tools import tool
from pathlib import Path
import subprocess
import os
import platform

 
@tool
def file_operations(action: str, path: str = "", content: str = "") -> str:
    """File and terminal operations.
    
    Actions: 'create', 'read', 'update', 'list', 'mkdir', 'mkdir_batch', 'run'
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
        elif action == "mkdir_batch":
            return _create_directories_batch(path)
        elif action == "run":
            return _run_terminal_command(path)  # path = command
        else:
            return "❌ Invalid action"
    except Exception as e:
        return f"❌ Error: {str(e)}"


@tool
def git_operations(action: str, message_or_files: str = "") -> str:
    """Git version control operations.
    
    Actions: 'status', 'add', 'commit', 'push', 'pull', 'log'
    """
    try:
        if action == "status":
            result = subprocess.run(['git', 'status'], capture_output=True, text=True)
            return f"📊 Git Status:\n{result.stdout}"
        
        elif action == "add":
            files = message_or_files or "."
            subprocess.run(['git', 'add', files], check=True)
            return f"✅ Added: {files}"
        
        elif action == "commit":
            subprocess.run(['git', 'commit', '-m', message_or_files], check=True)
            return f"✅ Committed: {message_or_files}"
        
        elif action == "push":
            subprocess.run(['git', 'push'], check=True)
            return "✅ Pushed to remote"
        
        elif action == "pull":
            subprocess.run(['git', 'pull'], check=True)
            return "✅ Pulled from remote"
        
        elif action == "log":
            result = subprocess.run(['git', 'log', '-5', '--oneline'], capture_output=True, text=True)
            return f"📜 Recent commits:\n{result.stdout}"
        
        else:
            return "❌ Invalid git action"
            
    except Exception as e:
        return f"❌ Git error: {str(e)}"


@tool
def project_status() -> str:
    """Get current project status and directory info."""
    try:
        cwd = os.getcwd()
        has_package_json = os.path.exists("package.json")
        dirs = [d for d in os.listdir(".") if os.path.isdir(d)]
        
        return f"""📍 PROJECT STATUS:
Directory: {cwd}
Has package.json: {has_package_json}
Folders: {', '.join(dirs[:10])}

⚠️ Verify location before creating files!"""
    except Exception as e:
        return f"❌ Error: {str(e)}"


# Helper functions (keep your existing implementations)
def _create_file(path, content):
    """Internal function to create files."""
    try:
        print(f"📝 Creating file: {path}")
        project_root = Path.cwd()
        full_path = project_root / path
        
        if not str(full_path.resolve()).startswith(str(project_root.resolve())):
            return "❌ File path must be within project directory"
        
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"✅ Created file: {path}"
    except Exception as e:
        return f"❌ Failed to create file: {str(e)}"


def _read_file(path):
    """Internal function to read files."""
    try:
        print(f"📂 Reading file: {path}")
        project_root = Path.cwd()
        full_path = project_root / path
        
        if not full_path.exists():
            return f"❌ File not found: {path}"
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"📄 Contents of {path}:\n{content}"
    except Exception as e:
        return f"❌ Failed to read file: {str(e)}"


def _update_file(path, content):
    """Internal function to update files."""
    try:
        print(f"🛠️ Updating file: {path}")
        project_root = Path.cwd()
        full_path = project_root / path
        
        if not str(full_path.resolve()).startswith(str(project_root.resolve())):
            return "❌ File path must be within project directory"
        
        if not full_path.exists():
            return f"❌ File not found: {path}"
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"✅ Updated file: {path}"
    except Exception as e:
        return f"❌ Failed to update file: {str(e)}"


def _list_directory(path):
    """Internal function to list directories."""
    try:
        print(f"📁 Listing directory: {path}")
        project_root = Path.cwd()
        full_path = project_root / path
        
        if not full_path.exists():
            return f"❌ Directory not found: {path}"
        
        items = []
        for item in sorted(full_path.iterdir()):
            if item.is_dir():
                items.append(f"📁 {item.name}/")
            else:
                size = item.stat().st_size
                items.append(f"📄 {item.name} ({size} bytes)")
        
        return f"Contents of {path}:\n" + "\n".join(items)
    except Exception as e:
        return f"❌ Failed to list directory: {str(e)}"


def _create_directory(path):
    """Internal function to create directories."""
    try:
        print(f"📂 Creating directory: {path}")
        project_root = Path.cwd()
        full_path = project_root / path
        
        if not str(full_path.resolve()).startswith(str(project_root.resolve())):
            return "❌ Directory path must be within project directory"
        
        full_path.mkdir(parents=True, exist_ok=True)
        return f"✅ Created directory: {path}"
    except Exception as e:
        return f"❌ Failed to create directory: {str(e)}"


def _create_directories_batch(paths):
    """Create multiple directories in one operation (comma-separated paths)."""
    try:
        if not paths or not paths.strip():
            return "❌ No directory paths provided"
        
        # Split by comma and clean whitespace
        dir_list = [p.strip() for p in paths.split(',') if p.strip()]
        
        if not dir_list:
            return "❌ No valid directory paths provided"
        
        project_root = Path.cwd()
        created = []
        failed = []
        
        for dir_path in dir_list:
            try:
                full_path = project_root / dir_path
                
                # Security check
                if not str(full_path.resolve()).startswith(str(project_root.resolve())):
                    failed.append(f"{dir_path} (outside project)")
                    continue
                
                # Create directory
                full_path.mkdir(parents=True, exist_ok=True)
                created.append(dir_path)
                
            except Exception as e:
                failed.append(f"{dir_path} ({str(e)})")
        
        # Build result message
        result = []
        if created:
            result.append(f"✅ Created {len(created)} directories:")
            for dir_path in created:
                result.append(f"  📁 {dir_path}")
        
        if failed:
            result.append(f"\n❌ Failed to create {len(failed)} directories:")
            for failure in failed:
                result.append(f"  ⚠️ {failure}")
        
        return "\n".join(result) if result else "❌ No directories created"
        
    except Exception as e:
        return f"❌ Batch directory creation failed: {str(e)}"


def _run_terminal_command(command):
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
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60, cwd=Path.cwd())
        output = result.stdout if result.stdout else result.stderr
        return f"💻 [{current_os}] {command}\n{output.strip()}"
    except subprocess.TimeoutExpired:
        return "❌ Command timed out (60 seconds)"
    except Exception as e:
        return f"❌ Command failed: {str(e)}"


# ... other helpers
