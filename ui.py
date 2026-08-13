import os
import streamlit as st
import httpx

st.set_page_config(page_title="MATCHA Client Portal", page_icon="🎮", layout="wide")
st.title("🎮 MATCHA Platform Interface")
API_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1/recommend")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
chat_column, monitor_column = st.columns(2)
with chat_column:
    st.subheader("Conversational Gateway")
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_query = st.chat_input("Ask for a game recommendation...")
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            try:
                response = httpx.post(API_URL, json={"user_id": "global_user_session", "prompt": user_query}, timeout=30.0)
                if response.status_code == 200:
                    res_data = response.json()
                    st.session_state["last_debug_payload"] = res_data

                    if res_data.get("status") == "SUCCESS":
                        game = res_data["data"]
                        reply = f"### Try **{game['game_title']}**!\n\n{game['explanation']}\n\n*Platforms: {', '.join(game['platforms'])}*"
                    elif res_data.get("status") == "SAFETY_VIOLATION":
                        reply = "⚠️ **Blocked:** Request flagged by alignment guardrails."
                    else:
                        reply = "ℹ️ No matches found."

                    st.markdown(reply)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error connecting to backend: {e}")
with monitor_column:
    st.subheader("🛠️ Telemetry logs")
    if "last_debug_payload" in st.session_state:
        st.json(st.session_state["last_debug_payload"])
    else:
        st.write("Submit a request to stream agent diagnostics.")
