import os
import json
import logging
logger = logging.getLogger(__name__)


from src.config import DEFAULT_INVOICE_AMOUNT, MINIMUM_INVOICE_AMOUNT, MAXIMUM_INVOICE_AMOUNT



def hi(_):
    from src.config import HI_TEXT
    return HI_TEXT


def version(_):
    """
    This is the docscring for the version command.
    #TODO I want to use this to help generate the usage text.
    #... or ... BETTER YET... i can have a use the /help <command> to get the docstring for that command!!! Just like man pages!!!
    """
    from src.VERSION import VERSION
    return f"Version `{VERSION}`"


def about(_):
    #TODO
    from src.config import ABOUT_TEXT
    return ABOUT_TEXT


def usage(_):
    # use the commands list to generate the usage text
    usage_text = "```\n"
    for command_names, _, description in command_list:
        usage_text += f"{', '.join(command_names)} - {description}\n"
    usage_text += "```"
    return usage_text


def draw(_):
    from src.graph.graph import GRAPH_ASCII
    return f"```\n{GRAPH_ASCII}\n```"

def long(_):
    return "sfd;ljas;fljas d;fljk asdf;lk jasdf;lj asdf;kjlas ;lkjf;lejiaf;io jae;lfj ads;lfjk ;oeifj ;oaj fsfd;ljas;fljas d;fljk asdf;lk jasdf;lj asdf;kjlas ;lkjf;lejiaf;io jae;lfj ads;lfjk ;oeifj ;oaj fsfd;ljas;fljas d;fljk asdf;lk jasdf;lj asdf;kjlas ;lkjf;lejiaf;io jae;lfj ads;lfjk ;oeifj ;oaj fsfd;ljas;fljas d;fljk asdf;lk jasdf;lj asdf;kjlas ;lkjf;lejiaf;io jae;lfj ads;lfjk ;oeifj ;oaj fsfd;ljas;fljas d;fljk asdf;lk jasdf;lj asdf;kjlas ;lkjf;lejiaf;io jae;lfj ads;lfjk ;oeifj ;oaj fsfd;ljas;fljas d;fljk asdf;lk jasdf;lj asdf;kjlas ;lkjf;lejiaf;io jae;lfj ads;lfjk ;oeifj ;oaj fsfd;ljas;fljas d;fljk asdf;lk jasdf;lj asdf;kjlas ;lkjf;lejiaf;io jae;lfj ads;lfjk ;oeifj ;oaj fsfd;ljas;fljas d;fljk asdf;lk jasdf;lj asdf;kjlas ;lkjf;lejiaf;io jae;lfj ads;lfjk ;oeifj ;oaj fsfd;ljas;fljas d;fljk asdf;lk jasdf;lj asdf;kjlas ;lkjf;lejiaf;io jae;lfj ads;lfjk ;oeifj ;oaj fsfd;ljas;fljas d;fljk asdf;lk jasdf;lj asdf;kjlas ;lkjf;lejiaf;io jae;lfj ads;lfjk ;oeifj ;oaj fsfd;ljas;fljas d;fljk asdf;lk jasdf;lj asdf;kjlas ;lkjf;lejiaf;io jae;lfj ads;lfjk ;oeifj ;oaj fsfd;ljas;fljas d;fljk asdf;lk jasdf;lj asdf;kjlas ;lkjf;lejiaf;io jae;lfj ads;lfjk ;oeifj ;oaj fsfd;ljas;fljas d;fljk asdf;lk jasdf;lj asdf;kjlas ;lkjf;lejiaf;io jae;lfj ads;lfjk ;oeifj ;oaj fsfd;ljas;fljas d;fljk asdf;lk jasdf;lj asdf;kjlas ;lkjf;lejiaf;io jae;lfj ads;lfjk ;oeifj ;oaj fsfd;ljas;fljas d;fljk asdf;lk jasdf;lj asdf;kjlas ;lkjf;lejiaf;io jae;lfj ads;lfjk ;oeifj ;oaj fsfd;ljas;fljas d;fljk asdf;lk jasdf;lj asdf;kjlas ;lkjf;lejiaf;io jae;lfj ads;lfjk ;oeifj ;oaj f"

def whoami(request):
    username = request.body['user']['email']
    return f"Your username is: `{username}`"


def debug(request):
    debug = os.getenv('DEBUG')
    return f"'DEBUG' environment variable: `{debug}`\n\n**body:**\n```json\n{json.dumps(request.body, indent=4)}\n```"





############################################################################
def balance(request):
    lud16 = request.body['user']['email']
    if not lud16:
        return "⚠️ No user LUD16 provided." #TODO: we need to log these errors.  This should never happen!!

    else:
        try:
            from .payment import get_user_balance
            bal = get_user_balance(lud16).get("balance", None)

            if bal is None:
                logger.warning(f"Error checking balance for {lud16}")
                yield "Hi 👋🏻\nYou are an unregistered user.\nUse the `/pay` command to get started."
            else:
                logger.info(f"{lud16} has a balance of {bal:.0f} tokens")
                yield f"User: `{lud16}`\nYour account has a balance of: `{bal:.0f}` tokens"

        except Exception as e:
            logger.error(f"Error checking balance for {lud16}: {e}")
            if os.getenv("DEBUG"): # TODO: fix these... they need to behave when DEBUG=false / 0
                # NOTE: hide the error message details from the user unless we're debugging!
                error_message = f"There was an error checking your balance:\n`{e}`"
            else:
                error_message = f"There was an error checking your balance."

            yield error_message


def pay(request):

    try:
        split = request.user_message.split(" ")
        # first_arg = split[1] if len(split) > 1 else None

        # if first_arg:
        #     requested_invoice_amount = int(first_arg)
        #     if requested_invoice_amount < MINIMUM_INVOICE_AMOUNT:
        #         return f"⚠️ The minimum invoice amount is {MINIMUM_INVOICE_AMOUNT} sats."

        #     if requested_invoice_amount > MAXIMUM_INVOICE_AMOUNT:
        #         return f"⚠️ The maximum invoice amount is {MAXIMUM_INVOICE_AMOUNT} sats."
        # else:
        #     requested_invoice_amount = DEFAULT_INVOICE_AMOUNT
        requested_invoice_amount = DEFAULT_INVOICE_AMOUNT

    except Exception as e:
        return f"⚠️ Please provide a valid invoice amount.\n\n**Example:**\n`\n/pay {DEFAULT_INVOICE_AMOUNT}\n`\n"

    lud16 = request.body['user']['email']
    if not lud16:
        return "⚠️ No user LUD16 provided." #TODO: we need to log these errors.  This should never happen!!
    else:
        from .payment import get_invoice
        invoice = get_invoice(lud16=lud16, sats=requested_invoice_amount)

        # return f"""[Click to pay with Lightning ⚡️](lightning:{invoice['pr']})\n\n```json\n{json.dumps(invoice, indent=4)}\n```\n"""
        ret = f"""
[Click to pay with Lightning ⚡️](lightning:{invoice['pr']})

Invoice ID: `{invoice['_id']}`

Amount: `{invoice['amount']}` sats

```
lightning:{invoice['pr']}
```
"""
        return ret





############################################################################
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



def readability(request):
    return "Not yet implemented"
#     # TODO: I want to consider charging the user for intensive commands like this...
#     split = request.user_message.split(" ")
#     first_arg = split[1] if len(split) > 1 else None

#     #TODO: modularize this code.  Maybe have a _ensure_proper_url() function that can be reused in other commands.
#     if not first_arg:
#         return "⚠️ Please provide a URL.\n\n**Example:**\n```\n/article https://example.com\n```"

#     if first_arg.startswith("http://"):
#         return f"⚠️ The URL must start with `https://`\n\n**Example:**\n```\n/article https://example.com\n```"

#     if not first_arg.startswith("https://"):
#         first_arg = f"https://{first_arg}"

#     try:
#         from readability import Document
#         # url = "https://tftc.io/home-and-car-insurance-providers-retreating/"
#         # response = requests.get( url )
#         response = requests.get( first_arg )
#         doc = Document(response.content)

#         article_markdown_contents = f""

#         article_markdown_contents += doc.title()
#         article_markdown_contents += doc.summary()
#         article_markdown_contents += doc.content()



#         return f"""
# This command will scrape the provided url and reply with a summary of the content.

# The URL you provided is: {first_arg}

# Here's the article:

# ---

# {article_markdown_contents}
# """

#     except Exception as e:
#         return f"""error in scraping this URL: {e}"""







############################################################################
############################################################################
# from pydantic import BaseModel, Field
# from typing import List

# class BotCommand(BaseModel):
#     keyword: List[str]
#     callback: callable
#     usage_description: str


command_list = [
#NOTE:
# first item is a list of keywords that will trigger the command
# second item is the function that will be called when the command is triggered
# third item is a description of the command (for the usage text)

    # STANDARD COMMANDS FOR EVERY AGENT
    [["hi"], hi, "Tell the bot to say hello to you."],
    [["version"], version, "Get the version of the agent"],
    [["info", "about"], about, "Get information about the agent"],
    [["usage", "help"], usage, "Get a list of commands"],
    [["draw"], draw, "Get the graph of the agent"],
    [["long"], long, "Get a long message"],
    [['whoami'], whoami, "Get your username"],
    [["debug"], debug, "Get debug information"],

    # PAYMENT COMMANDS
    [["bal"], balance, "Check the your token balance"],
    [["pay"], pay, "Request an invoice to top up your balance"],

    # CUSTOM COMMANDS TO THIS AGENT
    [["url"], url, "Scrape the URL and reply with the content"],
    [["article"], readability, "scrape a URL"],
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
