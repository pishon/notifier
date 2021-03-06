'''
Created on 21 lut 2016

@author: luk
'''

from comparator.comparatorfactory import ComparatorFactory
from input.inputfactory import InputFactory
from notifier.notifierfactory import NotifierFactory
from state.statemanagerfactory import StateManagerFactory
from mutate.mutator_factory import MutatorFactory
import time, sys, json, logging

FORMAT = '%(asctime)-24s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger('ChangeObserver')

class ChangeObserver(object):
    '''
    Defines rule of observing changes. After receiving data and comparing with previous state notifies about change
    '''
    


    def __init__(self, params=None):
        '''
        Constructor
        '''
        self.dataReceiver = InputFactory().get(params)
        self.stateManager = StateManagerFactory().get(params)
        self.comparator = ComparatorFactory().get(params)
        self.mutator = MutatorFactory().get(params)
        self.notifier = NotifierFactory().get(params)         
        
    def notify_if_changed(self) :
        current_state = self.dataReceiver.receive()
        saved_state = self.stateManager.read()
        mutated_state = self.mutator.mutate(current_state)
        diff = self.comparator.compare(previous_state=saved_state, current_state=mutated_state)
        self.stateManager.save(current_state)
        if type(diff) is dict:
            logger.debug('diff is type of dict')
            if (diff['changed']):
                print('was changed!')
                self.notifier.notify(diff)
                return diff
            else:
                print('..no change')
        else:
            logger.debug('diff is object')
            if (diff.changed()):
                print('was changed!')
                self.notifier.notify(diff)
                return diff
            else:
                print('..no change')

            


if __name__ == '__main__' :
    
    if len(sys.argv) == 2 :
        config_file = sys.argv[1]
        print ('running with config from', config_file)        
        params = json.load(open(config_file, 'r'))
    else :    
        from config import config
        recipients = config.config()['mail']['default_recipients']
        params = {
            'input' : {
                'type' : 'url.content',
                "url" : "http://www.timeapi.org/utc/now?format=%25a%20%25b%20%25d%20%25I:%25M:%25S"
            },
            'stateManager' : {
                'type' : 'file',
                'filename' : '../output/aa.json'
            },
            'comparator' : {
                'type' : 'text'
            },
            'notifier' : {
                'type' : 'debug',
                'recipients' : recipients
            }                        
        }
    
#    params = json.load(open('config.json', 'r'))
    observer = ChangeObserver(params)
    observer.notify_if_changed()
        
