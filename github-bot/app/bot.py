import logging
import os
from typing import Dict, Any

from fastapi import FastAPI, Request
from octokit import Octokit


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(levelname)s %(asctime)s %(name)s - %(message)s", "%H:%M:%S")

    file_handler = logging.FileHandler('app.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = get_logger(__name__)

app = FastAPI()

# Configuration
GITHUB_APP_ID = os.getenv('GITHUB_APP_ID', 'github_app_id')
GITHUB_PRIVATE_KEY = os.getenv('GITHUB_PRIVATE_KEY', 'github_private_key')


@app.post('/webhook')
async def handle_webhook(request: Request):
    # todo verify signature
    # signature = request.headers.get('x-hub-signature-256')
    # body = await request.body()

    # if not signature:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid signature"
    #     )

    event = request.headers.get('x-github-event')
    payload = await request.json()

    action = payload.get('action')

    for x in payload:
        logger.info(x)
    # logger.info(f'handling {event} - {payload}')

    if event == 'issue_comment' and action == 'created':
        await handle_issue_comment(payload)

    return {"status": "processed"}


async def handle_issue_comment(payload: Dict[str, Any]):
    """Handle issue comment events using Octokit.py"""
    comment = payload['comment']
    issue = payload['issue']
    repo = payload['repository']

    # Initialize Octokit client
    octokit = Octokit(auth='app', app_id=GITHUB_APP_ID, private_key=GITHUB_PRIVATE_KEY)

    # Post response comment
    response_message = f"👋 Thanks for your comment @{comment['user']['login']}! You said: \n\n> {comment['body']}"

    logger.info(response_message)

    await octokit.rest.issues.create_comment(
        owner=repo['owner']['login'],
        repo=repo['name'],
        issue_number=issue['number'],
        body=response_message
    )