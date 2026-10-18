
import requests
import streamlit as st
from uuid import uuid4

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="EnterpriseOpsAssistant",
    page_icon="🤖",
)

st.title("🤖 EnterpriseOpsAssistant")
st.caption("Your AI assistant for billing, accounts, and support.")

# Keep one conversation ID per browser session.
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Send a request only when the user submits a message.
if prompt := st.chat_input(
    "Ask about an invoice, subscription, or issue..."
):
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "question": prompt,
                        "thread_id": st.session_state.thread_id,
                    },
                    timeout=160,
                )
                response.raise_for_status()
                data = response.json()

                if data.get("pending_approval"):
                    answer = (
                        "Your refund request is pending "
                        "finance approval."
                    )
                    st.info(
                        "Pending approval — no refund "
                        "has been executed."
                    )
                else:
                    answer = data.get(
                        "answer",
                        "I couldn't generate a response.",
                    )

            except requests.RequestException as exc:
                answer = f"Couldn't reach the API: {exc}"

            st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
