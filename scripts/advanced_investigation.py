import math
import random
import statistics
from collections import Counter

def collatz_sequence(n, max_steps=10000):
    """
    Genera la secuencia completa de Collatz hasta llegar a 1.
    Retorna: (secuencia, número_de_pasos)
    """
    sequence = [n]
    steps = 0

    while n != 1 and steps < max_steps:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        sequence.append(n)
        steps += 1

    return sequence, steps

def explore_algebraic_patterns():
    """
    Exploración de patrones algebraicos más profundos en las familias eficientes
    """
    print(f"\n{'='*80}")
    print("EXPLORACIÓN DE PATRONES ALGEBRAICOS PROFUNDOS")
    print(f"{'='*80}")

    # Hipótesis: Familias de la forma 4*p donde p es primo podrían ser especiales
    primes = [7, 11, 13, 17, 19, 23, 29, 31]
    special_families = [4 * p for p in primes]

    print("Familias especiales 4*p (p primo):")
    for p in primes[:5]:  # Limitamos para no hacer demasiado largo
        a = 4 * p
        print(f"  a = 4 × {p} = {a}")

        # Analizar propiedades modulares
        print(f"    Propiedades: a ≡ {a % 4} (mod 4), a ≡ {a % p} (mod {p})")

        # Probar algunas semillas
        test_numbers = []
        for k in range(2):
            for z in range(2):
                n = a * (4 ** k) + 1 + z
                if n < 10000:  # Límite razonable
                    seq, steps = collatz_sequence(n)
                    if seq[-1] == 1 and steps < 200:
                        test_numbers.append((n, steps))

        if test_numbers:
            avg_steps = statistics.mean(steps for _, steps in test_numbers)
            print(f"    Rendimiento promedio: {avg_steps:.1f} pasos ({len(test_numbers)} muestras)")
        print()

def analyze_modular_cycles():
    """
    Análisis de ciclos modulares en las secuencias eficientes
    """
    print(f"\n{'='*80}")
    print("ANÁLISIS DE CICLOS MODULARES")
    print(f"{'='*80}")

    # Examinar cómo se comportan los residuos módulo diferentes potencias de 2
    test_cases = [
        (28, 1, 0),  # Nuestra familia estrella
        (44, 1, 0),  # Mejor en 3n+1 estándar
        (20, 1, 0),  # Familia original del notebook
    ]

    moduli = [4, 8, 16, 32]

    for a, k, z in test_cases:
        n = a * (4 ** k) + 1 + z
        seq, steps = collatz_sequence(n)

        print(f"\nAnálisis modular para n = {n} (a={a}):")
        print(f"Secuencia: {seq[:15]}{'...' if len(seq) > 15 else ''}")

        for mod in moduli:
            residues = [x % mod for x in seq[:20]]  # Primeros 20 términos
            print(f"  Residuos mod {mod}: {residues}")

            # Buscar patrones
            if len(set(residues)) < len(residues) * 0.7:  # Si hay repeticiones
                print(f"    → Patrón detectable mod {mod}")
        print()

def investigate_fractal_properties():
    """
    Investigación más profunda de las propiedades fractales
    """
    print(f"\n{'='*80}")
    print("INVESTIGACIÓN DE PROPIEDADES FRACTALES AVANZADAS")
    print(f"{'='*80}")

    # Generar conjunto de números eficientes
    efficient_numbers = []
    max_n = 10000

    for n in range(1, max_n + 1):
        seq, steps = collatz_sequence(n)
        if seq[-1] == 1 and steps < 50:  # Umbral de eficiencia
            efficient_numbers.append(n)

    print(f"Números eficientes encontrados: {len(efficient_numbers)}")
    print(f"Densidad: {len(efficient_numbers)/max_n:.3f}")

    # Análisis de distribución
    efficient_set = set(efficient_numbers)

    # Clustering: números eficientes cercanos
    clusters = []
    current_cluster = []

    for n in range(1, max_n + 1):
        if n in efficient_set:
            current_cluster.append(n)
        else:
            if current_cluster:
                if len(current_cluster) > 1:
                    clusters.append(current_cluster)
                current_cluster = []

    print(f"\nClusters de números eficientes (>1 elemento): {len(clusters)}")
    for i, cluster in enumerate(clusters[:5]):  # Mostrar primeros 5
        print(f"  Cluster {i+1}: {cluster[:10]}{'...' if len(cluster) > 10 else ''} (tamaño: {len(cluster)})")

    # Análisis de gaps
    gaps = []
    prev = None
    for n in efficient_numbers:
        if prev is not None:
            gaps.append(n - prev)
        prev = n

    if gaps:
        print(f"\nEstadísticas de gaps entre números eficientes:")
        print(f"  Gap promedio: {statistics.mean(gaps):.1f}")
        print(f"  Gap mediano: {statistics.median(gaps):.1f}")
        print(f"  Gap máximo: {max(gaps)}")
        print(f"  Gap mínimo: {min(gaps)}")

def explore_generalized_collatz_theory():
    """
    Exploración teórica de por qué ciertas transformaciones permiten eficacia universal
    """
    print(f"\n{'='*80}")
    print("EXPLORACIÓN TEÓRICA DE COLLATZ GENERALIZADO")
    print(f"{'='*80}")

    # Teoría: Transformaciones que preservan ciertas propiedades modulares
    # podrían permitir que familias eficientes mantengan su eficacia

    test_transforms = [
        (5, 1, "5n+1"),
        (7, 1, "7n+1"),
        (11, 1, "11n+1"),
        (13, 1, "13n+1"),
    ]

    print("Hipótesis: Transformaciones que son 'compatibles' con la estructura modular")
    print("de las familias eficientes permiten preservar su eficacia.\n")

    for mult, add, name in test_transforms:
        print(f"Transformación: {name}")

        # Analizar compatibilidad teórica
        print(f"  Multiplicador: {mult}, Suma: {add}")

        # Propiedades modulares clave para familias eficientes
        key_moduli = [4, 7, 8]  # Basado en nuestras familias

        compatible_moduli = []
        for mod in key_moduli:
            # Una transformación es "compatible" si preserva ciertas propiedades
            # Esto es una simplificación teórica
            if mult % mod != 0 or add % mod != 0:
                compatible_moduli.append(mod)

        if compatible_moduli:
            print(f"  Compatible con módulos: {compatible_moduli}")
        else:
            print("  Compatible con todos los módulos clave")

        # Predicción teórica vs evidencia empírica
        # (Aquí irían comparaciones con nuestros resultados anteriores)

        print()

def run_advanced_investigation():
    """
    Ejecutar investigación avanzada completa
    """
    print("🚀 INICIANDO INVESTIGACIÓN AVANZADA EN COLLATZ")
    print("Objetivo: Profundizar en los patrones algebraicos descubiertos")

    explore_algebraic_patterns()
    analyze_modular_cycles()
    investigate_fractal_properties()
    explore_generalized_collatz_theory()

    print(f"\n{'='*80}")
    print("INVESTIGACIÓN AVANZADA COMPLETADA")
    print("Descubrimientos preparados para análisis teórico profundo")
    print(f"{'='*80}")

# Ejecutar investigación avanzada
if __name__ == "__main__":
    run_advanced_investigation()