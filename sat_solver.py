import sys
import time
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


    # Verifica se os literais usam variaveis dentro do intervalo declarado
    max_var = max((abs(lit) for clause in clauses for lit in clause), default=0)
    if num_vars == 0:
        num_vars = max_var
    elif max_var > num_vars:
        print(f"Aviso: existem literais ate a variavel {max_var}, mas o cabecalho "
              f"declara {num_vars} variaveis; a usar {max_var}.", file=sys.stderr)
        num_vars = max_var

    # Avisa se o numero de clausulas nao corresponde ao cabecalho
    if num_clauses and len(clauses) != num_clauses:
        print(f"Aviso: o cabecalho declara {num_clauses} clausulas, "
              f"mas foram lidas {len(clauses)}.", file=sys.stderr)

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
    # Uso: python sat_solver.py [--dimacs] [ficheiro.cnf]
    use_dimacs = "--dimacs" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--dimacs"]
    file_path = args[0] if args else "hoos.cnf"

    num_vars, clauses = parse_dimacs_cnf(file_path)

    # Mede apenas a fase de busca (a solucao do problema)
    start = time.perf_counter()
    solutions = solve_exact_sat(num_vars, clauses)
    elapsed = time.perf_counter() - start

    num_assignments = 2 ** num_vars
    solution_value = 1 if solutions else 0

    if use_dimacs:
        # Formato de output do DIMACS (satformat.pdf, secao 2.4)
        print(f"c Instance: {file_path}")
        print(f"c Total de solucoes encontradas: {len(solutions)}")
        print(f"s cnf {solution_value} {num_vars} {len(clauses)}")
        for sol in solutions:
            literals = ' '.join(str(i + 1) if v else str(-(i + 1))
                                for i, v in enumerate(sol))
            print(f"v {literals}")
        print(f"t cnf {solution_value} {num_vars} {len(clauses)} "
              f"{elapsed:.3f} {num_assignments}")
    else:
        print(f"--- A processar {file_path} ---")
        print(f"Variaveis: {num_vars} | Clausulas lidas: {len(clauses)}")
        print(f"Total de solucoes encontradas: {len(solutions)}")
        for sol in solutions:
            bits = ''.join('1' if v else '0' for v in sol)
            values = ', '.join(f'x{i + 1}={v}' for i, v in enumerate(sol))
            print(f"  {bits}  ({values})")
        print(f"Tempo: {elapsed:.3f} s ({num_assignments} atribuicoes visitadas)")