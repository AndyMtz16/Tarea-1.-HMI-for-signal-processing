Procesador de Audio con Interfaz Gráfica
Este proyecto es una aplicación en Python que desarrollé para mi clase de Interfaces Humano-Máquina. La idea es que puedas cargar archivos de audio, aplicarles distintos filtros y ver cómo cambia la señal en tiempo real. Además, podrás escuchar la diferencia entre el audio original y el filtrado.

¿Qué hace la aplicación?
Permite cargar archivos de audio en formatos como WAV, MP3 y AAC.

Muestra la forma de onda del audio.

Ofrece tres tipos de filtros:

Pasa-bajas (se conservan las frecuencias bajas)

Pasa-altas (se conservan las frecuencias altas)

Pasa-banda (se permite un rango específico de frecuencias)

Calcula y muestra la transformada de Fourier (FFT) del audio original y filtrado, en gráficos separados.

Reproduce tanto el audio original como el filtrado.

Guarda el audio procesado en formato WAV.

Permite resetear la aplicación para volver al audio original.

Requisitos
Para ejecutar la aplicación necesitas tener instalado lo siguiente:

Python 3.x

Además, instala las siguientes bibliotecas usando pip:

nginx
Copiar
tkinter
matplotlib
numpy
scipy
librosa
soundfile
pygame
Cómo usar la aplicación
Ejecuta el archivo principal (por ejemplo, tu_archivo.py).

Haz clic en "Cargar archivo" y selecciona el audio que quieras procesar.

Elige el tipo de filtro que deseas aplicar.

Ajusta la frecuencia de corte (entre 20 Hz y 20000 Hz) y el orden del filtro (entre 1 y 10).

Presiona "Aplicar Filtro" para ver el resultado.

Los botones de reproducción te permiten escuchar tanto el audio original como el filtrado. Si no te convence el resultado, puedes presionar "Resetear" para volver a la señal original.

¿Qué muestran las gráficas?
Gráfica superior: La forma de onda del audio en función del tiempo.

Gráficas inferiores:

A la izquierda, se muestra la FFT del audio original.

A la derecha, la FFT del audio tras aplicar el filtro, para que puedas observar las diferencias en el contenido de frecuencias.

Guardar tu trabajo
Cuando estés conforme con el procesamiento, puedes guardar el audio filtrado en formato WAV usando el botón "Guardar Resultado".

Detalles visuales
La señal original se muestra en azul.

Los filtros se distinguen por colores:

Pasa-bajas: Rojo

Pasa-altas: Verde

Pasa-banda: Morado

Consideraciones
Si el audio es muy largo, la carga puede demorar un poco.

Los archivos temporales se eliminan automáticamente al cerrar la aplicación.

Si experimentas problemas con el botón de reseteo, espera unos instantes entre reproducciones.



Autor
Andrés Martínez Sánchez
A01656442
