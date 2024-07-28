from langgraph.graph import StateGraph, START, END

from src.PlebChat.graph import State
from src.PlebChat.graph.node import chatbot


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

GRAPH_ASCII = graph.get_graph().draw_ascii()
print(GRAPH_ASCII)
