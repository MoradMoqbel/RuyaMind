import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import io
import requests

# --- Page Configuration ---
st.set_page_config(
    page_title="Scraping from website",
    layout="wide",
    page_icon="🕸️"
)

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


# --- UI elements in Arabic ---
st.title("Scraping from websites 🕸️")
st.write("Insert the link, and let RuyaMind handle the rest.")
st.write("Note: Some dynamics website may take a bit longer time.")

# --- User Input ---
url_input = st.text_input(
    "Insert the link here:",""
)#https://en.wikipedia.org/wiki/List_of_countries_by_GNI_(PPP)_per_capita

# --- Web Scraping Function with Selenium ---
def get_tables_from_url_selenium(url):
    """
    Fetches the URL using Selenium to handle dynamic content,
    then extracts all HTML tables into a list of DataFrames.
    """
    try:
        # Set up headless Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Runs in background without UI
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Use WebDriver Manager to automatically handle driver
        # We need to manually handle this on some environments
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
        except Exception:
            # Fallback for environments without the manager
            st.warning("`webdriver_manager` not found. Assuming Chrome driver is in PATH.")
            service = Service('chromedriver')

        driver = webdriver.Chrome(service=service, options=chrome_options)

        st.info("Page loading, and run javascript...")
        driver.get(url)
        
        # Give the page some time to render dynamic content
        time.sleep(5)
        
        # Get the page source after rendering
        html_content = driver.page_source
        
        # Close the browser instance
        driver.quit()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all tables in the HTML
        tables = soup.find_all('table')
        
        if not tables:
            st.warning("After loading, there was no table in the html code.")
            return []
        
        # Convert tables to pandas DataFrames
        df_list = pd.read_html(io.StringIO(str(soup)))
        return df_list
        
    except Exception as e:
        st.error(f"❌ خطأ: حدث خطأ أثناء محاولة الوصول إلى الرابط أو استخراج الجداول. تفاصيل الخطأ: {e}")
        return None

# --- Main application logic ---
if 'tables' not in st.session_state:
    st.session_state['tables'] = []
if 'selected_table_index' not in st.session_state:
    st.session_state['selected_table_index'] = 0

if st.button("Scrap tables"):
    if url_input:
        with st.spinner("Scraping now, thanks for patience..."):
            extracted_tables = get_tables_from_url_selenium(url_input)
            
            if extracted_tables is not None:
                if extracted_tables:
                    st.session_state['tables'] = extracted_tables
                    st.success(f"✅ RuyaMind found {len(extracted_tables)} table.")
                    st.session_state['selected_table_index'] = 0 # Reset selection
                else:
                    st.error("❌ No table found in this link.")
                    st.session_state['tables'] = []
            else:
                st.session_state['tables'] = []
    else:
        st.error("Kindly insert a valid link.")

# --- Display logic ---
if st.session_state['tables']:
    # Use a selectbox to choose which table to display
    table_names = [f"Table number {i+1}" for i in range(len(st.session_state['tables']))]
    
    selected_table_index = st.selectbox(
        "Choose a table to show:",
        options=range(len(st.session_state['tables'])),
        format_func=lambda x: table_names[x],
        key="selected_table_index" # This links the selectbox to the session state
    )

    # Display the selected table from the session state
    if selected_table_index is not None:
        st.dataframe(st.session_state['tables'][selected_table_index])

    # --- Button to download the selected table as CSV ---
    csv_string = st.session_state['tables'][selected_table_index].to_csv(index=False)
    st.download_button(
        label="📥 Download the current table as CSV",
        data=csv_string,
        file_name=f"Table_{selected_table_index + 1}.csv",
        mime="text/csv"
    )
    if st.button("Is this your data?"):
        st.session_state.df = st.session_state['tables'][selected_table_index]
        st.success("Your data saved, you can now go ahead with it!")