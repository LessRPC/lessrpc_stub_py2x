'''
Created on Nov 7, 2017

@author: Salim
'''

import traceback
from exceptions import Exception

from io import BytesIO

import cherrypy


from lessrpc_common.types import StatusType
from lessrpc_common.info.basic import SerializationFormat, \
     ServiceInfo, ServiceLocator
from lessrpc_common.errors.less import AcceptTypeHTTPFormatNotParsable, \
    AcceptTypeNotSupported, WrongHTTPMethodException, ContentTypeNotSupported, \
    ContentTypeHTTPFormatNotParsable, ServiceNotSupportedException
from lessrpc_common.info.response import TextResponse, IntegerResponse, \
    ProviderInfoResponse, ServiceSupportResponse, ExecuteRequestResponse, ServiceResponse     
from lessrpc_common.info.request import ServiceRequest

from lessrpc_stub.stubs.base import Stub, InBase64Wrapper, OutBase64Wrapper
from lessrpc_common.errors.lessrpc import ServerStubNotInitialized
from pylods.deserialize import DeserializationContext
from lessrpc_stub.stubs.client import NSClient




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
            
            

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% server stub handler for cherry py
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 

class ServerStubHandler():
    '''
        Handles different requests
    '''
    
    def __init__(self, stub, provider):
        self.__stub__ = stub
        self.__provider__ = provider
    
    
    @cherrypy.expose    
    def index(self):
        return "Less RPC service"
    
    @cherrypy.expose
    @cherrypy.config(**{'response.stream': True})
    def ping(self):
        '''
        handles lessrpc's /ping request
        '''
        (flag, _, respserializer, status) = self.process_lessrpc_headers(False)
        
        if not flag:
            return status
        
        try:
            out = BytesIO()
            b64 = OutBase64Wrapper(out)
            respserializer.serialize(IntegerResponse(StatusType.OK.value, (1 if self.provider.ping() else 0)), IntegerResponse, b64)
            b64.flush()
            out.seek(0)
            return out
        except:
            return self.prepare_status(StatusType.SERIALIZATION_ERROR, respserializer.get_type())    
        
        
    
    @cherrypy.expose
    def info(self):
        '''
        handles lessrpc's /info request
        '''
        (flag, _, respserializer, status) = self.process_lessrpc_headers(False)
        
        if not flag:
            return status
              
        try:              
            out = BytesIO()
            b64= OutBase64Wrapper(out)
            respserializer.serialize(ProviderInfoResponse(StatusType.OK.value, self.provider.info()), ProviderInfoResponse, b64)
            b64.flush()
            out.seek(0)        
            return out
        except:
            return self.prepare_status(StatusType.SERIALIZATION_ERROR, respserializer.get_type())
    
    @cherrypy.expose        
    def service(self):
        '''
        handles lessrpc's /support request
        '''
        (flag, reqserializer, respserializer, status) = self.process_lessrpc_headers(True)
        
        if not flag:
            return status
        
        try:
            service = reqserializer.deserialize(InBase64Wrapper(BodyWrapper(cherrypy.request.body)), ServiceInfo)
        except:
            traceback.print_exc()
            return self.prepare_status(StatusType.SERIALIZATION_ERROR, respserializer.get_type())

        try:
            sup = self.provider.service(service)
        except:
            traceback.print_exc()
            return self.prepare_status(StatusType.SERVICE_NOT_SUPPORTED, respserializer.get_type())
#           
        try:    
            out = BytesIO()
            b64 = OutBase64Wrapper(out)
            respserializer.serialize(ServiceSupportResponse(StatusType.OK.value, sup), ServiceSupportResponse, b64)
            b64.flush()
            out.seek(0)        
            return out
        except:
            return self.prepare_status(StatusType.SERIALIZATION_ERROR, respserializer.get_type())
        
    @cherrypy.expose   
    def execute(self):
        '''
        handles lessrpc's /execute request
        '''
        
        (flag, reqserializer, respserializer, status) = self.process_lessrpc_headers(True)
        
        if not flag:
            return status
        
        try:
            request = reqserializer.deserialize(InBase64Wrapper(BodyWrapper(cherrypy.request.body)), ServiceRequest, ctxt=DeserializationContext.create_context([("CLSLOCATOR", ServiceLocator.create(self.provider.list_services()))]))
        except:
            traceback.print_exc();
            return self.prepare_status(StatusType.SERIALIZATION_ERROR, respserializer.get_type())
        
        if request is None:
            return self.prepare_status(StatusType.INTERNAL_ERROR, respserializer.get_type(), content="Request was null!!")
            
        try:
            result = self.provider.execute(request)
        except ServiceNotSupportedException:
            return self.prepare_status(StatusType.SERVICE_NOT_SUPPORTED, respserializer.get_type())
        except:
            traceback.print_exc();
            return self.prepare_status(StatusType.INTERNAL_ERROR, respserializer.get_type())
        try:
            out = BytesIO()
            b64 = OutBase64Wrapper(out)
            respserializer.serialize(ExecuteRequestResponse(StatusType.OK.value, ServiceResponse(request.service, result, request.requestid)), ExecuteRequestResponse, b64)
            b64.flush()
            out.seek(0)
            return out
        except:
            traceback.print_exc();
            return self.prepare_status(StatusType.SERIALIZATION_ERROR, respserializer.get_type())        
        
        
    
    def process_lessrpc_headers(self, inputrequired):
        try:
            # parse serialization format
            try:
                respserializer = self.find_accepted_format();
            except AcceptTypeHTTPFormatNotParsable:
                status = self.prepare_status(StatusType.ACCEPT_TYPE_CANNOT_BE_PARSED, SerializationFormat.default_format())
                return (False, None, None, status);
            except AcceptTypeNotSupported:
                status = self.prepare_status(StatusType.ACCEPT_TYPE_NOT_SUPPORTED, SerializationFormat.default_format())
                return (False, None, None, status);
            # setting response serialization format regardless if there is an error
            # or successful attempt
            cherrypy.response.headers['Content-Type'] = respserializer.get_type().http_format()
            
            # check if get and post are being used properly
            try:
                self.check_http_method_type(inputrequired)
            except WrongHTTPMethodException:
                status = self.prepare_status(StatusType.WRONG_HTTP_METHOD, SerializationFormat.default_format())
                return (False, None, None, status);
                
            # check if content-type exists and it is parsable and supported
            try:
                reqserializer = self.parse_content_type(inputrequired)
            except ContentTypeHTTPFormatNotParsable:
                status = self.prepare_status(StatusType.CONTENT_TYPE_CANNOT_BE_PARSED, SerializationFormat.default_format())
                return (False, None, None, status);
            except ContentTypeNotSupported:
                status = self.prepare_status(StatusType.CONTENT_TYPE_NOT_SUPPORTED, SerializationFormat.default_format())
                return (False, None, None, status);
            
            return (True, reqserializer, respserializer, None)
        
            
            
            
            

        except Exception as e:
            print("Unexpected error has happened!! " + str(e))
            self.prepare_status(StatusType.INTERNAL_ERROR, SerializationFormat.default_format())
    
    
    def find_accepted_format(self):
        accept = cherrypy.request.headers.get("Accept")
        if accept is None or len(accept) == 0:
            raise AcceptTypeHTTPFormatNotParsable(accept)
        # checking accepted formats
        
        formats = None
        try:
            formats = self.parse_accepted_formats(accept)
        except:
            raise AcceptTypeHTTPFormatNotParsable(accept)
        
        if formats is None or len(formats) == 0:
            raise AcceptTypeHTTPFormatNotParsable(accept)
        
        # getting the first supported serializer
        responeformat = self.stub.find_first_accepted_format(formats);
        if responeformat is None:
            raise AcceptTypeNotSupported(accept)
        
        return self.stub.get_serializer(responeformat)  
        
            
        
        
    def parse_accepted_formats(self, txt):
        parts = txt.split(",")
        formats = []
        
        for part in parts:
            formats.append(SerializationFormat.parse_http_format(part))
        
        return formats
    
    
    def parse_content_type(self, inputrequired):
        
        contenttype = cherrypy.request.headers.get("Content-Type")
        requestformat = None
        requestserializer = None
        
        if contenttype is not None and len(contenttype) > 0:
            try:
                requestformat = SerializationFormat.parse_http_format(contenttype)
            except:
                raise ContentTypeHTTPFormatNotParsable(contenttype)
            requestserializer = self.stub.get_serializer(requestformat)
            if requestserializer is None:
                raise ContentTypeNotSupported(requestformat)
        else:
            if inputrequired:
                raise ContentTypeHTTPFormatNotParsable(contenttype)
            
        
        return requestserializer
    
    
    def prepare_status(self, status, frmt=None, content=None):
        if frmt is not None:
            cherrypy.response.headers['Content-Type'] = frmt.http_format()
            
        if content is None:
            content = status.name

        serializer = self.stub.get_serializer(frmt)

        out = BytesIO()        
        b64=OutBase64Wrapper(out)
        serializer.serialize(TextResponse(status.value, content), TextResponse, b64)
        b64.flush()
        return out.getvalue()
        
        
        
        
    
    def check_http_method_type(self, inputrequired):
        if inputrequired and cherrypy.request.method.upper() != 'POST':
            raise WrongHTTPMethodException(cherrypy.request.method.upper())
        
        if not inputrequired and cherrypy.request.method.upper() == 'POST':
            raise WrongHTTPMethodException(cherrypy.request.method.upper())
            
    

    
    def __get_stub__(self):
        return self.__stub__;
    
    stub = property(__get_stub__)
    
    def __get_provider__(self):
        return self.__provider__;
    
    provider = property(__get_provider__)






# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% server stub 
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

class ServerStub(Stub):
    '''
    basic ServerStub class for lessRPC 
    '''
    
    
    def __init__(self, provider, serializers=[]):
        Stub.__init__(self, serializers)
        self.__port__ = provider.info().port
        self.__provider__ = provider
        
        
    
    
    def start(self):
        if self.__provider__ is None:
            raise ServerStubNotInitialized()
        
        self.before_start();
        
        
        
        cherrypy.config.update({'server.socket_port': self.__port__})
        cherrypy.tree.mount(ServerStubHandler(self, self.__provider__))
        cherrypy.engine.start()
        cherrypy.engine.block()
        
        self.after_start()
    
    
    def before_start(self):
        '''
            calls anything needs to be executed before starting
        '''
        pass
    
    def after_start(self):
        '''
            writes anything that needs to be executed after already started
        '''
        pass
    
    
    def stop(self):
        '''
        stop the server
        '''
        self.before_stop();
        cherrypy.engine.exit()
        self.after_stop();
    
    
    def before_stop(self):
        '''
            runs what needs to be executed before stopping the server
        '''
        pass
    
    def after_stop(self):
        '''
            runs anything needed to be executed after server has stopped
        '''
        pass
    
    
    def __get_port(self):
        return self.__port__
    
    def __get_provider(self):
        return self.__provider__
    
    
    
    def find_first_accepted_format(self, formats):
        '''
            finds the first accepted format from a list of formats
        :param formats: list of SerializationFormat
        :return format: an instance of SerializationFormat
        '''
        if formats is None or len(formats) == 0:
            return None
        
        for frmt in formats:
            if(self.accepts(frmt)):
                return frmt
        
        return None
    
    
    port = property(__get_port)
    provider = property(__get_provider)
    
    

class NSServerStub(ServerStub):
    
    def __init__(self, provider, nsinfo, serializers=[]):
        ServerStub.__init__(self, provider, serializers)
        self.__nsinfo__ = nsinfo
        self.__ns__ = NSClient(nsinfo, serializers)
        

    def after_start(self):
        '''
            Registers all supported services for this provider
        '''
        for support in self.provider.list_support():
            self.ns.register(support)
        
        
    def before_stop(self):
        '''
            unregisters all services just before stopping the server stub
        '''
        self.ns.unregister_all(self.provider.info())
        
        
        
        
    
    def __get_nsinfo(self):
        return self.__nsinfo__
    
    def __get_ns(self):
        return self.__ns__

    
    nsinfo = property(__get_nsinfo)
    ns = property(__get_ns)    






    
    
    



