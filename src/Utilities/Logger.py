from datetime import datetime



class Logger:
    """
    Facility for logging messages.
    
    Attributes:
        tabs (int): The number of tab stops to add
            to the left of the message.
    """

    tabs: int = 0


    
    @staticmethod
    def log(sender: str, message: str, tab_add: int = 0):
        """
        Logs the given message.
        
        Args:
            sender (str): Where the message is coming from.
            message (str): The message to log.
            tab_add (int, optional): Defaults to 0. The number 
                of tab stops to add or subtract from the global
                counter after logging.
        """

        print('{:\t<{indent_level}}[{time}] [{sender}] {message}'.format(
            '',
            indent_level = Logger.tabs,
            time = datetime.now(),
            sender = sender, 
            message = message,
        ))

        Logger.add_tabs(tab_add)



    @staticmethod
    def add_tabs(tabs: int) -> int:
        """
        Adds or subtracts from the global tab counter.
        
        Args:
            tabs (int): The number of tab stops to
                add or subtract.
        
        Returns:
            int: The current number of tab stops.
        """

        Logger.tabs += tabs
        Logger.tabs = max(Logger.tabs, 0)

        return Logger.tabs