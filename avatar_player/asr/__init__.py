from abc import abstractmethod

class IASR():

    def __init__(self):
        pass
    
    @abstractmethod
    def run(self, input_handler):
        pass
