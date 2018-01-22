'''
Created on Nov 7, 2017

@author: Salim
'''

import random
from datetime import datetime
from lessrpc_stub.serializer import JsonSerializer

class Stub():
    
    __slots__ = ['__serializers', '__serializer_map', '__accepted_type_string']
    
    
    def __init__(self, serializers = []):
        self.__serializers = serializers
        self.__serializer_map = {}

        hasjson = False
        
        # intialize serializers map
        for serializer in serializers:
            self.__serializer_map[serializer.get_type()] = serializer
            if serializer.get_type().name.lower == "json":
                hasjson = True
            
        if not hasjson:
            json = JsonSerializer()
            self.__serializers.append(json)
            self.__serializer_map[json.get_type()] = json
    

    def get_serializer(self, fmt):
        return self.__serializer_map.get(fmt,None)
    
    
    def get_serializers(self):
        return self.__serializers
    
    
    def get_accepted_types(self, accept=None):
        
        if accept is None:
            accept = []
            for s in self.get_serializers():
                accept.append(s.get_type())
                
                
        txt = ""
        for frmt in accept:
            if len(txt) > 0:
                txt = txt + " , "
            txt = txt + frmt.http_format()
        
        return txt;
    

    def get_random_id(self):
        random.seed(datetime.now())
        return random.randint(0,2**31-1)
    
    
    def accepts(self, frmt):
        return frmt in self.__serializer_map
    
    serializers = property(get_serializers)
    
    
    
