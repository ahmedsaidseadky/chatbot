import streamlit as st
from streamlit_mic_recorder import mic_recorder
from streamlit_js_eval import get_geolocation
from groq import Groq
import io
import math

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
    --bg: #f4f6fb;
    --white: #ffffff;
    --gray: #f0f2f7;
    --border: #e2e8f0;
    --text: #1a2340;
    --text-light: #64748b;
    --green: #22c55e;
}
* { font-family: 'Cairo', sans-serif !important; box-sizing: border-box; }
html, body, .stApp { direction: rtl; background: var(--bg); }
#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
div[data-testid="stHorizontalBlock"] button { visibility: hidden; height: 0 !important; padding: 0 !important; margin: 0 !important; border: none !important; }

.app-header {
    background: var(--primary);
    color: white; padding: 14px 16px;
    display: flex; align-items: center; justify-content: space-between;
    position: sticky; top: 0; z-index: 100;
    box-shadow: 0 2px 12px rgba(10,35,66,0.18);
    margin: -1rem -1rem 0 -1rem;
}
.header-avatar {
    width: 38px; height: 38px;
    background: rgba(255,255,255,0.15);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; position: relative;
}
.online-dot {
    width: 10px; height: 10px; background: var(--green);
    border-radius: 50%; border: 2px solid var(--primary);
    position: absolute; bottom: 0; left: 0;
}

.tabs-wrapper {
    background: white; border-bottom: 1px solid var(--border);
    padding: 10px 12px 8px; margin: 0 -1rem;
    overflow-x: auto; scrollbar-width: none;
}
.tabs-wrapper::-webkit-scrollbar { display: none; }
.tabs-row { display: flex; gap: 8px; width: max-content; direction: rtl; }
.tab-chip {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 6px 14px; border-radius: 20px; font-size: 0.78rem;
    font-weight: 700; white-space: nowrap;
    border: 1.5px solid var(--border);
    background: var(--gray); color: var(--text); cursor: pointer;
}
.tab-chip.active {
    background: var(--primary); color: white;
    border-color: var(--primary);
    box-shadow: 0 2px 8px rgba(26,86,160,0.3);
}

.stChatMessage { direction: rtl !important; }
[data-testid="stChatMessageContent"] {
    border-radius: 18px !important; font-size: 0.9rem !important;
    line-height: 1.75 !important; direction: rtl !important;
    text-align: right !important; padding: 12px 16px !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: var(--white) !important; border: 1px solid var(--border) !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06) !important; color: var(--text) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: var(--primary) !important; color: white !important; border: none !important;
}
.loc-bar {
    background: #eef4ff; border: 1px solid #c7daf9;
    border-radius: 12px; padding: 8px 14px; margin: 8px 0;
    font-size: 0.82rem; color: var(--primary); font-weight: 600;
}
.loc-bar.active { background: #f0fdf4; border-color: #86efac; color: #15803d; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# البيانات الكاملة
# ═══════════════════════════════════════════════

HOSPITALS = [
    {"name": "مستشفى الجيزة العام",          "lat": 30.0131, "lng": 31.2089},
    {"name": "مستشفى أم المصريين",            "lat": 30.0050, "lng": 31.2150},
    {"name": "مستشفى الشيخ زايد التخصصي",    "lat": 30.0450, "lng": 30.9950},
    {"name": "مستشفى العجوزة العام",          "lat": 30.0520, "lng": 31.2130},
    {"name": "مستشفى الهرم العام",            "lat": 29.9950, "lng": 31.1550},
]

INVESTMENT = [
    {
        "name": "قطعة أرض – نزلة السمان",
        "location": "نزلة السمان، قريبة من الأهرامات",
        "activity": "مطعم سياحي / كافيه / بازار",
        "advantage": "كثافة سياحية عالية طوال العام",
        "score": 9.5,
        "reasoning": "أعلى معدلات جذب سياحي في المنطقة، طلب مستمر على الخدمات، عائد استثماري سريع.",
        "bestFor": "مطعم، كافيه، متجر هدايا",
        "lat": 29.9812, "lng": 31.1390
    },
    {
        "name": "محيط المتحف المصري الكبير GEM",
        "location": "محيط المتحف المصري الكبير",
        "activity": "مركز ترفيهي / خدمات سياحية",
        "advantage": "قربها من أهم المشروعات القومية السياحية",
        "score": 9.0,
        "reasoning": "مشروع قومي جديد، تدفق سياحي هائل متوقع، بنية تحتية حديثة.",
        "bestFor": "مركز ترفيهي، خدمات سياحية فاخرة",
        "lat": 29.9950, "lng": 31.1168
    },
    {
        "name": "منطقة المنيل – إطلالة نيلية",
        "location": "المنيل، قريبة من النيل",
        "activity": "مشروع نهري / مطعم عائم / كافيه نيلي",
        "advantage": "إطلالة مباشرة على النيل وموقع مركزي",
        "score": 8.5,
        "reasoning": "موقع استراتيجي يربط الجيزة بالقاهرة، إقبال كبير من السكان والسياح.",
        "bestFor": "مطعم عائم، كافيه نيلي",
        "lat": 30.0150, "lng": 31.2250
    },
]

RESTAURANTS = {
    "مصري": {
        "أهرامات": {"name": "مطعم فلفلة", "location": "نزلة السمان", "rating": "4.8/5", "specialty": "طواجن وكشري وشاورما", "note": "إطلالة خيالية على الأهرامات"},
        "مدينة":   {"name": "صبحي كابر",  "location": "الشيخ زايد",  "rating": "4.7/5", "specialty": "مقبلات ومشويات ممتازة", "note": "أجواء عائلية دافئة"},
    },
    "شرقي": {
        "أهرامات": {"name": "حدائق الأهرام لاونج", "location": "حدائق الأهرام", "rating": "4.7/5", "specialty": "كباب وشيش ومزة شرقية", "note": "جلسات مفتوحة وإطلالة ساحرة"},
        "مدينة":   {"name": "مطعم الطوب",           "location": "الدقي",         "rating": "4.6/5", "specialty": "مشويات طازة يومياً",    "note": "جودة عالية وأسعار معقولة"},
    },
    "إيطالي": {
        "أهرامات": {"name": "باستا كاسا", "location": "الشيخ زايد", "rating": "4.6/5", "specialty": "باستا وبيتزا وريزوتو", "note": "باستا إيطالية أصلية"},
        "مدينة":   {"name": "باستا كاسا", "location": "الشيخ زايد", "rating": "4.6/5", "specialty": "باستا وبيتزا وريزوتو", "note": "أفضل إيطالي في الجيزة"},
    },
    "آسيوي": {
        "أهرامات": {"name": "هانا سوشي",         "location": "المهندسين", "rating": "4.6/5", "specialty": "سوشي طازة يومياً",    "note": "أفضل سوشي في الجيزة"},
        "مدينة":   {"name": "التنين الذهبي", "location": "الجيزة",    "rating": "4.5/5", "specialty": "أكلات صينية ويابانية", "note": "ديم سام وسوشي"},
    },
    "بحري": {
        "أهرامات": {"name": "مطعم النيل للمأكولات البحرية", "location": "كورنيش الجيزة", "rating": "4.5/5", "specialty": "سمك وجمبري طازة", "note": "إطلالة نيلية رائعة"},
        "مدينة":   {"name": "سيلور",                        "location": "المهندسين",     "rating": "4.4/5", "specialty": "مأكولات بحرية متنوعة", "note": "أسعار معقولة"},
    },
}

HOTELS = {
    "اقتصادي": {
        "أهرامات": {"name": "Pyramids View Inn",  "price": "40-60$/ليلة",   "rating": "4.2/5", "note": "إطلالة رائعة وسعر مناسب"},
        "مدينة":   {"name": "جرين بلازا شقق",     "price": "50-65$/ليلة",   "rating": "4.1/5", "note": "وسط المدينة وقريب من المول"},
    },
    "متوسط": {
        "أهرامات": {"name": "ستينبرجر بيراميدز", "price": "80-150$/ليلة",  "rating": "4.5/5", "note": "حمام سباحة وإفطار شامل"},
        "مدينة":   {"name": "ستيلا شقق فندقية",  "price": "85-130$/ليلة",  "rating": "4.4/5", "note": "مطعم وجيم وخدمات كونسيرج"},
    },
    "فاخر": {
        "أهرامات": {"name": "ماريوت مينا هاوس", "price": "250-400$/ليلة", "rating": "4.8/5", "note": "5 نجوم مع إطلالة مباشرة على الأهرامات"},
        "مدينة":   {"name": "فور سيزنز جيزة",   "price": "280-450$/ليلة", "rating": "4.9/5", "note": "منتجع شامل مع سبا وجيم عالمي"},
    },
}

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
    ],
    "السجل التجاري": [
        "استخراج شهادة قيد في السجل التجاري",
        "تعديل بيانات السجل التجاري", "تجديد قيد السجل التجاري"
    ],
}

TOURISM_PLANS = {
    "1": """📅 برنامج يوم واحد في الجيزة ⭐ 4.9/5

🌅 الصباح (4 ساعات):
🔺 أهرامات الجيزة وأبو الهول
📸 ركوب جمال والتقاط صور بانورامية

🌙 المساء:
🎭 عرض الصوت والضوء بالأهرامات
🍽️ عشاء في مطعم يطل على الأهرامات

💡 نصيحة: ابدأ بدري الساعة 7 صباحاً لتجنب الزحام!""",

    "2": """📅 برنامج يومين في الجيزة ⭐ 4.8/5

📍 اليوم الأول – المعالم التاريخية:
🌅 صباحاً: أهرامات الجيزة وأبو الهول (4 ساعات)
🎭 مساءً: عرض الصوت والضوء بالأهرامات

📍 اليوم الثاني – المتاحف والثقافة:
🏛️ صباحاً: المتحف المصري الكبير GEM (3 ساعات)
🛍️ مساءً: جولة في قرية الحرانية (سجاد يدوي وفن)

💡 نصيحة: احجز تذاكر GEM مسبقاً!""",

    "3": """📅 برنامج 3 أيام في الجيزة ⭐ 4.7/5

📍 اليوم الأول – المعالم التاريخية:
🔺 أهرامات الجيزة + أبو الهول صباحاً
🎭 عرض الصوت والضوء مساءً

📍 اليوم الثاني – المتاحف والتسوق:
🏛️ المتحف المصري الكبير GEM صباحاً
🛍️ قرية الحرانية أو كورنيش الجيزة مساءً

📍 اليوم الثالث – الطبيعة والترفيه:
🌳 حديقة الأورمان أو حديقة الحيوان صباحاً
🚤 رحلة نيلية بالفلوكة عند الغروب

💡 نصيحة: احجز فندق قريب من الأهرامات لتوفير الوقت!""",

    "7": """📅 برنامج أسبوع كامل في الجيزة ⭐ 4.9/5

📍 اليوم 1: أهرامات الجيزة + أبو الهول + عرض الصوت والضوء
📍 اليوم 2: المتحف المصري الكبير GEM (يوم كامل)
📍 اليوم 3: حديقة الأورمان + حديقة الحيوان
📍 اليوم 4: رحلة نيلية + كورنيش الجيزة + مطاعم نيلية
📍 اليوم 5: قرية الحرانية (سجاد وفنون) + التسوق
📍 اليوم 6: منطقة المنيل + المتاحف الصغيرة
📍 اليوم 7: يوم حر + سوق الجمعة + تسوق هدايا

💡 نصيحة: استخدم Uber أو Careem للتنقل بين المناطق!"""
}

# ═══════════════════════════════════════════════
# دوال الردود المباشرة
# ═══════════════════════════════════════════════

def haversine(lat1, lng1, lat2, lng2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def get_hospitals_response():
    loc = st.session_state.location
    if loc:
        lat, lng = loc["lat"], loc["lng"]
        sorted_h = sorted(HOSPITALS, key=lambda h: haversine(lat, lng, h["lat"], h["lng"]))
        lines = ["🏥 **أقرب المستشفيات لموقعك:**\n"]
        for i, h in enumerate(sorted_h[:3], 1):
            dist = haversine(lat, lng, h["lat"], h["lng"])
            maps_url = f"https://www.google.com/maps/dir/{lat},{lng}/{h['lat']},{h['lng']}"
            lines.append(f"**{i}. {h['name']}**\n📍 المسافة: {dist:.1f} كم\n🗺️ [افتح في خرائط جوجل]({maps_url})\n")
        lines.append(f"\n🔍 [ابحث عن مزيد من المستشفيات القريبة](https://www.google.com/maps/search/مستشفى/@{lat},{lng},14z)")
        return "\n".join(lines)
    else:
        lines = ["🏥 **مستشفيات محافظة الجيزة:**\n"]
        for h in HOSPITALS:
            maps_url = f"https://www.google.com/maps?q={h['lat']},{h['lng']}"
            lines.append(f"• **{h['name']}** — [الموقع]({maps_url})")
        lines.append("\n📍 *اضغط زرار 'موقعي' لعرض أقرب مستشفى ليك تحديداً*")
        return "\n".join(lines)

def get_investment_response():
    lines = ["📈 **فرص الاستثمار في محافظة الجيزة:**\n"]
    for opp in INVESTMENT:
        maps_url = f"https://www.google.com/maps?q={opp['lat']},{opp['lng']}"
        lines.append(f"""**⭐ {opp['name']} — تقييم {opp['score']}/10**
📍 الموقع: {opp['location']}
🏗️ النشاط: {opp['activity']}
✨ الميزة: {opp['advantage']}
💡 التحليل: {opp['reasoning']}
🎯 الأنسب لـ: {opp['bestFor']}
🗺️ [شوف الموقع على الخريطة]({maps_url})
""")
    lines.append("💼 للتواصل مع وحدة الاستثمار: تواصل مع محافظة الجيزة الرسمية")
    return "\n".join(lines)

def get_digital_services_response():
    lines = ["💻 **خدمات مصر الرقمية المتاحة:**\n🔗 https://digital.gov.eg\n"]
    for cat, services in DIGITAL_SERVICES.items():
        lines.append(f"**📌 {cat}:**")
        for s in services:
            lines.append(f"• {s}")
        lines.append("")
    lines.append("✅ سجّل بالرقم القومي على المنصة وابدأ الخدمة مباشرة")
    return "\n".join(lines)

def get_tourism_response():
    return """🏛️ **مرحباً بك في الجيزة!**

كم يوم بتفكر تقضي؟

• **يوم واحد** — جولة مكثفة بالمعالم الكبرى
• **يومين** — أهرامات + المتحف المصري الكبير
• **3 أيام** — برنامج كامل وشامل
• **أسبوع** — تجربة الجيزة بالكامل

اكتب عدد الأيام وهجهزلك البرنامج! 🗺️"""

def get_restaurants_response():
    return """🍽️ **أهلاً! عايز تاكل إيه؟**

اختار نوع الطعام:

• 🍲 **مصري** — أطباق تقليدية أصيلة
• 🔥 **شرقي** — مشويات وكباب
• 🍝 **إيطالي** — باستا وبيتزا
• 🥢 **آسيوي** — سوشي وأكلات شرقية
• 🦐 **بحري** — مأكولات بحرية طازة

اكتب نوع الطعام وهرشحلك أفضل مطعم! 😊"""

def get_hotels_response():
    return """🏨 **بتدور على فندق في الجيزة؟**

اختار ميزانيتك:

• 💰 **اقتصادي** — حتى 65$/ليلة
• ⭐ **متوسط** — 80-150$/ليلة
• 👑 **فاخر** — أكثر من 150$/ليلة

اكتب ميزانيتك وهرشحلك أفضل فندق! 🏨"""

def get_accessibility_response():
    return """♿ **خدمات ذوي الهمم في الجيزة**

أهلاً! أنا هنا أساعدك. محتاج خدمة إيه؟

• 📋 **سجل مدني** — استخراج وثائق
• 📮 **مكتب بريد** — خدمات بريدية
• 🛒 **مكتب تموين** — خدمات البطاقة التموينية
• 🏥 **خدمات صحية** — مستشفيات وعيادات

وعايز مكان بإمكانية وصول:
• 🦽 **منحدر** للكراسي المتحركة
• 🪟 **شباك أرضي** مخصص
• 🛗 **مصعد** مجهز

اكتب احتياجك وهساعدك! 🤝"""

def get_complaints_response():
    return """📋 **تقديم شكوى لمحافظة الجيزة**

يمكنك تقديم شكواك عبر:

🌐 **الموقع الرسمي:** [محافظة الجيزة](https://www.giza.gov.eg)
📞 **خط نجدة المواطن:** 16555
📱 **منصة مصر الرقمية:** [digital.gov.eg](https://digital.gov.eg)

أنواع الشكاوى المقبولة:
• إنارة الشوارع 💡
• النظافة والقمامة 🗑️
• الطرق والحفريات 🚧
• المخالفات والإشغالات ⚠️

هل محتاج مساعدة في أي نوع شكوى تاني؟"""

TAB_RESPONSES = {
    "مستشفيات":    get_hospitals_response,
    "السياحة":     get_tourism_response,
    "الاستثمار":   get_investment_response,
    "مصر الرقمية": get_digital_services_response,
    "مطاعم":       get_restaurants_response,
    "فنادق":       get_hotels_response,
    "ذوي الهمم":  get_accessibility_response,
    "الشكاوى":    get_complaints_response,
}

# ═══════════════════════════════════════════════
# معالجة المحادثة الذكية
# ═══════════════════════════════════════════════

SYSTEM_PROMPT = """أنت مساعد ذكي رسمي لمحافظة الجيزة، مصر. اسمك 'جيزا'.
تتكلم عربي وإنجليزي وترد بنفس لغة المستخدم.

أنت تساعد في:
1. المطاعم: اسأل نوع الطعام ثم الموقع (أهرامات / مدينة) ثم قدم توصية واحدة محددة
2. الفنادق: اسأل الميزانية (اقتصادي/متوسط/فاخر) ثم الموقع ثم قدم توصية
3. السياحة: اسأل كم يوم ثم قدم البرنامج
4. الاستثمار: اسأل الاسم ثم النشاط ثم المنطقة ثم الميزانية ثم قدم الفرص
5. الخدمات الحكومية: وجّه لـ digital.gov.eg
6. المستشفيات: وجّه للمستشفى الأقرب
7. الشكاوى: وجّه للموقع الرسمي

قواعد صارمة:
- جملة أو جملتين فقط في كل رد ما لم يطلب تفاصيل
- سؤال واحد فقط في كل رد
- لغة طبيعية ودية
- تذكر المحادثة السابقة دائماً"""

@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

def ai_response(user_text):
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
        messages=msgs, temperature=0.7, max_tokens=600
    )
    reply = resp.choices[0].message.content

    # كشف الردود المرتبطة بالداتا وإضافة معلومات حقيقية
    lower = user_text.lower()

    # مطاعم
    for cuisine in ["مصري", "شرقي", "إيطالي", "آسيوي", "بحري"]:
        if cuisine in user_text:
            for loc_key in ["أهرامات", "مدينة", "وسط"]:
                if loc_key in user_text or "وسط" in user_text:
                    loc = "مدينة" if "وسط" in user_text or "مدينة" in user_text else "أهرامات"
                    if cuisine in RESTAURANTS and loc in RESTAURANTS[cuisine]:
                        r = RESTAURANTS[cuisine][loc]
                        maps_q = f"مطعم+{r['name'].replace(' ', '+')}"
                        maps_url = f"https://www.google.com/maps/search/{maps_q}"
                        reply += f"\n\n🏆 **{r['name']}**\n📍 {r['location']} — ⭐ {r['rating']}\n🍽️ {r['specialty']}\n✨ {r['note']}\n🗺️ [الموقع على الخريطة]({maps_url})"
                    break

    # سياحة - عدد الأيام
    for days_key, days_val in [("يوم", "1"), ("يومين", "2"), ("يومان", "2"), ("3", "3"), ("ثلاث", "3"), ("أسبوع", "7"), ("7", "7")]:
        if days_key in user_text and days_val in TOURISM_PLANS:
            reply = TOURISM_PLANS[days_val]
            break

    # فنادق
    for budget in ["اقتصادي", "متوسط", "فاخر"]:
        if budget in user_text:
            for loc_key in ["أهرامات", "مدينة", "وسط", "زايد"]:
                if loc_key in user_text:
                    loc = "مدينة" if loc_key in ["مدينة", "وسط", "زايد"] else "أهرامات"
                    if budget in HOTELS and loc in HOTELS[budget]:
                        h = HOTELS[budget][loc]
                        reply += f"\n\n🏨 **{h['name']}**\n💰 {h['price']} — ⭐ {h['rating']}\n✨ {h['note']}"
                    break

    st.session_state.messages.append({"role": "assistant", "content": reply})

# ═══════════════════════════════════════════════
# التابات
# ═══════════════════════════════════════════════
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

# ─── تهيئة الحالة ──────────────────────────────
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

# ═══════════════════════════════════════════════
# الواجهة
# ═══════════════════════════════════════════════

# الهيدر
st.markdown("""
<div class="app-header">
  <div style="display:flex;align-items:center;gap:10px">
    <div class="header-avatar">🏛️<span class="online-dot"></span></div>
    <div>
      <div style="font-size:.95rem;font-weight:700">مساعدك الذكي ✨</div>
      <div style="font-size:.7rem;opacity:.75">محافظة الجيزة • متصل الآن</div>
    </div>
  </div>
  <div style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.3);color:white;border-radius:8px;padding:4px 10px;font-size:.72rem;font-weight:700">EN 🌐</div>
</div>
""", unsafe_allow_html=True)

# التابات المرئية
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
            # رد مباشر من الداتا بدون AI
            response_fn = TAB_RESPONSES.get(label)
            if response_fn:
                reply = response_fn()
                st.session_state.messages.append({"role": "user", "content": f"اضغط تاب: {label}"})
                st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

# شريط الموقع
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
        st.markdown('<div class="loc-bar active">✅ موقعك محدد — جاهز لعرض أقرب الخدمات</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="loc-bar">📍 اضغط لتحديد موقعك وعرض أقرب المستشفيات والمطاعم</div>', unsafe_allow_html=True)

# المحادثة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# الإدخال
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
        ai_response(prompt)
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
                ai_response(voice_text)
                st.rerun()
        except Exception:
            st.error("حصل خطأ في الصوت، جرب تاني.")

# مسح المحادثة
if len(st.session_state.messages) > 1:
    if st.button("🗑️ مسح المحادثة", use_container_width=True, key="clear"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "أهلاً بك 👋\nأنا مساعد الجيزة الذكي ✨\nيمكنني مساعدتك في الاستثمار، السياحة، الخدمات الحكومية وأكثر.\nاكتب ما تحتاجه وسأساعدك فوراً!"
        }]
        st.session_state.last_audio_id = None
        st.session_state.active_tab = None
        st.rerun()
