# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 16:22:36 2019

@author: guzy0
"""

steps = [{'pid_names': [u'\u8c37\u6b63\u9633'], 'name': u'init', 'actions': [{'nextsteps': ['handle'], 'type': 'default', 'title': u'\u63d0\u4ea4'}], 'title': u'\u63d0\u4ea4'}, {'pid_names': [u'\u8c37\u6b63\u9633'], 'name': u'handle', 'actions': [{'nextsteps': [u'check'], 'type': u'default', 'title': u'\u5b8c\u6210'}, {'nextsteps': [u'confirm'], 'type': u'error', 'title': u'\u4e0d\u662f\u6545\u969c'}, {'nextsteps': [u'haha'], 'type': u'default', 'title': u'\u5475\u5475'}], 'title': u'\u5904\u7406'}, {'pid_names': [u'\u8c37\u6b63\u9633'], 'name': u'check', 'actions': [{'nextsteps': [], 'type': u'default', 'title': u'\u901a\u8fc7'}, {'nextsteps': ['handle'], 'type': 'error', 'title': u'\u6253\u56de'}], 'title': u'\u68c0\u67e5'}, {'pid_names': [u'\u8c37\u6b63\u9633'], 'name': u'confirm', 'actions': [{'nextsteps': [u'init'], 'type': 'default', 'title': u'\u91cd\u65b0\u63d0\u4ea4'}, {'nextsteps': [], 'type': u'default', 'title': u'\u5e9f\u5f03'}], 'title': u'\u786e\u8ba4'}, {'pid_names': [u'\u8c37\u6b63\u9633'], 'name': u'haha', 'actions': [{'nextsteps': [], 'type': 'default', 'title': u'van'}], 'title': u'\u54c8\u54c8'}]
first_step_titles=[u'\u5904\u7406']
first_step_names={u'\u5904\u7406': 1}
first_fillcolor = '#FF8C00'
latter_fillcolor = '#A9A9A9'
def steps_list2dict(steps):
    steps_dict = dict()
    for step in steps:
        steps_dict[step['name']] = step
    return steps_dict

def steps_dump(step):
    steps_slice.append(step)
    for action in step['actions']:
        print(action)
        if not action:return
        elif action['type'] == 'error':return
        for nextstep in action['nextsteps']:
            #print(action['nextsteps'])
            #print(nextstep)
            if not nextstep:return
            if latter_fillcolor:
                steps_dict[nextstep]['fillcolor'] = latter_fillcolor
            steps_dump(steps_dict[nextstep])

def get_steps_slice(step):
    if step['title'] in first_step_titles:
        step['name'] = first_step_names[step['title']]
        if first_fillcolor:
            step['fillcolor'] = first_fillcolor
        steps_dump(step)
    else:
        for action in step['actions']:
            if not action:return
            if action['type'] == 'error':return
            for nextstep in action['nextsteps']:
                if not nextstep:return
                get_steps_slice(steps_dict[nextstep])
steps_dict = steps_list2dict(steps)
steps_slice = []
get_steps_slice(steps_dict['init'])
print(len(steps_slice))