import streamlit as st
import PyPDF2
import pandas as pd
import os
from dotenv import load_dotenv
from langchain_community.llms import OpenAI  # Updated
from langchain_openai import ChatOpenAI  # Updated
from langchain.schema import HumanMessage, SystemMessage  # This might still work, but could need updating

# Load environment variables from .env file
load_dotenv()

# Set page configuration
st.set_page_config(page_title="Due Diligence Assistant", layout="wide")

# Styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .highlight {
        background-color: #e3f2fd;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .report-section {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
    }
    .verified {
        color: green;
        font-weight: bold;
    }
    .unverified {
        color: red;
        font-weight: bold;
    }
    .neutral {
        color: orange;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("Investment Due Diligence Assistant")
st.markdown("### Verify pitch deck claims against financial data")

# API Key setup - check environment first, then fallback to UI input
api_key = os.getenv("OPENAI_API_KEY")  # Try to get from environment first
if not api_key:  # If not found in environment, ask user
    api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
    if api_key:  # Only set if user provided one
        os.environ["OPENAI_API_KEY"] = api_key

if not api_key:
    st.warning("Please enter your OpenAI API Key to proceed or set it in your .env file.")
    st.stop()

# Initialize state
if 'claims_extracted' not in st.session_state:
    st.session_state.claims_extracted = False
if 'verification_done' not in st.session_state:
    st.session_state.verification_done = False
if 'claims' not in st.session_state:
    st.session_state.claims = []
if 'verifications' not in st.session_state:
    st.session_state.verifications = {}

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Function to extract financial data from spreadsheet
def extract_financials(financial_file):
    try:
        df = pd.read_csv(financial_file)
        return df.to_string()
    except:
        try:
            df = pd.read_excel(financial_file)
            return df.to_string()
        except:
            return "Could not parse financial data file format."

# Function to extract claims from pitch deck
def extract_claims(pitch_deck_text):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    system_prompt = """
    You are a due diligence expert analyzing investment pitch decks.
    Extract the top 5-7 key financial and business claims made in the pitch deck text.
    Focus on claims that could be verified against financial data, such as:
    - Revenue or growth numbers
    - Market size claims
    - Customer or user metrics
    - Unit economics
    - Projections or forecasts
    
    Format each claim as a separate item in a list. Be specific and quote numbers where available.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Here is the pitch deck text to analyze:\n\n{pitch_deck_text}")
    ]
    
    response = llm(messages)
    claims = response.content.strip().split("\n")
    
    # Clean up the claims to remove list markers
    cleaned_claims = []
    for claim in claims:
        if claim.strip():
            # Remove list markers like "1.", "•", "-", etc.
            clean_claim = claim.strip()
            if clean_claim[0].isdigit() and clean_claim[1:3] in ['. ', '- ', ') ']:
                clean_claim = clean_claim[3:].strip()
            elif clean_claim[0] in ['-', '•', '*', '–']:
                clean_claim = clean_claim[1:].strip()
            cleaned_claims.append(clean_claim)
    
    return cleaned_claims

# Function to verify claims against financial data
def verify_claims(claims, financial_data):
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    verifications = {}
    
    for claim in claims:
        system_prompt = """
        You are a financial due diligence expert. Your task is to verify if the given claim is supported by the financial data provided.
        
        Provide your analysis in the following format:
        - VERIFICATION STATUS: [VERIFIED/NOT VERIFIED/PARTIALLY VERIFIED]
        - REASONING: [Your detailed reasoning with specific references to the financial data]
        - RECOMMENDATION: [What the investor should do regarding this claim]
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"CLAIM: {claim}\n\nFINANCIAL DATA:\n{financial_data}")
        ]
        
        response = llm(messages)
        verifications[claim] = response.content
    
    return verifications

# File upload section
st.header("Upload Documents")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Pitch Deck (PDF)")
    pitch_deck_file = st.file_uploader("Upload the pitch deck", type=["pdf"])

with col2:
    st.markdown("### Financial Data")
    financial_file = st.file_uploader("Upload financial data", type=["csv", "xlsx", "xls"])

# Process documents when both are uploaded
if pitch_deck_file and financial_file and not st.session_state.claims_extracted:
    with st.spinner("Extracting claims from pitch deck..."):
        # Extract text from pitch deck
        pitch_deck_text = extract_text_from_pdf(pitch_deck_file)
        
        # Extract claims
        st.session_state.claims = extract_claims(pitch_deck_text)
        st.session_state.claims_extracted = True
        
        # Extract financial data
        st.session_state.financial_data = extract_financials(financial_file)

# Display extracted claims and allow verification
if st.session_state.claims_extracted and not st.session_state.verification_done:
    st.header("Extracted Claims")
    
    claims_to_verify = []
    for i, claim in enumerate(st.session_state.claims):
        selected = st.checkbox(f"{claim}", key=f"claim_{i}", value=True)
        if selected:
            claims_to_verify.append(claim)
    
    if st.button("Verify Selected Claims") and claims_to_verify:
        with st.spinner("Verifying claims against financial data..."):
            st.session_state.verifications = verify_claims(claims_to_verify, st.session_state.financial_data)
            st.session_state.verification_done = True
            st.experimental_rerun()

# Display verification results
if st.session_state.verification_done:
    st.header("Verification Results")
    
    for claim, verification in st.session_state.verifications.items():
        with st.expander(f"Claim: {claim}", expanded=True):
            st.markdown(f"<div class='report-section'>{verification}</div>", unsafe_allow_html=True)
    
    # Summary section
    st.header("Summary Report")
    
    verified_count = sum(1 for v in st.session_state.verifications.values() if "VERIFIED" in v.upper())
    partial_count = sum(1 for v in st.session_state.verifications.values() if "PARTIALLY VERIFIED" in v.upper())
    not_verified_count = sum(1 for v in st.session_state.verifications.values() if "NOT VERIFIED" in v.upper())
    
    total = len(st.session_state.verifications)
    
    st.markdown(f"""
    <div class='highlight'>
        <h3>Verification Summary</h3>
        <p><span class='verified'>✓ Verified claims:</span> {verified_count}/{total} ({int(verified_count/total*100) if total > 0 else 0}%)</p>
        <p><span class='neutral'>⚠ Partially verified claims:</span> {partial_count}/{total} ({int(partial_count/total*100) if total > 0 else 0}%)</p>
        <p><span class='unverified'>✗ Unverified claims:</span> {not_verified_count}/{total} ({int(not_verified_count/total*100) if total > 0 else 0}%)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Recommendations
    st.markdown("""
    <div class='report-section'>
        <h3>Next Steps</h3>
        <ul>
            <li>Request clarification on unverified claims</li>
            <li>Ask for additional documentation to support partially verified claims</li>
            <li>Consider the impact of unverified claims on the overall investment thesis</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Reset button
    if st.button("Analyze Another Pitch Deck"):
        st.session_state.claims_extracted = False
        st.session_state.verification_done = False
        st.session_state.claims = []
        st.session_state.verifications = {}
        st.experimental_rerun()

# Sidebar info
with st.sidebar:
    st.header("About")
    st.markdown("""
    This tool helps investors quickly verify claims made in pitch decks against financial data.
    
    **How it works:**
    1. Upload a pitch deck (PDF)
    2. Upload financial data (CSV or Excel)
    3. The tool extracts key claims
    4. Select claims to verify
    5. Get a detailed verification report
    
    **Privacy:** All data processing happens in your browser session. Documents are not stored.
    """)