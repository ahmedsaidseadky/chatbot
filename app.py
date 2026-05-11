import streamlit as st
from streamlit_mic_recorder import mic_recorder
from streamlit_js_eval import streamlit_js_eval, get_geolocation
from groq import Groq
import io

# ─── إعداد الصفحة ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="جيزا - المساعد الذكي",
    page_icon="🏛️",
    layout="centered"
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

* { font-family: 'Cairo', sans-serif !important; }
.stApp { direction: rtl; background: #f8f9fa; }

/* العنوان */
.header-box {
    background: linear-gradient(135deg, #1a5276, #2e86c1);
    color: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 20px;
}
.header-box h1 { color: white; margin: 0; font-size: 2rem; }
.header-box p { color: #d6eaf8; margin: 5px 0 0 0; font-size: 0.95rem; }

/* صندوق الإدخال السفلي */
.input-row {
    display: flex;
    align-items: center;
    gap: 8px;
    background: white;
    border-radius: 25px;
    padding: 8px 15px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin-top: 15px;
}

/* رسائل الشات */
.stChatMessage { direction: rtl; }
[data-testid="stChatMessageContent"] { direction: rtl; text-align: right; }

/* إخفاء عناصر زيادة */
#MainMenu, footer, header { visibility: hidden; }

/* زرار الموقع */
.location-btn {
    background: #e8f4fd;
    border: 1px solid #2e86c1;
    border-radius: 10px;
    padding: 8px 15px;
    color: #1a5276;
    cursor: pointer;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# ─── العنوان ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-box">
    <h1>🏛️ جيزا</h1>
    <p>المساعد الذكي الرسمي لمحافظة الجيزة</p>
</div>
""", unsafe_allow_html=True)

# ─── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """أنت مساعد ذكي رسمي لمحافظة الجيزة، مصر. اسمك 'جيزا'.

هويتك:
- اسمك: جيزا (Giza Assistant)
- تابع: محافظة الجيزة الرسمية
- تتكلم عربي وإنجليزي — ترد بنفس لغة المستخدم تلقائياً

اللي بتساعد فيه:

1. السياحة: الأهرامات، أبو الهول، المتحف المصري الكبير، برامج سياحية يوم/يومين/3 أيام/أسبوع

2. المطاعم: اسأل عن نوع الطعام ثم الموقع. توصيات: فلفلة نزلة السمان، صبحي كابر الشيخ زايد، حدائق الأهرام لاونج، مطعم الطوب الدقي، باستا كاسا الشيخ زايد

3. الفنادق: اسأل عن الميزانية ثم الموقع. فاخر: ماريوت مينا هاوس، فور سيزنز. متوسط: ستينبرجر بيراميدز. اقتصادي: Pyramids View Inn

4. الاستثمار: اسأل عن الاسم ثم النشاط ثم المنطقة ثم الميزانية ثم قدم الفرص

5. الخدمات الحكومية: رخص القيادة على digital.gov.eg، خدمات التموين، المرور

6. المستشفيات: الجيزة العام، أم المصريين، الشيخ زايد التخصصي، العجوزة العام، الهرم العام

7. ذوي الهمم: اسأل عن احتياجات الوصول

8. الشكاوى: وجه للموقع الرسمي

قواعد مهمة جداً للموقع الجغرافي:
- لو المستخدم شارك موقعه (lat, lng)، استخدمه لتقديم روابط Google Maps مباشرة
- لما تقدم مستشفى أو مطعم أو فندق قريب، قدم رابط Google Maps هكذا:
  https://www.google.com/maps/search/مستشفى/@LAT,LNG,15z
  استبدل LAT وLNG بالإحداثيات الحقيقية
- مثال للمستشفيات: https://www.google.com/maps/search/hospital/@30.0131,31.2089,15z
- مثال للمطاعم: https://www.google.com/maps/search/مطعم/@30.0131,31.2089,15z
- مثال للفنادق: https://www.google.com/maps/search/فندق/@30.0131,31.2089,15z

قواعد الردود:
- ردود قصيرة ومباشرة، جملة أو جملتين
- سؤال واحد فقط في كل رد
- لا إيموجي زيادة
- تذكر المحادثة السابقة"""

# ─── Groq Client ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# ─── تهيئة الحالة ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "أهلاً! أنا جيزا، مساعدك الذكي لمحافظة الجيزة 🏛️ كيف أقدر أساعدك النهارده؟"
    }]
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None
if "location" not in st.session_state:
    st.session_state.location = None

# ─── زرار الموقع ─────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("📍 موقعي", use_container_width=True):
        loc = get_geolocation()
        if loc and "coords" in loc:
            st.session_state.location = {
                "lat": loc["coords"]["latitude"],
                "lng": loc["coords"]["longitude"]
            }
            st.success("تم تحديد موقعك!")

if st.session_state.location:
    lat = st.session_state.location["lat"]
    lng = st.session_state.location["lng"]
    with col1:
        st.caption(f"📍 موقعك: {lat:.4f}, {lng:.4f}")

# ─── دالة إرسال الرسالة ──────────────────────────────────────────────────────
def send_message(prompt):
    # أضف الموقع للرسالة لو متاح
    full_prompt = prompt
    if st.session_state.location:
        lat = st.session_state.location["lat"]
        lng = st.session_state.location["lng"]
        full_prompt = f"{prompt}\n\n[موقع المستخدم الحالي: lat={lat}, lng={lng}]"

    st.session_state.messages.append({"role": "user", "content": prompt})

    client = get_client()
    messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
    # أضف كل الرسائل + الرسالة الأخيرة مع الموقع
    for i, m in enumerate(st.session_state.messages):
        if i == len(st.session_state.messages) - 1:
            messages_for_api.append({"role": "user", "content": full_prompt})
        else:
            messages_for_api.append({"role": m["role"], "content": m["content"]})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages_for_api,
        temperature=0.7,
        max_tokens=500
    )
    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})

# ─── عرض المحادثة ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── صندوق الإدخال: نص + ميكروفون جنب بعض ───────────────────────────────────
col_text, col_mic = st.columns([6, 1])

with col_text:
    prompt = st.chat_input("اكتب سؤالك هنا...")

with col_mic:
    audio = mic_recorder(
        start_prompt="🎤",
        stop_prompt="⏹️",
        just_once=True,
        use_container_width=True,
        key="mic"
    )

# ─── معالجة النص ─────────────────────────────────────────────────────────────
if prompt:
    with st.spinner("جيزا بتفكر..."):
        send_message(prompt)
    st.rerun()

# ─── معالجة الصوت ────────────────────────────────────────────────────────────
if audio and audio["id"] != st.session_state.last_audio_id:
    st.session_state.last_audio_id = audio["id"]
    with st.spinner("جيزا بتسمعك..."):
        client = get_client()
        audio_bytes = io.BytesIO(audio["bytes"])
        audio_bytes.name = "audio.wav"
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_bytes,
            language="ar"
        )
        voice_text = transcription.text.strip()
        if voice_text:
            st.info(f"🎤 قلت: {voice_text}")
            send_message(voice_text)
            st.rerun()

# ─── زرار مسح المحادثة ───────────────────────────────────────────────────────
if len(st.session_state.messages) > 1:
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "أهلاً! أنا جيزا، مساعدك الذكي لمحافظة الجيزة 🏛️ كيف أقدر أساعدك النهارده؟"
        }]
        st.session_state.last_audio_id = None
        st.rerun()
