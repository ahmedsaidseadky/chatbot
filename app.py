import streamlit as st
from groq import Groq
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
    
    /* تنسيق حقل الإدخال مع زر الميكروفون */
    .input-container {
        display: flex;
        gap: 10px;
        align-items: center;
        direction: rtl;
    }
    .stChatInputContainer {
        flex: 1;
    }
    .mic-button {
        background-color: #1a5276;
        color: white;
        border: none;
        border-radius: 50%;
        width: 45px;
        height: 45px;
        cursor: pointer;
        font-size: 20px;
        transition: all 0.3s;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    .mic-button:hover {
        background-color: #2e86c1;
        transform: scale(1.05);
    }
    .mic-button.recording {
        background-color: #e74c3c;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
</style>

<script>
    let mediaRecorder;
    let audioChunks = [];
    
    function startRecording() {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };
                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const reader = new FileReader();
                    reader.readAsDataURL(audioBlob);
                    reader.onloadend = () => {
                        const base64Audio = reader.result.split(',')[1];
                        const event = new CustomEvent('streamlit:audio', {
                            detail: { audio: base64Audio }
                        });
                        window.dispatchEvent(event);
                    };
                    audioChunks = [];
                };
                mediaRecorder.start();
                document.getElementById('micBtn').classList.add('recording');
                document.getElementById('micBtn').innerHTML = '⏹️';
            });
    }
    
    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            document.getElementById('micBtn').classList.remove('recording');
            document.getElementById('micBtn').innerHTML = '🎤';
        }
    }
    
    function toggleRecording() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            stopRecording();
        } else {
            startRecording();
        }
    }
</script>
""", unsafe_allow_html=True)

# ─── العنوان ─────────────────────────────────────────────────────────────────
st.markdown("# 🏛️ جيزا")
st.markdown('<p class="subtitle">المساعد الذكي الرسمي لمحافظة الجيزة</p>', unsafe_allow_html=True)
st.divider()

# ─── قاعدة بيانات الأماكن (إحداثيات ثابتة للجيزة) ─────────────────────────
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

# ─── دوال المساعدة للموقع ───────────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    """حساب المسافة بين نقطتين بالكيلومترات"""
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def find_nearest_place(lat, lon, place_type):
    """البحث عن أقرب مكان"""
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

def get_location_from_browser():
    """الحصول على الموقع من المتصفح باستخدام JavaScript"""
    import streamlit.components.v1 as components
    
    location_holder = st.empty()
    
    # مكون HTML/JavaScript لطلب الموقع
    location_html = """
    <div id="location-result" style="display: none;"></div>
    <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        // تخزين الموقع في sessionStorage
                        sessionStorage.setItem('user_lat', lat);
                        sessionStorage.setItem('user_lon', lon);
                        // تحديث عنصر مخفي بالبيانات
                        const resultDiv = document.getElementById('location-result');
                        resultDiv.setAttribute('data-lat', lat);
                        resultDiv.setAttribute('data-lon', lon);
                        resultDiv.setAttribute('data-status', 'success');
                    },
                    function(error) {
                        const resultDiv = document.getElementById('location-result');
                        resultDiv.setAttribute('data-status', 'error');
                        resultDiv.setAttribute('data-error', error.message);
                    }
                );
            } else {
                const resultDiv = document.getElementById('location-result');
                resultDiv.setAttribute('data-status', 'error');
                resultDiv.setAttribute('data-error', 'المتصفح لا يدعم تحديد الموقع');
            }
        }
        getLocation();
    </script>
    """
    
    components.html(location_html, height=0)
    
    # محاولة قراءة الموقع من sessionStorage عبر rerun
    # (هذه الطريقة مبسطة - في التطبيق الحقيقي تحتاج مكتبة متخصصة)
    return None

# ─── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """أنت مساعد ذكي رسمي لمحافظة الجيزة، مصر. اسمك 'جيزا'.

⚡ مهم: عندما يطلب المستخدم "أقرب مستشفى" أو "أقرب مطعم" أو "أقرب صيدلية" أو "أقرب معلم سياحي":
- إذا كان الموقع غير متوفر: اطلب من المستخدم الضغط على زر "تحديد موقعي" أولاً
- إذا كان الموقع متوفر: استخدم البيانات الموجودة وأعرض أقرب مكان مع المسافة

قواعد الردود:
- ردودك قصيرة ومباشرة
- اسأل سؤالاً واحداً فقط في كل رد
- تذكر المحادثة السابقة
- لو مش عارف المعلومة وجه للموقع الرسمي لمحافظة الجيزة"""

# ─── Groq Client ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# ─── تهيئة المحادثة والمتغيرات ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "أهلاً! أنا جيزا، مساعدك الذكي لمحافظة الجيزة 🏛️ كيف أقدر أساعدك النهارده؟"
    }]

if "user_lat" not in st.session_state:
    st.session_state.user_lat = None
    st.session_state.user_lon = None

if "audio_processing" not in st.session_state:
    st.session_state.audio_processing = False

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
    
    # التحقق إذا كان الطلب يطلب أقرب مكان
    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in ["اقرب مستشفى", "اقرب صيدلية", "اقرب مطعم", "اقرب معلم"]):
        check_and_find_nearest(prompt_lower, reply)

def check_and_find_nearest(prompt, assistant_reply):
    """التحقق من الطلب وعرض أقرب مكان إذا كان الموقع متوفر"""
    if not st.session_state.user_lat:
        # إضافة رسالة تطلب تحديد الموقع
        location_msg = "\n\n📍 لتتمكن من العثور على أقرب مكان، اضغط على زر 'تحديد موقعي' في الشريط الجانبي."
        st.session_state.messages[-1]["content"] += location_msg
        return
    
    # تحديد نوع المكان المطلوب
    place_type = None
    if "مستشفى" in prompt:
        place_type = "مستشفى"
    elif "صيدلية" in prompt:
        place_type = "صيدلية"
    elif "مطعم" in prompt:
        place_type = "مطعم"
    elif "معلم" in prompt:
        place_type = "معلم سياحي"
    
    if place_type:
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

# ─── عرض المحادثة ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── الشريط الجانبي لتحديد الموقع ───────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📍 الموقع")
    
    # زر تحديد الموقع
    if st.button("📍 تحديد موقعي", use_container_width=True, type="primary"):
        # استخدام JavaScript للحصول على الموقع
        st.markdown("""
        <script>
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    // إعادة تحميل الصفحة مع إحداثيات في URL
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
    
    # قراءة الموقع من URL parameters
    query_params = st.query_params
    if "lat" in query_params and "lon" in query_params:
        try:
            st.session_state.user_lat = float(query_params["lat"])
            st.session_state.user_lon = float(query_params["lon"])
            st.success(f"✅ تم تحديد موقعك!")
            st.info(f"📍 الإحداثيات: {st.session_state.user_lat:.4f}, {st.session_state.user_lon:.4f}")
        except:
            st.error("خطأ في قراءة الموقع")
    elif st.session_state.user_lat:
        st.success(f"✅ تم تحديد موقعك!")
        st.info(f"📍 الإحداثيات: {st.session_state.user_lat:.4f}, {st.session_state.user_lon:.4f}")
    else:
        st.info("⚠️ لم يتم تحديد الموقع بعد")
        st.caption("اضغط على 'تحديد موقعي' لتتمكن من البحث عن أقرب الخدمات")
    
    st.divider()
    
    # أزرار البحث السريع (تظهر فقط إذا تم تحديد الموقع)
    if st.session_state.user_lat:
        st.markdown("### 🔍 بحث سريع")
        
        if st.button("🏥 أقرب مستشفى", use_container_width=True):
            nearest = find_nearest_place(st.session_state.user_lat, st.session_state.user_lon, "مستشفى")
            if nearest:
                msg = f"📍 **أقرب مستشفى لك:**\n🏥 {nearest['name']}\n📏 {nearest['distance']} كم\n📍 {nearest['address']}\n📞 {nearest['phone']}"
                with st.chat_message("assistant"):
                    st.markdown(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
                st.rerun()
        
        if st.button("💊 أقرب صيدلية", use_container_width=True):
            nearest = find_nearest_place(st.session_state.user_lat, st.session_state.user_lon, "صيدلية")
            if nearest:
                msg = f"📍 **أقرب صيدلية لك:**\n💊 {nearest['name']}\n📏 {nearest['distance']} كم\n📍 {nearest['address']}\n📞 {nearest['phone']}"
                with st.chat_message("assistant"):
                    st.markdown(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
                st.rerun()
        
        if st.button("🍽️ أقرب مطعم", use_container_width=True):
            nearest = find_nearest_place(st.session_state.user_lat, st.session_state.user_lon, "مطعم")
            if nearest:
                msg = f"📍 **أقرب مطعم لك:**\n🍽️ {nearest['name']}\n📏 {nearest['distance']} كم\n📍 {nearest['address']}\n📞 {nearest['phone']}"
                with st.chat_message("assistant"):
                    st.markdown(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
                st.rerun()
        
        if st.button("🏛️ أقرب معلم سياحي", use_container_width=True):
            nearest = find_nearest_place(st.session_state.user_lat, st.session_state.user_lon, "معلم سياحي")
            if nearest:
                msg = f"📍 **أقرب معلم سياحي لك:**\n🏛️ {nearest['name']}\n📏 {nearest['distance']} كم\n📍 {nearest['address']}\n📞 {nearest['phone']}"
                with st.chat_message("assistant"):
                    st.markdown(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
                st.rerun()
    
    st.divider()
    
    # زر مسح المحادثة
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "أهلاً! أنا جيزا، مساعدك الذكي لمحافظة الجيزة 🏛️ كيف أقدر أساعدك النهارده؟"
        }]
        st.rerun()

# ─── إدخال النص مع زر صوت جنبه ───────────────────────────────────────────────
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
                st.toast(f"🎤 قلت: {prompt_text[:50]}...")
                send_message(prompt_text)
                st.rerun()

# ─── إضافة توضيح للمستخدم ────────────────────────────────────────────────────
st.markdown("---")
st.caption("💡 **ملاحظة:** لتتمكن من البحث عن أقرب الخدمات، اضغط على 'تحديد موقعي' في الشريط الجانبي أولاً")
