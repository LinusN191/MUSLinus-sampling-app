import streamlit as st
import pandas as pd
import os

def mus_sampling(df, performance_materiality, trivial_threshold):
    # Automatically include all items above Performance Materiality
    above_pm = df[df['amount'] > performance_materiality]
    print(f"\nAutomatically selected {len(above_pm)} items above the Performance Materiality threshold.")

    # Filter the remaining population for MUS sampling
    remaining_df = df[df['amount'] <= performance_materiality]
    total_amount = remaining_df['amount'].sum()
    sample_size = int(total_amount / performance_materiality)
    mus_samples = remaining_df.sample(n=sample_size)

    return above_pm, mus_samples

st.title("MUS Sampling App")

# File upload
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Load data
    if uploaded_file.name.endswith('csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.write("File loaded successfully.")

    # Get user inputs
    performance_materiality = st.number_input("Performance Materiality", min_value=0.0)
    trivial_threshold = st.number_input("Clearly Trivial Threshold", min_value=0.0)

    if st.button("Run Sampling"):
        if 'amount' not in df.columns:
            st.error("The file must contain an 'amount' column.")
        else:
            above_pm, mus_samples = mus_sampling(df, performance_materiality, trivial_threshold)

            if above_pm.empty:
                st.write("No items above Performance Materiality threshold.")
            else:
                st.write(f"Automatically selected {len(above_pm)} items above the Performance Materiality threshold.")
                
                st.write("Sampled Items:")
                st.write(mus_samples)

                # Provide download links
                st.download_button(
                    label="Download Items Above PM",
                    data=above_pm.to_csv(index=False),
                    file_name='above_pm.csv',
                    mime='text/csv'
                )
                st.download_button(
                    label="Download MUS Samples",
                    data=mus_samples.to_csv(index=False),
                    file_name='mus_samples.csv',
                    mime='text/csv'
                )
else:
    st.write("Please upload a file.")

