from abc import abstractmethod

class IASR():

    def __init__(self, device_id = None):
        pass
    
    @abstractmethod
    def run(self, input_handler):
        pass
