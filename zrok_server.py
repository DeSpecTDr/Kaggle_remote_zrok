import subprocess
import argparse
from utils import Zrok
import string
import random

def generate_random_password(length=16):
    characters = (string.ascii_letters + string.digits + "!@#$%^*()-_=+{}[]<>.,?")
    return ''.join(random.choices(characters, k=length))


def main(args):
    if args.token.startswith('<') and args.token.endswith('>'):
        raise ValueError("Please provide an actual your zrok token")

    zrok = Zrok(args.token, args.name)
    
    if not Zrok.is_installed():
        Zrok.install()

    zrok.disable()
    zrok.enable()
    
    # Setup SSH server
    print("Setting up SSH server...")
    if args.authorized_keys_url:
        subprocess.run(["bash", "setup_ssh.sh", args.authorized_keys_url], check=True)
    else:
        subprocess.run(["bash", "setup_ssh.sh"], check=True)

    if args.password is not None:
        print(f"Setting password for root user: {args.password}")
        subprocess.run(f"echo 'root:{args.password}' | sudo chpasswd", shell=True, check=True)
    else:
        password = generate_random_password()
        print(f"Setting password for root user: {password}")
        subprocess.run(f"echo 'root:{password}' | sudo chpasswd", shell=True, check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Kaggle SSH connection setup')
    parser.add_argument('--token', help='zrok API token')
    parser.add_argument('--name', default='kaggle_server', help='Environment name to create (default: kaggle_server)')
    parser.add_argument('--authorized_keys_url', help='URL to authorized_keys file')
    parser.add_argument('--password', default=None, help='Password for root user, if not provided, a random password will be generated')
    args = parser.parse_args()

    if not args.token:
        args.token = input("Enter your zrok API token: ")
    
    try:
        main(args)
    except Exception as e:
        print(e)
        input("An error occurred. Press Enter to exit...")