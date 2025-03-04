import scipy.io
import numpy as np

# Load the .mat data file
data = scipy.io.loadmat('PA_data.mat')

# Inspect the keys in the file
for key in data.keys():
    if not key.startswith('__'):  # Ignore meta keys
        print(f"{key}: {type(data[key])}, shape: {np.shape(data[key])}")

# Inspect a small section of rfData
if 'rfData' in data:
    print("Sample rfData values:\n", data['rfData'][:5, :5, :5])  # Adjust based on actual dimensions
    