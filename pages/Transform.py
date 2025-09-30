import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="RuyaMind",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded",
)
st.title("Transform your data 🔀")

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

# If no file is uploaded or df is not yet in session_state (e.g., first run without upload)
if 'df' not in st.session_state or st.session_state.df.empty:
    st.warning("⚠️Please upload a file from the home page first.") # Please upload a dataset
    st.stop() # Stop further execution if no DataFrame is available

# Always use the DataFrame from session_state for the rest of the app
df = st.session_state.df
new_df = None


# Load the DataFrame from session state
df = st.session_state.df.copy()


select_operation = st.radio("What you would like to do? ",
        ["Change Data Type","Rename Columns","Create New Column","Merge Text Columns","Remove Columns"],
        horizontal=True) 

st.divider()
# Display the current DataFrame
st.subheader("Current Data:")
st.dataframe(df.head())
st.write("---")

# select operation
if select_operation == "Change Data Type":
    
    # --- 1. Change Data Type with Safety Check ---
    st.header("Change Data Type")
    st.write("Select a column to change its data type.")

    col_to_convert = st.selectbox(
        "Select Column",
        options=df.columns,
        key="convert_col_select"
    )

    # Display current data type
    if col_to_convert:
        st.info(f"💡 The current data type for column '{col_to_convert}' is: **{df[col_to_convert].dtype}**")

    col_type = st.selectbox(
        "Select New Data Type",
        options=['int', 'float', 'str', 'datetime', 'category'],
        key="convert_type_select"
    )

    if st.button("Apply Type Change", key="apply_convert_btn"):
        try:
            # Check for non-numeric values before converting to int or float
            if col_type in ['int', 'float']:
                non_numeric_vals = pd.to_numeric(df[col_to_convert], errors='coerce').isnull()
                if non_numeric_vals.any():
                    st.warning(f"⚠️ There are non-numeric values in the column '{col_to_convert}' which will be converted to missing values (NaN).")
                    st.dataframe(df[col_to_convert][non_numeric_vals].drop_duplicates())
                    if not st.checkbox("I agree to proceed despite non-numeric values", key="confirm_numeric_conv"):
                        st.stop()
            
            # Check for conversion to datetime
            if col_type == 'datetime':
                try:
                    pd.to_datetime(df[col_to_convert], errors='raise')
                except Exception as e:
                    st.error(f"❌ Cannot convert the column to datetime format. Please check the format.")
                    st.stop()

            # Perform the conversion
            if col_type == 'int':
                df[col_to_convert] = pd.to_numeric(df[col_to_convert], errors='coerce').astype('Int64')
            elif col_type == 'float':
                df[col_to_convert] = pd.to_numeric(df[col_to_convert], errors='coerce')
            elif col_type == 'str':
                df[col_to_convert] = df[col_to_convert].astype(str)
            elif col_type == 'datetime':
                df[col_to_convert] = pd.to_datetime(df[col_to_convert], errors='coerce')
            elif col_type == 'category':
                df[col_to_convert] = df[col_to_convert].astype('category')
            
            st.session_state.temp_df = df
            st.success(f"✅ Data type of column **{col_to_convert}** changed to **{col_type}** successfully.")
            #st.rerun()
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")

    st.write("---")

elif select_operation == "Rename Columns":

    # --- 2. Rename Columns ---
    st.header("Rename Columns")
    st.write("Select a column to rename it.")
    col_to_rename = st.selectbox(
        "Select Column",
        options=df.columns,
        key="rename_col_select"
    )
    new_col_name = st.text_input(
        "Enter the new name for the column",
        value=col_to_rename,
        key="new_name_input"
    )
    if st.button("Apply Rename", key="apply_rename_btn"):
        if col_to_rename != new_col_name and new_col_name:
            try:
                df.rename(columns={col_to_rename: new_col_name}, inplace=True)
                st.session_state.temp_df = df
                st.success(f"✅ Column name changed from **{col_to_rename}** to **{new_col_name}** successfully.")
                #st.rerun()
                st.dataframe(df)
            except Exception as e:
                st.error(f"❌ An error occurred: {e}")
        else:
            st.warning("⚠️ Please enter a new name different from the current one.")
            
    st.write("---")

elif select_operation == "Create New Column":
      
    # --- 3. Create New Column from Formula ---
    st.header("Create New Column from a Formula")
    st.write("Create a new column using a simple operation between two columns or a column and a custom value.")
    st.info("💡 **Note**: Mathematical operations are intended for numeric columns only.")

    # Get a list of only numeric columns
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    if not numeric_cols:
        st.warning("⚠️ There are no numeric columns to perform mathematical operations on.")
    else:
        new_col_name_formula = st.text_input("Enter the name for the new formula column", key="new_col_name_formula_input")
        col1_formula = st.selectbox("Select the first column", options=numeric_cols, key="col1_formula_select")
        operation = st.selectbox("Select the operation", options=['+', '-', '*', '/'], key="operation_select")
        
        operand_choice_formula = st.radio(
            "The second operand:",
            ('Another column', 'Custom value'),
            key="operand_choice_formula"
        )

        if operand_choice_formula == 'Another column':
            col2_formula = st.selectbox("Select the second column", options=numeric_cols, key="col2_formula_select")
        else:
            custom_value_formula = st.text_input("Enter the custom value", key="custom_value_formula_input")

        if st.button("Create Column from Formula", key="create_formula_col_btn"):
            if not new_col_name_formula:
                st.warning("⚠️ Please enter a name for the new column.")
            elif new_col_name_formula in df.columns:
                st.warning("⚠️ This name is exsit.")
            elif operand_choice_formula == 'Another column' and col1_formula == col2_formula:
                st.warning("⚠️ Please select two different columns.")
            else:
                try:
                    if operand_choice_formula == 'Another column':
                        if operation == '+':
                            df[new_col_name_formula] = df[col1_formula] + df[col2_formula]
                        elif operation == '-':
                            df[new_col_name_formula] = df[col1_formula] - df[col2_formula]
                        elif operation == '*':
                            df[new_col_name_formula] = df[col1_formula] * df[col2_formula]
                        elif operation == '/':
                            df[new_col_name_formula] = df[col1_formula] / df[col2_formula]
                    else:
                        value = float(custom_value_formula)
                        if operation == '+':
                            df[new_col_name_formula] = df[col1_formula] + value
                        elif operation == '-':
                            df[new_col_name_formula] = df[col1_formula] - value
                        elif operation == '*':
                            df[new_col_name_formula] = df[col1_formula] * value
                        elif operation == '/':
                            df[new_col_name_formula] = df[col1_formula] / value
                    
                    st.session_state.temp_df = df
                    st.success(f"✅ New column **{new_col_name_formula}** created successfully.")
                    #st.rerun()
                    st.dataframe(df)
                except Exception as e:
                    st.error(f"❌ An error occurred: {e}")

    st.write("---")

elif select_operation == "Merge Text Columns":
        
    # --- 4. Merge Multiple Text Columns ---
    st.header("Merge Text Columns")
    st.write("Create a new column by merging multiple text columns.")
    # Get a list of all non-numeric columns
    text_cols = df.columns.tolist()
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if numeric_cols:
        text_cols = [col for col in text_cols if col not in numeric_cols]

    if not text_cols:
        st.warning("⚠️ There are no text columns to merge.")
    else:
        new_col_name_merge = st.text_input("Enter the name for the new merged column", key="new_col_name_merge_input")
        cols_to_merge = st.multiselect(
            "Select the columns to merge",
            options=text_cols,
            key="cols_to_merge_select"
        )
        separator_merge = st.text_input("Enter a separator between columns (optional)", key="separator_merge_input")
        
        if st.button("Create Merged Column", key="create_merge_col_btn"):
            if not new_col_name_merge:
                st.warning("⚠️ Please enter a name for the new column.")
            elif len(cols_to_merge) < 2:
                st.warning("⚠️ Please select two or more columns to merge.")
            else:
                try:
                    # Convert all selected columns to string type
                    df_to_merge = df[cols_to_merge].astype(str)
                    # Concatenate the columns with the specified separator
                    df[new_col_name_merge] = df_to_merge.iloc[:, 0]
                    for i in range(1, len(cols_to_merge)):
                        df[new_col_name_merge] += separator_merge + df_to_merge.iloc[:, i]

                    st.session_state.temp_df = df
                    st.success(f"✅ New merged column **{new_col_name_merge}** created successfully.")
                    st.dataframe(df)
                    #st.rerun()
                except Exception as e:
                    st.error(f"❌ An error occurred: {e}")

elif select_operation == "Remove Columns":
        
    # --- 5. Remove Columns ---
    st.header("REMOVE Columns")
    st.write("Choose one or many columns to remove.")

    columns = df.columns.tolist()
    choosen_columns = st.multiselect("Choose columns to remove", options=columns)

    if st.button("Remove columns"):
        if choosen_columns:
            try:          
                df = df.drop(columns=choosen_columns) 
               
                st.session_state.temp_df = df
                st.success(f"✅ The column\s: {', '.join(choosen_columns)} removed.")
              
                st.dataframe(df)

            except Exception as e:
                st.error(f"❌ An arror occured {e}")
        else:
            st.warning("⚠️ Kindly Select at least one column to remove")


if st.button("💾 Save you changes?", key="save_changes_clean"): # Unique key
    st.session_state.df = st.session_state.temp_df # Save a copy of the modified DataFrame
    st.info("Your changes have been saved!") # Your changes have been saved!
    st.dataframe(st.session_state.df.head()) # Display for confirmation


st.download_button(label = "⬇️ Download your modified data (as .csv)", data= df.to_csv(index=False), file_name="modified_data.csv")