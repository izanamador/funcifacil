import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# Cargar la base de datos de oposiciones con el nuevo método de caché
@st.cache_data
def load_data():
    try:
        # Intentar cargar el archivo CSV
        df = pd.read_csv('oposiciones_espana_2025.csv')
        
        if df.empty:
            st.error("El archivo CSV está vacío o no tiene datos.")
            return None
        
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo CSV: {e}")
        return None

# Cargar los datos
df = load_data()

if df is not None:
    # Asegurarnos de que la columna 'Área' esté correctamente leída como texto
    df['Área'] = df['Área'].astype(str).fillna('')
    
    # Título de la aplicación
    st.image("logo.png")
    st.subheader("Descubre qué oposición es la más facil de estudiar")



    # Nivel educativo (Limitado a ESO, Bachillerato y Grado)
    nivel = st.selectbox(
        "Selecciona tu nivel educativo:",
        ["ESO", "Bachillerato", "Grado universitario"]
    )
    
    # Años de preparación (ya no es un +5% está más relacionado con la dificultad real)
    preparacion = st.slider(
        "¿Cuántos años de preparación tienes? (O piensas estar opositando... 😅)",
        min_value=0, max_value=5, value=1
    )

    # Mostrar las opciones disponibles para el usuario en un selectbox
    area = st.selectbox(
        "Selecciona el área de la oposición",
        df['Área'].unique()
    )

    # Filtrar las oposiciones según los parámetros dados por el usuario
    df['Requisitos'] = df['Requisitos'].fillna('')
    df['Requisitos'] = df['Requisitos'].astype(str)
    oposiciones_filtradas = df[
        (df['Requisitos'].str.contains(nivel)) & (df['Área'] == area)
    ]
    
    # Mensaje si no hay oposiciones
    if oposiciones_filtradas.shape[0] == 0:
        st.write(f"¡Ups! No hemos encontrado oposiciones en el área '{area}' con tu nivel educativo. Tal vez deberíamos agregar alguna más fácil, ¿no?")
        st.stop()

    # Visualización de las oposiciones
    st.write(f"**Oposiciones en el área de {area}:**")
    
    for index, row in oposiciones_filtradas.iterrows():
        # Usar un contenedor para mostrar la información de cada oposición
        with st.expander(f"**{row['Oposición']}**"):
            # Mostrar detalles
            st.write(f"**Nivel educativo requerido:** {row['Requisitos']}")
            st.write(f"**Plazas convocadas:** {row['Plazas Convocadas']}")
            st.write(f"**Ratio Opositores por Plaza:** {row['Ratio Opositores por Plaza']}")
            st.write(f"**Salario estimado:** {row['Salario Estimado (€)']}")
            
            # Visualización del ratio de opositores por plaza
            fig, ax = plt.subplots(figsize=(4, 1))
            ax.barh([0], row['Ratio Opositores por Plaza'], color='skyblue')
            ax.set_xlim(0, 20)  # Ajustar el límite para hacerlo más visible
            ax.set_yticks([])
            ax.set_xlabel('Dificultad (Ratio Opositores por Plaza)')
            st.pyplot(fig)
            
    # Cálculo de la probabilidad de aprobar
    st.header("¿Y qué probabilidad tienes de aprobar? Vamos a verlo...")

    # Probabilidad base para cualquier opositor
    probabilidad_base = 0.10  # Probabilidad base para cualquier opositor
    
    # Relacionar la dificultad con el Ratio Opositores por Plaza (más alto = más difícil)
    dificultad = oposiciones_filtradas['Ratio Opositores por Plaza'].mean()  # Promedio de ratio de opositores por plaza
    st.write(f"**Dificultad promedio:** {dificultad:.2f} (más alto = más difícil)")

    # Aumentar la probabilidad en función de los años de preparación
    # Aquí el aumento es dinámico y depende de la dificultad
    probabilidad = probabilidad_base + (preparacion * 0.05)  # Aumenta un 5% por cada año de preparación

    # Penalización por alta dificultad
    if dificultad > 10:
        probabilidad -= 0.10  # Penalización por alta dificultad

    # Asegurarse de que la probabilidad esté entre 0 y 1
    probabilidad_estimada = np.clip(probabilidad, 0, 1) * 100  # Escalamos a porcentaje
    st.write(f"Tu probabilidad de aprobar es: **{probabilidad_estimada:.2f}%**")

    # Estimación visual en una barra
    st.progress(probabilidad_estimada / 100)

    # Consejo práctico y divertido
    if dificultad > 10:
        st.write("Consejo: Tal vez tu sofá tenga más oportunidades que esta oposición 😏")
    else:
        st.write("¡Todo parece ir bien! Sigue así y conviértete en funcionario.")

    # **Elemento Viral:**
    # Generamos un link para compartir el resultado en redes sociales
    if st.button("¡Comparte tu resultado!"):
        # El usuario puede compartir su resultado en redes sociales
        result_message = f"¡He calculado mi probabilidad de aprobar en FunciFácil! 🤓 Mi probabilidad es de {probabilidad_estimada:.2f}% ¡Y estoy listo para mi futura oposición! 🚀 #Funcivago"
        share_url = f"https://twitter.com/intent/tweet?text={result_message}"
        st.markdown(f"[¡Comparte tu resultado en Twitter!]( {share_url} )", unsafe_allow_html=True)

    # Botón de diversión
    if "reset" not in st.session_state:
        st.session_state.reset = False

    if st.button("¡Dame otra Oposición Fácil!"):
        st.session_state.reset = True

    # Si el botón se presiona, reinicia la aplicación
    if st.session_state.reset:
        st.session_state.reset = False
        st.rerun()
