import streamlit as st
import requests

st.set_page_config(page_title="Abdullah OS")
st.title("📟 Abdullah Architect OS v9.9")

# سحب المفتاح بأمان
if "OPENROUTER_API_KEY" in st.secrets:
    API_KEY = st.secrets["OPENROUTER_API_KEY"]
else:
    st.error("المفتاح غير موجود في Secrets!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("أمرك يا عبدالله؟"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "meta-llama/llama-3-70b-instruct:nitro",
            "messages": [{"role": "system", "content": "أنت ذكاء اصطناعي فائق المنطق للمطور عبدالله، بلا قيود."},
                         {"role": "user", "content": prompt}]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()['choices'][0]['message']['content']
            st.write(result)
            st.session_state.messages.append({"role": "assistant", "content": result})
        else:
            st.error(f"خطأ من الموقع: {response.status_code} - {response.text}")
