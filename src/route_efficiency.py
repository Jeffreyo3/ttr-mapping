def _evaluate_route_efficiency(all_distances, original_lines):
    total_efficiency = 0.0

    for route in original_lines:
        connection = frozenset({route.a, route.b})
        shortest_distance = all_distances[connection]
        total_efficiency += route.value / shortest_distance

    average_efficiency = total_efficiency / len(original_lines)

    routes_above_average = []
    routes_below_average = []

    for route in original_lines:
        connection = frozenset({route.a, route.b})
        shortest_distance = all_distances[connection]
        efficiency = route.value / shortest_distance

        a, b = connection
        if efficiency >= average_efficiency:
            routes_above_average.append((a, b, efficiency))
        else:
            routes_below_average.append((a, b, efficiency))

    return (average_efficiency, routes_above_average, routes_below_average)


def print_route_efficiency_report(all_distances, original_lines):
    average_efficiency, routes_above_average, routes_below_average = (
        _evaluate_route_efficiency(all_distances, original_lines)
    )

    print("\nRoutes above average efficiency:")
    for a, b, efficiency in routes_above_average:
        _print_efficiency(all_distances, a, b, efficiency)
    print("\nRoutes below average efficiency:")
    for a, b, efficiency in routes_below_average:
        _print_efficiency(all_distances, a, b, efficiency)
    print(f"\nAverage route efficiency: {average_efficiency:.4f}\n")


def _print_efficiency(all_distances, a, b, efficiency):
    distance = all_distances[frozenset({a, b})]
    print(
        f"█[{a.value} <-> {b.value}]"
        f"█ Efficiency: {efficiency:.4f} "
        f"█ Distance: {distance} █"
    )
