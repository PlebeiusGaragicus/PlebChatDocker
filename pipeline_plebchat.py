import json
import requests
from typing_extensions import TypedDict

from typing import List, Union, Generator, Iterator, Optional
try:
    from pydantic.v1 import BaseModel
except Exception:
    from pydantic import BaseModel



LANGSERVE_ENDPOINT = f"http://host.docker.internal"
PORT = 8513
PIPELINE_ENDPOINT = "/langserver"


class PostRequest(TypedDict):
    user_message: str
    messages: List[dict]
    body: dict



class Pipeline:
    class Valves(BaseModel):
        pass

    def __init__(self):
        self.name = "PlebChat"
        self.graph_name = "plebchat"
        # self.cost_per_token = 1
        self.chat_id = None


    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        print(f"inlet:{__name__}")
        print(f"user: {user}")
        print(f"body: {body}")

        # Store the chat_id from body
        self.chat_id = body.get("chat_id")
        print(f"Stored chat_id: {self.chat_id}")

        return body


    async def on_startup(self):
        print(f">>> PIPELINE {self.name.upper()} IS STARTING!!! <<<")


    async def on_shutdown(self):
        print(f">>> PIPELINE {self.name.upper()} IS SHUTTING DOWN!!! <<<")


    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict
             ) -> Union[str, Generator, Iterator]:

        if body.get("task") == "Title Generation":
            print("################# Title Generation #################")
            yield "Test Pipeline"
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
                # print(f"Exception: {e}")
                # TODO: log here
                # TODO: give an ALERT to the system admin!
                # yield f"""Error: {e}"""
                yield f"""⛓️‍💥 uh oh!\nSomething broke.\nThe server may be down."""
