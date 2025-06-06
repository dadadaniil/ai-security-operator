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
        handle_issue_comment(payload)
    # not reacting to push events because uploading too sloow

    return {"status": "processed"}


async def handle_issue_comment(payload: Dict[str, Any]):
    """Handle issue comment events using Octokit.py"""
    comment = payload['comment']
    issue = payload['issue']
    repo = payload['repository']

    owner = repo['owner']['login']
    repo_name = repo['name']
    issue_number = issue['number']

    body = comment['body']
    if str.startswith(body, '/requirements'):
        try:
            # todo call analyzer (post body of issue (saved as some file) to technical requirements endpoint)

            response_message = f"@{comment['user']['login']}, uploading issue text as technical requirements for the project."
        except Exception as e:
            response_message = f"@{comment['user']['login']}, failed uploading issue text as technical requirements for the project: {str(e)}."

        octokit.issues.create_comment(
            owner=owner,
            repo=repo_name,
            issue_number=issue_number,
            body=response_message
        )

        logger.info(f"Created comment: {owner} {repo_name} {issue_number} {response_message}")
    elif str.startswith(body, '/unit'):

        octokit.issues.create_comment(
            owner=owner,
            repo=repo_name,
            issue_number=issue_number,
            body=f"@{comment['user']['login']}, I will generate unit-tests and respond with new PR url."
        )

        try:
            feature_request = body[6:]  # skip '/unit ' part

            # todo call analyzer (post UnitTestRequest with feature request)

            pr_url = None # todo create pr

            response_message = f"@{comment['user']['login']}, generated unit-tests can be found at {pr_url}. Review carefully."
        except Exception as e:
            response_message = f"@{comment['user']['login']}, PR was not created, failed generating unit-tests: {str(e)}."

        octokit.issues.create_comment(
            owner=owner,
            repo=repo_name,
            issue_number=issue_number,
            body=response_message
        )

    elif str.startswith(body, '/attack'):
        response_message = f"@{comment['user']['login']}, I will perform security testing for project and provide a report here."

        octokit.issues.create_comment(
            owner=owner,
            repo=repo_name,
            issue_number=issue_number,
            body=response_message
        )

        # todo better call analyzer and exploiter
    else:
        return
