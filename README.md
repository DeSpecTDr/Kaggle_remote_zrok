# Kaggle GPU/TPU + VS Code + Unlimited SSH Tunneling — Now Made Easy!
This repository offers powerful features:

- Use **Kaggle’s free GPUs/TPUs** (T4×2, P100, TPU v3-8) for up to **30 hours per week in a Visual Studio Code environment**—develop just like you would locally!

- With **zrok’s 5 GB/day free tunneling**, you can bypass **ngrok’s 1 GB/month limit** without any hassle.

- Powered by **OpenZiti’s dual-plane architecture**, this setup is not only secure and scalable—but can be launched in just **3 simple steps**.






## zrok compare ngrok

| Feature                | zrok          | ngrok               |
| ---------------------- | ------------- | ------------------- |
| Data Transfer       | 150GB/month | 1GB/month           |
| Open Source        | Yes           | No                  |
| Credit Card Required | No          | Yes (for free plan) |
| Free Plan              | Yes           | Yes                 |
| Self-hosting           | Do your thing | Enterprise only     |
| Security Model         | Zero Trust Network | VPN-based tunneling |
| Connection Type	| P2P-first (relay as fallback) | Central relay-based |




## Setup

### Step 1 : Zrok 
Create an account at [zrok](https://zrok.io) and copy your auth token. Please checkout [docs](https://docs.zrok.io/docs/getting-started/#enabling-your-zrok-environment)

> [!NOTE]
>
> remember to change your account to starter plan that way you can use NetFoundry's public zrok instance.

### Step 2 : Run the Kaggle Notebook

Open the [link](https://www.kaggle.com/code/kayak0/kaggle-zrok), copy the notebook to your account, paste your zrok token, then run the session and execute the cells.

In Session options, change internet to on and start the session to run the example notebook cells.

- Default password is set to **0**
- No need to set up SSH keys (if you wnat, see the notice)

### Step 3 : Setup local machine

Install [**zrok**](https://docs.zrok.io/docs/guides/install/) and [**vscode**](https://code.visualstudio.com/download) on your local machine. Also, make sure to install the [**Remote-SSH**](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh) extension for VS Code.

Finally, run the zrok_client.py file in your local machine.

```bash
# When run code in IDEs like VSCode or Cursor, the IDE launches automatically and then closes immediately. Run it in the CLI instead.
python zrok_client.py
# or 
python zrok_client.py --token <zrok token>
```

## Notice
### 1. Setup SSH public key authentication

Kaggle notebooks are ephemeral Linux servers, so they don't use public key authentication by default.
However, you can still choose to use public key authentication if you prefer.

Follow the prompts. Save the keys in the location ~/.ssh/kaggle_rsa


```sh
ssh-keygen -t rsa -b 4096 -C "kaggle_remote_ssh" -f ~/.ssh/kaggle_rsa
```


Now you got the key pair, what you need to do now is pushing that key to whatever remote server that allows us to fetch it(google drive, or github, gitlab, ...), here i use github

Create a new repo, copy `~/.ssh/kaggle_rsa.pub` to that repo and push it to github(remember to make a public repo), now the public key is available on github, you now need to head over to that repository and click to the public key you've pushed now you click to raw button at the top right and copy the url

You can provide this URL as the authorized_keys_url argument when running zrok_server.py.

```sh
!python3 zrok_server.py --token <zrok token> --authorized_keys_url <key url>
```


### 2. you might want to transfer files around between local and remote, in our case we can use `rsync` for this:

```bash
# from local to remote
rsync -e "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i ~/.ssh/kaggle_rsa -p 9191" <path_to_the_local_file> root@127.0.0.1:/kaggle/working
```

```bash
# from remote to local
rsync -e "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i ~/.ssh/kaggle_rsa -p 9191" root@127.0.0.1:<path_to_the_remote_file> <destination_path_in_local>
```

### 3. To minimize exceptions, 
the environment is disabled and re-enabled each time the code runs. This approach helps maintain stability. The code can be modified to run faster, but doing so may lead to numerous errors. 

Also, there may be exceptional situations in these operations. In such cases, you should access https://api-v1.zrok.io/ and manually delete the conflicting environments.

### 4. Technically

The solution directly interacts with the Zrok official web console (API V1) over HTTP and fully exploits OpenZiti’s dual-plane architecture for secure, high-performance connectivity:

- Control Plane: A centralized authentication and management service that automatically retrieves and synchronizes user environment data in real time, eliminating repetitive setup tasks.

- Data Plane: A distributed P2P overlay network that attempts direct peer connections whenever possible and falls back to relay servers only when necessary, delivering high bandwidth and reliability at no cost.

This allows developers to experience a secure and efficient tunneling environment. The integration with Kaggle via SSH serves merely as one example by adapting the provided code, you can easily extend this advanced approach to other platforms and use cases.





# Acknowledgement
This project is based on [Kaggle_VSCode_Remote_SSH](https://github.com/buidai123/Kaggle_VSCode_Remote_SSH/tree/feat/zrok-integration)
