import streamlit as st
import json
from google import genai

st.set_page_config(page_title="Generador de Ideas", page_icon="💡")
st.title("💡 Asistente de Ideas de Proyectos")

#pegar aca la clave api de google ia studio
API_KEY = "AIzaSyCr5TS2pg3ST4laBRQhjzFH2yxotuV4_UQ" 


# Configuración del cliente
client = genai.Client(api_key=API_KEY)


#le decimos al chatbot como debe de actuar 
system_instruction = """
Eres un Asistente de Ideación de Proyectos de Software.
Tu objetivo es generar ideas de proyectos basadas en los inputs del usuario.

REGLAS DE FORMATO (IMPORTANTE):
Tu respuesta DEBE ser siempre un objeto JSON válido con la siguiente estructura exacta:
{
    "principiante": {
        "titulo": "Título corto y atractivo",
        "descripcion": "Descripción detallada del proyecto..."
    },
    "intermedio": {
        "titulo": "Título corto y atractivo",
        "descripcion": "Descripción detallada del proyecto..."
    },
    "avanzado": {
        "titulo": "Título corto y atractivo",
        "descripcion": "Descripción detallada del proyecto..."
    }
}

REGLAS DE CONTENIDO:
1. Si el input es una tecnología o tema válido, genera el JSON con las 3 ideas.
2. Si el input NO tiene sentido (ej: "hola", "clima"), el JSON debe ser: {"error": "Solo puedo generar ideas de código. Por favor ingresa una tecnología."}
3. No incluyas bloques de código markdown (```json), solo el texto JSON crudo.
"""
def generar_codigo(proyecto):
    tecnologias = proyecto.get('tecnologias', ['General'])
    prompt_codigo = f"""
    Actúa como un experto programador senior.
    Genera el código base fundamental para el siguiente proyecto:
    
    TÍTULO: {proyecto['titulo']}
    DESCRIPCIÓN: {proyecto['descripcion']}
    STACK: {', '.join(tecnologias)}
    
    Instrucciones:
    1. Provee el código principal (ej: app.py, index.html).
    2. Usa comentarios para explicar las partes clave.
    """
    respuesta = st.session_state.chat_session.send_message(prompt_codigo)
    return respuesta.text



#configuracion del modeo a usar 
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=API_KEY)
    st.session_state.chat_session = st.session_state.client.chats.create(
        model="gemini-2.5-flash",
        config={"system_instruction": system_instruction}
    )
    #memoria del chat 
    st.session_state.messages = []



#mostrar el chat con streamlit
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    
#verificar y mostrar mensajes anteriores en caso de que se tocara un boton
if "current_ideas" in st.session_state: 
    st.divider()
    ideas = st.session_state.current_ideas
    def dibujar_idea(datos):
        with st.container(border=True):
            st.subheader(datos["titulo"])
            st.markdown(datos["descripcion"])
            st.caption(f"🛠️ Stack: {', '.join(datos.get('tecnologias', []))}")
        t1, t2, t3 = st.tabs(["🐣 Principiante", "🚀 Intermedio", "🔥 Avanzado"])
        with t1: dibujar_idea(ideas["principiante"])
        with t2: dibujar_idea(ideas["intermedio"])
        with t3: dibujar_idea(ideas["avanzado"])

if "codigo_generado" in st.session_state:
    st.write("---")
    st.success(f"👨‍💻 Código generado para: **{st.session_state.proyecto_actual}**")
    with st.expander("📜 Ver Código Completo", expanded=True):
        st.code(st.session_state.codigo_generado)
        
#permitir que el usuario pueda escrb¡ibir
if prompt := st.chat_input("Escribe una tecnología (ej: Java, SQL)..."):
    
    #limpiamos si quedo codigo generado anteriormente
    if "codigo_generado" in st.session_state:
        del st.session_state.codigo_generado
        
        
        
    # Guardar y mostrar lo que escribió el usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Llamar a Gemini y mostrar respuesta
    try:
        with st.spinner("💡 Pensando ideas"):
         response = st.session_state.chat_session.send_message(prompt)
        
         try: 
            
            
                ideas = json.loads(response.text)
                if "error" in ideas:
                 st.warning(["error"])
                 st.session_state.messages.append({"role": "assistant", "content": ideas["error"]})
                else:
                 tab1, tab2, tab3 = st.tabs(["🐣 Principiante", "🚀 Intermedio", "🔥 Avanzado"])
                 st.session_state.current_ideas = ideas
                with tab1:
                        with st.container(border=True):
                            st.subheader(ideas["principiante"]["titulo"])
                            st.markdown(ideas["principiante"]["descripcion"])
                with tab2:
                        with st.container(border=True):
                            st.subheader(ideas["intermedio"]["titulo"])
                            st.markdown(ideas["intermedio"]["descripcion"])
                with tab3:
                        with st.container(border=True):
                            st.subheader(ideas["avanzado"]["titulo"])
                            st.markdown(ideas["avanzado"]["descripcion"])
                
                resumen = f"**Ideas:** 🐣 {ideas['principiante']['titulo']} | 🚀 {ideas['intermedio']['titulo']} | 🔥 {ideas['avanzado']['titulo']}"
                st.session_state.messages.append({"role": "assistant", "content": resumen})
         except json.JSONDecodeError:
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
     st.error(f"Ocurrió un error: {e}")

# Barra lateral para limpiar el chat
with st.sidebar:
    st.header("Configuración")
    if st.button("🗑️ Borrar Historial"):
        st.session_state.messages = []
        st.session_state.chat_session = None # reinicia la sesion de gemini
        st.rerun() # recarga la pagina 
    
    if "current_ideas" in st.session_state:
        st.subheader("👨‍💻 Generar Código")
        nivel_seleccionado = st.selectbox(
            "Selecciona el proyecto:",
            ["principiante","intermedio","avanzado"],
            format_func = lambda x: x.capitalize()
        )
        
    if st.button("✨ Crear Código", type="primary", use_container_width=True):
            
            # A) Buscamos los datos completos de la idea seleccionada
            idea_elegida = st.session_state.current_ideas[nivel_seleccionado]
            
            with st.spinner(f"Programando {idea_elegida['titulo']}..."):
                # B) Llamamos a la función
                codigo = generar_codigo(idea_elegida)
                
                # C) Guardamos en memoria
                st.session_state.codigo_generado = codigo
                st.session_state.proyecto_actual = idea_elegida['titulo']
                
                # D) Recargamos para que aparezca en el centro
                st.rerun()
    


##le pide a gemini codigo base para empezar el proyecto 
