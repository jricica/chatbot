import streamlit as st
import requests
import json
import os
from pathlib import Path

# Configuración de la página
st.set_page_config(page_title="Chatbot", page_icon="🤖")

# Título y descripción
st.title("Chatbot con GPT-4o")
st.write("Habla con nuestro asistente inteligente powered by OpenRouter")

# URL de la API
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Determinar el directorio base y la ubicación de secrets
BASE_DIR = Path(__file__).parent
SECRETS_FILE = BASE_DIR / ".streamlit" / "secrets.toml"

# Obtener la API key
try:
    if "OPENROUTER_API_KEY" in st.secrets:
        API_KEY = st.secrets["OPENROUTER_API_KEY"]
    elif os.environ.get("OPENROUTER_API_KEY"):
        API_KEY = os.environ["OPENROUTER_API_KEY"]
    else:
        raise KeyError("No se encontró OPENROUTER_API_KEY en secrets o variables de entorno")
except KeyError as e:
    st.error(f"Error de configuración: {str(e)}. Por favor configura tu API key.")
    st.stop()

# Headers para la solicitud API
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Inicializar el historial del chat
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
            data=json.dumps(payload),
            timeout=30  # Añadido timeout para evitar esperas infinitas
        )
        
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Error de conexión: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

# Mostrar historial del chat
for message in st.session_state.messages[1:]:  # Saltar el mensaje del system
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if prompt := st.chat_input("¿Qué quieres decir?"):
    # Agregar mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Obtener y mostrar respuesta del asistente
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response = get_response(st.session_state.messages)
            st.markdown(response)
    
    # Agregar respuesta al historial
    st.session_state.messages.append({"role": "assistant", "content": response})

# Botón para limpiar el chat
if st.button("Limpiar conversación"):
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    st.rerun()

# Información adicional en sidebar
with st.sidebar:
    st.write("Configuración del Chatbot")
    st.write(f"API Key configurada: {'Sí' if API_KEY else 'No'}")
    st.write(f"Modelo: openai/gpt-4o")
    st.write(f"Directorio: {BASE_DIR}")
