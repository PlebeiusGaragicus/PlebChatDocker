import logging
logger = logging.getLogger(__name__)

from langchain_core.runnables import RunnableConfig
from langchain_ollama import ChatOllama
from langchain_core.chat_history import AIMessage, BaseMessage

from src.graphs.plebchat.graph import State
from src.usage import deduct_usage



def plebchat(state: State, config: RunnableConfig):
    logger.debug(f"plebchat node called with state: {state}")

    # MODEL = "phi3:latest"
    MODEL = "llama3.1"
    llm = ChatOllama(
                model=MODEL,
                # Keep the model alive indefinitely
                keep_alive="-1"
            )

    # r = llm.invoke(state["query"])
    r = llm.invoke(state["messages"])
    logger.debug(f"Ollama response: {r}")

    deduct_usage(config, r.usage_metadata)

    return {"messages": [r]}
