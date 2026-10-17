import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="EnterpriseOpsAssistant",
    page_icon="🤖",
)

st.title("🤖 EnterpriseOpsAssistant")
st.caption("Your AI assistant for billing, accounts, and support.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages in this browser session.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about an invoice, subscription, or issue..."):
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
                    json={"question": prompt},
                    timeout=120,
                )
                response.raise_for_status()
                data = response.json()
                answer = data["answer"]
            except requests.RequestException as exc:
                answer = f"Couldn't reach the API: {exc}"

            st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )