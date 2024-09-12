import pandas as pd
import os

# Define the file path directly
FILE_PATH = r"C:\Users\user\Desktop\MScFE\Samplefile.csv"
OUTPUT_DIR = r"C:\Users\user\Desktop\MScFE"  # Directory to save output files

# Function to read the CSV file
def read_csv_file():
    try:
        df = pd.read_csv(FILE_PATH)
        print("File loaded successfully.")
        return df
    except FileNotFoundError:
        print("File not found. Please check the path and try again.")
        return None
    except PermissionError:
        print("Permission denied. Please check your file permissions and try again.")
        return None
    except OSError as e:
        print(f"OS error occurred: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# Function to perform MUS sampling
def mus_sampling(df, amount_column, performance_materiality, trivial_threshold):
    # Ensure the specified 'amount' column exists in the file
    if amount_column not in df.columns:
        print(f"Error: The file must contain a column named '{amount_column}'.")
        return None, None

    # Convert the 'amount' column to numeric, coerce errors to NaN, and drop rows with NaN
    df[amount_column] = pd.to_numeric(df[amount_column], errors='coerce')
    df = df.dropna(subset=[amount_column])

    # Step 1: Automatically include all items above the Performance Materiality threshold
    above_pm = df[df[amount_column] > performance_materiality]
    print(f"\nAutomatically selected {len(above_pm)} items above the Performance Materiality threshold.")

    # Step 2: Filter the remaining population for MUS sampling (below PM threshold)
    remaining_population = df[df[amount_column] <= performance_materiality]

    # Step 3: Perform MUS sampling for remaining population based on Clearly Trivial threshold
    mus_samples = remaining_population[remaining_population[amount_column] >= trivial_threshold]

    return above_pm, mus_samples

# Main function
def main():
    # Get the CSV file from the defined path
    df = read_csv_file()
    if df is None:
        return

    # Ask the user to input the name of the 'amount' column
    amount_column = input("Enter the name of the column that contains the amounts: ")

    # Get Performance Materiality and Clearly Trivial thresholds from the user
    try:
        performance_materiality = float(input("Enter the Performance Materiality amount: "))
        trivial_threshold = float(input("Enter the Clearly Trivial threshold amount: "))
    except ValueError:
        print("Please enter valid numeric values for Performance Materiality and Clearly Trivial thresholds.")
        return

    # Perform MUS sampling
    above_pm, mus_samples = mus_sampling(df, amount_column, performance_materiality, trivial_threshold)

    if above_pm is None or mus_samples is None:
        print("Error: Sampling could not be performed due to missing or incorrect data.")
        return

    # Save the automatically selected items (above PM) to a separate file
    if not above_pm.empty:
        above_pm_file = os.path.join(OUTPUT_DIR, 'above_pm.csv')
        above_pm.to_csv(above_pm_file, index=False)
        print(f"Automatically selected items above PM saved to '{above_pm_file}'.")

    # Save the MUS-selected samples from the remaining population
    if mus_samples is not None and not mus_samples.empty:
        mus_samples_file = os.path.join(OUTPUT_DIR, 'mus_samples.csv')
        mus_samples.to_csv(mus_samples_file, index=False)
        print(f"MUS samples saved to '{mus_samples_file}'.")

# Run the program
if __name__ == "__main__":
    main()
