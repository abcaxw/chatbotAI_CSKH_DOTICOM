class HealthCheckException(Exception):
    def __init__(self, module):
        self.module = module


class InputException(Exception):
    def __init__(self, return_mess="InputException"):
        self.return_mess = return_mess
        self.err_code = 1


class InputFileException(Exception):
    def __init__(self, return_mess="InputFileException"):
        self.return_mess = return_mess
        self.err_code = 2


class MaxSizeException:
    def __init__(self, return_mess="MaxSizeException"):
        self.return_mess = return_mess
        self.err_code = 3


class MinSizeException:
    def __init__(self, return_mess="MinSizeException"):
        self.return_mess = return_mess
        self.err_code = 4


class DetectException:
    def __init__(self, return_mess="DetectException"):
        self.return_mess = return_mess
        self.err_code = 5
