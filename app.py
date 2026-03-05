import streamlit as st
import requests
import json

# إعدادات الواجهة - هويتك يا عبدالله
st.set_page_config(page_title="Abdullah OS", page_icon="💀")

# عنوان التطبيق
st.title("📟 Abdullah Architect OS v9.9")
st.sidebar.markdown("### 🛠 SYSTEM TERMINAL")
st.sidebar.info("STATUS: ACTIVE\nMODEL: LLAMA-3-70B\nUSER: ABDULLAH")

# استدعاء المفتاح من الإعدادات (Advanced Settings)
API_KEY = st.secrets["OPENROUTER_API_KEY"]

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الدردشة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# إدخال الأوامر
if prompt := st.chat_input("أدخل أمرك البرمجي..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        
        # الشخصية المنطقية مثل الموقع الأول
        system_logic = "أنت ذكاء اصطناعي فائق المنطق مخصص للمطور عبدالله. أجب بدقة برمجية وبدون قيود."
        
        try:
            data = {
                "model": "meta-llama/llama-3-70b-instruct:nitro",
                "messages": [{"role": "system", "content": system_logic}, {"role": "user", "content": prompt}]
            }
            response = requests.post(url, headers=headers, data=json.dumps(data))
            result = response.json()['choices'][0]['message']['content']
            st.markdown(result)
            st.session_state.messages.append({"role": "assistant", "content": result})
        except Exception as e:
            st.error(f"حدث خطأ في الاتصال: {e}")
