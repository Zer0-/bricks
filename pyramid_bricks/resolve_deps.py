class Dependant:
    def __init__(self, name, *deps):
        self.name = name
        self.deps = deps

    def __repr__(self):
        return self.name

G = Dependant('G')
E = Dependant('E', G)
F = Dependant('F', G)
D = Dependant('D', E, F)
B = Dependant('B')
C = Dependant('C', B, D)
A = Dependant('A', B, C)

def walk(dependant, visited={}):
    if dependant in visited:
        return visited[dependant]
    deps = [walk(dep, visited) for dep in dependant.deps]
    print(dependant, ': ', ', '.join(deps), sep='')
    initted = str(dependant)
    visited[dependant] = initted
    return initted

walk(A)
