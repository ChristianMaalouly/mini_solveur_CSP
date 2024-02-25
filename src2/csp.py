import copy


class Variable:
    def __init__(self, name, domain):
        self.name = name
        self.domain = [i for i in domain]


class Constraint:
    def __init__(self, var1, var2, possible_values):
        self.var1 = var1
        self.var2 = var2
        self.possible_values = [(i, j) for i, j in possible_values]


class CSPModel:
    def __init__(self):
        self.variables = []  # List of Variable objects
        self.constraints = []  # List of constraints (represented as functions or data)
        self.solution = {}  # Dictionary of variable assignments

    @classmethod
    def copy(cls, model):
        new_model = cls()
        new_model.variables = copy.deepcopy(model.variables)
        new_model.constraints = copy.deepcopy(model.constraints)
        new_model.solution = {}
        return new_model

    def add_variable_object(self, variable):
        self.variables.append(variable)

    def add_constraint_object(self, constraint):
        self.constraints.append(constraint)

    def add_variable(self, name, domain):
        variable = Variable(name, domain)
        self.variables.append(variable)

    def add_constraint(self, var1, var2, possible_values):
        constraint = Constraint(var1, var2, possible_values)
        self.constraints.append(constraint)

    def update_constraints(self):
        for constraint in self.constraints:
            constraint.possible_values = [
                (i, j)
                for i, j in constraint.possible_values
                if i in self.variables[constraint.var1].domain
                and j in self.variables[constraint.var2].domain
            ]

    def print_model(self):
        print("Variables:")
        for variable in self.variables:
            print(f"{variable.name}: {variable.domain}")
        print()

        print("\nConstraints:")
        for constraint in self.constraints:
            print(
                f"{self.variables[constraint.var1].name} - {self.variables[constraint.var2].name}: {constraint.possible_values}"
            )
        print()

    def print_variables(self):
        for variable in self.variables:
            print(f"{variable.name}: {variable.domain}")
        print()

    def print_constraints(self):
        for constraint in self.constraints:
            print(
                f"{self.variables[constraint.var1].name} - {self.variables[constraint.var2].name}: {constraint.possible_values}"
            )
        print()

    def print_solution(self):
        self.solution = dict(sorted(self.solution.items()))
        print(self.solution)
        # for k, v in self.solution.items():
        #    print(f"{self.variables[k].name}: {v}")
        print()

    def backtrack(self, i, fc=False, ac3=False):
        self.add_single_domain_values(i)

        if self.violates_constraint(i):
            return False

        if self.is_complete(i):
            self.solution = i
            print("Solution found")
            return True

        x = self.choose_unassigned_variable(i)
        for v in self.variables[x].domain:
            i_prime = self.instantiate(i, x, v)
            if ac3:
                print("AC3")
                original_domains = {var: var.domain[:] for var in self.variables}
                self.variables[x].domain = [v]
                if self.ac3():
                    if fc:
                        if self.forward_checking(i_prime, x, v, ac3=True):
                            return True
                        else:
                            for var in self.variables:
                                var.domain = original_domains[var]
                    else:
                        if self.backtrack(i_prime, ac3=True):
                            return True
                        else:
                            for var in self.variables:
                                var.domain = original_domains[var]
                else:
                    for var in self.variables:
                        var.domain = original_domains[var]

            elif fc:
                original_domains = {var: var.domain[:] for var in self.variables}
                self.variables[x].domain = [v]
                if self.forward_checking(i_prime, x, v):
                    return True
                else:
                    for var in self.variables:
                        var.domain = original_domains[var]
            else:
                if self.backtrack(i_prime):
                    return True

        return False

    def add_single_domain_values(self, i):
        for j, variable in enumerate(self.variables):
            if j not in i:
                if len(variable.domain) == 1:
                    i[j] = variable.domain[0]

    def violates_constraint(self, i):
        for constraint in self.constraints:
            if constraint.var1 in i and constraint.var2 in i:
                val1 = i[constraint.var1]
                val2 = i[constraint.var2]
                if (val1, val2) not in constraint.possible_values:
                    return True
        return False

    def is_complete(self, i):
        return len(i) == len(self.variables)

    def choose_unassigned_variable(self, i):

        # Choose the variable with the smallest domain
        unassigned_variables = [j for j in range(len(self.variables)) if j not in i]
        return min(unassigned_variables, key=lambda x: len(self.variables[x].domain))

        # Choose the first unassigned variable
        for j, variable in enumerate(self.variables):
            if j not in i:
                return j

    def instantiate(self, i, x, v):
        i_prime = i.copy()
        i_prime[x] = v
        return i_prime

    def ac3(self):
        to_test = [i for i in range(len(self.constraints))]

        while to_test:
            constraint = self.constraints[to_test.pop(0)]
            x = constraint.var1
            y = constraint.var2
            if self.reviseX(constraint):
                if not self.variables[x].domain:
                    # print("Inconsistency detected")
                    return False  # Inconsistency detected

                for i in range(len(self.constraints)):
                    if i not in to_test:
                        const = self.constraints[i]
                        if const.var1 == x and const.var2 != y:
                            to_test.append(i)
                        elif const.var2 == x and const.var1 != y:
                            to_test.append(i)

            if self.reviseY(constraint):
                if not self.variables[y].domain:
                    # print("Inconsistency detected")
                    return False  # Inconsistency detected

                for i in range(len(self.constraints)):
                    if i not in to_test:
                        const = self.constraints[i]
                        if const.var1 == y and const.var2 != x:
                            to_test.append(i)
                        elif const.var2 == y and const.var1 != x:
                            to_test.append(i)

        return True  # CSP is arc-consistent

    def reviseX(self, constraint):
        revised = False
        x = constraint.var1
        y = constraint.var2
        for vx in self.variables[x].domain[:]:  # Make a copy for iteration
            satisfied = False
            for vy in self.variables[y].domain[:]:
                if (vx, vy) in constraint.possible_values:
                    satisfied = True
                    break
            if not satisfied:
                self.variables[x].domain.remove(vx)
                revised = True

        return revised

    def reviseY(self, constraint):
        revised = False
        x = constraint.var1
        y = constraint.var2
        for vy in self.variables[y].domain[:]:  # Make a copy for iteration
            satisfied = False
            for vx in self.variables[x].domain[:]:
                if (vx, vy) in constraint.possible_values:
                    satisfied = True
                    break
            if not satisfied:
                self.variables[y].domain.remove(vy)
                revised = True

        return revised

    def forward_checking(self, i, x, vx, ac3=False):

        # Save a copy of the original domains

        for constraint in self.constraints:
            if constraint.var1 == x:
                for y in range(len(self.variables)):
                    if constraint.var2 == y:
                        for vy in self.variables[y].domain[:]:
                            if (vx, vy) not in constraint.possible_values:
                                self.variables[y].domain.remove(vy)
                                if not self.variables[y].domain:
                                    return False
            elif constraint.var2 == x:
                for y in range(len(self.variables)):
                    if constraint.var1 == y:
                        for vy in self.variables[y].domain[:]:
                            if (vy, vx) not in constraint.possible_values:
                                self.variables[y].domain.remove(vy)
                                if not self.variables[y].domain:
                                    return False

        # print(f"Trying {self.variables[x].name} = {vx}")
        # self.print_variables()

        # If the changes don't lead to a solution, revert back to the original domains
        if self.backtrack(i, fc=True, ac3=ac3):
            return True
        else:
            return False

    def ac4(self):
        q, s, count = self.init_ac4()

        while q:
            y, vy = q.pop(0)
            for x, vx in s[y, vy]:
                count[x, y, vx] -= 1
                if count[x, y, vx] == 0 and vx in self.variables[x].domain:
                    self.variables[x].domain.remove(vx)
                    q.append((x, vx))
        return True

    def init_ac4(self):
        q = []
        s = {}
        count = {}
        for constraint in self.constraints:
            x = constraint.var1
            y = constraint.var2
            for vx in self.variables[x].domain:
                total = 0
                for vy in self.variables[y].domain:
                    if (vx, vy) in constraint.possible_values:
                        total += 1
                        s[y, vy] = s.get((y, vy)) + [(x, vx)]
                    count[x, y, vx] = total
                    if total == 0:
                        self.variables[x].domain.remove(vx)
                        q.append((x, y))
        return q, s, count
