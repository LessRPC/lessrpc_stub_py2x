'''
Created on Nov 7, 2017

@author: Salim
'''
from abc import abstractmethod
from abc import ABCMeta



class ServiceProviderCache():
    __metaclass__ = ABCMeta
    
            
    @abstractmethod
    def cache(self, support):
        '''
            Caches a support entry for the service
        :param support of type ServiceSupportInfo:
        '''
    
    @abstractmethod
    def get(self, service):
        '''
            returns the cached ServiceProviderInfo for the given service
        :param service of type ServiceInfo:
        '''
        
        
    @abstractmethod
    def get_by_id(self, serviceid):
        '''
            returns the cached ServiceProviderInfo for the given service
        :param serviceid:
        '''
        
        
    @abstractmethod
    def cache_exists_by_id(self, serviceid):
        '''
            check if cache exists for given service id
        :param serviceid:
        '''
    
    @abstractmethod
    def cache_exists(self, service):
        '''
            check if cache exists for given service id
        :param service of type ServiceInfo:
        '''

        
    @abstractmethod
    def clear_by_id(self, serviceid):    
        '''
            clears the cache for the given service
        :param serviceid:
        '''
        
        
    @abstractmethod
    def clear(self, service):
        '''
            clears the cache for the given service
        :param service of type ServiceInfo:
        '''
        
        
        
    @abstractmethod
    def reset(self):
        '''
            resets all entries in cache
        '''
        
        
        
        
        



class NoCache(ServiceProviderCache):
    '''
        Dummy ServiceProviderCache implementation that doesn't do anything
    '''
    
            
    def cache(self, support):  # @UnusedVariable
        return

    def get(self, service):  # @UnusedVariable
        return None
    
    def get_by_id(self, serviceid):  # @UnusedVariable
        return None
    
        
    def cache_exists_by_id(self, serviceid):  # @UnusedVariable
        return False
    
    def cache_exists(self, service):  # @UnusedVariable
        return False
    
        
    def clear_by_id(self, serviceid):  # @UnusedVariable    
        return
        
    def clear(self, service):  # @UnusedVariable
        return
        
    def reset(self):
        return
        
    
    


class SimpleCache(ServiceProviderCache):
    '''
        Simple cache that stores one provider per service 
    '''
    
    def __init__(self):
        self.map = {}

    def cache(self, support):
        self.map[support.service.sid] = support    
    
    def cache_exists_by_id(self, serviceid):  
        return serviceid in self.map
    
    def cache_exists(self, service): 
        return service.sid in self.map
    
        
    def get_by_id(self, serviceid):  
        return map[serviceid]

    def get(self, service): 
        return self.map.get(service.sid, None)
    
        
    def clear_by_id(self, serviceid):     
        del self.map[serviceid]
        
    def clear(self, service): 
        del self.map[service.sid]
        
        
    def reset(self):
        self.map = {}
        
        
