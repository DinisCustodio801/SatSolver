import sys
import itertools

def parse_dimacs_cnf(filename):
    num_vars = 0
    num_clauses = 0
    clauses = []
    current_clause = []
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            # Ignora linhas de comentario e linhas vazias
            if not line or line.startswith('c'):
                continue
            
            # Linha de configuracao do problema: p cnf <vars> <clauses>
            elif line.startswith('p'):
                parts = line.split()
                num_vars = int(parts[2])
                num_clauses = int(parts[3])

            elif line.startswith('%'):
                break

            else:
                tokens = line.split()
                for token in tokens:
                    if token == '%':
                        continue
                    
                    val = int(token)
                    if val == 0:
                        if current_clause:
                            clauses.append(current_clause)
                            current_clause = []
                    else:
                        current_clause.append(val)
                        
    return num_vars, clauses

def eval_clause(clause, assignment):
    for literal in clause:
        var_idx = abs(literal) - 1
        var_val = assignment[var_idx]
        
        # Literal positivo quer True; literal negativo quer False
        literal_val = var_val if literal > 0 else not var_val
        
        if literal_val:
            return True  # Clausula satisfeita
    return False

def solve_exact_sat(num_vars, clauses):
    solutions = []
    
    # Gera todas as 2^n combinacoes de (False, True)
    for assignment in itertools.product([False, True], repeat=num_vars):
        satisfied = True
        for clause in clauses:
            if not eval_clause(clause, assignment):
                satisfied = False
                break
                
        if satisfied:
            solutions.append(assignment)
            
    return solutions

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "hoos.cnf"
    
    num_vars, clauses = parse_dimacs_cnf(file_path)
    print(f"--- A processar {file_path} ---")
    print(f"Variaveis: {num_vars} | Clausulas lidas: {len(clauses)}")
    
    solutions = solve_exact_sat(num_vars, clauses)
    
    print(f"Total de solucões encontradas: {len(solutions)}")