import heapq

class MinCostFlow:
    def __init__(self):
        self.graph = {}
        self.INF = 10**9
        self.task = {}
        self.node = {}

    def add_new_task(self, id,ram,cpu,deadline):
        if id not in self.graph:
            self.graph[id] = {}
        self.task[id]={'ram':ram,'cpu':cpu,'deadline':deadline}

    def add_new_node(self, id, ram , cpu):
        if id not in self.graph:
            self.graph[id] = {}
        self.node[id]={'ram':ram,'cpu':cpu}

    def add_edge(self, u, v, cap, cost):
        self.graph[u][v] = [cap, cost]
        self.graph[v][u] = [0, -cost]

    def build_network(self, tasks, nodes, exec_cost):
        self.graph['S'] = {}
        self.graph['T'] = {}

        # source -> tasks
        for t in tasks:
            self.add_new_task(t["id"], t["ram"], t["cpu"], t["deadline"])
            self.add_edge('S', t["id"], 1, 0)

        # nodes -> sink
        for n in nodes:
            self.add_new_node(n["id"], n["ram_capacity"], n["cpu_capacity"])
            self.add_edge(n["id"], 'T', self.INF, 0)

        # tasks -> nodes with cost
        for t in tasks:
            tid = t["id"]
            for nid, c in exec_cost[tid].items():
                if self.task[tid]['ram'] <= self.node[nid]['ram'] and self.task[tid]['cpu'] <= self.node[nid]['cpu']:
                    self.add_edge(tid, nid, 1, c)

    def min_cost_flow(self, max_flow):
        n = len(self.graph)
        h = dict()
        for v in self.graph:
            h[v] = 0
        dist = {}
        prevv = {}
        flow = 0
        cost = 0
        assignments = {}

        while flow < max_flow:
            dist = {}
            for v in self.graph:
                dist[v] = self.INF

            dist['S'] = 0
            prevv = {}

            pq = [(0, 'S')]
            while pq:
                d, v = heapq.heappop(pq)
                if dist[v] < d:
                    continue
                for u, (cap, w) in self.graph[v].items():
                    if cap > 0 and dist[u] > dist[v] + w + h[v] - h[u]:
                        if (v not in ('S','T') and u not in ('S','T') and v in self.task.keys() and u in self.node.keys()):
                            if self.task[v]['ram'] <= self.node[u]['ram'] and self.task[v]['cpu'] <= self.node[u]['cpu']:
                                dist[u] = dist[v] + w + h[v] - h[u]
                                prevv[u] = v
                                heapq.heappush(pq, (dist[u], u))
                        else:
                            dist[u] = dist[v] + w + h[v] - h[u]
                            prevv[u] = v
                            heapq.heappush(pq, (dist[u], u))

            if 'T' not in prevv:
                break

            for v in self.graph:
                if dist[v] < self.INF:
                    h[v] += dist[v]

            d = 1

            v = 'T'
            while v != 'S':
                u = prevv[v]
                self.graph[u][v][0] -= d
                self.graph[v][u][0] += d
                v = u

            flow += d
            cost += d * h['T']

            path = []
            v = 'T'
            while v != 'S':
                path.append(v)
                v = prevv[v]
            path.append('S')
            path.reverse()

            #I'm not sure about this part
            self.node[path[2]]['ram'] -= self.task[path[1]]['ram']
            self.node[path[2]]['cpu'] -= self.task[path[1]]['cpu']

            assignments[path[1]] = path[2]

        assignments = {k: assignments[k] for k in sorted(assignments.keys())}

        return {"total_cost": cost, "assignments": assignments}
    
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
  }
}



mcf = MinCostFlow()
mcf.build_network(dict_data["tasks"], dict_data["nodes"], dict_data["exec_cost"])
result = mcf.min_cost_flow(5)
print(result)
