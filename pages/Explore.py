import streamlit as st
import pandas as pd

st.set_page_config(page_title="Explore Data", page_icon="🔍", layout="wide")
st.title("🔍 Explore Your Dataset")

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



df = None
if "cleaned_data" in st.session_state:
    df = st.session_state.cleaned_data
    st.info("💡 Your dataset has been **modified**.")
if "df" in st.session_state:
    df = st.session_state.df
elif "uploaded_file" in st.session_state:
    uploaded_file = st.session_state.uploaded_file
    uploaded_file.seek(0)

    

    try:
        # Read data according to the file type
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("⚠️ Unsupported file format.")
            st.stop()
        #st.success("✅ Original dataset loaded successfully for exploration.")

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        st.stop()
else:
    st.warning("⚠️ Please upload a dataset from the **Home** page first.")
    st.stop()

# الآن، إذا كان df موجودًا، يمكننا المتابعة بالتحليل
if df is not None:
    # 👁️ The preview
    #how many rows t show
    num_of_rows = st.number_input(
    "How many rows do you want to display?", 
    min_value=1, max_value=100, value=5, help="Enter a number between 1 and 100"
    )

    #from the first or he last rows?
    st.text("The first or the last rows?")
    left,right = st.columns(2)
    
    # 🆕 تغيير في منطق الأزرار لتجنب مشكلة "else"
    show_first = left.button("The first", use_container_width=True)
    show_last = right.button("The last", use_container_width=True)

    if show_last:
        st.subheader(f"👁️ Preview of the last {num_of_rows} rows")
        st.dataframe(df.tail(num_of_rows))
    else: # افتراضيًا أو إذا تم الضغط على "The first"
        st.subheader(f"👁️ Preview of the first {num_of_rows} rows")
        st.dataframe(df.head(num_of_rows))
    
    # Dataset Dimensions
    st.header("📐 Dataset Dimensions")
    col1,col2,col3 = st.columns(3)

    col1.metric("Columns",df.shape[1])
    col2.metric("Rows",df.shape[0])
    col3.metric("Duplicated rows",df.duplicated().sum())
    st.markdown("**🕳️ Missing Values per Column:**")
    missing = df.isnull().sum()
    st.dataframe(missing[missing > 0].reset_index().rename(columns={"index": "Column", 0: "Missing Values"}))

    st.markdown("**🔢 Columns names & Types:**")
    st.dataframe(df.dtypes.reset_index().rename(columns={"index": "Column", 0: "Data Type"}))
    
    st.divider()
    st.info("You may need to clean your data. Kindly go to the **Clean Data** page from the sidebar — or choose any other page you'd like to explore.")