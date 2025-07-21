import streamlit as st
st.title('🚀 Intro')

st.markdown("""
# ¿No sabes qué ver?
Esta app te recomienda películas basadas en tus gustos usando técnicas de machine learning y datos reales de IMDb.

## ¿Cómo funciona esto?
**Procesamos todo IMDb**.

Tomamos el dataset completo de IMDb, combinamos variables numéricas y categóricas (como género, puntuación, votos, etc.) y lo reducimos a unas pocas dimensiones con PCA. Así, cada película se convierte en un punto en un espacio que resume sus características principales.

**Tú eliges tus favoritas**.

Solo tienes que escoger 5 películas que te gusten. Estas se usarán como referencia para encontrar recomendaciones similares.

**Buscamos películas parecidas**.

Para cada una de tus elecciones, encontramos las 10 más cercanas usando un algoritmo llamado KNN (básicamente, busca las más parecidas en el espacio PCA). En total, juntamos 55 películas candidatas.

**Creamos 3 "mixes" de recomendaciones**.

Con esas 55 películas, usamos KMeans para agruparlas en 3 clústeres. Cada grupo tiene su propio estilo, así que puedes explorar distintas combinaciones según tu mood.

""")
