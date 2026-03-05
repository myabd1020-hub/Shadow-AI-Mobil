def call_gemini_api(prompt, chat_mode=True):
    """الاتصال بـ Gemini API - نسخة مصححة"""
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return "⚠️ مفتاح API غير موجود. يرجى التحقق من الإعدادات."
    
    # تحضير المحادثة - تنسيق صحيح 100%
    contents = []
    
    # رسالة النظام (تذهب في مكان منفصل)
    system_instruction = st.session_state.messages[0]["parts"][0]
    
    if chat_mode and len(st.session_state.messages) > 1:
        # إضافة آخر 5 محادثات (وليس 10)
        start_idx = max(1, len(st.session_state.messages) - 5)
        for msg in st.session_state.messages[start_idx:]:
            if msg["role"] == "user":
                contents.append({
                    "role": "user",
                    "parts": [{"text": msg["parts"][0]}]
                })
            elif msg["role"] == "model":
                contents.append({
                    "role": "model", 
                    "parts": [{"text": msg["parts"][0]}]
                })
    
    # إضافة الرسالة الحالية
    contents.append({
        "role": "user",
        "parts": [{"text": prompt}]
    })
    
    # تجهيز الطلب بالتنسيق الصحيح
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    # البيانات بالتنسيق المطلوب من Google
    data = {
        "contents": contents,
        "system_instruction": {
            "parts": [{"text": system_instruction}]
        },
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
            "topP": 0.95,
            "topK": 40
        },
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
    }
    
    try:
        add_to_terminal("جاري الاتصال بـ Gemini API...", "info")
        
        # طباعة الطلب للتشخيص (يمكن إزالتها بعد التأكد)
        st.write("Debug: إرسال الطلب...")
        
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(data),
            timeout=30
        )
        
        # تشخيص الخطأ
        if response.status_code != 200:
            st.write(f"Debug: Status Code: {response.status_code}")
            st.write(f"Debug: Response: {response.text[:500]}")
        
        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0]["text"]
                    add_to_terminal("تم استلام الرد بنجاح", "success")
                    return text
                else:
                    return f"⚠️ تنسيق رد غير متوقع: {str(result)[:200]}"
            else:
                return "⚠️ لا يوجد رد من API"
        else:
            error_msg = f"خطأ {response.status_code}"
            try:
                error_json = response.json()
                if "error" in error_json:
                    error_msg += f": {error_json['error'].get('message', '')}"
            except:
                error_msg += f": {response.text[:200]}"
            
            add_to_terminal(error_msg, "error")
            return f"⚠️ {error_msg}"
            
    except Exception as e:
        add_to_terminal(f"استثناء: {str(e)}", "error")
        return f"⚠️ خطأ: {str(e)[:200]}"
