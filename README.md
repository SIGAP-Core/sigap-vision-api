# 🚗🤖 SIGAP Vision API

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![YOLOv8](https://img.shields.io/badge/AI-YOLOv8-blueviolet)](https://ultralytics.com/)
[![MQTT](https://img.shields.io/badge/MQTT-HiveMQ-00557E?logo=mqtt&logoColor=white)](https://www.hivemq.com/)

**SIGAP Vision API** - Backend service berbasis Python Flask yang bertugas sebagai "otak" pengenal kendaraan secara real-time menggunakan model **YOLOv8**.

Service ini merupakan bagian inti dari ekosistem **SIGAP (Sistem Integrasi Gerbang & Akses Pintar)** untuk validasi visual kendaraan.

---

## Fitur Utama

- **AI Vehicle Detection**: Klasifikasi untuk mobil, bus, dan truk menggunakan YOLOv8.
- **Real-time Status Broadcast**: Mengirim sinyal validasi ke Dashboard Next.js via MQTT (HiveMQ Cloud).
- **In-Memory Image Stream**: Mengirimkan preview gambar Base64 secara instan ke UI.
- **Asynchronous Data Pipeline**: Meneruskan log dan file gambar asli ke Next.js (Hadoop storage) via HTTP POST.
- **Automated Local Archival**: Backup otomatis setiap jepretan kamera ke penyimpanan lokal.

---

## 🛠️ Instalasi & Setup

1. Clone repositori ini.
2. Buat dan aktifkan virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔐 Konfigurasi API (.env)

Project ini membutuhkan kredensial broker MQTT dan endpoint Next.js agar sistem integrasi berjalan lancar.

1. Hubungi **Pemilik Proyek (Project Owner)** untuk meminta file konfigurasi `.env`.
2. Letakkan file `.env` tersebut di root direktori proyek.

> [!IMPORTANT]
> File `.env` tidak disertakan dalam repositori demi keamanan kredensial MQTT Cloud dan API Endpoint.

---

## 🚀 Menjalankan Service

```bash
python main.py
```

---

## 🏗️ Tech Stack

- **Language:** [Python 3.10+](https://www.python.org/)
- **Web Framework:** [Flask](https://flask.palletsprojects.com/) (API Gateway)
- **Computer Vision:** [YOLOv8 by Ultralytics](https://ultralytics.com/)
- **Messaging Protocol:** [MQTT](https://mqtt.org/) (via Paho-MQTT & HiveMQ Cloud)
- **Networking:** [Requests](https://requests.readthedocs.io/) (for Async Logging)

---

_Developed with 💡 by the SIGAP-Core Team._
