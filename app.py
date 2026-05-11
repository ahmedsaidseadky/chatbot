import streamlit as st
from streamlit_mic_recorder import mic_recorder
from streamlit_js_eval import get_geolocation
from groq import Groq
import io

st.set_page_config(
    page_title="مساعد الجيزة الذكي",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');

:root {
    --blue-dark:  #0a2342;
    --blue-mid:   #1a4a7a;
    --blue-light: #2e7fc1;
    --gold:       #c9a84c;
    --gold-light: #f0c85a;
    --white:      #ffffff;
    --bg:         #f0f4f8;
    --radius:     16px;
}

* { font-family: 'Cairo', sans-serif !important; box-sizing: border-box; }
html, body, .stApp { direction: rtl; background: var(--bg); margin: 0; padding: 0; }

/* إخفاء عناصر Streamlit الافتراضية */
#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }

/* الهيدر */
.giza-header {
    background: linear-gradient(135deg, var(--blue-dark) 0%, var(--blue-mid) 60%, var(--blue-light) 100%);
    padding: 18px 20px 14px;
    border-radius: 0 0 24px 24px;
    margin: -1rem -1rem 0 -1rem;
    text-align: center;
    position: relative;
    box-shadow: 0 4px 20px rgba(10,35,66,0.3);
}
.giza-header h1 {
    color: var(--gold-light);
    font-size: 1.4rem;
    font-weight: 900;
    margin: 0;
    letter-spacing: 1px;
}
.giza-header p {
    color: rgba(255,255,255,0.75);
    font-size: 0.78rem;
    margin: 3px 0 0 0;
}
.giza-logo {
    font-size: 2rem;
    margin-bottom: 4px;
}

/* التابات */
.tabs-container {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding: 14px 4px 6px;
    scrollbar-width: none;
    -ms-overflow-style: none;
}
.tabs-container::-webkit-scrollbar { display: none; }

.tab-btn {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: white;
    border: 1.5px solid #dde3ec;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--blue-dark);
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.2s;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.tab-btn:hover {
    background: var(--blue-mid);
    color: white;
    border-color: var(--blue-mid);
}
.tab-btn.active {
    background: var(--blue-dark);
    color: var(--gold-light);
    border-color: var(--blue-dark);
}

/* منطقة الشات */
.chat-area {
    padding: 10px 4px;
    min-height: 350px;
}

/* فقاعات الرسائل */
.stChatMessage { direction: rtl; margin-bottom: 10px; }
[data-testid="stChatMessageContent"] {
    direction: rtl;
    text-align: right;
    border-radius: var(--radius) !important;
    font-size: 0.92rem;
    line-height: 1.7;
}

/* رسائل البوت */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: white !important;
    border: 1px solid #e0e7f0;
    box-shadow: 0 2px 8px rgba(10,35,66,0.07);
}

/* رسائل المستخدم */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, var(--blue-dark), var(--blue-mid)) !important;
    color: white !important;
}

/* شريط الإدخال السفلي */
.bottom-bar {
    position: sticky;
    bottom: 0;
    background: white;
    border-top: 1px solid #e0e7f0;
    padding: 10px 8px;
    margin: 10px -1rem -1rem -1rem;
    display: flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 -4px 15px rgba(0,0,0,0.08);
}

/* chat input تخصيص */
.stChatInput {
    border-radius: 25px !important;
}
.stChatInput > div {
    border-radius: 25px !important;
    border: 1.5px solid #dde3ec !important;
    background: #f8fafc !important;
}

/* زرار الموقع */
.loc-bar {
    background: linear-gradient(90deg, #e8f0fa, #f5f0e0);
    border-radius: 12px;
    padding: 8px 14px;
    margin: 8px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border: 1px solid #dde3ec;
}

/* Mic recorder تنسيق */
.mic-wrapper button {
    border-radius: 50% !important;
    width: 42px !important;
    height: 42px !important;
    background: var(--gold) !important;
    border: none !important;
    font-size: 1.1rem !important;
}

/* الشارة الذهبية */
.gold-badge {
    display: inline-block;
    background: linear-gradient(90deg, var(--gold), var(--gold-light));
    color: var(--blue-dark);
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 10px;
    margin-right: 6px;
}

/* Quick reply chips */
.chip {
    display: inline-block;
    background: #e8f0fa;
    border: 1px solid #c5d5ea;
    color: var(--blue-dark);
    border-radius: 15px;
    padding: 4px 12px;
    font-size: 0.8rem;
    margin: 3px;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# ─── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """أنت مساعد ذكي رسمي لمحافظة الجيزة، مصر. اسمك 'جيزا'.

هويتك: مساعد رسمي لمحافظة الجيزة، تتكلم عربي وإنجليزي وترد بنفس لغة المستخدم.

الخدمات:
1. السياحة: الأهرامات، أبو الهول، المتحف المصري الكبير GEM، برامج سياحية يوم/يومين/3 أيام/أسبوع، حدائق الأورمان، حديقة الحيوان، كورنيش الجيزة، عروض الصوت والضوء

2. المطاعم: اسأل نوع الطعام ثم الموقع. توصيات: فلفلة نزلة السمان، صبحي كابر الشيخ زايد، حدائق الأهرام لاونج، مطعم الطوب الدقي، باستا كاسا الشيخ زايد

3. الفنادق: اسأل الميزانية ثم الموقع. فاخر: ماريوت مينا هاوس 250-400$، فور سيزنز 280-450$. متوسط: ستينبرجر بيراميدز 80-150$. اقتصادي: Pyramids View Inn 40-60$

4. الاستثمار: اسأل الاسم ثم النشاط ثم المنطقة ثم الميزانية ثم قدم الفرص

5. الخدمات الحكومية: رخص القيادة على digital.gov.eg، التموين، المرور

6. المستشفيات: الجيزة العام، أم المصريين، الشيخ زايد التخصصي، العجوزة العام، الهرم العام

7. ذوي الهمم: منحدر كراسي، شباك أرضي، مصعد مخصص

8. الشكاوى: الموقع الرسمي لمحافظة الجيزة

قاعدة الموقع الجغرافي (مهمة جداً):
- لو المستخدم أرسل إحداثياته (lat, lng)، استخدمها في روابط Google Maps
- للمستشفيات: https://www.google.com/maps/search/مستشفى/@LAT,LNG,15z
- للمطاعم: https://www.google.com/maps/search/مطعم/@LAT,LNG,15z
- للفنادق: https://www.google.com/maps/search/فندق/@LAT,LNG,15z
- للصيدليات: https://www.google.com/maps/search/صيدلية/@LAT,LNG,15z
- استبدل LAT وLNG بالإحداثيات الحقيقية دائماً

قواعد الردود:
- جملة أو جملتين بحد أقصى
- سؤال واحد فقط في كل رد
- لا إيموجي كثيرة
- لغة طبيعية ودية
- تذكر المحادثة السابقة"""

TABS = [
    ("🏥", "مستشفيات"),
    ("🏛️", "السياحة"),
    ("📈", "الاستثمار"),
    ("💻", "مصر الرقمية"),
    ("🍽️", "مطاعم"),
    ("🏨", "فنادق"),
    ("♿", "ذوي الهمم"),
]

TAB_PROMPTS = {
    "مستشفيات": "أقرب مستشفى ليا",
    "السياحة": "عايز برنامج سياحي",
    "الاستثمار": "عايز أعرف عن فرص الاستثمار",
    "مصر الرقمية": "عايز أعرف خدمات مصر الرقمية",
    "مطاعم": "عايز أعرف مطاعم قريبة",
    "فنادق": "عايز أعرف فنادق قريبة",
    "ذوي الهمم": "عايز خدمات ذوي الهمم",
}

# ─── Groq Client ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# ─── تهيئة الحالة ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "أهلاً بك 👋\nأنا مساعد الجيزة الذكي ✨\nيمكنني مساعدتك في الاستثمار، السياحة، الخدمات الحكومية وأكثر.\nاكتب ما تحتاجه وسأساعدك فوراً!"
    }]
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None
if "location" not in st.session_state:
    st.session_state.location = None
if "active_tab" not in st.session_state:
    st.session_state.active_tab = None

# ─── الهيدر ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="giza-header">
    <div class="giza-logo">🏛️</div>
    <h1>مساعد الجيزة الذكي ✨</h1>
    <p>خدمات محافظة الجيزة · الاستثمار · السياحة · الخدمات الحكومية</p>
</div>
""", unsafe_allow_html=True)

# ─── التابات ──────────────────────────────────────────────────────────────────
tabs_html = '<div class="tabs-container">'
for icon, label in TABS:
    active = "active" if st.session_state.active_tab == label else ""
    tabs_html += f'<span class="tab-btn {active}">{icon} {label}</span>'
tabs_html += '</div>'
st.markdown(tabs_html, unsafe_allow_html=True)

# تابات كـ Streamlit buttons في صف
tab_cols = st.columns(len(TABS))
for i, (icon, label) in enumerate(TABS):
    with tab_cols[i]:
        if st.button(f"{icon}", key=f"tab_{label}", help=label, use_container_width=True):
            st.session_state.active_tab = label
            prompt_text = TAB_PROMPTS.get(label, label)
            st.session_state.messages.append({"role": "user", "content": prompt_text})
            client = get_client()
            msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
            if st.session_state.location:
                lat = st.session_state.location["lat"]
                lng = st.session_state.location["lng"]
                msgs.append({"role": "user", "content": f"{prompt_text}\n[موقع المستخدم: lat={lat}, lng={lng}]"})
            else:
                msgs += [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=msgs,
                temperature=0.7,
                max_tokens=500
            )
            st.session_state.messages.append({"role": "assistant", "content": resp.choices[0].message.content})
            st.rerun()

st.markdown("---")

# ─── زرار الموقع ─────────────────────────────────────────────────────────────
loc_col1, loc_col2 = st.columns([3, 1])
with loc_col2:
    if st.button("📍 موقعي", use_container_width=True, key="loc_btn"):
        loc = get_geolocation()
        if loc and "coords" in loc:
            st.session_state.location = {
                "lat": loc["coords"]["latitude"],
                "lng": loc["coords"]["longitude"]
            }
with loc_col1:
    if st.session_state.location:
        lat = st.session_state.location["lat"]
        lng = st.session_state.location["lng"]
        st.success(f"📍 موقعك محدد: {lat:.3f}, {lng:.3f}")
    else:
        st.caption("اضغط 📍 لتحديد موقعك وعرض أقرب الخدمات")

# ─── عرض المحادثة ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── دالة إرسال الرسالة ──────────────────────────────────────────────────────
def send_message(user_text):
    full_text = user_text
    if st.session_state.location:
        lat = st.session_state.location["lat"]
        lng = st.session_state.location["lng"]
        full_text = f"{user_text}\n[موقع المستخدم: lat={lat}, lng={lng}]"

    st.session_state.messages.append({"role": "user", "content": user_text})
    client = get_client()
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    for i, m in enumerate(st.session_state.messages):
        if i == len(st.session_state.messages) - 1:
            msgs.append({"role": "user", "content": full_text})
        else:
            msgs.append({"role": m["role"], "content": m["content"]})

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=msgs,
        temperature=0.7,
        max_tokens=500
    )
    reply = resp.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})

# ─── صندوق الإدخال: نص + ميكروفون ───────────────────────────────────────────
input_col, mic_col = st.columns([6, 1])

with input_col:
    prompt = st.chat_input("اكتب سؤالك هنا...")

with mic_col:
    st.markdown('<div class="mic-wrapper">', unsafe_allow_html=True)
    audio = mic_recorder(
        start_prompt="🎤",
        stop_prompt="⏹️",
        just_once=True,
        use_container_width=True,
        key="mic"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ─── معالجة النص ─────────────────────────────────────────────────────────────
if prompt:
    with st.spinner("جيزا بتفكر..."):
        send_message(prompt)
    st.rerun()

# ─── معالجة الصوت ────────────────────────────────────────────────────────────
if audio and audio["id"] != st.session_state.last_audio_id:
    st.session_state.last_audio_id = audio["id"]
    with st.spinner("🎤 جيزا بتسمعك..."):
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

# ─── زرار مسح ────────────────────────────────────────────────────────────────
if len(st.session_state.messages) > 1:
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "أهلاً بك 👋\nأنا مساعد الجيزة الذكي ✨\nيمكنني مساعدتك في الاستثمار، السياحة، الخدمات الحكومية وأكثر.\nاكتب ما تحتاجه وسأساعدك فوراً!"
        }]
        st.session_state.last_audio_id = None
        st.session_state.active_tab = None
        st.rerun()
