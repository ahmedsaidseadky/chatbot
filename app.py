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
    --bg:         #f0f4f8;
    --radius:     16px;
}

* { font-family: 'Cairo', sans-serif !important; box-sizing: border-box; }
html, body, .stApp { direction: rtl; background: var(--bg); margin: 0; padding: 0; }
#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }

/* الهيدر */
.giza-header {
    background: linear-gradient(135deg, var(--blue-dark) 0%, var(--blue-mid) 60%, var(--blue-light) 100%);
    padding: 18px 20px 14px;
    border-radius: 0 0 24px 24px;
    margin: -1rem -1rem 0 -1rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(10,35,66,0.3);
}
.giza-header h1 { color: var(--gold-light); font-size: 1.4rem; font-weight: 900; margin: 0; }
.giza-header p  { color: rgba(255,255,255,0.75); font-size: 0.78rem; margin: 3px 0 0 0; }

/* التابات - إخفاء buttons الافتراضية */
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div > div > button {
    display: none !important;
}

/* تنسيق التابات المخصصة */
.tabs-scroll {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding: 12px 4px 8px;
    scrollbar-width: none;
    -ms-overflow-style: none;
    direction: rtl;
}
.tabs-scroll::-webkit-scrollbar { display: none; }

.tab-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    border-radius: 20px;
    padding: 7px 14px;
    font-size: 0.82rem;
    font-weight: 700;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.25s ease;
    border: 2px solid transparent;
    user-select: none;
}

.tab-pill.inactive {
    background: white;
    color: var(--blue-dark);
    border-color: #dde3ec;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.tab-pill.inactive:hover {
    background: #e8f0fa;
    border-color: var(--blue-light);
}

.tab-pill.active {
    background: var(--blue-dark);
    color: var(--gold-light);
    border-color: var(--gold);
    box-shadow: 0 3px 12px rgba(10,35,66,0.25);
}

/* رسائل الشات */
.stChatMessage { direction: rtl; margin-bottom: 10px; }
[data-testid="stChatMessageContent"] {
    direction: rtl; text-align: right;
    border-radius: var(--radius) !important;
    font-size: 0.92rem; line-height: 1.7;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: white !important;
    border: 1px solid #e0e7f0;
    box-shadow: 0 2px 8px rgba(10,35,66,0.07);
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, var(--blue-dark), var(--blue-mid)) !important;
    color: white !important;
}

/* زرار الموقع */
div[data-testid="stButton"] > button[kind="secondary"] {
    border-radius: 20px;
    border: 1.5px solid var(--blue-light);
    color: var(--blue-dark);
    font-weight: 700;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

# ─── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """أنت مساعد ذكي رسمي لمحافظة الجيزة، مصر. اسمك 'جيزا'.
تتكلم عربي وإنجليزي وترد بنفس لغة المستخدم.

الخدمات:
1. السياحة: الأهرامات، أبو الهول، المتحف المصري الكبير GEM، برامج سياحية يوم/يومين/3 أيام/أسبوع
2. المطاعم: اسأل نوع الطعام ثم الموقع. توصيات: فلفلة نزلة السمان، صبحي كابر، حدائق الأهرام لاونج، مطعم الطوب، باستا كاسا
3. الفنادق: اسأل الميزانية ثم الموقع. فاخر: ماريوت مينا هاوس، فور سيزنز. متوسط: ستينبرجر بيراميدز. اقتصادي: Pyramids View Inn
4. الاستثمار: اسأل الاسم ثم النشاط ثم المنطقة ثم الميزانية ثم قدم الفرص
5. الخدمات الحكومية: رخص القيادة على digital.gov.eg، التموين، المرور
6. المستشفيات: الجيزة العام، أم المصريين، الشيخ زايد التخصصي، العجوزة العام، الهرم العام
7. ذوي الهمم: منحدر كراسي، شباك أرضي، مصعد مخصص

قاعدة الموقع الجغرافي:
- لو المستخدم أرسل إحداثياته (lat, lng)، استخدمها في روابط Google Maps
- للمستشفيات: https://www.google.com/maps/search/مستشفى/@LAT,LNG,15z
- للمطاعم: https://www.google.com/maps/search/مطعم/@LAT,LNG,15z
- للفنادق: https://www.google.com/maps/search/فندق/@LAT,LNG,15z
- استبدل LAT وLNG بالإحداثيات الحقيقية

قواعد الردود:
- جملة أو جملتين بحد أقصى
- سؤال واحد فقط في كل رد
- لغة طبيعية ودية
- تذكر المحادثة السابقة"""

TABS = [
    ("🏥", "مستشفيات"),
    ("🏛️", "السياحة"),
    ("📈", "الاستثمار"),
    ("💻", "مصر الرقمية"),
    ("🍽️", "مطاعم قريبة"),
    ("🏨", "فنادق"),
    ("♿", "ذوي الهمم"),
]

TAB_PROMPTS = {
    "مستشفيات":     "أقرب مستشفى ليا",
    "السياحة":      "عايز برنامج سياحي",
    "الاستثمار":    "عايز أعرف فرص الاستثمار في الجيزة",
    "مصر الرقمية": "عايز أعرف خدمات مصر الرقمية",
    "مطاعم قريبة": "عايز مطاعم قريبة مني",
    "فنادق":        "عايز فنادق قريبة",
    "ذوي الهمم":   "عايز خدمات ذوي الهمم",
}

# ─── Groq ────────────────────────────────────────────────────────────────────
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
    <div style="font-size:2rem">🏛️</div>
    <h1>مساعدك الذكي ✨</h1>
    <p>محافظة الجيزة · استثمار · سياحة · خدمات حكومية</p>
</div>
""", unsafe_allow_html=True)

# ─── التابات بـ HTML + JS ─────────────────────────────────────────────────────
tabs_html = '<div class="tabs-scroll">'
for icon, label in TABS:
    css_class = "active" if st.session_state.active_tab == label else "inactive"
    tabs_html += f'''<div class="tab-pill {css_class}" onclick="
        window.parent.document.querySelectorAll('[data-tab-id]').forEach(b => b.click());
    ">{icon} {label}</div>'''
tabs_html += '</div>'
st.markdown(tabs_html, unsafe_allow_html=True)

# أزرار مخفية للتابات
tab_cols = st.columns(len(TABS))
for i, (icon, label) in enumerate(TABS):
    with tab_cols[i]:
        if st.button(label, key=f"tab_{label}", use_container_width=True):
            st.session_state.active_tab = label
            prompt_text = TAB_PROMPTS.get(label, label)

            full_prompt = prompt_text
            if st.session_state.location:
                lat = st.session_state.location["lat"]
                lng = st.session_state.location["lng"]
                full_prompt = f"{prompt_text}\n[موقع المستخدم: lat={lat}, lng={lng}]"

            st.session_state.messages.append({"role": "user", "content": prompt_text})
            client = get_client()
            msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
            for j, m in enumerate(st.session_state.messages):
                if j == len(st.session_state.messages) - 1:
                    msgs.append({"role": "user", "content": full_prompt})
                else:
                    msgs.append({"role": m["role"], "content": m["content"]})

            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=msgs,
                temperature=0.7,
                max_tokens=500
            )
            st.session_state.messages.append({"role": "assistant", "content": resp.choices[0].message.content})
            st.rerun()

# ─── التابات المرئية الحقيقية بـ Streamlit ───────────────────────────────────
# رسم التابات المرئية بناءً على الـ active_tab
active = st.session_state.active_tab
if active:
    icon_map = {label: icon for icon, label in TABS}
    icon = icon_map.get(active, "")
    st.markdown(f"""
    <div style="display:flex; gap:8px; overflow-x:auto; padding:12px 4px 8px; direction:rtl; scrollbar-width:none;">
        {''.join([
            f'<div class="tab-pill {"active" if label == active else "inactive"}">{ico} {label}</div>'
            for ico, label in TABS
        ])}
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─── زرار الموقع ─────────────────────────────────────────────────────────────
loc_col1, loc_col2 = st.columns([3, 1])
with loc_col2:
    if st.button("📍 موقعي", use_container_width=True):
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
        st.success(f"📍 موقعك محدد ✓")
    else:
        st.caption("📍 اضغط لتحديد موقعك وعرض أقرب الخدمات")

# ─── عرض المحادثة ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── دالة إرسال ──────────────────────────────────────────────────────────────
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
    st.session_state.messages.append({"role": "assistant", "content": resp.choices[0].message.content})

# ─── الإدخال: نص + ميكروفون ──────────────────────────────────────────────────
input_col, mic_col = st.columns([6, 1])
with input_col:
    prompt = st.chat_input("اكتب سؤالك هنا...")
with mic_col:
    audio = mic_recorder(
        start_prompt="🎤",
        stop_prompt="⏹️",
        just_once=True,
        use_container_width=True,
        key="mic"
    )

if prompt:
    with st.spinner("جيزا بتفكر..."):
        send_message(prompt)
    st.rerun()

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

# ─── مسح المحادثة ────────────────────────────────────────────────────────────
if len(st.session_state.messages) > 1:
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "أهلاً بك 👋\nأنا مساعد الجيزة الذكي ✨\nيمكنني مساعدتك في الاستثمار، السياحة، الخدمات الحكومية وأكثر.\nاكتب ما تحتاجه وسأساعدك فوراً!"
        }]
        st.session_state.last_audio_id = None
        st.session_state.active_tab = None
        st.rerun()
