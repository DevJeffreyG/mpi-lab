# Ejecutar con:
# docker run --rm -v ".:/app" augustosalazar/slim-mpi:2 mpirun --oversubscribe -n 4 --allow-run-as-root python /app/mpi2.py

from mpi4py import MPI
import os
import time
from collections import Counter

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

DATASET_DIR = "/app/dataset"
CONSULTA_PATH = os.path.join(DATASET_DIR, "consulta.txt")

TAG_REQUEST = 1
TAG_WORK    = 2
TAG_RESULT  = 3
TAG_FIN     = 4


def procesar_archivo(ruta, palabras_objetivo):
    contador = Counter()

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            for linea in f:
                for w in linea.lower().split():
                    if w in palabras_objetivo:
                        contador[w] += 1
    except Exception:
        pass

    return contador

# RANK 0
if rank == 0:

    t_total_inicio = time.perf_counter()

    try:
        with open(CONSULTA_PATH, "r", encoding="utf-8") as f:
            palabras_objetivo = set(
                line.strip().lower()
                for line in f
                if line.strip()
            )
    except FileNotFoundError:
        print(f"Error: no se encontró {CONSULTA_PATH}")
        palabras_objetivo = set()

    if os.path.isdir(DATASET_DIR):
        all_files = sorted(
            f for f in os.listdir(DATASET_DIR)
            if f.startswith("file_") and f.endswith(".txt")
        )
    else:
        all_files = []

    total_archivos = len(all_files)

    # Broadcast de palabras objetivo
    palabras_objetivo = comm.bcast(palabras_objetivo, root=0)

    # Distribución dinámica
    siguiente = 0
    workers_activos = size - 1

    freq_global = Counter()

    archivos_por_rank = {r: 0 for r in range(size)}
    tiempos_locales = {r: 0.0 for r in range(size)}

    
    t_local_inicio = time.perf_counter()

    while siguiente < total_archivos:

        # Rank 0 procesa un archivo
        fname = all_files[siguiente]
        siguiente += 1

        ruta = os.path.join(DATASET_DIR, fname)

        local_counter = procesar_archivo(ruta, palabras_objetivo)

        freq_global.update(local_counter)
        archivos_por_rank[0] += 1

        # Atender workers que pidan trabajo
        while comm.iprobe(source=MPI.ANY_SOURCE, tag=TAG_REQUEST):

            status = MPI.Status()
            comm.recv(source=MPI.ANY_SOURCE,
                      tag=TAG_REQUEST,
                      status=status)

            worker = status.Get_source()

            if siguiente < total_archivos:
                archivo = all_files[siguiente]
                siguiente += 1

                comm.send(archivo, dest=worker, tag=TAG_WORK)
                archivos_por_rank[worker] += 1
            else:
                comm.send(None, dest=worker, tag=TAG_FIN)
                workers_activos -= 1

    tiempos_locales[0] = time.perf_counter() - t_local_inicio

    # Finalizar workers restantes
    
    while workers_activos > 0:

        status = MPI.Status()

        comm.recv(source=MPI.ANY_SOURCE,
                  tag=TAG_REQUEST,
                  status=status)

        worker = status.Get_source()

        comm.send(None, dest=worker, tag=TAG_FIN)

        workers_activos -= 1

    # Recolectar resultados
    for _ in range(1, size):

        payload = comm.recv(source=MPI.ANY_SOURCE,
                            tag=TAG_RESULT)

        origen = payload["rank"]

        freq_global.update(payload["counter"])
        tiempos_locales[origen] = payload["time"]

    t_total = time.perf_counter() - t_total_inicio

    # Métricas
    tiempos = list(tiempos_locales.values())

    t_max = max(tiempos)
    t_prom = sum(tiempos) / size

    imbalance = t_max / t_prom if t_prom > 0 else 1.0

    print("\n" + "=" * 40)
    print("MPI VERSION 2 - RESUMEN GLOBAL")
    print("=" * 40)

    for r in range(size):
        print(
            f"[Rank {r}] "
            f"Archivos: {archivos_por_rank[r]} | "
            f"Tiempo local: {tiempos_locales[r]:.6f}s"
        )

    print("-" * 40)
    print(f"Total archivos: {total_archivos}")
    print(f"Total ocurrencias: {sum(freq_global.values())}")
    print(f"Tiempo total: {t_total:.6f}s")
    print(f"Tiempo máximo por proceso: {t_max:.6f}s")
    print(f"Tiempo promedio por proceso: {t_prom:.6f}s")
    print(f"Load imbalance ratio: {imbalance:.6f}s")

    print("\nTop 10 palabras:")
    for palabra, cuenta in freq_global.most_common(10):
        print(f"  {palabra}: {cuenta}")


# WORKERS
else:

    palabras_objetivo = comm.bcast(None, root=0)

    local_counter = Counter()

    t_inicio = time.perf_counter()

    while True:

        # Solicitar trabajo
        comm.send(None, dest=0, tag=TAG_REQUEST)

        status = MPI.Status()

        tarea = comm.recv(source=0,
                          tag=MPI.ANY_TAG,
                          status=status)

        if status.Get_tag() == TAG_FIN:
            break

        ruta = os.path.join(DATASET_DIR, tarea)

        local_counter.update(
            procesar_archivo(ruta, palabras_objetivo)
        )

    t_local = time.perf_counter() - t_inicio

    comm.send(
        {
            "rank": rank,
            "counter": local_counter,
            "time": t_local
        },
        dest=0,
        tag=TAG_RESULT
    )