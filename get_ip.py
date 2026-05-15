import subprocess
import re
from github import Github, Auth, GithubException

def get_wifi_ip():
    """Extracts the IPv4 address specifically for the Wi-Fi adapter."""
    try:
        # Runs ipconfig and decodes output
        data = subprocess.check_output(['ipconfig']).decode('utf-8')
        
        # Split into blocks based on adapter headers
        sections = data.split('\n\n')
        
        for section in sections:
            # We target the specific Wi-Fi adapter header
            if "Wireless LAN adapter Wi-Fi" in section:
                # Regex looks for the IPv4 Address line and captures the digits
                match = re.search(r'IPv4 Address\. . . . . . . . . . . : ([\d\.]+)', section)
                if match:
                    return match.group(1)
        return None
    except Exception as e:
        print(f"Extraction Error: {e}")
        return None

def update_github():
    # 1. Configuration
    REPO_NAME = "pranav-joshi-iitgn/matlab_server_ip"
    FILE_PATH = "README.md"
    TOKEN_FILE = "token.txt"

    try:
        # 2. Read the token securely
        with open(TOKEN_FILE, 'r') as f:
            GITHUB_TOKEN = f.read().strip()

        # 3. Get the current IP
        ip_address = get_wifi_ip()
        if not ip_address:
            print("Failed to find an active Wi-Fi IPv4 address.")
            return

        # 4. Authenticate using the updated Auth.Token syntax
        auth = Auth.Token(GITHUB_TOKEN)
        g = Github(auth=auth)
        repo = g.get_repo(REPO_NAME)

        # Prepare the markdown content
        new_content = f"# MATLAB Server Status\n\n**Current Wi-Fi IP:** `{ip_address}`\n\n*Last updated: (Automated Script)*"

        try:
            # 5. Check if file exists to get the SHA (required for updating)
            contents = repo.get_contents(FILE_PATH)
            
            # If content is identical, skip update to avoid unnecessary commits
            # (Note: contents.decoded_content is bytes, so we decode it)
            if contents.decoded_content.decode('utf-8') == new_content:
                print("IP has not changed. No update needed on GitHub.")
                return

            repo.update_file(
                path=FILE_PATH,
                message=f"Update IP to {ip_address}",
                content=new_content,
                sha=contents.sha
            )
            print(f"Successfully updated {FILE_PATH} with IP: {ip_address}")

        except GithubException as e:
            if e.status == 404:
                # File doesn't exist yet, create it
                repo.create_file(
                    path=FILE_PATH,
                    message="Initial IP log creation",
                    content=new_content
                )
                print(f"Successfully created {FILE_PATH} with IP: {ip_address}")
            else:
                # Likely a 403 (Permissions) or 401 (Bad Token)
                print(f"GitHub Error ({e.status}): {e.data.get('message')}")
                print("Tip: Check if your token has 'repo' or 'contents:write' permissions.")

    except FileNotFoundError:
        print(f"Error: {TOKEN_FILE} not found in the script directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    update_github()