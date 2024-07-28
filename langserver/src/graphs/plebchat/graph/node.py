from langchain_core.runnables import RunnableConfig
from langchain_ollama import ChatOllama
from langchain_core.chat_history import AIMessage, BaseMessage

# from src.payment import deduct_with_usage
from src.graphs.plebchat.graph import State

from src.usage import deduct_with_usage


def plebchat(state: State, config: RunnableConfig):
    if not config['configurable'].get('is_admin', False):
        deduct_with_usage(configurable=config['configurable'], tokens_used=1)


    MODEL = "phi3:latest"
    llm = ChatOllama(model=MODEL,
                     keep_alive="-1" # Keep the model alive indefinitely
        )

    r = llm.invoke(state["messages"])

    return {"messages": [r]}

    # resp = {
    #     "role": "assistant",
    #     "content": "hi"
    # }

    # return {"messages": [resp]}
    # return {"messages": [AIMessage("hi")]}
    # return {"messages": [{
    #                 "role": "assistant",
    #                 "content": "hi"
    #         }]}
