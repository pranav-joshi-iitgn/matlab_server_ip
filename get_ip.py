import subprocess
import re
from github import Github, GithubException

# 1. Extraction Logic
def get_wifi_ip():
    data = subprocess.check_output(['ipconfig']).decode('utf-8')
    sections = data.split('\n\n')
    for section in sections:
        if "Wireless LAN adapter Wi-Fi" in section:
            match = re.search(r'IPv4 Address\. . . . . . . . . . . : ([\d\.]+)', section)
            if match:
                return match.group(1)
    return None

# 2. GitHub Configuration
REPO_NAME = "pranav-joshi-iitgn/matlab_server_ip"  # Change this
FILE_PATH = "README.md"                 # The name of the file in the repo

try:
    # Load token
    with open('token.txt', 'r') as f:
        GITHUB_TOKEN = f.read().strip()

    ip_address = get_wifi_ip()

    if ip_address:
        content = f"# System Wi-Fi IP\n\n**Current IPv4:** `{ip_address}`"
        
        # Initialize GitHub API
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)

        try:
            # Check if file exists to get its 'sha' (required for updates)
            contents = repo.get_contents(FILE_PATH)
            repo.update_file(
                path=FILE_PATH,
                message="Update Wi-Fi IP address",
                content=content,
                sha=contents.sha
            )
            print(f"Successfully updated {FILE_PATH} on GitHub.")
        
        except GithubException as e:
            if e.status == 404:
                # File doesn't exist, create it
                repo.create_file(
                    path=FILE_PATH,
                    message="Initial IP log",
                    content=content
                )
                print(f"Successfully created {FILE_PATH} on GitHub.")
            else:
                print(f"GitHub Error: {e}")
    else:
        print("Could not find Wi-Fi IP address.")

except FileNotFoundError:
    print("Error: token.txt not found.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")