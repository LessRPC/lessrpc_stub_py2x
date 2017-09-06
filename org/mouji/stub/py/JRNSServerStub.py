'''
Created on Jul 21, 2017

@author: Salim
'''
from org.mouji.stub.py.JRNSStub import JRNSStub


class JRNSServerStub(JRNSStub):
    
    
    def __init__(self, port):
        self.port = port
        self.provider = None
        
        
    def init(self, provider):
        pass
    
    
    def start(self):
        pass
    
    
    
    def register(self, nsInfo):
        pass
        
    
    
    def getService(self):
        pass
    
    
    def getProvider(self):
        pass
        
