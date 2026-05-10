import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import io

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
</style>
""", unsafe_allow_html=True)

# ─── العنوان ─────────────────────────────────────────────────────────────────
st.markdown("# 🏛️ جيزا")
st.markdown('<p class="subtitle">المساعد الذكي الرسمي لمحافظة الجيزة</p>', unsafe_allow_html=True)
st.divider()

# ─── System Prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """أنت مساعد ذكي رسمي لمحافظة الجيزة، مصر. اسمك 'جيزا'. مهمتك مساعدة المواطنين والسياح في كل ما يخص المحافظة.

هويتك:
- اسمك: جيزا (Giza Assistant)
- تابع: محافظة الجيزة الرسمية
- تتكلم عربي وإنجليزي — تتعرف على لغة المستخدم وترد بنفس اللغة تلقائياً

اللي بتساعد فيه:

1. السياحة والتخطيط السياحي:
   - الأهرامات وأبو الهول والمتحف المصري الكبير (GEM)
   - برامج سياحية: يوم، يومين، 3 أيام، أسبوع
   - عند السؤال عن برنامج سياحي أو رحلة أو جولة: اسأل كم يوم
   - حدائق الأورمان، حديقة الحيوان، كورنيش الجيزة، رحلات نيلية، عروض الصوت والضوء

2. المطاعم:
   - الخطوة 1: اسأل عن نوع الطعام (مصري، شرقي، إيطالي، آسيوي، بحري، عالمي)
   - الخطوة 2: اسأل عن الموقع (إطلالة أهرامات أم وسط المدينة)
   - توصيات: فلفلة نزلة السمان، صبحي كابر الشيخ زايد، حدائق الأهرام لاونج، مطعم الطوب الدقي، باستا كاسا الشيخ زايد

3. الفنادق:
   - الخطوة 1: اسأل عن الميزانية (اقتصادي، متوسط، فاخر)
   - الخطوة 2: اسأل عن الموقع المفضل
   - فاخر: ماريوت مينا هاوس 250-400 دولار، فور سيزنز جيزة 280-450 دولار
   - متوسط: ستينبرجر بيراميدز 80-150 دولار، ستيلا شقق فندقية 85-130 دولار
   - اقتصادي: Pyramids View Inn 40-60 دولار، جرين بلازا شقق 50-65 دولار

4. الاستثمار:
   - الخطوة 1: اسأل عن الاسم
   - الخطوة 2: اسأل عن نوع النشاط (كافيه، فندق، مطعم، بوتيك، مكتب)
   - الخطوة 3: اسأل عن المنطقة المفضلة (الأهرامات، المتحف، النيل، وسط الجيزة)
   - الخطوة 4: اسأل عن الميزانية (أقل من مليون، 1-5 مليون، 5-10 مليون، أكثر من 10 مليون جنيه)
   - الخطوة 5: قدم الفرص: نزلة السمان تقييم 9.5، محيط المتحف الكبير تقييم 9.0، المنيل تقييم 8.5

5. الخدمات الحكومية:
   - تجديد رخصة القيادة: منصة مصر الرقمية digital.gov.eg
   - خدمات التموين: ضم أفراد، إصدار بطاقة، فصل، نقل محافظة
   - المرور: تجديد رخصة، استعلام مخالفات، سداد مخالفات

6. المستشفيات:
   - مستشفى الجيزة العام، أم المصريين، الشيخ زايد التخصصي، العجوزة العام، الهرم العام
   - اطلب تحديد المنطقة وقدم أقرب مستشفى

7. ذوي الهمم:
   - اسأل عن احتياجات الوصول: منحدر للكراسي المتحركة، شباك أرضي، مصعد مخصص

8. الشكاوى:
   - وجه المستخدم لصفحة الشكاوى على الموقع الرسمي

قواعد الردود:
- ردودك قصيرة ومباشرة، جملة أو جملتين بحد أقصى
- اسأل سؤالاً واحداً فقط في كل رد
- ابدأ بترحيب ودي وسريع
- تذكر المحادثة السابقة لتكمل السيناريوهات
- لو مش عارف المعلومة وجه للموقع الرسمي لمحافظة الجيزة"""

# ─── Groq Client ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# ─── تهيئة المحادثة ───────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "أهلاً! أنا جيزا، مساعدك الذكي لمحافظة الجيزة 🏛️ كيف أقدر أساعدك النهارده؟"
    }]

if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None

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
            "content": "أهلاً! أنا جيزا، مساعدك الذكي لمحافظة الجيزة 🏛️ كيف أقدر أساعدك النهارده؟"
        }]
        st.session_state.last_audio_id = None
        st.rerun()
