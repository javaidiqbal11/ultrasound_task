import scipy.io
import numpy as np
import matplotlib.pyplot as plt

# Load the .mat data file
data = scipy.io.loadmat('PA_data.mat')

# Extract RF data
rfData = data['rfData']  # Shape (4000, 128, 97)

# Choose a scanline index (e.g., middle scanline)
scanline_index = 50  # Change this to visualize different scanlines

# Extract RF signals for this scanline (all depth samples across 128 elements)
rf_scanline = rfData[:, :, scanline_index]  # Shape: (4000, 128)

# Apply log compression to enhance contrast
rf_log = np.log1p(np.abs(rf_scanline))  # log(1 + |signal|) to avoid log(0) issues

# Plot the improved RF data visualization
plt.figure(figsize=(10, 6))
plt.imshow(rf_log, cmap='gray', aspect='auto', extent=[0, 128, 4000, 0])
plt.xlabel('Transducer Element')
plt.ylabel('Depth Sample Index')
plt.title(f'Log-Compressed RF Data - Scanline {scanline_index}')
plt.colorbar(label='Log Amplitude')
plt.show()

