import streamlit as st
from streamlit_mic_recorder import mic_recorder
from streamlit_js_eval import get_geolocation
from groq import Groq
import io, math

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

/* إخفاء أزرار Streamlit للتابات */
div[data-testid="stHorizontalBlock"] button {
    visibility: hidden; height: 0 !important;
    padding: 0 !important; margin: 0 !important; border: none !important;
}

/* الهيدر */
.app-header {
    background: var(--primary); color: white;
    padding: 14px 16px; display: flex;
    align-items: center; justify-content: space-between;
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

/* التابات */
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

/* فقاعات الشات */
.stChatMessage { direction: rtl !important; }
[data-testid="stChatMessageContent"] {
    border-radius: 18px !important; font-size: 0.9rem !important;
    line-height: 1.75 !important; direction: rtl !important;
    text-align: right !important; padding: 12px 16px !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: var(--white) !important; border: 1px solid var(--border) !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: var(--primary) !important; color: white !important; border: none !important;
}

/* بانل مصر الرقمية */
.digital-panel { background: white; border-radius: 16px; overflow: hidden; margin: 8px 0; border: 1px solid var(--border); }
.search-bar {
    width: 100%; padding: 10px 14px; border: 1.5px solid var(--border);
    border-radius: 12px; font-size: 0.85rem; direction: rtl;
    background: var(--gray); outline: none; margin-bottom: 10px;
}
.search-bar:focus { border-color: var(--primary); background: white; }
.filter-row { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 8px; scrollbar-width: none; direction: rtl; }
.filter-row::-webkit-scrollbar { display: none; }
.filter-chip {
    padding: 5px 12px; border-radius: 15px; font-size: 0.75rem;
    font-weight: 700; white-space: nowrap; cursor: pointer;
    border: 1.5px solid var(--border); background: var(--gray); color: var(--text);
    display: inline-flex; align-items: center; gap: 4px;
}
.filter-chip.active { background: var(--primary); color: white; border-color: var(--primary); }

.service-card {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 12px; background: white; border: 1px solid var(--border);
    border-radius: 12px; margin-bottom: 8px; text-decoration: none;
    color: var(--text); transition: all 0.2s;
}
.service-card:hover { border-color: var(--primary); background: #eef4ff; }
.service-icon {
    width: 36px; height: 36px; border-radius: 10px;
    background: #eef4ff; display: flex; align-items: center;
    justify-content: center; font-size: 1rem; flex-shrink: 0;
}
.service-name { font-size: 0.82rem; font-weight: 700; margin-bottom: 2px; }
.service-desc { font-size: 0.72rem; color: var(--text-light); line-height: 1.4; }
.cat-header {
    font-size: 0.8rem; font-weight: 700; color: var(--primary);
    padding: 8px 0 6px; border-bottom: 1px solid var(--border);
    margin-bottom: 8px; display: flex; align-items: center; gap: 6px;
}

/* بطاقات الاستثمار */
.invest-card {
    background: white; border: 1px solid var(--border);
    border-radius: 16px; padding: 16px; margin-bottom: 12px;
    transition: all 0.2s;
}
.invest-card:hover { border-color: var(--primary); box-shadow: 0 4px 16px rgba(26,86,160,0.1); }
.score-badge {
    display: inline-block; background: var(--primary); color: white;
    font-size: 0.72rem; font-weight: 700; padding: 3px 10px;
    border-radius: 20px; margin-bottom: 8px;
}
.invest-title { font-size: 0.9rem; font-weight: 700; margin-bottom: 6px; }
.invest-detail { font-size: 0.78rem; color: var(--text-light); margin-bottom: 4px; }
.maps-link {
    display: inline-flex; align-items: center; gap: 4px;
    background: var(--primary); color: white; padding: 6px 14px;
    border-radius: 20px; font-size: 0.75rem; font-weight: 700;
    text-decoration: none; margin-top: 8px;
}

/* بطاقات المستشفيات */
.hospital-card {
    background: white; border: 1px solid var(--border);
    border-radius: 12px; padding: 12px 16px; margin-bottom: 8px;
    display: flex; align-items: center; justify-content: space-between;
}
.hospital-name { font-size: 0.85rem; font-weight: 700; }
.hospital-dist { font-size: 0.75rem; color: var(--text-light); margin-top: 2px; }
.maps-btn {
    background: #eef4ff; color: var(--primary); padding: 6px 12px;
    border-radius: 10px; font-size: 0.72rem; font-weight: 700;
    text-decoration: none; white-space: nowrap; flex-shrink: 0;
}

/* loc bar */
.loc-bar {
    background: #eef4ff; border: 1px solid #c7daf9;
    border-radius: 12px; padding: 8px 14px; margin: 8px 0;
    font-size: 0.82rem; color: var(--primary); font-weight: 600;
}
.loc-bar.ok { background: #f0fdf4; border-color: #86efac; color: #15803d; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# البيانات الكاملة
# ═══════════════════════════════════════════

DIGITAL_SERVICES = [
    # التموين
    {"cat": "التموين", "icon": "🛒", "name": "ضم أفراد أسرتي", "desc": "ضم أفراد أسرتك غير المقيدين على بطاقتك التموينية", "href": "https://digital.gov.eg/categories/terms/ضم-أفراد-أسرتى"},
    {"cat": "التموين", "icon": "🛒", "name": "إصدار بطاقة تموين جديدة", "desc": "إصدار بطاقة تموين جديدة", "href": "https://digital.gov.eg/categories/terms/إصدار-بطاقة-تموين-جديدة"},
    {"cat": "التموين", "icon": "🛒", "name": "الاستعلام عن صرف", "desc": "الاستعلام عن صرف البطاقة التموينية", "href": "https://digital.gov.eg"},
    {"cat": "التموين", "icon": "🛒", "name": "إصدار بدل تالف أو فاقد لبطاقة تموين", "desc": "إصدار بدل تالف أو فاقد لبطاقتك التموينية", "href": "https://digital.gov.eg"},
    {"cat": "التموين", "icon": "🛒", "name": "تفعيل بطاقة تموين", "desc": "تفعيل بطاقتك التموينية", "href": "https://digital.gov.eg"},
    {"cat": "التموين", "icon": "🛒", "name": "فصل نفسي", "desc": "فصل نفسك من البطاقة التموينية الحالية واستخراج بطاقة جديدة", "href": "https://digital.gov.eg"},
    {"cat": "التموين", "icon": "🛒", "name": "نقل من محافظة إلى أخرى", "desc": "نقل بطاقتك التموينية من محافظة لأخرى", "href": "https://digital.gov.eg"},
    {"cat": "التموين", "icon": "🛒", "name": "حذف طالب", "desc": "حذف فرد من البطاقة التموينية", "href": "https://digital.gov.eg"},
    {"cat": "التموين", "icon": "🛒", "name": "شراء سلع إضافية", "desc": "شراء سلع إضافية عبر البطاقة التموينية", "href": "https://digital.gov.eg"},
    # المرور
    {"cat": "المرور والمركبات", "icon": "🚗", "name": "تجديد رخصة قيادة", "desc": "تجديد رخصة القيادة الخاصة بك إلكترونياً", "href": "https://digital.gov.eg"},
    {"cat": "المرور والمركبات", "icon": "🚗", "name": "إصدار رخصة قيادة بدل تالف/فاقد", "desc": "إصدار بدل تالف أو فاقد لرخصة القيادة", "href": "https://digital.gov.eg"},
    {"cat": "المرور والمركبات", "icon": "🚗", "name": "تجديد رخصة تسيير مركبة", "desc": "تجديد رخصة تسيير المركبة", "href": "https://digital.gov.eg"},
    {"cat": "المرور والمركبات", "icon": "🚗", "name": "الاستعلام عن المخالفات المرورية", "desc": "الاستعلام عن المخالفات المرورية برقمك القومي", "href": "https://digital.gov.eg"},
    {"cat": "المرور والمركبات", "icon": "🚗", "name": "سداد المخالفات المرورية", "desc": "سداد المخالفات المرورية إلكترونياً", "href": "https://digital.gov.eg"},
    {"cat": "المرور والمركبات", "icon": "🚗", "name": "إصدار رخصة تسيير مركبة جديدة", "desc": "إصدار رخصة تسيير لأول مرة", "href": "https://digital.gov.eg"},
    {"cat": "المرور والمركبات", "icon": "🚗", "name": "الاستعلام عن بيانات مركبة", "desc": "الاستعلام عن بيانات المركبة برقم اللوحة", "href": "https://digital.gov.eg"},
    {"cat": "المرور والمركبات", "icon": "🚗", "name": "نقل ملكية مركبة", "desc": "طلب نقل ملكية مركبة إلكترونياً", "href": "https://digital.gov.eg"},
    # المعاشات
    {"cat": "المعاشات والتأمينات", "icon": "💰", "name": "الاستعلام عن مستحقات المعاش", "desc": "الاستعلام عن قيمة المعاش المستحق", "href": "https://digital.gov.eg"},
    {"cat": "المعاشات والتأمينات", "icon": "💰", "name": "تقديم طلب صرف معاش", "desc": "تقديم طلب صرف معاش لأول مرة", "href": "https://digital.gov.eg"},
    {"cat": "المعاشات والتأمينات", "icon": "💰", "name": "تعديل بيانات المعاش", "desc": "تعديل البيانات الشخصية المرتبطة بالمعاش", "href": "https://digital.gov.eg"},
    {"cat": "المعاشات والتأمينات", "icon": "💰", "name": "الاستعلام عن المدد التأمينية", "desc": "الاستعلام عن المدد التأمينية السابقة", "href": "https://digital.gov.eg"},
    # التوثيق
    {"cat": "التوثيق والشهر العقاري", "icon": "📄", "name": "إصدار توكيل عام", "desc": "إصدار توكيل عام إلكتروني", "href": "https://digital.gov.eg"},
    {"cat": "التوثيق والشهر العقاري", "icon": "📄", "name": "إصدار توكيل خاص", "desc": "إصدار توكيل خاص لمهمة محددة", "href": "https://digital.gov.eg"},
    {"cat": "التوثيق والشهر العقاري", "icon": "📄", "name": "الاستعلام عن ملكية عقارية", "desc": "الاستعلام عن ملكية عقار برقم القيد", "href": "https://digital.gov.eg"},
    {"cat": "التوثيق والشهر العقاري", "icon": "📄", "name": "طلب عقد زواج", "desc": "تقديم طلب إصدار عقد زواج", "href": "https://digital.gov.eg"},
    {"cat": "التوثيق والشهر العقاري", "icon": "📄", "name": "طلب عقد بيع", "desc": "تقديم طلب إصدار عقد بيع", "href": "https://digital.gov.eg"},
    # السجل التجاري
    {"cat": "السجل التجاري", "icon": "🏢", "name": "استخراج شهادة قيد في السجل التجاري", "desc": "استخراج شهادة قيد تجاري", "href": "https://digital.gov.eg"},
    {"cat": "السجل التجاري", "icon": "🏢", "name": "تعديل بيانات السجل التجاري", "desc": "تعديل بيانات الشركة في السجل التجاري", "href": "https://digital.gov.eg"},
    {"cat": "السجل التجاري", "icon": "🏢", "name": "تجديد قيد السجل التجاري", "desc": "تجديد قيد المنشأة في السجل التجاري", "href": "https://digital.gov.eg"},
    # الإسكان
    {"cat": "الإسكان الاجتماعي", "icon": "🏠", "name": "تقديم طلب حجز وحدة سكنية", "desc": "تقديم طلب حجز وحدة سكنية في مشروعات الإسكان الاجتماعي", "href": "https://digital.gov.eg"},
    {"cat": "الإسكان الاجتماعي", "icon": "🏠", "name": "الاستعلام عن طلب الإسكان", "desc": "الاستعلام عن حالة طلب الإسكان الخاص بك", "href": "https://digital.gov.eg"},
    {"cat": "الإسكان الاجتماعي", "icon": "🏠", "name": "سداد أقساط الإسكان الاجتماعي", "desc": "سداد أقساط الوحدة السكنية إلكترونياً", "href": "https://digital.gov.eg"},
]

HOSPITALS = [
    {"name": "مستشفى الجيزة العام",       "lat": 30.0131, "lng": 31.2089},
    {"name": "مستشفى أم المصريين",         "lat": 30.0050, "lng": 31.2150},
    {"name": "مستشفى الشيخ زايد التخصصي", "lat": 30.0450, "lng": 30.9950},
    {"name": "مستشفى العجوزة العام",       "lat": 30.0520, "lng": 31.2130},
    {"name": "مستشفى الهرم العام",         "lat": 29.9950, "lng": 31.1550},
]

INVESTMENT = [
    {"name": "قطعة أرض – نزلة السمان", "location": "نزلة السمان، قريبة من الأهرامات",
     "activity": "مطعم سياحي / كافيه / بازار", "advantage": "كثافة سياحية عالية طوال العام",
     "score": 9.5, "reasoning": "أعلى معدلات جذب سياحي، طلب مستمر، عائد استثماري سريع.",
     "bestFor": "مطعم، كافيه، متجر هدايا", "lat": 29.9812, "lng": 31.1390},
    {"name": "محيط المتحف المصري الكبير GEM", "location": "محيط المتحف المصري الكبير",
     "activity": "مركز ترفيهي / خدمات سياحية", "advantage": "قرب من أهم المشروعات القومية",
     "score": 9.0, "reasoning": "مشروع قومي جديد، تدفق سياحي هائل متوقع، بنية تحتية حديثة.",
     "bestFor": "مركز ترفيهي، خدمات سياحية فاخرة", "lat": 29.9950, "lng": 31.1168},
    {"name": "منطقة المنيل – إطلالة نيلية", "location": "المنيل، قريبة من النيل",
     "activity": "مشروع نهري / مطعم عائم", "advantage": "إطلالة مباشرة على النيل",
     "score": 8.5, "reasoning": "موقع استراتيجي يربط الجيزة بالقاهرة، إقبال كبير.",
     "bestFor": "مطعم عائم، كافيه نيلي", "lat": 30.0150, "lng": 31.2250},
]

TOURISM_PLANS = {
    "1": "📅 **يوم واحد في الجيزة** ⭐4.9\n\n🌅 **صباحاً:** أهرامات الجيزة + أبو الهول (4 ساعات)\n📸 ركوب جمال وصور بانورامية\n\n🌙 **مساءً:** عرض الصوت والضوء بالأهرامات\n🍽️ عشاء في مطعم مع إطلالة على الأهرامات\n\n💡 ابدأ الساعة 7 صباحاً لتجنب الزحام!",
    "2": "📅 **يومين في الجيزة** ⭐4.8\n\n**اليوم 1 – التاريخ:**\n🔺 أهرامات الجيزة + أبو الهول صباحاً\n🎭 عرض الصوت والضوء مساءً\n\n**اليوم 2 – الثقافة:**\n🏛️ المتحف المصري الكبير GEM (3 ساعات)\n🛍️ قرية الحرانية — سجاد يدوي وفن مصري\n\n💡 احجز تذاكر GEM مسبقاً!",
    "3": "📅 **3 أيام في الجيزة** ⭐4.7\n\n**اليوم 1:** أهرامات + أبو الهول + عرض صوت وضوء\n**اليوم 2:** المتحف المصري الكبير GEM + قرية الحرانية\n**اليوم 3:** حديقة الأورمان + رحلة نيلية بالفلوكة عند الغروب\n\n💡 افضل فندق: ماريوت مينا هاوس لإطلالة الأهرامات!",
    "7": "📅 **أسبوع في الجيزة** ⭐4.9\n\n**يوم 1:** أهرامات + أبو الهول + عرض صوت وضوء\n**يوم 2:** المتحف المصري الكبير GEM\n**يوم 3:** حديقة الأورمان + حديقة الحيوان\n**يوم 4:** رحلة نيلية + كورنيش الجيزة\n**يوم 5:** قرية الحرانية + تسوق\n**يوم 6:** منطقة المنيل + متاحف صغيرة\n**يوم 7:** سوق الجمعة + هدايا تذكارية\n\n💡 استخدم Uber للتنقل بين المناطق!",
}

SYSTEM_PROMPT = """أنت مساعد ذكي رسمي لمحافظة الجيزة، مصر. اسمك 'جيزا'. تتكلم عربي وإنجليزي وترد بنفس لغة المستخدم.

تساعد في: المطاعم (اسأل النوع ثم الموقع)، الفنادق (اسأل الميزانية ثم الموقع)، السياحة (اسأل كم يوم)، الاستثمار (اسأل الاسم، النشاط، المنطقة، الميزانية)، الخدمات الحكومية (digital.gov.eg)، المستشفيات، الشكاوى.

قواعد: جملتين بحد أقصى، سؤال واحد فقط، لغة ودية، تذكر المحادثة."""

# ─── Groq ──────────────────────────────────────
@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

def haversine(lat1, lng1, lat2, lng2):
    R = 6371
    dlat = math.radians(lat2-lat1); dlng = math.radians(lng2-lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlng/2)**2
    return R*2*math.asin(math.sqrt(a))

# ─── تهيئة ──────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"assistant","content":"أهلاً بك 👋\nأنا مساعد الجيزة الذكي ✨\nيمكنني مساعدتك في الاستثمار، السياحة، الخدمات الحكومية وأكثر.\nاكتب ما تحتاجه وسأساعدك فوراً!"}]
if "last_audio_id" not in st.session_state: st.session_state.last_audio_id = None
if "location"     not in st.session_state: st.session_state.location = None
if "active_tab"   not in st.session_state: st.session_state.active_tab = "chat"
if "dig_search"   not in st.session_state: st.session_state.dig_search = ""
if "dig_cat"      not in st.session_state: st.session_state.dig_cat = "الكل"

TABS = [("💬","chat","محادثة حرة"),("💻","digital","مصر الرقمية"),("📈","investment","الاستثمار"),
        ("🏛️","tourism","السياحة"),("🏥","hospitals","مستشفيات"),("🍽️","restaurants","مطاعم"),
        ("🏨","hotels","فنادق"),("📋","complaints","شكاوى")]

# ═══ الهيدر ════════════════════════════════════
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

# ═══ التابات المرئية ════════════════════════════
active = st.session_state.active_tab
tabs_html = '<div class="tabs-wrapper"><div class="tabs-row">'
for icon, tid, label in TABS:
    css = "active" if tid == active else ""
    tabs_html += f'<div class="tab-chip {css}">{icon} {label}</div>'
tabs_html += '</div></div>'
st.markdown(tabs_html, unsafe_allow_html=True)

# أزرار مخفية وظيفية
cols = st.columns(len(TABS))
for i, (icon, tid, label) in enumerate(TABS):
    with cols[i]:
        if st.button(label, key=f"tab_{tid}"):
            st.session_state.active_tab = tid
            st.rerun()

# ═══ شريط الموقع ════════════════════════════════
lc1, lc2 = st.columns([4,1])
with lc2:
    if st.button("📍 موقعي", use_container_width=True, key="loc_btn"):
        loc = get_geolocation()
        if loc and "coords" in loc:
            st.session_state.location = {"lat": loc["coords"]["latitude"], "lng": loc["coords"]["longitude"]}
            st.rerun()
with lc1:
    if st.session_state.location:
        st.markdown('<div class="loc-bar ok">✅ موقعك محدد — جاهز لعرض أقرب الخدمات</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="loc-bar">📍 اضغط لتحديد موقعك وعرض أقرب المستشفيات والمطاعم</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# محتوى كل تاب
# ═══════════════════════════════════════════════
tab = st.session_state.active_tab

# ── 1. محادثة حرة ──────────────────────────────
if tab == "chat":
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    def send_msg(text):
        full = text
        if st.session_state.location:
            lat=st.session_state.location["lat"]; lng=st.session_state.location["lng"]
            full = f"{text}\n[موقع المستخدم: lat={lat}, lng={lng}]"
        st.session_state.messages.append({"role":"user","content":text})
        client = get_client()
        msgs = [{"role":"system","content":SYSTEM_PROMPT}]
        for i,m in enumerate(st.session_state.messages):
            msgs.append({"role":m["role"],"content": full if i==len(st.session_state.messages)-1 else m["content"]})
        resp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=msgs, temperature=0.7, max_tokens=600)
        st.session_state.messages.append({"role":"assistant","content":resp.choices[0].message.content})

    ic, mc = st.columns([6,1])
    with ic: prompt = st.chat_input("اكتب سؤالك هنا...")
    with mc:
        audio = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", just_once=True, use_container_width=True, key="mic")

    if prompt:
        with st.spinner("جيزا بتفكر..."): send_msg(prompt)
        st.rerun()

    if audio and audio["id"] != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio["id"]
        with st.spinner("🎤 جيزا بتسمعك..."):
            try:
                client = get_client()
                ab = io.BytesIO(audio["bytes"]); ab.name = "audio.wav"
                tr = client.audio.transcriptions.create(model="whisper-large-v3", file=ab, language="ar")
                vt = tr.text.strip()
                if vt:
                    st.info(f"🎤 قلت: {vt}")
                    send_msg(vt)
                    st.rerun()
            except: st.error("خطأ في الصوت، جرب تاني.")

    if len(st.session_state.messages) > 1:
        if st.button("🗑️ مسح المحادثة", use_container_width=True, key="clear"):
            st.session_state.messages = [{"role":"assistant","content":"أهلاً بك 👋\nأنا مساعد الجيزة الذكي ✨\nيمكنني مساعدتك في الاستثمار، السياحة، الخدمات الحكومية وأكثر.\nاكتب ما تحتاجه وسأساعدك فوراً!"}]
            st.rerun()

# ── 2. مصر الرقمية ─────────────────────────────
elif tab == "digital":
    st.markdown("### 💻 خدمات مصر الرقمية")
    st.caption("🔗 digital.gov.eg")

    # سيرش
    search = st.text_input("", placeholder="🔍 ابحث في الخدمات...", key="dig_search_input", label_visibility="collapsed")

    # فلاتر الفئات
    cats = ["الكل"] + sorted(list(set(s["cat"] for s in DIGITAL_SERVICES)))
    cat_counts = {c: sum(1 for s in DIGITAL_SERVICES if s["cat"]==c) for c in cats[1:]}

    cols_f = st.columns(len(cats))
    for i, cat in enumerate(cats):
        with cols_f[i]:
            label = f"{cat} ({cat_counts.get(cat,'')})" if cat != "الكل" else f"الكل ({len(DIGITAL_SERVICES)})"
            if st.button(label, key=f"cat_{cat}", use_container_width=True):
                st.session_state.dig_cat = cat
                st.rerun()

    selected_cat = st.session_state.dig_cat

    # فلترة
    filtered = [s for s in DIGITAL_SERVICES if
        (selected_cat == "الكل" or s["cat"] == selected_cat) and
        (not search or search in s["name"] or search in s["desc"])
    ]

    # تجميع حسب الفئة
    grouped = {}
    for s in filtered:
        grouped.setdefault(s["cat"], []).append(s)

    if not filtered:
        st.info("لا توجد خدمات مطابقة للبحث")
    else:
        for cat, services in grouped.items():
            st.markdown(f'<div class="cat-header">{services[0]["icon"]} {cat} <span style="color:var(--text-light);font-size:.7rem">({len(services)})</span></div>', unsafe_allow_html=True)
            for s in services:
                st.markdown(f"""
                <a href="{s['href']}" target="_blank" class="service-card">
                    <div class="service-icon">{s['icon']}</div>
                    <div style="flex:1">
                        <div class="service-name">{s['name']}</div>
                        <div class="service-desc">{s['desc']}</div>
                    </div>
                    <span style="color:var(--text-light);font-size:1rem">←</span>
                </a>
                """, unsafe_allow_html=True)

# ── 3. الاستثمار ───────────────────────────────
elif tab == "investment":
    st.markdown("### 📈 فرص الاستثمار في الجيزة")
    for opp in INVESTMENT:
        maps_url = f"https://www.google.com/maps?q={opp['lat']},{opp['lng']}"
        st.markdown(f"""
        <div class="invest-card">
            <span class="score-badge">⭐ {opp['score']}/10</span>
            <div class="invest-title">{opp['name']}</div>
            <div class="invest-detail">📍 {opp['location']}</div>
            <div class="invest-detail">🏗️ {opp['activity']}</div>
            <div class="invest-detail">✨ {opp['advantage']}</div>
            <div class="invest-detail">💡 {opp['reasoning']}</div>
            <div class="invest-detail">🎯 الأنسب: {opp['bestFor']}</div>
            <a href="{maps_url}" target="_blank" class="maps-link">🗺️ شوف على الخريطة</a>
        </div>
        """, unsafe_allow_html=True)
    st.info("💼 للتواصل مع وحدة الاستثمار: تواصل مع محافظة الجيزة الرسمية على giza.gov.eg")

# ── 4. السياحة ─────────────────────────────────
elif tab == "tourism":
    st.markdown("### 🏛️ البرامج السياحية في الجيزة")
    day = st.radio("اختار عدد الأيام:", ["يوم واحد", "يومين", "3 أيام", "أسبوع"], horizontal=True, key="tourism_days")
    day_map = {"يوم واحد": "1", "يومين": "2", "3 أيام": "3", "أسبوع": "7"}
    plan = TOURISM_PLANS.get(day_map[day], "")
    st.markdown(f"""
    <div style="background:white;border:1px solid var(--border);border-radius:16px;padding:20px;margin-top:12px">
    {plan.replace(chr(10), '<br>')}
    </div>
    """, unsafe_allow_html=True)
    st.markdown("🗺️ [خريطة المعالم السياحية](https://www.google.com/maps/search/سياحة+الجيزة)", unsafe_allow_html=True)

# ── 5. المستشفيات ──────────────────────────────
elif tab == "hospitals":
    st.markdown("### 🏥 مستشفيات محافظة الجيزة")
    loc = st.session_state.location
    if loc:
        hospitals_sorted = sorted(HOSPITALS, key=lambda h: haversine(loc["lat"], loc["lng"], h["lat"], h["lng"]))
        st.success("✅ تم ترتيب المستشفيات حسب قربها منك")
    else:
        hospitals_sorted = HOSPITALS
        st.warning("📍 اضغط 'موقعي' لترتيب المستشفيات حسب الأقرب ليك")

    for h in hospitals_sorted:
        maps_url = f"https://www.google.com/maps/dir/{loc['lat']},{loc['lng']}/{h['lat']},{h['lng']}" if loc else f"https://www.google.com/maps?q={h['lat']},{h['lng']}"
        dist = f"{haversine(loc['lat'], loc['lng'], h['lat'], h['lng']):.1f} كم" if loc else ""
        st.markdown(f"""
        <div class="hospital-card">
            <div>
                <div class="hospital-name">🏥 {h['name']}</div>
                <div class="hospital-dist">{dist}</div>
            </div>
            <a href="{maps_url}" target="_blank" class="maps-btn">🗺️ الاتجاهات</a>
        </div>
        """, unsafe_allow_html=True)

    if loc:
        all_maps = f"https://www.google.com/maps/search/مستشفى/@{loc['lat']},{loc['lng']},14z"
        st.markdown(f"🔍 [ابحث عن مزيد من المستشفيات القريبة]({all_maps})")

# ── 6. مطاعم ───────────────────────────────────
elif tab == "restaurants":
    st.markdown("### 🍽️ المطاعم في الجيزة")
    cuisine = st.selectbox("نوع الطعام:", ["مصري 🍲", "شرقي 🔥", "إيطالي 🍝", "آسيوي 🥢", "بحري 🦐"], key="cuisine_sel")
    location = st.radio("الموقع المفضل:", ["إطلالة على الأهرامات", "وسط المدينة"], horizontal=True, key="rest_loc")
    loc_key = "أهرامات" if "أهرامات" in location else "مدينة"
    cuisine_key = cuisine.split()[0]

    recs = {
        "مصري":   {"أهرامات": {"name":"فلفلة","loc":"نزلة السمان","rate":"4.8/5","spec":"طواجن وكشري وشاورما","note":"إطلالة على الأهرامات"},
                   "مدينة":  {"name":"صبحي كابر","loc":"الشيخ زايد","rate":"4.7/5","spec":"مقبلات ومشويات","note":"أجواء عائلية"}},
        "شرقي":   {"أهرامات": {"name":"حدائق الأهرام لاونج","loc":"حدائق الأهرام","rate":"4.7/5","spec":"كباب وشيش ومزة","note":"جلسات مفتوحة"},
                   "مدينة":  {"name":"مطعم الطوب","loc":"الدقي","rate":"4.6/5","spec":"مشويات طازة","note":"أسعار معقولة"}},
        "إيطالي": {"أهرامات": {"name":"باستا كاسا","loc":"الشيخ زايد","rate":"4.6/5","spec":"باستا وبيتزا وريزوتو","note":"أصيل ومميز"},
                   "مدينة":  {"name":"باستا كاسا","loc":"الشيخ زايد","rate":"4.6/5","spec":"باستا وبيتزا","note":"أفضل إيطالي بالجيزة"}},
        "آسيوي":  {"أهرامات": {"name":"هانا سوشي","loc":"المهندسين","rate":"4.6/5","spec":"سوشي طازة","note":"الأفضل في الجيزة"},
                   "مدينة":  {"name":"التنين الذهبي","loc":"الجيزة","rate":"4.5/5","spec":"صيني وياباني","note":"ديم سام وسوشي"}},
        "بحري":   {"أهرامات": {"name":"مطعم النيل البحري","loc":"كورنيش الجيزة","rate":"4.5/5","spec":"سمك وجمبري طازة","note":"إطلالة نيلية"},
                   "مدينة":  {"name":"سيلور","loc":"المهندسين","rate":"4.4/5","spec":"مأكولات بحرية","note":"أسعار معقولة"}},
    }

    r = recs.get(cuisine_key, {}).get(loc_key, {})
    if r:
        maps_url = f"https://www.google.com/maps/search/{r['name'].replace(' ', '+')}+{r['loc'].replace(' ', '+')}"
        st.markdown(f"""
        <div class="invest-card">
            <span class="score-badge">⭐ {r['rate']}</span>
            <div class="invest-title">🏆 {r['name']}</div>
            <div class="invest-detail">📍 {r['loc']}</div>
            <div class="invest-detail">🍽️ {r['spec']}</div>
            <div class="invest-detail">✨ {r['note']}</div>
            <a href="{maps_url}" target="_blank" class="maps-link">🗺️ شوف على الخريطة</a>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.location:
        lat=st.session_state.location["lat"]; lng=st.session_state.location["lng"]
        near_url = f"https://www.google.com/maps/search/مطعم+{cuisine_key}/@{lat},{lng},15z"
        st.markdown(f"🔍 [ابحث عن مطاعم {cuisine_key} قريبة منك]({near_url})")

# ── 7. فنادق ───────────────────────────────────
elif tab == "hotels":
    st.markdown("### 🏨 الفنادق في الجيزة")
    budget = st.radio("الميزانية:", ["اقتصادي 💰", "متوسط ⭐", "فاخر 👑"], horizontal=True, key="hotel_budget")
    location = st.radio("الموقع:", ["قرب الأهرامات", "الشيخ زايد / وسط الجيزة"], horizontal=True, key="hotel_loc")
    budget_key = budget.split()[0]
    loc_key = "أهرامات" if "أهرامات" in location else "مدينة"

    hotels_data = {
        "اقتصادي": {"أهرامات": {"name":"Pyramids View Inn","price":"40-60$/ليلة","rate":"4.2/5","note":"إطلالة رائعة وسعر مناسب"},
                    "مدينة":  {"name":"جرين بلازا شقق","price":"50-65$/ليلة","rate":"4.1/5","note":"وسط المدينة قريب من المول"}},
        "متوسط":   {"أهرامات": {"name":"ستينبرجر بيراميدز","price":"80-150$/ليلة","rate":"4.5/5","note":"حمام سباحة وإفطار شامل"},
                    "مدينة":  {"name":"ستيلا شقق فندقية","price":"85-130$/ليلة","rate":"4.4/5","note":"مطعم وجيم وكونسيرج"}},
        "فاخر":    {"أهرامات": {"name":"ماريوت مينا هاوس","price":"250-400$/ليلة","rate":"4.8/5","note":"5 نجوم — إطلالة مباشرة على الأهرامات"},
                    "مدينة":  {"name":"فور سيزنز جيزة","price":"280-450$/ليلة","rate":"4.9/5","note":"منتجع شامل مع سبا وجيم عالمي"}},
    }

    h = hotels_data.get(budget_key, {}).get(loc_key, {})
    if h:
        maps_url = f"https://www.google.com/maps/search/{h['name'].replace(' ', '+')}"
        st.markdown(f"""
        <div class="invest-card">
            <span class="score-badge">⭐ {h['rate']}</span>
            <div class="invest-title">🏨 {h['name']}</div>
            <div class="invest-detail">💰 {h['price']}</div>
            <div class="invest-detail">✨ {h['note']}</div>
            <a href="{maps_url}" target="_blank" class="maps-link">🗺️ شوف على الخريطة</a>
        </div>
        """, unsafe_allow_html=True)

# ── 8. شكاوى ───────────────────────────────────
elif tab == "complaints":
    st.markdown("### 📋 تقديم شكوى")
    st.markdown("""
    <div class="invest-card">
        <div class="invest-title">📞 خط نجدة المواطن</div>
        <div class="invest-detail" style="font-size:1.2rem;font-weight:700;color:var(--primary)">16555</div>
    </div>
    <div class="invest-card">
        <div class="invest-title">🌐 الموقع الرسمي</div>
        <a href="https://www.giza.gov.eg" target="_blank" class="maps-link">giza.gov.eg</a>
    </div>
    <div class="invest-card">
        <div class="invest-title">💻 منصة مصر الرقمية</div>
        <a href="https://digital.gov.eg" target="_blank" class="maps-link">digital.gov.eg</a>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("**أنواع الشكاوى:** إنارة الشوارع 💡 | النظافة 🗑️ | الطرق 🚧 | المخالفات ⚠️")
