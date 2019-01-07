class Logger:
    tab = 0

    @staticmethod
    def log(sender, message, tab_add = 0):
        spaces = max((Logger.tab * 3), 0)

        print(r'{: <{indent_level}}[{sender}] {message}'.format(
            '',
            indent_level = spaces,
            sender = sender, 
            message = message,
        ))

        Logger.tab += tab_add