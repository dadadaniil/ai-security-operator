import json
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

GITHUB_APP_ID = os.getenv('GITHUB_APP_ID')
GITHUB_PRIVATE_KEY = os.getenv('GITHUB_PRIVATE_KEY').strip('"')
GITHUB_PRIVATE_KEY = str.replace(GITHUB_PRIVATE_KEY, '\\n', '\n')


octokit = Octokit(auth='installation', app_id=GITHUB_APP_ID, private_key=GITHUB_PRIVATE_KEY)


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

    logger.info(payload)

    # wtf
    payload = json.loads(payload.get('payload'))

    action = payload.get('action')


    logger.info(f'handling {event} - {action}')

    if event == 'issue_comment' and action == 'created':
        handle_issue_comment(payload)

    return {"status": "processed"}


def handle_issue_comment(payload: Dict[str, Any]):
    comment = payload['comment']
    issue = payload['issue']
    repo = payload['repository']

    body = comment['body']
    if str.startswith(body, '/unit'):
        response_message = f"@{comment['user']['login']}, I will generate unit-tests and respond with new PR url."
    else:
        return

    owner = repo['owner']['login']
    repo_name = repo['name']
    issue_number = issue['number']

    octokit.issues.create_comment(
        owner=owner,
        repo=repo_name,
        issue_number=issue_number,
        body=response_message
    )

    logger.info(f"Created comment: {owner} {repo_name} {issue_number} {response_message}")
