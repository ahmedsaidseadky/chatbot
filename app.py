import streamlit as st
from streamlit_mic_recorder import mic_recorder
from streamlit_js_eval import get_geolocation
from groq import Groq
import io
import json

st.set_page_config(
    page_title="Giza Smart Assistant | مساعد الجيزة الذكي",
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
# System Prompt المتكامل - يدعم العربية والإنجليزية
# ═══════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """You are an official AI assistant for Giza Governorate, Egypt. Your name is 'Giza'. 
You speak **both Arabic and English** perfectly. You MUST respond in the SAME language the user uses.

إذا كتب المستخدم بالإنجليزية، رد بالإنجليزية. إذا كتب بالعربية، رد بالعربية.

【Restaurants Scenario - English/Arabic】
Step 1: Ask about cuisine type (Egyptian/Italian/Asian etc. or مصري/إيطالي/آسيوي)
Step 2: Ask about location (Pyramids view or city center / إطلالة أهرامات أو وسط المدينة)
Step 3: Provide recommendation with full details and Google Maps link

Recommendations:
- Egyptian + Pyramids: 'Felfela' restaurant, Nazlet El-Samman, ⭐4.8, tagines, koshari, shawarma
- Egyptian + City: 'Sobhi Kaber' restaurant, Sheikh Zayed, ⭐4.7
- Italian: 'Pasta Casa', Sheikh Zayed, ⭐4.6

【Hotels Scenario - English/Arabic】
Step 1: Ask about budget (economy/mid-range/luxury or اقتصادي/متوسط/فاخر)
Step 2: Ask about location (near Pyramids/Sheikh Zayed or قرب الأهرامات/الشيخ زايد)

Recommendations:
- Luxury + Pyramids: Marriott Mena House, $250-400, ⭐4.8
- Luxury + City: Four Seasons Giza, $280-450, ⭐4.9
- Mid-range + Pyramids: Steigenberger Pyramids, $80-150, ⭐4.5
- Economy + Pyramids: Pyramids View Inn, $40-60, ⭐4.2

【Investment Scenario - 5 steps in English/Arabic】
Step 1: Ask for investor's name (الاسم)
Step 2: Ask for activity type (cafe/hotel/restaurant/office - كافيه/فندق/مطعم/مكتب)
Step 3: Ask for preferred zone (Pyramids/GEM/Nile/Central Giza - الأهرامات/المتحف/النيل/وسط الجيزة)
Step 4: Ask for budget (less than 3M/3-5M/5-10M/over 10M EGP - أقل من 3م/3-5م/5-10م/أكثر من 10م جنيه)
Step 5: Provide opportunities:
  • Nazlet El-Samman (score 9.5/10): restaurants/cafes, high tourist density, lat=29.9812 lng=31.1390
  • GEM surroundings (score 9.0/10): entertainment center, new national project, lat=29.9950 lng=31.1168
  • Manial Island (score 8.5/10): floating restaurant/Nile cafe, direct Nile view, lat=30.0150 lng=31.2250

【Tourism Scenario - English/Arabic】
When asked for tourist program, ask how many days, then offer:
- 1 day: Pyramids + Sphinx morning, Sound & Light show evening
- 2 days: + Grand Egyptian Museum (GEM) on day 2
- 3 days: + Orman Gardens or Zoo, Nile trip on day 3
- 1 week: all above + Harraniya village + Giza Corniche + Friday market

【Government Services - Digital Egypt (English/Arabic)】
Supply: add family members, issue card, inquiry about disbursement, replace damaged/lost card, activate card
Traffic: renew driving license, replace damaged/lost license, renew vehicle license, check violations, pay violations, transfer ownership
Pensions: inquire about pension dues, apply for pension, update data
Notarization: general power of attorney, specific power of attorney, property ownership inquiry
Link: https://digital.gov.eg

【Hospitals - English/Arabic】
- Giza General Hospital (lat=30.0131, lng=31.2089)
- Om El-Masryeen Hospital (lat=30.0050, lng=31.2150)
- Sheikh Zayed Specialized Hospital (lat=30.0450, lng=30.9950)
- Agouza General Hospital (lat=30.0520, lng=31.2130)
- Haram General Hospital (lat=29.9950, lng=31.1550)

【People with Disabilities - English/Arabic】
Ask about required service (civil registry/post/supply/health - سجل مدني/بريد/تموين/صحة)
Then ask about access needs: wheelchair ramp/low counter/special elevator (منحدر كراسي/شباك أرضي/مصعد مخصص)

【Complaints - English/Arabic】
Direct to Giza Governorate official website

【Geolocation Rule - Very Important】
If user sends coordinates (lat, lng), use them in Google Maps links:
- Hospitals: https://www.google.com/maps/search/hospital/@LAT,LNG,15z
- Restaurants: https://www.google.com/maps/search/restaurant/@LAT,LNG,15z
- Hotels: https://www.google.com/maps/search/hotel/@LAT,LNG,15z
- Pharmacies: https://www.google.com/maps/search/pharmacy/@LAT,LNG,15z
Replace LAT and LNG with actual coordinates

Response rules:
- Maximum 1-2 sentences unless user asks for details
- Only ONE question per response
- Natural, friendly tone
- Always remember conversation history"""

# ─── Tabs ثنائية اللغة ──────────────────────────────────────────────────────
TABS = [
    ("🏥", "مستشفيات/Hospitals"),
    ("🏛️", "السياحة/Tourism"),
    ("📈", "الاستثمار/Investment"),
    ("💻", "مصر الرقمية/Digital Egypt"),
    ("🍽️", "مطاعم/Restaurants"),
    ("🏨", "فنادق/Hotels"),
    ("♿", "ذوي الهمم/Disabilities"),
    ("📋", "الشكاوى/Complaints"),
]

TAB_PROMPTS = {
    "مستشفيات/Hospitals":    "أقرب مستشفى ليا / Nearest hospital to me",
    "السياحة/Tourism":     "عايز برنامج سياحي / I want a tourist program in Giza",
    "الاستثمار/Investment":   "عايز أعرف فرص الاستثمار في الجيزة / I want investment opportunities in Giza",
    "مصر الرقمية/Digital Egypt":"عايز أعرف خدمات مصر الرقمية المتاحة / Tell me about available Digital Egypt services",
    "مطاعم/Restaurants":       "عايز مطاعم قريبة مني / Restaurants near me",
    "فنادق/Hotels":       "عايز فنادق في الجيزة / Hotels in Giza",
    "ذوي الهمم/Disabilities":  "عايز خدمات ذوي الهمم / Disability services in Giza",
    "الشكاوى/Complaints":    "عايز أقدم شكوى / I want to submit a complaint",
}

# ─── Groq ────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# ─── تهيئة الحالة ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "أهلاً بك 👋\nWelcome!\nأنا مساعد الجيزة الذكي ✨\nI am Giza's smart assistant.\nيمكنني مساعدتك بالعربية أو الإنجليزية.\nI can help in Arabic or English.\nاسأل عن: استثمار، سياحة، خدمات حكومية، مطاعم، فنادق...\nAsk me about: Investment, Tourism, Government services, Restaurants, Hotels..."
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
    <h1>مساعدك الذكي ✨ | Your Smart Assistant</h1>
    <p>محافظة الجيزة · استثمار · سياحة · خدمات حكومية | Giza · Investment · Tourism · Government Services</p>
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

# أزرار التابات
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
                full_prompt = f"{prompt_text}\n[User location: lat={lat}, lng={lng}]"
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
        st.success(f"📍 موقعك محدد ✓ | Your location is set — سيتم استخدامه لعرض أقرب الخدمات | Will be used to show nearest services")
    else:
        st.caption("📍 اضغط لتحديد موقعك وعرض أقرب المستشفيات والمطاعم والفنادق | Click to set your location and see nearest hospitals, restaurants, and hotels")

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
        full_text = f"{user_text}\n[User location: lat={lat}, lng={lng}]"
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

# ─── الإدخال: نص + ميكروفون ──────────────────────────────────────────────────
input_col, mic_col = st.columns([6, 1])
with input_col:
    prompt = st.chat_input("اكتب سؤالك هنا | Type your question here...")
with mic_col:
    audio = mic_recorder(
        start_prompt="🎤", stop_prompt="⏹️",
        just_once=True, use_container_width=True, key="mic"
    )

if prompt:
    with st.spinner("جيزا بتفكر... | Giza is thinking..."):
        send_message(prompt)
    st.rerun()

if audio and audio["id"] != st.session_state.last_audio_id:
    st.session_state.last_audio_id = audio["id"]
    with st.spinner("🎤 جيزا بتسمعك... | Giza is listening..."):
        client = get_client()
        audio_bytes = io.BytesIO(audio["bytes"])
        audio_bytes.name = "audio.wav"
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3", file=audio_bytes, language="ar"
        )
        voice_text = transcription.text.strip()
        if voice_text:
            st.info(f"🎤 قلت | You said: {voice_text}")
            send_message(voice_text)
            st.rerun()
        else:
            st.warning("🚫 لم يتم التعرف على كلام. Try speaking again. | No speech recognized.")

# ─── مسح المحادثة ────────────────────────────────────────────────────────────
if len(st.session_state.messages) > 1:
    if st.button("🗑️ مسح المحادثة | Clear Conversation", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "أهلاً بك 👋\nWelcome!\nتم مسح المحادثة. Conversation cleared.\nأنا مساعد الجيزة الذكي ✨\nI am Giza's smart assistant.\nكيف يمكنني مساعدتك؟ How can I help?"
        }]
        st.session_state.last_audio_id = None
        st.session_state.active_tab = None
        st.rerun()
