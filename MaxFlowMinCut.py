import heapq
from collections import deque

class MinCostFlow:
    def __init__(self):
        self.graph = {}
        self.graph_residual = {}
        self.INF = 10**9
        self.task = {}
        self.node = {} # node == computational node

    def add_new_task(self, id, ram, cpu, deadline):
        if id not in self.graph:
            self.graph[id] = {}
            self.graph_residual[id] = {}
        self.task[id] = {'ram': ram, 'cpu': cpu, 'deadline': deadline}
        
    def add_new_node(self, id, ram, cpu):
        if id not in self.graph:
            self.graph[id] = {}
            self.graph_residual[id] = {}
        self.node[id] = {'ram_cap' : ram , 'cpu_cap' : cpu , 'ram': 0, 'cpu' : 0}

    def add_edge(self, u, v, cap, cost):
        # Add to original graph
        if u not in self.graph:
            self.graph[u] = {}
        self.graph[u][v] = [0,cap, cost]
        
        # Add to residual graph (forward edge)
        if u not in self.graph_residual:
            self.graph_residual[u] = {}
        self.graph_residual[u][v] = [cap, cost]  # [flow, cost]
        
        # Add reverse edge to residual graph
        if v not in self.graph_residual:
            self.graph_residual[v] = {}
        self.graph_residual[v][u] = [0, -cost]  # reverse edge has negative cost

    def build_network(self, tasks, nodes, exec_cost,time_slots,node_capacity):
        self.graph['S'] = {}
        self.graph['T'] = {}
        self.graph_residual['S'] = {}
        self.graph_residual['T'] = {}
        tempDictNodeCap = {}
        for key in node_capacity.keys() : 
            tempDictNodeCap[key]=0
            for time_sl,cap in node_capacity[key].items() : 
                tempDictNodeCap[key]+=int(cap)
        # print(tempDictNodeCap)

        # source -> tasks
        for t in tasks:
            self.add_new_task(t["id"], t["ram"], t["cpu"], t["deadline"])
            self.add_edge('S', t["id"], 1, 0)

        # nodes -> sink
        for n in nodes:
            self.add_new_node(n["id"], n["ram_capacity"], n["cpu_capacity"])
            # phase 1 : self.add_edge(n["id"], 'T', self.INF, 0)
            # phase 2 : 
            self.add_edge(n["id"], 'T',tempDictNodeCap[n["id"]],  0)


        # tasks -> nodes with cost
        for t in tasks:
            tid = t["id"]
            for nid, c in exec_cost[tid].items():
                if self.task[tid]['ram'] <= self.node[nid]['ram_cap'] and self.task[tid]['cpu'] <= self.node[nid]['cpu_cap']:
                    self.add_edge(tid, nid, 1, c)

    def Is_Valid_Ram_and_Cpu_NodeCapcity(self,u,v):

        if u =='S' or u=='T' or v=='S' or v=='T' :
            return True
        if u in self.node.keys() and v in self.task.keys(): # v->u
            if self.task[v]['cpu'] + self.node[u]['cpu'] > self.node[u]['cpu_cap'] or self.task[v]['ram'] + self.node[u]['ram'] > self.node[u]['ram_cap'] : 
                return False
        elif u in self.task.keys() and v in self.node.keys(): # u->v
            if self.task[u]['cpu'] + self.node[v]['cpu'] > self.node[v]['cpu_cap'] or self.task[u]['ram'] + self.node[v]['ram'] > self.node[v]['ram_cap'] : 
                return False
        return True



    def BellmanFord_residual(self, source, sink):
        # Initialize distances and predecessors
        dist = {node: self.INF for node in self.graph_residual}
        dist[source] = 0
        parent = {node: None for node in self.graph_residual}
        # print(self.graph_residual)
        # Relax edges repeatedly
        for _ in range(len(self.graph_residual) - 1):
            updated = False
            for u in self.graph_residual:
                if dist[u] == self.INF:
                    continue
                for v, edge in self.graph_residual[u].items():
                    flow, cost = edge
                    # Check if there's residual capacity
                    # print(u,",",v)
                    if flow > 0 and dist[u] + cost < dist[v] and self.Is_Valid_Ram_and_Cpu_NodeCapcity(u,v):
                        dist[v] = dist[u] + cost
                        parent[v] = (u, cost)
                        updated = True
            if not updated:
                break
        
        # Check if sink is reachable
        if dist[sink] == self.INF:
            return None, None, None
        
        # Reconstruct the path and find minimum residual capacity
        path = []
        min_cap_bottenleck = self.INF
        current = sink
        
        while current != source:
            if parent[current] is None:
                return None, None, None
            u, cost = parent[current]
            flow, _ = self.graph_residual[u][current]
            min_cap_bottenleck = min(min_cap_bottenleck, flow)
            path.append((u, current, cost))
            current = u
        
        path.reverse()
        return path, min_cap_bottenleck, dist[sink]

    def min_cost_flow_Bellman_EdmondKarp(self):
        total_flow = 0
        total_cost = 0

        path, min_cap, path_cost = None , None , None

        while True:
            # Find shortest path using Bellman-Ford on residual graph
            path, min_cap, path_cost = self.BellmanFord_residual('S', 'T')
            
            if path is None:
                break  # No augmenting path found
            
            for u, v, cost in path:
                # Update forward edge flow
                
                if u in self.graph and v in self.graph[u] : # u->v
                    self.graph[u][v][0]+=min_cap
                    self.graph_residual[u][v][0] -= min_cap
                    self.graph_residual[v][u][0] += min_cap
                else : # no u->v
                    self.graph_residual[u][v][0] -= min_cap
                    self.graph_residual[v][u][0] += min_cap
                    self.graph[v][u][0] -= min_cap
                if u =='S' or u=='T' or v=='S' or v=='T' :
                    continue
                else :
                    if u in self.node.keys() and v in self.task.keys(): # node->task
                        self.node[u]['ram']-=self.task[v]['ram']
                        self.node[u]['cpu']-=self.task[v]['cpu']
                    elif u in self.task.keys() and v in self.node.keys(): # task->node
                        self.node[v]['ram']+=self.task[u]['ram']
                        self.node[v]['cpu']+=self.task[u]['cpu']


            

        # Build assignment result
        assignment = {}
        for vertex , [flow , cap , cost] in self.graph['S'].items() : 
            if flow==1 :
                total_flow+=1
        
        for task in self.task.keys():
            node_task = self.graph[task]
            for child_nodeTask,[flow,cap,cost]  in node_task.items(): 
                if flow==1 :
                    assignment[task]=child_nodeTask
                    total_cost+=cost

        return {
            'total_cost': total_cost,
            'total_flow': total_flow,
            'assignment': assignment
        }

# Test data

dict_data = {
  "tasks": [
    {"id": "T1", "cpu": 2, "ram": 3,"deadline":2},
    {"id": "T2", "cpu": 1, "ram": 2,"deadline":2},
    {"id": "T3", "cpu": 6, "ram": 9,"deadline":2},
    {"id": "T4", "cpu": 2, "ram": 1,"deadline":2},
    {"id": "T5", "cpu": 1, "ram": 1,"deadline":2}
  ],
  "nodes": [
    {"id": "N1", "cpu_capacity": 6, "ram_capacity": 8},
    {"id": "N2", "cpu_capacity": 10, "ram_capacity": 12},
    {"id": "N3", "cpu_capacity": 5, "ram_capacity": 6}
  ],
  "exec_cost": {
    "T1": {"N1": 5, "N2": 8, "N3": 6},
    "T2": {"N1": 3, "N2": 2, "N3": 4},
    "T3": {"N1": 7, "N2": 9, "N3": 5},
    "T4": {"N1": 4, "N2": 3, "N3": 6},
    "T5": {"N1": 3, "N2": 7, "N3": 3}
  },
  "time_slots": [
    0,
    1,
    2,
    3
  ],
"node_capacity_per_time": {
    "N1": {
    "0": 1,
    "1": 0,
    "2": 0,
    "3": 0
    },
    "N2": {
    "0": 3,
    "1": 3,
    "2": 2,
    "3": 2
    } , 
    "N3": {
    "0": 3,
    "1": 3,
    "2": 2,
    "3": 2
    }
 }
}

# if __name__ == "__main__" :
mcf = MinCostFlow()
mcf.build_network(dict_data["tasks"], dict_data["nodes"], dict_data["exec_cost"],dict_data["time_slots"],dict_data["node_capacity_per_time"])
result = mcf.min_cost_flow_Bellman_EdmondKarp()
print(f"Total cost: {result['total_cost']}")
print(f"Total flow: {result['total_flow']}")
print("Assignments:")
for task, node in result['assignment'].items():
    print(f"  {task} -> {node}")