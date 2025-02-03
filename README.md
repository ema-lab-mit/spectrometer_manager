# Connecting to spectrometer using NIOLINK from windows

## Instructions
1. Install wsl
    Read the instructions to do so: https://learn.microsoft.com/en-us/windows/wsl/install
2. install miniconda on the wsl
    Read the instructions here: https://docs.conda.io/projects/conda/en/stable/user-guide/install/linux.html
3. Create a new env
    ```
    source ~/.bashrc
    conda init
    conda create -n envSpectr python=3.10
    ```
4. Attatch the com ports to th VM
    
    1. Install usbip (follow link instructions: https://learn.microsoft.com/en-us/windows/wsl/connect-usb)
    2. Identify the usb port where the device is connected with powershell (with admin privs)
        ```powershell
        usbipd list
        ```
    3. Bind the usb to share:
        ```powershell
        usbipd bind --busid 3-1
        usbipd attach --wsl --busid 3-1 
        ```
        And you should see something like:
        ```
        usbipd: info: Using WSL distribution 'Ubuntu' to attach; the device will be available in all WSL 2 distributions.
        usbipd: info: Using IP address 172.29.160.1 to reach the host.    
        ```
    4. Install the usb driver inside the Ubuntu:
        ```
        sudo apt install usbutils
        ```

        Now verify using usbip list that its shared within the WSL terminal:
        ```bash
        lsusb 
        ```

5. Install the driver from the attached terminal:
    ```bash
    cd spectrometer_manager
    python ./pyrgbdriverkit-0.3.7/setup.py install
    ```

### Common issues

- If windows updated, just pray and hope for the best.
- If you want to attach the USB-c back to the windows to use the software, do:
    ```
    usbipd unbind --busid 3-1
    ```
- To bind the usb-c again:
    ```
    usbipd bind --busid 3-1
    usbipd attach --wsl --busid 3-1 
    ```

