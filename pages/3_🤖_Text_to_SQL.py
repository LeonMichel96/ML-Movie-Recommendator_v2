import streamlit as st
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login  # Para autenticación si es necesario
from utils.connect_db import return_df, connect_to_db, load_sql_query

# Configuración del modelo
model_id = "deepseek-ai/deepseek-coder-1.3b-instruct"

# Función para limpiar el output y solo regresar consulta SQL
def clean_sql_output(sql: str) -> str:
    """Extrae solo el SQL ejecutable"""
    # Elimina todo antes del primer SELECT/INSERT/UPDATE/DELETE
    sql = re.sub(r'^.*?(?=SELECT|INSERT|UPDATE|DELETE|WITH)', '', sql, flags=re.IGNORECASE | re.DOTALL)

    # Elimina todo después del último punto y coma
    sql = re.sub(r';.*$', ';', sql, flags=re.DOTALL)

    # Elimina comentarios SQL (-- o /* */)
    sql = re.sub(r'--.*?$|/\*.*?\*/', '', sql, flags=re.DOTALL | re.MULTILINE)

    return sql.strip()

# Función que descarga modelo y lo cachea
@st.cache_resource
def cargar_modelo():
    try:

        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        return tokenizer, model
    except Exception as e:
        st.error(f"Error al cargar el modelo: {str(e)}")
        return None, None

with st.spinner("Cargando modelo..."):
    tokenizer, model = cargar_modelo()
    if tokenizer is None or model is None:
        st.stop()

# Función para generar SQL
def pregunta_a_sql(pregunta: str) -> str:
    if not pregunta.strip():
        return None

    system_prompt = """Eres un experto en SQL. Genera consultas SQL válidas para este esquema de películas:

    Esquema completo:
    TABLE public.crew (
      title_id character varying NOT NULL,
      name_id character varying NOT NULL,
      CONSTRAINT crew_pkey PRIMARY KEY (title_id, name_id),
      CONSTRAINT crew_title_id_fkey FOREIGN KEY (title_id) REFERENCES public.titles(title_id),
      CONSTRAINT crew_name_id_fkey FOREIGN KEY (name_id) REFERENCES public.names(name_id)
    )
    TABLE public.genres (
      genre_name character varying NOT NULL,
      CONSTRAINT genres_pkey PRIMARY KEY (genre_name)
    )
    TABLE public.names (
      name_id character varying NOT NULL,
      primaryname character varying NOT NULL,
      birthyear integer,
      CONSTRAINT names_pkey PRIMARY KEY (name_id)
    )
    TABLE public.ratings (
      title_id character varying NOT NULL,
      averagerating double precision NOT NULL,
      numvotes integer NOT NULL,
      CONSTRAINT ratings_pkey PRIMARY KEY (title_id),
      CONSTRAINT ratings_title_id_fkey FOREIGN KEY (title_id) REFERENCES public.titles(title_id)
    )
    TABLE public.titles (
      title_id character varying NOT NULL,
      titletype character varying NOT NULL,
      primarytitle character varying NOT NULL,
      isadult integer,
      startyear integer,
      runtimeminutes integer,
      CONSTRAINT titles_pkey PRIMARY KEY (title_id)
    )
    TABLE public.titles_genres (
      title_id character varying NOT NULL,
      genre_name character varying NOT NULL,
      CONSTRAINT titles_genres_pkey PRIMARY KEY (title_id, genre_name),
      CONSTRAINT titles_genres_title_id_fkey FOREIGN KEY (title_id) REFERENCES public.titles(title_id),
      CONSTRAINT titles_genres_genre_name_fkey FOREIGN KEY (genre_name) REFERENCES public.genres(genre_name)
    )
    Reglas estrictas:
    1. SOLO devuelve la consulta SQL pura
    2. Nunca incluyas ```sql o marcas similares
    3. Siempre termina con punto y coma
    4. Usa JOINs explícitos cuando relaciones tablas
    5. Incluye siempre el punto y coma final
    6. Usa nombres de columnas completos (tabla.columna)
    7. Mantén las consultas eficientes

    Ejemplo 1:
    Pregunta: "Películas de drama con mejor calificación"
    SQL:
    SELECT t.primarytitle, r.averagerating
    FROM public.titles t
    JOIN public.titles_genres tg ON t.title_id = tg.title_id
    JOIN public.ratings r ON t.title_id = r.title_id
    WHERE tg.genre_name = 'Drama'
    ORDER BY r.averagerating DESC
    LIMIT 10;

    Ejemplo 2:
    Pregunta: "Directores de películas posteriores a 2010"
    SQL:
    SELECT DISTINCT n.primaryname
    FROM public.crew c
    JOIN public.names n ON c.name_id = n.name_id
    JOIN public.titles t ON c.title_id = t.title_id
    WHERE t.startyear > 2010;
    """

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': pregunta}
    ]

    try:
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(model.device)

        outputs = model.generate(
            inputs,
            max_new_tokens=300,
            do_sample=False,
            top_k=50,
            top_p=0.95,
            temperature=0.3,
            eos_token_id=tokenizer.eos_token_id
        )

        # Decodificar y limpiar la salida
        sql = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)

        # Extraer solo el SQL (por si el modelo añade texto adicional)
        if "SQL:" in sql:
            sql = sql.split("SQL:")[-1].strip()

        # Asegurar formato correcto
        sql = sql.split(";")[0] + ";" if ";" in sql else sql
        return clean_sql_output(sql.strip())

    except Exception as e:
        st.error(f"Error durante la generación: {str(e)}")
        return None

## Página
st.title('🤖 SQL Query Agent')

with st.form('sql_form'):
    pregunta = st.text_area("Hazme una pregunta sobre películas 🎬",
                          placeholder="Ej: ¿Qué películas de acción tienen más de 2 horas de duración?",
                          height=100)
    submitted = st.form_submit_button("Generar SQL")

if submitted:
    if not pregunta.strip():
        st.warning("Por favor ingresa una pregunta válida")
    else:
        with st.spinner("Generando consulta SQL..."):
            sql = pregunta_a_sql(pregunta)

            if sql:
                st.subheader("Consulta generada:")
                st.code(sql, language="sql")

                connection = connect_to_db()
                base_df = return_df(sql,connection)
                st.dataframe(base_df)

            else:
                st.error("No se pudo generar la consulta. Intenta con otra pregunta.")
