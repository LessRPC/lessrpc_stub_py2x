'''
Created on Nov 7, 2017

@author: Salim
'''

import random
from datetime import datetime
from lessrpc_stub.serializer import JsonSerializer
import base64
from _io import BytesIO







class Stub():
    
    __slots__ = ['__serializers', '__serializer_map', '__accepted_type_string']
    
    
    def __init__(self, serializers=[]):
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
        return self.__serializer_map.get(fmt, None)
    
    
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
        return random.randint(0, 2 ** 31 - 1)
    
    
    def accepts(self, frmt):
        return frmt in self.__serializer_map
    
    serializers = property(get_serializers)
    
    
class BodyWrapper():
    
    def __init__(self, body): 
        self.body = body
        self.cache = None
        
        
    def read(self, size=None):
        
            
        if size is not None and size == 0:
            if self.cache is None:
                self.cache = self.body.read(1)
            else:
                self.cache = self.cache + self.body.read(1)  
            return self.cache[0:0]
        else:
            data = None
            if size is None:
                data = self.body.read()
            else:
                data = self.body.read(size)
            
            if self.cache is not None:
                data = self.cache + data;
                self.cache = None
            
            return data    
    
 
class InBase64Wrapper():
    
    DO_BASE64 = False
    
    def __init__(self, instream):
        self.instream = instream
        self.cache = ''
        
        
     
    def read(self, size=-1):
        if self.DO_BASE64 :
        
            data = self.instream.read(size)
            finished = len(data) < size or size == -1
            
            if finished:
                return base64.b64decode(self.cache + data)
            else:
                idx = data.rfind('\n')
                idx = max(idx, data.rfind('='))
                if idx > -1:
                    out = base64.b64decode(self.cache + data[0:idx])
                    self.cache = data[idx:]
                    return out
                else:
                    self.cache = self.cache + data
        else:
            return self.instream.read(size)
        
    
    def close(self):
        self.instream.close()
            
    
class OutBase64Wrapper():
    
    
    DO_BASE64 = False
    
    def __init__(self, outstream):
        self.outstream = outstream
        self.cache = ''


    
    def write(self, data):
        if self.DO_BASE64 :
            size = len(data) + len(self.cache)
            sizetowrite = int(round(size / 3))*3
            fromcache = min(sizetowrite, len(self.cache))
            out = self.cache[0:fromcache] + data[0:(sizetowrite - fromcache)]
            self.cache = self.cache[fromcache:len(self.cache)] + data[(sizetowrite - fromcache):len(data)]
            self.outstream.write(base64.b64encode(out))
        else:
            self.outstream.write(data)
        

    
    def flush(self):
        if self.DO_BASE64 :
            if len(self.cache) > 0:
                self.outstream.write(base64.b64encode(self.cache))
                self.outstream.flush()
        else:
            self.outstream.flush()
    
    def close(self):
        self.flush()
        self.outstream.close()
    
    

# out = BytesIO()
# out.write(base64.b64encode("test-ts-xx-yyy-zzzz-mmmmm"))
# out.seek(0)
# # 
# b64= InBase64Wrapper(out)
# 
# print(b64.read(2))
# print(b64.read(4))
# print(b64.read(1))
# print(b64.read(10))
# print(b64.read(7))
# print(b64.read(1))
# print(b64.read(1))




# out = BytesIO()
# # 
# b64 = OutBase64Wrapper(out)
# b64.write("1234"); print(out.getvalue())
# b64.write("5"); print(out.getvalue())
# b64.write("67"); print(out.getvalue())
# b64.write(""); print(out.getvalue())
# b64.flush(); print(out.getvalue())


#
