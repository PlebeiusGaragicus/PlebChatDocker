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
            # if callable(getattr(self, method)) and not method.startswith("__") and not method.startswith("_")
            if callable(getattr(self, method)) and not method.startswith("_")
        ]
        # and (method.endswith("_") or request.body['user']['role'] == 'admin')
        strip_admin_commands = lambda x: x if request.body['user']['role'] == 'admin' else not x.endswith("_")
        command_list = list(filter(strip_admin_commands, command_list))

        return "\n".join(f"/{cmd} - {getattr(self, cmd).__doc__}" for cmd in command_list)

    def whoami_(self, request, *args):
        """print user info from the request body."""
        if request.body['user']['role'] == 'admin' or os.getenv('DEBUG', False):
            user = request.body['user']
            return f"""```\n{json.dumps(user, indent=4)}\n```"""
        else:
            username = request.body['user']['email']
            return f"Your username is: `{username}`"

    def debug_(self, request, *args):
        """ADMIN ONLY: Get the request body and `DEBUG` environment variable."""
        if request.body['user']['role'] == 'admin' or os.getenv('DEBUG', False):
            return f"'DEBUG' environment variable: `{os.getenv('DEBUG')}`\n\n**body:**\n```json\n{json.dumps(request.body, indent=4)}\n```"
        else:
            return "Debug mode is disabled."

    def draw_(self, request, *args):
        """Draw the graph."""
        graph_ascii = self._get_graph().get_graph().draw_ascii()
        return f"```\n{graph_ascii}\n```"

    def cuss(self, request, *args):
        """Let off some steam... 😡"""
        return "fuck\n\nteehee"

    def version_(self, request, *args):
        return self.VERSION
        # raise NotImplementedError("Your bot must implement this function!")

####################################################################################
#### YOUR CUSTOM GRAPH AGENTS MUST IMPLEMENT THE FOLLOWING METHODS #################
####################################################################################
    def _get_computable_graph(self):
        raise NotImplementedError("Your bot must implement this function!")


    def hi(self, request, *args):
        # return self.HI_MESSAGE
        raise NotImplementedError("Your bot must implement this function!")

    def about(self, request, *args):
        # return self.ABOUT_MESSAGE
        raise NotImplementedError("Your bot must implement this function!")


####################################################################################
######### BITCOIN LIGHTNING PAYMENT, INVOICING, AND USAGE METHODS ##################
####################################################################################
    def bal(self, request, *args):
        """Check your token **balance**."""

        is_admin = request.body['user']['role'] == 'admin'
        user_to_check = args[0] if args else None
        if is_admin and user_to_check is None:
            return """You're a system administrator - you don't have a balance.\nYou can use me for free!\nUse `/bal <username>` to check a user's balance."""

        if is_admin and user_to_check is not None:
            lud16 = user_to_check
        else:
            lud16 = request.body['user']['email']

        if not lud16:
            return "⚠️ No user LUD16 provided." #TODO: we need to log these errors.  This should never happen!!

        else:
            try:
                from .payment import get_user_balance
                bal = get_user_balance(lud16).get("balance", None)

                if bal is None:
                    logger.warning(f"Error checking balance for {lud16}")
                    # return "Hey 👋🏻\nYou, you must be new! 🤗.\nUse the **`/buy`** command to get started."
                    yield "## Welcome to **`PlebChat`** 🥳\n  * 👋🏻 Hey - ***you must be new!***\n  * 💬 Learn more about me by typing **`/about`**\n  * 👇🏼 To get started, you'll need some tokens.\n" + self.buy(request)

                else:
                    logger.info(f"{lud16} has a balance of {bal:.0f} tokens")
                    return f"User: `{lud16}`\nYou have: **`{bal:.0f}` generation tokens** left."

            except Exception as e:
                logger.error(f"Error checking balance for {lud16}: {e}")
                if os.getenv("DEBUG"): # TODO: fix these... they need to behave when DEBUG=false / 0
                    # NOTE: hide the error message details from the user unless we're debugging!
                    error_message = f"There was an error checking your balance:\n`{e}`"
                else:
                    error_message = f"There was an error checking your balance."

                return error_message


####################################################################################

    def buy(self, request, *args):
        """Request an invoice to top up your balance."""
        is_admin = request.body['user']['role'] == 'admin'
        if is_admin:
            return "You're a system administrator - you don't have to pay!\nYou can use me for free!"


        try:
            # split = request.user_message.split(" ")
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
            invoice = get_invoice(lud16=lud16)

### Invoice Request
            return f"""
  * 👉🏼 Buy `100,000` **generation tokens** for only **{requested_invoice_amount} sats**! 🎉

## ⚡️ ***[Tap to pay with Lightning](lightning:{invoice['pr']})*** ⚡️"""
## [⚡️ Tap to pay with Lightning ⚡️](lightning:{invoice['pr']})"""
# ```
# Request: `{invoice['pr'][:5]}..{invoice['pr'][-5:]}`
# Invoice: `{invoice['_id'][:5]}..{invoice['_id'][-5:]}`
# ```


####################################################################################

    def usage(self, request, *args):
        """Track your **token usage** for this conversation."""

        is_admin = request.body['user']['role'] == 'admin'
        if is_admin:
            return "You're a system administrator - I don't track your usage!\nYou can use me for free!"

        lud16 = request.body['user']['email']
        if not lud16:
            return "⚠️ No user LUD16 provided."

        thread_id = request.body['chat_id']
        if not thread_id:
            return "⚠️ No thread ID provided."

        try:
            from .payment import get_usage
            usage = get_usage(lud16, thread_id)
            return f"User: `{lud16}`\nThread: `{thread_id}`\nYou have used: **`{0 if not usage else usage}`** generation tokens in this conversation."
        except Exception as e:
            return f"Error checking usage: {e}"


        # return "This feature is not yet implemented."




####################################################################################
####################################################################################
####################################################################################

    # def read(self, request, *args):
    #     # TODO: charge the user for this feature!!
    #     """Scrape a URL and return the article."""
    #     url = args[0] if args else "No URL provided"
    #     return f"Returning article from {url}"


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
        # TODO: charge the user for this feature!!
        """**Copy an article** or website by providing the URL.  `/url https://example.com/articles/298302`"""
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

