import json
from fastapi.responses import StreamingResponse

from src.common.payment import UserNotRegistered



# Markdown text to explain the commands available
USAGE = """
/version                  Get the version of the agent

/info, /about             Get information about the agent

/draw                     Get the graph of the agent

/help, /usage             Get a list of commands

/debug                    Get debug information
"""



############################################################################
def version(_):
    """
    This is the docscring for the version command.
    #TODO I want to use this to help generate the usage text.
    #... or ... BETTER YET... i can have a use the /help <command> to get the docstring for that command!!! Just like man pages!!!
    """
    from src.VERSION import VERSION
    return f"Version `{VERSION}`"


############################################################################
def about(_):
    # Markdown text to explain this construct
    return """
# Chatbot Agent

Hi, I'm just some agent dude...

Try `/usage` for a list of commands.
"""


############################################################################
def usage(_):
    # return f"```\n{USAGE}\n```"

    # use the commands list to generate the usage text
    usage_text = "```\n"
    for command_names, _, description in command_list:
        usage_text += f"{', '.join(command_names)} - {description}\n"
    usage_text += "```"
    return usage_text


############################################################################
def draw(_):
    from src.graph.graph import GRAPH_ASCII
    return f"```\n{GRAPH_ASCII}\n```"

############################################################################
def debug(request):
    return f"# body:\n```json\n{json.dumps(request.body, indent=4)}\n```"

############################################################################



def balance(request):
    lud16 = request.body['user']['email']
    if not lud16:
        return "⚠️ No user LUD16 provided." #TODO: we need to log these errors.  This should never happen!!
    else:
        try:
            from .payment import show_user_balance
            return show_user_balance(lud16=lud16)
        except UserNotRegistered as e:
            error_message = f"Hello new user!  You have no balance yet - type `/pay` to get started."
            return StreamingResponse(iter([error_message]), media_type="text/event-stream")

            


def pay(request):
# This command will:
# - check if the user has any pending invoices.
# - if so, it will check if the invoice has been paid
# - if not, it will generate a new invoice for the user to pay.

    lud16 = request.body['user']['email']
    if not lud16:
        return "⚠️ No user LUD16 provided." #TODO: we need to log these errors.  This should never happen!!
    else:
        #TODO: the user can specify an amount to invoice??

        from .payment import get_invoice
        invoice = get_invoice(lud16=lud16)

        ln_link = f"lightning:{invoice['pr']}?amount={invoice['amount']}"

        return f"""[Click to pay with Lightning ⚡️](lightning:{invoice['pr']})\n\n```json\n{invoice}\n```\n"""
        # return f"""[Click here to pay]({ln_link})\n\n```json\n{invoice}\n```\n"""
        # return f"""<a href="lightning:{invoice['pr']}" target="_blank">Click to pay with Lightning ⚡️</a>"""


def url(request):
    split = request.user_message.split(" ")
    first_arg = split[1] if len(split) > 1 else None

    if not first_arg:
        return "⚠️ Please provide a URL.\n\n**Example:**\n```\n/url https://example.com\n```"

    if first_arg.startswith("http://"):
        return f"⚠️ The URL must start with `https://`\n\n**Example:**\n```\n/url https://example.com\n```"

    if not first_arg.startswith("https://"):
        first_arg = f"https://{first_arg}"

    return f"""
This command will scrape the provided url and reply with the "readability" text.

This way, the contents of the url can be injected into the context of the conversation and can be discussed, summariezed, etc.

This is a placeholder for the implementation of the url command.

The URL you provided is: {first_arg}

[Click here to view the content of the URL]({first_arg})

The content of the URL will be displayed here.
"""
#NOTE: providing just the url link like so:
# [Click here to view the content of the URL]({first_arg})
# will prepend the base url/c/ so that we can link TO CONVERSATIONS!!! WOW!



def summarize(request):
    split = request.user_message.split(" ")
    first_arg = split[1] if len(split) > 1 else None

    #TODO: modularize this code.  Maybe have a _ensure_proper_url() function that can be reused in other commands.
    if not first_arg:
        return "⚠️ Please provide a URL.\n\n**Example:**\n```\n/summarize https://example.com\n```"

    if first_arg.startswith("http://"):
        return f"⚠️ The URL must start with `https://`\n\n**Example:**\n```\n/summarize https://example.com\n```"

    if not first_arg.startswith("https://"):
        first_arg = f"https://{first_arg}"

    return f"""
This command will scrape the provided url and reply with a summary of the content.

The URL you provided is: {first_arg}
"""













command_list = [
###################################
# STANDARD COMMANDS FOR EVERY AGENT
    [["version"], version, "Get the version of the agent"],
    [["info", "about"], about, "Get information about the agent"],
    [["usage", "help"], usage, "Get a list of commands"],
    [["draw"], draw, "Get the graph of the agent"],
    [["debug"], debug, "Get debug information"],

###################################
# PAYMENT COMMANDS
    [["bal"], balance, "Check the your token balance"],
    [["pay"], pay, "Request an invoice to top up your balance"],

###################################
# CUSTOM COMMANDS TO THIS AGENT
    [["url"], url, "Scrape the URL and reply with the content"],
    [["summarize"], summarize, "scrape a URL"],
]





def handle_commands(request):
    split = request.user_message.split(" ")
    # first_arg = split[1] if len(split) > 1 else None
    command = split[0][1:].lower() # Remove the slash and take the first word

    valid_command = False
    for command_names, command_function, _ in command_list:
        if command in command_names:
            valid_command = True
            return command_function(request)
        else:
            continue

    if not valid_command:
        # return f"⚠️ Command not found.\n\n```txt\n{USAGE}\n```"
        return usage(request)
