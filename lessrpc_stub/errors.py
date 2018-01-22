'''
Created on Jan 2, 2018

@author: Salim
'''
class NoProviderAvailableException(Exception):
    
    def __init__(self, service):
        # Call the base class constructor with the parameters it needs
        super(NoProviderAvailableException, self).__init__("Tried to fetch a provider info from NameServer but NameServer did not return any for service: "
                + service)