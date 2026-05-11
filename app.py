import streamlit as st
from streamlit_mic_recorder import mic_recorder
from streamlit_js_eval import get_geolocation
from groq import Groq
import io

# ═══════════════════════════════════════════════════════════════
# إعدادات الصفحة - غيرناها لـ wide عشان تظهر أحسن
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Giza Smart Assistant | مساعد الجيزة الذكي",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════
# CSS القوي - يضمن ظهور الشات بشكل صحيح
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');

* {
    font-family: 'Cairo', sans-serif !important;
}

/* توجيه الصفحة */
html, body, .stApp {
    direction: rtl;
    background: linear-gradient(135deg, #f0f4f8 0%, #e8eef5 100%);
}

/* إخفاء العناصر غير المرغوب فيها */
#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"] { 
    display: none !important; 
}

/* الهيدر الجميل */
.giza-header {
    background: linear-gradient(135deg, #0a2342 0%, #1a4a7a 60%, #2e7fc1 100%);
    padding: 20px 25px;
    border-radius: 0 0 30px 30px;
    margin: -1rem -1rem 1rem -1rem;
    text-align: center;
    box-shadow: 0 6px 25px rgba(10,35,66,0.3);
}
.giza-header h1 {
    color: #f0c85a;
    font-size: 1.8rem;
    font-weight: 900;
    margin: 0;
}
.giza-header p {
    color: rgba(255,255,255,0.8);
    font-size: 0.9rem;
    margin: 8px 0 0 0;
}

/* الأزرار */
div.stButton > button {
    background: linear-gradient(135deg, #0a2342, #1a4a7a);
    color: white;
    border-radius: 30px;
    padding: 0.6rem 1.2rem;
    font-weight: bold;
    border: 1px solid #c9a84c;
    transition: all 0.3s ease;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #c9a84c, #f0c85a);
    color: #0a2342;
    border-color: white;
    transform: translateY(-2px);
}

/* التابات - أزرار منزلقة */
.tabs-container {
    display: flex;
    gap: 10px;
    overflow-x: auto;
    padding: 15px 5px 10px;
    scrollbar-width: thin;
    direction: rtl;
    flex-wrap: wrap;
    justify-content: center;
}
.tab-button {
    background: white;
    border: 2px solid #dde3ec;
    border-radius: 35px;
    padding: 10px 20px;
    font-size: 0.9rem;
    font-weight: 700;
    color: #0a2342;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
}
.tab-button.active {
    background: #0a2342;
    border-color: #c9a84c;
    color: #f0c85a;
    box-shadow: 0 4px 12px rgba(10,35,66,0.25);
}

/* رسائل الشات */
[data-testid="stChatMessage"] {
    direction: rtl;
    margin-bottom: 15px;
}
[data-testid="stChatMessageContent"] {
    direction: rtl;
    text-align: right;
    border-radius: 20px !important;
    font-size: 0.95rem;
    line-height: 1.7;
    padding: 12px 16px !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: white !important;
    border: 1px solid #e0e7f0;
    box-shadow: 0 2px 10px rgba(10,35,66,0.08);
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #0a2342, #1a4a7a) !important;
    color: white !important;
}

/* صندوق الإدخال */
.stChatInputContainer {
    direction: rtl;
}
.stChatInputContainer input {
    border-radius: 30px !important;
    border: 2px solid #c9a84c !important;
    padding: 12px 20px !important;
    font-size: 1rem !important;
}

/* رسائل النجاح */
div[data-testid="stAlert"] {
    border-radius: 15px;
    direction: rtl;
}

/* تباعد */
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# البيانات (نفسها موجودة)
# ═══════════════════════════════════════════════════════════════
HOSPITALS = [
    {"name": "مستشفى العجوزة العام", "lat": 30.0520, "lng": 31.2130},
    {"name": "مستشفى الهرم العام", "lat": 29.9950, "lng": 31.1550},
    {"name": "مستشفى أم المصريين", "lat": 30.0050, "lng": 31.2150},
    {"name": "مستشفى الشيخ زايد التخصصي", "lat": 30.0450, "lng": 30.9950},
    {"name": "مستشفى الجيزة العام", "lat": 30.0131, "lng": 31.2089},
]

# ═══════════════════════════════════════════════════════════════
# System Prompt المتكامل (عربي + إنجليزي)
# ═══════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """You are Giza, official AI assistant for Giza Governorate, Egypt.

⚠️ CRITICAL RULE: You MUST respond in the SAME LANGUAGE as the user.
- If user writes in Arabic → respond in Arabic
- If user writes in English → respond in English

Keep responses SHORT: 1-2 sentences maximum unless user asks for details.
Ask ONE question at a time.
Be friendly and helpful.

【Available info - use when relevant】
Hospitals in Giza: 
- Agouza General Hospital (30.0520, 31.2130)
- Haram General Hospital (29.9950, 31.1550)
- Om El-Masryeen Hospital (30.0050, 31.2150)
- Sheikh Zayed Specialized (30.0450, 30.9950)
- Giza General Hospital (30.0131, 31.2089)

For user location coordinates → provide Google Maps links:
- Hospitals: https://www.google.com/maps/search/hospital/@LAT,LNG,15z
- Restaurants: https://www.google.com/maps/search/restaurant/@LAT,LNG,15z
- Hotels: https://www.google.com/maps/search/hotel/@LAT,LNG,15z

For tourism: Ask how many days, then suggest:
1 day: Pyramids + Sphinx + Sound & Light show
2 days: + Grand Egyptian Museum (GEM)
3 days: + Orman Gardens + Nile trip

For digital services: Direct to https://digital.gov.eg

Remember conversation history naturally."""

# ═══════════════════════════════════════════════════════════════
# التابات (أزرار الخدمات السريعة)
# ═══════════════════════════════════════════════════════════════
QUICK_ACTIONS = [
    ("🏥", "مستشفيات | Hospitals", "أقرب مستشفى ليا | Nearest hospital to me"),
    ("🏛️", "سياحة | Tourism", "برنامج سياحي | Tourist program"),
    ("📈", "استثمار | Investment", "فرص استثمارية | Investment opportunities"),
    ("💻", "مصر الرقمية | Digital Egypt", "خدمات مصر الرقمية | Digital Egypt services"),
    ("🍽️", "مطاعم | Restaurants", "مطاعم قريبة | Restaurants near me"),
    ("🏨", "فنادق | Hotels", "فنادق في الجيزة | Hotels in Giza"),
]

# ═══════════════════════════════════════════════════════════════
# تهيئة Groq
# ═══════════════════════════════════════════════════════════════
@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# ═══════════════════════════════════════════════════════════════
# دوال مساعدة
# ═══════════════════════════════════════════════════════════════
def get_groq_response(messages):
    """إرسال الرسائل إلى Groq والحصول على الرد"""
    client = get_client()
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"عذراً | Sorry, an error occurred: {str(e)}"

# ═══════════════════════════════════════════════════════════════
# تهيئة حالة الجلسة
# ═══════════════════════════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "🏛️ أهلاً بك! Welcome!\n\nأنا **مساعد الجيزة الذكي** | I am **Giza Smart Assistant**\n\n✅ أتحدث العربية والإنجليزية | I speak Arabic & English\n✅ أساعدك في: استثمار، سياحة، خدمات حكومية، مطاعم، فنادق\n\n**اسألني أي شيء عن محافظة الجيزة** | **Ask me anything about Giza Governorate**"
    }]

if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None

if "location" not in st.session_state:
    st.session_state.location = None

# ═══════════════════════════════════════════════════════════════
# واجهة المستخدم
# ═══════════════════════════════════════════════════════════════

# الهيدر
st.markdown("""
<div class="giza-header">
    <h1>🏛️ مساعدك الذكي | Your Smart Assistant</h1>
    <p>محافظة الجيزة · استثمار · سياحة · خدمات حكومية | Giza · Investment · Tourism · Government Services</p>
</div>
""", unsafe_allow_html=True)

# صف الأزرار السريعة (التابات)
st.markdown('<div class="tabs-container">', unsafe_allow_html=True)
cols = st.columns(len(QUICK_ACTIONS))
for i, (icon, label, prompt_text) in enumerate(QUICK_ACTIONS):
    with cols[i]:
        if st.button(f"{icon} {label}", key=f"quick_{i}", use_container_width=True):
            # إضافة رسالة المستخدم
            st.session_state.messages.append({"role": "user", "content": prompt_text})
            # تحضير الرسائل لـ Groq
            groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in st.session_state.messages:
                groq_messages.append({"role": m["role"], "content": m["content"]})
            # الحصول على الرد
            reply = get_groq_response(groq_messages)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# خط فاصل
st.markdown("---")

# صف الموقع
loc_col1, loc_col2 = st.columns([4, 1])
with loc_col2:
    if st.button("📍 موقعي | My Location", use_container_width=True):
        loc = get_geolocation()
        if loc and "coords" in loc:
            st.session_state.location = {
                "lat": loc["coords"]["latitude"],
                "lng": loc["coords"]["longitude"]
            }
            st.rerun()
with loc_col1:
    if st.session_state.location:
        lat = st.session_state.location["lat"]
        lng = st.session_state.location["lng"]
        st.success(f"✅ موقعك محدد | Your location is set: {lat:.4f}, {lng:.4f}")
    else:
        st.info("📍 اضغط على الزر لتحديد موقعك | Click the button to set your location")

# عرض سجل المحادثة (الشات)
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# دالة إرسال الرسالة
def send_message(user_input):
    """إرسال رسالة المستخدم والحصول على رد المساعد"""
    # إضافة رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # تحضير الرسائل لإرسالها إلى Groq
    groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # إضافة الموقع إذا وجد
    full_user_input = user_input
    if st.session_state.location:
        lat = st.session_state.location["lat"]
        lng = st.session_state.location["lng"]
        full_user_input = f"{user_input}\n[User location: lat={lat}, lng={lng}]"
    
    # بناء قائمة الرسائل
    for i, m in enumerate(st.session_state.messages):
        if i == len(st.session_state.messages) - 1:
            groq_messages.append({"role": "user", "content": full_user_input})
        else:
            groq_messages.append({"role": m["role"], "content": m["content"]})
    
    # الحصول على الرد
    reply = get_groq_response(groq_messages)
    st.session_state.messages.append({"role": "assistant", "content": reply})

# حقل إدخال النص والميكروفون
input_col, mic_col = st.columns([6, 1])

with input_col:
    prompt = st.chat_input("✍️ اكتب سؤالك هنا | Type your question here...")

with mic_col:
    audio = mic_recorder(
        start_prompt="🎤",
        stop_prompt="⏹️",
        just_once=True,
        use_container_width=True,
        key="mic_recorder"
    )

# معالجة الإدخال النصي
if prompt:
    with st.spinner("🤔 جيزا بتفكر | Giza is thinking..."):
        send_message(prompt)
    st.rerun()

# معالجة الإدخال الصوتي
if audio and audio.get("bytes") and audio.get("id") != st.session_state.last_audio_id:
    st.session_state.last_audio_id = audio.get("id")
    with st.spinner("🎧 جيزا بتسمعك | Giza is listening..."):
        try:
            client = get_client()
            audio_bytes = io.BytesIO(audio["bytes"])
            audio_bytes.name = "audio.webm"
            
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_bytes,
                language="ar"
            )
            voice_text = transcription.text.strip()
            
            if voice_text:
                st.info(f"🎤 قلت | You said: {voice_text}")
                send_message(voice_text)
                st.rerun()
            else:
                st.warning("⚠️ لم يتم التعرف على كلام | No speech recognized")
        except Exception as e:
            st.error(f"❌ خطأ في الصوت | Audio error: {str(e)}")

# زر مسح المحادثة
if len(st.session_state.messages) > 1:
    if st.button("🗑️ مسح المحادثة | Clear Chat", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "🏛️ تم مسح المحادثة | Chat cleared!\n\nأنا هنا لمساعدتك من جديد | I'm here to help you again.\n\nاسألني أي شيء عن الجيزة | Ask me anything about Giza."
        }]
        st.session_state.last_audio_id = None
        st.rerun()
