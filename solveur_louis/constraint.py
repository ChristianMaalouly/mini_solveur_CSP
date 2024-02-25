from variable import Variable


class Constraint:
    def __init__(self, x: Variable, y: Variable, solution: list):
        self.variables = (x, y)
        self.solution = solution

    def add_solution(self, solution: list):
        for sol in solution:
            self.solution.append(sol)
