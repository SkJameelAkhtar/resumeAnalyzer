import streamlit as st
import PyPDF2
import io
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📃", layout="centered")

st.markdown("""
<style>
/* Target the main block container */
.st-emotion-cache-1y4p8pa {
    width: 90%;
    margin: auto;
}
/* Target the analysis results markdown */
.analysis-results {
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)


st.title("AI Resume Critiquer")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")

# Configure the Google Generative AI client
try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        st.error("GOOGLE_API_KEY not found. Please set it in your .env file.")
        st.stop()
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"Error configuring Google AI: {e}")
    st.stop()

uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
job_role = st.text_input("Enter the job role you're targeting (optional)")

analyze = st.button("Analyze Resume")

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None

def extract_text_from_file(uploaded_file):
    """Extracts text from the uploaded file."""
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    elif uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")
    return None

if analyze and uploaded_file:
    with st.spinner("Analyzing your resume..."):
        try:
            file_content = extract_text_from_file(uploaded_file)

            if not file_content or not file_content.strip():
                st.error("File does not have any content or could not be read.")
                st.stop()

            model = genai.GenerativeModel('gemini-1.5-flash')

            prompt = f"""Please analyze this resume and provide constructive feedback.
            Focus on the following aspects:
            1.  Content clarity and impact
            2.  Skills presentation
            3.  Experience descriptions
            4.  Specific improvements for {job_role if job_role else 'general job applications'}

            Resume content:
            {file_content}

            Please provide your analysis in a clear, structured format with specific recommendations."""

            response = model.generate_content(prompt)

            st.markdown("### Analysis Results")
            # --- Apply custom class for larger font ---
            st.markdown(f'<div class="analysis-results">{response.text}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")