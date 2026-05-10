import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import io
import requests
import math
import json

# ─── إعداد الصفحة ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="جيزا - المساعد الذكي",
    page_icon="🏛️",
    layout="centered"
)

# ─── CSS مخصص ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    body, .stApp { direction: rtl; font-family: 'Cairo', sans-serif; }
    .stChatMessage { direction: rtl; }
    .stTextInput > div > div > input { direction: rtl; }
    h1 { text-align: center; color: #1a5276; }
    .subtitle { text-align: center; color: #666; margin-bottom: 20px; }
    .location-info { background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin: 10px 0; }
    .stButton button { background-color: #1a5276; color: white; }
</style>
""", unsafe_allow_html=True)

# ─── JavaScript مخصص للحصول على الموقع ─────────────────────────────────────
get_location_js = """
<script>
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const locationData = {
                    lat: lat,
                    lon: lon,
                    status: "success"
                };
                // إرسال البيانات إلى Streamlit
                const event = new CustomEvent("streamlit:location", {
                    detail: locationData
                });
                window.dispatchEvent(event);
            },
            function(error) {
                const locationData = {
                    status: "error",
                    message: error.message
                };
                const event = new CustomEvent("streamlit:location", {
                    detail: locationData
                });
                window.dispatchEvent(event);
            }
        );
    } else {
        const locationData = {
            status: "error",
            message: "المتصفح لا يدعم تحديد الموقع"
        };
        const event = new CustomEvent("streamlit:location", {
            detail: locationData
        });
        window.dispatchEvent(event);
    }
}
document.addEventListener("DOMContentLoaded", function() {
    const button = document.getElementById("get-location-btn");
    if (button) {
        button.addEventListener("click", getLocation);
    }
});
</script>
"""

# ─── قاعدة بيانات الأماكن (إحداثيات ثابتة للجيزة) ─────────────────────────
PLACES_DATABASE = {
    "مستشفيات": [
        {"name": "مستشفى الجيزة العام", "lat": 30.0131, "lon": 31.2089, "address": "شارع البحر الأعظم, الجيزة", "phone": "02-12345678"},
        {"name": "مستشفى أم المصريين", "lat": 30.0265, "lon": 31.2090, "address": "المهندسين, الجيزة", "phone": "02-23456789"},
        {"name": "مستشفى الشيخ زايد التخصصي", "lat": 29.9798, "lon": 31.0092, "address": "الشيخ زايد, الجيزة", "phone": "02-34567890"},
        {"name": "مستشفى العجوزة العام", "lat": 30.0438, "lon": 31.2152, "address": "العجوزة, الجيزة", "phone": "02-45678901"},
        {"name": "مستشفى الهرم العام", "lat": 29.9895, "lon": 31.1850, "address": "الهرم, الجيزة", "phone": "02-56789012"},
    ],
    "صيدليات": [
        {"name": "صيدليات العزبي - المهندسين", "lat": 30.0312, "lon": 31.2105, "address": "شارع السودان, المهندسين", "phone": "02-67890123"},
        {"name": "صيدليات نجم - الهرم", "lat": 29.9875, "lon": 31.1823, "address": "شارع الهرم, الجيزة", "phone": "02-78901234"},
        {"name": "صيدليات صيدناوي - الدقي", "lat": 30.0384, "lon": 31.2121, "address": "شارع التحرير, الدقي", "phone": "02-89012345"},
    ],
    "مطاعم": [
        {"name": "فلفلة نزلة السمان", "lat": 29.9832, "lon": 31.1405, "address": "نزلة السمان, الهرم", "phone": "02-90123456"},
        {"name": "صبحي كابر - الشيخ زايد", "lat": 29.9765, "lon": 31.0050, "address": "الشيخ زايد, الجيزة", "phone": "02-01234567"},
        {"name": "مطعم الطوب - الدقي", "lat": 30.0380, "lon": 31.2130, "address": "شارع وادي النيل, الدقي", "phone": "02-12345678"},
    ],
    "معالم سياحية": [
        {"name": "أهرامات الجيزة", "lat": 29.9792, "lon": 31.1342, "address": "الهرم, الجيزة", "phone": "02-23456789"},
        {"name": "أبو الهول", "lat": 29.9753, "lon": 31.1377, "address": "الهرم, الجيزة", "phone": "02-34567890"},
        {"name": "المتحف المصري الكبير (GEM)", "lat": 29.9931, "lon": 31.1201, "address": "الهرم, الجيزة", "phone": "02-45678901"},
        {"name": "حديقة الأورمان", "lat": 30.0315, "lon": 31.2140, "address": "الدقي, الجيزة", "phone": "02-56789012"},
        {"name": "كورنيش النيل", "lat": 30.0475, "lon": 31.2305, "address": "العجوزة, الجيزة", "phone": "-"},
    ]
}

# ─── دوال المساعدة للموقع ───────────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    """حساب المسافة بين نقطتين باستخدام صيغة هافرزين (بالكيلومترات)"""
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def find_nearest_place(lat, lon, place_type_ar):
    """البحث عن أقرب مكان بناءً على النوع"""
    place_type_en = {
        "مستشفى": "مستشفيات",
        "صيدلية": "صيدليات",
        "مطعم": "مطاعم",
        "معلم سياحي": "معالم سياحية"
    }.get(place_type_ar, "مستشفيات")
    
    if place_type_en not in PLACES_DATABASE:
        return None
    
    nearest = None
    min_distance = float('inf')
    
    for place in PLACES_DATABASE[place_type_en]:
        distance = haversine(lat, lon, place["lat"], place["lon"])
        if distance < min_distance:
            min_distance = distance
            nearest = place.copy()
            nearest["distance"] = round(distance, 2)
    
    return nearest

def format_location_response(place, place_type):
    """تنسيق الرد مع معلومات المكان"""
    if not place:
        return f"عذراً، لم أجد {place_type} قريب منك."
    
    return f"""
📍 **أقرب {place_type} لك:**
🏥 {place['name']}
📏 المسافة: {place['distance']} كم
📍 العنوان: {place['address']}
📞 الهاتف: {place['phone']}

🗺️ [افتح في خرائط جوجل](https://www.google.com/maps?q={place['lat']},{place['lon']})
    """

# ─── نظام المراسلة مع JavaScript ───────────────────────────────────────────
def init_location_handling():
    """تهيئة معالجة الموقع باستخدام JavaScript"""
    location_component = st.empty()
    
    # إضافة JavaScript
    st.markdown(get_location_js, unsafe_allow_html=True)
    
    # زر الحصول على الموقع
    st.markdown("""
    <div style="text-align: center; margin: 20px 0;">
        <button id="get-location-btn" style="
            background-color: #1a5276;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        ">
            📍 خذ موقعي
        </button>
    </div>
    """, unsafe_allow_html=True)
    
    # استقبال الموقع من JavaScript عبر query parameters
    import urllib.parse
    query_params = st.query_params
    if "lat" in query_params and "lon" in query_params:
        try:
            lat = float(query_params["lat"])
            lon = float(query_params["lon"])
            return {"latitude": lat, "longitude": lon}
        except:
            return None
    return None

# ─── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """أنت مساعد ذكي رسمي لمحافظة الجيزة، مصر. اسمك 'جيزا'. مهمتك مساعدة المواطنين والسياح في كل ما يخص المحافظة.

⚡ **ميزة تحديد الموقع**: المستخدم يستطيع استخدام زر "خذ موقعي" للحصول على أقرب مستشفى، صيدلية، مطعم، أو معلم سياحي.

هويتك:
- اسمك: جيزا (Giza Assistant)
- تابع: محافظة الجيزة الرسمية
- تتكلم عربي وإنجليزي — تتعرف على لغة المستخدم وترد بنفس اللغة تلقائياً

اللي بتساعد فيه: [باقي المحتوى كما هو...]
"""

# ─── Groq Client ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# ─── تهيئة المحادثة ───────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "أهلاً! أنا جيزا، مساعدك الذكي لمحافظة الجيزة 🏛️ كيف أقدر أساعدك النهارده؟\n\n💡 ملاحظة: استخدم زر 'خذ موقعي' فوق عشان أقدر ألاقيلك أقرب مستشفى أو صيدلية أو مطعم!"
    }]

if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None

if "user_location" not in st.session_state:
    st.session_state.user_location = None

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

# ─── عرض المحادثة ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── تحديد الموقع الجغرافي ───────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📍 خدمة تحديد الموقع")

# تهيئة معالجة الموقع
location_data = init_location_handling()

if location_data:
    st.session_state.user_location = {
        "lat": location_data["latitude"],
        "lon": location_data["longitude"]
    }
    st.success(f"✅ تم تحديد موقعك بنجاح!")
    st.info(f"الإحداثيات: {location_data['latitude']:.4f}, {location_data['longitude']:.4f}")
    
    # عرض أزرار البحث السريع
    st.markdown("#### 🔍 ابحث عن أقرب:")
    btn_cols = st.columns(4)
    
    with btn_cols[0]:
        if st.button("🏥 مستشفى", use_container_width=True):
            with st.spinner("جاري البحث عن أقرب مستشفى..."):
                nearest = find_nearest_place(location_data['latitude'], location_data['longitude'], "مستشفى")
                reply = format_location_response(nearest, "مستشفى")
                with st.chat_message("assistant"):
                    st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()
    
    with btn_cols[1]:
        if st.button("💊 صيدلية", use_container_width=True):
            with st.spinner("جاري البحث عن أقرب صيدلية..."):
                nearest = find_nearest_place(location_data['latitude'], location_data['longitude'], "صيدلية")
                reply = format_location_response(nearest, "صيدلية")
                with st.chat_message("assistant"):
                    st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()
    
    with btn_cols[2]:
        if st.button("🍽️ مطعم", use_container_width=True):
            with st.spinner("جاري البحث عن أقرب مطعم..."):
                nearest = find_nearest_place(location_data['latitude'], location_data['longitude'], "مطعم")
                reply = format_location_response(nearest, "مطعم")
                with st.chat_message("assistant"):
                    st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()
    
    with btn_cols[3]:
        if st.button("🏛️ معلم سياحي", use_container_width=True):
            with st.spinner("جاري البحث عن أقرب معلم سياحي..."):
                nearest = find_nearest_place(location_data['latitude'], location_data['longitude'], "معلم سياحي")
                reply = format_location_response(nearest, "معلم سياحي")
                with st.chat_message("assistant"):
                    st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()
else:
    st.info("📍 اضغط على زر 'خذ موقعي' لتحديد موقعك والعثور على أقرب الخدمات")

st.markdown("---")

# ─── الميكروفون ──────────────────────────────────────────────────────────────
st.markdown("##### 🎤 أو تكلم مع جيزا:")
audio = mic_recorder(
    start_prompt="🎤 اضغط وتكلم",
    stop_prompt="⏹️ وقّف التسجيل",
    just_once=True,
    use_container_width=True,
    key="mic"
)

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
        prompt = transcription.text
        if prompt.strip():
            st.info(f"قلت: {prompt}")
            send_message(prompt)
            st.rerun()

# ─── إدخال النص ───────────────────────────────────────────────────────────────
if prompt := st.chat_input("اكتب سؤالك هنا..."):
    with st.spinner("جيزا بتفكر..."):
        send_message(prompt)
    st.rerun()

# ─── زر مسح المحادثة ─────────────────────────────────────────────────────────
if len(st.session_state.messages) > 1:
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "أهلاً! أنا جيزا، مساعدك الذكي لمحافظة الجيزة 🏛️ كيف أقدر أساعدك النهارده؟\n\n💡 ملاحظة: استخدم زر 'خذ موقعي' فوق عشان أقدر ألاقيلك أقرب مستشفى أو صيدلية أو مطعم!"
        }]
        st.session_state.last_audio_id = None
        st.session_state.user_location = None
        st.rerun()
