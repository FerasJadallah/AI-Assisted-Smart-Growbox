# 🌿 AI-Assisted Smart GrowBox

An AI-powered IoT system that automates plant monitoring and care using **Streamlit**, **ESP32**, and pre-trained AI models. The system optimizes plant health by detecting plant species and identifying early signs of plant diseases through sensor data and image classification.

---

## 🚀 Features

- 🌡️ Monitors real-time environmental factors like **soil moisture** and **temperature** using sensors connected to an **ESP32 microcontroller**.
- 📷 Uses **pre-trained AI models** for:
  - Plant Species Classification
  - Disease Detection
- 🧠 Integrates models into a **Streamlit web interface** for intuitive, real-time interaction.
- 📡 Sends data between hardware and web via serial communication.
- 🌱 Ideal for smart agriculture, home gardening, and agricultural research.

---

## 🧠 AI Models Used

This project uses **two pre-trained models** for image classification tasks:

### 1. Plant Species Detection

- **Source:** HuggingFace Model Hub  
- **Model Page:** [foduucom/plant-leaf-detection-and-classification](https://huggingface.co/foduucom/plant-leaf-detection-and-classification)
- **Format:** `best.pt`, `yolov8n.pt`
- **Note:** This model identifies different plant species from leaf images.

### 2. Plant Disease Detection (YOLOv8)

- **Source:** Google Drive  
- **Download Link:** [Click here](https://drive.google.com/drive/folders/1wGNFhdjxl7J1rljxicbArto9Z9AJT8WA)
- **Files Included:** `.h5` and `.keras` 
- **Note:** YOLOv8 model trained to detect leaf diseases from plant images.

> ⚠️ **Important:** These models are not included in the GitHub repository due to size limits.  
> You must download and add them manually to the project directory.

---

## 📦 Installation & Setup

### 1. Clone the Repo

```bash
git clone https://github.com/FerasJadallah/AI-Assisted-Smart-Growbox.git
cd AI-Assisted-Smart-Growbox
```

### 2. Set Up Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download and Add Pretrained Models

- From [HuggingFace](https://huggingface.co/foduucom/plant-leaf-detection-and-classification):
  - Add `trained_model.h5` and `trained_model.keras` inside `Plant Predection/`
- From [Google Drive](https://drive.google.com/drive/folders/1wGNFhdjxl7J1rljxicbArto9Z9AJT8WA):
  - Add `best.pt` and/or `yolov8n.pt` inside `DiseaseDetection/`

> Make sure these folders and files exist exactly as listed.

### 5. Run the Streamlit App

```bash
streamlit run main.py
```

---

## 🔌 ESP32 Setup

1. Open `ESP32logic.ino` in Arduino IDE.
2. Install required libraries:
   - `DHT`
3. Upload the code to your ESP32 board.
4. Connect sensors (e.g., DHT11/22, soil moisture sensors).
5. Connect via Serial to Streamlit app.

---


## 🤝 Acknowledgements

- [foduucom/plant-leaf-detection-and-classification](https://huggingface.co/foduucom/plant-leaf-detection-and-classification)
- YOLOv8 model provided via [Google Drive link](https://drive.google.com/drive/folders/1wGNFhdjxl7J1rljxicbArto9Z9AJT8WA)
- Streamlit, ESP32, and open-source ML communities


## 📜 License

This project is for educational and demonstration purposes. For any commercial use of the models, please refer to their original licensing terms on HuggingFace and Google Drive.
