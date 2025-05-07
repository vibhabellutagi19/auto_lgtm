from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import hmac
import hashlib
import os
from dotenv import load_dotenv
from typing import Dict, Any
import json
from lgtm import review_pr
from common.rich_logger import RichLogger

app = FastAPI()
logger = RichLogger()

def verify_github_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify that the webhook payload was sent by GitHub"""
    if not signature_header:
        return False
    
    try:
        webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        if not webhook_secret:
            logger.print_error("GITHUB_WEBHOOK_SECRET not set in environment variables")
            return False
            
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            payload_body,
            hashlib.sha256
        ).hexdigest()
        
        actual_signature = signature_header.replace('sha256=', '')
        return hmac.compare_digest(expected_signature, actual_signature)
    except Exception as e:
        logger.print_error(f"Error verifying signature: {str(e)}")
        return False

@app.post("/webhook")
async def github_webhook(request: Request):
    signature = request.headers.get("X-Hub-Signature-256")
    
    payload_body = await request.body()
    
    if not verify_github_signature(payload_body, signature):
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
        
        if not all([repo, pr_number]):
            raise HTTPException(status_code=400, detail="Missing required PR information")
        
        # Set environment variables for the review process
        os.environ["REPO_NAME"] = repo
        os.environ["PR_NUMBER"] = str(pr_number)
        
        # Trigger the review process
        review_pr(repo, pr_number)
        
        return JSONResponse(content={
            "message": "Review process triggered successfully",
            "repo": repo,
            "pr_number": pr_number
        })
        
    except Exception as e:
        logger.print_error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    load_dotenv()
    uvicorn.run(app, host="0.0.0.0", port=8000) 