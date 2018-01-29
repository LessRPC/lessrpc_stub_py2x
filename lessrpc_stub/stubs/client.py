'''
Created on Nov 7, 2017

@author: Salim
'''
from lessrpc_stub.stubs.base import Stub, OutBase64Wrapper, InBase64Wrapper
from lessrpc_stub.StubConstants import LESS_RPC_REQUEST_PING, LESS_RPC_REQUEST_INFO, LESS_RPC_REQUEST_SERVICE, LESS_RPC_REQUEST_EXECUTE, HTTP_WAIT_TIME_SHORT, HTTP_WAIT_TIME_LONG
import httplib
from lessrpc_common.errors.less import ResponseContentTypeCannotBePrasedException, \
    SerializationFormatNotSupported, ApplicationSpecificErrorException, \
    RPCProviderFailureException, ServiceProviderNotAvailable
from lessrpc_common.info.basic import SerializationFormat, ServiceInfo, \
    EnvironmentInfo, ServiceLocator, ServiceDescription
from lessrpc_common.errors.lessrpc import RPCException
from lessrpc_common.info.response import TextResponse, IntegerResponse, \
    ProviderInfoResponse, ServiceSupportResponse, ExecuteRequestResponse
from pylods.error import ParseException
from io import BytesIO
from lessrpc_stub.serializer import JsonSerializer
from lessrpc_common.info.request import ServiceRequest
from httpoutputstream.stream import HttpBufferedOutstream
from pylods.deserialize import DeserializationContext
from lessrpc_common.services import NameServerServices, \
    NameServerFunctions
from lessrpc_stub.cache import NoCache, SimpleCache
from lessrpc_stub.errors import NoProviderAvailableException
import traceback
import base64





class ClientStub(Stub):

    def __init__(self, serializers=[]):
        Stub.__init__(self, serializers)
        
        
        
    
    def call(self, desc, spInfo, args, serializer, timeout=HTTP_WAIT_TIME_LONG, accept=None):
        '''
        
        :param service: ServiceInfo
        :param spInfo: ServiceProviderInfo 
        :param args: array of arguments as any kind of object
        :param serializer: Serializer used
        :return ServiceResponse: 
        '''
        
        request = ServiceRequest.create(desc.info, EnvironmentInfo.current_env_info() , self.get_random_id(), args)
        
        result = None
        
        try:
            headers = {'Accept': self.get_accepted_types(accept), 'Content-Type':serializer.get_type().http_format(), 'Transfer-Encoding': 'chunked'}
            
            # http connection
            conn = httplib.HTTPConnection(str(spInfo.url) + ":" + str(spInfo.port), timeout=timeout)
            conn.putrequest("POST", LESS_RPC_REQUEST_EXECUTE)
            for hdr, value in headers.iteritems():
                conn.putheader(hdr, value)
            conn.endheaders()
            
            # create an outputstream for http connection
            out= HttpBufferedOutstream(conn)
            b64 = OutBase64Wrapper(out)
            serializer.serialize(request, ServiceRequest, b64)
            b64.flush()
            out.close()
            
            # read response
            response = conn.getresponse()
            
            ctxt = DeserializationContext.create_context([("CLSLOCATOR", ServiceLocator.create([desc]))])
            result = self._read_response(response, ExecuteRequestResponse, ctxt)
            conn.close()
        except ResponseContentTypeCannotBePrasedException:
            raise
        except SerializationFormatNotSupported :
            raise
        except RPCProviderFailureException:
            raise
        except ParseException:
            raise
        except :
            traceback.print_exc();
            raise
        return result.content
    
    def ping(self, spInfo, timeout=HTTP_WAIT_TIME_SHORT):
        '''
             pings a service provider to assure it working. It will return true of
             service provide is working and running propery. It will return false if
             provide doesn't exist on network or of the provider provides a false due
             to internal system error
        '''
        flg = True
        ping = None
        
        
        headers = {'Accept': self.get_accepted_types([SerializationFormat.default_format()])}
        try:
            conn = httplib.HTTPConnection(str(spInfo.url) + ":" + str(spInfo.port), timeout=timeout)
            conn.request("GET", LESS_RPC_REQUEST_PING, headers=headers)
            response = conn.getresponse()
            ping = self._read_response(response, IntegerResponse)
            conn.close()
        except ResponseContentTypeCannotBePrasedException:
            raise
        except SerializationFormatNotSupported :
            raise
        except RPCProviderFailureException:
            raise
        except ParseException:
            raise
        except :
            flg = False
            
            
        if not flg or ping.content is None or ping.content != 1:
            return False
        else:
            return True
        
    
    def get_info(self, url, port, timeout=HTTP_WAIT_TIME_SHORT):
        '''
             calls /info service of a service provider
             :param url:
             :param port:
             :return instance of ServiceProivderInfo
        '''
        info = None
        
        headers = {'Accept': self.get_accepted_types([SerializationFormat.default_format()])}
        try:
            conn = httplib.HTTPConnection(url + ":" + str(port), timeout=timeout)
            conn.request("GET", LESS_RPC_REQUEST_INFO, headers=headers)
            response = conn.getresponse()
            info = self._read_response(response, ProviderInfoResponse)
            conn.close()
        except Exception:
            raise 
            
        return info.content;
        
        
    def get_service_support(self, spInfo, service, timeout=HTTP_WAIT_TIME_SHORT):
        '''
            executes /service service for given service to given service provider
        :param spInfo: ServiceProviderInfo:
        :param service: ServiceInfo:
        :return ServiceSupportInfo
        '''
        serializer = self.get_serializer(SerializationFormat.default_format());
        
        
        try:
            out = OutBase64Wrapper(BytesIO())
            serializer.serialize(service, ServiceInfo, out)
            length = out.tell()
            out.seek(0)
            
            headers = {'Accept': self.get_accepted_types([SerializationFormat.default_format()]), 'Content-Type':serializer.get_type().http_format(), 'Content-Length': length}
            
            # http connection
            conn = httplib.HTTPConnection(str(spInfo.url) + ":" + str(spInfo.port), timeout=timeout)
            conn.putrequest("POST", LESS_RPC_REQUEST_SERVICE)
            for hdr, value in headers.iteritems():
                conn.putheader(hdr, value)
            conn.endheaders()
            conn.send(out)
            # send results as stream
            
            
            response = conn.getresponse()
            support = self._read_response(response, ServiceSupportResponse)
            conn.close()
        except Exception:
            raise 
        
        return support.content

        
    def _read_response(self, response, cls, ctxt=DeserializationContext.create_context()):
        
        # TODO handle response status
        if response.msg is None or response.msg.gettype() is None or len(response.msg.gettype()) < 1:
            raise ResponseContentTypeCannotBePrasedException(response.msg.gettype())
            return  # TODO send error
        
        contenttype = response.msg.gettype() + " ;" + " ; ".join(response.msg.getplist())
            
        # read format
        frmt = None
        try:
            frmt = SerializationFormat.parse_http_format(" ; ".join(response.msg.getplist()))
        except :
            raise ResponseContentTypeCannotBePrasedException(contenttype);
        
        # if no format was read
        if format is None:
            raise ResponseContentTypeCannotBePrasedException(contenttype);
        

        serializer = self.get_serializer(frmt);

        if serializer is None:
            raise SerializationFormatNotSupported(frmt);

        # checking status
        if response.status != httplib.OK:
            error = self._read_error(response, serializer);
            if error.status > 3000:
                raise ApplicationSpecificErrorException(error.status, error.content);
            else:
                raise RPCException(error.status, error.content);

        # status is OK so read response
        try:
            return serializer.deserialize(InBase64Wrapper(response), cls, ctxt=ctxt);
        except:
            raise 
        
        
    def _read_error(self, response, serializer):
        '''
        
        :param response: the http client request's response
        :param serializer: the serialize to prarse content type
        :return TextResponse instance
        '''
        return serializer.deserialize(InBase64Wrapper(response), TextResponse);
    
    
    

class NSClient(ClientStub, NameServerFunctions):    
    
    
    def __init__(self, nsInfo, serializers=[]):
        self.__nsInfo = nsInfo
        ClientStub.__init__(self, serializers)
    
    
    
    
    def get_provider(self, service):
        '''
            Returns one service provider information for a service given the
            service's id. The process of choosing a service provider may have been
            random or based on a load balancing strategy. However, the decision is
            made by the name server        
        :param service:
        '''
        response = ClientStub.call(self, NameServerServices.GET_PROVIDER, self.nsinfo, [service], self.get_serializer(SerializationFormat.default_format()), timeout=HTTP_WAIT_TIME_SHORT)
        return response.content
    
    
    def get_providers(self, service):
        '''
            This function returns all service providers implementing the requested service
        :param service:
        '''
        response = ClientStub.call(self, NameServerServices.GET_PROVIDERS, self.nsinfo, [service], self.get_serializer(SerializationFormat.default_format()), timeout=HTTP_WAIT_TIME_SHORT)
        return response.content
    
    
    def get_all_providers(self):
        '''
            returns all Service Provider informations for all available services
        '''
        response = ClientStub.call(self, NameServerServices.GET_ALL_PROVIDERS, self.nsinfo, [], self.get_serializer(SerializationFormat.default_format()), timeout=HTTP_WAIT_TIME_SHORT)
        return response.content
    
    
    def get_service_info_by_name(self, name):
        '''
            returns a service information object for given service name
        :param name:
        '''
        response = ClientStub.call(self, NameServerServices.GET_SERVICE_INFO_BY_NAME, self.nsinfo, [name], self.get_serializer(SerializationFormat.default_format()), timeout=HTTP_WAIT_TIME_SHORT)
        return response.content
    
    
    def get_service_info_by_id(self, sid):
        '''
            returns a service information object for given service id
        :param sid:
        '''
        response = ClientStub.call(self, NameServerServices.GET_SERVICE_INFO_BY_ID, self.nsinfo, [sid], self.get_serializer(SerializationFormat.default_format()), timeout=HTTP_WAIT_TIME_SHORT)
        return response.content
    
    
    def register(self, support):
        '''
            Registers a new service provider for given service information
        :param support:
        '''
        response = ClientStub.call(self, NameServerServices.REGISTER, self.nsinfo, [support], self.get_serializer(SerializationFormat.default_format()), timeout=HTTP_WAIT_TIME_SHORT)
        return response.content
    
    def unregister(self, service, provider):
        '''
            Unregisters a new service provider for given service information
        :param service:
        :param provider:
        '''
        response = ClientStub.call(self, NameServerServices.UNREGISTER, self.nsinfo, [service, provider], self.get_serializer(SerializationFormat.default_format()), timeout=HTTP_WAIT_TIME_SHORT)
        return response.content
    
    
    def unregister_all(self, provider):
        '''
            Unregisters a new service provider for all of the registered services
        :param provider:
        '''
        response = ClientStub.call(self, NameServerServices.UNREGISTER_ALL, self.nsinfo, [provider], self.get_serializer(SerializationFormat.default_format()), timeout=HTTP_WAIT_TIME_SHORT)
        return response.content
    
    
    def check_provider_status(self, provider):
        '''
            This function forces the name server to check a provider's status and
            update its tables. The returned boolean indicates that the check was done
            or not and is not related to the actual status of the provider
        :param provider:
        '''
        response = ClientStub.call(self, NameServerServices.CHECK_PROVIDER_STATUS, self.nsinfo, [provider], self.get_serializer(SerializationFormat.default_format()), timeout=HTTP_WAIT_TIME_SHORT)
        return response.content
    
    
    def ping(self):
        '''
            Determines if everything is working properly
        '''
        return ClientStub.ping(self, self.nsinfo)
        
        
        
    def __get_nsinfo(self):
        return self.__nsInfo
    
    nsinfo = property(__get_nsinfo)
    


class NSClientStub(ClientStub):    
    
    
    def __init__(self, nsInfo, cache=NoCache(), serializers=[]):
        ClientStub.__init__(self, serializers)
        self.__nsInfo = nsInfo
        self.__ns = NSClient(nsInfo, serializers)
        self.__cache = cache
    
    def get_service_support(self, service):
        return ClientStub.get_service_support(self, self._get_provider(service).provider, service);
    
    def _get_provider(self, service):
        '''
            Retrieves a provider from cache. If it doesn't exist then it requests one from database
        :param service:
        '''
        # attempts to get the cached service provider for the given service
        info = self.cache.get(service);
        # checks if an info is cached for the given service
        if info is None:
            info = self.ns.get_provider(service);
            self.cache.cache(info);
        
        if info is None:
            raise  ServiceProviderNotAvailable(service);
            
        return info;
    
    
    def call(self, desc, args, serializer, accept=None):
        '''
        calls execute service. It uses cached service provider or retrieves an
        available provider from the name server
        
        :param service:
        :param args:
        :param serializer:
        '''
        provider = self._get_provider(desc.info).provider
        
        if provider is None:
            # no provider existed so throw appropriate Exception
            raise NoProviderAvailableException(desc.info)
        
        # provider existed so try to connect
        response = None;
        
        try :
            response = ClientStub.call(self, desc, provider, args, serializer, accept);
        except (ResponseContentTypeCannotBePrasedException, RPCException, SerializationFormatNotSupported):
            # none connectivity error happened
            raise
        except (RPCProviderFailureException):
            # a connectivity error happened. So try to find a new Provider
            # clear cache
            self.cache.clear(desc.inf);
            # check if provider still works
            self.ns.check_provider_status(provider);
            # call again and it will ask for a provider from NameServer
            # accordingly
            self.call(desc, args, serializer);
        except:
            # other none connectivity errors
            raise

        return response;
        
    
    def get_service_info_by_id(self, sid):
        return self.ns.get_service_info_by_id(sid);
    
    def get_service_info_by_name(self, name):
        return self.ns.get_service_info_by_name(name);        
    
    def __get_ns(self):
        return self.__ns
    
    def __get_cache(self):
        return self.__cache
    
    def __get_nsinfo(self):
        return self.__nsinfo
    
    ns = property(__get_ns)
    cache = property(__get_cache)  
    nsinfo = property(__get_nsinfo)      
            
# c = ClientStub()
# 
# info = c.get_info("localhost", 6060)
# print(info)
# flag = c.ping(info)
# print(flag)
# # 
# support = c.get_service_support(info, ServiceInfo("getProvider", 1))
# print(support)
# # print(EnvironmentInfo.current_env_info())
# 
# json = JsonSerializer()
# req = ServiceRequest(ServiceInfo("getProvider", 1), EnvironmentInfo.current_env_info(), 1, [10])
# json = JsonSerializer()
# out = BytesIO()
# json.serialize(req, ServiceRequest, out)
# 
# 

# ns = NSClient(info)
# flag = ns.ping()
# print(flag)
# 
# 
# service = provider = ns.get_service_info_by_id(10)
# print(service)
# 
# service  = ns.get_service_info_by_name(service.name)
# print(service)
# 
# 
# support = ns.get_provider(ServiceInfo("test", 10))
# print(support)
# 
# support = ns.get_providers(ServiceInfo("test", 10))
# if(len(support) > 0):
#     support = support[0]
#     print(support)
# 
# ns.unregister(support.service, support.provider)
#  
# support2 = ns.get_provider(ServiceInfo("test", 10))
# print(support2)
# 
# ns.register(support)
# 
# support = ns.get_provider(ServiceInfo("test", 10))
# print(support)
# 
# 
# support = ns.get_provider(ServiceInfo("test", 10))
# print(support)
# 
# flag = ns.check_provider_status(support.provider)
# print(flag)
# 
# ns.unregister_all(support.provider)
# 
# support2 = ns.get_provider(ServiceInfo("test", 10))
# print(support2)
# 
# ns.register(support)
# 
# support = ns.get_provider(ServiceInfo("test", 10))
# print(support)


# out = BytesIO()
# json.serialize(sp.content[0], ServiceRequest,out)
# print("** "+out.getvalue())
# 
# request = ServiceRequest.create(NameServerServices.CHECK_PROVIDER_STATUS.info, EnvironmentInfo.current_env_info() , 1, [sp.content[0]])
# out = BytesIO()
# json.serialize(request, ServiceRequest,out)
# print(out.getvalue())

# provider = ns.get_provider(ServiceInfo("test", 10))


# flag = ns.check_provider_status(provider)
# print(flag)



if __name__ == '__main__':

    c = ClientStub()
    nsInfo = c.get_info("localhost", 6060)
    print(nsInfo)
    flag = c.ping(nsInfo)
    print(flag)
    
    
    client = NSClientStub(nsInfo, SimpleCache())
    
    service = client.get_service_info_by_id(10)
    print(service)
    
    service = client.get_service_info_by_name('test')
    print(service)
    
    
    prov = client._get_provider(service)
    print(prov)
    
    sup = client.get_service_support(service)
    print(sup)
    
    
    res = client.call(ServiceDescription(service, [int], int), [5], JsonSerializer());
    print(res)
