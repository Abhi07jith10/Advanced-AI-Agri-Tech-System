# Advanced-AI-Agri-Tech-System
A smart agriculture system that combines Artificial Intelligence (AI), Machine Learning (ML), and Internet of Things (IoT) technologies to improve crop monitoring and irrigation management. The system uses a custom-trained YOLO-based machine learning model to detect diseases in tomato leaves from uploaded images with high accuracy. Environmental data such as soil moisture, temperature, and humidity are continuously collected using sensors connected to an ESP32 microcontroller. Based on these real-time parameters, the system automatically controls irrigation to provide optimal water supply for plant growth. By integrating AI-powered disease diagnosis with automated irrigation, the project helps farmers improve crop health, reduce water wastage, and increase agricultural productivity.

## Features

### Tomato Disease Detection
- Upload tomato leaf images through a web interface.
- Disease detection using a custom-trained YOLO model (`best.pt`).
- Identifies healthy and diseased leaves.
- Displays disease name, confidence score, and remedies.
- Cloud AI fallback using Groq when local model confidence is low.

### Smart Irrigation System
- Real-time monitoring of:
  - Soil Moisture
  - Temperature
  - Humidity
- Automatic irrigation based on environmental conditions.
- Manual and Auto irrigation modes.
- Dynamic moisture threshold adjustment based on weather conditions.
- Manual pump override for emergency watering.

- ### IoT Connectivity
- ESP32 communicates with Flask server over Wi-Fi.
- Real-time sensor data updates.
- REST API endpoints for hardware monitoring and control.
- mDNS support for easy local network access.

### Web Dashboard
- Live hardware monitoring.
- Pump status visualization.
- Irrigation mode selection.
- Disease detection interface.
- Responsive user interface.


## Technologies Used

### Software
- Python
- Flask
- YOLOv8 (Ultralytics)
- Groq API
- OpenCV
- Pillow
- Zeroconf

### Hardware
- ESP32 Development Board
- DHT11 Temperature & Humidity Sensor
- Capacitive Soil Moisture Sensor
- Relay Module
- Mini Water Pump
- Power Supply / Battery

## 📂 Project Structure

```text
Tomato-Doctor/
│
├── app.py                 # Main Flask application
├── best.pt                # Trained YOLO disease detection model
├── requirements.txt       # Python dependencies
├── .env                   # API keys (not uploaded to GitHub)
├── .gitignore
├── README.md
│
├── templates/
│   └── index.html         # Web dashboard
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── uploads/               # Uploaded leaf images


## 📂 Screenshots
(1.png)
(2.png)
(3.png)


