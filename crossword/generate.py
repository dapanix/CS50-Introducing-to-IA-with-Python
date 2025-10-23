import sys
from collections import deque
from crossword import *
##python generate.py data/structure1.txt data/words1.txt output.png


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        listaParaEliminar={}
        for i in self.crossword.variables:
            for j in self.domains[i]:
                if i.length==len(j):
                    continue
                else:
                    listaParaEliminar.update({j:i})
        
        for key, value in listaParaEliminar.items():

            self.domains[value].remove(key)
            
    def revise(self, x, y):

        revised=False
        if self.crossword.overlaps[x,y]:
            x1, y1 = self.crossword.overlaps[x, y]
            
        for i in self.domains[x]:
            satisface=False
            for j in self.domains[y]:
                if x1>=len(i) and y1>=len(j):
                    if i[x1]==j[y1]:
                        satisface=True
            if not satisface:
                self.domains[x].remove(i)
                revised=True

        return revised
  
    def ac3(self, arcs=None):

        AllArcs=[]#AllArcs tiene las tuplas de los arcs en ambos sentidos, tanto (A,B) como (B,A)
        if arcs is None:
            for i in self.crossword.variables:
                for j in self.crossword.variables:
                    if i==j:
                        continue
                    else:
                        interseccion=self.crossword.overlaps[i,j]
                        if interseccion is not None:
                            TuplaBasura=(i,j)
                            AllArcs.append(TuplaBasura)
                            TuplaBasura=(j,i)
                            AllArcs.append(TuplaBasura)
        else:
            AllArcs=arcs

        cola = deque(AllArcs)
        while cola:

            x, y = cola.popleft()
            if self.revise(x,y):
                Tuplabasura2=(y,x)
                if Tuplabasura2 not in cola:
                    cola.append((y,x))
            cola.pop(0)
        
        for var in self.crossword.variables:
            if len(self.domains[var]) == 0:
                return False
            
            


    def assignment_complete(self, assignment):

        listavalores=assignment.values()
        for i in listavalores:
            if not i or i[0]=="_":
                return False
        return True

    def consistent(self, assignment):
        # 1. Las palabras no deben contener guiones bajos
        for word in assignment.values():
         if "_" in word:
             return False

    # 2. Las palabras asignadas deben ser únicas
        if len(set(assignment.values())) != len(assignment.values()):
         return False

    # 3. Las asignaciones deben tener la longitud correcta
        for variable, word in assignment.items():
            if len(word) != variable.length:
             return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of var, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of var.
        """
        listaSinOrdenar={}
        tienenInterseccion=[]
        listaOrdenada=[]

        tienenInterseccion=self.neighbors(var)
        for j in tienenInterseccion:
            for i in self.domains[var]:
                for x in self.domains[j]:
                    
                    if self.overlaps[var, j] is not None:
                        v1, v2 = self.overlaps[var, j]
                        if x[v2]==i[v1]:
                            continue
                        else:
                            if i not in listaSinOrdenar:
                                listaSinOrdenar[i] = 1
                            else:
                                z=listaSinOrdenar[i]
                                listaSinOrdenar[i]=z+1
        for i in listaSinOrdenar.keys():
            if len(listaSinOrdenar)==0:
                listaOrdenada.append(i)
            else:
                for j in range(len(listaOrdenada)):
                    if listaSinOrdenar[i] > listaSinOrdenar[listaOrdenada[j]]:
                        continue
                    else:
                        listaOrdenada.insert(j,i)
                        break

        return listaOrdenada

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of assignment.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        listaSinAsignar=[]
        nuevalista=[]
        empate=[]
        for i in self.crossword.variables:
            if i not in assignment:
                listaSinAsignar.append(i)
        
        for i in listaSinAsignar:
            if len(nuevalista)==0:
                nuevalista.append(i)
            else:
                for j in range(len(nuevalista)):
                    if len(self.domains[i])>j:
                        continue
                    else:
                        nuevalista.insert(j,i)
        
            empa=False
        for x in nuevalista:
                if self.domains[nuevalista[0]]==self.domains[nuevalista[x]]:
                    empate.append(x)
                    empa=True
                else:
                    break
        if empa:
                empate2={}
                empate.append(nuevalista[0])
                for z in empate:
                    numeroVecinos=self.neighbors(z)
                    empate2[z]=numeroVecinos
                final = max(empate2.values())
        else:
                final=nuevalista[0]
        return final

            


                    

        
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        assignment is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
            # 1. Si el assignment está completo, devolverlo
        if len(assignment) == len(self.crossword.variables):
            return assignment

        # 2. Elegir una variable sin asignar (usamos tu heurística)
        var = self.select_unassigned_variable(assignment)

        # 3. Probar los valores posibles para esa variable
        for value in self.order_domain_values(var, assignment):
            # 4. Comprobar si es consistente
            new_assignment = assignment.copy()
            new_assignment[var] = value

            if self.consistent(new_assignment):
                # 5. Llamar recursivamente
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result  # éxito

        # 6. Si no hay solución
        return None
        

        
        


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
