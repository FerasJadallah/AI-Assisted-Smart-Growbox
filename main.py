import streamlit as st
from streamlit_autorefresh import st_autorefresh
from ultralytics import YOLO
import tensorflow as tf
import numpy as np
from PIL import Image
import requests
import json


# Paths to models and logo
# Replace with your actual paths
yolo_model_path = "/Users/ferasjadallah/Desktop/SMGB/Smart GrowBox AI Model/Plant Predection/best.pt"
cnn_model_path = "/Users/ferasjadallah/Desktop/SMGB/Smart GrowBox AI Model/DiseaseDetection/trained_model.h5"
logo_path = "/Users/ferasjadallah/Desktop/SMGB/Smart GrowBox AI Model/ArtificialAlliance.jpeg"

# ESP32 IP address
# Replace with your actual ESP32 IP address esp32_ip = "http://
esp32_ip = "http://"

# Load models
yolo_model = YOLO(yolo_model_path)
cnn_model = tf.keras.models.load_model(cnn_model_path)

# Class labels for disease detection
class_labels = ['Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
                'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew',
                'Cherry_(including_sour)___healthy', 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
                'Corn_(maize)___Common_rust_', 'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy',
                'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
                'Grape___healthy', 'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot',
                'Peach___healthy', 'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy',
                'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy',
                'Soybean___healthy', 'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy',
                'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold',
                'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite',
                'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus',
                'Tomato___healthy']

# Sample plant growing condition data
# This data should ideally be fetched from a database or a more structured source
# but for simplicity, we are using a dictionary here.
# Sample plant growing condition (Temperature) data
plant_conditions = {
    "ginger": {"temperature": 22.5},
    "banana": {"temperature": 25},
    "tobacco": {"temperature": 25},
    "rose": {"temperature": 22.5},
    "soyabean": {"temperature": 25},
    "papaya": {"temperature": 27},
    "garlic": {"temperature": 7},
    "raspberry": {"temperature": 20},
    "mango": {"temperature": 25},
    "cotton": {"temperature": 25},
    "corn": {"temperature": 29},
    "pomegranate": {"temperature": 30.5},
    "strawberry": {"temperature": 18},
    "blueberry": {"temperature": 20},
    "brinjal": {"temperature": 25.5},
    "wheat": {"temperature": 18.5},
    "olive": {"temperature": 20},
    "rice": {"temperature": 27.5},
    "lemon": {"temperature": 25},
    "cabbage": {"temperature": 17.5},
    "guava": {"temperature": 25.5},
    "chilli": {"temperature": 25},
    "capsicum": {"temperature": 21.5},
    "sunflower": {"temperature": 22.5},
    "cherry": {"temperature": 20},
    "cassava": {"temperature": 27},
    "tea": {"temperature": 24},
    "sugarcane": {"temperature": 25},
    "groundnut": {"temperature": 27.5},
    "weed": {"temperature": 20},
    "peach": {"temperature": 25},
    "coffee": {"temperature": 21},
    "cauliflower": {"temperature": 17.5},
    "onion": {"temperature": 18.5},
    "gram": {"temperature": 22.5},
    "chiku": {"temperature": 27.5},
    "jamun": {"temperature": 25},
    "castor": {"temperature": 25},
    "pea": {"temperature": 15.5},
    "cucumber": {"temperature": 21},
    "grape": {"temperature": 22.5},
    "cardamom": {"temperature": 22.5},
    "tomato": {"temperature": 22},
    "potato": {"temperature": 18},
    "apple": {"temperature": 8}
}

# Prediction functions 
# Using YOLO for plant recognition
def predict_with_yolo(image_file):
    image = Image.open(image_file)
    image_np = np.array(image)
    results = yolo_model.predict(source=image_np, save=False)
    return results

# Using CNN for disease detection
def predict_with_cnn(image_file):
    image = tf.keras.preprocessing.image.load_img(image_file, target_size=(128, 128))
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])
    predictions = cnn_model.predict(input_arr)
    return np.argmax(predictions)

# Sensor Data
def fetch_sensor_data():
    try:
        response = requests.get(esp32_ip, timeout=10)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return f"Failed with status code: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

# Send conditions to ESP32
def send_conditions_to_esp32(plant_name):
    print("Sendings")
    if plant_name in plant_conditions:
        try:
            temperature = plant_conditions[plant_name]["temperature"]
            payload = json.dumps({"unit": 1, "temperature": temperature})
            headers = {'Content-Type': 'application/json'}

            print(f"Sending to ESP32: {payload}")  # Debug line

            response = requests.post(f"{esp32_ip}/assign", data=payload, headers=headers, timeout=10)
            print(f"ESP32 Response: {response.status_code}, {response.text}")  # Debug line
            print(response)
            if response.status_code == 200:
                return True, f"Temperature ({temperature}°C) sent to ESP32 successfully."
            else:
                return False, f"Failed to send temperature. Status code: {response.status_code}, Message: {response.text}"
        except Exception as e:
            print(f"Exception during request: {e}")  # Debug line
            return False, f"Error: {e}"
    return False, "Unknown plant"

# UI
st.sidebar.title("Dashboard")
app_mode = st.sidebar.selectbox("Select Page", ["Home", "Plant Recognition", "Disease Detection", "Sensor Monitor"])

if app_mode == "Home":
    st.header("AI Assisted Smart GrowBox")
    st.image(logo_path, use_container_width=True)
    st.markdown("""
    Welcome to our Plant Disease & Recognition System! 🌿🔍

    Our mission is to help identify plant species and diseases efficiently.

    - Accurate Detection
    - Fast Predictions
    - Easy-to-Use Interface

    👉 Try out **Plant Recognition** or **Disease Detection**
    """)

elif app_mode == "Plant Recognition":
    st.header("Plant Recognition")
    test_image = st.file_uploader("Upload Plant Image", type=["jpg", "jpeg", "png"])

    if test_image is not None:
        st.image(test_image, caption="Uploaded Image", use_container_width=True)

        if st.button("Detect Plant"):
            st.info("Processing with YOLO...")
            results = predict_with_yolo(test_image)
            for result in results:
                result_image = result.plot()
                st.image(result_image, caption="Detection Result", use_container_width=True)
                for box in result.boxes:
                    class_id = box.cls.item()
                    class_name = yolo_model.names[class_id]
                    confidence = box.conf.item()
                    st.write(f"Sending: {class_name}")
                    print("Sendings")
                    st.success(f"Detected Plant: **{class_name}** (Confidence: {confidence:.2f})")

                    if class_name in plant_conditions:
                        st.info("Suggested Growing Conditions:")
                        st.write(f"Sending: {class_name}")

                        st.json(plant_conditions[class_name])
                        print(class_name)

                        success, message = send_conditions_to_esp32(class_name)
                        if success:
                                st.success(message)
                        else:
                                st.error(message)
                    else:
                        st.warning("No growing condition data found for this plant.")

elif app_mode == "Disease Detection":
    st.header("Disease Detection")
    test_image = st.file_uploader("Upload Leaf Image", type=["jpg", "jpeg", "png"])

    if test_image is not None:
        st.image(test_image, caption="Uploaded Image", use_container_width=True)

        if st.button("Detect Disease"):
            result_index = predict_with_cnn(test_image)
            st.success(f"Detected: **{class_labels[result_index]}**")

elif app_mode == "Sensor Monitor":
    st.header("🌡️ Real-Time Sensor Monitor")
    st_autorefresh(interval=5000, key="sensor_refresh")
    sensor_data = fetch_sensor_data()

    if "Error" in sensor_data:
        st.error(sensor_data)
    else:
        st.success("Sensor data received:")
        st.code(sensor_data)

