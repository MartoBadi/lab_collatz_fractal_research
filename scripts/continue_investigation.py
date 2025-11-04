import math
import random
import json
from statistics import mean
import matplotlib.pyplot as plt
try:
    import sklearn
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.neural_network import MLPRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("scikit-learn no disponible, omitiendo modelos ML")

import csv

# Collatz utilities

def collatz_step(n):
    return n // 2 if n % 2 == 0 else 3 * n + 1


def collatz_sequence(n, max_steps=10000):
    seq = [n]
    steps = 0
    while n != 1 and steps < max_steps:
        n = collatz_step(n)
        seq.append(n)
        steps += 1
    return seq, steps


# Families exploration

def analyze_family(a, max_k=5, z_values=(1,2,3,4)):
    results = []
    for k in range(max_k):
        for z in z_values:
            n = a * (4 ** k) + 1 + z
            seq, steps = collatz_sequence(n)
            results.append({'a': a, 'k': k, 'z': z, 'n': n, 'steps': steps})
    return results


def analyze_family_extended(a, max_k=20, z_values=(1,2,3,4), max_n=10**7):
    results = []
    for k in range(max_k):
        for z in z_values:
            n = a * (4 ** k) + 1 + z
            if n > max_n:
                break
            seq, steps = collatz_sequence(n)
            results.append({'a': a, 'k': k, 'z': z, 'n': n, 'steps': steps})
    return results

def train_ml_model():
    if not SKLEARN_AVAILABLE:
        return None
    
    # Generate training data with more features
    data = []
    for _ in range(2000):  # More data
        n = random.randint(1, 20000)
        seq, steps = collatz_sequence(n, max_steps=5000)
        if seq[-1] == 1:
            data.append({
                'n': n, 
                'log_n': math.log(n), 
                'n_mod_4': n % 4,
                'n_mod_8': n % 8,
                'parity': n % 2,
                'steps': steps
            })
    
    if len(data) < 100:
        return None
    
    X = [[d['n'], d['log_n'], d['n_mod_4'], d['n_mod_8'], d['parity']] for d in data]
    y = [d['steps'] for d in data]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train models
    models = {
        'LinearRegression': LinearRegression(),
        'RandomForest': RandomForestRegressor(n_estimators=50, random_state=42),
        'MLPRegressor': MLPRegressor(hidden_layer_sizes=(50, 25), max_iter=500, random_state=42)
    }
    
    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, pred)
        results[name] = {'mae': mae}
        print(f"{name} MAE: {mae:.2f}")
    
    return results

def save_to_csv(results, filename='collatz_analysis.csv'):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['a', 'k', 'z', 'n', 'steps']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for a, res_list in results.items():
            for res in res_list:
                writer.writerow(res)
    print(f"Datos guardados en {filename}")

def plot_improvements(summary):
    a_values = [s['a'] for s in summary]
    improvements = [s['improvement'] for s in summary]
    
    plt.figure(figsize=(10, 6))
    plt.bar(a_values, improvements)
    plt.xlabel('a')
    plt.ylabel('Mejora (x veces)')
    plt.title('Mejora de convergencia por familia')
    plt.savefig('family_improvements.png')
    plt.close()
    print("Gráfico guardado en family_improvements.png")

def estimate_fractal_dimension():
    """Estima la dimensión fractal del conjunto de números eficientes."""
    print("Estimando dimensión fractal de las islas de orden...")
    
    # Usar método de box-counting simple
    # Considerar números hasta max_n, con "cajas" de tamaño 2^k
    
    max_n = 10000
    efficient_numbers = []
    
    for n in range(1, max_n + 1):
        seq, steps = collatz_sequence(n)
        if steps < 50:  # Umbral de eficiencia
            efficient_numbers.append(n)
    
    # Estimar dimensión usando conteo de cajas
    # Para dimensión fractal, usar log(N(epsilon)) vs log(1/epsilon)
    
    epsilons = [2**k for k in range(5, 14)]  # epsilon = 32,64,128,...,8192
    counts = []
    
    for eps in epsilons:
        # Contar "cajas" de tamaño eps que contienen números eficientes
        boxes = set()
        for n in efficient_numbers:
            box = n // eps
            boxes.add(box)
        counts.append(len(boxes))
    
    # Regresión lineal para estimar dimensión
    if len(counts) > 2:
        x = [math.log(1/eps) for eps in epsilons]
        y = [math.log(count) for count in counts]
        
        # Simple linear regression
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi*yi for xi,yi in zip(x,y))
        sum_x2 = sum(xi**2 for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
        
        print(f"Dimensión fractal estimada: {slope:.4f}")
        print(f"Números eficientes encontrados: {len(efficient_numbers)}")
        print(f"Densidad: {len(efficient_numbers)/max_n:.6f}")
        
        return slope
    else:
        print("Insuficientes datos para estimar dimensión fractal")
        return None

def sample_random_steps(sample_size=200, max_n=10000):
    steps = []
    for _ in range(sample_size):
        n = random.randint(1, max_n)
        seq, s = collatz_sequence(n, max_steps=5000)
        steps.append(s)
    return mean(steps) if steps else None

def main():
    families = [20,24,28,32,36,40,44,48]
    all_results = {}

    avg_random = sample_random_steps(200, max_n=20000)
    print(f'Promedio pasos números aleatorios (muestra 200): {avg_random:.2f}')

    summary = []
    for a in families:
        res = analyze_family_extended(a, max_k=10)  # Increased to 10 with n limit
        avg_steps = mean(r['steps'] for r in res)
        improvement = avg_random / avg_steps if avg_steps > 0 else float('inf')
        summary.append({'a': a, 'avg_steps': avg_steps, 'improvement': improvement, 'sample_size': len(res)})
        all_results[a] = res
        print(f'Familia a={a}: avg_steps={avg_steps:.2f}, improvement={improvement:.3f}')

    summary_sorted = sorted(summary, key=lambda x: x['improvement'], reverse=True)
    print('\nTop familias por mejora:')
    for s in summary_sorted:
        print(f" a={s['a']} -> avg_steps={s['avg_steps']:.2f}, improvement={s['improvement']:.3f}")

    # Save results
    out = {'avg_random': avg_random, 'summary': summary, 'details': all_results}
    with open('investigation_results.json', 'w') as f:
        json.dump(out, f, indent=2)
    print('\nResultados guardados en investigation_results.json')

    # ML training
    ml_results = train_ml_model()
    if ml_results:
        print(f"Modelos ML entrenados: {list(ml_results.keys())}")

    # Save to CSV
    save_to_csv(all_results, 'collatz_analysis.csv')

    # Plot improvements
    plot_improvements(summary)
    
    # Fractal analysis
    fractal_dim = estimate_fractal_dimension()
    if fractal_dim:
        print(f"Dimensión fractal de las islas de orden: {fractal_dim:.4f}")
    
    # Generalized Collatz
    print("\n=== ANÁLISIS DE COLLATZ GENERALIZADO ===")
    generalizations = [
        (5, 1, "5n+1"),
        (7, 1, "7n+1"),
        (9, 1, "9n+1"),
        (11, 1, "11n+1"),
        (3, -1, "3n-1"),
        (5, -1, "5n-1"),
        (7, -1, "7n-1")
    ]
    for mult, add, name in generalizations:
        print(f"\n--- {name} ---")
        gen_results = analyze_generalized_families(multiplier=mult, add=add)
    
    # Theoretical analysis
    print("\n=== ANÁLISIS TEÓRICO ===")
    theory_results = theoretical_analysis()
    
    # Special analysis of a=28
    print("\n=== ANÁLISIS ESPECIAL a=28 ===")
    a28_results = analyze_a28_special_properties()
    
    # Mathematical analysis of a=28
    analyze_a28_mathematical_properties()
    
    # Prueba extendida para validar hipótesis
    test_extended_generalized_collatz()

    print("Análisis completado.")

def generalized_collatz_step(n, multiplier=3, add=1):
    """Generalized Collatz step: n/2 if even, multiplier*n + add if odd"""
    return n // 2 if n % 2 == 0 else multiplier * n + add

def generalized_collatz_sequence(n, multiplier=3, add=1, max_steps=10000):
    seq = [n]
    steps = 0
    while n != 1 and steps < max_steps:
        n = generalized_collatz_step(n, multiplier, add)
        seq.append(n)
        steps += 1
    return seq, steps

def analyze_generalized_families(multiplier=5, add=1, families=[20,24,28], max_k=5):
    """Analyze efficient families for generalized Collatz"""
    print(f"Analizando familias para Collatz generalizado: {multiplier}n + {add}")
    
    # Sample random for generalized
    random_steps = []
    for _ in range(100):
        n = random.randint(1, 5000)
        seq, s = generalized_collatz_sequence(n, multiplier, add, max_steps=2000)
        if seq and seq[-1] == 1:
            random_steps.append(s)
    avg_random = mean(random_steps) if random_steps else 100
    print(f'Pasos promedio aleatorios: {avg_random:.2f}')
    
    results = {}
    for a in families:
        res = []
        for k in range(max_k):
            for z in range(1, 5):
                n = a * (4 ** k) + 1 + z
                if n > 10**5: continue
                seq, steps = generalized_collatz_sequence(n, multiplier, add)
                if seq and seq[-1] == 1:
                    res.append({'a': a, 'k': k, 'z': z, 'n': n, 'steps': steps})
        if res:
            avg_steps = mean(r['steps'] for r in res)
            improvement = avg_random / avg_steps if avg_steps > 0 else 1
            results[a] = {'avg_steps': avg_steps, 'improvement': improvement, 'samples': len(res)}
            print(f'Familia a={a}: avg_steps={avg_steps:.2f}, improvement={improvement:.3f} (muestras: {len(res)})')
    
    return results

def analyze_modular_preservation(n, multiplier=3, add=1, max_steps=50):
    """Analyze how modular properties are preserved in the sequence."""
    seq = generalized_collatz_sequence(n, multiplier, add, max_steps)[0]
    if not seq or seq[-1] != 1:
        return None
    
    # Check preservation mod 4
    odd_nums = [x for x in seq if x % 2 == 1]
    if len(odd_nums) < 2:
        return {'preserved_mod4': True, 'consistency': 1.0}
    
    diffs = [odd_nums[i+1] - odd_nums[i] for i in range(len(odd_nums)-1)]
    preserved_mod4 = all(d % 4 == 0 for d in diffs)
    
    # Consistency ratio
    consistent_count = sum(1 for d in diffs if d % 4 == 0)
    consistency = consistent_count / len(diffs)
    
    return {
        'preserved_mod4': preserved_mod4,
        'consistency': consistency,
        'odd_steps': len(odd_nums),
        'total_steps': len(seq)
    }

def theoretical_analysis():
    """Theoretical analysis of why certain families work."""
    print("=== ANÁLISIS TEÓRICO DE EFICACIA MODULAR ===")
    
    # Test modular preservation for efficient families
    test_cases = []
    for mult, add in [(3,1), (5,1), (7,1), (9,1), (11,1)]:
        for a in [20, 24, 28, 32]:
            n = a * 4 + 1 + 1  # k=1, z=1
            result = analyze_modular_preservation(n, mult, add)
            if result:
                test_cases.append({
                    'mult': mult, 'add': add, 'a': a, 'n': n,
                    'preserved': result['preserved_mod4'],
                    'consistency': result['consistency']
                })
    
    # Analyze patterns
    preserved_cases = [tc for tc in test_cases if tc['preserved']]
    print(f"Casos con preservación modular: {len(preserved_cases)}/{len(test_cases)}")
    
    if preserved_cases:
        avg_consistency = sum(tc['consistency'] for tc in preserved_cases) / len(preserved_cases)
        print(f"Consistencia promedio: {avg_consistency:.3f}")
        
        # Check if a=28 is special
        a28_cases = [tc for tc in preserved_cases if tc['a'] == 28]
        if a28_cases:
            a28_avg = sum(tc['consistency'] for tc in a28_cases) / len(a28_cases)
            print(f"Consistencia para a=28: {a28_avg:.3f}")
    
    return test_cases

def analyze_a28_special_properties():
    """Analyze why a=28 is exceptionally effective across transformations."""
    print("=== ANÁLISIS ESPECIAL DE a=28 ===")
    
    # Test different transformations
    transformations = [
        (3, 1, "3n+1"),
        (5, 1, "5n+1"),
        (7, 1, "7n+1"),
        (9, 1, "9n+1"),
        (11, 1, "11n+1"),
        (3, -1, "3n-1"),
        (5, -1, "5n-1"),
        (7, -1, "7n-1")
    ]
    
    results = []
    
    for mult, add, name in transformations:
        print(f"\n--- Analizando {name} ---")
        
        # Test different k for a=28
        for k in range(5):
            n = 28 * (4 ** k) + 1 + 1  # z=1
            if n > 10**6: continue
            
            seq, steps = generalized_collatz_sequence(n, mult, add)
            if seq and seq[-1] == 1:
                # Analyze sequence properties
                odd_count = sum(1 for x in seq if x % 2 == 1)
                max_val = max(seq)
                growth_factor = max_val / n
                
                # Check modular properties
                mod_preservation = analyze_modular_preservation(n, mult, add)
                
                results.append({
                    'transform': name,
                    'k': k,
                    'n': n,
                    'steps': steps,
                    'odd_ratio': odd_count / len(seq),
                    'growth_factor': growth_factor,
                    'modular_preserved': mod_preservation['preserved_mod4'] if mod_preservation else False
                })
                
                print(f"  k={k}, n={n}, steps={steps}, growth={growth_factor:.2f}, modular={'✓' if mod_preservation and mod_preservation['preserved_mod4'] else '✗'}")
    
    # Analyze patterns
    print("\n=== PATRONES IDENTIFICADOS ===")
    
    # Group by transformation
    by_transform = {}
    for r in results:
        t = r['transform']
        if t not in by_transform:
            by_transform[t] = []
        by_transform[t].append(r)
    
    for t, res_list in by_transform.items():
        avg_steps = sum(r['steps'] for r in res_list) / len(res_list)
        modular_count = sum(1 for r in res_list if r['modular_preserved'])
        print(f"{t}: avg_steps={avg_steps:.1f}, modular_preserved={modular_count}/{len(res_list)}")
    
    # Why a=28?
    print("\n=== HIPÓTESIS PARA EFICACIA DE a=28 ===")
    print("1. a=28 = 4×7, donde 7 es primo")
    print("2. Posible resonancia con módulo 7 en algunas transformaciones")
    print("3. Estructura algebraica especial en campo finito")
    print("4. Preservación de propiedades en múltiples módulos")
    
    return results

def analyze_a28_mathematical_properties():
    """
    Análisis matemático profundo de por qué a=28 es excepcional
    """
    print("\n=== ANÁLISIS MATEMÁTICO PROFUNDO DE a=28 ===")
    
    a = 28
    print(f"a = {a} = 4 × 7")
    print(f"Factores: {factorize(a)}")
    
    # Análisis de propiedades algebraicas
    print(f"\nPropiedades algebraicas:")
    print(f"  - Módulo 4: {a} ≡ {a % 4} (mod 4)")
    print(f"  - Módulo 7: {a} ≡ {a % 7} (mod 7)")
    print(f"  - Módulo 8: {a} ≡ {a % 8} (mod 8)")
    
    # Análisis de resonancia con transformaciones
    transformations = [
        (3, 1, "3n+1"),
        (5, 1, "5n+1"), 
        (7, 1, "7n+1"),
        (9, 1, "9n+1"),
        (11, 1, "11n+1"),
        (3, -1, "3n-1"),
        (5, -1, "5n-1"),
        (7, -1, "7n-1")
    ]
    
    print(f"\nAnálisis de resonancia con transformaciones:")
    for mult, add, name in transformations:
        mod_mult = a % mult if mult != 0 else 0
        mod_add = a % abs(add) if add != 0 else 0
        print(f"  {name}: a ≡ {mod_mult} (mod {mult}), a ≡ {mod_add} (mod {abs(add)})")
        
        # Hipótesis de resonancia
        if mult == 7 or abs(add) == 7:
            print(f"    → POSIBLE RESONANCIA: 7 divide a {a}!")
        elif mod_mult == 0:
            print(f"    → RESONANCIA PERFECTA: {mult} divide a {a}!")
    
    # Análisis de estructura en campo finito
    print(f"\nEstructura en campos finitos:")
    for p in [2, 3, 5, 7, 11, 13]:
        if a % p == 0:
            print(f"  F_{p}: a ≡ 0 (divisible por {p})")
        else:
            # Calcular orden o propiedades
            print(f"  F_{p}: a ≡ {a % p}, orden potencial")
    
    # Hipótesis sobre eficacia universal
    print(f"\nHIPÓTESIS SOBRE EFICACIA UNIVERSAL DE a=28:")
    print(f"1. Resonancia con primo 7: a=28=4×7, explicando excelencia en 7n±1")
    print(f"2. Estructura modular especial: 28 mod 4 = 0, creando familias 'puras'")
    print(f"3. Propiedad aditiva: 28 = 32 - 4, relacionando con potencias de 2")
    print(f"4. Compatibilidad con transformación base: 3n+1 preserva ciertas propiedades")
    print(f"5. Teoría de campos: Comportamiento excepcional en F_7 y F_4")

def factorize(n):
    """Factorización simple"""
    factors = []
    i = 2
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors

def test_extended_generalized_collatz():
    """
    Prueba transformaciones extendidas para validar hipótesis de resonancia
    """
    print("\n=== PRUEBA EXTENDIDA DE COLLATZ GENERALIZADO ===")
    
    # Transformaciones extendidas para probar hipótesis
    extended_transforms = [
        (13, 1, "13n+1"),
        (17, 1, "17n+1"), 
        (19, 1, "19n+1"),
        (23, 1, "23n+1"),
        (13, -1, "13n-1"),
        (17, -1, "17n-1"),
        (19, -1, "19n-1"),
        (23, -1, "23n-1"),
    ]
    
    families_to_test = [28, 44, 52, 68, 76]  # Múltiplos de 4 × primos
    
    for mult, add, name in extended_transforms:
        print(f"\n--- {name} ---")
        analyze_generalized_families(multiplier=mult, add=add, families=families_to_test, max_k=3)

if __name__ == '__main__':
    main()
