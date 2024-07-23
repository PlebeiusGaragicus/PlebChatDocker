import dotenv
dotenv.load_dotenv()

import logging
from src.logger import setup_logging
setup_logging()
logger = logging.getLogger(__name__)


from typing import List
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, PlainTextResponse

from src.graph.graph import graph
from src.common.commands import handle_commands
from src.common.payment import get_user_balance

#NOTE: adjust the endpoint in the pipeline module!
# from pipeline import PIPELINE_ENDPOINT
PIPELINE_ENDPOINT = "/template"


app = FastAPI()
logger.debug("app is built!")


# This is the data that the client (pipeline) sends to us
class PostRequest(BaseModel):
    user_message: str
    messages: List[dict]
    body: dict



#TODO: fix this endpoint name
@app.post(PIPELINE_ENDPOINT)
async def main(request: PostRequest):

    ########################################
    # CHECK IF THE USER IS RUNNING A COMMAND
    if request.user_message.startswith("/"):
        def call_command():
            return handle_commands(request)
        return StreamingResponse(call_command(), media_type="text/event-stream")


    ###############
    # CHECK BALANCE
    # user_balance = assure_positive_balance(request.body['user']['email'])

    try:
        user_balance = get_user_balance(lud16=request.body['user']['email'])
    # except UserNotRegistered as e:
    except Exception as e:
        #TODO: I think I have a new flow so I don't need this anymore
        error_message = f"Hello new user!  Type `/pay` to get started."
        return StreamingResponse(iter([error_message]), media_type="text/event-stream")

    if user_balance < 0: # assure_positive_balance(request.body['user']['email']):
        return StreamingResponse(iter(["Insufficient balance. Please top up your account."]), media_type="text/event-stream")

        # NOTE: This doesn't work... it still streams slowly WTF!?!
        # return PlainTextResponse(iter(["Insufficient balance. Please top up your account."]), media_type="text/plain")
    else:


        #######################
        # INVOKE THE GRAPH HERE
        async def event_stream():
            graph_input = {
                "messages": [request.messages[-1]],
                "lud16": request.body['user']['email']
            }

            config = {"configurable": {
                "lud16": request.body['user']['email']
            }}

            async for event in graph.astream_events(input=graph_input, config=config, version="v2"):
                kind = event["event"]
                if  kind == "on_chat_model_stream" or kind=="on_chain_stream":
                    content = event["data"]["chunk"]

                    if content:
                        if isinstance(content, dict):
                            yield ''
                            # pass
                        else:
                            print(content.content, end="")
                            yield content.content

        return StreamingResponse(event_stream(), media_type="text/event-stream")





# body: dict
# {
#     "stream": true,                   # ignore this...
#     "model": "pipeline_template",     # pipeline python filename?
#     "messages": [
#         {
#             "role": "user",
#             "content": "/version"
#         }
#     ],
#     "user": {
#         "name": "local_admin",
#         "id": "b1e31733-d29f-407a-a43a-0de19cfc84a6",
#         "email": "something@athing.com",
#         "role": "admin"
#     }
# }
