%% MATLAB file
% Programming Assignment for BME 581/ECE 493/ECE 700
% Ultrasound in Medicine and Biology
% ver. 1.0  (Feb 2025 -- by Di Xiao)

load('PA_data.mat')

%% setting imaging parameters
Ns = size(rfData,1);

pos_z = sos*(0:Ns-1)/(2*fs);
pos_x = tx_centers;

%% visualize RF data
figure
for tx_idx = 1:size(rfData,3)
    imagesc(pos_x,pos_z,log(abs(hilbert(rfData(:,:,tx_idx)))))
    colormap gray
    title(['Tx = ' num2str(tx_idx)])
    drawnow
    pause(0.05)
end

%% run delay-and-sum beamformer
img = DASbeamform(rfData,tx_centers,focus,pos_z,pos_x,pos_trans,fs,sos);

log_img = log_scale_and_demodulate(img);

display_image(pos_z, pos_x, log_img)

%% helper functions

%%%%%%%%%%%%%%% FILL OUT THIS FUNCTION %%%%%%%%%%%%%%%%%%
function img = DASbeamform(rfData,tx_centers,focus,pos_z,pos_x,pos_trans,fs,sos)
    % rfData - 4000x128x97 (samples x array elements x scanlines) ultrasound data
    % tx_centers - 1x97 (1 x scanlines) center of scanline (m)
    % focus - 1x1 scalar transmit focus (m)
    % pos_z - 1x4000 (1 x samples) axial/depth positions (m)
    % pos_x - 1x97 (1 x scanlines) lateral positions (m)
    % pos_trans - 1x128 (1 x array elements) (m)
    % fs - 1x1 scalar sampling frequency (Hz)
    % sos - 1x1 scalar speed of sound (m/s)
    img = zeros(length(pos_z),length(pos_x));
    
    
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function log_img = log_scale_and_demodulate(img)
    log_img = 20*log10(abs(hilbert(img))+1e-8);
end

function display_image(pos_z, pos_x, log_img)
    dynamic_range = 60;
    img_max = max(log_img(:));

    figure
    imagesc(pos_x,pos_z,log_img,[img_max-dynamic_range,img_max])
    colormap gray
    axis equal tight
end