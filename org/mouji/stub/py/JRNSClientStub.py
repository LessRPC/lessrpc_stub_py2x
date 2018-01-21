'''
Created on Jul 21, 2017

@author: Salim
'''

import requests
import json
import socket
from org.mouji.stub.py import JRNSStub
from org.mouji.stub.py.StubConstants import RPC_PROTOCOL


class JRNSClientStub(JRNSStub):
    
    def __init__(self, ns_info):
        self.ns_info = ns_info

    def call(self, service, args):
        provider = self._findProvider(self.ns_info, service);
        return self._call(service, provider, args);
    
    
    def _call(self, service, provider, args_json):
        url = RPC_PROTOCOL + provider.getIP() + ":" + str(provider.getPort()) + "/JRNSProviderService.json"
        headers = {'content-type': 'application/json'}
            
        
        # Example echo method
        payload = {
            "method": "execute", 
            "params": [ClientInfo(socket.gethostbyname(socket.gethostname()), StubEnvType.PYTHON).__dict__, service.__dict__,args_json],
            "jsonrpc": "2.0",
            "id": 0,
        }
        
        
        response = requests.post(
            url, data=json.dumps(payload), headers=headers).json()
     
        
        print(response['result'])
    
        execResponse = ExecutionResponse.from_dict(response['result']);
        
    
        clspath = execResponse.getResponseInfo().getOutputType();
        
        if( len(clspath.split(".")) <= 1):
            return json.loads(execResponse.getObjectJson());
        else:
            cls = class_for_name(clspath);                        
            json_dict = json.loads(execResponse.getObjectJson())
            return cls(**json_dict)
        
        
        
        
    
    
    def _findProvider(self, ns_info, service):
        url = RPC_PROTOCOL + ns_info.getAddress() + ":" + str(ns_info.getPort()) + "/NSService.json"
        headers = {'content-type': 'application/json'}
    
        # Example echo method
        payload = {
            "method": "getServerById",
            "params": [service.getId()],
            "jsonrpc": "2.0",
            "id": 0,
        }
        response = requests.post(
            url, data=json.dumps(payload), headers=headers).json()
    
        print(response['result'])
        return ServiceProviderInfo.from_dict(response['result']);
    
    
    
    
