import time
import streamlit as st
from uuid import uuid4
import json


st.set_page_config(
    page_title="Cecilia - The Cuban Language Model", page_icon="logo.png", layout="wide"
)
st.logo("logo.png", size="large")


st.markdown("## Entrenamiento de Cecilia")


if not st.session_state.get("accepted_terms", False):
    with open("apps/training_instructions.md", "r") as f:
        st.markdown(f.read())

    t1 = st.checkbox("He leído y entendido las instrucciones anteriores.")
    t2 = st.checkbox(
        "Acepto que los datos proporcionados por mi serán utilizados para entrenar el modelo."
    )
    t3 = st.checkbox(
        "Entiendo que no debo proporcionar datos que puedan identificar a niguna persona."
    )

    if t1 and t2 and t3 and st.button("Continuar"):
        st.session_state.accepted_terms = True
        st.rerun()

    st.stop()


st.info(
    "Utilice la caja de texto para construir un ejemplo de entrenamiento para Cecilia. Comenzará con el rol de usuario, y luego podrá responder como asistente. Una vez que haya terminado, haga clic en el botón **Enviar** para enviar el ejemplo."
)


if not "training_example" in st.session_state:
    st.session_state.training_example = []

left, right = st.columns([3, 1])

with left:
    for message in st.session_state.training_example:
        with st.chat_message(message["role"]):
            st.write(message["content"])

with right:
    example_type = st.selectbox(
        "Tipo de ejemplo",
        ["Pregunta", "Instrucción", "Conversación"],
        index=0,
        key="example_type",
    )
    tags = st.pills(
        "Etiquetas",
        [
            "cultura",
            "salud",
            "ciencia",
            "arte",
            "historia",
            "política",
            "economía",
            "coloquial",
            "otros",
        ],
        key="tags",
        selection_mode="multi",
    )

    if st.session_state.training_example and st.button("Borrar último mensaje"):
        st.session_state.training_example.pop()
        st.rerun()

    if st.session_state.training_example and st.button("Borrar todo"):
        st.session_state.training_example.clear()
        st.rerun()

    if (
        len(st.session_state.training_example) >= 2
        and len(st.session_state.training_example) % 2 == 0
        and st.button("Enviar ejemplo de entrenamiento")
    ):

        message_id = str(uuid4())
        data = dict(
            id=message_id,
            example_type=example_type,
            tags=tags,
            messages=st.session_state.training_example,
        )

        with open(f"data/instructions/submitted/{message_id}.json", "a") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        st.session_state.training_example.clear()
        st.toast("Ejemplo de entrenamiento enviado correctamente.", icon="✅")
        time.sleep(2)
        st.rerun()


current_role = (
    "user" if len(st.session_state.training_example) % 2 == 0 else "assistant"
)

if prompt := st.chat_input(
    current_role.capitalize() + " (escriba su mensaje aquí)", key="training_input"
):
    st.session_state.training_example.append({"role": current_role, "content": prompt})
    st.rerun()
