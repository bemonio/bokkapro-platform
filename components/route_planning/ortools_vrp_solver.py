import importlib.util
from dataclasses import dataclass

HAS_ORTOOLS = importlib.util.find_spec("ortools") is not None
if HAS_ORTOOLS:
    from ortools.constraint_solver import pywrapcp, routing_enums_pb2


@dataclass
class VehicleRoutePlan:
    vehicle_index: int
    task_indices: list[int]
    distance_m: int
    total_load: int


@dataclass
class VrpSolution:
    routes: list[VehicleRoutePlan]


def _solve_fallback(distance_matrix: list[list[int]], demands: list[int], vehicle_capacities: list[int]) -> VrpSolution:
    remaining = set(range(1, len(demands)))
    plans: list[VehicleRoutePlan] = []

    for vehicle_index, capacity in enumerate(vehicle_capacities):
        load = 0
        current_node = 0
        distance_m = 0
        route_task_nodes: list[int] = []

        while remaining:
            candidates = [node for node in remaining if load + demands[node] <= capacity]
            if not candidates:
                break
            next_node = min(candidates, key=lambda node: distance_matrix[current_node][node])
            distance_m += distance_matrix[current_node][next_node]
            route_task_nodes.append(next_node - 1)
            load += demands[next_node]
            current_node = next_node
            remaining.remove(next_node)

        if route_task_nodes:
            distance_m += distance_matrix[current_node][0]
            plans.append(
                VehicleRoutePlan(
                    vehicle_index=vehicle_index,
                    task_indices=route_task_nodes,
                    distance_m=distance_m,
                    total_load=load,
                )
            )

    if remaining:
        return VrpSolution(routes=[])

    return VrpSolution(routes=plans)


def solve_capacitated_vrp(
    distance_matrix: list[list[int]],
    demands: list[int],
    vehicle_capacities: list[int],
    time_limit_seconds: int = 5,
) -> VrpSolution:
    if not distance_matrix or not vehicle_capacities:
        return VrpSolution(routes=[])

    if not HAS_ORTOOLS:
        return _solve_fallback(distance_matrix=distance_matrix, demands=demands, vehicle_capacities=vehicle_capacities)

    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), len(vehicle_capacities), 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(from_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(demand_callback_index, 0, vehicle_capacities, True, "Capacity")

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search_parameters.time_limit.seconds = time_limit_seconds

    solution = routing.SolveWithParameters(search_parameters)
    if solution is None:
        return VrpSolution(routes=[])

    plans: list[VehicleRoutePlan] = []
    for vehicle_index in range(len(vehicle_capacities)):
        index = routing.Start(vehicle_index)
        task_indices: list[int] = []
        distance_m = 0
        total_load = 0

        while not routing.IsEnd(index):
            next_index = solution.Value(routing.NextVar(index))
            from_node = manager.IndexToNode(index)
            to_node = manager.IndexToNode(next_index)
            distance_m += distance_matrix[from_node][to_node]

            if to_node != 0:
                task_indices.append(to_node - 1)
                total_load += demands[to_node]

            index = next_index

        if task_indices:
            plans.append(VehicleRoutePlan(vehicle_index, task_indices, distance_m, total_load))

    return VrpSolution(routes=plans)


def solve_single_vehicle_route(
    distance_matrix: list[list[int]],
    demands: list[int],
    vehicle_capacity: int,
    time_limit_seconds: int = 5,
) -> VehicleRoutePlan | None:
    solution = solve_capacitated_vrp(distance_matrix, demands, [vehicle_capacity], time_limit_seconds)
    if not solution.routes:
        return None
    return solution.routes[0]
