from dotenv import load_dotenv

load_dotenv()
import base64
import streamlit as st
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai

#genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

def get_gemini_response(input,pdf_cotent,prompt):
    model=genai.GenerativeModel('gemini-pro-vision')
    response=model.generate_content([input,pdf_content[0],prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        ## Convert the PDF to image
        images=pdf2image.convert_from_bytes(uploaded_file.read())

        first_page=images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

## Streamlit App

st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")
input_text=st.text_area("Job Description: ",key="input")
uploaded_files=st.file_uploader("Upload resumes(PDF)...",type=["pdf"], accept_multiple_files=True)


if uploaded_files is not None:
    st.write(f"{len(uploaded_files)} PDF(s) Uploaded Successfully")



submit1 = st.button("Resume matched")

input_prompt1 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume for the provided job description. Give me the percentage of match if the resume matches
the job description. First the output should come as the matching percentage and then missing keywords and 1 line last final thought.
"""

if submit1:
    if uploaded_files is not None:
        resume=dict()
        for file in uploaded_files:
            st.subheader(file)
            pdf_content=input_pdf_setup(file)
            response=get_gemini_response(input_prompt1,pdf_content,input_text)
            resume[file]=response
        
        for key,value in resume.items:
            st.subheader("Details for resume "+key)
            st.write(value)
    else:
        st.write("Please uplaod the resume")

