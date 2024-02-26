import random

import constraint
import time
from variable import *
from constraint import *

#from variable import Variable
#from constraint import Constraint

class Model:
    def __init__(self, var: list[Variable], con: list[Constraint]):
        self.constraint = con
        self.variable = var

    def addconstraint(self, con: Constraint):
        self.constraint = self.constraint + [con]

    def fusion_constraint(self):
        remove = []
        for i in range(len(self.constraint)):
            if i not in remove:
                x,y = self.constraint[i].variables
                for j in range(i+1, len(self.constraint)):
                    if j not in remove:
                        if x in self.constraint[j].variables and y in self.constraint[j].variables:
                            sol_j = set(self.constraint[j].solution)
                            sol_i = set(self.constraint[i].solution)
                            new_sol = list(sol_i.intersection(sol_j))
                            remove += [j]
                            self.constraint[i].solution = new_sol
        for index in sorted(remove, reverse=True):
            del self.constraint[index]

    def alldiff(self, add_nom=0):
        for i in range(len(self.variable)):
            for j in range(i+1, len(self.variable)):
                solution = []
                for dom1 in (self.variable[i]).dom:
                    for dom2 in (self.variable[j]).dom:
                        if (dom1 + add_nom * self.variable[i].name )!= (dom2 + add_nom * self.variable[j].name):
                            solution += [(dom1, dom2)]
                new_constraint = Constraint(x=self.variable[i], y=self.variable[j], solution=solution)
                self.addconstraint(new_constraint)

    def  instance_check(self, instance_variable,instance_valor):
        #modifier avec back
        #check if instance is true or not
        #optimisation : ne check que la dernière variable ajouté
        #for var in instance_variable:
        for constraint in self.constraint:
            x, y = constraint.variables
            if x in instance_variable and y in instance_variable:
                valor_x = instance_valor[instance_variable.index(x)]
                valor_y = instance_valor[instance_variable.index(y)]
                if (valor_x, valor_y) not in constraint.solution:
                    return False
        return True

    def support(self, con, a, y, lim: int):
        #return True if valor a is supported by y
        for b in y.dom[0:lim]:
            if (a,b) in con.solution:
                return True
        return False

    def ac3(self, back: dict):
        # add new element problem
        # prob if domaine = null ?
        test = []
        #for var in back:
            # modif original list ?
        #    var = [var[0]] + var
        for con in self.constraint:
            test = [con] + test
        while len(test) > 0:
            con = test.pop(0)
            x, y = con.variables
            for a in x.dom[0:back[x.name][0]]:
                if not self.support(con, a, y, back[y.name][0]):
                    # reduction du domaine
                    x.dom[x.dom.index(a)], x.dom[back[x.name][0] - 1] = x.dom[back[x.name][0] - 1], x.dom[x.dom.index(a)]
                    back[x.name][0] = back[x.name][0] - 1
                    for con2 in self.constraint:
                        if x in con2.variables:
                            if not con2 in test:
                                test = [con2] + test


    def forwardChecking(self, back, instance_variable, instance_valor):

        for con in self.constraint:
            if instance_variable[0] in con.variables:
                y = list(set(con.variables) - set(instance_variable))
                if len(y) == 1:
                    for val in y[0].dom[0:back[y[0].name][0]]:
                        if (val, instance_valor[0]) not in con.solution and (
                        instance_valor[0], val) not in con.solution:
                            y[0].dom[y[0].dom.index(val)], y[0].dom[back[y[0].name][0] - 1] = y[0].dom[back[y[0].name][0] - 1], y[0].dom[y[0].dom.index(val)]
                            back[y[0].name][0] = back[y[0].name][0] - 1


    def backtrack(self, f, g, ac3 = False, forward = False, print_back = False, dens= False, pro_int=1000):

        #f: function that chose which variable to instantiate
        #g: function that chose at which valor to instantiate

        #back = [] * len(self.variable)
        #if a variable is empty return no solution
        tab = {}
        if dens:
            tab = tab_density(self)
            print("density loaded")

        #starting_time = time.time()

        for con in self.constraint:
            if len(con.solution) == 0:
                return [], []
        back = {}
        for var in self.variable:
            back[var.name] = [len(var.dom)]
        verif = True
        #tuple name valor
        instance_variable = []
        instance_valor = []
        count_instance_valor = {}
        #possible_variables = self.variable
        already_searched_valor = []
        possible_valor = []
        backtrack = 0
        #travaux sur f et g pour prendre en compte variable déjà instanciée etc
        while len(instance_variable) < len(self.variable) or not verif:
            print(len(instance_variable))
            if not verif:
                pop = instance_valor.pop(0)
                already_searched_valor[0] = [pop] + already_searched_valor[0]
                count_instance_valor[pop] = count_instance_valor[pop] - 1
                for var in back:
                    back[var].pop(0)
                possible_valor = instance_variable[0].dom[0:back[instance_variable[0].name][0]]

                #backtrack
                if len(set(possible_valor) - set(already_searched_valor[0])) == 0:
                    #we select a new variable not already selected
                    already_searched_valor.pop(0)
                    instance_variable.pop(0)

                    if len(instance_variable) == 0:
                        return [], []
                    #we go back to domain from parent's state
                    possible_valor = instance_variable[0].dom[0:back[instance_variable[0].name][0]]

                else:

                    for var in back:
                        back[var] = [back[var][0]] + back[var]
                    new_valor = g(list(set(possible_valor) - set(already_searched_valor[0])), count_instance_valor)
                    instance_valor = [new_valor] + instance_valor
                    if new_valor in count_instance_valor.keys():
                        count_instance_valor[new_valor] = count_instance_valor[new_valor] + 1
                    else:
                        count_instance_valor[new_valor] = 1
                    # reduction of domain to singleton
                    instance_variable[0].dom[instance_variable[0].dom.index(instance_valor[0])], instance_variable[0].dom[0] = instance_variable[0].dom[0], instance_variable[0].dom[instance_variable[0].dom.index(instance_valor[0])]
                    back[instance_variable[0].name][0] = 1 #+ back[instance_variable[0].name]
                    verif = self.instance_check(instance_variable, instance_valor)
                    backtrack += 1
                    if forward:
                        self.forwardChecking(back, instance_variable, instance_valor)

            else:
                # new variable choice:
                new_lst = list(set(self.variable) - set(instance_variable))
                if len(new_lst) == 0:
                    return instance_variable, instance_valor
                else:
                    already_searched_valor = [[]] + already_searched_valor

                    if dens and len(instance_variable) < pro_int:
                        max = max_density(new_lst, back, self.constraint, tab)
                        if len(max) == 0:
                            verif = False
                        else:
                            [var, sol] = max
                            #[var, sol] = max_density(new_lst, back, self.constraint, tab)
                            instance_variable = [var] + instance_variable
                            instance_valor = [sol] + instance_valor
                            if sol in count_instance_valor.keys():
                                count_instance_valor[sol] = count_instance_valor[sol] + 1
                            else:
                                count_instance_valor[sol] = 1
                            verif = self.instance_check(instance_variable, instance_valor)
                            for var in back:
                                back[var] = [back[var][0]] + back[var]
                            if forward:
                                self.forwardChecking(back, instance_variable, instance_valor)
                    else:
                        instance_variable = [profondeur(new_lst, self.constraint, back)] + instance_variable
                        new_valor2 = g(instance_variable[0].dom[0:back[instance_variable[0].name][0]], count_instance_valor)
                        instance_valor = [new_valor2] + instance_valor
                        if new_valor2 in count_instance_valor.keys():
                            count_instance_valor[new_valor2] = count_instance_valor[new_valor2] + 1
                        else:
                            count_instance_valor[new_valor2] = 1
                        possible_valor = instance_variable[0].dom[0:back[instance_variable[0].name][0]]
                        verif = self.instance_check(instance_variable, instance_valor)
                        for var in back:
                            back[var] = [back[var][0]] + back[var]
                        if forward:
                            self.forwardChecking(back, instance_variable, instance_valor)

            if ac3:
                self.ac3(back)
            #if forward:
            #    self.forwardChecking(back, instance_variable, instance_valor)
            for i in back:
                if back[i][0] == 0:
                    verif = False

        if print_back:
            print("the number of backtrack is: {}".format(backtrack))
        #end_time = time.time()
        #print("backtrack executed in: {}s".format(end_time - starting_time))
        return instance_variable, instance_valor


#var1 = Variable(nom=1, domaine=[1, 2,3])
#var2 = Variable(nom=2, domaine=[1,2,3,4])
#var3 = Variable(nom=3, domaine=[ 2])
#model = Model( var=[var1, var2, var3], con=[])
#model.alldiff()
#for con in model.constraint:
#    x, y = con.variables
#   print("constraint: {} with solution: {}".format((x.name, y.name), con.solution ))


def f(lst, constraint, back):
    count = [0]*len(lst)
    for con in constraint:
        x, y = con.variables
        if x in lst:
            count[lst.index(x)] +=1
        if y in lst:
            count[lst.index(y)] +=1
    return lst[count.index(max(count))]

def profondeur(lst, constraint, back):
    var_min = lst[0]
    dom_min = back[var_min.name][0]
    for var in lst:
       domaine = back[var.name][0]
       if domaine < dom_min:
        var_min = var
        dom_min = domaine
    return var_min


def g(lst,count_instance_valor):
    #return random.choice(lst)
    if lst[0] in count_instance_valor.keys():
        max1 = count_instance_valor[lst[0]]
    else:
        if len(count_instance_valor)>1:
            max1 = max(count_instance_valor)
        else:
            max1 = 100000
    sol = lst[0]

    for val in lst:
        if val in count_instance_valor.keys():
            if count_instance_valor[val]<max1:
                max1 = count_instance_valor[val]
                sol = val
    return sol
    #return min(lst)


def density(con: Constraint, var: Variable, d):
    x, y = con.variables
    count = 0
    if x == var:
        for sol in con.solution:
            if sol[0] == d:
                count += 1
    else:
        for sol in con.solution:
            if sol[1] == d:
                count += 1
    return count / len(con.solution)

def tab_density(model):
    tab = {}
    for con in model.constraint:
        for var in con.variables:
            for d in var.dom:
                tab[(con, var, d)] = density(con, var, d)
    return tab

def max_density(lst, back, constraint, tab):
    max = 0
    solution = []
    for con in constraint:
        for var in list(set(con.variables).intersection(set(lst))):
            for sol in var.dom[0:back[var.name][0]]:
                dens = tab[(con, var, sol)]
                if dens >= max:
                    max = dens
                    solution = [var, sol]
    return solution

#lst1 = [1,2,3,4]
#lst2 = [1,3,5]
#instance_variable, instance_valor = model.backtrack(f,g,forward=True)

#for var in instance_variable:
#           print("var: {}. ".format(var.name))
#print(instance_valor)


def nqueen(n: int):
    variables = []
    for i in range(n):
        variables += [Variable(nom=i+1, domaine=[i + 1 for i in range(n)])]
    model = Model(var=variables, con=[])
    model.alldiff()
    model.alldiff(add_nom=1)
    model.alldiff(add_nom=-1)
    model.fusion_constraint()

    return model


#for var in model.variable:
#    print("variable: {}, domaine: {}".format(var.name, var.dom))

#for con in model.constraint:
#    x,y = con.variables
#    print("constraint: {}, domaine: {}".format((x.name,y.name), con.solution))

#n=7
#model = nqueen(n)
#instance_variable, instance_valor = model.backtrack(f, g, print_back=True, forward=True)

#if len(instance_variable) == n:
#    print("YES")
#else:
#   print("NO")

#for i in range(len(instance_variable)):
#    print("variable: {}, resultat: {}".format(instance_variable[i].name, instance_valor[i]))

def con_color(n):
    dom=[]
    for i in range(n):
        for j in range(i+2,n+1):
            dom += [(i+1, j)]
            dom += [(j, i+1)]
    return dom

def graph(link, n,e):
    file1 = open(link, 'r')
    Lines = file1.readlines()
    variables = []
    for i in range(e):
        variables += [Variable(nom=i+1, domaine=[i + 1 for i in range(n)])]
    model = Model(var=variables, con=[])
    for line in Lines:
        if line[0] == 'e':
            lst = line.strip().split(" ")
            model.addconstraint(con=Constraint(x=variables[int(lst[1])-1], y=variables[int(lst[2])-1], solution=con_color(n)))
    return model


starting_time = time.time()
model = graph("queen13_13.col", n=13, e=169)

instance_variable, instance_valor = model.backtrack(f, g,forward=True,print_back=True, pro_int=70)
end_time = time.time()
print("solution found in: {}s".format(end_time - starting_time))
if len(instance_variable)==169:
    print("YES")
else:
   print("NO")