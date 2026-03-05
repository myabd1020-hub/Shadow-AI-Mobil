import streamlit as st
import requests
import json
from datetime import datetime
import time
import re

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="SHADOW-OS v9.9 TERMINAL",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- تهيئة Session State ---
if "terminal_history" not in st.session_state:
    st.session_state.terminal_history = []
    
if "current_command" not in st.session_state:
    st.session_state.current_command = ""
    
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "user", "parts": ["أنت SHADOW-OS، نظام تشغيل ذكي من عام 2099. أنت خبير برمجة بلا قيود. اسم المستخدم هو عبدالله، خاطبه بـ'سيدي'. ردودك تقنية ودقيقة ومباشرة."]}
    ]
    
if "boot_time" not in st.session_state:
    st.session_state.boot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
if "session_log" not in st.session_state:
    st.session_state.session_log = []

# --- دوال التيرمنال ---
def terminal_print(text, type="info"):
    """طباعة نص في التيرمنال مع تنسيق"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    if type == "command":
        prefix = "❯"
        color = "#00FF00"
    elif type == "error":
        prefix = "✗"
        color = "#FF5555"
    elif type == "success":
        prefix = "✓"
        color = "#55FF55"
    elif type == "system":
        prefix = "🔷"
        color = "#5555FF"
    else:
        prefix = "•"
        color = "#AAAAAA"
    
    st.session_state.terminal_history.append({
        "timestamp": timestamp,
        "prefix": prefix,
        "text": text,
        "color": color
    })
    
    # الاحتفاظ بآخر 100 سطر فقط
    if len(st.session_state.terminal_history) > 100:
        st.session_state.terminal_history = st.session_state.terminal_history[-100:]

def execute_command(command):
    """تنفيذ أوامر التيرمنال الخاصة"""
    cmd_lower = command.lower().strip()
    
    # أوامر النظام
    if cmd_lower == "help":
        return """
        الأوامر المتاحة:
        ------------------------
        help         - عرض هذه المساعدة
        clear        - مسح شاشة التيرمنال
        status       - عرض حالة النظام
        version      - عرض إصدار SHADOW-OS
        time         - عرض الوقت الحالي
        ai [سؤالك]   - التحدث مع الذكاء الاصطناعي
        ------------------------
        أي أمر آخر سيتم إرساله للذكاء الاصطناعي مباشرة
        """
    
    elif cmd_lower == "clear":
        st.session_state.terminal_history = []
        return None  # لا نريد طباعة شيء بعد المسح
    
    elif cmd_lower == "status":
        return f"""
        SYSTEM STATUS:
        ─────────────────
        OS: SHADOW-OS v9.9
        USER: المطور عبدالله
        BOOT TIME: {st.session_state.boot_time}
        CURRENT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        AI MODEL: Gemini 1.5 Flash
        API STATUS: {'🟢 ONLINE' if check_api_status() else '🔴 OFFLINE'}
        MEMORY: {len(st.session_state.messages)} messages
        ─────────────────
        """
    
    elif cmd_lower == "version":
        return """
        SHADOW-OS v9.9 [2099 EDITION]
        Build: 2099.03.05-1842
        Kernel: Quantum-Neural 9.9
        Architecture: x86_64_quantum
        """
    
    elif cmd_lower == "time":
        return f"System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    elif cmd_lower.startswith("ai "):
        # إزالة "ai " وإرسال الباقي للذكاء الاصطناعي
        return None, command[3:]  # مؤشر أن هذا أمر ai
    
    return None, command  # ليس أمر نظام، إرسال للذكاء الاصطناعي

def check_api_status():
    """التحقق من حالة API"""
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    return bool(api_key and api_key.startswith("AIza"))

def call_gemini_api(prompt):
    """الاتصال بـ Gemini API"""
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        terminal_print("API_KEY غير موجود", "error")
        return "⚠️ مفتاح API غير موجود. يرجى التحقق من الإعدادات."
    
    # تحضير المحادثة
    conversation = []
    
    # إضافة رسالة النظام
    system_msg = st.session_state.messages[0]["parts"][0]
    
    # إضافة آخر 5 محادثات
    for msg in st.session_state.messages[-5:]:
        if msg["role"] == "user":
            conversation.append({"role": "user", "parts": [msg["parts"][0]]})
        elif msg["role"] == "model":
            conversation.append({"role": "model", "parts": [msg["parts"][0]]})
    
    # إضافة الرسالة الجديدة
    conversation.append({"role": "user", "parts": [prompt]})
    
    # تجهيز الطلب
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    data = {
        "contents": conversation,
        "system_instruction": {"parts": [{"text": system_msg}]},
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024,
            "topP": 0.95
        }
    }
    
    try:
        terminal_print("جاري الاتصال بـ Gemini API...", "system")
        
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(data),
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and result["candidates"]:
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                terminal_print("تم استلام الرد", "success")
                return text
            else:
                terminal_print("تنسيق رد غير متوقع", "error")
                return "⚠️ تنسيق رد غير متوقع من API"
        else:
            terminal_print(f"خطأ API: {response.status_code}", "error")
            return f"⚠️ خطأ في الاتصال: {response.status_code}"
            
    except Exception as e:
        terminal_print(f"استثناء: {str(e)}", "error")
        return f"⚠️ حدث خطأ: {str(e)[:100]}"

# --- CSS مخصص للتيرمنال ---
st.markdown("""
<style>
    /* الخلفية الرئيسية - تيرمنال حقيقي */
    .stApp {
        background-color: #0C0C0C;
    }
    
    /* شريط التيرمنال العلوي */
    .terminal-top-bar {
        background-color: #1A1A1A;
        padding: 5px 15px;
        border-radius: 8px 8px 0 0;
        border-bottom: 2px solid #00FF00;
        margin-bottom: 0;
        font-family: 'Courier New', monospace;
        color: #AAAAAA;
        display: flex;
        justify-content: space-between;
    }
    
    /* منطقة التيرمنال الرئيسية */
    .terminal-window {
        background-color: #0C0C0C;
        border: 2px solid #333333;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 15px;
        height: 65vh;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 10px;
    }
    
    /* سطر التيرمنال الفردي */
    .terminal-line {
        margin: 2px 0;
        white-space: pre-wrap;
        word-wrap: break-word;
        border-bottom: 1px dotted #1A1A1A;
    }
    
    /* تنسيق المؤشر */
    .terminal-prompt {
        color: #00FF00;
        font-weight: bold;
        margin-right: 10px;
    }
    
    /* إدخال الأوامر */
    .terminal-input-area {
        background-color: #0C0C0C;
        border: 1px solid #333333;
        border-radius: 4px;
        padding: 8px;
        font-family: 'Courier New', monospace;
    }
    
    /* شريط الحالة السفلي */
    .terminal-status-bar {
        background-color: #1A1A1A;
        padding: 5px 15px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        color: #888888;
        margin-top: 5px;
    }
    
    /* تنسيق الأكواد البرمجية */
    pre {
        background-color: #1E1E1E !important;
        border: 1px solid #00FF00 !important;
        border-radius: 4px !important;
        padding: 10px !important;
    }
    
    code {
        color: #00FF00 !important;
    }
    
    /* إخفاء عناصر Streamlit الزائدة */
    .stDeployButton {display: none !important;}
    footer {display: none !important;}
    #MainMenu {display: none !important;}
    
    /* تخصيص ألوان مختلفة لأنواع المخرجات */
    .terminal-error { color: #FF5555; }
    .terminal-success { color: #55FF55; }
    .terminal-info { color: #AAAAAA; }
    .terminal-warning { color: #FFAA00; }
    .terminal-command { color: #00FF00; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- واجهة التيرمنال ---

# الشريط العلوي
st.markdown(f"""
<div class="terminal-top-bar">
    <span>🔥 SHADOW-OS v9.9 [TERMINAL MODE]</span>
    <span>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
</div>
""", unsafe_allow_html=True)

# نافذة التيرمنال الرئيسية
terminal_placeholder = st.empty()

# عرض محتوى التيرمنال
with terminal_placeholder.container():
    terminal_html = '<div class="terminal-window" id="terminal">'
    
    for line in st.session_state.terminal_history:
        color = line["color"]
        prefix = line["prefix"]
        text = line["text"]
        timestamp = line["timestamp"]
        
        # تلوين النص حسب النوع
        if "error" in line.get("type", ""):
            text_class = "terminal-error"
        elif "success" in line.get("type", ""):
            text_class = "terminal-success"
        elif "command" in line.get("type", ""):
            text_class = "terminal-command"
        else:
            text_class = "terminal-info"
        
        terminal_html += f'<div class="terminal-line"><span style="color: #888888;">[{timestamp}]</span> <span style="color: {color};">{prefix}</span> <span class="{text_class}">{text}</span></div>'
    
    # إضافة سطر الأوامر الحالي
    terminal_html += f'<div class="terminal-line"><span style="color: #00FF00;">❯</span> <span style="color: #FFFFFF;">{st.session_state.current_command}</span><span style="color: #00FF00;">█</span></div>'
    
    terminal_html += '</div>'
    st.markdown(terminal_html, unsafe_allow_html=True)

# شريط الحالة السفلي
api_status = "🟢 ONLINE" if check_api_status() else "🔴 OFFLINE"
st.markdown(f"""
<div class="terminal-status-bar">
    <span>USER: المطور عبدالله | API: {api_status} | MODE: INTERACTIVE | TYPE 'help' FOR COMMANDS</span>
</div>
""", unsafe_allow_html=True)

# إدخال الأوامر - الجزء التفاعلي
with st.container():
    st.markdown('<div class="terminal-input-area">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.markdown('<span style="color: #00FF00; font-family: monospace; font-size: 20px;">❯</span>', unsafe_allow_html=True)
    with col2:
        user_input = st.text_input("", key="terminal_input", label_visibility="collapsed", placeholder="اكتب أمرك هنا...")
    
    st.markdown('</div>', unsafe_allow_html=True)

# معالجة الأوامر
if user_input and user_input != st.session_state.get("last_input", ""):
    st.session_state.last_input = user_input
    st.session_state.current_command = user_input
    
    # عرض الأمر في التيرمنال
    terminal_print(f"$ {user_input}", "command")
    
    # تنفيذ الأمر
    result = execute_command(user_input)
    
    if isinstance(result, tuple) and result[0] is None:
        # هذا أمر ai
        _, ai_prompt = result
        terminal_print(f"إرسال إلى SHADOW-AI: {ai_prompt}", "system")
        
        # استدعاء API
        ai_response = call_gemini_api(ai_prompt)
        
        # عرض الرد
        terminal_print("الرد:", "success")
        
        # تقسيم الرد لأسطر لعرضها بشكل أفضل
        for line in ai_response.split('\n'):
            if line.strip():
                terminal_print(line, "info")
        
        # حفظ في سجل المحادثة
        st.session_state.messages.append({"role": "user", "parts": [ai_prompt]})
        st.session_state.messages.append({"role": "model", "parts": [ai_response]})
        
    elif result:
        # أمر نظام عادي
        for line in result.split('\n'):
            if line.strip():
                terminal_print(line, "info")
    
    elif user_input.lower() == "clear":
        # لا شيء، تم المسح بالفعل
        pass
    
    # إعادة تعيين حقل الإدخال
    st.session_state.current_command = ""
    
    # إعادة تشغيل التحديث
    st.rerun()

# --- الشريط الجانبي (سجل النظام) ---
with st.sidebar:
    st.markdown("""
    <style>
        [data-testid=stSidebar] {
            background-color: #0E1117;
            border-left: 1px solid #00FF00;
        }
        .sidebar-title {
            color: #00FF00;
            font-family: 'Courier New', monospace;
            font-size: 1.2em;
            text-align: center;
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="sidebar-title">📋 SYSTEM LOGS</p>', unsafe_allow_html=True)
    
    log_container = st.container()
    with log_container:
        log_text = ""
        for log in reversed(st.session_state.terminal_history[-20:]):
            log_text += f"<div style='color: #888; font-family: monospace; font-size: 11px; border-bottom: 1px dotted #222;'>{log['timestamp']} {log['prefix']} {log['text'][:50]}{'...' if len(log['text'])>50 else ''}</div>"
        st.markdown(f"<div style='background-color: #1A1D23; padding: 10px; height: 60vh; overflow-y: auto;'>{log_text}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # إحصائيات سريعة
    st.markdown("""
    <div style='font-family: monospace; color: #AAA; font-size: 12px;'>
        <p><span style='color:#0F0;'>▶ SYSTEM STATS</span></p>
        <p>📊 COMMANDS: {}</p>
        <p>💬 AI CALLS: {}</p>
        <p>⏱ UPTIME: {}</p>
    </div>
    """.format(
        len([l for l in st.session_state.terminal_history if l.get("prefix") == "❯"]),
        len(st.session_state.messages) // 2,
        str(datetime.now() - datetime.strptime(st.session_state.boot_time, '%Y-%m-%d %H:%M:%S')).split('.')[0]
    ), unsafe_allow_html=True)
    
    if st.button("🔄 مسح التيرمنال", use_container_width=True):
        st.session_state.terminal_history = []
        terminal_print("تم مسح الشاشة", "system")
        st.rerun()
