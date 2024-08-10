from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    # query: str
    messages: Annotated[list, add_messages]
    # output: str
