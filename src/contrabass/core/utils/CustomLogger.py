class CustomLogger:

    def __init__(self, print_function, args1, args2):
        self.print_function = print_function
        self.args1 = args1
        self.args2 = args2

    def print(self, string):
        self.print_function(string, self.args1, self.args2)