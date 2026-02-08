import streamlit as st
import json
from google import genai

st.set_page_config(page_title="Generador de Ideas", page_icon="💡")
st.title("💡 Asistente de Ideas de Proyectos")

#pegar aca la clave api de google ia studio
API_KEY = "AIzaSyDlKSpknyjc8Y1K-FlDo7q3l0pd3DCStDg" 


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
            
            with st.spinner("pensando ideas"):
                ideas = json.loads(response.text)
                if "error" in ideas:
                 st.warning(["error"])
                 st.session_state.messages.append({"role": "assistant", "content": ideas["error"]})
                else:
                 tab1, tab2, tab3 = st.tabs(["🐣 Principiante", "🚀 Intermedio", "🔥 Avanzado"])
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
    
    


##le pide a gemini codigo base para empezar el proyecto 
def generar_codigo(proyecto):
    prompt_codigo = f"""
    Actúa como un experto programador senior.
    Genera el código base fundamental para el siguiente proyecto:
    
    TÍTULO: {proyecto['titulo']}
    DESCRIPCIÓN: {proyecto['descripcion']}
    STACK: {', '.join(proyecto['tecnologias'])}
    
    Instrucciones:
    1. Provee el código principal (ej: app.py, index.html, script.js según corresponda).
    2. Usa comentarios para explicar las partes clave.
    3. Si requiere instalación, indica los comandos brevemente al inicio.
    """
    respuesta = st.session_state.chat_session.send_message(prompt_codigo)
    return respuesta 

