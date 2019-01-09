from datetime import datetime

# Description:
#   Facility for logging messages.
#
# Params:
#   none
class Logger:
    # The number of tab stops to add
    # to the left of the message.
    tabs: int = 0



    # Description:
    #   Logs the given message.
    #
    # Params:
    #   str sender:  Where the message is coming from.
    #   str message: The message to log.
    #   int tab_add: Optional. The number of tab stops
    #                to add or subtract from the global
    #                counter after logging.
    #
    # Returns:
    #   void
    @staticmethod
    def log(sender: str, message: str, tab_add: int = 0):
        print('{:\t<{indent_level}}[{time}] [{sender}] {message}'.format(
            '',
            indent_level = Logger.tabs,
            time = datetime.now(),
            sender = sender, 
            message = message,
        ))

        Logger.add_tabs(tab_add)



    # Description:
    #   Adds or subtracts from the global
    #   tab counter.
    #
    # Params:
    #   int tabs: The number of tab stops to
    #             add or subtract.
    #
    # Returns:
    #   int: The 
    @staticmethod
    def add_tabs(tabs: int) -> int:
        Logger.tabs += tabs
        Logger.tabs = max(Logger.tabs, 0)

        return Logger.tabs