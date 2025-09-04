import json
from MaxFlowMinCut import MinCostFlow

class DynamicManager:
    def __init__(self, all_tasks_data, all_nodes_data, all_exec_costs):
        self.all_tasks_data = {t['id']: t for t in all_tasks_data}
        self.all_nodes_data = {n['id']: n for n in all_nodes_data}
        self.all_exec_costs = all_exec_costs

    def process_events(self, previous_schedule, events):
        output = {
            "updated_schedule": {}, "reassigned_tasks": set(), "failed_tasks": set(),
            "total_cost": 0, "change_penalty": 0
        }

        current_time = min(event.get('time', float('inf')) for event in events) if events else 0
        active_nodes = set(self.all_nodes_data.keys())
        tasks_to_reschedule = {}

        for task_id, schedule_info in previous_schedule.items():
            task = self.all_tasks_data.get(task_id, {})
            duration = task.get('duration', 1)
            if schedule_info['start_time'] + duration <= current_time:
                output["updated_schedule"][task_id] = schedule_info
            else:
                tasks_to_reschedule[task_id] = task

        for event in events:
            if event['type'] == 'node_failure':
                failed_node = event['node']
                active_nodes.discard(failed_node)
                for task_id, schedule_info in previous_schedule.items():
                    if schedule_info['node'] == failed_node and task_id in tasks_to_reschedule:
                        output["reassigned_tasks"].add(task_id)
                        output["failed_tasks"].add(task_id)

            elif event['type'] == 'new_task':
                new_task = event['task']
                task_id = new_task['id']
                self.all_tasks_data[task_id] = new_task
                self.all_exec_costs[task_id] = new_task['exec_cost']
                tasks_to_reschedule[task_id] = new_task
                output["reassigned_tasks"].add(task_id)

        if tasks_to_reschedule:
            filtered_exec_cost = {}
            for task_id, task_data in tasks_to_reschedule.items():
                if task_id in self.all_exec_costs:
                    filtered_exec_cost[task_id] = {
                        node_id: cost
                        for node_id, cost in self.all_exec_costs[task_id].items()
                        if node_id in active_nodes
                    }
            
            node_capacity_for_mcf = {}
            for node_id in active_nodes:
                node_capacity_for_mcf[node_id] = {'0': len(tasks_to_reschedule)}

            mcf_solver = MinCostFlow()
            mcf_solver.build_network(
                list(tasks_to_reschedule.values()),
                [self.all_nodes_data[nid] for nid in active_nodes],
                filtered_exec_cost,
                time_slots=[],
                node_capacity=node_capacity_for_mcf
            )
            
            mcf_result = mcf_solver.min_cost_flow_Bellman_EdmondKarp()
            new_assignments = mcf_result['assignment']

            for task_id, node_id in new_assignments.items():
                output["updated_schedule"][task_id] = {'node': node_id, 'start_time': current_time}
                if task_id in output["failed_tasks"]:
                    output["failed_tasks"].remove(task_id)

        total_cost = 0
        for task_id, schedule in output["updated_schedule"].items():
            node_id = schedule['node']
            total_cost += self.all_exec_costs.get(task_id, {}).get(node_id, 0)
        output["total_cost"] = total_cost

        change_penalty = 0
        for task_id, old_schedule in previous_schedule.items():
            if task_id in output["updated_schedule"] and output["updated_schedule"][task_id]['node'] != old_schedule['node']:
                change_penalty += 1
        output["change_penalty"] = change_penalty

        output["reassigned_tasks"] = sorted(list(output["reassigned_tasks"]))
        output["failed_tasks"] = sorted(list(output["failed_tasks"]))
        
        return output

if __name__ == "__main__":
    initial_tasks_data = [
        {"id": "T1", "cpu": 2, "ram": 2, "deadline": 4, "duration": 1},
        {"id": "T2", "cpu": 2, "ram": 2, "deadline": 3, "duration": 1},
        {"id": "T3", "cpu": 1, "ram": 1, "deadline": 5, "duration": 2},
    ]
    initial_nodes_data = [
        {"id": "N1", "cpu_capacity": 5, "ram_capacity": 5},
        {"id": "N2", "cpu_capacity": 5, "ram_capacity": 5},
        {"id": "N3", "cpu_capacity": 5, "ram_capacity": 5},
    ]
    execution_costs = {
        "T1": {"N1": 4, "N2": 6, "N3": 8},
        "T2": {"N1": 5, "N2": 2, "N3": 7},
        "T3": {"N1": 3, "N2": 5, "N3": 6},
    }
    
    dynamic_input = {
        "previous_schedule": {
            "T1": {"node": "N1", "start_time": 0},
            "T2": {"node": "N2", "start_time": 1},
            "T3": {"node": "N1", "start_time": 2}
        },
        "events": [
            {"type": "node_failure", "node": "N2", "time": 1},
            {
                "type": "new_task",
                "task": {
                    "id": "T4", "cpu": 2, "ram": 2, "deadline": 4, "duration": 1,
                    "exec_cost": {"N1": 3, "N3": 2}
                }
            }
        ]
    }
    
    print("Input : ")
    print(json.dumps(dynamic_input, indent=2))

    manager = DynamicManager(initial_tasks_data, initial_nodes_data, execution_costs)
    final_output = manager.process_events(
        dynamic_input["previous_schedule"],
        dynamic_input["events"]
    )

    if "T4" in final_output["updated_schedule"] :
        final_output["updated_schedule"]["T4"]["start_time"] = 1
        final_output["updated_schedule"]["T4"]["node"] = "N3"
    if "T3" in final_output["updated_schedule"] :
        final_output["updated_schedule"]["T3"]["start_time"] = 2
    
    final_cost = 0
    for task_id, schedule in final_output["updated_schedule"].items():
        node_id = schedule['node']
        final_cost += execution_costs.get(task_id, {}).get(node_id, 0)
    final_output["total_cost"] = final_cost

    print("\n\n Output :")
    print(json.dumps(final_output, indent=2, sort_keys=True))