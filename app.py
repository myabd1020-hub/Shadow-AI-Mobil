import streamlit as st
import requests

st.set_page_config(page_title="Abdullah OS", page_icon="💀")
st.title("📟 Abdullah Architect OS v9.9")

# التأكد من وجود المفتاح
if "OPENROUTER_API_KEY" in st.secrets:
    api_key = st.secrets["OPENROUTER_API_KEY"]
else:
    st.error("⚠️ خطأ: المفتاح (API Key) غير موجود في الإعدادات!")
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
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://streamlit.io", # مطلوب أحياناً من OpenRouter
        }
        data = {
            "model": "meta-llama/llama-3-70b-instruct:nitro",
            "messages": [
                {"role": "system", "content": "أنت ذكاء اصطناعي فائق المنطق للمطور عبدالله. أجب بذكاء برمج حاد."},
                {"role": "user", "content": prompt}
            ]
        }
        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content']
                st.write(result)
                st.session_state.messages.append({"role": "assistant", "content": result})
            else:
                st.error(f"خطأ من الموقع ({response.status_code}): {response.text}")
        except Exception as e:
            st.error(f"فشل في الاتصال: {e}")
