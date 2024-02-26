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
        self.variables = []  # List of variables
        self.constraints = []  # List of constraints
        self.solution = {}  # Dictionary of variable assignments
        self.counter = 0  # Counter for the number of branches

    # Copy the model
    @classmethod
    def copy(cls, model):
        new_model = cls()
        new_model.variables = copy.deepcopy(model.variables)
        new_model.constraints = copy.deepcopy(model.constraints)
        new_model.solution = {}
        new_model.counter = 0
        return new_model

    # Add a variable object to the model
    def add_variable_object(self, variable):
        self.variables.append(variable)

    # Add a constraint object to the model
    def add_constraint_object(self, constraint):
        self.constraints.append(constraint)

    # Add a variable to the model
    def add_variable(self, name, domain):
        variable = Variable(name, domain)
        self.variables.append(variable)

    # Add a constraint to the model
    def add_constraint(self, var1, var2, possible_values):
        constraint = Constraint(var1, var2, possible_values)
        self.constraints.append(constraint)

    # Update the constraints after variable changes were made
    def update_constraints(self):
        for constraint in self.constraints:
            constraint.possible_values = [
                (i, j)
                for i, j in constraint.possible_values
                if i in self.variables[constraint.var1].domain
                and j in self.variables[constraint.var2].domain
            ]

    # Print the model
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

    # Print the variables
    def print_variables(self):
        for variable in self.variables:
            print(f"{variable.name}: {variable.domain}")
        print()

    # Print the constraints
    def print_constraints(self):
        for constraint in self.constraints:
            print(
                f"{self.variables[constraint.var1].name} - {self.variables[constraint.var2].name}: {constraint.possible_values}"
            )
        print()

    # Print the solution
    def print_solution(self):
        self.solution = dict(sorted(self.solution.items()))
        print(self.solution)
        print(self.counter)
        # for k, v in self.solution.items():
        #    print(f"{self.variables[k].name}: {v}")
        print()

    # Solve the CSP with backtracking with options for forward checking and MAC with AC3
    def backtrack(self, i, fc=False, ac3=False):
        self.counter += 1

        # Add single domain values to the assignment
        # This speeds up the algorithm when using AC3, but less efficient for other methods
        if ac3:
            self.add_single_domain_values(i)

        # verify if no constraint is violated
        if self.violates_constraint(i):
            return False

        # If the assignment is complete, return the solution
        if self.is_complete(i):
            self.solution = i
            # print("Solution found")
            return True

        # Choose an unassigned variable
        x = self.choose_unassigned_variable(i)

        # Try all values in the domain of the variable
        for v in self.variables[x].domain:
            i_prime = self.instantiate(i, x, v)

            # if MAC with AC3 is used, run AC3 at each branch
            if ac3:
                # print("AC3")

                # Save a copy of the original domains to backtrack
                original_domains = {var: var.domain[:] for var in self.variables}
                self.variables[x].domain = [v]
                if self.ac3():
                    # use forward checking if the option is picked
                    if fc:
                        if self.forward_checking(i_prime, x, v, ac3=True):
                            return True
                        else:

                            # if the changes don't lead to a solution, revert back to the original domains
                            for var in self.variables:
                                var.domain = original_domains[var]
                    else:
                        if self.backtrack(i_prime, ac3=True):
                            return True

                        # if the changes don't lead to a solution, revert back to the original domains
                        else:
                            for var in self.variables:
                                var.domain = original_domains[var]
                else:
                    for var in self.variables:
                        var.domain = original_domains[var]

            # use forward checking if the option is picked
            elif fc:
                original_domains = {var: var.domain[:] for var in self.variables}
                self.variables[x].domain = [v]
                if self.forward_checking(i_prime, x, v):
                    return True
                else:
                    # if the changes don't lead to a solution, revert back to the original domains
                    for var in self.variables:
                        var.domain = original_domains[var]

            # if no option is picked, use regular backtracking
            else:
                if self.backtrack(i_prime):
                    return True

        return False

    # Add single domain values to the assignment
    def add_single_domain_values(self, i):
        for j, variable in enumerate(self.variables):
            if j not in i:
                if len(variable.domain) == 1:
                    i[j] = variable.domain[0]

    # Verify if no constraint is violated
    def violates_constraint(self, i):
        for constraint in self.constraints:
            if constraint.var1 in i and constraint.var2 in i:
                val1 = i[constraint.var1]
                val2 = i[constraint.var2]
                if (val1, val2) not in constraint.possible_values:
                    return True
        return False

    # Verify if the assignment is complete
    def is_complete(self, i):
        return len(i) == len(self.variables)

    # Choose an unassigned variable to instantiate
    # The default is to choose the first unassigned variable
    # Other options include choosing the variable with the smallest domain
    # We can add more heuristics here for the choic of variables
    def choose_unassigned_variable(self, i):

        unassigned_variables = [j for j in range(len(self.variables)) if j not in i]
        return min(unassigned_variables, key=lambda x: len(self.variables[x].domain))
        return max(
            unassigned_variables,
            key=lambda x: len(
                [c for c in self.constraints if c.var1 == x or c.var2 == x]
            ),
        )

        if len(unassigned_variables) > len(self.variables) / 2:
            # Choose the variable that has the most constraints
            return max(
                unassigned_variables,
                key=lambda x: len(
                    [c for c in self.constraints if c.var1 == x or c.var2 == x]
                ),
            )
        else:
            # Choose the variable with the smallest domain
            return min(
                unassigned_variables, key=lambda x: len(self.variables[x].domain)
            )

        # Choose the first unassigned variable
        for j, variable in enumerate(self.variables):
            if j not in i:
                return j

    # Instantiate a variable
    def instantiate(self, i, x, v):
        i_prime = i.copy()
        i_prime[x] = v
        return i_prime

    # AC3 algorithm
    def ac3(self):
        to_test = [i for i in range(len(self.constraints))]

        while to_test:
            constraint = self.constraints[to_test.pop(0)]
            x = constraint.var1
            y = constraint.var2
            # revise the domains of x
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

            # revise the domains of y
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

    # Forward checking algorithm
    def forward_checking(self, i, x, vx, ac3=False):

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

    # Attempt to implement AC4, but it is not working
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
