# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 13:15:15 2019

@author: guzy0
"""

import cgi

def get_related_step(task):
    related_step = task.relatedStep
    if step_with_children and related_step is step_with_children:
        for child_step in child_steps:
            if task.title == child_step.title:
                return child_step
    return related_step

def set_potential_step_names(step):
    if step is None: return

    for action in step.values():
        if action.type == 'error': continue
        for next_step_name in action.nextsteps:
            if next_step_name in potential_step_names: continue
            if not next_step_name: continue

            potential_step_names.append(next_step_name)
            next_step = step_container.get(next_step_name)
            if next_step is None:
                next_step = child_step_container.get(next_step_name)
            if next_step is None:
                raise Exception(u"无法根据下一步骤的名字找到步骤对象: %s" % next_step_name)
            set_potential_step_names(next_step)


def gen_child_steps(step_names, parent_step, next_step_name):
    """ 根据子步骤的名字列表, 父步骤对象，父步骤下一步骤的名字生成子步骤对象 """
    child_steps_list = []
    child_steps_dict = {}
    # 子步骤的actions 与父步骤相同
    actions = parent_step.values()
    parent_step_name = parent_step.name
    for n, step in enumerate(step_names[:-1]):
        child_step = ChildStep(step, step, actions,
            parent_step_name, step_names[n+1])
        child_steps_list.append(child_step)
        child_steps_dict[step] = child_step

    child_step = ChildStep(step_names[-1], step_names[-1], actions,
        parent_step_name, real_next_step=next_step_name)
    child_steps_list.append(child_step)
    child_steps_dict[step_names[-1]] = child_step

    return child_steps_list, child_steps_dict

def get_child_step_names(datamanager):
    # 在流程设置里面定义的步骤表,假定步骤表的设置名必须为'steps'
    steps_table = datamanager.md.get('steps', [])\
            or datamanager.mdset.get('zopen.review_relations:review_steps', {}).get('steps', [])
    return [step['title'] for step in steps_table]

def get_parent_of_custom_steps(steps, step_names):
    """ 得到有自定义子步骤的那个大步骤 """
    index = step_names.index('review')
    parent_step = steps[index]
    return index, parent_step

def get_next_step_name(steps, index):
    """ get the name of next step after index """
    try:
        return steps[index + 1].name
    except IndexError:
        return ''

def get_child_steps_info(datamanager, steps):
    """得到自定义的子步骤"""
    step_with_children = None
    child_steps_list = []
    child_steps_dict = {}
    child_step_names = get_child_step_names(datamanager)
    step_names = [s.name for s in steps]
    # 这里假定有自定义子步骤的步骤名字必须为'review'
    if child_step_names and 'review' in step_names:
        index, step_with_children = get_parent_of_custom_steps(steps,
                step_names)
        next_step_name = get_next_step_name(steps, index)
        child_steps_list, child_steps_dict = gen_child_steps(
                child_step_names, step_with_children, next_step_name)
        steps[index:index+1] = child_steps_list
    return step_with_children, child_steps_list, child_steps_dict, steps

def draw_box(name, label, color):
    label = cgi.escape(label)
    graph.node(name, label=label, style='filled', fillcolor=color)

end_box_drawed = False
def draw_arrow(start, end, label):
    if end == 'x__end_flow_node' and not end_box_drawed:
        # 结束节点
        draw_box('x__end_flow_node', t_('end', '结束'), '#3EFFC1')

    label = cgi.escape(label)
    graph.edge(start, end, label, style='solid')

def translate_task_finish_action(task):
    step = task.relatedStep
    finish_action = task.finish_action
    if step is None:
        return finish_action
    # 采用步骤翻译
    if finish_action == step.title:
        return step.i18n.get_text('title') or finish_action
    # 采用操作翻译
    for action in step.values():
        if finish_action == action.title:
            return action.i18n.get_text('title') or finish_action
    return finish_action

t_ = root.packages['zopen.datacontainer'].i18n.get_translator(request)
dataitem = context
datamanager = dataitem.parent
step_container = dataitem.workitems.values()[0].related_workflow
steps = step_container.values()

# 得到已完成的任务和当前任务
ftm = dataitem.workitems
# listCurrentTasks 是列出已经执行过的任务或当前的任务
completed_tasks = ftm.query(state='flowtask.finished')
current_tasks = ftm.query(state=set(['flowtask.active', 'flowtask.working', 'flowtask.pending']))

step_with_children, child_steps, child_step_container, steps = get_child_steps_info(datamanager, steps)

# 当前的步骤
current_steps = [get_related_step(task) for task in current_tasks]
# 未来有可能执行的步骤
potential_step_names = []
for step in current_steps:
    set_potential_step_names(step)

# 已经画出来的步骤
drawed_steps = []
# 图片生成器
graph = ui.graph()

# 开始节点
draw_box('x__start_flow_node', t_('start', '开始'), '#3EFFC1')

if completed_tasks:
    init = get_related_step(completed_tasks[0]).name
    draw_arrow('x__start_flow_node', init, t_('start_up', '启动'))

# 处理已完成的步骤 TODO 现在只能线性排，不能显示并行流程
for n, task in enumerate(completed_tasks):
    related_step = get_related_step(task)
    try:
        next_task = completed_tasks[n + 1]
        next_steps = [get_related_step(next_task)]
    except IndexError:
        next_steps = current_steps

    # 如果两个task属于同一个step，跳到后一个task
    if related_step in next_steps: continue
    if related_step is None: continue

    # 画方框
    pid_names = [org_info.getPrincipalInfo(pid)['title'] for pid in task.responsibles]
    draw_box(related_step.name, '%s (%s)' % (
        related_step.i18n.get_text('title') or related_step.title, ','.join(pid_names)), '#ADFF2F'
    )
    # 画连接线
    for next_step in next_steps:
        next_step_name = next_step.name if next_step is not None else 'x__end_flow_node'
        draw_arrow(related_step.name, next_step_name, translate_task_finish_action(task))
        if next_step_name == 'x__end_flow_node':
            end_box_drawed = True
        drawed_steps.append(related_step)

# 处理后续步骤的情况
count = 0
for step in steps:
    if step is None: continue

    fillcolor = '#A9A9A9'

    # 如果是当前进行的步骤，颜色改为绿色
    if step in current_steps:
        fillcolor = '#FF8C00'
    # 如果是已经完成的步骤，跳过
    elif step in drawed_steps:
        continue
    # 如果不是当前步骤，而且未来也不会执行该步骤，也跳过
    elif step.name not in potential_step_names:
        continue  #xxx

    pids = step.get_graph_responsibles(request=request, context=dataitem, container=datamanager)
    pid_names = [org_info.getPrincipalInfo(pid)['title'] for pid in pids]
    draw_box(step.name, '%s (%s)' % (step.i18n.get_text('title') or step.title, ','.join(pid_names)), fillcolor)

    for action in step.values():
        # 不显示异常的流程操作
        if action.type == 'error': continue
        count = count + 1
        # 没有Nextstep，都是结束节点
        if not action.nextsteps:
            draw_arrow(step.name, 'x__end_flow_node',
                str(count) + '.' + (action.i18n.get_text('title') or action.title))
            end_box_drawed = True
            continue
        for next_step in action.nextsteps:
            if next_step == 'review' and child_steps:
                next_step = child_steps[0].name
            draw_arrow(step.name, next_step,
                str(count) + '.' + (action.i18n.get_text('title') or action.title))
    count = 0

request.response.setHeader('Content-Type','image/svg+xml')
return graph.dot2graph(graph.get_dot())