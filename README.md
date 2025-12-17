# 🏃‍♀️ Monitor de Fatiga y Recuperación

Aplicación web desarrollada con **Streamlit** para analizar entrenamientos de running y evaluar niveles de **fatiga, carga y recuperación**, a partir de datos exportados desde plataformas como **Garmin Connect** o **Strava**.

---

## Objetivo del proyecto

Brindar una herramienta simple y visual que permita:

* Analizar la carga de entrenamiento a lo largo del tiempo
* Detectar posibles estados de fatiga acumulada
* Prevenir lesiones mediante métricas de control de carga
* Facilitar la toma de decisiones sobre descanso y recuperación

El proyecto está pensado como un **caso práctico de ciencia de datos aplicada al deporte**.

---

## ¿Qué hace la aplicación?

La app permite:

* 📊 Analizar entrenamientos de running a partir de un archivo CSV
* 📈 Calcular métricas de carga y fatiga (ATL / CTL / TSB)
* ⚠️ Evaluar riesgo de lesión mediante el ratio **ACWR (Agudo : Crónico)**
* ❤️ Analizar eficiencia cardíaca
* 🧠 Mostrar recomendaciones generales según los resultados

---

## Datos de entrada

La aplicación requiere un archivo **CSV** exportado desde Garmin Connect, Strava u otra plataforma similar, con al menos las siguientes columnas:

* Fecha
* Distancia
* TE aeróbico
* Frecuencia cardíaca media

> El archivo se procesa localmente en la sesión del usuario. No se almacenan datos.

---

## 🛠️ Tecnologías utilizadas

* Python
* Streamlit
* Pandas
* NumPy
* Matplotlib
* Seaborn
* Plotly

---

## Ejecución local

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/tu-usuario/monitor-fatiga.git
   cd monitor-fatiga
   ```

2. Crear un entorno virtual (opcional pero recomendado)

3. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Ejecutar la aplicación:

   ```bash
   streamlit run app.py
   ```

---

## Aplicación online

La app está desplegada públicamente en Streamlit Community Cloud:

👉 (https://monitor-fatiga-uwpnycxz2ezwkepdpft5ep.streamlit.app/)

---

## Estado del proyecto

Proyecto en desarrollo.
Próximas mejoras posibles:
...

---

## 👩‍💻 Autora

**Ayelén Bertorello**
Proyecto de ciencia de datos aplicado al análisis deportivo.

* GitHub: [https://github.com/ayelenbertorello](https://github.com/ayelenbertorello)
* LinkedIn: www.linkedin.com/in/ayelen-bertorello-8ab328268 

---


