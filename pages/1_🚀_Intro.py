import streamlit as st
st.title('🚀 Intro')

st.markdown("""
# 🎬 Sist de Recomendación de Películas + Agente SQL

Este proyecto es una aplicación interactiva construida con **Streamlit** que combina un sistema de recomendación de películas con un agente inteligente capaz de responder preguntas en lenguaje natural sobre una base de datos de películas (IMDB).

---

## 🧠 Tecnologías y Enfoque

### 1. Sistema de Recomendación
Basado en técnicas de **aprendizaje no supervisado (Unsupervised Learning)**, el sistema permite al usuario seleccionar películas que le gustan y, en función de esas elecciones, genera recomendaciones personalizadas.

#### 🔍 Reducción de Dimensiones con PCA
Se utiliza **PCA (Análisis de Componentes Principales)** para:
- Reducir la dimensionalidad de los datos numéricos.
- Identificar patrones y relaciones ocultas entre las películas.
- Mejorar la eficiencia y visualización de los datos.

#### 🤝 Recomendación con KNN
Se emplea el algoritmo **K-Nearest Neighbors** para:
- Encontrar las películas más similares a las seleccionadas por el usuario.
- Generar una lista final de recomendaciones relevantes.

#### 🎯 Agrupamiento con KMeans
Las películas recomendadas se agrupan en **3 clústeres distintos** con **KMeans**, permitiendo mostrar diferentes "mixes" de recomendaciones

---

### 2. Agente SQL Inteligente
Incluye un **SQL Agent** impulsado por un modelo de lenguaje (LLM), que permite:
- Escribir preguntas en lenguaje natural sobre las películas.
- El modelo interpreta la pregunta, genera la consulta SQL correspondiente y devuelve los resultados en tiempo real.
- Ejemplo:
  _"¿Cuáles son las películas mejor valoradas del año 2000?"_ → genera y ejecuta una consulta SQL automáticamente.

---

## 🛠️ Tecnologías Utilizadas

- 🐍 Python
- 📊 Pandas, Scikit-learn
- 🌐 Streamlit
- 🧠 Modelos LLM (DeepSeek)
- 🗃️ SQL
- 📁 Base de datos IMDB

link a loom:
https://www.loom.com/share/5d1590c5e42e42e0af96482116f71fc9?sid=a7fe899b-968e-4ba8-9cfc-7327c687ad9c
""")
