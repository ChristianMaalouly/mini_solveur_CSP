from csp import *
import time


# Initialize the model for the n-queens problem
def reines(n):
    n += 1

    model = CSPModel()

    # Add variables
    for i in range(1, n):
        model.add_variable(f"x{i}", range(1, n))

    # Add constraints
    for i in range(1, n):
        for j in range(i + 1, n):
            model.add_constraint(
                i - 1,
                j - 1,
                [
                    (v1, v2)
                    for v1 in range(1, n)
                    for v2 in range(1, n)
                    if v1 != v2 and abs(v1 - v2) != abs(i - j)
                ],
            )
    return model


# Solve the n-queens problem
def solve_reines(n, fc=False, ac3=False, start_ac3=False):
    model = reines(n)

    # Use AC3 at the beginning
    if start_ac3:
        model.ac3()

    # Solve the problem with backtracking and options for forward checking and MAC with AC3
    model.backtrack({}, fc=fc, ac3=ac3)

    print(f"Solution for {n} queens")
    model.print_solution()
    return model


# Read the graph from a file adn return the edges, number of vertices and the maximum degree
def read_graph(file_path):
    edges = []
    degrees = {}
    with open(file_path, "r") as file:
        for line in file:
            if line.startswith("p"):
                _, _, v, _ = line.split()
                nb_vertices = int(v)
            if line.startswith("e"):
                _, node1, node2 = line.split()
                if (int(node2), int(node1)) not in edges:
                    edges.append((int(node1), int(node2)))
                    degrees[int(node1)] = degrees.get(int(node1), 1) + 1
                    degrees[int(node2)] = degrees.get(int(node2), 1) + 1
    max_degree = max(degrees.values())
    return edges, nb_vertices, max_degree


# Generate constraint of x diff y, takes the domains of the two variables and returns the constraint
def generate_diff_constraint(domain1, domain2):
    constraint = []
    constraint = [(v1, v2) for v1 in domain1 for v2 in domain2 if v1 != v2]
    return constraint


# Initialize the model for the graph coloring problem
def graph_coloring(file_path):
    model = CSPModel()
    edges, nb_vertices, ub = read_graph(file_path)

    # Add variables
    for i in range(1, nb_vertices + 1):
        model.add_variable(f"x{i}", range(1, ub + 1))

    # Add constraints
    for x1, x2 in edges:
        vals = generate_diff_constraint(range(1, ub + 1), range(1, ub + 1))
        model.add_constraint(x1 - 1, x2 - 1, vals)

    return model, ub


# Solve the graph coloring optimization problem through dichotomic
def solve_graph_coloring(file_path, fc=False, ac3=False, start_ac3=False):

    model, ub = graph_coloring(file_path)
    lb = 0
    mb = ub * 10 // 12

    # Dichotomic search
    while lb != ub:
        print(f"lb: {lb}, mb: {mb}, ub: {ub}")
        # Copy the original model that has all constraints and max domains and update based on the new value of mb
        new_model = CSPModel.copy(model)
        for var in new_model.variables:
            var.domain = [i for i in range(1, mb + 1)]
        new_model.update_constraints()

        # Use AC3 at the beginning
        if start_ac3:
            new_model.ac3()
        # Solve the problem with backtracking and options for forward checking and MAC with AC3
        new_model.backtrack({}, fc=fc, ac3=ac3)

        # If the solution is complete, update the upper bound and best solution, else update the lower bound
        if new_model.is_complete(new_model.solution):
            ub = mb
            mb = min((lb + ub) * 10 // 12, mb - 1)
            model.solution = new_model.solution
        else:
            lb = mb + 1
            mb = (lb + ub) * 10 // 12

    print(f"Solution for {file_path}")
    model.print_solution()
    print(f"Chromatic number: {ub}")
    return model, ub


def solve_graph_coloring_with_optimal_value(
    file_path, optimal, fc=False, ac3=False, start_ac3=False
):

    model, ub = graph_coloring(file_path)

    # Copy the original model that has all constraints and max domains and update based on the new value of optimal
    new_model = CSPModel.copy(model)
    for var in new_model.variables:
        var.domain = [i for i in range(1, optimal + 1)]
    new_model.update_constraints()

    # Use AC3 at the beginning
    if start_ac3:
        new_model.ac3()
    # Solve the problem with backtracking and options for forward checking and MAC with AC3
    new_model.backtrack({}, fc=fc, ac3=ac3)

    # If the solution is complete, update the upper bound and best solution, else update the lower bound
    if new_model.is_complete(new_model.solution):
        model.solution = new_model.solution
        model.counter = new_model.counter

    print(f"Solution for {file_path}")
    model.print_solution()
    print(f"Chromatic number: {optimal}")
    return model, ub


def main(choice, n, fc, ac3, start_ac3):

    if choice == 1:
        start_time = time.time()
        model = solve_reines(n, fc=fc, ac3=ac3, start_ac3=start_ac3)
        print(f"Time: {time.time() - start_time}")

    elif choice == 2:
        start_time = time.time()
        model, chromatic_number = solve_graph_coloring(
            "data/" + n + ".col", fc=fc, ac3=ac3, start_ac3=start_ac3
        )
        print(f"Time: {time.time() - start_time}")

    elif choice == 3:
        start_time = time.time()
        model, chromatic_number = solve_graph_coloring_with_optimal_value(
            "data/" + n + ".col", optimal, fc=fc, ac3=ac3, start_ac3=start_ac3
        )
        print(f"Time: {time.time() - start_time}")

        # model.print_model()


"""
graphs = ["myciel3", "myciel4", "myciel5", "myciel6", "myciel7"]
optimal_values = [4, 5, 6, 7, 8]

# for i in [j for j in range(76, 101) if j % 5 == 0]:
for j in [i for i in range(73) if i % 5 == 0]:
    # i = graphs[j]
    # optimal = optimal_values[j]
    start_time = time.time()
    # model = solve_graph_coloring_with_optimal_value(
    #    "data/" + i + ".col", optimal, fc=False, ac3=True, start_ac3=False
    # )
    model = solve_reines(j, fc=False, ac3=True, start_ac3=False)
    print(f"Time: {time.time() - start_time}")
"""

choice = int(
    input("1. Reines\n2. Graph coloring\n3. Graph coloring with optimal value\n")
)
if choice == 1:
    n = int(input("Enter the number of queens: "))
elif choice == 2:
    n = input("Enter the file name: ex: myciel3\n")
elif choice == 3:
    n = input("Enter the file name: ex: myciel3\n")
    optimal = int(input("Enter the optimal chromatic number: "))
fc = int(input("Forward checking? (y=1/n=0) "))
ac3 = int(input("MAC avecAC3? (y=1/n=0) "))
start_ac3 = int(input("Start with AC3? (y=1/n=0) "))

print(f"Choice: {choice}, n: {n}, fc: {fc}, ac3: {ac3}, start_ac3: {start_ac3}")
main(choice, n, fc, ac3, start_ac3)
