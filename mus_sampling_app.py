import streamlit as st
import pandas as pd
import os
import numpy as np
from io import BytesIO

# Function to perform MUS sampling
def mus_sampling(df, amount_column, performance_materiality, trivial_threshold):
    # Convert the 'amount' column to numeric, coerce errors to NaN, and drop rows with NaN
    df[amount_column] = pd.to_numeric(df[amount_column], errors='coerce')
    df = df.dropna(subset=[amount_column])
    
    # Automatically include all items above Performance Materiality
    above_pm = df[df[amount_column] > performance_materiality]
    st.write(f"Automatically selected {len(above_pm)} items above the Performance Materiality threshold.")
    
    # Filter the remaining population for MUS sampling
    remaining_population = df[df[amount_column] <= performance_materiality]
    total_amount = remaining_population[amount_column].sum()
    sample_size = int(total_amount / performance_materiality) if total_amount > performance_materiality else 1
    
    # Perform MUS sampling
    cumulative_amounts = remaining_population[amount_column].cumsum()
    random_start = np.random.uniform(0, performance_materiality)
    sample_points = [random_start + i * performance_materiality for i in range(sample_size)]
    
    mus_samples = remaining_population.iloc[cumulative_amounts.searchsorted(sample_points)]
    
    return above_pm, mus_samples

# Function to validate inputs
def validate_inputs(df, amount_column, performance_materiality, trivial_threshold):
    errors = []
    if amount_column not in df.columns:
        errors.append(f"The file must contain a column named '{amount_column}'.")
    if performance_materiality <= 0:
        errors.append("Performance Materiality must be greater than 0.")
    if trivial_threshold <= 0:
        errors.append("Clearly Trivial threshold must be greater than 0.")
    if trivial_threshold >= performance_materiality:
        errors.append("Clearly Trivial threshold must be less than Performance Materiality.")
    return errors

# Streamlit app starts here
st.set_page_config(page_title="Monetary Unit Sampling (MUS) Web App", layout="wide")
st.title("Monetary Unit Sampling (MUS) Web App")

# Sidebar for inputs
with st.sidebar:
    st.header("Input Parameters")
    uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=['csv', 'xlsx'])
    
    if uploaded_file:
        file_extension = os.path.splitext(uploaded_file.name)[1]
        try:
            if file_extension == '.csv':
                df = pd.read_csv(uploaded_file)
            elif file_extension == '.xlsx':
                df = pd.read_excel(uploaded_file)
            else:
                st.error("Unsupported file type. Please upload a CSV or Excel file.")
                df = None
        except Exception as e:
            st.error(f"Error reading file: {e}")
            df = None
        
        if df is not None:
            st.success("File loaded successfully!")
            amount_column = st.selectbox("Select the column containing amounts", options=df.columns)
            performance_materiality = st.number_input("Enter the Performance Materiality amount", min_value=0.01, step=0.01)
            trivial_threshold = st.number_input("Enter the Clearly Trivial threshold amount", min_value=0.01, step=0.01)
            
            if st.button("Run Sampling"):
                errors = validate_inputs(df, amount_column, performance_materiality, trivial_threshold)
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Run sampling process
                    with st.spinner('Performing MUS sampling...'):
                        above_pm, mus_samples = mus_sampling(df, amount_column, performance_materiality, trivial_threshold)
                    
                    if above_pm is not None and mus_samples is not None:
                        st.success("Sampling completed successfully!")
                        
                        # Display results
                        st.header("Results")
                        st.subheader("Items Above Performance Materiality")
                        st.dataframe(above_pm)
                        st.subheader("MUS Samples")
                        st.dataframe(mus_samples)
                        
                        # Provide download buttons
                        def to_excel(df):
                            output = BytesIO()
                            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                df.to_excel(writer, sheet_name='Sheet1', index=False)
                            return output.getvalue()
                        
                        st.download_button(
                            label="Download Items Above PM (Excel)",
                            data=to_excel(above_pm),
                            file_name='above_pm.xlsx',
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )
                        
                        st.download_button(
                            label="Download MUS Samples (Excel)",
                            data=to_excel(mus_samples),
                            file_name='mus_samples.xlsx',
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )
                        
                        # Additional CSV download buttons
                        st.download_button(
                            label="Download Items Above PM (CSV)",
                            data=above_pm.to_csv(index=False),
                            file_name='above_pm.csv',
                            mime='text/csv'
                        )
                        
                        st.download_button(
                            label="Download MUS Samples (CSV)",
                            data=mus_samples.to_csv(index=False),
                            file_name='mus_samples.csv',
                            mime='text/csv'
                        )
    else:
        st.info("Please upload a file to begin.")

# Main area
if 'df' in locals():
    st.header("Data Preview")
    st.dataframe(df.head())
    
    st.header("Data Statistics")
    st.write(df.describe())
    
    # Data visualization
    if 'amount_column' in locals() and amount_column in df.columns:
        st.header("Data Visualization")
        st.bar_chart(df[amount_column])

# Instructions
st.sidebar.markdown("""
## Instructions
1. Upload a CSV or Excel file containing your data.
2. Select the column that contains the monetary amounts.
3. Enter the Performance Materiality and Clearly Trivial threshold amounts.
4. Click 'Run Sampling' to perform MUS.
5. View results and download Excel or CSV files with the samples.
""")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Developed with ❤️ using Streamlit")

