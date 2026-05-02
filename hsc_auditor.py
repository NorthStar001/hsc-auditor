import streamlit as st
import google.generativeai as genai
from PIL import Image
import fitz  # pymupdf

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart HSC Audit Automator",
    page_icon="🦺",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.header-banner {
    background: linear-gradient(135deg, #00A86B, #006B44);
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 2rem;
}
.header-banner h1 { color: white; font-size: 2.2rem; margin: 0; }
.header-banner p { color: #d0f0e0; font-size: 1rem; margin-top: 0.5rem; }
.info-card {
    background-color: #1E2130;
    border-left: 4px solid #00A86B;
    border-radius: 8px;
    padding: 1rem 1.5rem;
    margin-bottom: 1rem;
}
.result-box {
    background-color: #1E2130;
    border: 1px solid #00A86B;
    border-radius: 10px;
    padding: 1.5rem;
    margin-top: 1rem;
}
div.stButton > button {
    background-color: #00A86B;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 2rem;
    font-size: 1rem;
    font-weight: bold;
    width: 100%;
}
div.stButton > button:hover { background-color: #006B44; color: white; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
    <h1>🦺 Smart HSC Audit Automator</h1>
    <p>AI-powered site inspection analysis based on ISO 45001 & Fire Safety Codes</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")
    st.markdown("---")

    api_key = st.text_input(
        "🔑 Gemini API Key",
        type="password",
        placeholder="AIza...",
        help="Get your free key at aistudio.google.com"
    )

    st.markdown("---")
    st.markdown("### 📌 How to use")
    st.markdown("""
1. Enter your Gemini API key
2. Choose your file type
3. Upload your report
4. Click **Analyse Report**
5. Download your summary
    """)

    st.markdown("---")
    st.markdown("### 🔍 What it checks")
    st.markdown("""
- ✅ ISO 45001 compliance
- ✅ Fire safety codes
- ✅ Severity classification
- ✅ Corrective actions
    """)

    st.markdown("---")
    st.caption("Built with Streamlit & Gemini AI")

# ── Main layout ───────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📁 Upload Inspection Report")

    upload_type = st.radio(
        "Choose input type:",
        ["Text / PDF File", "Image (photo of report)"],
        horizontal=True
    )

    uploaded_file = st.file_uploader(
        "Drop your file here",
        type=["txt", "pdf"] if upload_type == "Text / PDF File" else ["png", "jpg", "jpeg"]
    )

    if uploaded_file:
        st.success(f"📄 **{uploaded_file.name}** uploaded successfully ({round(uploaded_file.size / 1024, 2)} KB)")

    analyse = st.button("🔍 Analyse Report")

with col2:
    st.markdown("### 📊 Severity Guide")
    st.markdown("""
- 🔴 **Critical** — Immediate risk to life or safety
- 🟠 **Major** — Significant breach requiring urgent action
- 🟡 **Minor** — Low risk but must be addressed
- ✅ **Corrective Actions** — Steps to fix each violation
- 📊 **Safety Rating** — Overall site assessment
    """)

    st.markdown("### 📋 Supported Standards")
    st.markdown("""
- 🏗️ **ISO 45001** — Occupational Health & Safety
- 🔥 **Fire Safety Codes** — International standards
- ⚠️ **HSE Protocols** — Health & Safety Executive guidelines
    """)

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

# ── Analysis ──────────────────────────────────────────────────────────────────
if analyse:
    if not api_key:
        st.error("⚠️ Please enter your Gemini API key in the sidebar.")
    elif not uploaded_file:
        st.error("⚠️ Please upload a file to analyse.")
    else:
        with st.spinner("🔍 Scanning report for HSE violations..."):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name="gemini-2.0-flash",
                    system_instruction=SYSTEM_PROMPT
                )

                if upload_type == "Text / PDF File":
                    if uploaded_file.name.endswith(".pdf"):
                        pdf_bytes = uploaded_file.read()
                        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
                        report_text = ""
                        for page in pdf_document:
                            report_text += page.get_text()
                        pdf_document.close()

                        if not report_text.strip():
                            st.error("Could not extract text from this PDF. Try uploading it as an image instead.")
                            st.stop()
                    else:
                        report_text = uploaded_file.read().decode("utf-8")

                    response = model.generate_content(
                        f"Please analyse this site inspection report and flag any safety violations:\n\n{report_text}"
                    )

                else:
                    image = Image.open(uploaded_file)
                    response = model.generate_content([
                        "Please analyse this site inspection photo and flag any safety violations based on ISO 45001 and fire safety codes.",
                        image
                    ])

                result = response.text

                st.markdown("---")
                st.markdown("## 📋 Safety Alert Summary")
                st.markdown(result)

                st.download_button(
                    label="📥 Download Safety Alert Summary",
                    data=result,
                    file_name="safety_alert_summary.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"Something went wrong: {e}")