from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END

from src.graphs.plebchat.graph import State
from src.graphs.plebchat.graph.node import plebchat


# def finish(state: State, config: RunnableConfig):
#     return {"output": [state["messages"][-1]]}


graph_builder = StateGraph(State)
graph_builder.add_node("plebchat", plebchat)
# graph_builder.add_node("finish", finish)

graph_builder.add_edge(START, "plebchat")
# graph_builder.add_edge("plebchat", "finish")
# graph_builder.add_edge("finish", END)
graph_builder.add_edge("plebchat", END)

graph = graph_builder.compile()
