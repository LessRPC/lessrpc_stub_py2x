'''
Created on Nov 7, 2017

@author: Salim
'''
from lessrpc_common.serialize import Serializer
from lessrpc_common.info.basic import SerializationFormat
from pylodsjson.pylodsjson import JsonObjectMapper, JsonParser
from pylods.deserialize import DeserializationContext




class JsonSerializer(Serializer):
    '''
        JSONSerializer is the default serializer for less RPC if a serializer couldn't be recognized
    '''
    
    __slots__ = ['__mapper']
    
    def __init__(self, mapper=JsonObjectMapper()):
        self.__mapper = mapper
        
    
    def serialize(self, obj, cls, outstream): 
        '''
            serialize into outstream
        :param obj:
        :param cls:
        :param outstream:
        :return no output
        '''
        self.__mapper.write(obj, outstream) 
        
        
    def deserialize(self, instream, cls, ctxt=DeserializationContext.create_context()): 
        '''
            deserialize instream
        :param instream: inputstream
        :param cls class of object to be read:
        :return object instance of class cls
        '''
        parser = JsonParser()
        parser = parser.parse(instream)
        return self.__mapper.read_obj(parser, cls, ctxt=ctxt)
        
    def get_type(self):
        return SerializationFormat("JSON", "")
        

    def prepare(self, module):
        self.__mapper.register_module(module)
    
    
    def copy(self):
        tmp = JsonSerializer()
        tmp.__mapper = self.__mapper.copy()
        return tmp
    
    
