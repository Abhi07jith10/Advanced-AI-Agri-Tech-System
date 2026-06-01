# 🌱 Tomato Doctor - Smart Irrigation & Disease Detection System

A smart agricultural IoT system that merges Edge AI (YOLOv8) and Cloud AI (Gemini & Groq) to diagnose tomato plant diseases and autonomously manage irrigation based on real-time environmental conditions.

## ✨ Key Features

### 🧠 AI & Diagnostics Architecture
* **Local Edge Vision:** Instantly detects diseases locally using a custom YOLOv8 (`best.pt`) model optimized for high-resolution (800px) leaf analysis.
* **Cloud Fallback:** Seamlessly routes to **Google Gemini 2.5 Flash** for deep analysis and remedy generation if the local YOLO model lacks confidence.
* **Input Guardrails:** Utilizes **Groq (Llama 3.2 Vision)** to verify that uploaded images are actual plants before running costly diagnostic compute.
* **Diagnosis Logging:** Automatically logs visual evidence, AI confidence percentages, and prescribed remedies.

### 💧 Smart Irrigation Logic
The system splits decision-making into two distinct modes:
* **Manual Mode (Target-Driven):** The user sets a strict soil moisture threshold (e.g., 40%) via the dashboard slider. The system ignores the weather and waters the plant strictly to maintain this exact percentage.
* **Auto Mode (Weather-Adaptive):** The system calculates the plant's needs dynamically:
    * *Base Threshold:* 30% Moisture
    * *Heat Compensation:* Adds +10% if the temperature exceeds 30°C.
    * *Dry Air Compensation:* Adds +5% if humidity drops below 40%.
* **Manual Override:** Dashboard ON/OFF buttons bypass all sensor logic, forcing the pump on or off for exactly 30 seconds before returning to automated monitoring.

---

## 🛠️ Hardware Setup

### Components
* **Microcontroller:** ESP32 Dev Module
* **Sensors:** DHT11 (Temperature & Humidity), Capacitive Soil Moisture Sensor (v1.2)
* **Actuator:** 5V Relay Module (Active-Low) + Mini Water Pump
* **Power:** 18650 Battery (Pump Muscle) + 5V USB/Power Bank (ESP32 Brain)

### 🔌 ESP32 Pin Connections
| Component | ESP32 Pin | Notes |
| :--- | :--- | :--- |
| **DHT11 Data** | `Pin 4` | |
| **Soil Sensor** | `Pin 34` | Analog input |
| **Relay Signal** | `Pin 26` | Active-Low logic |

*(Note: Ensure your ESP32 Serial Monitor is set to `115200` baud rate.)*

---

## ⚙️ Installation & Setup

### 1. Install Dependencies
Ensure you have Python 3.8+ installed, then install the required libraries:
```bash
pip install -r requirements.txt
```

### 2. Environment Variables (.env)
Create a `.env` file in the root directory of your project and add your cloud API keys:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Network Configuration
This system uses a local Flask server communicating with the ESP32 over Wi-Fi. 
1. Host a Mobile Hotspot from your laptop.
2. Ensure the ESP32 C++ code is updated with your laptop's hotspot IP address (typically `192.168.137.1`).

### 4. Start the Server
Run the Flask application to start the dashboard and API listeners:
```bash
python app.py
```
Access the web dashboard at: `http://localhost:5000`