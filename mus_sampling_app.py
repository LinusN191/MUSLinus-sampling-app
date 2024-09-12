import pandas as pd
import os
import streamlit as st

# Function to perform MUS sampling
def mus_sampling(df, amount_column, performance_materiality, trivial_threshold):
    # Ensure the specified 'amount' column exists in the file
    if amount_column not in df.columns:
        st.error(f"Error: The file must contain a column named '{amount_column}'.")
        return None, None

    # Convert the 'amount' column to numeric, coerce errors to NaN, and drop rows with NaN
    df[amount_column] = pd.to_numeric(df[amount_column], errors='coerce')
    df = df.dropna(subset=[amount_column])

    # Step 1: Automatically include all items above the Performance Materiality threshold
    above_pm = df[df[amount_column] > performance_materiality]
    st.write(f"Automatically selected {len(above_pm)} items above the Performance Materiality threshold.")

    # Step 2: Filter the remaining population for MUS sampling (below PM threshold)
    remaining_population = df[df[amount_column] <= performance_materiality]

    # Step 3: Perform MUS sampling for remaining population based on Clearly Trivial threshold
    mus_samples = remaining_population[remaining_population[amount_column] >= trivial_threshold]

    return above_pm, mus_samples

# Streamlit app starts here
st.title("Monetary Unit Sampling (MUS) Web App")

# Step 2: File Upload for CSV/Excel
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=['csv', 'xlsx'])

# Check if a file has been uploaded
if uploaded_file:
    file_extension = os.path.splitext(uploaded_file.name)[1]

    # Load CSV or Excel file
    if file_extension == '.csv':
        df = pd.read_csv(uploaded_file)
    elif file_extension == '.xlsx':
        df = pd.read_excel(uploaded_file)
    
    st.write("File loaded successfully!")
    st.dataframe(df.head())  # Show the first few rows of the dataframe

    # Step 3: Input for column containing amounts
    amount_column = st.text_input("Enter the column name that contains the amounts")

    # Step 4: Input Performance Materiality (PM) and Clearly Trivial (CT) Thresholds
    performance_materiality = st.number_input("Enter the Performance Materiality amount", min_value=0.0, step=0.01)
    trivial_threshold = st.number_input("Enter the Clearly Trivial threshold amount", min_value=0.0, step=0.01)

    # Step 5: Input folder path to save output files
    output_dir = st.text_input("Enter the folder path to save the output files")

    # Step 6: Run Sampling Process
    if st.button("Run"):
        if not os.path.exists(output_dir):
            st.error("The specified folder path does not exist. Please provide a valid path.")
        else:
            if df is not None and amount_column:
                above_pm, mus_samples = mus_sampling(df, amount_column, performance_materiality, trivial_threshold)

                if above_pm is not None and mus_samples is not None:
                    # Save the results to the specified directory
                    above_pm_file = os.path.join(output_dir, 'above_pm.csv')
                    mus_samples_file = os.path.join(output_dir, 'mus_samples.csv')

                    above_pm.to_csv(above_pm_file, index=False)
                    mus_samples.to_csv(mus_samples_file, index=False)

                    st.success(f"Automatically selected items above PM saved to '{above_pm_file}'.")
                    st.success(f"MUS samples saved to '{mus_samples_file}'.")
