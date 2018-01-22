
import unittest
from lessrpc.common.info.basic import EnvironmentInfo, \
    ServiceProviderInfo, SerializationFormat, ServiceInfo, ServiceSupportInfo, \
    ServiceDescription
from lessrpc.common.errors.less import ServiceNotSupportedException
from lessrpc.common.services import ServiceProvider
from lessrpc.stub.stubs.server import ServerStub
import threading
from lessrpc.stub.stubs.client import ClientStub
from lessrpc.stub.serializer import JsonSerializer


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% test
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

class TestProvider(ServiceProvider):
    
    
    def ping(self):
        '''
            This is called to check if the server is working. It has to just return a boolean flag
        '''
        return True
    
    
    def execute(self, request):
        '''
            This is called to execute a service
            
        :param request:
        '''
        if request.service.sid == 1:
            return 5
        elif request.service.sid == 2:
            return ServiceInfo('test', 1)
        else:
            raise ServiceNotSupportedException(request.service)
    
    
    def info(self):
        '''    
              This is called to get the ServiceProivder info regarding this service provider
        '''
        return ServiceProviderInfo("localhost", 4342, EnvironmentInfo.current_env_info())
    
    
    def service(self, service):
        '''
            This is called to get ServuceSupportInfo for a service. It will return ServiceNotSupported Exception
            
        :param service:
        '''
        if service.sid == 1:
            return ServiceSupportInfo(service, ServiceProviderInfo("localhost", 4342, EnvironmentInfo.current_env_info()), [SerializationFormat.default_format()])
        else:
            return ServiceSupportInfo(service, ServiceProviderInfo("localhost", 4342, EnvironmentInfo.current_env_info()), [SerializationFormat.default_format()])
    
    
    
    def list_support(self):
        '''
            Returns the list of all supported services
        '''
        return [ServiceSupportInfo(ServiceInfo('test', 1), ServiceProviderInfo("localhost", 4342, EnvironmentInfo.current_env_info()), [SerializationFormat.default_format()])]
    
    
    def list_services(self):
        '''
            Returns the list of all supported services
        '''
        return [ServiceDescription(ServiceInfo('test', 1), [int, int], int), ServiceDescription(ServiceInfo('test2', 2), [int], ServiceInfo)]




class TestServerClient(unittest.TestCase):
    
    
    
    @classmethod
    def setUpClass(cls):
        prov = TestProvider()
        cls.stub = ServerStub(prov, serializers=[JsonSerializer()])
        cls.spinfo = prov.info();
        cls.t = threading.Thread(target=cls.stub.start)
        cls.t.start()
        threading._sleep(1)
    
    def test_ping(self):
        client = ClientStub([]);
        flag = client.ping(self.__class__.spinfo)
        self.assertTrue(flag)
        
    def test_ping_false(self):
        client = ClientStub([]);
        flag = client.ping(ServiceProviderInfo("localhost", 8789, EnvironmentInfo.current_env_info()))
        self.assertFalse(flag)
        
        
    def test_info(self):
        client = ClientStub([]);
        spinfo = client.get_info("localhost", self.spinfo.port)
        self.assertEquals(self.spinfo, spinfo)
    
    def test_info_notconnected(self):
        try:
            client = ClientStub([]);
            client.get_info("localhost", 8787)
        except:
            self.assertTrue(True)
            return
        
        self.assertTrue(False)
        
        
        
    def test_service(self):
        client = ClientStub([]);
        sup = client.get_service_support(self.spinfo, ServiceInfo('test', 1))
        self.assertEqual(ServiceSupportInfo(ServiceInfo('test', 1), ServiceProviderInfo("localhost", 4342, EnvironmentInfo.current_env_info()), [SerializationFormat.default_format()]), sup)
        
    
    def test_execute(self):
        client = ClientStub([]);
        desc = ServiceDescription(ServiceInfo('test', 1), [int, int], int) 
        res = client.call(desc, ServiceProviderInfo("localhost", 4342, EnvironmentInfo.current_env_info()), [1, 2], JsonSerializer())
        
        self.assertEquals(res, res)
        
        
    def test_execute_choose_format(self):
        client = ClientStub([JsonSerializer()]);
        desc = ServiceDescription(ServiceInfo('test', 1), [int, int], int) 
        res = client.call(desc, ServiceProviderInfo("localhost", 4342, EnvironmentInfo.current_env_info()), [1, 2], JsonSerializer(), accept=[SerializationFormat("MSGPACK", "2.0")])
        
        self.assertEquals(res, res)
    
    def test_execute_clspath(self):
        client = ClientStub([]);
        desc = ServiceDescription(ServiceInfo('test2', 2), [int, int], ServiceInfo) 
        res = client.call(desc, ServiceProviderInfo("localhost", 4342, EnvironmentInfo.current_env_info()), [1, 2], JsonSerializer())
        self.assertEquals(ServiceInfo('test', 1), res.content)    
        
    @classmethod
    def tearDownClass(cls):
        cls.stub.stop()
        
        
        
        
if __name__ == '__main__':
    unittest.main()
    
