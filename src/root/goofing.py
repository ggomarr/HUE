'''
Created on Jan 15, 2016

@author: ggomarr
'''

def change_name(light_id, to_name):
    from beautifulhue.api import Bridge
    bridge = Bridge(device={'ip':'1.1.1.104'}, user={'name':'huepymaster'})
    resource = {
        'which':light_id,
        'data':{
            'attr':{'name':to_name}
        }
    }
    bridge.light.update(resource)
    
def toggle_light(light_id):
    from beautifulhue.api import Bridge
    bridge = Bridge(device={'ip':'1.1.1.104'}, user={'name':'huepymaster'})
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
    from beautifulhue.api import Bridge
    bridge = Bridge(device={'ip':'1.1.1.104'}, user={'name':'huepymaster'})
    resource = {
        'which':light_id,
        'data':{
            'state':{'xy':xy, 'bri':brightness}
        }
    }
    bridge.light.update(resource)
    