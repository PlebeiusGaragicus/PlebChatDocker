from langgraph.graph import StateGraph, START, END

from src.graphs.plebchat.graph import State
from src.graphs.plebchat.graph.node import plebchat


graph_builder = StateGraph(State)
graph_builder.add_node("plebchat", plebchat)
graph_builder.add_edge(START, "plebchat")
graph_builder.add_edge("plebchat", END)

graph = graph_builder.compile()
