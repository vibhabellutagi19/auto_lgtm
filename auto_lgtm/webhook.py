from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import hmac
import hashlib
import os
from auto_lgtm.lgtm import review_pr
from auto_lgtm.common.rich_logger import RichLogger
from auto_lgtm.services.secret_service import SecretService


SECRET_ID = os.getenv("SECRET_ID")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set")

app = FastAPI()
logger = RichLogger()

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy"}

def verify_github_signature(payload_body: bytes, signature_header: str, project_id: str) -> bool:
    """Verify that the webhook payload was sent by GitHub"""
    if not signature_header:
        return False
    
    try:
        secret_service = SecretService(project_id)
        webhook_secret = secret_service.get_secret(SECRET_ID, "github_webhook_secret")
        if not webhook_secret:
            logger.error("GitHub webhook secret not found in secrets")
            return False
            
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            payload_body,
            hashlib.sha256
        ).hexdigest()
        
        actual_signature = signature_header.replace('sha256=', '')
        return hmac.compare_digest(expected_signature, actual_signature)
    except Exception as e:
        logger.error(f"Error verifying signature: {str(e)}")
        return False

@app.post("/webhook")
async def github_webhook(request: Request):
    signature = request.headers.get("X-Hub-Signature-256")
    
    payload_body = await request.body()
    
    if not verify_github_signature(payload_body, signature, PROJECT_ID):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = await request.json()
    
    if request.headers.get("X-GitHub-Event") != "pull_request":
        return JSONResponse(content={"message": "Not a pull request event"})
    
    if payload.get("action") != "opened":
        return JSONResponse(content={"message": "Not a PR open event"})
    
    try:
        pr = payload.get("pull_request", {})
        repo = payload.get("repository", {}).get("name")
        pr_number = pr.get("number")
        github_owner = payload.get("repository", {}).get("owner", {}).get("login")
        
        if not all([repo, pr_number, github_owner]):
            logger.error("Missing required fields in payload")
            return JSONResponse(
                status_code=400,
                content={"error": "Missing required fields in payload"}
            )
        
        # Set environment variables for the review process
        os.environ["REPO_NAME"] = repo
        os.environ["PR_NUMBER"] = str(pr_number)
        
        review_pr(repo, pr_number, github_owner, PROJECT_ID)
        
        return JSONResponse(content={
            "message": "Review process triggered successfully",
            "repo": repo,
            "pr_number": pr_number
        })
        
    except Exception as e:
        logger.print_error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 