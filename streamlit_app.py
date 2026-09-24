import streamlit as st
import cv2
import requests
import joblib
import ipaddress
import os
from urllib.parse import urlparse, parse_qs
from gtts import gTTS


st.set_page_config(
    page_title="AI QR Phishing Risk Predictor",
    page_icon="🛡️",
    layout="centered"
)


MODEL_FILE = "qr_phishing_model.pkl"
VOICE_FILE = "qr_alert.mp3"


try:
    model = joblib.load(MODEL_FILE)
except Exception:
    model = None


LANGUAGE_CODES = {
    "English": "en",
    "Tamil": "ta",
    "Hindi": "hi",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Turkish": "tr",
    "Dutch": "nl",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese": "zh-CN",
    "Arabic": "ar"
}


def detect_location():

    try:
        response = requests.get(
            "https://hackmyip.com/api/ip",
            timeout=5
        )

        data = response.json()

        if data.get("success"):

            location = data.get("data", {})
            location_data = location.get("location", {})

            city = location_data.get("city", "Unknown")
            state = location_data.get("region", "Unknown")
            country = location_data.get("country", "Unknown")

            return city, state, country

    except Exception:
        pass

    return "Unknown", "Unknown", "Unknown"


def get_language(country, state):

    country = str(country).lower().strip()
    state = str(state).lower().strip()

    if country == "in":

        if "tamil" in state:
            return "Tamil"

        if "telangana" in state or "andhra" in state:
            return "Telugu"

        if "karnataka" in state:
            return "Kannada"

        if "kerala" in state:
            return "Malayalam"

        return "English"

    country_languages = {

        "us": "English",
        "gb": "English",
        "ca": "English",
        "au": "English",

        "es": "Spanish",
        "mx": "Spanish",

        "fr": "French",

        "de": "German",

        "it": "Italian",

        "pt": "Portuguese",
        "br": "Portuguese",

        "ru": "Russian",

        "tr": "Turkish",

        "nl": "Dutch",

        "jp": "Japanese",

        "kr": "Korean",

        "cn": "Chinese",

        "ae": "Arabic",
        "sa": "Arabic",
        "eg": "Arabic"
    }

    return country_languages.get(country, "English")


def get_voice_message(result, language):

    messages = {

        "English": {
            "SAFE": "This QR code appears safe. You may proceed.",
            "SUSPICIOUS": "Warning. This QR code appears suspicious. Please verify before proceeding.",
            "DANGEROUS": "Danger. This QR code appears dangerous. Do not proceed."
        },

        "Tamil": {
            "SAFE": "இந்த QR குறியீடு பாதுகாப்பாக உள்ளது. நீங்கள் தொடரலாம்.",
            "SUSPICIOUS": "எச்சரிக்கை. இந்த QR குறியீடு சந்தேகத்திற்குரியது. தொடர்வதற்கு முன் சரிபார்க்கவும்.",
            "DANGEROUS": "ஆபத்து. இந்த QR குறியீடு ஆபத்தானதாக இருக்கலாம். தொடர வேண்டாம்."
        },

        "Hindi": {
            "SAFE": "यह QR कोड सुरक्षित दिखाई देता है। आप आगे बढ़ सकते हैं।",
            "SUSPICIOUS": "चेतावनी। यह QR कोड संदिग्ध दिखाई देता है। आगे बढ़ने से पहले जांच करें।",
            "DANGEROUS": "खतरा। यह QR कोड खतरनाक दिखाई देता है। आगे न बढ़ें।"
        },

        "Telugu": {
            "SAFE": "ఈ QR కోడ్ సురక్షితంగా కనిపిస్తోంది. మీరు కొనసాగవచ్చు.",
            "SUSPICIOUS": "హెచ్చరిక. ఈ QR కోడ్ అనుమానాస్పదంగా కనిపిస్తోంది. కొనసాగించే ముందు తనిఖీ చేయండి.",
            "DANGEROUS": "ప్రమాదం. ఈ QR కోడ్ ప్రమాదకరంగా కనిపిస్తోంది. కొనసాగవద్దు."
        },

        "Kannada": {
            "SAFE": "ಈ QR ಕೋಡ್ ಸುರಕ್ಷಿತವಾಗಿದೆ. ನೀವು ಮುಂದುವರಿಯಬಹುದು.",
            "SUSPICIOUS": "ಎಚ್ಚರಿಕೆ. ಈ QR ಕೋಡ್ ಅನುಮಾನಾಸ್ಪದವಾಗಿದೆ. ಮುಂದುವರಿಯುವ ಮೊದಲು ಪರಿಶೀಲಿಸಿ.",
            "DANGEROUS": "ಅಪಾಯ. ಈ QR ಕೋಡ್ ಅಪಾಯಕಾರಿಯಾಗಿರಬಹುದು. ಮುಂದುವರಿಯಬೇಡಿ."
        },

        "Malayalam": {
            "SAFE": "ഈ QR കോഡ് സുരക്ഷിതമാണെന്ന് തോന്നുന്നു. നിങ്ങൾക്ക് തുടരാം.",
            "SUSPICIOUS": "മുന്നറിയിപ്പ്. ഈ QR കോഡ് സംശയാസ്പദമാണ്. തുടരുന്നതിന് മുമ്പ് പരിശോധിക്കുക.",
            "DANGEROUS": "അപകടം. ഈ QR കോഡ് അപകടകരമാണെന്ന് തോന്നുന്നു. തുടരരുത്."
        },

        "Spanish": {
            "SAFE": "Este código QR parece seguro. Puede continuar.",
            "SUSPICIOUS": "Advertencia. Este código QR parece sospechoso. Verifique antes de continuar.",
            "DANGEROUS": "Peligro. Este código QR parece peligroso. No continúe."
        },

        "French": {
            "SAFE": "Ce code QR semble sûr. Vous pouvez continuer.",
            "SUSPICIOUS": "Attention. Ce code QR semble suspect. Vérifiez avant de continuer.",
            "DANGEROUS": "Danger. Ce code QR semble dangereux. Ne continuez pas."
        },

        "German": {
            "SAFE": "Dieser QR-Code scheint sicher zu sein. Sie können fortfahren.",
            "SUSPICIOUS": "Warnung. Dieser QR-Code erscheint verdächtig. Bitte überprüfen Sie ihn.",
            "DANGEROUS": "Gefahr. Dieser QR-Code scheint gefährlich zu sein. Fahren Sie nicht fort."
        },

        "Italian": {
            "SAFE": "Questo codice QR sembra sicuro. Puoi procedere.",
            "SUSPICIOUS": "Attenzione. Questo codice QR sembra sospetto. Verifica prima di procedere.",
            "DANGEROUS": "Pericolo. Questo codice QR sembra pericoloso. Non procedere."
        },

        "Portuguese": {
            "SAFE": "Este código QR parece seguro. Você pode continuar.",
            "SUSPICIOUS": "Aviso. Este código QR parece suspeito. Verifique antes de continuar.",
            "DANGEROUS": "Perigo. Este código QR parece perigoso. Não prossiga."
        },

        "Russian": {
            "SAFE": "Этот QR-код выглядит безопасным. Вы можете продолжить.",
            "SUSPICIOUS": "Предупреждение. Этот QR-код выглядит подозрительно. Проверьте его.",
            "DANGEROUS": "Опасность. Этот QR-код может быть опасным. Не продолжайте."
        },

        "Turkish": {
            "SAFE": "Bu QR kodu güvenli görünüyor. Devam edebilirsiniz.",
            "SUSPICIOUS": "Uyarı. Bu QR kodu şüpheli görünüyor. Devam etmeden önce kontrol edin.",
            "DANGEROUS": "Tehlike. Bu QR kodu tehlikeli görünüyor. Devam etmeyin."
        },

        "Dutch": {
            "SAFE": "Deze QR-code lijkt veilig. U kunt doorgaan.",
            "SUSPICIOUS": "Waarschuwing. Deze QR-code lijkt verdacht. Controleer voordat u doorgaat.",
            "DANGEROUS": "Gevaar. Deze QR-code lijkt gevaarlijk. Ga niet verder."
        },

        "Japanese": {
            "SAFE": "このQRコードは安全なようです。続行できます。",
            "SUSPICIOUS": "警告。このQRコードは疑わしい可能性があります。続行する前に確認してください。",
            "DANGEROUS": "危険。このQRコードは危険な可能性があります。続行しないでください。"
        },

        "Korean": {
            "SAFE": "이 QR 코드는 안전해 보입니다. 계속 진행할 수 있습니다.",
            "SUSPICIOUS": "경고. 이 QR 코드는 의심스러워 보입니다. 계속하기 전에 확인하세요.",
            "DANGEROUS": "위험. 이 QR 코드는 위험할 수 있습니다. 진행하지 마세요."
        },

        "Chinese": {
            "SAFE": "此二维码看起来是安全的。您可以继续。",
            "SUSPICIOUS": "警告。此二维码看起来可疑。继续之前请先验证。",
            "DANGEROUS": "危险。此二维码可能存在风险。请勿继续。"
        },

        "Arabic": {
            "SAFE": "يبدو أن رمز الاستجابة السريعة هذا آمن. يمكنك المتابعة.",
            "SUSPICIOUS": "تحذير. يبدو أن رمز الاستجابة السريعة هذا مشبوه. تحقق قبل المتابعة.",
            "DANGEROUS": "خطر. يبدو أن رمز الاستجابة السريعة هذا خطير. لا تتابع."
        }
    }

    return messages.get(language, messages["English"]).get(
        result,
        messages["English"]["SUSPICIOUS"]
    )


def create_voice(result, language):

    try:

        message = get_voice_message(result, language)

        code = LANGUAGE_CODES.get(language, "en")

        tts = gTTS(
            text=message,
            lang=code,
            slow=False
        )

        tts.save(VOICE_FILE)

        return True

    except Exception:
        return False


def extract_upi_details(data):

    try:

        parsed = urlparse(data)

        params = parse_qs(parsed.query)

        upi_id = params.get("pa", ["Unknown"])[0]
        merchant = params.get("pn", ["Unknown"])[0]
        amount = params.get("am", ["Not specified"])[0]

        return upi_id, merchant, amount

    except Exception:

        return "Unknown", "Unknown", "Not specified"


def analyze_upi(data):

    text = data.lower()

    dangerous_patterns = [
        "verify-bank-secure",
        "verify-bank",
        "account-verify",
        "urgent",
        "payment-verify",
        "bank-secure"
    ]

    suspicious_patterns = [
        "verify",
        "login",
        "update",
        "secure",
        "confirm",
        "validation",
        "authenticate"
    ]

    for pattern in dangerous_patterns:

        if pattern in text:

            return (
                "DANGEROUS",
                "Dangerous payment pattern detected"
            )

    for pattern in suspicious_patterns:

        if pattern in text:

            return (
                "SUSPICIOUS",
                "Suspicious payment pattern detected"
            )

    return (
        "SAFE",
        "No major suspicious payment pattern detected"
    )


def analyze_url(url):

    reasons = []
    score_danger = False
    score_suspicious = False

    try:

        parsed = urlparse(url)
        hostname = parsed.hostname

        if not hostname:

            return (
                "DANGEROUS",
                "Invalid or unsafe URL detected"
            )

        try:

            ipaddress.ip_address(hostname)

            score_danger = True
            reasons.append("IP address used instead of a domain")

        except Exception:
            pass

        if len(url) > 75:

            score_danger = True
            reasons.append("Unusually long URL")

        elif len(url) >= 54:

            score_suspicious = True
            reasons.append("Long URL detected")

        if "https" not in url.lower():

            score_suspicious = True
            reasons.append("HTTPS protection not detected")

        if "-" in hostname:

            score_suspicious = True
            reasons.append("Suspicious domain structure")

        suspicious_words = [
            "login",
            "verify",
            "update",
            "secure",
            "account",
            "password",
            "bank",
            "confirm"
        ]

        for word in suspicious_words:

            if word in url.lower():

                score_suspicious = True
                reasons.append(
                    "Suspicious keyword detected: " + word
                )
                break

        if model is not None:

            try:

                features = [
                    len(url),
                    1 if "https" in url.lower() else 0,
                    1 if "-" in hostname else 0,
                    1 if score_danger else 0
                ]

                prediction = model.predict([features])[0]

                if prediction == -1:

                    score_danger = True
                    reasons.append(
                        "Machine learning model detected phishing characteristics"
                    )

            except Exception:
                pass

        if score_danger:

            return (
                "DANGEROUS",
                "; ".join(reasons) if reasons else "Dangerous URL detected"
            )

        if score_suspicious:

            return (
                "SUSPICIOUS",
                "; ".join(reasons) if reasons else "Suspicious URL detected"
            )

        return (
            "SAFE",
            "No major suspicious URL characteristics detected"
        )

    except Exception:

        return (
            "DANGEROUS",
            "Unable to safely analyze this URL"
        )


def decode_qr(image):

    try:

        image_array = image

        detector = cv2.QRCodeDetector()

        data, points, _ = detector.detectAndDecode(image_array)

        if data:

            return data

    except Exception:
        pass

    return None


st.title("🛡️ AI-Powered QR Code Phishing Risk Predictor")

st.write(
    "AI-based QR security analysis with multilingual voice alerts"
)


st.divider()


city, state, country = detect_location()

automatic_language = get_language(country, state)


st.subheader("🌍 Location & Language")


col1, col2 = st.columns(2)

with col1:

    st.write("**City:**", city)
    st.write("**State / Region:**", state)
    st.write("**Country:**", country)


with col2:

    st.write(
        "**Automatic Language:**",
        automatic_language
    )


manual_language = st.selectbox(
    "🔊 Choose Alert Language",
    list(LANGUAGE_CODES.keys()),
    index=list(LANGUAGE_CODES.keys()).index(
        automatic_language
    )
)


st.info(
    "Automatic language is selected from detected location. "
    "Manual language can be used as an override."
)


st.divider()


st.subheader("📷 QR Code Scanner")


source = st.radio(
    "Select QR input",
    ["Camera", "Upload Image"],
    horizontal=True
)


image = None


if source == "Camera":

    camera_image = st.camera_input(
        "Scan a QR Code"
    )

    if camera_image is not None:

        file_bytes = camera_image.getvalue()

        image = cv2.imdecode(
            __import__("numpy").frombuffer(
                file_bytes,
                dtype=__import__("numpy").uint8
            ),
            cv2.IMREAD_COLOR
        )


else:

    uploaded_image = st.file_uploader(
        "Upload QR image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_image is not None:

        file_bytes = uploaded_image.getvalue()

        image = cv2.imdecode(
            __import__("numpy").frombuffer(
                file_bytes,
                dtype=__import__("numpy").uint8
            ),
            cv2.IMREAD_COLOR
        )


if image is not None:

    decoded_data = decode_qr(image)

    if decoded_data:

        st.success("✅ QR Code detected successfully")

        st.subheader("🔎 Decoded QR Data")

        st.code(decoded_data)


        if decoded_data.lower().startswith("upi://"):

            qr_type = "UPI Payment QR"

            upi_id, merchant, amount = extract_upi_details(
                decoded_data
            )

            result, reason = analyze_upi(
                decoded_data
            )

            st.subheader("💳 QR Details")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write("**UPI ID**")
                st.write(upi_id)

            with col2:
                st.write("**Merchant**")
                st.write(merchant)

            with col3:
                st.write("**Amount**")
                st.write(amount)

        else:

            qr_type = "URL / Web QR"

            result, reason = analyze_url(
                decoded_data
            )

            st.subheader("🌐 QR Details")

            st.write("**Detected URL:**")
            st.code(decoded_data)


        st.divider()


        st.subheader("🛡️ SECURITY ANALYSIS")


        st.write("**QR TYPE**")
        st.write(qr_type)


        if result == "SAFE":

            st.success(
                "🟢 SAFE"
            )

            action = "PROCEED"

            st.write(
                "No major security threats detected."
            )

        elif result == "SUSPICIOUS":

            st.warning(
                "🟠 SUSPICIOUS"
            )

            action = "VERIFY"

            st.write(
                "This QR contains characteristics that require verification."
            )

        else:

            st.error(
                "🔴 DANGEROUS"
            )

            action = "DO NOT PROCEED"

            st.write(
                "This QR may expose the user to phishing or fraudulent activity."
            )


        st.subheader("🔍 Reason")

        st.info(reason)


        st.subheader("🚦 Recommended Action")


        if result == "SAFE":

            st.success(
                "🟢 PROCEED"
            )

        elif result == "SUSPICIOUS":

            st.warning(
                "🟠 VERIFY BEFORE PROCEEDING"
            )

        else:

            st.error(
                "🔴 DO NOT PROCEED"
            )


        st.subheader("🔊 Voice Alert")

        st.write(
            "Alert Language:",
            manual_language
        )


        if st.button(
            "🔊 Play Voice Alert",
            use_container_width=True
        ):

            success = create_voice(
                result,
                manual_language
            )

            if success:

                audio_file = open(
                    VOICE_FILE,
                    "rb"
                )

                st.audio(
                    audio_file.read(),
                    format="audio/mp3"
                )

                st.success(
                    "Voice alert generated successfully."
                )

            else:

                st.error(
                    "Unable to generate voice alert."
                )


    else:

        st.warning(
            "⚠️ No QR code detected. Please try another image."
        )


st.divider()


st.caption(
    "AI-Powered QR Code Phishing Risk Predictor with Multilingual Voice Alert Agent"
)