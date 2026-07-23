import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed to ensure reproducible results
np.random.seed(42)
random.seed(42)

# Create 5000 records of data
n_records = 5000

# Basic fields
data = {
    'id': range(1, n_records + 1),
    'collector': [f'Surveyor{random.choice(["A", "B", "C", "D", "E"])}' for _ in range(n_records)],
    'location': [random.choice(['Practice Range A', 'Practice Range B', 'Private Club C', 'Public Course D', 'Resort Course E']) for _ in range(n_records)],
    'timestamp': [(datetime(2023, 10, 26, 10, 0, 0) + timedelta(minutes=i)).strftime('%Y-%m-%d %H:%M:%S') for i in range(n_records)]
}

# Add questionnaire fields
# Gender (single choice)
data['gender'] = [random.choice(['Male', 'Female']) for _ in range(n_records)]

# Age group (single choice)
data['age_group'] = [random.choice(['18-25', '26-35', '36-45', '46-55', '56-65', '65+']) for _ in range(n_records)]

# Occupation (open text)
occupations = ['Business Manager', 'Technical Professional', 'Civil Servant', 'Teacher', 'Doctor', 'Lawyer', 'Engineer', 'Sales Person', 'Freelancer', 'Retiree']
data['occupation'] = [random.choice(occupations) for _ in range(n_records)]

# Venue type preference (multiple choice, comma-separated)
venue_types = ['Public Course', 'Private Club', 'Practice Range', 'Resort Course']
data['venue_preference'] = [','.join(random.sample(venue_types, random.randint(1, 3))) for _ in range(n_records)]

# Scale questions (1-5 points)
data['price_influence'] = np.random.randint(1, 6, n_records)  # Price influence level
data['satisfaction'] = np.random.randint(1, 6, n_records)     # Satisfaction level
data['amenities_importance'] = np.random.randint(1, 6, n_records)  # Amenities importance
data['service_quality'] = np.random.randint(1, 6, n_records)  # Service quality rating
data['value_for_money'] = np.random.randint(1, 6, n_records)  # Value for money rating

# Visit frequency
data['visit_frequency'] = [random.choice(['Once a week', '2-3 times per month', 'Once a month', 'Once per quarter', 'Several times per year']) for _ in range(n_records)]

# Annual spending
data['annual_spending'] = np.random.randint(5000, 50000, n_records)

# Recommendation score (1-10 points)
data['recommendation_score'] = np.random.randint(1, 11, n_records)

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV file
df.to_csv('evaluation/large_data.csv', index=False, encoding='utf-8')
print(f"Created large data file with {len(df)} records: evaluation/large_data.csv")
print(f"File size: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
print("Data fields:", list(df.columns))