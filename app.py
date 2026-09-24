import cv2
from gtts import gTTS
from playsound3 import playsound
import joblib
import ipaddress
import requests
from urllib.parse import urlparse, parse_qs


# ---------------- LOAD MODEL ----------------

model = joblib.load("qr_phishing_model.pkl")


# ---------------- LOCATION DETECTION ----------------

def detect_location():

    try:
        response = requests.get(
            "https://hackmyip.com/api/ip",
            timeout=5
        )

        data = response.json()

        location = data["data"]["location"]

        city = location.get("city", "Unknown")
        state = location.get("region", "Unknown")
        country = location.get("country", "Unknown")

        print("\nLocation Detection")
        print("City:", city)
        print("State/Region:", state)
        print("Country:", country)

        return city, state, country

    except Exception as e:

        print("\nLocation detection failed.")
        print("Using default location: Tamil Nadu")

        return "Unknown", "Tamil Nadu", "IN"


# ---------------- AUTOMATIC LANGUAGE ----------------

def get_language(state, country):

    state = str(state).lower()
    country = str(country).lower()

    if "tamil" in state or "tamil nadu" in state:
        return "Tamil"

    elif "telangana" in state or "andhra" in state:
        return "Telugu"

    elif "karnataka" in state:
        return "Kannada"

    elif "kerala" in state:
        return "Malayalam"

    elif country in ["es", "spain", "mexico", "argentina", "colombia", "chile"]:
        return "Spanish"

    elif country in ["fr", "france", "belgium", "canada"]:
        return "French"

    elif country in ["de", "germany", "austria", "switzerland"]:
        return "German"

    elif country in ["it", "italy"]:
        return "Italian"

    elif country in ["jp", "japan"]:
        return "Japanese"

    elif country in ["kr", "south korea"]:
        return "Korean"

    elif country in ["cn", "china"]:
        return "Chinese"

    elif country in ["ae", "sa", "qa", "eg", "arabic"]:
        return "Arabic"

    elif country in ["pt", "brazil", "portugal"]:
        return "Portuguese"

    elif country in ["ru", "russia"]:
        return "Russian"

    elif country in ["tr", "turkey"]:
        return "Turkish"

    elif country in ["nl", "netherlands"]:
        return "Dutch"

    else:
        return "English"


# ---------------- MANUAL LANGUAGE ----------------

def manual_language_option():

    print("\nChange Alert Language")

    print("1. English")
    print("2. Tamil")
    print("3. Telugu")
    print("4. Kannada")
    print("5. Malayalam")
    print("6. Spanish")
    print("7. French")
    print("8. German")
    print("9. Italian")
    print("10. Japanese")
    print("11. Korean")
    print("12. Chinese")
    print("13. Arabic")
    print("14. Portuguese")
    print("15. Russian")
    print("16. Turkish")
    print("17. Dutch")
    print("18. Cancel")

    choice = input("Select option: ").strip()

    languages = {
        "1": "English",
        "2": "Tamil",
        "3": "Telugu",
        "4": "Kannada",
        "5": "Malayalam",
        "6": "Spanish",
        "7": "French",
        "8": "German",
        "9": "Italian",
        "10": "Japanese",
        "11": "Korean",
        "12": "Chinese",
        "13": "Arabic",
        "14": "Portuguese",
        "15": "Russian",
        "16": "Turkish",
        "17": "Dutch"
    }

    return languages.get(choice)


# ---------------- VOICE ALERT ----------------

def voice_alert(result, language):

    messages = {

        "English": {
            "SAFE": "This QR code appears safe. You can proceed.",
            "SUSPICIOUS": "Warning. This QR code appears suspicious. Please verify before proceeding.",
            "DANGEROUS": "Danger. This QR code appears dangerous. Do not proceed."
        },

        "Tamil": {
            "SAFE": "இந்த QR குறியீடு பாதுகாப்பாக உள்ளது. நீங்கள் தொடரலாம்.",
            "SUSPICIOUS": "எச்சரிக்கை. இந்த QR குறியீடு சந்தேகத்திற்குரியது. தொடர்வதற்கு முன் சரிபார்க்கவும்.",
            "DANGEROUS": "ஆபத்து. இந்த QR குறியீடு ஆபத்தானதாக இருக்கலாம். தொடர வேண்டாம்."
        },

        "Telugu": {
            "SAFE": "ఈ QR కోడ్ సురక్షితంగా కనిపిస్తోంది. మీరు కొనసాగవచ్చు.",
            "SUSPICIOUS": "హెచ్చరిక. ఈ QR కోడ్ అనుమానాస్పదంగా ఉంది. కొనసాగించే ముందు తనిఖీ చేయండి.",
            "DANGEROUS": "ప్రమాదం. ఈ QR కోడ్ ప్రమాదకరంగా ఉండవచ్చు. కొనసాగవద్దు."
        },

        "Kannada": {
            "SAFE": "ಈ QR ಕೋಡ್ ಸುರಕ್ಷಿತವಾಗಿ ಕಾಣುತ್ತದೆ. ನೀವು ಮುಂದುವರಿಯಬಹುದು.",
            "SUSPICIOUS": "ಎಚ್ಚರಿಕೆ. ಈ QR ಕೋಡ್ ಅನುಮಾನಾಸ್ಪದವಾಗಿದೆ. ಮುಂದುವರಿಯುವ ಮೊದಲು ಪರಿಶೀಲಿಸಿ.",
            "DANGEROUS": "ಅಪಾಯ. ಈ QR ಕೋಡ್ ಅಪಾಯಕಾರಿಯಾಗಿರಬಹುದು. ಮುಂದುವರಿಯಬೇಡಿ."
        },

        "Malayalam": {
            "SAFE": "ഈ QR കോഡ് സുരക്ഷിതമാണെന്ന് തോന്നുന്നു. നിങ്ങൾക്ക് തുടരാം.",
            "SUSPICIOUS": "മുന്നറിയിപ്പ്. ഈ QR കോഡ് സംശയാസ്പദമാണ്. തുടരുന്നതിന് മുമ്പ് പരിശോധിക്കുക.",
            "DANGEROUS": "അപകടം. ഈ QR കോഡ് അപകടകരമായിരിക്കാം. തുടരരുത്."
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
            "SUSPICIOUS": "Warnung. Dieser QR-Code scheint verdächtig zu sein. Überprüfen Sie ihn vor dem Fortfahren.",
            "DANGEROUS": "Gefahr. Dieser QR-Code scheint gefährlich zu sein. Fahren Sie nicht fort."
        },

        "Italian": {
            "SAFE": "Questo codice QR sembra sicuro. Puoi procedere.",
            "SUSPICIOUS": "Attenzione. Questo codice QR sembra sospetto. Verifica prima di procedere.",
            "DANGEROUS": "Pericolo. Questo codice QR sembra pericoloso. Non procedere."
        },

        "Japanese": {
            "SAFE": "このQRコードは安全なようです。続行できます。",
            "SUSPICIOUS": "警告。このQRコードは疑わしい可能性があります。続行する前に確認してください。",
            "DANGEROUS": "危険。このQRコードは危険な可能性があります。続行しないでください。"
        },

        "Korean": {
            "SAFE": "이 QR 코드는 안전한 것으로 보입니다. 계속 진행할 수 있습니다.",
            "SUSPICIOUS": "경고. 이 QR 코드는 의심스러워 보입니다. 계속하기 전에 확인하세요.",
            "DANGEROUS": "위험. 이 QR 코드는 위험할 수 있습니다. 진행하지 마세요."
        },

        "Chinese": {
            "SAFE": "此二维码看起来是安全的。您可以继续。",
            "SUSPICIOUS": "警告。此二维码看起来可疑。请在继续之前进行验证。",
            "DANGEROUS": "危险。此二维码可能存在危险。请不要继续。"
        },

        "Arabic": {
            "SAFE": "يبدو أن رمز QR هذا آمن. يمكنك المتابعة.",
            "SUSPICIOUS": "تحذير. يبدو أن رمز QR هذا مشبوه. يرجى التحقق قبل المتابعة.",
            "DANGEROUS": "خطر. قد يكون رمز QR هذا خطيراً. لا تتابع."
        },

        "Portuguese": {
            "SAFE": "Este código QR parece seguro. Você pode continuar.",
            "SUSPICIOUS": "Aviso. Este código QR parece suspeito. Verifique antes de continuar.",
            "DANGEROUS": "Perigo. Este código QR parece perigoso. Não continue."
        },

        "Russian": {
            "SAFE": "Этот QR-код выглядит безопасным. Вы можете продолжить.",
            "SUSPICIOUS": "Предупреждение. Этот QR-код выглядит подозрительно. Проверьте его перед продолжением.",
            "DANGEROUS": "Опасность. Этот QR-код может быть опасным. Не продолжайте."
        },

        "Turkish": {
            "SAFE": "Bu QR kodu güvenli görünüyor. Devam edebilirsiniz.",
            "SUSPICIOUS": "Uyarı. Bu QR kodu şüpheli görünüyor. Devam etmeden önce doğrulayın.",
            "DANGEROUS": "Tehlike. Bu QR kodu tehlikeli olabilir. Devam etmeyin."
        },

        "Dutch": {
            "SAFE": "Deze QR-code lijkt veilig. U kunt doorgaan.",
            "SUSPICIOUS": "Waarschuwing. Deze QR-code lijkt verdacht. Controleer deze voordat u doorgaat.",
            "DANGEROUS": "Gevaar. Deze QR-code kan gevaarlijk zijn. Ga niet verder."
        }
    }

    language_codes = {
        "English": "en",
        "Tamil": "ta",
        "Telugu": "te",
        "Kannada": "kn",
        "Malayalam": "ml",
        "Spanish": "es",
        "French": "fr",
        "German": "de",
        "Italian": "it",
        "Japanese": "ja",
        "Korean": "ko",
        "Chinese": "zh-CN",
        "Arabic": "ar",
        "Portuguese": "pt",
        "Russian": "ru",
        "Turkish": "tr",
        "Dutch": "nl"
    }

    message = messages.get(
        language,
        messages["English"]
    ).get(
        result,
        messages["English"]["SUSPICIOUS"]
    )

    print("Alert Language:", language)

    try:

        speech = gTTS(
            text=message,
            lang=language_codes.get(language, "en"),
            slow=False
        )

        speech.save("qr_alert.mp3")

        playsound("qr_alert.mp3")

    except Exception as e:

        print("Voice Error:", e)


# ---------------- UPI QR DETECTION ----------------

def is_upi_qr(data):

    return data.lower().strip().startswith("upi://pay")


# ---------------- EXTRACT UPI DETAILS ----------------

def extract_upi_details(data):

    try:

        query = data.split("?", 1)[1]

        details = parse_qs(query)

        upi_id = details.get(
            "pa",
            ["Not available"]
        )[0]

        name = details.get(
            "pn",
            ["Not available"]
        )[0]

        amount = details.get(
            "am",
            ["Not specified"]
        )[0]

        return upi_id, name, amount

    except Exception:

        return (
            "Not available",
            "Not available",
            "Not specified"
        )


# ---------------- UPI ANALYSIS ----------------

def analyze_upi(data):

    upi_id, name, amount = extract_upi_details(data)

    upi_text = (
        upi_id + " " + name
    ).lower()

    dangerous_patterns = [
        "verify-bank-secure",
        "verify-bank",
        "account-verify",
        "urgent"
    ]

    for pattern in dangerous_patterns:

        if pattern in upi_text:

            return "DANGEROUS"

    suspicious_patterns = [
        "verify",
        "login",
        "update",
        "secure"
    ]

    for pattern in suspicious_patterns:

        if pattern in upi_text:

            return "SUSPICIOUS"

    return "SAFE"


# ---------------- URL ANALYSIS ----------------

def analyze_url(url):

    url_lower = url.lower()

    url_length = len(url)

    if url_length < 54:

        url_length_feature = 1

    elif url_length <= 75:

        url_length_feature = 0

    else:

        url_length_feature = -1

    hostname = urlparse(url).hostname or ""

    try:

        ipaddress.ip_address(hostname)

        having_ip = -1

    except ValueError:

        having_ip = 1

    if "https" in url_lower:

        https_token = -1

    else:

        https_token = 1

    if "-" in hostname:

        prefix_suffix = -1

    else:

        prefix_suffix = 1

    features = [[
        having_ip,
        url_length_feature,
        https_token,
        prefix_suffix
    ]]

    if having_ip == -1:

        return "DANGEROUS"

    try:

        prediction = model.predict(features)

        if prediction[0] == -1:

            return "DANGEROUS"

    except Exception as e:

        print("ML Model Error:", e)

    suspicious_words = [
        "login",
        "verify",
        "update",
        "secure",
        "account",
        "bank"
    ]

    for word in suspicious_words:

        if word in url_lower:

            return "SUSPICIOUS"

    return "SAFE"


# ---------------- FINAL DECISION ----------------

def user_decision(result):

    print("\nFinal Decision")

    if result == "SAFE":

        print("Status: SAFE")
        print("Decision: PROCEED")

        return "PROCEED"

    elif result == "SUSPICIOUS":

        print("Status: SUSPICIOUS")
        print("Decision: VERIFY")

        return "VERIFY"

    elif result == "DANGEROUS":

        print("Status: DANGEROUS")
        print("Decision: STOP")

        return "STOP"


# ---------------- PROGRAM START ----------------

print("\n==============================================")
print("AI-POWERED QR CODE PHISHING RISK PREDICTOR")
print("WITH MULTILINGUAL VOICE ALERT AGENT")
print("==============================================")


# ---------------- AUTOMATIC LOCATION ----------------

city, state, country = detect_location()

default_language = get_language(
    state,
    country
)

print("\nAutomatic Language:", default_language)


# ---------------- CAMERA ----------------

camera = cv2.VideoCapture(0)

detector = cv2.QRCodeDetector()

scanned = False

result = None

selected_language = default_language


print("\nQR Scanner Started...")
print("Waiting for QR code...")

print("\nControls:")
print("L = Change Language")
print("R = Replay Voice")
print("Q = Quit")


# ---------------- SCANNING LOOP ----------------

while True:

    ret, frame = camera.read()

    if not ret:

        print("\nCamera could not be opened.")

        break

    data, points, _ = detector.detectAndDecode(frame)

    if data and not scanned:

        scanned = True

        print("\nQR Data:", data)

        # ---------------- UPI QR ----------------

        if is_upi_qr(data):

            print("QR Type: UPI Payment QR")

            upi_id, name, amount = extract_upi_details(data)

            print("UPI ID:", upi_id)
            print("Merchant:", name)
            print("Amount:", amount)

            result = analyze_upi(data)

        # ---------------- URL QR ----------------

        else:

            print("QR Type: URL QR")

            result = analyze_url(data)

        print("\nClassification:", result)

        selected_language = default_language

        print(
            "Default Alert Language:",
            selected_language
        )

        voice_alert(
            result,
            selected_language
        )

        print("\nQR analysis completed.")

        print("\nPress Q for final decision.")
        print("Press L to change language.")
        print("Press R to replay voice.")


    # ---------------- CAMERA DISPLAY ----------------

    cv2.imshow(
        "AI QR Phishing Risk Predictor",
        frame
    )

    key = cv2.waitKey(1) & 0xFF


    # ---------------- Q KEY ----------------

    if key == ord("q"):

        if result is not None:

            decision = user_decision(result)

            print(
                "\nFinal Result:",
                decision
            )

        else:

            print("\nScanner closed.")

        break


    # ---------------- L KEY ----------------

    if key == ord("l") and result is not None:

        new_language = manual_language_option()

        if new_language is not None:

            selected_language = new_language

            print(
                "\nSelected Language:",
                selected_language
            )

            voice_alert(
                result,
                selected_language
            )


    # ---------------- R KEY ----------------

    if key == ord("r") and result is not None:

        print("\nReplaying voice...")

        voice_alert(
            result,
            selected_language
        )


# ---------------- CLOSE CAMERA ----------------

camera.release()

cv2.destroyAllWindows()

print("\nProgram completed.")