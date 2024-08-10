import json
import requests
from typing_extensions import TypedDict

from typing import List, Union, Generator, Iterator, Optional
try:
    from pydantic.v1 import BaseModel
except Exception:
    from pydantic import BaseModel


########################################################################
# This is shown in the UI to the user
AGENT_NAME = "LangGraph graph_template"

# This is used to identify the approprate graph in the Langserver
# NOTE: This must match exactly with the graph_name variable in your inherited BotCommandHandler class!
GRAPH_NAME = "graph_template"

# Settings for this pipeline
HARD_DISABLE_TITLE_GENERATION = False

# Langserver endpoint
LANGSERVE_ENDPOINT = f"http://host.docker.internal"
PORT = 8513
PIPELINE_ENDPOINT = "/langserver"
########################################################################


class PostRequest(TypedDict):
    user_message: str
    messages: List[dict]
    body: dict


class Pipeline:
    class Valves(BaseModel):
        pass

    def __init__(self):
        self.name = AGENT_NAME
        self.graph_name = GRAPH_NAME
        self.chat_id = None


    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        print(f"inlet:{__name__}")
        print(f"user: {user}")
        print(f"body: {body}")

        if body.get("task") == "title_generation":
            print("################# Title Generation #################")
            body['ignore'] = True

        # Store the chat_id from body
        self.chat_id = body.get("chat_id")
        print(f"Stored chat_id: {self.chat_id}")

        return body


    # async def on_startup(self):
    #     print(f">>> PIPELINE {self.name.upper()} IS STARTING!!! <<<")

    # async def on_shutdown(self):
    #     print(f">>> PIPELINE {self.name.upper()} IS SHUTTING DOWN!!! <<<")


    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict
             ) -> Union[str, Generator, Iterator]:

        if body.get("task") == "title_generation" and not HARD_DISABLE_TITLE_GENERATION:
            print("################# Title Generation #################")
            yield f"Pipeline {self.name}"

        else:

            print(f">>> PIPELINE '{self.name.upper()}' RUNNING <<<")
            print("######################################")
            print("user_message: str")
            print(f"{user_message}")
            print("model_id: str")
            print(f"{model_id}")
            # print("messages: List[dict]")
            # print(f"{messages}")
            print("body: dict")
            print(f"{json.dumps(body, indent=4)}")
            print("######################################")


            url = f"{LANGSERVE_ENDPOINT}:{PORT}{PIPELINE_ENDPOINT}"
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }

            body['chat_id'] = self.chat_id
            body['graph_name'] = self.graph_name
            req = PostRequest(user_message=user_message, messages=messages, body=body)

            try:
                response = requests.post(url, json=req, headers=headers, stream=True)
                response.raise_for_status()

                for line in response.iter_lines():
                    if line:
                        yield line.decode() + '\n'

            except Exception as e:
            # except requests.exceptions.RequestException as e:
                # TODO: give an ALERT to the system admin!
                yield f"""⛓️‍💥 uh oh!\nSomething broke.\nThe server may be down."""
