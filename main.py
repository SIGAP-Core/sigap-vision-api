import os
import ssl
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from ultralytics import YOLO
import paho.mqtt.client as mqtt
import json
from dotenv import load_dotenv
import base64

load_dotenv()

app = Flask(__name__)

# --- KONFIGURASI MQTT .ENV ---
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
TOPIC_UI_STATE = os.getenv("TOPIC_UI_STATE")

# URL NEXT JS (Later)
NEXTJS_API_URL = os.getenv("NEXTJS_API_URL")

# --- SETUP MQTT CLIENT ---
# Menggunakan CallbackAPIVersion.VERSION2 sesuai standar terbaru paho-mqtt
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Python_AI_Backend")
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE) # Bypass SSL check agar praktis
mqtt_client.tls_insecure_set(True)

print("🔄 Menghubungkan Python ke HiveMQ Cloud...")
try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start() # Menjalankan MQTT di background
    print("✅ Python terhubung ke Broker VIP!")
except Exception as e:
    print(f"❌ Gagal terhubung ke MQTT: {e}")

# --- INISIALISASI MODEL AI ---
print("⏳ Memuat model YOLOv8n (Nano)...")
model = YOLO('yolov8n.pt') 
print("✅ Model YOLO siap!")

SAVE_DIR = "./potret_mobil"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "Key 'image' tidak ditemukan"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "File kosong"}), 400
    
    def get_base64_image(image_path):
        with open(image_path, "rb") as img_file:
            # Kita ambil gambarnya, di-encode ke base64
            return base64.b64encode(img_file.read()).decode('utf-8')

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"kamera_parkir_{timestamp}.jpg"
    filepath = os.path.join(SAVE_DIR, filename)

    # 1. Simpan file gambar
    file.save(filepath)
    print(f"\n📸 [GAMBAR DITERIMA] Disimpan di: {filepath}")
    
    # Ambil base64
    image_base64 = get_base64_image(filepath)
    
    # 2. Proses Gambar dengan YOLOv8
    print("🧠 Menganalisis gambar dengan AI...")
    results = model(filepath)
    mobil_terdeteksi = False
    jumlah_mobil = 0
    confidence_score = 0.0
    
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            # Class ID 2 = car, 5 = bus, 7 = truck
            if cls_id in [2, 5, 7]: 
                mobil_terdeteksi = True
                jumlah_mobil += 1
                # Mengambil tingkat kepercayaan AI (confidence)
                conf = float(box.conf[0])
                if conf > confidence_score:
                    confidence_score = conf

    # 3. Keputusan AI & Broadcast (MQTT & HTTP)
    if mobil_terdeteksi:
        print(f"✅ [VALIDASI AI] Benar, ada {jumlah_mobil} kendaraan terdeteksi (Conf: {confidence_score:.2f})!")
        status_ai = "Kendaraan Valid"
        mqtt_status = "MOBIL_VALID"
    else:
        print("❌ [VALIDASI AI] Tidak ada kendaraan di dalam foto.")
        status_ai = "Bukan Kendaraan"
        mqtt_status = "MOBIL_TIDAK_VALID"
        # Walaupun 0, kita tetap kirim confidence score tertinggi (biasanya objek random) untuk log analisis
        
    # --- JALUR CEPAT: PYTHON BERTERIAK KE UI NEXT.JS VIA MQTT ---
    # (Update UI Dashboard Admin: Buka blur jika valid, tampilkan error jika tidak valid)
    print(f"📢 Mengirim status '{mqtt_status}' ke UI via MQTT...")
    payload_mqtt = {
        "status": mqtt_status,
        "vehicle_count": jumlah_mobil,
        "confidence": f"{int(confidence_score * 100)}%",
        "image_base64": f"data:image/jpeg;base64,{image_base64}"
    }
    mqtt_client.publish(TOPIC_UI_STATE, json.dumps(payload_mqtt))

    # --- JALUR KARGO: KIRIM DATA KE NEXT.JS VIA HTTP ---
    # (SELALU KIRIM gambar ke Next.js agar disimpan di Hadoop dan ditampilkan di layar Admin)
    # NOTE: Bagian ini bisa di-uncomment jika API Next.js sudah jadi
    if NEXTJS_API_URL:
        print(f"🚚 Mengirim log gambar ({status_ai}) ke Next.js...")
        try:
            data_meta = {
                "status_ai": status_ai,
                "vehicle_count": jumlah_mobil,
                "timestamp": timestamp,
                "confidence": f"{int(confidence_score * 100)}%"
            }
            # Membuka ulang file untuk dikirim via form-data HTTP
            with open(filepath, 'rb') as img_file:
                files = {'file_gambar':(filename, img_file, 'image/jpeg')}
                response = requests.post(NEXTJS_API_URL, data=data_meta, files=files)
                print(f"✅ Data log sukses terkirim ke Next.js (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ Gagal mengirim ke Next.js: {e}")


    return jsonify({
        "message": "Gambar diproses AI", 
        "filename": filename,
        "ai_status": status_ai,
        "vehicle_count": jumlah_mobil,
        "confidence": f"{int(confidence_score * 100)}%"
    }), 200

if __name__ == '__main__':
    print("🚀 Flask Server AI berjalan! Menunggu trigger dari IoT...")
    app.run(host='0.0.0.0', port=5000, debug=True)