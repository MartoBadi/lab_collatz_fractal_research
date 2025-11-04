"""
╔══════════════════════════════════════════════════════════════════════╗
║        COLLATZ BRUTE FORCE ATTACK - MÁXIMA INTENSIDAD               ║
║                                                                      ║
║  Objetivo: Resolver la conjetura de Collatz o encontrar límites     ║
║  Estrategia: Verificación exhaustiva con familias extendidas        ║
║  Autor: MartoBadi                                                    ║
║  Fecha: 2025-11-04                                                   ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
import json
import time
from collections import defaultdict
from datetime import datetime
import multiprocessing as mp
from functools import partial

# =============================================================================
# CONFIGURACIÓN DE ATAQUE BRUTAL
# =============================================================================

CONFIG = {
    'MAX_N': 10000000,         # Límite superior de números a probar
    'MAX_STEPS': 10000,        # Pasos máximos antes de declarar "fallo"
    'EXTENDED_A': [12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 
                   68, 72, 80, 84, 88, 96, 100],  # Conjunto A extendido
    'Z_TOLERANCE': 20,         # Tolerancia para z en a·4^j + 1 + z
    'MAX_J': 30,               # Potencia máxima de 4 a considerar
    'PARALLEL': True,          # Usar procesamiento paralelo
    'CHUNK_SIZE': 1000,        # Tamaño de chunk para paralelización
    'SAVE_INTERVAL': 50000,    # Guardar resultados cada N números (menos frecuente)
    'SAVE_TO_GIT': False,      # NO subir intermedios
    'VERBOSE': True,           # Mostrar progreso detallado
}

# =============================================================================
# FUNCIONES CORE DE COLLATZ
# =============================================================================

def collatz_step(n):
    """Un paso de Collatz optimizado."""
    return n // 2 if n % 2 == 0 else 3 * n + 1

def collatz_full_trajectory(n, max_steps=10000):
    """
    Calcula trayectoria completa con métricas.
    Retorna: (secuencia, steps, max_value, converged)
    """
    sequence = [n]
    max_val = n
    steps = 0
    
    while n != 1 and steps < max_steps:
        n = collatz_step(n)
        sequence.append(n)
        max_val = max(max_val, n)
        steps += 1
    
    converged = (n == 1)
    return sequence, steps, max_val, converged

# =============================================================================
# VERIFICACIÓN DE PERTENENCIA A FAMILIAS EXTENDIDAS
# =============================================================================

def check_family_membership(n, a_values, z_tolerance=20, max_j=30):
    """
    Verifica si n ∈ {a·4^j + 1 + z : a ∈ A, j ∈ ℕ, |z| ≤ z_tolerance}.
    Retorna: (is_member, a, j, z) o (False, None, None, None)
    """
    for j in range(max_j):
        power = 4**j
        if power > n * 2:  # Optimización: salir si 4^j es demasiado grande
            break
        
        for a in a_values:
            base = a * power + 1
            diff = n - base
            
            if abs(diff) <= z_tolerance:
                return True, a, j, diff
    
    return False, None, None, None

def find_entry_to_family(n, a_values, max_steps=10000, z_tolerance=20):
    """
    Encuentra k_max tal que C^(k_max)(n) está en familia extendida.
    Retorna: (k_max, value, a, j, z, full_trajectory)
    """
    trajectory = [n]
    current = n
    
    for k in range(max_steps):
        is_member, a, j, z = check_family_membership(current, a_values, z_tolerance)
        
        if is_member:
            return k, current, a, j, z, trajectory
        
        if current == 1:
            # Llegó a 1 sin pasar por familia identificable
            return k, 1, None, None, None, trajectory
        
        current = collatz_step(current)
        trajectory.append(current)
    
    # No encontró entrada en max_steps
    return None, None, None, None, None, trajectory

# =============================================================================
# ANÁLISIS INDIVIDUAL DE NÚMERO
# =============================================================================

def analyze_single_number(n, config):
    """
    Análisis exhaustivo de un número individual.
    """
    start_time = time.time()
    
    # Trayectoria completa
    full_seq, total_steps, max_val, converged = collatz_full_trajectory(
        n, max_steps=config['MAX_STEPS']
    )
    
    # Entrada a familia
    k_max, entry_val, a, j, z, entry_traj = find_entry_to_family(
        n, 
        config['EXTENDED_A'],
        max_steps=config['MAX_STEPS'],
        z_tolerance=config['Z_TOLERANCE']
    )
    
    elapsed = time.time() - start_time
    
    result = {
        'n': n,
        'converged': converged,
        'total_steps': total_steps,
        'max_value': max_val,
        'growth_factor': max_val / n if n > 0 else 0,
        'entered_family': k_max is not None,
        'k_max': k_max,
        'entry_value': entry_val,
        'family_a': a,
        'family_j': j,
        'family_z': z,
        'computation_time': elapsed,
        'trajectory_sample': full_seq[:20] if len(full_seq) > 20 else full_seq,
    }
    
    return result

# =============================================================================
# ATAQUE EN PARALELO
# =============================================================================

def parallel_attack(start, end, config):
    """
    Ataque en paralelo sobre un rango de números.
    """
    odds = list(range(start | 1, end, 2))  # Solo impares
    
    if config['PARALLEL']:
        with mp.Pool() as pool:
            analyze_func = partial(analyze_single_number, config=config)
            results = pool.map(analyze_func, odds, chunksize=config['CHUNK_SIZE'])
    else:
        results = [analyze_single_number(n, config) for n in odds]
    
    return results

# =============================================================================
# ANÁLISIS DE RESULTADOS
# =============================================================================

def analyze_results(results):
    """
    Análisis estadístico de resultados.
    """
    total = len(results)
    converged = sum(1 for r in results if r['converged'])
    entered_family = sum(1 for r in results if r['entered_family'])
    
    # Números problemáticos
    failed_convergence = [r for r in results if not r['converged']]
    failed_entry = [r for r in results if not r['entered_family']]
    
    # Estadísticas de k_max
    k_max_values = [r['k_max'] for r in results if r['k_max'] is not None]
    
    # Estadísticas de pasos totales
    total_steps = [r['total_steps'] for r in results if r['converged']]
    
    # Distribución de familias
    family_distribution = defaultdict(int)
    for r in results:
        if r['family_a'] is not None:
            family_distribution[r['family_a']] += 1
    
    summary = {
        'total_tested': total,
        'converged': converged,
        'convergence_rate': converged / total if total > 0 else 0,
        'entered_family': entered_family,
        'family_entry_rate': entered_family / total if total > 0 else 0,
        'failed_convergence': len(failed_convergence),
        'failed_entry': len(failed_entry),
        'k_max_stats': {
            'mean': np.mean(k_max_values) if k_max_values else 0,
            'median': np.median(k_max_values) if k_max_values else 0,
            'std': np.std(k_max_values) if k_max_values else 0,
            'max': max(k_max_values) if k_max_values else 0,
            'min': min(k_max_values) if k_max_values else 0,
        },
        'total_steps_stats': {
            'mean': np.mean(total_steps) if total_steps else 0,
            'median': np.median(total_steps) if total_steps else 0,
            'max': max(total_steps) if total_steps else 0,
        },
        'family_distribution': dict(family_distribution),
        'failed_convergence_samples': [r['n'] for r in failed_convergence[:20]],
        'failed_entry_samples': [r['n'] for r in failed_entry[:20]],
    }
    
    return summary, failed_convergence, failed_entry

# =============================================================================
# REPORTES Y VISUALIZACIÓN
# =============================================================================

def print_progress_report(current, total, elapsed, summary):
    """Reporte de progreso en tiempo real."""
    percent = 100 * current / total
    rate = current / elapsed if elapsed > 0 else 0
    eta = (total - current) / rate if rate > 0 else 0
    
    print(f"\n{'='*70}")
    print(f"PROGRESO: {current}/{total} ({percent:.2f}%)")
    print(f"Velocidad: {rate:.1f} números/seg")
    print(f"Tiempo transcurrido: {elapsed:.1f}s")
    print(f"ETA: {eta:.1f}s")
    print(f"{'='*70}")
    print(f"Convergencia: {summary['convergence_rate']*100:.2f}%")
    print(f"Entrada a familias: {summary['family_entry_rate']*100:.2f}%")
    print(f"Fallos de convergencia: {summary['failed_convergence']}")
    print(f"Fallos de entrada: {summary['failed_entry']}")
    
    if summary['failed_convergence'] > 0:
        print(f"\n⚠️ CONTRAEJEMPLOS POTENCIALES:")
        print(f"   {summary['failed_convergence_samples']}")
    
    if summary['failed_entry'] > 0:
        print(f"\n⚠️ NÚMEROS SIN ENTRADA:")
        print(f"   {summary['failed_entry_samples'][:10]}")

def generate_final_report(config, all_results, total_time):
    """Genera reporte final comprehensivo."""
    summary, failed_conv, failed_entry = analyze_results(all_results)
    
    report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║              COLLATZ BRUTE FORCE - REPORTE FINAL                     ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                                  ║
║  Números probados: {summary['total_tested']:,}                                     ║
║  Tiempo total: {total_time:.2f} segundos                                    ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                         RESULTADOS                                   ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ✓ Convergencia a 1: {summary['convergence_rate']*100:.2f}%                                ║
║  ✓ Entrada a familias: {summary['family_entry_rate']*100:.2f}%                              ║
║                                                                      ║
║  ✗ Fallos de convergencia: {summary['failed_convergence']}                                  ║
║  ✗ Fallos de entrada: {summary['failed_entry']}                                      ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                      ESTADÍSTICAS k_max                              ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Promedio: {summary['k_max_stats']['mean']:.2f}                                          ║
║  Mediana: {summary['k_max_stats']['median']:.0f}                                           ║
║  Máximo: {summary['k_max_stats']['max']}                                              ║
║  Desv. Est.: {summary['k_max_stats']['std']:.2f}                                       ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                  DISTRIBUCIÓN DE FAMILIAS                            ║
╠══════════════════════════════════════════════════════════════════════╣
"""
    
    # Agregar distribución de familias
    for a, count in sorted(summary['family_distribution'].items()):
        report += f"║  a={a:3d}: {count:6d} números ({100*count/summary['total_tested']:.2f}%)                      ║\n"
    
    report += "║                                                                      ║\n"
    report += "╚══════════════════════════════════════════════════════════════════════╝\n"
    
    # Conclusión
    if summary['failed_convergence'] == 0 and summary['failed_entry'] == 0:
        report += "\n✅ TEOREMA VERIFICADO: Todos los números convergen y entran a familias.\n"
    elif summary['failed_convergence'] == 0:
        report += "\n✅ Convergencia verificada, pero algunos no entran a familias conocidas.\n"
        report += "   → Expandir conjunto A o aumentar tolerancia z.\n"
    else:
        report += "\n⚠️ CONTRAEJEMPLOS ENCONTRADOS a la convergencia de Collatz.\n"
        report += f"   → Números problemáticos: {summary['failed_convergence_samples']}\n"
    
    return report, summary

# =============================================================================
# GUARDADO DE RESULTADOS
# =============================================================================

def save_results(results, summary, filename_base='collatz_brute_force'):
    """Guarda resultados en múltiples formatos."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # JSON completo
    json_file = f"{filename_base}_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump({
            'config': CONFIG,
            'summary': summary,
            'results': results,
        }, f, indent=2)
    
    print(f"✓ Resultados guardados en: {json_file}")
    
    # CSV simplificado
    import csv
    csv_file = f"{filename_base}_{timestamp}.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'n', 'converged', 'total_steps', 'k_max', 
            'family_a', 'family_j', 'family_z'
        ])
        writer.writeheader()
        for r in results:
            writer.writerow({
                'n': r['n'],
                'converged': r['converged'],
                'total_steps': r['total_steps'],
                'k_max': r['k_max'],
                'family_a': r['family_a'],
                'family_j': r['family_j'],
                'family_z': r['family_z'],
            })
    
    print(f"✓ CSV guardado en: {csv_file}")

# =============================================================================
# ATAQUE PRINCIPAL
# =============================================================================

def main_attack():
    """Ejecución principal del ataque de fuerza bruta."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║        COLLATZ BRUTE FORCE ATTACK - INICIANDO                        ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  "Soy más ambicioso de lo que debería ser"                          ║
║  - MartoBadi, 2025                                                   ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    print(f"\nCONFIGURACIÓN:")
    print(f"  Rango: 1 a {CONFIG['MAX_N']:,}")
    print(f"  Conjunto A: {len(CONFIG['EXTENDED_A'])} valores")
    print(f"  Tolerancia z: ±{CONFIG['Z_TOLERANCE']}")
    print(f"  Pasos máximos: {CONFIG['MAX_STEPS']:,}")
    print(f"  Paralelización: {'SÍ' if CONFIG['PARALLEL'] else 'NO'}")
    
    # input("\nPresiona ENTER para iniciar el ataque brutal...")  # Auto-ejecutar
    print("\nIniciando ataque brutal automáticamente...")
    
    start_time = time.time()
    all_results = []
    
    # Procesamiento por chunks
    chunk_ranges = list(range(1, CONFIG['MAX_N'], CONFIG['SAVE_INTERVAL']))
    
    for i, chunk_start in enumerate(chunk_ranges):
        chunk_end = min(chunk_start + CONFIG['SAVE_INTERVAL'], CONFIG['MAX_N'])
        
        print(f"\n{'#'*70}")
        print(f"CHUNK {i+1}/{len(chunk_ranges)}: Procesando {chunk_start} a {chunk_end}")
        print(f"{'#'*70}")
        
        chunk_results = parallel_attack(chunk_start, chunk_end, CONFIG)
        all_results.extend(chunk_results)
        
        # Reporte de progreso
        elapsed = time.time() - start_time
        summary, _, _ = analyze_results(all_results)
        
        if CONFIG['VERBOSE']:
            print_progress_report(len(all_results), CONFIG['MAX_N']//2, elapsed, summary)
        
        # Guardar checkpoint solo si SAVE_TO_GIT es True
        # De lo contrario, solo guardar el resultado final
        if CONFIG.get('SAVE_TO_GIT', False):
            if i % 5 == 0 or i == len(chunk_ranges) - 1:
                save_results(all_results, summary, filename_base='collatz_checkpoint')
    
    # Reporte final
    total_time = time.time() - start_time
    final_report, final_summary = generate_final_report(CONFIG, all_results, total_time)
    
    print(final_report)
    
    # Guardar resultados finales
    save_results(all_results, final_summary, filename_base='collatz_final')
    
    # Guardar reporte
    with open('collatz_final_report.txt', 'w') as f:
        f.write(final_report)
    
    print("\n✅ ATAQUE COMPLETADO")
    print(f"   Resultados guardados en archivos locales")
    
    return all_results, final_summary

# =============================================================================
# EJECUCIÓN
# =============================================================================

if __name__ == "__main__":
    results, summary = main_attack()