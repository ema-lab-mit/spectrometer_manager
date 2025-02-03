# powershell

################################
# Bind the USB device
usbipd bind --busid 3-1
usbipd attach --wsl --busid 3-1 

################################
# Launch the server from WSL
wsl /home/laserlab/miniconda3/envs/envSpectr/bin/python /home/laserlab/Programs/spectrometer_manager/src/pcaspy_server.py

################################
# Launch the server from windows
python C:\Users\admin\Desktop\SPECTROMETER\republisher.py