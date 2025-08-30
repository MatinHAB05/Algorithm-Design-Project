from MaxFlowMinCut import result as result_maxFlow
from MaxFlowMinCut import mcf as graph
assignment = result_maxFlow["assignment"]
# print(assignment )

def CreateDependencies_Graph(dependencies,duration) :
    dp_graph= {}
    task_node_sch = {}
    for t in graph.task.keys() :
        dp_graph[t] = {'parent':[] , 'child' : []} #parent (parents,start,end,duration,deadline)  
        task_node_sch[t] ={'start':-97,'end':-97,'duration' : duration[t] ,'deadline':  graph.task[t]['deadline'] ,'flag' : 0}
    for dep in dependencies :
        dp_graph[dep['after']]['parent'].append(dep['before'])
        dp_graph[dep['before']]['child'].append(dep['after'])

    return dp_graph , task_node_sch

def SchedulePerNode() : 
    Schedule_Nodes = {}
    for x in graph.node.keys() :
        Schedule_Nodes[x] = []
    for  task, node in assignment.items() : 
        Schedule_Nodes[node].append(task)
    # print(Schedule_Nodes)
    for node in Schedule_Nodes.keys() :
        #Sort Deadline and Topological
        nodeTaskList = TopologicalPerNode_Deadline(Schedule_Nodes,node)
        # print(nodeTaskList)
        Schedule_Nodes[node]=nodeTaskList
    return Schedule_Nodes
        

def TopologicalPerNode_Deadline(Schedule_Nodes,node) : 
    Specfic_TopoGrap = {}
    Specfic_TopoGrap_temp = {}

    for task in Schedule_Nodes[node] :
        Specfic_TopoGrap[task] = {'parent' : [] , 'child' : [] }
        Specfic_TopoGrap_temp[task] = { 'child' : [] }

        for child_task in dependencies_graph[task]['child'] : 
            if child_task in Schedule_Nodes[node] :
                Specfic_TopoGrap[task]['child'].append(child_task)
                Specfic_TopoGrap_temp[task]['child'].append(child_task)


        for parent_task in dependencies_graph[task]['parent'] : 
            if parent_task in Schedule_Nodes[node] :
                Specfic_TopoGrap[task]['parent'].append(parent_task)
    
    Topological_Sort_list = []
    # print("####",Specfic_TopoGrap_temp)
    while(Specfic_TopoGrap_temp) : 
        vertex=find_ZerooutDegree_withMaxDeadline(node,Specfic_TopoGrap_temp)
        # print("****",vertex)
        del Specfic_TopoGrap_temp[vertex[0]]
        for parent in Specfic_TopoGrap_temp.keys() :
            if vertex[0] in  Specfic_TopoGrap_temp[parent]['child'] :
                 Specfic_TopoGrap_temp[parent]['child'].remove(vertex[0])
        
        Topological_Sort_list.append(vertex)


    Topological_Sort_list.reverse()
    return Topological_Sort_list


def find_ZerooutDegree_withMaxDeadline(node , Specfic_TopoGrap_temp) : 
    ZeroList = []
    
    for parent , childlist in Specfic_TopoGrap_temp.items() :
        if len(childlist['child'])==0 :
            ZeroList.append((parent,task_node_sch_list[parent]['deadline']))

    return max(ZeroList,key=lambda t :t[1] )


input_dict = {
"dependencies": [
    {
    "before": "T1",
    "after": "T3"
    },
    {
    "before": "T1",
    "after": "T5"
    },
    {
    "before": "T2",
    "after": "T3"
    }
],

"task_duration": {
    "T1": 1,
    "T2": 1,
    "T3": 2 , 
    "T4": 3 , 
    "T5": 3
 }
}

dependencies_graph , task_node_sch_list = CreateDependencies_Graph(input_dict["dependencies"],input_dict["task_duration"])
# print(dependencies_graph)
Schedule_Nodes = SchedulePerNode()
print(Schedule_Nodes)