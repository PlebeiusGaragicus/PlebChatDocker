import os
import json
import logging
logger = logging.getLogger(__name__)


from .payment import DEFAULT_INVOICE_AMOUNT, MINIMUM_INVOICE_AMOUNT, MAXIMUM_INVOICE_AMOUNT


class BotCommandHandler:
    def _handle_command(self, request):
        split = request.user_message.split(" ")
        command = split[0][1:].lower()  # Remove the slash and take the first word
        params = split[1:]  # Everything else is parameters

        # Try to get the method corresponding to the command
        method = getattr(self, command, None)

        # If method exists and is callable, invoke it
        if callable(method) and not command.startswith('_'):
            return method(request, *params)
        else:
            return f"""# ⛓️‍💥\n`/{command}` command not found!\n## Commands available:\n{self.help(request)}"""

    def help(self, request, *args):
        """Get a list of commands."""
        # Generate usage text from available methods with a docstring
        command_list = [
            method for method in dir(self)
            if callable(getattr(self, method)) and not method.startswith("__") and not method.startswith("_")
        ]
        return "\n".join(f"/{cmd} - {getattr(self, cmd).__doc__}" for cmd in command_list)

    def whoami(self, request, *args):
        """Get your username."""
        if request.body['user']['role'] == 'admin' or os.getenv('DEBUG', False):
            user = request.body['user']
            return f"""```\n{json.dumps(user, indent=4)}\n```"""
        else:
            username = request.body['user']['email']
            return f"Your username is: `{username}`"

    def debug(self, request, *args):
        """Get debug information."""
        if request.body['user']['role'] == 'admin' or os.getenv('DEBUG', False):
            return f"'DEBUG' environment variable: `{os.getenv('DEBUG')}`\n\n**body:**\n```json\n{json.dumps(request.body, indent=4)}\n```"
        else:
            return "Debug mode is disabled."

    def draw(self, request, *args):
        graph_ascii = self._get_graph().get_graph().draw_ascii()
        return f"```\n{graph_ascii}\n```"

    def cuss(self, request, *args):
        """Let off some steam."""
        return "fuck\n\nteehee"

####################################################################################
#### YOUR CUSTOM GRAPH AGENTS MUST IMPLEMENT THE FOLLOWING METHODS #################
####################################################################################
    def _get_graph(self):
        raise NotImplementedError("Your bot must implement this function!")

    def version(self, request, *args):
        raise NotImplementedError("Your bot must implement this function!")

    def hi(self, request, *args):
        raise NotImplementedError("Your bot must implement this function!")

    def about(self, request, *args):
        raise NotImplementedError("Your bot must implement this function!")


####################################################################################
######### BITCOIN LIGHTNING PAYMENT, INVOICING, AND USAGE METHODS ##################
####################################################################################
    def bal(self, request, *args):
        """Check your token balance."""
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


####################################################################################

    def pay(self, request, *args):
        """Request an invoice to top up your balance."""
        try:
            split = request.user_message.split(" ")
            # first_arg = split[1] if len(split) > 1 else None

            # if first_arg:
            #     requested_invoice_amount = int(first_arg)
            #     if requested_invoice_amount < MINIMUM_INVOICE_AMOUNT:
            #         return f"⚠️ The minimum invoice amount is {MINIMUM_INVOICE_AMOUNT} sats."

            #     if requested_invoice_amount > MAXIMUM_INVOICE_AMOUNT:
            #         return f"⚠️ The maximum invoice amount is {MAXIMUM_INVOICE_AMOUNT} sats.\nThank you for your enthusiasm, but let's play this a little more safely."
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
            return f"""
[Click to pay with Lightning ⚡️](lightning:{invoice['pr']})

Invoice ID: `{invoice['_id']}`

Amount: `{invoice['amount']}` sats

```
lightning:{invoice['pr']}
```
"""


####################################################################################

    def usage(self, request, *args):
        """Track your token usage for the last `n` days with "`/usage n`\""""
        return "This feature is not yet implemented."




####################################################################################
####################################################################################
####################################################################################

    def read(self, request, *args):
        """Scrape a URL and return the article."""
        url = args[0] if args else "No URL provided"
        return f"Returning article from {url}"


# def readability(request):
#     return "Not yet implemented"
# #     # TODO: I want to consider charging the user for intensive commands like this...
# #     split = request.user_message.split(" ")
# #     first_arg = split[1] if len(split) > 1 else None

# #     #TODO: modularize this code.  Maybe have a _ensure_proper_url() function that can be reused in other commands.
# #     if not first_arg:
# #         return "⚠️ Please provide a URL.\n\n**Example:**\n```\n/article https://example.com\n```"

# #     if first_arg.startswith("http://"):
# #         return f"⚠️ The URL must start with `https://`\n\n**Example:**\n```\n/article https://example.com\n```"

# #     if not first_arg.startswith("https://"):
# #         first_arg = f"https://{first_arg}"

# #     try:
# #         from readability import Document
# #         # url = "https://tftc.io/home-and-car-insurance-providers-retreating/"
# #         # response = requests.get( url )
# #         response = requests.get( first_arg )
# #         doc = Document(response.content)

# #         article_markdown_contents = f""

# #         article_markdown_contents += doc.title()
# #         article_markdown_contents += doc.summary()
# #         article_markdown_contents += doc.content()



# #         return f"""
# # This command will scrape the provided url and reply with a summary of the content.

# # The URL you provided is: {first_arg}

# # Here's the article:

# # ---

# # {article_markdown_contents}
# # """

# #     except Exception as e:
# #         return f"""error in scraping this URL: {e}"""




# ############################################################################
    def url(self, request, *args):
        """Scrape the URL and reply with the content."""
        url = args[0] if args else "No URL provided"
        return f"Scraping content from {url}"


# def url(request):
#     split = request.user_message.split(" ")
#     first_arg = split[1] if len(split) > 1 else None

#     if not first_arg:
#         return "⚠️ Please provide a URL.\n\n**Example:**\n```\n/url https://example.com\n```"

#     if first_arg.startswith("http://"):
#         return f"⚠️ The URL must start with `https://`\n\n**Example:**\n```\n/url https://example.com\n```"

#     if not first_arg.startswith("https://"):
#         first_arg = f"https://{first_arg}"

#     return f"""
# This command will scrape the provided url and reply with the "readability" text.

# This way, the contents of the url can be injected into the context of the conversation and can be discussed, summariezed, etc.

# This is a placeholder for the implementation of the url command.

# The URL you provided is: {first_arg}

# [Click here to view the content of the URL]({first_arg})

# The content of the URL will be displayed here.
# """
# #NOTE: providing just the url link like so:
# # [Click here to view the content of the URL]({first_arg})
# # will prepend the base url/c/ so that we can link TO CONVERSATIONS!!! WOW!

