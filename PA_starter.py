# # -*- coding: utf-8 -*-
# """
# Programming Assignment for BME 581/ECE 493/ECE 700
# Ultrasound in Medicine and Biology
# ver. 1.0  (Feb 2025 -- by Di Xiao)
# """

# import numpy as np
# from scipy.io import loadmat
# from scipy.signal import hilbert
# from matplotlib import pyplot as plt

# mat_dict = loadmat('PA_data.mat')

# focus = mat_dict['focus']
# fs = mat_dict['fs']
# pos_trans = mat_dict['pos_trans']
# rfData = mat_dict['rfData']
# sos = mat_dict['sos']
# tx_centers = mat_dict['tx_centers']


# # setting imaging parameters
# Ns = np.shape(rfData)[0]

# pos_z = sos*np.arange(Ns)/(2*fs)
# pos_x = tx_centers

# # visualize RF data
# fig = plt.figure()
# ax = plt.gca()
# img_draw = ax.imshow(np.log(np.abs(hilbert(rfData[:,:,0],axis=0))),cmap='gray',extent=(np.amin(pos_x),np.amax(pos_x),np.amax(pos_z),np.amin(pos_z)))
# for tx_idx in range(np.shape(rfData)[2]):
#     img_draw.set_data(np.log(np.abs(hilbert(rfData[:,:,tx_idx],axis=0))))
#     plt.title('Tx  = ' + str(tx_idx))
#     plt.draw()
#     plt.pause(0.05)
    

# # define functions

# ################### FILL OUT THIS FUNCTION ############################
# def DASbeamform(rfData,tx_centers,focus,pos_z,pos_x,pos_trans,fs,sos):
#     # rfData - 4000x128x97 (samples x array elements x scanlines) ultrasound data
#     # tx_centers - 1x97 (1 x scanlines) center of scanline (m)
#     # focus - 1x1 scalar transmit focus (m)
#     # pos_z - 1x4000 (1 x samples) axial/depth positions (m)
#     # pos_x - 1x97 (1 x scanlines) lateral positions (m)
#     # pos_trans - 1x128 (1 x array elements) (m)
#     # fs - 1x1 scalar sampling frequency (Hz)
#     # sos - 1x1 scalar speed of sound (m/s)
#     img = np.zeros((pos_z.size,pos_x.size))
#     return img


# #######################################################################

# def log_scale_and_demodulate(img):
#     return 20*np.log10(np.abs(hilbert(img,axis=0))+1e-8);

# def display_image(pos_z,pos_x,log_img):
#     dynamic_range = 60
#     img_max = np.amax(log_img)
    
#     plt.figure()
#     plt.imshow(log_img ,cmap='gray',extent=(np.amin(pos_x),np.amax(pos_x),np.amax(pos_z),np.amin(pos_z)),vmin = img_max-dynamic_range, vmax = img_max)

# # run test script
# img = DASbeamform(rfData,tx_centers,focus,pos_z,pos_x,pos_trans,fs,sos);

# log_img = log_scale_and_demodulate(img);

# display_image(pos_z, pos_x, log_img)




##########################################UPDATED#############################################################################


# -*- coding: utf-8 -*-
"""
Programming Assignment for BME 581/ECE 493/ECE 700
Ultrasound in Medicine and Biology
Updated DAS Beamforming Implementation
"""

import numpy as np
from scipy.io import loadmat
from scipy.signal import hilbert
import matplotlib.pyplot as plt

# Load data
mat_dict = loadmat('PA_data.mat')

focus = float(mat_dict['focus'])
fs = float(mat_dict['fs'])
pos_trans = mat_dict['pos_trans'].flatten()
rfData = mat_dict['rfData']
sos = float(mat_dict['sos'])
tx_centers = mat_dict['tx_centers'].flatten()

# Define imaging parameters
Ns = rfData.shape[0]  # Number of depth samples
num_scanlines = len(tx_centers)
num_elements = 32  # Subaperture size
num_transducers = len(pos_trans)

pos_z = np.linspace(0, Ns * (sos / (2 * fs)), Ns)  # Axial depth positions (m)
pos_x = tx_centers  # Lateral scanline positions

def DASbeamform(rfData, tx_centers, focus, pos_z, pos_x, pos_trans, fs, sos):
    """
    Implements Delay-And-Sum (DAS) beamforming.
    """
    num_depths = len(pos_z)
    beamformed_image = np.zeros((num_depths, num_scanlines))
    dt = 1 / fs  # Sampling interval

    for scanline_idx in range(num_scanlines):
        tx_pos = tx_centers[scanline_idx]  # Scanline lateral position
        mid_element = np.argmin(np.abs(pos_trans - tx_pos))  # Closest element
        start_idx = max(0, mid_element - 16)
        end_idx = min(start_idx + num_elements, num_transducers)
        subaperture_trans = pos_trans[start_idx:end_idx]

        distance_tx = np.sqrt((subaperture_trans - tx_pos) ** 2 + focus ** 2)
        
        for depth_idx in range(num_depths):
            z = pos_z[depth_idx]
            x = pos_x[scanline_idx]
            distance_rx = np.sqrt((subaperture_trans - x) ** 2 + z ** 2)
            total_distance = distance_tx + distance_rx
            time_delay = total_distance / sos
            sample_delay = np.round(time_delay / dt).astype(int)
            valid_indices = (sample_delay >= 0) & (sample_delay < rfData.shape[0])
            if np.any(valid_indices):
                row_indices = sample_delay[valid_indices]
                col_indices = np.arange(start_idx, end_idx)[valid_indices]
                sum_signal = np.sum(rfData[row_indices, col_indices, scanline_idx])
            else:
                sum_signal = 0
            beamformed_image[depth_idx, scanline_idx] = sum_signal

    return beamformed_image

# Run beamforming
img = DASbeamform(rfData, tx_centers, focus, pos_z, pos_x, pos_trans, fs, sos)

# Post-processing
def log_scale_and_demodulate(img):
    return 20 * np.log10(np.abs(hilbert(img, axis=0)) + 1e-8)

def display_image(pos_z, pos_x, log_img):
    dynamic_range = 60
    img_max = np.amax(log_img)
    plt.figure()
    plt.imshow(log_img, cmap='gray', extent=(np.amin(pos_x), np.amax(pos_x), np.amax(pos_z), np.amin(pos_z)),
               vmin=img_max - dynamic_range, vmax=img_max)
    plt.xlabel('Lateral Position (m)')
    plt.ylabel('Depth (m)')
    plt.title('Beamformed B-mode Ultrasound Image')
    plt.colorbar(label='Intensity (dB)')
    plt.show()

log_img = log_scale_and_demodulate(img)
display_image(pos_z, pos_x, log_img)
