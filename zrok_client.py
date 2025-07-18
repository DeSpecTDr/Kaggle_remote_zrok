import os
import subprocess
import time
import argparse
from utils import Zrok


def main(args):
    zrok = Zrok(args.token, args.name)
    
    if not Zrok.is_installed():
        Zrok.install()

    zrok.disable()
    zrok.enable()

    # 1. Get zrok share token
    env = zrok.find_env(args.server_name)
    if env is None:
        raise Exception(f"{args.server_name} environment not found. Are you running the notebook?")

    share_token = None
    for share in env.get("shares", []):
        if (share.get("backendMode") == "tcpTunnel" and
            share.get("backendProxyEndpoint") == f"localhost:{args.port}"):
            share_token = share.get("shareToken")
            break

    if not share_token:
        raise Exception(f"SSH tunnel not found in {args.server_name} environment. Are you running the notebook?")

    # 2. Start zrok process
    print(f"zrok access private {share_token}")
    subprocess.Popen(
        ["cmd", "/k", f"zrok access private {share_token}"],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

    # 3. Wait 5 seconds for zrok connection
    time.sleep(5)

    # 4. Update SSH config
    config_path = os.path.join(os.environ['USERPROFILE'], '.ssh', 'config')
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    if not os.path.exists(config_path):
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write('')
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entry = f"""Host {args.name}
    HostName 127.0.0.1
    User root
    Port 9191
    IdentityFile ~/.ssh/kaggle_rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null""".strip("\n")

    if f"Host {args.name}" not in content:
        with open(config_path, 'w', encoding='utf-8', newline='') as f:
            f.write(content.rstrip("\n") + "\n" + entry)
    else:
        print(f"SSH config already contains {args.name} entry")

    # 5. Launch VS Code remote-SSH
    if not args.no_vscode:
        print("Launching VS Code with remote SSH connection...")
        subprocess.Popen(
            ["code", "--remote", f"ssh-remote+{args.name}", args.workspace],
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP
        )
        print("VS Code launched. Please wait for the connection to establish...")
        time.sleep(5)  # Give some time for VS Code to start


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Kaggle SSH connection setup')
    parser.add_argument('--token', type=str, help='zrok API token')
    parser.add_argument('--name', type=str, default='kaggle_client', help='zrok environment name and SSH config Host name (default: kaggle_client)')
    parser.add_argument('--server_name', type=str, default='kaggle_server', help='Server environment name (default: kaggle_server)')
    parser.add_argument('--port', type=int, default=22, help='SSH port (default: 22)')
    parser.add_argument('--no-vscode', action='store_true', help='Do not launch VS Code after setup')
    parser.add_argument('--workspace', type=str, default='/kaggle/working', help='Default workspace directory to open in VS Code remote session')
    args = parser.parse_args()

    if not args.token:
        args.token = input("Enter your zrok API token: ")

    try:
        main(args)
    except Exception as e:
        print(e)
        input("An error occurred. Press Enter to exit...")
