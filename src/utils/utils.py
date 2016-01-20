'''
Created on Jan 15, 2016

@author: ggomarr
'''

import sys                                                                          
from beautifulhue.api import Bridge

username = 'huepymaster'
hueip='1.1.1.104'

col_verts=[[0.15,0.1],[0.2,0.55],[0.65,0.3]] # Blue, Green, Red

def weights_to_color(bands):
    if sum(bands)==0:
        bands=[1,1,1]
    bands=[ 1.0*b/sum(bands) for b in bands ]
    return [ col_verts[0][0]*bands[0]+col_verts[1][0]*bands[1]+col_verts[2][0]*bands[2],
             col_verts[0][1]*bands[0]+col_verts[1][1]*bands[1]+col_verts[2][1]*bands[2]]

def change_name(light_id, to_name):
    bridge = Bridge(device={'ip':hueip}, user={'name':username})
    resource = {
        'which':light_id,
        'data':{
            'attr':{'name':to_name}
        }
    }
    bridge.light.update(resource)
    
def toggle_light(light_id,new_state=None):
    bridge = Bridge(device={'ip':hueip}, user={'name':username})
    if new_state==None:
        light_state=bridge.light.get({'which':light_id})
        new_state=not light_state['resource']['state']['on']
    resource = {
        'which':light_id,
        'data':{
            'state':{'on':new_state}
        }
    }
    bridge.light.update(resource)
    
def change_color(light_id, xy=[0.7,0.25], brightness=254):
    bridge = Bridge(device={'ip':hueip}, user={'name':username})
    resource = {
        'which':light_id,
        'data':{
            'state':{'xy':xy, 'bri':brightness}
        }
    }
    bridge.light.update(resource)
    
def createConfig(bridge,username):                                                                 
    created = False                                                                 
    print 'Press the button on the Hue bridge'                                      
    while not created:                                                              
        resource = {'user':{'devicetype': username, 'name': username}}    
        response = bridge.config.create(resource)['resource']                       
        if 'error' in response[0]:                                                  
            if response[0]['error']['type'] != 101:                                 
                print 'Unhandled error creating configuration on the Hue'           
                sys.exit(response)                                                  
        else:                                                                       
            created = True                                                          

def getSystemData(bridge):                                                                    
    resource = {'which':'system'}                                                     
    return bridge.config.get(resource)['resource']                                    

def createUser(ip=hueip,usr=username):
    bridge = Bridge(device={'ip':ip}, user={'name':username})
    response = getSystemData(bridge) 
    if 'lights' in response:                                                          
        print 'Connected to the Hub'                                                  
        print response['lights']                                                      
    elif 'error' in response[0]:                                                      
        error = response[0]['error']                                                  
        if error['type'] == 1:                                                        
            createConfig(bridge,usr)                                                            
            createUser()  
            
if __name__ == "__main__":
#    createUser(hueip,username)
    toggle_light(3)