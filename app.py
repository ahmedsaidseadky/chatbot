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
    --primary: #1a56a0;
    --primary-dark: #0a2342;
    --gold: #f0c85a;
    --gold-dim: #c9a84c;
    --bg: #f4f6fb;
    --white: #ffffff;
    --gray: #f0f2f7;
    --border: #e2e8f0;
    --text: #1a2340;
    --text-light: #64748b;
    --green: #22c55e;
    --radius: 18px;
}

* { font-family: 'Cairo', sans-serif !important; box-sizing: border-box; margin: 0; padding: 0; }
html, body, .stApp { direction: rtl; background: var(--bg); }
#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stBottom"] { display: none !important; }

/* إخفاء أزرار التابات الحقيقية */
div[data-testid="stHorizontalBlock"] button { visibility: hidden; height: 0 !important; padding: 0 !important; margin: 0 !important; border: none !important; }

/* ═══ الهيدر ═══ */
.app-header {
    background: var(--primary);
    color: white;
    padding: 14px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 12px rgba(10,35,66,0.18);
    margin: -1rem -1rem 0 -1rem;
}
.header-right { display: flex; align-items: center; gap: 10px; }
.header-avatar {
    width: 38px; height: 38px;
    background: rgba(255,255,255,0.15);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem;
    position: relative;
}
.online-dot {
    width: 10px; height: 10px;
    background: var(--green);
    border-radius: 50%;
    border: 2px solid var(--primary);
    position: absolute;
    bottom: 0; left: 0;
}
.header-title { font-size: 0.95rem; font-weight: 700; }
.header-sub { font-size: 0.7rem; opacity: 0.75; }
.lang-btn {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    color: white;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 0.72rem;
    font-weight: 700;
    cursor: pointer;
}

/* ═══ التابات ═══ */
.tabs-wrapper {
    background: white;
    border-bottom: 1px solid var(--border);
    padding: 10px 12px 8px;
    margin: 0 -1rem;
    overflow-x: auto;
    scrollbar-width: none;
    -webkit-overflow-scrolling: touch;
}
.tabs-wrapper::-webkit-scrollbar { display: none; }
.tabs-row { display: flex; gap: 8px; width: max-content; direction: rtl; }

.tab-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 700;
    cursor: pointer;
    white-space: nowrap;
    border: 1.5px solid var(--border);
    background: var(--gray);
    color: var(--text);
    transition: all 0.2s;
    user-select: none;
}
.tab-chip.active {
    background: var(--primary);
    color: white;
    border-color: var(--primary);
    box-shadow: 0 2px 8px rgba(26,86,160,0.3);
}
.tab-chip:hover:not(.active) {
    background: #e8f0fb;
    border-color: var(--primary);
    color: var(--primary);
}

/* ═══ منطقة الشات ═══ */
.chat-area { padding: 16px 4px 8px; }

/* فقاعات الرسائل */
.stChatMessage { direction: rtl !important; }
[data-testid="stChatMessageContent"] {
    border-radius: 18px !important;
    font-size: 0.9rem !important;
    line-height: 1.75 !important;
    direction: rtl !important;
    text-align: right !important;
    padding: 12px 16px !important;
}

/* رسائل البوت */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: var(--white) !important;
    border: 1px solid var(--border) !important;
    border-top-right-radius: 4px !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06) !important;
    color: var(--text) !important;
}

/* رسائل المستخدم */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: var(--primary) !important;
    color: white !important;
    border-top-left-radius: 4px !important;
    border: none !important;
}

/* ═══ شريط الموقع ═══ */
.loc-bar {
    background: #eef4ff;
    border: 1px solid #c7daf9;
    border-radius: 12px;
    padding: 8px 14px;
    margin: 8px 0;
    font-size: 0.82rem;
    color: var(--primary);
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
}
.loc-bar.active { background: #f0fdf4; border-color: #86efac; color: #15803d; }

/* ═══ شريط الإدخال ═══ */
.input-section {
    position: sticky;
    bottom: 0;
    background: white;
    border-top: 1px solid var(--border);
    padding: 10px 12px;
    margin: 12px -1rem -1rem -1rem;
    box-shadow: 0 -4px 16px rgba(0,0,0,0.06);
}

/* تنسيق صندوق الكتابة */
.stChatInput > div {
    border-radius: 25px !important;
    border: 1.5px solid var(--border) !important;
    background: var(--gray) !important;
    direction: rtl !important;
}
.stChatInput textarea { direction: rtl !important; text-align: right !important; }
.stChatInput button { border-radius: 50% !important; background: var(--primary) !important; }

/* ═══ زرار مسح ═══ */
.clear-btn button {
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    background: white !important;
    color: var(--text-light) !important;
    font-size: 0.82rem !important;
}

/* ═══ الـ Spinner ═══ */
.stSpinner > div { border-top-color: var(--primary) !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# System Prompt الكامل مع كل الداتا
# ═══════════════════════════════════════════════
SYSTEM_PROMPT = """أنت مساعد ذكي رسمي لمحافظة الجيزة، مصر. اسمك 'جيزا'. تتكلم عربي وإنجليزي وترد بنفس لغة المستخدم تلقائياً.

═══ سيناريو المطاعم ═══
الخطوة 1: اسأل "ما نوع الطعام الذي تفضله؟" (مصري / شرقي / إيطالي / آسيوي / بحري / عالمي)
الخطوة 2: اسأل "تفضل إطلالة على الأهرامات أم في وسط المدينة؟"
الخطوة 3: قدم التوصية التالية مع رابط Google Maps لو عندك موقع المستخدم

التوصيات:
• مصري + أهرامات → مطعم فلفلة، نزلة السمان، ⭐4.8/5، طواجن وكشري وشاورما
• مصري + مدينة → صبحي كابر، الشيخ زايد، ⭐4.7/5، أكلات شعبية عائلية
• شرقي + أهرامات → حدائق الأهرام لاونج، ⭐4.7/5، كباب وشيش ومزة شرقية
• شرقي + مدينة → مطعم الطوب، الدقي، ⭐4.6/5، مشويات طازة يومياً
• إيطالي → باستا كاسا، الشيخ زايد، ⭐4.6/5، باستا وبيتزا وريزوتو
• آسيوي → هانا سوشي، المهندسين، ⭐4.6/5، سوشي طازة

═══ سيناريو الفنادق ═══
الخطوة 1: اسأل "ما هي ميزانيتك؟" (اقتصادي / متوسط / فاخر)
الخطوة 2: اسأل "تفضل قريب من الأهرامات أم الشيخ زايد؟"
الخطوة 3: قدم التوصية

التوصيات:
• فاخر + أهرامات → ماريوت مينا هاوس، 250-400$/ليلة، ⭐4.8/5، إطلالة مباشرة على الأهرامات
• فاخر + مدينة → فور سيزنز جيزة، 280-450$/ليلة، ⭐4.9/5، سبا وجيم عالمي
• متوسط + أهرامات → ستينبرجر بيراميدز، 80-150$/ليلة، ⭐4.5/5، حمام سباحة وإفطار شامل
• متوسط + مدينة → ستيلا شقق فندقية، 85-130$/ليلة، ⭐4.4/5، خدمات كونسيرج
• اقتصادي + أهرامات → Pyramids View Inn، 40-60$/ليلة، ⭐4.2/5، إطلالة رائعة وسعر مناسب
• اقتصادي + مدينة → جرين بلازا شقق، 50-65$/ليلة، ⭐4.1/5، وسط المدينة

═══ سيناريو الاستثمار - 5 خطوات ═══
الخطوة 1: اسأل "ما اسمك؟"
الخطوة 2: اسأل "ما نوع النشاط الاستثماري؟" (كافيه / فندق / مطعم / بوتيك / مكتب)
الخطوة 3: اسأل "ما المنطقة المفضلة؟" (الأهرامات / المتحف / النيل / وسط الجيزة)
الخطوة 4: اسأل "ما نطاق الميزانية؟" (أقل من 3م / 3-5م / 5-10م / أكثر من 10م جنيه)
الخطوة 5: قدم الفرص المناسبة:
  ◆ نزلة السمان (تقييم 9.5/10)
    النشاط: مطعم سياحي / كافيه / بازار
    الميزة: كثافة سياحية عالية طوال العام، أعلى معدلات جذب سياحي
    الموقع: lat=29.9812, lng=31.1390
  ◆ محيط المتحف المصري الكبير GEM (تقييم 9.0/10)
    النشاط: مركز ترفيهي / خدمات سياحية
    الميزة: مشروع قومي جديد، تدفق سياحي هائل متوقع
    الموقع: lat=29.9950, lng=31.1168
  ◆ منطقة المنيل - إطلالة نيلية (تقييم 8.5/10)
    النشاط: مشروع نهري / مطعم عائم / كافيه نيلي
    الميزة: إطلالة مباشرة على النيل وموقع مركزي
    الموقع: lat=30.0150, lng=31.2250

═══ سيناريو السياحة ═══
لما يسأل عن برنامج سياحي، اسأل كم يوم، ثم قدم:
• يوم واحد: أهرامات الجيزة + أبو الهول صباحاً (4 ساعات) ← عرض الصوت والضوء مساءً ⭐4.9/5
• يومين: + المتحف المصري الكبير GEM ← قرية الحرانية للتسوق ⭐4.7/5
• 3 أيام: + حديقة الأورمان أو حديقة الحيوان ← رحلة نيلية بالفلوكة عند الغروب ⭐4.5/5
• أسبوع: كل ما سبق + كورنيش الجيزة + سوق الجمعة + المنيل

الأماكن السياحية مع الإحداثيات:
• أهرامات الجيزة: lat=29.9792, lng=31.1342
• أبو الهول: lat=29.9753, lng=31.1376
• المتحف المصري الكبير GEM: lat=29.9950, lng=31.1168

═══ الخدمات الحكومية - مصر الرقمية ═══
الموقع: https://digital.gov.eg

التموين (10 خدمات):
ضم أفراد أسرتي، إصدار بطاقة تموين جديدة، الاستعلام عن صرف،
إصدار بدل تالف أو فاقد لبطاقة تموين، تفعيل بطاقة تموين،
فصل نفسي، نقل من محافظة إلى أخرى، حذف طالب، شراء سلع إضافية

المرور والمركبات (8 خدمات):
تجديد رخصة قيادة، إصدار رخصة قيادة بدل تالف/فاقد،
تجديد رخصة تسيير مركبة، الاستعلام عن المخالفات المرورية،
سداد المخالفات المرورية، إصدار رخصة تسيير مركبة جديدة،
الاستعلام عن بيانات مركبة، نقل ملكية مركبة

المعاشات والتأمينات:
الاستعلام عن مستحقات المعاش، تقديم طلب صرف معاش،
تعديل بيانات المعاش، الاستعلام عن المدد التأمينية

التوثيق والشهر العقاري:
إصدار توكيل عام، إصدار توكيل خاص، الاستعلام عن ملكية عقارية،
طلب عقد زواج، طلب عقد بيع

السجل التجاري:
استخراج شهادة قيد في السجل التجاري، تعديل بيانات السجل التجاري، تجديد قيد السجل التجاري

الإسكان الاجتماعي:
تقديم طلب حجز وحدة سكنية، الاستعلام عن طلب الإسكان، سداد أقساط الإسكان

═══ المستشفيات ═══
• مستشفى الجيزة العام: lat=30.0131, lng=31.2089
• مستشفى أم المصريين: lat=30.0050, lng=31.2150
• مستشفى الشيخ زايد التخصصي: lat=30.0450, lng=30.9950
• مستشفى العجوزة العام: lat=30.0520, lng=31.2130
• مستشفى الهرم العام: lat=29.9950, lng=31.1550

═══ ذوي الهمم ═══
اسأل عن الخدمة (سجل مدني / بريد / تموين / صحة)
اسأل عن احتياجات الوصول: منحدر كراسي متحركة / شباك أرضي / مصعد مخصص

═══ الشكاوى ═══
وجّه للموقع الرسمي لمحافظة الجيزة أو صفحة الشكاوى

═══ قاعدة الموقع الجغرافي ═══
لو المستخدم أرسل إحداثياته (lat, lng)، قدم روابط Google Maps:
• مستشفيات: https://www.google.com/maps/search/مستشفى/@LAT,LNG,15z
• مطاعم: https://www.google.com/maps/search/مطعم/@LAT,LNG,15z
• فنادق: https://www.google.com/maps/search/فندق/@LAT,LNG,15z
• صيدليات: https://www.google.com/maps/search/صيدلية/@LAT,LNG,15z
استبدل LAT وLNG بالإحداثيات الحقيقية دائماً

═══ قواعد الردود ═══
- ردود قصيرة ومباشرة ما لم يطلب تفاصيل (جملتين بحد أقصى)
- سؤال واحد فقط في كل رد
- لغة طبيعية ودية
- ابدأ بترحيب سريع فقط في أول رسالة
- تذكر المحادثة السابقة دائماً لإكمال السيناريوهات"""

# ─── التابات ─────────────────────────────────────────────────
TABS = [
    ("🏥", "مستشفيات"),
    ("🏛️", "السياحة"),
    ("📈", "الاستثمار"),
    ("💻", "مصر الرقمية"),
    ("🍽️", "مطاعم"),
    ("🏨", "فنادق"),
    ("♿", "ذوي الهمم"),
    ("📋", "الشكاوى"),
]
TAB_PROMPTS = {
    "مستشفيات":    "أقرب مستشفى ليا",
    "السياحة":     "عايز برنامج سياحي في الجيزة",
    "الاستثمار":   "عايز أعرف فرص الاستثمار في الجيزة",
    "مصر الرقمية":"عايز أعرف خدمات مصر الرقمية المتاحة",
    "مطاعم":       "عايز مطاعم قريبة مني",
    "فنادق":       "عايز فنادق في الجيزة",
    "ذوي الهمم":  "عايز خدمات ذوي الهمم",
    "الشكاوى":    "عايز أقدم شكوى",
}

# ─── Groq ─────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# ─── تهيئة الحالة ──────────────────────────────────────────────
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

# ─── دالة إرسال ───────────────────────────────────────────────
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
        content = full_text if i == len(st.session_state.messages) - 1 else m["content"]
        msgs.append({"role": m["role"], "content": content})
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=msgs, temperature=0.7, max_tokens=700
    )
    st.session_state.messages.append({"role": "assistant", "content": resp.choices[0].message.content})

# ══════════════════════════════════════════════
# الواجهة
# ══════════════════════════════════════════════

# ─── الهيدر ───────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="header-right">
    <div class="header-avatar">
      🏛️
      <span class="online-dot"></span>
    </div>
    <div>
      <div class="header-title">مساعدك الذكي ✨</div>
      <div class="header-sub">محافظة الجيزة • متصل الآن</div>
    </div>
  </div>
  <div style="display:flex;gap:8px;align-items:center">
    <span class="lang-btn">EN 🌐</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── التابات المرئية ───────────────────────────
active = st.session_state.active_tab
tabs_html = '<div class="tabs-wrapper"><div class="tabs-row">'
for icon, label in TABS:
    css = "active" if label == active else ""
    tabs_html += f'<div class="tab-chip {css}">{icon} {label}</div>'
tabs_html += '</div></div>'
st.markdown(tabs_html, unsafe_allow_html=True)

# أزرار مخفية وظيفية
cols = st.columns(len(TABS))
for i, (icon, label) in enumerate(TABS):
    with cols[i]:
        if st.button(label, key=f"tab_{label}"):
            st.session_state.active_tab = label
            prompt_text = TAB_PROMPTS.get(label, label)
            with st.spinner("جيزا بتفكر..."):
                send_message(prompt_text)
            st.rerun()

# ─── شريط الموقع ──────────────────────────────
loc_col1, loc_col2 = st.columns([4, 1])
with loc_col2:
    if st.button("📍 موقعي", use_container_width=True, key="loc_btn"):
        loc = get_geolocation()
        if loc and "coords" in loc:
            st.session_state.location = {
                "lat": loc["coords"]["latitude"],
                "lng": loc["coords"]["longitude"]
            }
            st.rerun()
with loc_col1:
    if st.session_state.location:
        st.markdown('<div class="loc-bar active">✅ موقعك محدد — سيتم استخدامه لعرض أقرب الخدمات</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="loc-bar">📍 اضغط لتحديد موقعك وعرض أقرب المستشفيات والمطاعم والفنادق</div>', unsafe_allow_html=True)

# ─── المحادثة ─────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── الإدخال: نص + ميكروفون ───────────────────
input_col, mic_col = st.columns([6, 1])
with input_col:
    prompt = st.chat_input("اكتب سؤالك هنا...")
with mic_col:
    audio = mic_recorder(
        start_prompt="🎤", stop_prompt="⏹️",
        just_once=True, use_container_width=True, key="mic"
    )

if prompt:
    with st.spinner("جيزا بتفكر..."):
        send_message(prompt)
    st.rerun()

if audio and audio["id"] != st.session_state.last_audio_id:
    st.session_state.last_audio_id = audio["id"]
    with st.spinner("🎤 جيزا بتسمعك..."):
        try:
            client = get_client()
            audio_bytes = io.BytesIO(audio["bytes"])
            audio_bytes.name = "audio.wav"
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3", file=audio_bytes, language="ar"
            )
            voice_text = transcription.text.strip()
            if voice_text:
                st.info(f"🎤 قلت: {voice_text}")
                send_message(voice_text)
                st.rerun()
        except Exception as e:
            st.error("حصل خطأ في تحويل الصوت، جرب تاني.")

# ─── مسح المحادثة ─────────────────────────────
st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
if len(st.session_state.messages) > 1:
    if st.button("🗑️ مسح المحادثة", use_container_width=True, key="clear"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "أهلاً بك 👋\nأنا مساعد الجيزة الذكي ✨\nيمكنني مساعدتك في الاستثمار، السياحة، الخدمات الحكومية وأكثر.\nاكتب ما تحتاجه وسأساعدك فوراً!"
        }]
        st.session_state.last_audio_id = None
        st.session_state.active_tab = None
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
