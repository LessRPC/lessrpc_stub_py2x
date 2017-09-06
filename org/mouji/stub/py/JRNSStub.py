'''
Created on Jul 21, 2017

@author: Salim
'''
import json
import requests

from  org.mouji.jrns.common.Constants import RPC_PROTOCOL
from org.mouji.jrns.common.info.ServiceInfo import ServiceInfo


class JRNSStub:
    
    def __init__(self):
        pass
    
    
    def getServiceInfoById(self, ns_info, service_id):        
        url = RPC_PROTOCOL + ns_info.getAddress() + ":" + str(ns_info.getPort()) + "/NSService.json"
        headers = {'content-type': 'application/json'}
    
        # Example echo method
        payload = {
            "method": "getServiceInfoById",
            "params": [service_id],
            "jsonrpc": "2.0",
            "id": 0,
        }
        response = requests.post(
            url, data=json.dumps(payload), headers=headers).json()
    
        return ServiceInfo.from_dict(response['result']);
    
    def getServiceInfoByName(self, ns_info, service_name):
        url = RPC_PROTOCOL + ns_info.getAddress() + ":" + str(ns_info.getPort()) + "/NSService.json"
        headers = {'content-type': 'application/json'}
    
        # Example echo method
        payload = {
            "method": "getServiceInfoByName",
            "params": [service_name],
            "jsonrpc": "2.0",
            "id": 0,
        }
        response = requests.post(
            url, data=json.dumps(payload), headers=headers).json()
    
        return ServiceInfo.from_dict(response['result'])
