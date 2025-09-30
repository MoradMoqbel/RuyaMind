import streamlit as st
import pandas as pd
import json
import requests
import time
import copy
import re # Added for potential future use, but mainly for clarity of imports

# --- 0. Page Configuration ---
st.set_page_config(
    page_title="AI Analyze",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded",
)

st.title("Analyze your data with AI🧠")

st.sidebar.title("Actions")
st.sidebar.page_link("main.py", label="Home", icon="🏠")
st.sidebar.page_link("pages/Scraping.py", label="Scrap Data", icon="🕸️")
st.sidebar.page_link("pages/Explore.py", label="Explore Data", icon="🔍")
st.sidebar.page_link("pages/Clean.py", label="Clean Data ", icon="🧼")
st.sidebar.page_link("pages/Transform.py", label="Transform Columns", icon="🔀")
st.sidebar.page_link("pages/ai_analysis.py", label="AI Analysis", icon="🧠")
st.sidebar.page_link("pages/Statistical.py", label="Statistical Analysis", icon="📊", disabled=True)
st.sidebar.page_link("pages/Visualization.py", label="Data Visualization", icon="📈", disabled=True)
st.sidebar.page_link("pages/Prediction.py", label="Prediction", icon="🤖", disabled=True)
st.sidebar.page_link("pages/Report.py", label="Generate Report", icon="📄", disabled=True)

# --- 1. Load DataFrame from Session State ---

# Check if a file has been uploaded in the session state (e.g., from Home page)
if "uploaded_file" in st.session_state and st.session_state.uploaded_file is not None:
    uploaded_file = st.session_state.uploaded_file

    # --- Start of fix for 'UploadedFile' object has no attribute 'id' ---
    # Create a unique identifier for the uploaded file using its name and size
    current_file_identifier = f"{uploaded_file.name}-{uploaded_file.size}"

    # Use this identifier to detect if the file has changed to avoid re-reading unnecessarily
    if 'current_loaded_file_identifier' not in st.session_state or st.session_state.current_loaded_file_identifier != current_file_identifier:
        
        uploaded_file.seek(0)  # Important: Reset file pointer to the beginning before reading
        
        try:
            # Read the file based on its extension
            if uploaded_file.name.endswith(".csv"):
                new_df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith((".xlsx", ".xls")):
                new_df = pd.read_excel(uploaded_file)
            else:
                st.error("❌ The file format is not supported yet. The supported formats are: CSV & Excel.") # Unsupported file format
                # Reset session state for df if format is unsupported
                st.session_state.df = pd.DataFrame() 
                st.session_state.current_loaded_file_identifier = None # Clear identifier
                st.stop() # Stop execution if file format is not supported

            st.success("✅ Dataset loaded successfully.") # Dataset loaded successfully
            st.session_state.df = new_df.copy() # Store a copy of the loaded DataFrame in session_state
            st.session_state.current_loaded_file_identifier = current_file_identifier # Store the new identifier
            # st.rerun() # Uncomment if you need an immediate rerun after file upload to refresh UI
            
        except Exception as e:
            st.error(f"❌ Error reading or processing file: {e}") # Error reading or processing file
            st.session_state.df = pd.DataFrame() # Set to empty DataFrame on error
            st.session_state.current_loaded_file_identifier = None
            st.stop() # Stop execution on error
    # --- End of fix ---
    
if 'df' not in st.session_state or st.session_state.df.empty:
    st.warning("⚠️Upload a file first.")
    st.stop()

 # Display a warning to the user about data privacy
st.info("Your data is sent to the AI model for processing. Be aware that this data is not stored, retained, or used by us for training or benefit. All information is immediately discarded once you close this tool.")
    
df = st.session_state.df

# --- 2. Initialize Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. Display Chat Messages from History on App Rerun ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Check if message has 'content' key (older format) or 'parts' key (new format)
        if 'content' in message:
            st.markdown(message["content"])
        elif 'parts' in message and message['parts']:
            # The API response is in a list of parts, so we extract the text
            st.markdown(message['parts'][0]['text'])

# --- 4. Get User's Prompt ---
if prompt := st.chat_input("What are you curios about?"):
   
    # Append the user's prompt to the messages list with the correct format for the API
    st.session_state.messages.append({"role": "user", "parts": [{"text": prompt}]})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- 5. Generate AI Response ---
    with st.chat_message("assistant"):
        with st.spinner("Analyzing in progress..."):
            
            # --- Construct the payload for a true conversational model ---
            df_csv = df.to_csv(index=False)
            
            # Create a copy of the messages to modify for the API call
            messages_for_api = copy.deepcopy(st.session_state.messages)

            # Check if this is the first message in the conversation.
            if len(messages_for_api) == 1:
                
                # V V V V V V V V V V V V V V V V V V V V V V V V V V V V V
                # التعديل الرئيسي: إضافة تعليمات مطابقة اللغة إلى التعليمات الأولية
                initial_instructions = (
                    "CRITICAL AND NON-NEGOTIABLE RULE: You are a data analysis assistant. You MUST respond ONLY in the exact language used by the user for their current query. For example, if the user writes in English, answer in English. If they write in Arabic, respond in Arabic. Do not translate the answer or switch languages unless the user explicitly requests it.\n"
                    "Based on the provided CSV data, answer the user's questions. "
                    "If the user requires Python code for analysis or visualization, provide it ONLY if explicitly asked. "
                    "If no code is requested, provide the answer directly in a clear, formatted text response. "
                    "The actual data in CSV format is below:\n"
                    f"```csv\n{df_csv}\n```\n"
                )
                # ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^
                
                # Prepend the instructions to the first user message
                messages_for_api[0]["parts"][0]["text"] = initial_instructions + messages_for_api[0]["parts"][0]["text"]

            # --- API Configuration for Gemini ---
            # IMPORTANT: The API key is set to an empty string as per environment requirements.
            apiKey = "AIzaSyCUPLVSFJkETekCbkvzOayMfKQG0zNlYU4" 
            apiUrl = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=" + apiKey

            headers = {
                "Content-Type": "application/json",
            }

            # The payload now uses the conversational history
            payload = {
                "contents": messages_for_api
            }

            max_retries = 5
            backoff_factor = 1.0
            response_text = "حدث خطأ أثناء الاتصال بالنموذج. يرجى المحاولة مرة أخرى."
            
            for i in range(max_retries):
                try:
                    response = requests.post(apiUrl, headers=headers, data=json.dumps(payload), timeout=30)
                    response.raise_for_status()
                    result = response.json()
                    
                    if result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts"):
                        response_text = result["candidates"][0]["content"]["parts"][0]["text"]
                        
                        # Store the assistant's response in the session state with the correct format
                        st.session_state.messages.append({"role": "model", "parts": [{"text": response_text}]})
                        break
                    else:
                        st.error("❌ استجابة النموذج لم تكن بالصيغة المتوقعة.")
                        break
                        
                except requests.exceptions.RequestException as e:
                    # Implement exponential backoff for retries
                    st.warning(f"⚠️ خطأ في الاتصال: {e}. محاولة إعادة الاتصال رقم {i + 1}...")
                    if i < max_retries - 1:
                        time.sleep(backoff_factor * (2 ** i))
                    else:
                        st.error("❌ لم يتمكن من الوصول للنموذج بعد عدة محاولات. يرجى التحقق من اتصالك بالإنترنت.")
                        break
                except Exception as e:
                    st.error(f"❌ خطأ غير متوقع: {e}")
                    break

            st.markdown(response_text)
