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

#NOTE: adjust the endpoint in the pipeline module!
# from pipeline import PIPELINE_ENDPOINT
PIPELINE_ENDPOINT = "/langserver"


app = FastAPI()
logger.debug("app is built!")




def return_graph(graph_name: str):
    if graph_name == "testing":
        from src.test_graph.graph import graph
        return graph

    raise NotImplementedError(f"Graph {graph_name} is not implemented.")


def return_bot_commands(request):
    if request == "testing":
        from src.test_graph.commands import CustomBot
        return CustomBot()._handle_command(request)

    raise NotImplementedError(f"Command {command} is not implemented.")




# This is the data that the client (pipeline) sends to us
class PostRequest(BaseModel):
    user_message: str
    messages: List[dict]
    body: dict


# def handle_generic_commands(request: PostRequest):
#     logger.warning("User NOT running a generic command")
#     return None


#TODO: fix this endpoint name
@app.post(PIPELINE_ENDPOINT)
async def main(request: PostRequest):

    ########################################
    # CHECK IF THE USER IS RUNNING A COMMAND
    if request.user_message.startswith("/"):

        if request.body['graph_name'] == 'testing':
            from src.test_graph.commands import CustomBot
            ret = CustomBot()._handle_command(request=request)
        else:
            ret = "Your bot doesn't have any commands implemented."

        return StreamingResponse(ret, media_type="text/event-stream")


    ###############
    # CHECK BALANCE
    # user_balance = assure_positive_balance(request.body['user']['email'])

    try:
        user_balance = get_user_balance(lud16=request.body['user']['email'])
        user_balance = user_balance['balance']
        # logger.critical(user_balance)
    # except UserNotRegistered as e:
    except Exception as e:
        if os.getenv("DEBUG", None):
            # NOTE: hide the error message details from the user unless we're debugging!
            error_message = f"There was an error checking your balance:\n`{e}`"
        else:
            error_message = f"There was an error checking your balance."

        return StreamingResponse(iter([error_message]), media_type="text/event-stream")

    if user_balance is None or user_balance < 0: # assure_positive_balance(request.body['user']['email']):
        # TODO - say the user's name and tell them something nicer
        return StreamingResponse(iter(["Insufficient balance. Please top up your account."]), media_type="text/event-stream")


    else:
        # INVOKE THE GRAPH HERE #######################
        async def event_stream():
            graph_input = {
                "messages": [request.messages[-1]],
                "lud16": request.body['user']['email']
            }

            config = {"configurable": {
                "lud16": request.body['user']['email']
            }}

            # from src.test_graph.graph import graph
            # TODO - pick a different graph based on the body (the pipeline should inject the graph name)


            # async for event in graph.astream_events(input=graph_input, config=config, version="v2"):
            async for event in return_graph(request['graph_name']).astream_events(input=graph_input, config=config, version="v2"):
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
