# Conteo Paralelo de Palabras en un Corpus de Texto con MPI

## 1. Información del Equipo
* **Estudiante 1:** [Nombre y Apellidos] - [Código/Usuario]
* **Estudiante 2:** [Nombre y Apellidos] - [Código/Usuario]
* **Estudiante 3:** [Nombre y Apellidos] - [Código/Usuario]
* **Estudiante 4:** [Nombre y Apellidos] - [Código/Usuario]

## 2. Descripción del Problema
El objetivo de este laboratorio es diseñar, implementar y evaluar experimentalmente soluciones paralelas para un problema de procesamiento de texto. Específicamente, se busca contar cuántas veces aparece un conjunto de palabras clave (definidas en consulta.txt) dentro de un gran corpus de texto fragmentado en múltiples archivos (file_XXXX.txt). Se reportarán las 10 palabras más frecuentes. 

El problema se aborda primero con una solución secuencial de referencia, seguida de dos implementaciones paralelas usando MPI (Message Passing Interface): una con distribución estática de archivos y otra con balanceo de carga dinámico, para analizar cómo el número de procesos y la estrategia de distribución de carga afectan el rendimiento general (Speedup, Eficiencia y Balanceo).

## 3. Entorno e Instrucciones de Ejecución
Para garantizar un entorno reproducible y consistente, todas las ejecuciones se realizan dentro de un contenedor Docker provisto para el laboratorio.

Requisitos previos:
* Docker instalado y en ejecución.

Generación del Dataset:
Antes de ejecutar las pruebas, se debe generar el conjunto de datos ejecutando:
docker run --rm -v "$(pwd)":/app augustosalazar/slim-mpi:2 python /app/generator.py

Ejecución del Baseline Secuencial:
docker run --rm -v "$(pwd)":/app augustosalazar/slim-mpi:2 python /app/baseline_secuencial.py

Ejecución de MPI Versión 1 (Ejemplo con 4 workers):
docker run --rm -v "$(pwd)":/app augustosalazar/slim-mpi:2 mpirun --oversubscribe -n 4 --allow-run-as-root python /app/mpi1.py

Ejecución de MPI Versión 2 (Ejemplo con 4 workers):
docker run --rm -v "$(pwd)":/app augustosalazar/slim-mpi:2 mpirun --oversubscribe -n 4 --allow-run-as-root python /app/mpi2.py

(Nota: Para cambiar el número de procesos, modifica el valor después de la bandera -n en los comandos de mpirun).

## 4. Plan Experimental

### a. Baseline Secuencial (Qué hace y cómo)
El script baseline_secuencial.py lee las palabras a buscar desde consulta.txt y las almacena en un conjunto (set) en memoria. Luego, itera linealmente por cada archivo file_*.txt presente en el directorio del corpus. Por cada línea en cada archivo, extrae las palabras, las convierte a minúsculas y verifica si están en el conjunto de palabras objetivo. Si existe coincidencia, incrementa un contador global (Counter de Python). Al finalizar la lectura de todos los archivos, ordena los resultados, imprime el Top 10 y guarda el conteo total en un archivo CSV.

### b. MPI Versión 1 (Qué hace y cómo)
El script mpi1.py implementa un modelo de distribución de carga estático. 
1. El proceso maestro (Rank 0) lee las palabras de consulta y determina la lista total de archivos del corpus.
2. Esta lista se divide en partes iguales (chunks) dependiendo del tamaño del comunicador (número de procesos).
3. Rank 0 usa comm.bcast para transmitir las palabras objetivo a todos los procesos y comm.scatter para asignar a cada nodo su respectivo bloque de archivos.
4. Cada proceso (incluyendo el maestro) itera sobre su subconjunto de archivos de forma independiente, procesando las coincidencias y llevando un conteo local.
5. Finalmente, se usa comm.gather para recolectar los contadores locales, los tiempos y los tokens en el Rank 0, quien consolida los contadores y extrae el Top 10 global.

### c. El Procedimiento de Prueba
Para evaluar el rendimiento de ambas implementaciones MPI se realizará el siguiente procedimiento:
1. Se verificará la cantidad de núcleos físicos/lógicos disponibles en el contenedor.
2. Se ejecutarán pruebas para configuraciones de p en {1, 2, 4, 8} procesos.
3. Para mitigar variaciones del sistema operativo, se realizarán 4 ejecuciones por cada configuración.
4. Se registrará el tiempo de ejecución total y el tiempo local de cada proceso para calcular el Speedup, la Eficiencia y observar la presencia de desbalanceo de carga.

---

## 5. Ejecución del Plan Experimental

### a. Tiempos del Baseline Secuencial
* **Ejecución 1:** 6.0204 s
* **Ejecución 2:** 5.9594 s
* **Ejecución 3:** 5.9587 s
* **Ejecución 4:** 6.0089 s
* **Promedio Secuencial (Tseq):** 5.9868 s

### b. Resultados de Tiempos MPI Versión 1

#### MPI 1 - 1 Worker (Proceso)
<table>
  <tr>
    <td><img src="resultados/mpi1/1worker/run1.png" width="400" alt="Run 1"/></td>
    <td><img src="resultados/mpi1/1worker/run2.png" width="400" alt="Run 2"/></td>
  </tr>
  <tr>
    <td><img src="resultados/mpi1/1worker/run3.png" width="400" alt="Run 3"/></td>
    <td><img src="resultados/mpi1/1worker/run4.png" width="400" alt="Run 4"/></td>
  </tr>
</table>
**Tiempo Promedio (1 Worker):** 4.26735s

#### MPI 1 - 2 Workers
<table>
  <tr>
    <td><img src="resultados/mpi1/2workers/run1.png" width="400" alt="Run 1"/></td>
    <td><img src="resultados/mpi1/2workers/run2.png" width="400" alt="Run 2"/></td>
  </tr>
  <tr>
    <td><img src="resultados/mpi1/2workers/run3.png" width="400" alt="Run 3"/></td>
    <td><img src="resultados/mpi1/2workers/run4.png" width="400" alt="Run 4"/></td>
  </tr>
</table>
**Tiempo Promedio (2 Workers):** 2.34152s

#### MPI 1 - 4 Workers
<table>
  <tr>
    <td><img src="resultados/mpi1/4workers/run1.png" width="400" alt="Run 1"/></td>
    <td><img src="resultados/mpi1/4workers/run2.png" width="400" alt="Run 2"/></td>
  </tr>
  <tr>
    <td><img src="resultados/mpi1/4workers/run3.png" width="400" alt="Run 3"/></td>
    <td><img src="resultados/mpi1/4workers/run4.png" width="400" alt="Run 4"/></td>
  </tr>
</table>
**Tiempo Promedio (4 Workers):** 1.337225s

#### MPI 1 - 8 Workers
<table>
  <tr>
    <td><img src="resultados/mpi1/8workers/run1.png" width="400" alt="Run 1"/></td>
    <td><img src="resultados/mpi1/8workers/run2.png" width="400" alt="Run 2"/></td>
  </tr>
  <tr>
    <td><img src="resultados/mpi1/8workers/run3.png" width="400" alt="Run 3"/></td>
    <td><img src="resultados/mpi1/8workers/run4.png" width="400" alt="Run 4"/></td>
  </tr>
</table>
**Tiempo Promedio (8 Workers):** 0.83215s

### c. Evidencia de Desbalanceo de Carga
*Añade aquí tu análisis y evidencia (basada en las capturas anteriores) sobre si hubo procesos que terminaron mucho antes que otros en la Versión 1. Usa los reportes de "Tiempo máximo" vs "Tiempo promedio por proceso".*

### d. Implementation of MPI Version 2 correcting the imbalance with its timing results

La versión mpi2.py soluciona el desbalanceo utilizando un patrón Maestro-Trabajador (Dinámico). El Rank 0 mantiene una cola con todos los archivos; cuando un trabajador (Rank > 0) se queda sin trabajo, envía una solicitud (TAG_REQUEST). El maestro escucha dinámicamente usando comm.iprobe y asigna un único archivo a la vez (TAG_WORK). El Rank 0 también procesa archivos locales cuando solo hay 1 proceso disponible. Cuando ya no quedan archivos, envía señales de terminación (TAG_FIN) y recolecta los contadores.

#### MPI 2 - 1 Worker (Proceso)
<table>
  <tr>
    <td><img src="resultados/mpi2/1worker/run1.png" width="400" alt="Run 1"/></td>
    <td><img src="resultados/mpi2/1worker/run2.png" width="400" alt="Run 2"/></td>
  </tr>
  <tr>
    <td><img src="resultados/mpi2/1worker/run3.png" width="400" alt="Run 3"/></td>
    <td><img src="resultados/mpi2/1worker/run4.png" width="400" alt="Run 4"/></td>
  </tr>
</table>
**Tiempo Promedio:** 3.6678s | **Speedup:** [X] | **Eficiencia:** [X] | **Balance Ratio:** [X]

#### MPI 2 - 2 Workers
<table>
  <tr>
    <td><img src="resultados/mpi2/2workers/run1.png" width="400" alt="Run 1"/></td>
    <td><img src="resultados/mpi2/2workers/run2.png" width="400" alt="Run 2"/></td>
  </tr>
  <tr>
    <td><img src="resultados/mpi2/2workers/run3.png" width="400" alt="Run 3"/></td>
    <td><img src="resultados/mpi2/2workers/run4.png" width="400" alt="Run 4"/></td>
  </tr>
</table>
**Tiempo Promedio:** 3.7103s | **Speedup:** [X] | **Eficiencia:** [X] | **Balance Ratio:** [X]

#### MPI 2 - 4 Workers
<table>
  <tr>
    <td><img src="resultados/mpi2/4workers/run1.png" width="400" alt="Run 1"/></td>
    <td><img src="resultados/mpi2/4workers/run2.png" width="400" alt="Run 2"/></td>
  </tr>
  <tr>
    <td><img src="resultados/mpi2/4workers/run3.png" width="400" alt="Run 3"/></td>
    <td><img src="resultados/mpi2/4workers/run4.png" width="400" alt="Run 4"/></td>
  </tr>
</table>
**Tiempo Promedio:** 1.3828s | **Speedup:** [X] | **Eficiencia:** [X] | **Balance Ratio:** [X]

#### MPI 2 - 8 Workers
<table>
  <tr>
    <td><img src="resultados/mpi2/8workers/run1.png" width="400" alt="Run 1"/></td>
    <td><img src="resultados/mpi2/8workers/run2.png" width="400" alt="Run 2"/></td>
  </tr>
  <tr>
    <td><img src="resultados/mpi2/8workers/run3.png" width="400" alt="Run 3"/></td>
    <td><img src="resultados/mpi2/8workers/run4.png" width="400" alt="Run 4"/></td>
  </tr>
</table>
**Tiempo Promedio:** 0.7163s | **Speedup:** [X] | **Eficiencia:** [X] | **Balance Ratio:** [X]

---

## 6. Analysis

**a. Did the first MPI implementation improve execution time compared to the sequential baseline?**
* [Espacio para tu respuesta basada en la evidencia de los tiempos obtenidos]

**b. Was the observed speedup linear?**
* [Espacio para tu respuesta: Compara si al duplicar núcleos el tiempo se redujo exactamente a la mitad, y justifica por el overhead de comunicación]

**c. Is there evidence of load imbalance? How was it observed?**
* [Espacio para tu respuesta: Refiérete a los tiempos locales (Tiempo máximo vs Tiempo promedio) arrojados en MPI 1]

**d. Did the second implementation reduce load imbalance?**
* [Espacio para tu respuesta: Compara la métrica de Load imbalance ratio de la versión 2 frente a las variaciones de la versión 1]

**e. Did the improved distribution strategy produce a real performance improvement?**
* [Espacio para tu respuesta: Compara los Tp de MPI 2 vs MPI 1 para 4 y 8 procesos]

**f. What limitations affected your experiment?**
* [Espacio para tu respuesta: Habla sobre lectura a disco (I/O bound), número real de núcleos de la máquina host frente a contenedores Docker sobre-suscritos, cuellos de botella de hardware, etc.]

## 7. Conclusions

[Espacio para la conclusión general. Aquí debes declarar formalmente si las implementaciones mejoraron los tiempos frente al secuencial, detallar que el problema principal en V1 fue que archivos más pesados demoraban a ciertos nodos mientras otros estaban ociosos (estático), y cómo la V2 mitigó esto pidiendo trabajo bajo demanda (dinámico), finalizando con un juicio ingenieril fundamentado en los datos y el hardware disponible.]