import streamlit as st
import PyPDF2
import os
from groq import Groq
import tempfile

# Initialize Groq client
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_text_from_pdf(pdf_file):
    text = ""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(pdf_file.getvalue())
        temp_file_path = temp_file.name
    
    with open(temp_file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    
    os.unlink(temp_file_path)
    return text

def analyze_resume(resume_text, job_description):
    prompt = f"""
    Analyze the following resume against the job description and provide:
    1. Key strengths that match the job requirements
    2. Areas of weakness or gaps
    3. Specific suggestions for improvement to increase chances of selection
    
    Resume:
    {resume_text}
    
    Job Description:
    {job_description}
    """
    
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an expert resume analyzer and career coach."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        # Update this line in your code
        model="llama-3.3-70b-versatile",  # This is a production-ready model,
        temperature=0.7,
        max_tokens=2000,
    )
    
    return completion.choices[0].message.content

# Streamlit UI
st.title("Resume Analysis Tool")
st.write("Upload your resume and paste the job description to get personalized analysis")

# File uploader
uploaded_file = st.file_uploader("Upload your resume (PDF)", type=['pdf'])

# Job description input
job_description = st.text_area("Paste the job description here", height=200)

# Submit button
if st.button("Analyze Resume"):
    if uploaded_file is not None and job_description:
        with st.spinner("Analyzing your resume..."):
            # Extract text from PDF
            resume_text = extract_text_from_pdf(uploaded_file)
            
            # Get analysis
            analysis = analyze_resume(resume_text, job_description)
            
            # Display results
            st.subheader("Analysis Results")
            st.write(analysis)
    else:
        st.error("Please upload a resume and provide a job description")
