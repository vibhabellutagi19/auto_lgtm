import os
from auto_lgtm.common.github_client import GitHubApiClient
from auto_lgtm.services.github_service import GitHubService, GitHubServiceError

# --- CONFIGURE THESE ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "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")  # Set this in your shell!
GITHUB_OWNER = "vibhabellutagi19"         
GITHUB_REPO = "lgtm_test"                
PR_NUMBER = 9                            

def main():
    if not GITHUB_TOKEN:
        print("Please set the GITHUB_TOKEN environment variable.")
        return
    client = GitHubApiClient(token=GITHUB_TOKEN, owner=GITHUB_OWNER)
    service = GitHubService(api_client=client)

    try:
        print(f"Fetching diff for PR #{PR_NUMBER} in {GITHUB_OWNER}/{GITHUB_REPO}...")
        structured_diff = service.fetch_pr_diff(GITHUB_REPO, PR_NUMBER)
        print("Structured diff:")
        for file_diff in structured_diff:
            print(f"File: {file_diff['file']}")
            for chunk in file_diff['chunks']:
                print(f"  Chunk: {chunk}")
        print("Success!")
    except GitHubServiceError as e:
        print(f"GitHubServiceError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()