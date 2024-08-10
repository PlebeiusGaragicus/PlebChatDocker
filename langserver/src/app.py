import os
import dotenv
dotenv.load_dotenv()

import logging
from src.logger import setup_logging
setup_logging()
logger = logging.getLogger(__name__)


from typing import List
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# from langserver.src.test_graph.commands import handle_commands
from src.payment import get_user_balance



app = FastAPI()


from src.graphs.graph_template.commands import TestBot
from src.graphs.plebchat.commands import PlebChat
ALL_CONSTRUCTS = [TestBot, PlebChat]


def get_construct(graph_name: str):
    for graph in ALL_CONSTRUCTS:
        if graph_name == graph.graph_name:
            # return graph()._get_graph()
            return graph()

    raise NotImplementedError(f"Graph {graph_name} is not implemented.")






# This is the data that the client (pipeline) sends to us
class PostRequest(BaseModel):
    user_message: str
    messages: List[dict]
    body: dict


#NOTE: adjust the endpoint in the pipeline module!
# from pipeline import PIPELINE_ENDPOINT
# nvm we can't do that
PIPELINE_ENDPOINT = "/langserver"
@app.post(PIPELINE_ENDPOINT)
async def main(request: PostRequest):

    logger.debug(f"request: {request}")

    construct = get_construct(request.body['graph_name'])


    ########################################
    # CHECK IF THE USER IS RUNNING A COMMAND
    if request.user_message.startswith("/"):
        # for graph in ALL_CONSTRUCTS:
        #     if request.body['graph_name'] == graph.graph_name:
        #         ret = graph()._handle_command(request=request)
        #         break
        command_output = construct._handle_command(request=request)
        return StreamingResponse(command_output, media_type="text/event-stream")


    ########################################
    # CHECK BALANCE
    is_admin = request.body['user']['role'] == "admin"
    if not is_admin:
        try:
            user_balance = get_user_balance(lud16=request.body['user']['email'])
            user_balance = user_balance['balance']
            logger.debug(f"User balance: {user_balance}")

        except Exception as e:
            if os.getenv("DEBUG", None):
                # NOTE: hide the error message details from the user unless we're debugging!
                error_message = f"There was an error checking your balance:\n`{e}`"
            else:
                error_message = f"There was an error checking your balance."

            return StreamingResponse(iter([error_message]), media_type="text/event-stream")

        if user_balance is None:
            # command_output = construct.buy(request=request)
            command_output = construct.bal(request=request) # /bal gives a good message when you're a new unregistered user
            return StreamingResponse(command_output, media_type="text/event-stream")
            # return StreamingResponse(iter(["Your token balance has run out - pay for more tokens by typing '/pay'."]), media_type="text/event-stream")

        ########################################
        # check if the user says 'hi'
        if request.user_message.lower() == 'hi':
            return StreamingResponse(construct.hi(request=request), media_type="text/event-stream")

        if user_balance < 0:
            # TODO - say the user's name and tell them something nicer
            return StreamingResponse(iter(["Your token balance has run out - pay for more tokens by typing '/pay'."]), media_type="text/event-stream")


    #####################################
    # INVOKE THE GRAPH
    async def event_stream():
        graph_input = {
            # "query": request.user_message,
            # "messages": request.messages[:-1],
            "messages": request.messages,
        }

        config = {"configurable": {
            "is_admin": is_admin,
            "lud16": request.body['user']['email'],
            # "thread_id": request.body['chat_id'], # refer to usage.py's deduct_with_usage() for why this is commented out
            "chat_id": request.body['chat_id'],
        }}

        # graph = return_graph(request.body['graph_name'])
        graph = construct._get_computable_graph()

        # async for event in graph.astream_events(input=graph_input, config=config, version="v2"):
        # async for event in return_graph(request.body['graph_name']).astream_events(input=graph_input, config=config, version="v2"):
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
#     "stream": true,                   # NOTE: we ignore this...
#     "model": "pipeline_template",     # pipeline python filename
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
