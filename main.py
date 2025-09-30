import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Ruya mind",
    layout="wide",
    page_icon="D:\Morad\InsightBox\RuyaMind.ico",
    initial_sidebar_state="expanded", 
)
st.title("RuyaMind")
st.caption("Simple steps. Great results")
st.markdown("""
RuyaMind is an open-source platform that simplifies data analytics through an intuitive and bilingual interface.
""")
st.link_button("Develpoed by: Morad Moqbel", "https://linkedin.com/in/moradmoqbel")

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

#st.info("This is a beta release. Your experience may vary as we continue to improve the platform.")

st.header("Upload your file 📁 ")
st.caption("Kindly notice that in the meaning time, this tool accpets only .csv & .xlsx formats!")
data = st.file_uploader("Upload your dataset", type=["csv","xlsx"])

if data:
    if data.name.endswith(".csv"):
        df = pd.read_csv(data)
    else:
        df = pd.read_excel(data)

    st.info("Looks like you've uploaded a file! If it's the right one, feel free to explore the next step from the sidebar — or re-upload if you'd like to start over", icon="ℹ️")
    st.dataframe(df.head())
    st.session_state.uploaded_file = data

st.divider()

st.header("📘 What can you do with RuyaMind")

st.subheader("Web Scraping 🕸️")
st.write("Extract data tables from any website and store them directly in the application for analysis.")
st.divider()

st.subheader("Explore Data 🔍")
st.write("Get a quick overview of your dataset — view its structure, columns, and missing values to understand your data at a glance.")
st.divider()

st.subheader("Clean Data 🧼")
st.write("Handle missing values, remove duplicates, and prepare your dataset for deeper analysis — all with easy, guided options.")
st.divider()

st.subheader("Transform Columns 🔀")
st.write("Convert data types, encode text values, or engineer new variables to reshape your dataset into analysis-ready form. ")
st.divider()

st.subheader("AI-Powered Analysis 🧠")
st.write("Ask natural language questions about your data and get answers and insights from an AI model.")
st.divider()

st.header("Coming soon...")

st.subheader("Statistical Analysis 📊")
st.write("Generate quick statistical summaries like mean, median, range, and standard deviation to better understand numeric patterns in your data.")
st.divider()

st.subheader("Data Visualization 📈")
st.write("Create interactive visualizations like histograms and bar charts to explore trends and distributions visually")
st.divider()

st.subheader("Prediction 🤖")
st.write("Apply smart models to make predictions from your data and discover hidden insights automatically. ")
st.divider()

st.subheader("Generate Report 📄")
st.write("Export your cleaned or transformed data as a downloadable report — ready for sharing or further processing.")
st.divider()
