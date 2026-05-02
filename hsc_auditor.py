import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import fitz  # pymupdf

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Smart HSC Audit Automator", page_icon="🦺", layout="centered")
st.title("🦺 Smart HSC Audit Automator")
st.caption("Upload a site inspection report (text, PDF or image) to automatically flag safety violations based on HSE protocols.")

# ── API Key input ─────────────────────────────────────────────────────────────
api_key = st.text_input("Enter your Gemini API Key:", type="password", placeholder="AIza...")

# ── File upload ───────────────────────────────────────────────────────────────
st.subheader("📁 Upload Inspection Report")
upload_type = st.radio("Choose input type:", ["Text / PDF File", "Image (photo of report)"])

uploaded_file = st.file_uploader(
    "Upload your file here",
    type=["txt", "pdf"] if upload_type == "Text / PDF File" else ["png", "jpg", "jpeg"]
)

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a certified Health, Safety and Environment (HSE) compliance expert 
with deep knowledge of ISO 45001 occupational health and safety standards and international 
fire safety codes.

Your job is to carefully analyse site inspection notes or images and:
1. Identify any breaches of ISO 45001 or standard fire safety codes
2. Categorise each violation by severity (Critical, Major, Minor)
3. Reference the specific ISO 45001 clause or fire safety code that is breached
4. Suggest a corrective action for each violation
5. Provide an overall site safety rating (Unsafe / Needs Improvement / Satisfactory)

Format your response as a clear Safety Alert Summary with sections:
- 🔴 Critical Violations
- 🟠 Major Violations  
- 🟡 Minor Violations
- ✅ Corrective Actions
- 📊 Overall Site Safety Rating
"""

# ── Analyse button ────────────────────────────────────────────────────────────
if st.button("🔍 Analyse Report", use_container_width=True):

    if not api_key:
        st.error("Please enter your Gemini API key.")

    elif not uploaded_file:
        st.error("Please upload a file to analyse.")

    else:
        with st.spinner("Analysing report for HSE violations..."):
            try:
                # Configure Gemini
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=SYSTEM_PROMPT
                )

                # ── Handle TEXT or PDF file ───────────────────────────────────
                if upload_type == "Text / PDF File":
                    if uploaded_file.name.endswith(".pdf"):
                        pdf_bytes = uploaded_file.read()
                        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
                        report_text = ""
                        for page in pdf_document:
                            report_text += page.get_text()
                        pdf_document.close()

                        if not report_text.strip():
                            st.error("Could not extract text from this PDF. It may be a scanned image — try uploading it as an image instead.")
                            st.stop()
                    else:
                        report_text = uploaded_file.read().decode("utf-8")

                    response = model.generate_content(
                        f"Please analyse this site inspection report and flag any safety violations:\n\n{report_text}"
                    )
                    result = response.text

                # ── Handle IMAGE file ─────────────────────────────────────────
                else:
                    image = Image.open(uploaded_file)
                    response = model.generate_content([
                        "Please analyse this site inspection photo and flag any safety violations based on ISO 45001 and fire safety codes.",
                        image
                    ])
                    result = response.text

                # ── Display result ────────────────────────────────────────────
                st.subheader("📋 Safety Alert Summary")
                st.markdown(result)

                # ── Download button ───────────────────────────────────────────
                st.download_button(
                    label="📥 Download Safety Alert Summary",
                    data=result,
                    file_name="safety_alert_summary.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"Something went wrong: {e}")