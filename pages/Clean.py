import streamlit as st
import pandas as pd
import numpy as np # Required for np.nan if used in default data

# --- 0. Page Configuration ---
st.set_page_config(
    page_title="InsightBox - Clean Data", # Page title for the browser tab
    layout="wide",
    page_icon="🧼",
    initial_sidebar_state="expanded",
)

st.title("Clean your data 🧼")

# --- Sidebar Navigation (Assuming this is for a multi-page app structure) ---
# It's generally better to define sidebar navigation in main.py or a shared module
# to avoid duplication across pages. However, keeping it as per user's request.

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



# --- 1. Initialize and Manage DataFrame in Session State ---
# This block ensures the DataFrame persists across interactions and loads from uploaded file.

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
# --- 2. Choose an operation ---

select_operation = st.radio("What you would like to ? ",
        ["Missing data","Duplicated data","Text normalization","Edit records"],
        horizontal=True) 



# --- Missing Data Handling ---
if select_operation == "Missing data":
    # --- 3. Missing Values Summary ---
    count_of_missing = df.isnull().sum().sum()
    st.header("Handle missing data") 
    st.subheader("🕳️ Summary of missing data")
    if count_of_missing > 0:
        st.caption(f"This dataset has {count_of_missing} rows of missing values distributed as:")
    missing_df = df.isnull().sum().reset_index()
    missing_df.columns = ["Column", "Missing Values"]
    missing_df = missing_df[missing_df["Missing Values"] > 0]

    if missing_df.empty:
        st.success("🎉 No missing data found!") # No missing values detected!
    else:
        st.dataframe(missing_df)

        st.markdown("### 🛠️ How would you like to handle them?") # How would you like to handle them?

        cleaning_option = st.radio(
            "Choose a strategy:", # Choose a strategy:
            ["❌ Drop rows with missing values", # Drop rows with missing values
             "🔧 Fill columns with (mean / median / zero) value (Only for the numarical ones)", # Fill numeric columns (mean / median / zero)
             "📊 Fill columns with the most frequent value (Only for the categorical ones)",
             "✏️ Fill manually with a custom value"], # Fill manually with a custom value
            index=0,
            key="cleaning_strategy_radio_clean" # Unique key for this radio button
        )
    
        # --- 4. Column Selection Interface (Applies to all cleaning operations) ---
        st.subheader("Choose columns to apply:") # Choose columns to apply:
        col_select1, col_select2 = st.columns(2) # Use new variable names to avoid potential conflicts

        # Initialize session state for column selection
        if 'all_cols_selected_state' not in st.session_state:
            st.session_state.all_cols_selected_state = False
        if 'custom_cols_selected_list_state' not in st.session_state:
            st.session_state.custom_cols_selected_list_state = []

        # Button for "All Columns"
        if col_select1.button("All columns", key="all_cols_btn_clean"): # Unique key
            st.session_state.all_cols_selected_state = True
            st.session_state.custom_cols_selected_list_state = [] # Clear custom selection
            #st.rerun() # Rerun to update UI based on new selection state

        # Multiselect for "Custom Columns"
        current_custom_selection = col_select2.multiselect(
            "or custom columns:", # Or custom columns:
            options=df.columns.tolist(),
            default=st.session_state.custom_cols_selected_list_state, # Retain previous selection
            key="custom_cols_multiselect_clean" # Unique key
        )

    # Update session state when custom multiselect changes
    if not missing_df.empty and current_custom_selection != st.session_state.custom_cols_selected_list_state:
        st.session_state.custom_cols_selected_list_state = current_custom_selection
        st.session_state.all_cols_selected_state = False # Clear "All Columns" selection
        #st.rerun() # Rerun to update UI

    # ------------------------------------------------------------------

    # --- 5. Cleaning Operations Logic ---

    # --- 5.1. Drop rows with missing values ---
    if not missing_df.empty and cleaning_option == "❌ Drop rows with missing values":
        st.markdown("---")
        st.subheader("Remove rows with missing values:") # Remove rows with missing values
        commit_drop_button = st.button("Commit drop missing values", key="commit_drop_clean") # Unique key

        if commit_drop_button:
            original_rows = df.shape[0]
            
            # Logic based on stored selection state
            if st.session_state.all_cols_selected_state:
                df.dropna(inplace=True)
                removed_rows = original_rows - df.shape[0]
                st.info(f"🧹 **{removed_rows}** rows had been removed.") # Removed X rows from all columns
            elif st.session_state.custom_cols_selected_list_state:
                if not st.session_state.custom_cols_selected_list_state:
                    st.warning("Please select at least one column.") # Please select at least one column
                else:
                    df.dropna(subset=st.session_state.custom_cols_selected_list_state, inplace=True)
                    removed_rows = original_rows - df.shape[0]
                    st.info(f"🧹 **{removed_rows}** rows had been removed from the columns: **{', '.join(st.session_state.custom_cols_selected_list_state)}**.") # Removed X rows from selected columns
            else:
                st.warning("Before commit this operation, please select all columns or custom columns.") # Please choose an option
            
            st.dataframe(df) # Display DataFrame after modification

    # --- 5.2. Fill numeric columns (mean / median / zero) ---
    elif not missing_df.empty and cleaning_option == "🔧 Fill columns with (mean / median / zero) value (Only for the numarical ones)":
        st.markdown("---")
        st.subheader("Fill missing numeric values:") # Fill missing numeric values
        strategy = st.selectbox("Select the filling way:", ["Mean", "Median", "Zero"], key="fill_strategy_select_clean_numeric") # Unique key
        
        
            # --- Start of modification: Filter numeric columns to include only those with missing values ---
        numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
        numeric_cols_with_missing = numeric_cols[df[numeric_cols].isnull().any()].tolist()
        # --- End of modification ---
        
        commit_fill_numeric_button = st.button("تطبيق الملء الرقمي", key="commit_fill_numeric_clean") # Unique key

        if commit_fill_numeric_button:
            cols_to_fill = []
            if st.session_state.all_cols_selected_state:
                cols_to_fill = numeric_cols_with_missing # All numeric columns with missing values
            elif st.session_state.custom_cols_selected_list_state:
                # Filter custom selected columns to include only numeric ones with missing values
                cols_to_fill = [col for col in st.session_state.custom_cols_selected_list_state if col in numeric_cols_with_missing]
            
            if not cols_to_fill:
                 st.warning("الرجاء اختيار 'كل الأعمدة' أو تحديد أعمدة رقمية مخصصة تحتوي على قيم مفقودة.") # Please select 'All Columns' or specific numeric columns with missing values
            else:
                for col in cols_to_fill:
                    if col in df.columns: # Ensure column still exists (good practice)
                        # Check if the column actually has missing values before attempting to fill
                        if df[col].isnull().any():
                            if strategy == "Mean":
                                df[col].fillna(df[col].mean(), inplace=True)
                            elif strategy == "Median":
                                df[col].fillna(df[col].median(), inplace=True)
                            elif strategy == "Zero":
                                df[col].fillna(0, inplace=True)
                        else:
                            st.info(f"ℹ️ العمود '{col}' لا يحتوي على قيم مفقودة لملئها.") # Column has no missing values to fill
                
                st.success(f"✅ تم ملء القيم الرقمية المفقودة في **{', '.join(cols_to_fill)}** باستخدام `{strategy}`.") # Missing numeric values filled
                st.dataframe(df)

    # --- 5.3.  Fill the categorical columns with the most frequent value    ---
    elif not missing_df.empty and cleaning_option == "📊 Fill columns with the most frequent value (Only for the categorical ones)":
        st.markdown("---")
        st.subheader("Fill missing values:") # Fill missing values
        #strategy = st.selectbox("Select the filling way:", ["Mean", "Median", "Zero"], key="fill_strategy_select_clean_numeric") # Unique key
        
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns
        categorical_cols_with_missing = categorical_cols[df[categorical_cols].isnull().any()].tolist()
        
        commit_fill_categorical_button = st.button("Commit filling", key="commit_fill_categorical_clean") # Unique key

        if commit_fill_categorical_button:
            cols_to_fill = []
            if st.session_state.all_cols_selected_state:
                cols_to_fill = categorical_cols_with_missing # All categorical columns
            elif st.session_state.custom_cols_selected_list_state:
                # Filter custom selected columns to include only categorical ones
                cols_to_fill = [col for col in st.session_state.custom_cols_selected_list_state if col in categorical_cols_with_missing]
            
            if not cols_to_fill:
                 st.warning("Please select 'All Columns' or specific categorical columns.") # Please select 'All Columns' or specific numeric columns
            else:
                for col in cols_to_fill:
                    if col in df.columns: # Ensure column still exists (good practice)
                        mode_result = df[col].mode()
                        if not mode_result.empty:
                            mode_val = mode_result[0] 
                            df[col].fillna(mode_val, inplace=True)
                        else:
                           st.warning(f"⚠️ No frequent value found to fill column '{col}'. It might contain all missing values.") # No mode found
                
                st.success(f"✅ Missing values in the **{', '.join(cols_to_fill)}** columns, filled with the most frequent value.") # Missing numeric values filled
                st.dataframe(df)

                        

    # --- 5.4. Fill manually with a custom value ---
    elif not missing_df.empty and cleaning_option == "✏️ Fill manually with a custom value":
        st.markdown("---")
        st.subheader("Fill manually with a custom value:") # Fill manually with a custom value
        custom_fill_value = st.text_input("Enter a value to fill the missing values:", key="manual_fill_value_input_clean") # Unique key
        
        commit_fill_manual_button = st.button("Commit the manual filling", key="commit_fill_manual_clean") # Unique key

        if commit_fill_manual_button:
            if not custom_fill_value:
                st.warning("Please enter a value!.") # Please enter a value
            elif not st.session_state.all_cols_selected_state and not st.session_state.custom_cols_selected_list_state:
                st.warning("Please select 'All Columns' or custom columns.") # Please select 'All Columns' or custom columns
            else:
                cols_to_fill = []
                if st.session_state.all_cols_selected_state:
                    cols_to_fill = df.columns.tolist() # All columns
                elif st.session_state.custom_cols_selected_list_state:
                    cols_to_fill = st.session_state.custom_cols_selected_list_state # Selected custom columns
                
                for col in cols_to_fill:
                    if col in df.columns: # Ensure column still exists
                        df[col].fillna(custom_fill_value, inplace=True)
                
                st.success(f"✅ Missing values in the  **{', '.join(cols_to_fill)}** columns, filled with `{custom_fill_value}`.") # Missing values filled
                st.dataframe(df)









# --- Duplicated Data Handling ---
elif select_operation == 'Duplicated data': # select_operation == "Duplicated data"
    # --- 7. Duplicated values ---
 
    count_of_duplicated = df.duplicated().sum()
    count_of_custom_duplicated = df.duplicated(subset=(df.columns.tolist())).sum()

    if count_of_duplicated < 1 & count_of_custom_duplicated:
        st.success("🎉 No duplicated data found!") # No duplicated values detected!
    else:
        
        st.header(" Handle duplicated data")     
        st.subheader("♻️ Summary of duplicated data")


        col1,col2 = st.columns(2)
        all_rows = col1.button("All rows", key="duplicated_all_rows") # Added unique key
        
        # Ensure custome_rows is initialized before use
        if 'duplicated_custom_cols_selected_list' not in st.session_state:
            st.session_state.duplicated_custom_cols_selected_list = []

        custome_rows = col2.multiselect(
            "Custom rows (select columns to consider for duplicates)",
            df.columns.tolist(),
            default=st.session_state.duplicated_custom_cols_selected_list,
            key="duplicated_custom_rows_multiselect" # Added unique key
        )
        
        # Update session state for custom rows selection
        if custome_rows != st.session_state.duplicated_custom_cols_selected_list:
            st.session_state.duplicated_custom_cols_selected_list = custome_rows
            #st.rerun()

        sum_of_duplicated_display = 0
        current_duplicated_df = pd.DataFrame()

        if all_rows: 
            sum_of_duplicated_display = df.duplicated().sum()
            current_duplicated_df = df[df.duplicated()] # Show all duplicated rows for preview
        elif custome_rows: 
            sum_of_duplicated_display = df.duplicated(subset=custome_rows).sum()
            current_duplicated_df = df[df.duplicated(subset=custome_rows)] # Show all duplicated rows for preview
        else:
            # Default state when neither "All rows" button is pressed nor custom rows are selected
            sum_of_duplicated_display = df.duplicated().sum()
            current_duplicated_df = df[df.duplicated()]
            
        st.caption(f"This dataset currently shows {sum_of_duplicated_display} duplicated values based on your selection.")
        
        if not current_duplicated_df.empty:
            st.write("Preview of duplicated rows (before removal):")
            st.dataframe(current_duplicated_df)

            st.markdown("### 🛠️ How would you like to handle them?") # How would you like to handle them?
        
            col1_del, col2_del = st.columns(2) # Renamed to avoid conflict with previous col1, col2

            delete_operation = col1_del.radio(
                "Delete based on:", 
                options=["All rows", "Custom rows (requires selection above)"],
                key="duplicated_delete_operation_radio" # Added unique key
            )
            delete_options = col2_del.selectbox(
                "Keep:", 
                options=["First occurrence", "Last occurrence", "None (delete all duplicates)"],
                key="duplicated_keep_option_select" # Added unique key
            )

            commit_delete = st.button("Commit delete", key="commit_delete_duplicates") # Added unique key

            if commit_delete:
                new_df = df.copy() # Create a copy to modify

            subset_cols = None

            if delete_operation == "Custom rows (requires selection above)":
                if not st.session_state.duplicated_custom_cols_selected_list:
                    st.warning("Please select custom columns above to apply 'Custom rows' deletion.")
                    st.stop()
                subset_cols = st.session_state.duplicated_custom_cols_selected_list

            keep_strategy = 'first' # Default
            if delete_options == "Last occurrence":
                keep_strategy = 'last'
            elif delete_options == "None (delete all duplicates)":
                keep_strategy = False # This keeps no duplicates

            # Apply drop_duplicates
            if new_df is not None:
                rows_before = new_df.shape[0]
                new_df = new_df.drop_duplicates(subset=subset_cols, keep=keep_strategy)
                rows_after = new_df.shape[0]
            
                removed_count = rows_before - rows_after

            # --- Crucial: Update the DataFrame in session state ---
                st.session_state.df = new_df.copy() # Save the modified DataFrame back to session state
                df = st.session_state.df # Update the local df variable to reflect changes

                st.success(f"✅ Successfully removed **{removed_count}** duplicated rows.")
                st.write(f"🧮 New dataset shape: {df.shape}")
                st.dataframe(df.head()) # Show a preview of the cleaned DataFrame
           # st.rerun() # Rerun to refresh the UI and the duplicated count
        else:
            st.info("No duplicated rows to display based on current selection.")







# --- Text Normalization Handling ---
elif select_operation == "Text normalization":
    st.header("Normalization text columns") 
    text_columns_df = df.select_dtypes(include=['object', "category"]) # Get the DataFrame with only text/categorical columns

    if len(text_columns_df.columns) > 0:
        st.subheader("🔤 Summary of text columns")
        st.caption(f"This dataset contains {len(text_columns_df.columns)} text columns.") 
        st.dataframe(text_columns_df.head()) # Display a preview of text columns

        st.markdown("### 🛠️ How would you like to normalize them?")

        selected_text_cols = st.multiselect("Select columns to normalize:", text_columns_df.columns.tolist(), key="text_norm_multiselect")

        selected_operation = st.selectbox("How do you want to normalize? ", options=["Lower", "Upper", "Capitalize", "Remove Whitespaces","Remove the strange characters (#,%,etc)"], key="text_norm_operation_select")

        commit_normalize = st.button("Commit normalize", key="commit_normalize_text")

        if commit_normalize:
         
            new_df = df.copy() 

            if not selected_text_cols:
                st.warning("Please select at least one column to normalize.")
            else:
                for col in selected_text_cols:
                    if col in new_df.columns: # Ensure column exists                 
                            if selected_operation == "Lower":
                                new_df[col] = new_df[col].str.lower()
                            elif selected_operation == "Upper":
                                new_df[col] = new_df[col].str.upper()
                            elif selected_operation == "Capitalize": # Added Capitalize logic
                                new_df[col] = new_df[col].str.capitalize()
                            elif selected_operation == "Remove Whitespaces": # Added Remove Whitespaces logic
                                new_df[col] = new_df[col].str.strip() # .strip() removes leading/trailing whitespace
                            elif selected_operation == "Remove the strange characters (#,%,etc)":
                                new_df[col] =  new_df[col].str.replace(r"[^\w\s]", "", regex=True) 
                       
                st.success("✅ Text columns normalized successfully!")

                # --- Crucial: Update the DataFrame in session state ---
                st.session_state.df = new_df.copy() # Save the modified DataFrame back to session state
                # No need to update local df variable here as st.rerun() will reload it
                
                st.dataframe(st.session_state.df.head()) # Display preview of normalized data
                #st.rerun() # Rerun to refresh the UI and show updated DataFrame
        
    else:
        st.info("There are no text columns in this dataset.")

elif select_operation == "Edit records": # NEW SECTION FOR EDIT RECORDS
    st.header("Edit Records")
    st.subheader("📝 Edit your dataset directly")

    st.info("You can edit cells, add new rows, or delete existing rows directly in the table below.")

    # Use st.data_editor to allow direct editing
    # The returned DataFrame `edited_df` contains the changes
    # Use st.session_state.df directly here so data editor works on the current state
    edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", key="data_editor_clean")
    commit_edit = st.button("Commit Edits")
    # --- FIX for st.data_editor: Try to convert numerical columns back to Int64Dtype ---
    # This block runs after data_editor returns, on every rerun.
    temp_df_for_editor_conversion = edited_df.copy() # Work on a copy of the edited_df

    # Iterate through columns to attempt conversion
    for col in temp_df_for_editor_conversion.columns:
        # Check if the column currently has a numeric type (float or int)
        if pd.api.types.is_numeric_dtype(temp_df_for_editor_conversion[col]):
            # Try to convert to Int64Dtype (nullable integer)
            try:
                # Convert to numeric first, coercing errors to NaN
                # Then convert to nullable integer type
                temp_df_for_editor_conversion[col] = pd.to_numeric(temp_df_for_editor_conversion[col], errors='coerce').astype(pd.Int64Dtype())
            except Exception:
                # If conversion to Int64Dtype fails (e.g., contains non-integer floats),
                # keep it as its current numeric type (likely float)
                pass # Do nothing, keep original numeric type (float or int)

    # Check if the processed DataFrame from data_editor is different from the current session state df
    # This detects changes made directly in the data editor.
    if not temp_df_for_editor_conversion.equals(st.session_state.df) and commit_edit:
        st.session_state.df = temp_df_for_editor_conversion.copy() # Save the edited DataFrame back to session state
        st.success("✅ Changes from data editor saved successfully!")
        st.dataframe(st.session_state.df.head()) # Show updated DataFrame preview
        #st.rerun() # Rerun to reflect changes immediately across the app

    
    col1,col2 = st.columns(2)
    remove_or_replace = col2.selectbox("Replace or Remove?",options=["Replace","Remove"])
    col1.subheader(f"Find and {remove_or_replace}")

    if remove_or_replace == "Replace":

        col3,col4,col5 = st.columns(3)
        old_value = col3.text_input("Old value to replace:", key="old_value_input")
        new_value = col4.text_input("New value:", key="new_value_input")
        to_column = col5.selectbox("Apply to column:", options=df.columns.tolist(), key="replace_column_select")

    else:
        col6,col7 = st.columns(2)
        remove_value = col6.text_input("Enter the value which you want to delete base on it", key="remove_value_input")
        to_column = col7.selectbox("In the column:", options=df.columns.tolist(), key="replace_column_select")


    commit_changes_button = st.button("Apply your chnges", key="commit_changes_button")
    if commit_changes_button:
        # --- FIX: Ensure new_df is defined within this block ---
        # We need a copy to work on, then save it back to session state
        temp_df_for_changes = df.copy() # Use a temporary name to avoid confusion

        if remove_or_replace == "Replace":
            if not to_column:
                st.warning("Please select a column to apply the changes.")
            elif not old_value:
                st.warning("Please enter the old value to replace.")
            elif not new_value:
                st.warning("Please enter the new value to replace.")
            else:
            # Determine column type for appropriate replacement
                current_col_dtype = temp_df_for_changes[to_column].dtype

                replaced_count = 0
                
                # --- FIX for Find and Replace: Handle numerical vs. string replacement ---
                if pd.api.types.is_numeric_dtype(current_col_dtype):
                    try:
                        # Attempt numerical replacement
                        old_val_num = pd.to_numeric(old_value)
                        new_val_num = pd.to_numeric(new_value)
                        
                        initial_count = (temp_df_for_changes[to_column] == old_val_num).sum()
                        temp_df_for_changes[to_column].replace(old_val_num, new_val_num, inplace=True)
                        final_count = (temp_df_for_changes[to_column] == old_val_num).sum()
                        replaced_count = initial_count - final_count

                        # After numerical replacement, try to convert to nullable integer if applicable
                        try:
                            temp_df_for_changes[to_column] = temp_df_for_changes[to_column].astype(pd.Int64Dtype())
                        except Exception:
                            # If it can't be Int64 (e.g., contains floats), keep it as float
                            pass

                    except ValueError:
                        st.warning(f"⚠️ Cannot replace '{old_value}' with '{new_value}' numerically in column '{to_column}'. Values are not purely numeric.")
                        st.stop() # Stop execution if numerical conversion fails
                else: # Assume it's a string/object/categorical column
                    # Ensure values are string before string replacement
                    initial_count = (temp_df_for_changes[to_column].astype(str) == str(old_value)).sum()
                    temp_df_for_changes[to_column] = temp_df_for_changes[to_column].astype(str).replace(str(old_value), str(new_value))
                    final_count = (temp_df_for_changes[to_column].astype(str) == str(old_value)).sum()
                    replaced_count = initial_count - final_count

                st.session_state.df = temp_df_for_changes.copy() # Save the modified DataFrame back to session state
                
                st.success(f"✅ Successfully replaced '{old_value}' with '{new_value}' in column '{to_column}'. (Affected {replaced_count} cells)")
                st.dataframe(st.session_state.df.head()) # Show updated DataFrame preview
                #st.rerun() # Rerun to reflect changes immediately
        else:
            temp_df_for_removal = df.copy() # Work on a copy

            # --- FIX: Handle data type consistency for comparison ---
            # Convert remove_value to the column's dtype if possible for accurate comparison
            try:
                # Try to convert remove_value to the column's original dtype
                if pd.api.types.is_numeric_dtype(temp_df_for_removal[to_column].dtype):
                    converted_remove_value = pd.to_numeric(remove_value)
                else:
                    # For non-numeric, compare as string
                    converted_remove_value = str(remove_value)
                    temp_df_for_removal[to_column] = temp_df_for_removal[to_column].astype(str) # Ensure column is string for comparison
            except ValueError:
                st.error(f"❌ Cannot convert '{remove_value}' to match the data type of column '{to_column}'.")
                st.stop()

            # Find indices of rows where the value matches
            # Use .loc for explicit indexing to avoid SettingWithCopyWarning
            rows_to_drop_indices = temp_df_for_removal.index[temp_df_for_removal[to_column] == converted_remove_value].tolist()
            
            if not rows_to_drop_indices:
                st.info(f"ℹ️ No rows found with value '{remove_value}' in column '{to_column}'.")
            else:
                original_row_count = temp_df_for_removal.shape[0]
                temp_df_for_removal.drop(rows_to_drop_indices, inplace=True)
                removed_count = original_row_count - temp_df_for_removal.shape[0]

                st.session_state.df = temp_df_for_removal.copy() # Save the modified DataFrame
                
                st.success(f"✅ Successfully removed **{removed_count}** rows where '{remove_value}' was found in column '{to_column}'.")
                st.dataframe(st.session_state.df.head()) 

# --- 6. Save Cleaned Data to Session State ---
st.markdown("---")
if st.button("💾 Save you changes?", key="save_changes_clean"): # Unique key
    st.session_state.cleaned_data = df.copy() # Save a copy of the modified DataFrame
    st.info("Your changes have been saved!") # Your changes have been saved!
    st.dataframe(st.session_state.cleaned_data.head()) # Display for confirmation


st.download_button(label = "⬇️ Download your modified data (as .csv)", data= df.to_csv(index=False), file_name="modified_data.csv")