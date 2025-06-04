from fastapi import APIRouter, UploadFile

from api.data.vectorstore import *
from api.routers.document_router import upload_and_index_document

logger = logs.get_logger(__name__)

router = APIRouter(prefix="/hook", tags=["Hooks for GitHub and other services"])


@router.post("/github", response_model=dict)
async def process_hook(src: dict):

    event = src['event']
    payload = src['payload']

    if event == 'issues':
        action = payload['action']

        # New TR issue opened
        if action == 'opened':
            issue = src['issue']

            body = issue['body']
            filename = issue['url']

            with open(filename, 'wb', encoding='utf-8') as f:
                f.write(body)

                upload_file = UploadFile(f)

                await upload_and_index_document(upload_file, DataType.REQUIREMENTS)

    elif event == 'push':
        # fixme
        for commit in payload['commits']:
          for file in commit['added']:
              pass
              # add
          for file in commit['removed']:
              pass
              # remove
          for file in commit['modified']:
              pass
              # remove, add
