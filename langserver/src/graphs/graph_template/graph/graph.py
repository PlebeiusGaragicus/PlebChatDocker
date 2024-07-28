from langgraph.graph import StateGraph, START, END

from src.graphs.graph_template.graph import State
from src.graphs.graph_template.graph.node import chatbot


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()
