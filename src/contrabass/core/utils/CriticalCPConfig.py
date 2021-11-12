class CriticalCPConfig:

    def __init__(self):
        self.__model_path = None
        self.__print_f = None
        self.__args1 = None
        self.__args2 = None
        self.__output_path_spreadsheet = None
        self.__output_path_html = None
        self.__objective = None
        self.__fraction = None
        self.__processes = None

    @property
    def model_path(self):
        return self.__model_path

    @model_path.setter
    def model_path(self, value):
        self.__model_path = value

    @property
    def print_f(self):
        return self.__print_f

    @print_f.setter
    def print_f(self, value):
        self.__print_f = value

    @property
    def args1(self):
        return self.__args1

    @args1.setter
    def args1(self, value):
        self.__args1 = value

    @property
    def args2(self):
        return self.__args2

    @args2.setter
    def args2(self, value):
        self.__args2 = value

    @property
    def output_path_spreadsheet(self):
        return self.__output_path_spreadsheet

    @output_path_spreadsheet.setter
    def output_path_spreadsheet(self, value):
        self.__output_path_spreadsheet = value

    @property
    def output_path_html(self):
        return self.__output_path_html

    @output_path_html.setter
    def output_path_html(self, value):
        self.__output_path_html = value

    @property
    def objective(self):
        return self.__objective

    @objective.setter
    def objective(self, value):
        self.__objective = value

    @property
    def fraction(self):
        return self.__fraction

    @fraction.setter
    def fraction(self, value):
        self.__fraction = value

    @property
    def processes(self):
        return self.__processes

    @processes.setter
    def processes(self, value):
        self.__processes = value