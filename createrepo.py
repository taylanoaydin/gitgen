from github import Github
import os
from dotenv import load_dotenv
from datetime import datetime
import hashlib
import requests

# gets the base repo name and the collaborator username as arguments
def main(tst, cusr):
    # Load the .env file and get the PAT
    load_dotenv()
    PAT = os.environ.get("PAT")

    # Authenticate with GitHub using the PAT
    g = Github(PAT)
    user = g.get_user()

    # Generate a unique name using the current timestamp and username
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S") + cusr
    hash_object = hashlib.sha256(timestamp.encode())
    hex_dig = hash_object.hexdigest()

    # Use part of the hash as the repo name (first 10 characters)
    repo_name = hex_dig[:16]

    # Create a new private repository
    new_repo = user.create_repo(
        name= tst + "-" + repo_name,  # creates a unique repo name using the base name and the hash
        private=True,  
        auto_init=True 
    )

    print(f"Repository created: {new_repo.html_url}")

    # Username of the person you want to invite
    collaborator_username = cusr

    # Send an invitation to collaborate on the repository
    invitation = new_repo.add_to_collaborators(collaborator_username, permission="push")

    if invitation is not None:
        print(f"Invitation sent to {collaborator_username} to collaborate on {new_repo.name}")
    else:
        print(f"User {collaborator_username} is already a collaborator or invitation could not be sent.")

    print(f"Collaborator added: {new_repo.html_url}")

    # Set up the API URL for triggering the workflow
    owner = "talentsiv"  # Replace with the owner of the base repository
    repo = tst + "-" + "base"  # Assumes existence of tst + "-base" repo owned by owner
    workflow_file_name = "main.yml" # Assumes main.yml workflow file in the base repo
    api_url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_file_name}/dispatches"

    # The headers for authorization and accepting the JSON response
    headers = {
        "Authorization": f"token {PAT}",
        "Accept": "application/vnd.github.v3+json"
    }

    # The data payload with the reference and inputs for the workflow
    data = {
        "ref": "main",
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
    return new_repo.html_url

if __name__ == '__main__':
    main()