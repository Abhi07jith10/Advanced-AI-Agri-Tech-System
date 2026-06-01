import os
import json
import socket
import time
import io
import base64
from flask import Flask, render_template, request, jsonify
from PIL import Image
from zeroconf import ServiceInfo, Zeroconf

# --- 🧠 AI LIBRARIES ---
from ultralytics import YOLO
from groq import Groq

app = Flask(__name__)

# --- ⚙️ STATE & CONFIGURATION ---
HARDWARE_DATA = {
    "temperature": 0.0,
    "humidity": 0.0,
    "soil_moisture": 0.0,
    "pump_status": False
}

SYSTEM_SETTINGS = {
    "mode": "manual",
    "manual_threshold": 40,
    "auto_threshold": 30
}

OVERRIDE_DURATION = 30  
last_user_action_time = 0

# --- 🤖 AI CONFIGURATION ---
CONFIDENCE_THRESHOLD = 0.55
LOCAL_MODEL = None
client_groq = None

# Load Groq Key
try:
    groq_key = "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"
    if groq_key:
        client_groq = Groq(api_key=groq_key)
except:
    print("⚠️ Groq API Key missing or invalid.")

# Load YOLO Model
print("⏳ Loading YOLO model...")
try:
    LOCAL_MODEL = YOLO("best.pt")
    print("✅ YOLO Model Loaded: best.pt")
except Exception as e:
    print(f"⚠️ YOLO Error: {e}")

# --- 🏠 STARTUP HELPER ---
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except: 
        return "127.0.0.1"

# --- 🌐 mDNS SETUP ---
def register_mdns():
    desc = {'path': '/'}
    info = ServiceInfo(
        "_http._tcp.local.",
        "agribot._http._tcp.local.",
        addresses=[socket.inet_aton(get_local_ip())],
        port=5000,
        properties=desc,
        server="agribot.local.",
    )
    zeroconf = Zeroconf()
    try:
        zeroconf.register_service(info)
    except Exception as e:
        print(f"⚠️ mDNS Warning: {e} (continuing anyway)")
    return zeroconf

# --- 🧠 SMART IRRIGATION LOGIC ---
def run_smart_irrigation():
    global HARDWARE_DATA, SYSTEM_SETTINGS, last_user_action_time

    # ⏳ 0. Check Manual Override Timer
    if time.time() - last_user_action_time < OVERRIDE_DURATION:
        return # Do not change pump state during override period!

    if SYSTEM_SETTINGS["mode"] == "manual":
        slider_value = SYSTEM_SETTINGS["manual_threshold"]
        if slider_value < 40:
            HARDWARE_DATA["pump_status"] = True
        else:
            HARDWARE_DATA["pump_status"] = False

    elif SYSTEM_SETTINGS["mode"] == "auto":
        calc_threshold = 30
        if HARDWARE_DATA["temperature"] > 30: calc_threshold += 10
        if HARDWARE_DATA["humidity"] < 40:  calc_threshold += 5

        if HARDWARE_DATA["soil_moisture"] < calc_threshold:
            HARDWARE_DATA["pump_status"] = True
        else:
            HARDWARE_DATA["pump_status"] = False

# --- 📡 WIFI ROUTES (ESP32) ---
@app.route('/update_sensors', methods=['POST'])
def update_sensors():
    global HARDWARE_DATA
    try:
        data = request.json
        HARDWARE_DATA["temperature"] = float(data.get("temperature", 0))
        HARDWARE_DATA["humidity"] = float(data.get("humidity", 0))
        HARDWARE_DATA["soil_moisture"] = float(data.get("moisture", 0))

        run_smart_irrigation()

        status = "PUMP_ON" if HARDWARE_DATA["pump_status"] else "PUMP_OFF"
        return status
    except Exception as e:
        return "ERROR", 400

# --- 🖥️ DASHBOARD ROUTES ---
@app.route('/api/hardware', methods=['GET'])
def get_hardware_status():
    response = HARDWARE_DATA.copy()
    response.update(SYSTEM_SETTINGS)
    return jsonify(response)

@app.route('/api/settings', methods=['POST'])
def update_settings():
    global SYSTEM_SETTINGS
    data = request.json
    if 'mode' in data: SYSTEM_SETTINGS['mode'] = data['mode']
    if 'manual_threshold' in data:
        try: SYSTEM_SETTINGS['manual_threshold'] = float(data['manual_threshold'])
        except: pass
    run_smart_irrigation()
    return jsonify({"status": "updated", "settings": SYSTEM_SETTINGS})

@app.route('/api/pump', methods=['POST'])
def toggle_pump():
    global HARDWARE_DATA, last_user_action_time
    data = request.json
    action = data.get('action')
    
    last_user_action_time = time.time()
    
    if action == 'on': HARDWARE_DATA["pump_status"] = True
    elif action == 'off': HARDWARE_DATA["pump_status"] = False
    elif action == 'toggle': HARDWARE_DATA["pump_status"] = not HARDWARE_DATA["pump_status"]
    
    print(f"🕹️ Manual Override: Pausing auto for {OVERRIDE_DURATION}s")
    return jsonify({"status": "success", "pump_state": HARDWARE_DATA["pump_status"]})

# --- 📸 CAMERA & AI ANALYSIS ---
def analyze_with_groq(pil_image):
    """Checks if it is a plant and finds disease in one go using Groq."""
    if client_groq is None:
        return {"status": "Error", "diagnosis": "Groq API not configured."}

    try:
        if pil_image.mode != 'RGB': pil_image = pil_image.convert('RGB')
        buffered = io.BytesIO()
        pil_image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        base64_url = f"data:image/jpeg;base64,{img_str}"

        prompt = """
        Analyze this image:
        1. Is this a plant/leaf? (Yes/No)
        2. If No, return {"status": "Invalid", "diagnosis": "Not a plant"}.
        3. If Yes, check if it is Healthy or Diseased.
        4. Identify the disease name and provide 3 short remedies.
        Return ONLY JSON: {"status": "Healthy/Diseased", "disease_name": "Name", "confidence": 90, "diagnosis": "1-sentence description", "remedies": ["step 1", "step 2", "step 3"]}
        """

        chat = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": base64_url}}]}],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            response_format={"type": "json_object"}
        )
        return json.loads(chat.choices[0].message.content)
    except Exception as e:
        return {"status": "Error", "diagnosis": str(e)}

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handles manual file uploads from the Web UI."""
    if 'file' not in request.files: return jsonify({'error': 'No file'})
    file = request.files['file']
    fallback = request.form.get('fallback') == 'true'
    
    try:
        img = Image.open(file.stream)
        
        # First try Local YOLO
        if LOCAL_MODEL:
            results = LOCAL_MODEL(img, imgsz=800, verbose=False) # Keep 800 for tiny spots
            if results and results[0].boxes and len(results[0].boxes) > 0:
                top_box = max(results[0].boxes, key=lambda x: x.conf[0])
                if top_box.conf[0] > CONFIDENCE_THRESHOLD:
                    label = results[0].names[int(top_box.cls[0])]
                    is_healthy = 'healthy' in label.lower()
                    return jsonify({
                        "status": "Healthy" if is_healthy else "Diseased",
                        "disease_name": label.replace('_', ' ').title(),
                        "confidence": round(float(top_box.conf[0]) * 100, 2),
                        "diagnosis": "Local AI confirmed the plant status.",
                        "remedies": ["Regular checkups"] if is_healthy else ["Remove leaves", "Apply treatment"]
                    })
        
        # Fallback to Groq if YOLO is unsure or fallback is forced
        return jsonify(analyze_with_groq(img))
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    ip = get_local_ip()
    mdns = register_mdns()
    print(f"\n🚀 SERVER LIVE")
    print(f"👉 Local: http://localhost:5000")
    print(f"👉 mDNS: http://agribot.local:5000")
    print(f"👉 ESP32 URL: http://{ip}:5000/update_sensors\n")

    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        Zeroconf().unregister_all_services()