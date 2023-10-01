import pandas as pd

# Read data from the CSV file into a DataFrame
df = pd.read_csv('hatebase_data.csv')

# Extract the numeric part from the 'sightings' column
# Extract the numeric part from the 'sightings' column (handling both comma and dot as separators)
df['sightings'] = df['sightings'].str.replace(',', '').str.extract('(\d+)', expand=False)

# Convert the 'sightings' column to numeric type (float)
df['sightings'] = pd.to_numeric(df['sightings'], errors='coerce')

# Remove rows with NaN values in the 'sightings' column
df = df.dropna(subset=['sightings'])

df['term'] = df['term'].str.replace(r'\([^)]*\)', '', regex=True)


# Filter rows where offense_level is "Highly offensive"
filtered_df = df[(df['offense_level'] == 'Extremely offensive') | (df['offense_level'] == 'Highly offensive')]

# Display the filtered DataFrame
print(filtered_df)
filtered_df.to_csv('cleaned_data.csv', index=False)
