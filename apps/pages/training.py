import time
import streamlit as st
from uuid import uuid4
import json


st.set_page_config(
    page_title="Cecilia - The Cuban Language Model", page_icon="logo.png", layout="wide"
)


if not st.session_state.get("accepted_terms", False):
    with open("apps/training_instructions.md", "r") as f:
        st.markdown(f.read())

    st.info(
        """A continuación le solicitamos sus datos personales e información de contacto,
            exclusivamente con el propósito de evaluar y validar la relevancia y correctitud
            de los ejemplos de entrenamiento que usted proporcione. En ningún caso sus datos
            personales serán usadon como parte del entrenamiento ni compartidos con terceros."""
    )

    cols = st.columns(3)

    name = cols[0].text_input("Nombre y apellidos")
    institution = cols[1].text_input("Institución")
    email = cols[2].text_input("Correo electrónico")

    t1 = st.checkbox("He leído y entendido las instrucciones anteriores.")
    t2 = st.checkbox(
        "Acepto que los ejemplos de entrenamiento proporcionados por mi serán utilizados para entrenar el modelo."
    )
    t3 = st.checkbox(
        "Entiendo que no debo proporcionar datos en ningún ejemplo de entrenamiento que puedan identificar a niguna persona."
    )

    if not name or not institution or not email:
        st.stop()

    if t1 and t2 and t3 and st.button("Continuar", type="primary"):
        st.session_state.accepted_terms = True
        st.session_state.contact_info = dict(
            name=name,
            institution=institution,
            email=email,
        )
        st.rerun()

    st.stop()


if not "training_example" in st.session_state:
    st.session_state.training_example = []

left, right = st.columns([2, 1])

with left:
    st.info(
        "Utilice la caja de texto para construir un ejemplo de entrenamiento para Cecilia. Comenzará con el rol de usuario, y luego podrá responder como asistente. Asegúrese de seleccionar las etiquetas relevantes. Una vez que haya terminado, haga clic en el botón **Enviar ejemplo actual** para enviar el ejemplo."
    )

    for message in st.session_state.training_example:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    def on_conversation_control():
        control = st.session_state.conversation_controls

        match control:
            case "Borrar último":
                st.session_state.training_example.pop()
            case "Borrar todo":
                st.session_state.training_example.clear()

        st.session_state.conversation_controls = None

    if st.session_state.training_example:
        st.segmented_control(
            "Controles de conversación",
            ["Borrar último", "Borrar todo"],
            label_visibility="collapsed",
            key="conversation_controls",
            on_change=on_conversation_control,
        )

    current_role = (
        "user" if len(st.session_state.training_example) % 2 == 0 else "assistant"
    )

    match current_role:
        case "user":
            placeholder = "Escriba el mensaje del usuario"
        case "assistant":
            placeholder = "Escriba la respuesta del asistente"

    if prompt := st.chat_input(placeholder, key="training_input"):
        st.session_state.training_example.append(
            {"role": current_role, "content": prompt}
        )
        st.rerun()


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
            "arte",
            "ciencia",
            "cultura",
            "deporte",
            "economía",
            "historia",
            "política",
            "salud",
            "casual",
            "otros",
        ],
        key="tags",
        selection_mode="multi",
        help="Seleccione una o más etiquetas según el contexto o dominio de la conversación.",
    )

    context = st.text_area(
        "Contexto adicional (opcional)",
        placeholder="Información adicional para verificar la información factual del ejemplo.",
        key="context",
        help="Puede incluir texto libre, referencias bibliográficas, y/o links a recursos donde verificar la factualidad de la conversación, en caso de ser necesario.",
    )

    if st.button(
        "Enviar ejemplo actual",
        type="primary",
        use_container_width=True,
        disabled=(
            len(st.session_state.training_example) < 2
            or len(st.session_state.training_example) % 2 == 1
            or len(tags) == 0
        ),
        help="Aségurese de tener al menos un mensaje de cada rol (usuario y asistente), y haber seleccionado al menos un tag.",
    ):

        message_id = str(uuid4())
        data = dict(
            id=message_id,
            contact_info=st.session_state.contact_info,
            example_type=example_type,
            tags=tags,
            context=context,
            created_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            messages=st.session_state.training_example,
        )

        with open(f"data/instructions/submitted/{message_id}.json", "a") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        st.session_state.training_example.clear()
        st.toast("Ejemplo enviado correctamente.", icon="✅")
        time.sleep(1)
        st.rerun()
