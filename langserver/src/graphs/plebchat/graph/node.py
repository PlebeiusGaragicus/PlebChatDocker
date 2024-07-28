from langchain_core.runnables import RunnableConfig
from langchain_ollama import ChatOllama
from langchain_core.chat_history import AIMessage, BaseMessage

# from src.payment import deduct_with_usage
from src.graphs.plebchat.graph import State



def plebchat(state: State, config: RunnableConfig):
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

    # REFER TO: https://python.langchain.com/v0.2/docs/how_to/llm_token_usage_tracking/
    # NOTE: I should downvote this article as it ONLY applies to OpenAI and may be out of date
    # TODO: I should follow the LangSmith link to see how I can use LangSmith... I'm not optimistic about it though...
    # TODO: try this one: https://docs.smith.langchain.com/old/tracing/faq/custom_llm_token_counting

    # TODO: get the run_id of a run: https://docs.smith.langchain.com/old/tracing/faq/langchain_specific_guides#getting-a-run-id-from-a-langchain-call
    # NOTE: no.. I need to get the TRACE_ID not the RUN_ID.  But either one would help for tracking usage.
    # https://docs.smith.langchain.com/old/tracing/concepts
    # deduct_with_usage(config["configurable"].get("lud16"), "chat_12345", 1.0)
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
