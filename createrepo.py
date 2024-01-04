from github import Github
import os
from dotenv import load_dotenv
from datetime import datetime
import hashlib
import requests
import argparse

def main():
    parser = argparse.ArgumentParser(description='Create a new repository and trigger the workflow.',
                                    prog='createrepo')
    parser.add_argument('testname', metavar='testname', type=str, help='Base test name to be used for the repo')
    parser.add_argument('username', metavar='username', type=str, help='Github username to be added as collaborator')

    try:
        args = parser.parse_args()
    except Exception as e:
        print(e)
        exit(2)

    # Load the .env file and get the PAT
    load_dotenv()
    PAT = os.environ.get("PAT")

    # Authenticate with GitHub using the PAT
    g = Github(PAT)

    # User who will own the new repo (should be the same user as the PAT)
    user = g.get_user()

    # Generate a unique name using the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S") + args.username

    # Create a hash of the timestamp
    hash_object = hashlib.sha256(timestamp.encode())
    hex_dig = hash_object.hexdigest()

    # Use part of the hash as the repo name (first 10 characters)
    repo_name = hex_dig[:16]

    # Create a new private repository
    new_repo = user.create_repo(
        name= args.testname + "-" + repo_name,  # Replace with your desired repo name
        private=True,  # Set to False if you want the repo to be public
        auto_init=True  # Initialize with a README (set to False if not needed)
    )

    print(f"Repository created: {new_repo.html_url}")

    # Username of the person you want to invite
    collaborator_username = args.username

    # Send an invitation to collaborate on the repository
    invitation = new_repo.add_to_collaborators(collaborator_username, permission="push")

    if invitation is not None:
        print(f"Invitation sent to {collaborator_username} to collaborate on {new_repo.name}")
    else:
        print(f"User {collaborator_username} is already a collaborator or invitation could not be sent.")

    print(f"Collaborator added: {new_repo.html_url}")

    # Set up the API URL for triggering the workflow
    owner = "talentsiv"  # Replace with your GitHub username or organization
    repo = args.testname + "-" + "base"  # Replace with your repository name
    workflow_file_name = "main.yml"  # Replace with your workflow file name
    api_url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_file_name}/dispatches"

    # The headers for authorization and accepting the JSON response
    headers = {
        "Authorization": f"token {PAT}",
        "Accept": "application/vnd.github.v3+json"
    }

    # The data payload with the reference and inputs for the workflow
    data = {
        "ref": "main",  # Branch to trigger the workflow on
        "inputs": {
            'target_repo': "clientsuccess-" + repo_name
        }
    }

    # Make the POST request to trigger the workflow
    response = requests.post(api_url, headers=headers, json=data)

    # Check the response
    if response.status_code == 204:
        print("Workflow dispatched successfully.")
    else:
        print(f"Failed to dispatch workflow. Status code: {response.status_code}. Response: {response.text}")


    # Close the Github object after use
    g.close()

if __name__ == '__main__':
    main()