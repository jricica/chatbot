import streamlit as st
import requests
import json

# Configuración de la página
st.set_page_config(page_title="Chatbot", page_icon="🤖")

# Título y descripción
st.title("Chatbot con GPT-4o")
st.write("Habla con nuestro asistente inteligente powered by OpenRouter")

# URL de la API
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Obtener la API key desde los secrets
API_KEY = st.secrets["OPENROUTER_API_KEY"]
# Headers para la solicitud API
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Inicializar el historial del chat en la sesión
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# Función para obtener respuesta del modelo
def get_response(messages):
    try:
        payload = {
            "model": "openai/gpt-4o",
            "messages": messages
        }
        
        response = requests.post(
            API_URL,
            headers=HEADERS,
            data=json.dumps(payload)
        )
        
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"

# Mostrar historial del chat
for message in st.session_state.messages[1:]:  # Saltar el mensaje del system
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Input del usuario
if prompt := st.chat_input("¿Qué quieres decir?"):
    # Agregar mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.write(prompt)
    
    # Obtener y mostrar respuesta del asistente
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response = get_response(st.session_state.messages)
            st.write(response)
    
    # Agregar respuesta al historial
    st.session_state.messages.append({"role": "assistant", "content": response})

# Botón para limpiar el chat
if st.button("Limpiar conversación"):
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    st.rerun()
