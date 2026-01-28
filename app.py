import streamlit as st
from google import genai

st.set_page_config(page_title="Generador de Ideas", page_icon="💡")
st.title("💡 Asistente de Ideas de Proyectos")

#pegar aca la clave api de google ia studio
API_KEY = "" 


# Configuración del cliente
client = genai.Client(api_key=API_KEY)


#le decimos al chatbot como debe de actuar 
system_instruction = """
Eres un Asistente de Ideación de Proyectos de Software. 
Tu único objetivo es generar ideas de proyectos de programación basadas en los inputs del usuario.

REGLAS OBLIGATORIAS:
1. Si el usuario ingresa una tecnología (ej: "Python", "React") o un tema (ej: "Animales", "Finanzas"), debes responder con 3 ideas de proyectos: Nivel Principiante, Intermedio y Avanzado.
2. Si el usuario intenta hablar de otra cosa (clima, saludos, filosofía u otros), DEBES rechazar responder y decir: "Solo puedo generar ideas de proyectos. ¿Qué tecnología te interesa?".
3. No des explicaciones largas, ve directo a las ideas. Usa formato Markdown limpio.
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
    
    # Guardar y mostrar lo que escribió el usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Llamar a Gemini y mostrar respuesta
    try:
        response = st.session_state.chat_session.send_message(prompt)
        
        with st.chat_message("assistant"):
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
    
    