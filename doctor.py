# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Import required libraries
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

# Configure the Gemini API using the loaded API key
# Configure Gemini API key
GEMINI_API_KEY = "" 
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model and chat object
# model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Function to prepare image data for Gemini API
def prepare_image_data(uploaded_file):
    """
    Convert uploaded image file into the format required by the Gemini API.
    """
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded. Please upload an image.")

# Function to generate analysis from Gemini Vision API
def analyze_food_image(prompt_text, image_data):
    """
    Send the image and prompt to the Gemini model and return the response.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([prompt_text, image_data[0], prompt_text])
    return response.text

# -------------------- Streamlit App UI --------------------

# Set Streamlit page configuration
st.set_page_config(page_title="Gemini Health Analyzer", layout="centered")

# App Header
st.title("🥗 Gemini Health Analyzer")
st.write("Upload a food image and get a health breakdown with nutritional insights.")

# File uploader for food image
uploaded_image = st.file_uploader("📤 Upload an image of your meal", type=["jpg", "jpeg", "png"])

# Display the uploaded image
if uploaded_image is not None:
    image_display = Image.open(uploaded_image)
    st.image(image_display, caption="Uploaded Meal Image", use_container_width=True)

# Prompt for Gemini to analyze the meal image
health_analysis_prompt = """
You are a nutrition expert. Analyze the food items in this image and provide:
1. Name of each food item
2. Estimated calorie count
3. Macronutrient breakdown (carbs, proteins, fats)
4. Health rating (Healthy / Unhealthy / Moderate)
5. If unhealthy, explain why and suggest a healthier alternative.
6. Summary: Should this meal be part of a healthy diet? What to add or remove?
"""

# Submit button to trigger analysis
if st.button("🔍 Analyze Meal"):
    try:
        with st.spinner("Analyzing your image..."):
            image_data = prepare_image_data(uploaded_image)
            analysis_result = analyze_food_image(health_analysis_prompt, image_data)
            st.success("✅ Analysis Complete")
            st.markdown(analysis_result)
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")