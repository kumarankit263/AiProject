# Import necessary libraries
import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv

# Load environment variables from .env file (for API key)
load_dotenv()

# Configure the Gemini API with your key
GEMINI_API_KEY = "" 
genai.configure(api_key=GEMINI_API_KEY)

# Function to extract text from the uploaded PDF resume
def extract_text_from_pdf(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to get a response from Gemini using a given prompt
def get_gemini_response(prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

# Streamlit App UI
st.title("🔍 Smart ATS Resume Evaluator")
st.text("Upload your resume and compare it against a job description to improve your ATS score.")

# Input: Job Description
jd = st.text_area("📄 Paste the Job Description")

# Input: Resume File Upload (PDF only)
uploaded_file = st.file_uploader("📎 Upload Your Resume (PDF)", type="pdf", help="Only PDF files are supported.")

# Button to trigger analysis
if st.button("Submit"):
    if uploaded_file is not None and jd.strip() != "":
        # Extract resume text
        resume_text = extract_text_from_pdf(uploaded_file)

        # Prepare the prompt for Gemini
        prompt = f"""
        Hey, act like a skilled and experienced ATS (Application Tracking System)
        with expertise in tech fields such as Software Engineering, Data Science, 
        Data Analysis, and Big Data Engineering. Evaluate the following resume 
        against the provided job description. The job market is very competitive, 
        so provide high-quality feedback for improvement. Include:
        - Percentage match
        - Missing important keywords
        - Short profile summary

        Format your response as a single JSON string:
        {{
          "JD Match": "%",
          "MissingKeywords": [],
          "Profile Summary": ""
        }}

        resume: {resume_text}
        description: {jd}
        """

        # Get response from Gemini
        response = get_gemini_response(prompt)

        # Display the result
        st.subheader("📊 ATS Evaluation Result")
        st.code(response, language="json")
    else:
        st.warning("Please upload a PDF resume and paste a job description.")