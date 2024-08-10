from src.BotCommandHandler import BotCommandHandler

class PlebChat(BotCommandHandler):
    graph_name: str = "plebchat" # This should match the "graph_name" set in this agent's pipeline module
    VERSION: str = "0.0.1"
#     HI_MESSAGE: str = """#  🗣️🤖💬👀
    
# 👋 Hi there!  You must be the "`{request.body['user']['name']}`" I've heard so much about...

# I'm `PlebChat`.  I'm just a simple chatbot agent.

# Type `/about` to learn more.
# """
#     ABOUT_MESSAGE: str = """
# I am proof of concept LangGraph agent that accepts direct bitcoin payments from users.

# I aim to be a useful assistant that anyone can use anonymously.

# There's a lot I can do with more features being added all the time!

# Try `/help` for a list of commands.

# Here's my [source code on GitHub](https://github.com/PlebeiusGaragicus/PlebChatDocker)

# Send me a message on nostr to chat about issues, features you'd like to see or anything AI-related.

# ```txt
# npub1xegedgkkjf24pl4d76cdwhufacng5hapzjnrtgms3pyhlvmyqj9suym08k
# ```
# """

    def _get_computable_graph(self):
        from .graph.graph import graph
        return graph

    # def version(self, request, *args):
    #     """Get the version information for this graph."""
    #     from .VERSION import VERSION
    #     return f"Version `{VERSION}`"



    def hi(self, request, *args):
        """Tell the bot to say hello to you."""
        return f"""
***👋 Hi there!***

You must be the "`{request.body['user']['name']}`" I've heard so much about...

## I'm ***`PlebChat`*** 🗣️🤖💬

I'm just a simple chatbot agent.

  * Type **`/about`** to learn more.
  * Type **`/help`** to see a list of commands.
  * Type **`/bal`** to check your token balance.

#### Otherwise, just start asking questions!  I'm here to help.


"""


    def about(self, request, *args):
        """Get information about the agent."""
        return """
I am proof of concept LangGraph agent that accepts direct bitcoin payments from users.

I aim to be a useful assistant that anyone can use anonymously.

There's a lot I can do with more features being added all the time!

Try `/help` for a list of commands.

Here's my [source code on GitHub](https://github.com/PlebeiusGaragicus/PlebChatDocker)

Send me a message on nostr to chat about issues, features you'd like to see or anything AI-related.

```txt
npub1xegedgkkjf24pl4d76cdwhufacng5hapzjnrtgms3pyhlvmyqj9suym08k
```
"""
