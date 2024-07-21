from langchain_core.runnables import RunnableConfig
from langchain_ollama import ChatOllama
from langchain_core.chat_history import AIMessage, BaseMessage

from src.common.payment import BalanceManager, deduct
from src.graph import State



def chatbot(state: State, config: RunnableConfig):
    # bm = BalanceManager()

    # lud16 = config["configurable"].get("lud16")
    # if not lud16:
    #     raise ValueError("User's lud16 is not specified")
    # bm.deduct_balance(lud16, "chat_12345", 1.0)


    MODEL = "phi3:latest"
    llm = ChatOllama(model=MODEL,
                     keep_alive="-1" # Keep the model alive indefinitely
        )

    r = llm.invoke(state["messages"])

    # r = BaseMessage(
    #     content="hji",
    #     type="assistant"
    # )

    #TODO: calculate usage
    deduct(config["configurable"].get("lud16"), "chat_12345", 1.0)
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














# import asyncio
# from typing import Sequence

# from langchain_community.callbacks import StreamlitCallbackHandler

# from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# # from langchain_openai import ChatOpenAI
# from langchain_community.chat_models import ChatOllama


# from typing import List, Sequence

# from langgraph.graph import END, MessageGraph

# from pydantic import BaseModel

# import streamlit as st

# from src.components.presets import find_preset



# DEFAULT_GOAL = """You are an essay assistant tasked with writing excellent 5-paragraph essays.
# Generate the best essay possible for the user's request.
# If the user provides critique, respond with a revised version of your previous attempts."""

# DEFAULT_REFLECTION = """You are a teacher grading an essay submission. Generate critique and recommendations for the user's submission.
# Provide detailed recommendations, including requests for length, depth, style, etc."""






# class ChainReflectionBot():
#     name: str = "Reflection"
#     avatar: str = "🤔"

#     def show_prompts(self):
#         st.text_area("Goal Prompt", height=150,
#                 value=find_preset("goal_prompt", default=DEFAULT_GOAL),
#                 key="preset_goal_prompt")

#         st.text_area("Reflection Prompt", height=150,
#                 value=find_preset("reflection_prompt", default=DEFAULT_REFLECTION),
#                 key="preset_reflection_prompt")


#         st.write("Generate a short essay on the topicality of The Little Prince and its message in modern life. Keep it no more than 200 words.")


#     def show_settings(self):
#         # st.selectbox("Model", ["dolphin-mistral:latest", "mistral:7b", "llama2:7b", "gemma:2b"], key="selected_model")
#         # st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.5, step=0.01, key="temperature")
#         # st.number_input("Max Iterations", min_value=1, max_value=10, value=3, step=1, key="max_iterations")
#         st.select_slider("Max Iterations", options=[i + 1 for i in range(10)],
#                 value=find_preset("max_iterations", default=3),
#                 key="preset_max_iterations")



        


#     def run_prompt(self, bot_reply_placeholder):
#         stream_handler = StreamlitCallbackHandler(bot_reply_placeholder, collapse_completed_thoughts=True)
#         graph = compile_runnable(stream_handler, max_iterations = st.session_state.preset_max_iterations)

#         # return graph.stream([HumanMessage(content=st.session_state.prompt)],)

#         async def update_UI():
#             # yield graph.astream([HumanMessage(content=st.session_state.prompt)],)
#             return graph.astream([HumanMessage(content=st.session_state.prompt)],)

#         return asyncio.run(update_UI())



# def compile_runnable(stream_handler, max_iterations):

#     prompt = ChatPromptTemplate.from_messages(
#         [
#             (
#                 "system",
#                 st.session_state.preset_goal_prompt,
#             ),
#             MessagesPlaceholder(variable_name="messages"),
#         ]
#     )

#     # llm = ChatOpenAI(streaming=True, callbacks=[stream_handler])
#     llm = ChatOllama(
#                 model="llama2:7b",
#                 streaming=True,
#                 temperature=str(0.5),
#                 callbacks=[stream_handler]
#             )
#     generate = prompt | llm



#     reflection_prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             st.session_state.preset_reflection_prompt, # This is a 2-tuple of (role, content) with role being 'human', 'user', 'ai', 'assistant', or 'system'.
#         ),
#         MessagesPlaceholder(variable_name="messages"),
#     ])
#     reflect = reflection_prompt | llm




#     async def generation_node(state: Sequence[BaseMessage]):
#         return await generate.ainvoke({"messages": state})


#     async def reflection_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
#         # Other messages we need to adjust
#         cls_map = {"ai": HumanMessage, "human": AIMessage}
#         # First message is the original user request. We hold it the same for all nodes
#         translated = [messages[0]] + [
#             cls_map[msg.type](content=msg.content) for msg in messages[1:]
#         ]
#         res = await reflect.ainvoke({"messages": translated})
#         # We treat the output of this as human feedback for the generator
#         return HumanMessage(content=res.content)


#     builder = MessageGraph()
#     builder.add_node("generate", generation_node)
#     builder.add_node("reflect", reflection_node)
#     builder.set_entry_point("generate")


#     def should_continue(state: List[BaseMessage]):
#         # if len(state) / 2 > max_iterations: # TODO... hmmm
#         if len(state) / 2 > max_iterations: # TODO... hmmm
#             return END
#         return "reflect"


#     builder.add_conditional_edges("generate", should_continue)
#     builder.add_edge("reflect", "generate")
#     graph = builder.compile() # returns a Pregel
#     return graph
