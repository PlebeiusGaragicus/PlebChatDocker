from src.BaseBot import BaseBot

class CustomBot(BaseBot):
    def version(self, request, *args):
        """Get the version information for this graph."""
        from .VERSION import VERSION
        return f"Version `{VERSION}`"


    def hi(self, request, *args):
        """Tell the bot to say hello to you."""
        return f"""#  🗣️🤖💬👀
    
👋 Hi there!  You must be the "`{request.body['user']['name']}`" I've heard so much about...

I'm `PlebChat`.  I'm just a simple chatbot agent.

Type `/about` to learn more.
"""


    def about(self, request, *args):
        """Get information about the agent."""
        return """
I am proof of concept LangGraph agent that accepts direct bitcoin payments from users.

I aim to be a useful assistant that anyone can use anonymously.

There's a lot I can do with more features being added all the time!

Try `/usage` for a list of commands.

Here's my [source code on GitHub](https://github.com/PlebeiusGaragicus/PlebChatDocker)

Send me a message on nostr to chat about issues, features you'd like to see or anything AI-related.

```txt
npub1xegedgkkjf24pl4d76cdwhufacng5hapzjnrtgms3pyhlvmyqj9suym08k
```
"""


    def draw(self, request, *args):
        from .graph.graph import GRAPH_ASCII
        return f"```\n{GRAPH_ASCII}\n```"




####################################################################################
# ADD CUSTOM COMMANDS BELOW
####################################################################################
    # def url(self, request, *args):
    #     """Scrape the URL and reply with the content."""
    #     url = args[0] if args else "No URL provided"
    #     return f"Scraping content from {url}"
