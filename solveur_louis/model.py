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
                y = [var not in instance_variable for var in con.variables]
                if len(y) == 1:
                    for val in y[0].dom[0:back[y[0].name][0]]:
                        if (val, instance_valor[0]) not in con.solution and (
                        instance_valor[0], val) not in con.solution:
                            y[0].dom[y[0].dom.index(val)], y[0].dom[back[y[0].name][0] - 1] = y[0].dom[back[y[0].name][0] - 1], y[0].dom[y[0].dom.index(val)]
                            back[y[0].name][0] = back[y[0].name][0] - 1


    def backtrack(self, f, g, ac3 = False, forward = False):

        #f: function that chose which variable to instantiate
        #g: function that chose at which valor to instantiate

        #back = [] * len(self.variable)
        #if a variable is empty return no solution
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
        #possible_variables = self.variable
        already_searched_valor = []
        possible_valor = []
        #travaux sur f et g pour prendre en compte variable déjà instanciée etc
        while len(instance_variable) < len(self.variable) or not verif:
            if not verif:
                already_searched_valor[0] = [instance_valor.pop(0)] + already_searched_valor[0]
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

                    instance_valor = [g(list(set(possible_valor) - set(already_searched_valor[0])))] + instance_valor
                    # reduction of domain to singleton
                    instance_variable[0].dom[instance_variable[0].dom.index(instance_valor[0])], instance_variable[0].dom[0] = instance_variable[0].dom[0], instance_variable[0].dom[instance_variable[0].dom.index(instance_valor[0])]
                    back[instance_variable[0].name][0] = 1 #+ back[instance_variable[0].name]
                    verif = self.instance_check(instance_variable, instance_valor)

            else:
                # new variable choice:
                new_lst = list(set(self.variable) - set(instance_variable))
                if len(new_lst) == 0:
                    return instance_variable, instance_valor
                else:
                    already_searched_valor = [[]] + already_searched_valor
                    instance_variable = [f(new_lst)] + instance_variable
                    instance_valor = [g(instance_variable[0].dom[0:back[instance_variable[0].name][0]])] + instance_valor
                    possible_valor = instance_variable[0].dom[0:back[instance_variable[0].name][0]]
                    verif = self.instance_check(instance_variable, instance_valor)
                    for var in back:
                        back[var] = [back[var][0]] + back[var]



            #verif si contrainte ok ?
            #for constraint in self.constraint :
            #    x,y = constraint
            #    if x
            #forward checking or not
                #ajoute les valeurs dans back


            if ac3:
                self.ac3(back)
            if forward:
                self.forwardChecking(back, instance_variable, instance_valor)
            for i in back:
                if back[i][0] == 0:
                    verif = False

        return instance_variable, instance_valor


#var1 = Variable(nom=1, domaine=[1, 2,3])
#var2 = Variable(nom=2, domaine=[1,2,3,4])
#var3 = Variable(nom=3, domaine=[ 2])
#model = Model( var=[var1, var2, var3], con=[])
#model.alldiff()
#for con in model.constraint:
#    x, y = con.variables
#   print("constraint: {} with solution: {}".format((x.name, y.name), con.solution ))


def f(lst):
    return lst[0]


def g(lst):
    return lst[0]

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

model = nqueen(3)
for var in model.variable:
    print("variable: {}, domaine: {}".format(var.name, var.dom))

for con in model.constraint:
    x,y = con.variables
    print("constraint: {}, domaine: {}".format((x.name,y.name), con.solution))

instance_variable, instance_valor = model.backtrack(f,g,ac3=True)

for i in range(len(instance_variable)):
    print("variable: {}, resultat: {}".format(instance_variable[i].name, instance_valor[i]))