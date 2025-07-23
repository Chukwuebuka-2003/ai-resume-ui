import streamlit as st
import requests

#
FASTAPI_URL = "https://ai-resume-api.vercel.app"

st.set_page_config(page_title="AI Resume Improver", layout="wide")

#  Helper Functions
def analyze_resume(file):
    """Sends resume to the FastAPI backend for analysis."""
    files = {'file': (file.name, file, file.type)}
    try:

        response = requests.post(f"{FASTAPI_URL}/upload-resume/", files=files)
        response.raise_for_status()  # Raises an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the backend: {e}")
        st.error(f"Backend response: {e.response.text if e.response else 'No response'}")
        return None

def generate_improved_resume(analysis_data):
    """Sends the analysis data to the backend to get the rewritten resume."""
    try:

        response = requests.post(f"{FASTAPI_URL}/generate-pdf/", json=analysis_data)
        response.raise_for_status()
        return response.text  # Returns the final HTML content
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the backend: {e}")
        st.error(f"Backend response: {e.response.text if e.response else 'No response'}")
        return None


st.title("✨ AI Resume Improver")
st.markdown("Upload your PDF resume, and let AI provide suggestions and rewrite it for you!")

# Session State Initialization
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'final_html' not in st.session_state:
    st.session_state.final_html = None

# Main App Flow
with st.sidebar:
    st.header("Controls")
    uploaded_file = st.file_uploader("Choose a resume PDF", type="pdf")

if uploaded_file:
    if st.sidebar.button("Analyze Resume", use_container_width=True):
        with st.spinner("AI is analyzing your resume... This may take a moment."):
            st.session_state.analysis = analyze_resume(uploaded_file)
            st.session_state.final_html = None

# Display Results
if st.session_state.analysis:
    st.header("Analysis Complete!")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("AI-Generated Suggestions")
        st.markdown(st.session_state.analysis['suggested_improvements'])

    with col2:
        st.subheader("Parsed Resume Data")
        st.json(st.session_state.analysis['original_resume'])

    st.divider()


    if st.button("🚀 Generate Improved Resume", use_container_width=True):
         with st.spinner("AI is rewriting your resume..."):
            st.session_state.final_html = generate_improved_resume(st.session_state.analysis)

if st.session_state.final_html:
    st.header("Your New & Improved Resume")

    st.download_button(
        label="Download Resume as HTML",
        data=st.session_state.final_html,
        file_name="improved_resume.html",
        mime="text/html",
        use_container_width=True
    )

    st.components.v1.html(st.session_state.final_html, height=800, scrolling=True)

else:
    st.info("Please upload your resume PDF and click 'Analyze Resume' to begin.")
