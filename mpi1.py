# Ejecutar con: docker run --rm -v ".:/app" augustosalazar/slim-mpi:2 mpirun --oversubscribe -n 2 --allow-run-as-root python /app/mpi1.py

from mpi4py import MPI
import os
import time
from collections import Counter

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

DATASET_DIR = '/app/dataset'
CONSULTA_PATH = os.path.join(DATASET_DIR, 'consulta.txt')

# --- FASE 1: Preparación y Distribución ---
palabras_objetivo = None
chunks = None

if rank == 0:
    ex_time = time.perf_counter()

    # Cargar palabras de consulta
    try:
        with open(CONSULTA_PATH, 'r', encoding='utf-8') as f:
            palabras_objetivo = set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        print(f"Rank 0: Error crítico - No se encontró {CONSULTA_PATH}")
        palabras_objetivo = set()

    # Obtener lista de archivos a procesar
    if os.path.isdir(DATASET_DIR):
        all_files = [f for f in os.listdir(DATASET_DIR) if f.startswith("file_") and f.endswith(".txt")]
    else:
        all_files = []

    # Dividir los archivos para cada proceso
    avg = len(all_files) // size
    rem = len(all_files) % size
    chunks = []
    start = 0
    for i in range(size):
        end = start + avg + (1 if i < rem else 0)
        chunks.append(all_files[start:end])
        start = end
else:
    palabras_objetivo = None
    chunks = None

# Distribución
palabras_objetivo = comm.bcast(palabras_objetivo, root=0)
files_assigned = comm.scatter(chunks, root=0)

# --- FASE 2: Procesamiento ---
t_start_local = time.perf_counter()

local_counter = Counter()
local_tokens = 0
num_files = len(files_assigned)

for fname in files_assigned:
    ruta = os.path.join(DATASET_DIR, fname)
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            for linea in f:
                palabras = linea.lower().split()
                local_tokens += len(palabras)
                for w in palabras:
                    if w in palabras_objetivo:
                        local_counter[w] += 1
    except Exception as e:
        pass 

t_end_local = time.perf_counter()
local_elapsed = t_end_local - t_start_local

# --- FASE 3: Reporte de archivos procesados ---
print(f"[Rank {rank}] Archivos asignados: {num_files} | Tiempo local: {local_elapsed:.6f}s")

# --- FASE 4: Envió de resultados a Rank 0 ---
all_counters = comm.gather(local_counter, root=0)
all_tokens = comm.gather(local_tokens, root=0)
all_times = comm.gather(local_elapsed, root=0)

if rank == 0:
    freq_global = Counter()
    for c in all_counters:
        freq_global.update(c)
    
    total_tokens = sum(all_tokens)
    max_local_time = max(all_times)
    avg_local_time = sum(all_times) / size
    ex_time = time.perf_counter() - ex_time
    print("\n" + "="*40)
    print("RESUMEN GLOBAL")
    print("="*40)
    print(f"Total tokens leídos: {total_tokens}")
    print(f"Total ocurrencias:   {sum(freq_global.values())}")
    print(f"Tiempo total (ejecución):  {ex_time:.6f}s")
    print(f"Tiempo máximo por proceso:  {max_local_time:.6f}s")
    print(f"Tiempo promedio por proceso:  {avg_local_time:.6f}s")
    print("-" * 40)
    print("Top 10 palabras encontradas:")
    for palabra, cuenta in freq_global.most_common(10):
        print(f"  {palabra}: {cuenta}")