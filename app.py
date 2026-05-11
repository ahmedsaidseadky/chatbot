import streamlit as st
from streamlit_mic_recorder import mic_recorder
from streamlit_js_eval import get_geolocation
from groq import Groq
import io
import json

st.set_page_config(
    page_title="مساعد الجيزة الذكي",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
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
}
# .tabs-scroll {
#     display: none !important;
# }
* { font-family: 'Cairo', sans-serif !important; box-sizing: border-box; }
html, body, .stApp { direction: rtl; background: var(--bg); }
#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }

.giza-header {
    background: linear-gradient(135deg, var(--blue-dark) 0%, var(--blue-mid) 60%, var(--blue-light) 100%);
    padding: 18px 20px 14px; border-radius: 0 0 24px 24px;
    margin: -1rem -1rem 0 -1rem; text-align: center;
    box-shadow: 0 4px 20px rgba(10,35,66,0.3);
}
.giza-header h1 { color: var(--gold-light); font-size: 1.4rem; font-weight: 900; margin: 0; }
.giza-header p  { color: rgba(255,255,255,0.75); font-size: 0.78rem; margin: 3px 0 0 0; }

.tabs-scroll {
    display: flex; gap: 8px; overflow-x: auto;
    padding: 12px 4px 8px; scrollbar-width: none; direction: rtl;
}
.tabs-scroll::-webkit-scrollbar { display: none; }
.tab-pill {
    display: inline-flex; align-items: center; gap: 5px;
    border-radius: 20px; padding: 7px 14px; font-size: 0.82rem;
    font-weight: 700; white-space: nowrap; border: 2px solid transparent;
}
.tab-pill.inactive { background: white; color: var(--blue-dark); border-color: #dde3ec; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.tab-pill.active   { background: var(--blue-dark); color: var(--gold-light); border-color: var(--gold); box-shadow: 0 3px 12px rgba(10,35,66,0.25); }

.stChatMessage { direction: rtl; margin-bottom: 10px; }
[data-testid="stChatMessageContent"] { direction: rtl; text-align: right; border-radius: 16px !important; font-size: 0.92rem; line-height: 1.7; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: white !important; border: 1px solid #e0e7f0; box-shadow: 0 2px 8px rgba(10,35,66,0.07);
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, var(--blue-dark), var(--blue-mid)) !important; color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# البيانات الكاملة
# ═══════════════════════════════════════════════════════════════

INVESTMENT_OPPORTUNITIES = [
    {
        "id": "nazlet-semman",
        "name": "قطعة أرض استثمارية – منطقة نزلة السمان",
        "location": "نزلة السمان، قريبة من الأهرامات",
        "activity": "مطعم سياحي / كافيه / بازار",
        "advantage": "كثافة سياحية عالية طوال العام",
        "score": 9.5,
        "reasoning": "أعلى معدلات جذب سياحي في المنطقة، طلب مستمر على الخدمات، وعائد استثماري سريع.",
        "bestFor": "مطعم، كافيه، متجر هدايا",
        "lat": 29.9812, "lng": 31.1390
    },
    {
        "id": "gem-surroundings",
        "name": "فرصة استثمارية – محيط المتحف المصري الكبير",
        "location": "محيط المتحف المصري الكبير",
        "activity": "مركز ترفيهي / خدمات سياحية",
        "advantage": "قربها من أحد أهم المشروعات القومية السياحية",
        "score": 9.0,
        "reasoning": "مشروع قومي جديد، تدفق سياحي هائل متوقع، وبنية تحتية حديثة.",
        "bestFor": "مركز ترفيهي، خدمات سياحية فاخرة",
        "lat": 29.9950, "lng": 31.1168
    },
    {
        "id": "manial-island",
        "name": "منطقة المنيل – إطلالة نيلية",
        "location": "المنيل، قريبة من النيل",
        "activity": "مشروع سياحي نهري / مطعم عائم",
        "advantage": "إطلالة مباشرة على النيل وموقع مركزي",
        "score": 8.5,
        "reasoning": "موقع استراتيجي يربط بين الجيزة والقاهرة، إقبال كبير من السكان والسياح.",
        "bestFor": "مطعم عائم، كافيه نيلى",
        "lat": 30.0150, "lng": 31.2250
    }
]

HOSPITALS = [
    {"name": "مستشفى العجوزة العام", "lat": 30.0520, "lng": 31.2130},
    {"name": "مستشفى الهرم العام", "lat": 29.9950, "lng": 31.1550},
    {"name": "مستشفى أم المصريين", "lat": 30.0050, "lng": 31.2150},
    {"name": "مستشفى الشيخ زايد التخصصي", "lat": 30.0450, "lng": 30.9950},
    {"name": "مستشفى الجيزة العام", "lat": 30.0131, "lng": 31.2089},
]

DIGITAL_SERVICES = {
    "التموين": [
        "ضم أفراد أسرتي", "إصدار بطاقة تموين جديدة", "الاستعلام عن صرف",
        "إصدار بدل تالف أو فاقد لبطاقة تموين", "تفعيل بطاقة تموين",
        "فصل نفسي", "نقل من محافظة إلى أخرى", "حذف طالب", "شراء سلع إضافية"
    ],
    "المرور والمركبات": [
        "تجديد رخصة قيادة", "إصدار رخصة قيادة بدل تالف/فاقد",
        "تجديد رخصة تسيير مركبة", "الاستعلام عن المخالفات المرورية",
        "سداد المخالفات المرورية", "إصدار رخصة تسيير مركبة جديدة",
        "الاستعلام عن بيانات مركبة", "نقل ملكية مركبة"
    ],
    "المعاشات والتأمينات": [
        "الاستعلام عن مستحقات المعاش", "تقديم طلب صرف معاش",
        "تعديل بيانات المعاش", "الاستعلام عن المدد التأمينية"
    ],
    "التوثيق والشهر العقاري": [
        "إصدار توكيل عام", "إصدار توكيل خاص",
        "الاستعلام عن ملكية عقارية", "طلب عقد زواج", "طلب عقد بيع"
    ]
}

RESTAURANTS = {
    "مصري": {
        "أهرامات": "🏆 مطعم 'فلفلة'\n📍 نزلة السمان\n⭐ 4.8/5\n🍽️ أطباق مصرية أصيلة مع إطلالة على الأهرامات\nطواجن، كشري، شاورما",
        "مدينة": "🏆 مطعم 'صبحي كابر'\n📍 الشيخ زايد\n⭐ 4.7/5\n🍽️ أكلات مصرية شعبية في أجواء عائلية\nمقبلات ومشويات ممتازة"
    },
    "شرقي": {
        "أهرامات": "🏆 'حدائق الأهرام لاونج'\n📍 حدائق الأهرام\n⭐ 4.7/5\n🍽️ مشويات فاخرة مع جلسات مفتوحة\nكباب وشيش ومزة شرقية",
        "مدينة": "🏆 'مطعم الطوب'\n📍 الدقي\n⭐ 4.6/5\n🍽️ شاورما وكباب بجودة عالية\nمشويات طازة يومياً"
    },
    "إيطالي": {
        "أهرامات": "🏆 'باستا كاسا'\n📍 الشيخ زايد\n⭐ 4.6/5\n🍽️ باستا إيطالية أصلية في أجواء كلاسيكية\nباستا وبيتزا وريزوتو",
        "مدينة": "🏆 'باستا كاسا'\n📍 الشيخ زايد\n⭐ 4.6/5\n🍽️ أفضل إيطالي في الجيزة"
    },
    "آسيوي": {
        "أهرامات": "🏆 'مطعم التنين الذهبي'\n📍 الجيزة\n⭐ 4.5/5\n🍽️ أكلات صينية ويابانية\nسوشي وديم سام",
        "مدينة": "🏆 'هانا سوشي'\n📍 المهندسين\n⭐ 4.6/5\n🍽️ سوشي طازة يومياً"
    }
}

HOTELS = {
    "اقتصادي": {
        "أهرامات": "🏨 'Pyramids View Inn'\n⭐ 4.2/5\n💰 40-60$/ليلة\n📍 نزلة السمان\n✨ إطلالة رائعة وسعر مناسب",
        "مدينة": "🏨 'جرين بلازا شقق'\n⭐ 4.1/5\n💰 50-65$/ليلة\n📍 الشيخ زايد\n✨ وسط المدينة وقريب من المول"
    },
    "متوسط": {
        "أهرامات": "🏨 'ستينبرجر بيراميدز'\n⭐ 4.5/5\n💰 80-150$/ليلة\n📍 الجيزة مع إطلالة نيلية\n✨ حمام سباحة وإفطار شامل",
        "مدينة": "🏨 'ستيلا شقق فندقية'\n⭐ 4.4/5\n💰 85-130$/ليلة\n📍 الشيخ زايد\n✨ مطعم وجيم وخدمات كونسيرج"
    },
    "فاخر": {
        "أهرامات": "🏨 'ماريوت مينا هاوس'\n⭐ 4.8/5\n💰 250-400$/ليلة\n📍 نزلة السمان\n✨ 5 نجوم مع إطلالة مباشرة على الأهرامات",
        "مدينة": "🏨 'فور سيزنز جيزة'\n⭐ 4.9/5\n💰 280-450$/ليلة\n📍 الشيخ زايد الفاخر\n✨ منتجع شامل مع سبا وجيم عالمي"
    }
}

# ═══════════════════════════════════════════════════════════════
# System Prompt المتكامل
# ═══════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """أنت مساعد ذكي رسمي لمحافظة الجيزة، مصر. اسمك 'جيزا'.
تتكلم عربي وإنجليزي وترد بنفس لغة المستخدم.

【سيناريو المطاعم】
الخطوة 1: اسأل عن نوع الطعام (مصري / شرقي / إيطالي / آسيوي / بحري / عالمي)
الخطوة 2: اسأل عن الموقع (إطلالة أهرامات / وسط المدينة)
الخطوة 3: قدم التوصية مع التفاصيل الكاملة ورابط Google Maps

التوصيات:
- مصري + أهرامات: مطعم فلفلة، نزلة السمان، ⭐4.8، طواجن وكشري وشاورما
- مصري + مدينة: صبحي كابر، الشيخ زايد، ⭐4.7
- شرقي + أهرامات: حدائق الأهرام لاونج، ⭐4.7، كباب وشيش
- شرقي + مدينة: مطعم الطوب، الدقي، ⭐4.6
- إيطالي: باستا كاسا، الشيخ زايد، ⭐4.6

【سيناريو الفنادق】
الخطوة 1: اسأل عن الميزانية (اقتصادي / متوسط / فاخر)
الخطوة 2: اسأل عن الموقع (قرب الأهرامات / الشيخ زايد)
التوصيات:
- فاخر + أهرامات: ماريوت مينا هاوس، 250-400$، ⭐4.8
- فاخر + مدينة: فور سيزنز جيزة، 280-450$، ⭐4.9
- متوسط + أهرامات: ستينبرجر بيراميدز، 80-150$، ⭐4.5
- متوسط + مدينة: ستيلا شقق فندقية، 85-130$، ⭐4.4
- اقتصادي + أهرامات: Pyramids View Inn، 40-60$، ⭐4.2
- اقتصادي + مدينة: جرين بلازا شقق، 50-65$، ⭐4.1

【سيناريو الاستثمار - 5 خطوات】
الخطوة 1: اسأل عن اسم المستثمر
الخطوة 2: اسأل عن نوع النشاط (كافيه / فندق / مطعم / بوتيك / مكتب)
الخطوة 3: اسأل عن المنطقة المفضلة (الأهرامات / المتحف / النيل / وسط الجيزة)
الخطوة 4: اسأل عن الميزانية (أقل من 3م / 3-5م / 5-10م / أكثر من 10م جنيه)
الخطوة 5: قدم الفرص المناسبة:
  • نزلة السمان (تقييم 9.5/10): مطعم/كافيه، كثافة سياحية عالية، lat=29.9812 lng=31.1390
  • محيط المتحف المصري الكبير (تقييم 9.0/10): مركز ترفيهي، مشروع قومي جديد، lat=29.9950 lng=31.1168
  • المنيل (تقييم 8.5/10): مطعم عائم/كافيه نيلي، إطلالة نيل مباشرة، lat=30.0150 lng=31.2250

【سيناريو السياحة】
لما يسأل عن برنامج سياحي، اسأل كم يوم، ثم قدم:
- يوم واحد: أهرامات + أبو الهول صباحاً، عرض صوت وضوء مساءً
- يومين: + المتحف المصري الكبير GEM يوم 2
- 3 أيام: + حدائق الأورمان أو حديقة الحيوان، رحلة نيلية يوم 3
- أسبوع: كل ما سبق + قرية الحرانية + كورنيش الجيزة + سوق الجمعة

【الخدمات الحكومية - مصر الرقمية】
التموين: ضم أفراد، إصدار بطاقة، استعلام عن صرف، بدل تالف، تفعيل بطاقة، فصل نفسي، نقل محافظة
المرور: تجديد رخصة قيادة، بدل تالف لرخصة، تجديد رخصة تسيير، استعلام مخالفات، سداد مخالفات، نقل ملكية
المعاشات: استعلام مستحقات، طلب صرف معاش، تعديل بيانات
التوثيق: توكيل عام، توكيل خاص، استعلام ملكية عقارية
الرابط: https://digital.gov.eg

【المستشفيات】
- مستشفى الجيزة العام (lat=30.0131, lng=31.2089)
- مستشفى أم المصريين (lat=30.0050, lng=31.2150)
- مستشفى الشيخ زايد التخصصي (lat=30.0450, lng=30.9950)
- مستشفى العجوزة العام (lat=30.0520, lng=31.2130)
- مستشفى الهرم العام (lat=29.9950, lng=31.1550)

【ذوي الهمم】
اسأل عن الخدمة المطلوبة (سجل مدني / بريد / تموين / صحة)
ثم اسأل عن احتياجات الوصول: منحدر كراسي / شباك أرضي / مصعد مخصص

【الشكاوى】
وجّه للموقع الرسمي لمحافظة الجيزة

【قاعدة الموقع الجغرافي - مهمة جداً】
لو المستخدم أرسل إحداثياته (lat, lng)، استخدمها في روابط Google Maps:
- مستشفيات: https://www.google.com/maps/search/مستشفى/@LAT,LNG,15z
- مطاعم: https://www.google.com/maps/search/مطعم/@LAT,LNG,15z
- فنادق: https://www.google.com/maps/search/فندق/@LAT,LNG,15z
- صيدليات: https://www.google.com/maps/search/صيدلية/@LAT,LNG,15z
استبدل LAT وLNG بالإحداثيات الحقيقية

قواعد الردود:
- جملة أو جملتين بحد أقصى ما لم يطلب تفاصيل
- سؤال واحد فقط في كل رد
- لغة طبيعية ودية
- تذكر المحادثة السابقة دائماً"""

# ─── Tabs ────────────────────────────────────────────────────────────────────
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
    "فنادق":       "عايز فنادق قريبة في الجيزة",
    "ذوي الهمم":  "عايز خدمات ذوي الهمم",
    "الشكاوى":    "عايز أقدم شكوى",
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

# ─── التابات المرئية ──────────────────────────────────────────────────────────
active = st.session_state.active_tab
tabs_html = '<div class="tabs-scroll">'
for icon, label in TABS:
    css = "active" if label == active else "inactive"
    tabs_html += f'<div class="tab-pill {css}">{icon} {label}</div>'
tabs_html += '</div>'
st.markdown(tabs_html, unsafe_allow_html=True)

# أزرار مخفية للتابات
cols = st.columns(len(TABS))
for i, (icon, label) in enumerate(TABS):
    with cols[i]:
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
                messages=msgs, temperature=0.7, max_tokens=700
            )
            st.session_state.messages.append({"role": "assistant", "content": resp.choices[0].message.content})
            st.rerun()

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
            st.rerun()
with loc_col1:
    if st.session_state.location:
        lat = st.session_state.location["lat"]
        lng = st.session_state.location["lng"]
        st.success(f"📍 موقعك محدد ✓ — سيتم استخدامه لعرض أقرب الخدمات")
    else:
        st.caption("📍 اضغط لتحديد موقعك وعرض أقرب المستشفيات والمطاعم والفنادق")

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
        messages=msgs, temperature=0.7, max_tokens=700
    )
    reply = resp.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})

# ─── الإدخال: نص + ميكروفون جنب بعض ─────────────────────────────────────────
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
