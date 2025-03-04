import numpy as np
import scipy.io
import matplotlib.pyplot as plt
from scipy.signal import hilbert
from scipy.ndimage import median_filter

def DASbeamform(rfData, tx_centers, focus, pos_z, pos_x, pos_trans, fs, sos):
    """
    Implements Delay-And-Sum (DAS) beamforming with a 32-element subaperture.

    Args:
        rfData (numpy.ndarray): Raw RF data (samples x elements x scanlines).  
        tx_centers (numpy.ndarray): Centered lateral position of each scanline.
        focus (float): Axial focus depth.
        pos_z (numpy.ndarray): Axial positions of image pixels.
        pos_x (numpy.ndarray): Lateral positions of image pixels.
        pos_trans (numpy.ndarray): Lateral positions of transducer elements.
        fs (float): Sampling frequency.
        sos (float): Speed of sound.

    Returns:
        numpy.ndarray: Beamformed image.
    """

    num_depths = len(pos_z)
    num_scanlines = len(pos_x)
    num_elements = 32  # Each scanline uses a 32-element subaperture
    num_transducers = len(pos_trans)  # Total transducer elements
    beamformed_image = np.zeros((num_depths, num_scanlines))
    dt = 1 / fs  # Sampling time interval

    pos_trans = pos_trans.flatten()  # Ensure pos_trans is a 1D array

    for scanline_idx in range(num_scanlines):
        tx_pos = tx_centers[scanline_idx]  # Lateral position of this scanline

        #  Correct 32-element subaperture selection
        mid_element = np.argmin(np.abs(pos_trans - tx_pos))  # Closest transducer
        start_idx = max(0, mid_element - 16)  # Start index (16 before mid)
        end_idx = min(start_idx + num_elements, num_transducers)  # Ensure within bounds

        #  Ensure valid subaperture selection
        if end_idx == num_transducers:
            start_idx = max(0, num_transducers - num_elements)

        subaperture_trans = pos_trans[start_idx:end_idx]  # 32-element subaperture

        #  Compute distances for transmission (Tx -> Focus)
        distance_tx = np.sqrt((subaperture_trans - tx_pos) ** 2 + focus ** 2)

        for depth_idx in range(num_depths):
            z = pos_z[depth_idx]  # Axial depth
            x = pos_x[scanline_idx]  # Lateral position

            #  Compute distances for reception (Pixel <- Rx)
            distance_rx = np.sqrt((subaperture_trans - x) ** 2 + z ** 2)

            #  Total distance (Tx -> Focus -> Rx)
            total_distance = distance_tx + distance_rx

            #  Convert to time delay & sample index
            time_delay = total_distance / sos
            sample_delay = np.round(time_delay / dt).astype(int)

            #  Ensure valid indices
            valid_indices = (sample_delay >= 0) & (sample_delay < rfData.shape[0])

            #  Sum only valid delayed signals
            if np.any(valid_indices):
                row_indices = sample_delay[valid_indices]
                col_indices = np.arange(start_idx, end_idx)[valid_indices]
                rf_values = rfData[row_indices, col_indices, scanline_idx]
                sum_signal = np.sum(rf_values)
            else:
                sum_signal = 0

            beamformed_image[depth_idx, scanline_idx] = sum_signal

    return beamformed_image

#  Load the ultrasound data
data = scipy.io.loadmat('PA_data.mat')

rfData = data['rfData']
tx_centers = data['tx_centers'].flatten()
focus = float(data['focus'])
pos_trans = data['pos_trans'].flatten()
fs = float(data['fs'])
sos = float(data['sos'])

#  Compute correct depth (pos_z) and lateral (pos_x) axes
Ns = rfData.shape[0]  # Number of depth samples
pos_z = np.linspace(0, Ns * (sos / (2 * fs)), Ns)  # Depth positions in meters
pos_x = tx_centers  # Lateral scanline positions

#  Run the beamforming function
beamformed_image = DASbeamform(rfData, tx_centers, focus, pos_z, pos_x, pos_trans, fs, sos)

#  Post-processing: Envelope Detection, Log Compression & Normalization
beamformed_image_env = np.abs(hilbert(beamformed_image, axis=0))  # Envelope detection
beamformed_image_log = np.log1p(beamformed_image_env)  # Log compression

#  Normalize to [0, 255]
beamformed_image_norm = (beamformed_image_log - np.min(beamformed_image_log)) / \
                        (np.max(beamformed_image_log) - np.min(beamformed_image_log))
beamformed_image_norm *= 255  # Scale to 0-255

#  Apply Median Filter for Speckle Noise Reduction
beamformed_image_smooth = median_filter(beamformed_image_norm, size=3)

#  Correct Image Width Scaling
lateral_extent = np.abs(pos_x[-1] - pos_x[0])  # Use scanline positions
depth_extent = pos_z.max() - pos_z.min()
aspect_ratio = depth_extent / lateral_extent  # Fix width issue

#  Plot the final B-mode ultrasound image
plt.figure(figsize=(5, 10))  # Adjust proportions
plt.imshow(beamformed_image_smooth, cmap='gray', aspect=aspect_ratio, 
           extent=[pos_x.min(), pos_x.max(), pos_z.max(), pos_z.min()])
plt.xlabel("Lateral Position (m)")
plt.ylabel("Depth (m)")
plt.title("Enhanced B-mode Ultrasound Image")
plt.colorbar(label="Intensity (0-255)")
plt.show()
