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
        raise Exception("kaggle environment not found. Are you running the Kaggle notebook cells?")

    share_token = None
    for share in env.get("shares", []):
        if (share.get("backendMode") == "tcpTunnel" and
            share.get("backendProxyEndpoint") == "localhost:22"):
            share_token = share.get("shareToken")
            break

    if not share_token:
        raise Exception("SSH tunnel not found in kaggle environment. Are you running the Kaggle notebook cells?")

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
    
    entry = """Host kaggle-local
    HostName 127.0.0.1
    User root
    Port 9191
    IdentityFile ~/.ssh/kaggle_rsa
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null""".strip("\n")

    if "Host kaggle-local" not in content:
        with open(config_path, 'w', encoding='utf-8', newline='') as f:
            f.write(content.rstrip("\n") + "\n" + entry)
    else:
        print("SSH config already contains kaggle-local entry")

    # 5. Launch VS Code remote-SSH
    print("Launching VS Code with remote SSH connection...")
    subprocess.Popen(
        ["code", "--remote", "ssh-remote+kaggle-local", "/kaggle/working"],
        shell=True,
        creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP
    )
    print("VS Code launched. Please wait for the connection to establish...")
    time.sleep(5)  # Give some time for VS Code to start


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Kaggle SSH connection setup')
    parser.add_argument('--token', help='zrok API token')
    parser.add_argument('--name', default='kaggle_client', help='Environment name to create (default: kaggle_client)')
    parser.add_argument('--server_name', default='kaggle_server', help='Server environment name (default: kaggle_server)')
    args = parser.parse_args()

    if not args.token:
        args.token = input("Enter your zrok API token: ")

    try:
        main(args)
    except Exception as e:
        print(e)
        input("An error occurred. Press Enter to exit...")
