import streamlit as st
from groq import Groq
import io
import requests
import math

# ─── إعداد الصفحة ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="جيزا - المساعد الذكي",
    page_icon="🏛️",
    layout="centered"
)

# ─── CSS مخصص للشكل الجديد ───────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2? Cairo:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif;
    }
    
    body, .stApp {
        direction: rtl;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* الحاوية الرئيسية */
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* بطاقة الترحيب */
    .welcome-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 40px 30px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        animation: fadeIn 0.8s ease-out;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .welcome-icon {
        font-size: 64px;
        margin-bottom: 20px;
    }
    
    .welcome-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    .welcome-subtitle {
        font-size: 18px;
        opacity: 0.95;
        margin-bottom: 20px;
    }
    
    .welcome-description {
        font-size: 16px;
        opacity: 0.9;
        line-height: 1.6;
        max-width: 500px;
        margin: 0 auto;
    }
    
    /* تنسيق محادثة الشات */
    .stChatMessage {
        direction: rtl;
    }
    
    /* تنسيق حقل الإدخال */
    .stChatInputContainer {
        direction: rtl;
    }
    
    .stTextInput > div > div > input {
        direction: rtl;
        border-radius: 25px;
        padding: 12px 20px;
    }
    
    /* إخفاء العلامة المائية لـ Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* تنسيق الأزرار في الشريط الجانبي */
    .stButton > button {
        border-radius: 25px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* تنسيق رسائل الشات */
    [data-testid="stChatMessage"] {
        border-radius: 15px;
        margin: 10px 0;
    }
    
    /* تنسيق الشريط الجانبي */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
</style>
""", unsafe_allow_html=True)

# ─── عرض بطاقة الترحيب ──────────────────────────────────────────────────────
st.markdown("""
<div class="welcome-card">
    <div class="welcome-icon">🏛️✨</div>
    <div class="welcome-title">مساعدك الذكي</div>
    <div class="welcome-subtitle">أهلاً بك</div>
    <div class="welcome-description">
        أنا مساعدك الذكي لمحافظة الجيزة.<br>
        يمكنني مساعدتك في الاستثمار، السياحة، الخدمات الحكومية وأكثر.<br>
        <strong>اكتب ما تحتاجه وسأساعدك فوراً!</strong>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── قاعدة بيانات الأماكن ────────────────────────────────────────────────────
PLACES_DATABASE = {
    "مستشفى": [
        {"name": "مستشفى الجيزة العام", "lat": 30.0131, "lon": 31.2089, "address": "شارع البحر الأعظم, الجيزة", "phone": "02-12345678"},
        {"name": "مستشفى أم المصريين", "lat": 30.0265, "lon": 31.2090, "address": "المهندسين, الجيزة", "phone": "02-23456789"},
        {"name": "مستشفى الشيخ زايد التخصصي", "lat": 29.9798, "lon": 31.0092, "address": "الشيخ زايد, الجيزة", "phone": "02-34567890"},
        {"name": "مستشفى العجوزة العام", "lat": 30.0438, "lon": 31.2152, "address": "العجوزة, الجيزة", "phone": "02-45678901"},
        {"name": "مستشفى الهرم العام", "lat": 29.9895, "lon": 31.1850, "address": "الهرم, الجيزة", "phone": "02-56789012"},
    ],
    "صيدلية": [
        {"name": "صيدليات العزبي - المهندسين", "lat": 30.0312, "lon": 31.2105, "address": "شارع السودان, المهندسين", "phone": "02-67890123"},
        {"name": "صيدليات نجم - الهرم", "lat": 29.9875, "lon": 31.1823, "address": "شارع الهرم, الجيزة", "phone": "02-78901234"},
        {"name": "صيدليات صيدناوي - الدقي", "lat": 30.0384, "lon": 31.2121, "address": "شارع التحرير, الدقي", "phone": "02-89012345"},
    ],
    "مطعم": [
        {"name": "فلفلة نزلة السمان", "lat": 29.9832, "lon": 31.1405, "address": "نزلة السمان, الهرم", "phone": "02-90123456"},
        {"name": "صبحي كابر - الشيخ زايد", "lat": 29.9765, "lon": 31.0050, "address": "الشيخ زايد, الجيزة", "phone": "02-01234567"},
        {"name": "مطعم الطوب - الدقي", "lat": 30.0380, "lon": 31.2130, "address": "شارع وادي النيل, الدقي", "phone": "02-12345678"},
    ],
    "معلم سياحي": [
        {"name": "أهرامات الجيزة", "lat": 29.9792, "lon": 31.1342, "address": "الهرم, الجيزة", "phone": "02-23456789"},
        {"name": "أبو الهول", "lat": 29.9753, "lon": 31.1377, "address": "الهرم, الجيزة", "phone": "02-34567890"},
        {"name": "المتحف المصري الكبير (GEM)", "lat": 29.9931, "lon": 31.1201, "address": "الهرم, الجيزة", "phone": "02-45678901"},
        {"name": "حديقة الأورمان", "lat": 30.0315, "lon": 31.2140, "address": "الدقي, الجيزة", "phone": "02-56789012"},
        {"name": "كورنيش النيل", "lat": 30.0475, "lon": 31.2305, "address": "العجوزة, الجيزة", "phone": "-"},
    ]
}

# ─── دوال المساعدة ──────────────────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def find_nearest_place(lat, lon, place_type):
    if place_type not in PLACES_DATABASE:
        return None
    nearest = None
    min_distance = float('inf')
    for place in PLACES_DATABASE[place_type]:
        distance = haversine(lat, lon, place["lat"], place["lon"])
        if distance < min_distance:
            min_distance = distance
            nearest = place.copy()
            nearest["distance"] = round(distance, 2)
    return nearest

# ─── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """أنت مساعد ذكي رسمي لمحافظة الجيزة، مصر. اسمك 'جيزا'.

⚡ مهم: عندما يطلب المستخدم "أقرب مستشفى" أو "أقرب مطعم" أو "أقرب صيدلية" أو "أقرب معلم سياحي":
- إذا كان الموقع غير متوفر: اطلب من المستخدم الضغط على زر "تحديد موقعي" في الشريط الجانبي أولاً
- إذا كان الموقع متوفر: استخدم البيانات الموجودة وأعرض أقرب مكان مع المسافة

يمكنك مساعدة المستخدمين في:
1. السياحة والأماكن السياحية في الجيزة
2. المطاعم وتوصيات الأكل
3. الفنادق والحجوزات
4. الاستثمار والفرص الاستثمارية
5. الخدمات الحكومية
6. المستشفيات والخدمات الطبية
7. خدمات ذوي الهمم
8. الشكاوى والاقتراحات

قواعد الردود:
- ردودك مختصرة ومباشرة
- اسأل سؤالاً واحداً فقط في كل رد
- تذكر المحادثة السابقة
- استخدم اللغة العربية الفصحى أو العامية المصرية حسب راحة المستخدم
- لو مش عارف المعلومة وجه للموقع الرسمي لمحافظة الجيزة"""

# ─── Groq Client ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# ─── تهيئة المحادثة والمتغيرات ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_lat" not in st.session_state:
    st.session_state.user_lat = None
    st.session_state.user_lon = None

# ─── دالة إرسال الرسالة ──────────────────────────────────────────────────────
def send_message(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    client = get_client()
    messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages_for_api += [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages_for_api,
        temperature=0.7,
        max_tokens=500
    )
    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})
    
    # التحقق من طلب أقرب مكان
    prompt_lower = prompt.lower()
    place_keywords = {
        "مستشفى": "مستشفى",
        "صيدلية": "صيدلية", 
        "مطعم": "مطعم",
        "معلم": "معلم سياحي"
    }
    
    for keyword, place_type in place_keywords.items():
        if keyword in prompt_lower and ("اقرب" in prompt_lower or "أقرب" in prompt_lower):
            if st.session_state.user_lat:
                nearest = find_nearest_place(st.session_state.user_lat, st.session_state.user_lon, place_type)
                if nearest:
                    location_info = f"""
                    
📍 **أقرب {place_type} لك:**
🏥 **{nearest['name']}**
📏 المسافة: {nearest['distance']} كم
📍 {nearest['address']}
📞 {nearest['phone']}
🗺️ [فتح في خرائط جوجل](https://www.google.com/maps?q={nearest['lat']},{nearest['lon']})
"""
                    st.session_state.messages[-1]["content"] += location_info
            else:
                location_msg = "\n\n📍 **ملاحظة:** لتتمكن من العثور على أقرب مكان، اضغط على زر 'تحديد موقعي' في الشريط الجانبي أولاً."
                st.session_state.messages[-1]["content"] += location_msg
            break

# ─── عرض المحادثة ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── الشريط الجانبي ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏛️ القائمة")
    st.divider()
    
    st.markdown("### 📍 الموقع")
    
    # زر تحديد الموقع
    if st.button("📍 تحديد موقعي", use_container_width=True, type="primary"):
        st.markdown("""
        <script>
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    window.location.href = window.location.pathname + '?lat=' + lat + '&lon=' + lon;
                },
                function(error) {
                    alert('خطأ في تحديد الموقع: ' + error.message);
                }
            );
        } else {
            alert('المتصفح لا يدعم تحديد الموقع');
        }
        </script>
        """, unsafe_allow_html=True)
    
    # قراءة الموقع من URL
    query_params = st.query_params
    if "lat" in query_params and "lon" in query_params:
        try:
            st.session_state.user_lat = float(query_params["lat"])
            st.session_state.user_lon = float(query_params["lon"])
            st.success("✅ تم تحديد موقعك بنجاح!")
            st.info(f"📍 الإحداثيات: {st.session_state.user_lat:.4f}, {st.session_state.user_lon:.4f}")
        except:
            st.error("خطأ في قراءة الموقع")
    elif st.session_state.user_lat:
        st.success("✅ تم تحديد موقعك بنجاح!")
        st.info(f"📍 الإحداثيات: {st.session_state.user_lat:.4f}, {st.session_state.user_lon:.4f}")
    else:
        st.info("⚠️ لم يتم تحديد الموقع بعد")
        st.caption("اضغط على 'تحديد موقعي' للبحث عن أقرب الخدمات")
    
    st.divider()
    
    # أزرار البحث السريع
    if st.session_state.user_lat:
        st.markdown("### 🔍 بحث سريع")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏥 مستشفى", use_container_width=True):
                nearest = find_nearest_place(st.session_state.user_lat, st.session_state.user_lon, "مستشفى")
                if nearest:
                    msg = f"📍 **أقرب مستشفى لك:**\n\n🏥 **{nearest['name']}**\n📏 {nearest['distance']} كم\n📍 {nearest['address']}\n📞 {nearest['phone']}"
                    st.session_state.messages.append({"role": "assistant", "content": msg})
                    st.rerun()
        
        with col2:
            if st.button("💊 صيدلية", use_container_width=True):
                nearest = find_nearest_place(st.session_state.user_lat, st.session_state.user_lon, "صيدلية")
                if nearest:
                    msg = f"📍 **أقرب صيدلية لك:**\n\n💊 **{nearest['name']}**\n📏 {nearest['distance']} كم\n📍 {nearest['address']}\n📞 {nearest['phone']}"
                    st.session_state.messages.append({"role": "assistant", "content": msg})
                    st.rerun()
        
        col3, col4 = st.columns(2)
        with col3:
            if st.button("🍽️ مطعم", use_container_width=True):
                nearest = find_nearest_place(st.session_state.user_lat, st.session_state.user_lon, "مطعم")
                if nearest:
                    msg = f"📍 **أقرب مطعم لك:**\n\n🍽️ **{nearest['name']}**\n📏 {nearest['distance']} كم\n📍 {nearest['address']}\n📞 {nearest['phone']}"
                    st.session_state.messages.append({"role": "assistant", "content": msg})
                    st.rerun()
        
        with col4:
            if st.button("🏛️ معلم", use_container_width=True):
                nearest = find_nearest_place(st.session_state.user_lat, st.session_state.user_lon, "معلم سياحي")
                if nearest:
                    msg = f"📍 **أقرب معلم سياحي لك:**\n\n🏛️ **{nearest['name']}**\n📏 {nearest['distance']} كم\n📍 {nearest['address']}\n📞 {nearest['phone']}"
                    st.session_state.messages.append({"role": "assistant", "content": msg})
                    st.rerun()
    
    st.divider()
    
    # أزرار إضافية
    st.markdown("### 📋 خدمات")
    
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("ℹ️ عن المساعد", use_container_width=True):
        about_msg = """**🏛️ جيزا - المساعد الذكي**

أنا مساعدك الذكي الرسمي لمحافظة الجيزة.

**يمكنني مساعدتك في:**
• 🏨 السياحة والمعالم السياحية
• 🍽️ المطاعم وتوصيات الأكل
• 🏨 الفنادق والحجوزات
• 💼 الاستثمار والفرص
• 📋 الخدمات الحكومية
• 🏥 المستشفيات والخدمات الطبية
• 🤝 خدمات ذوي الهمم
• 📝 الشكاوى والاقتراحات

**للبحث عن أقرب مكان:**
اضغط على 'تحديد موقعي' أولاً، ثم اسألني أو استخدم أزرار البحث السريع.

© محافظة الجيزة - جميع الحقوق محفوظة"""
        st.session_state.messages.append({"role": "assistant", "content": about_msg})
        st.rerun()

# ─── إدخال النص مع زر الصوت ─────────────────────────────────────────────────
st.markdown("---")

# استخدام عمودين لإدخال النص وزر الصوت
col1, col2 = st.columns([5, 1])

with col1:
    prompt = st.chat_input("اكتب سؤالك هنا...")
    if prompt:
        with st.spinner("جيزا بتفكر..."):
            send_message(prompt)
        st.rerun()

with col2:
    # زر تسجيل الصوت
    from streamlit_mic_recorder import mic_recorder
    audio = mic_recorder(
        start_prompt="🎤",
        stop_prompt="⏹️",
        just_once=True,
        use_container_width=True,
        key="mic_recorder"
    )
    
    if audio and audio["bytes"]:
        with st.spinner("جيزا بتسمعك..."):
            client = get_client()
            audio_bytes = io.BytesIO(audio["bytes"])
            audio_bytes.name = "audio.wav"
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_bytes,
                language="ar"
            )
            prompt_text = transcription.text
            if prompt_text.strip():
                st.toast(f"🎤 سمعتك: {prompt_text[:50]}...")
                send_message(prompt_text)
                st.rerun()
