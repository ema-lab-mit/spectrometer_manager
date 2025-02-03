import os
import time
import threading
import numpy as np
# Import spectrometer modules
import rgbdriverkit as rgbdriverkit
from rgbdriverkit.qseriesdriver import Qseries
from rgbdriverkit.calibratedspectrometer import SpectrometerProcessing

# Import pcaspy modules
from pcaspy import SimpleServer, Driver

os.environ['EPICS_CA_ADDR_LIST'] = '172.29.160'
os.environ['EPICS_CA_AUTO_ADDR_LIST'] = 'NO'
os.environ["EPICS_CA_MAX_ARRAY_BYTES"] = "100000"

#os.environ['EPICS_CAS_INTF_ADDR_LIST'] = "172.29.160.1"


# EPICS PV prefix and database
prefix = "LaserLab:"
pvdb = {
    # This PV will hold the spectrum data as a string; adjust type if needed.
    "spectrum": {
        "type": "string"
    },
    # You can add more PVs (e.g. for status, error messages, etc.)
}

class SpectrometerDriver(Driver):
    def __init__(self, exposure_time=0.1, read_interval=0.5):
        super(SpectrometerDriver, self).__init__()
        self.exposure_time = exposure_time
        self.read_interval = read_interval
        self.spectrometer = None
        self.running = False
        self.initialize_spectrometer()

    def initialize_spectrometer(self):
        """Initialize the spectrometer and open the connection."""
        devices = Qseries.search_devices()
        if not devices:
            raise RuntimeError("No spectrometer device found.")
        # Use the first found device
        self.spectrometer = Qseries(devices[0])
        try:
            self.spectrometer.exposure_time = self.exposure_time
        except Exception as e:
            print("Could not set exposure time:", e)

        print("Spectrometer initialized:")
        print(f"Model: {self.spectrometer.model_name}")
        print(f"Manufacturer: {self.spectrometer.manufacturer}")
        print(f"Serial Number: {self.spectrometer.serial_number}")
        self.spectrometer.open()
        print("Spectrometer connection opened.")
        
    def peak_of_histogram(self, arr, bins=200):
        counts, bin_edges = np.histogram(arr, bins=bins)  # Compute histogram
        peak_idx = np.argmax(counts)  # Find index of max frequency bin
        peak_value = (bin_edges[peak_idx] + bin_edges[peak_idx + 1]) / 2  # Bin center

        return peak_value


    def read_loop(self):
        """Continuously read spectrum data and update the PV."""
        self.running = True
        while self.running:
            try:
                # Set processing step to adjust offset
                self.spectrometer.processing_steps = SpectrometerProcessing.AdjustOffset
                # Start an exposure (the argument here might represent number of accumulations)
                self.spectrometer.start_exposure(1)
                # Wait until a spectrum is available
                while not self.spectrometer.available_spectra:
                    # You might want to check for a timeout or add a small delay
                    time.sleep(0.1)
                # Retrieve spectrum data
                spec_data = self.spectrometer.get_spectrum_data().Spectrum
                peak = self.peak_of_histogram(np.array(spec_data))
                # Update the PV (setParam only updates the local copy; updatePVs() pushes to the server)
                self.setParam("spectrum", str(peak))
                self.updatePVs()
                print(f"Updated spectrum PV: {len(spec_data)}... Peak: {peak}")  # print first 50 chars for brevity
            except Exception as e:
                print("Error reading spectrometer data:", e)
            time.sleep(self.read_interval)

    def stop(self):
        """Stop the read loop and close the spectrometer."""
        self.running = False
        if self.spectrometer:
            self.spectrometer.close()
            print("Spectrometer connection closed.")

if __name__ == "__main__":
    # Create the pcaspy server and PVs
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    
    # Create an instance of the spectrometer driver
    driver = SpectrometerDriver(exposure_time=0.1, read_interval=0.5)
    
    # Start the background thread to read data continuously
    read_thread = threading.Thread(target=driver.read_loop)
    read_thread.daemon = True  # Allow thread to exit when main program exits
    read_thread.start()
    
    print("Spectrometer EPICS server started. Press Ctrl+C to exit.")
    try:
        # Process pcaspy requests; the argument is the polling period (in seconds)
        while True:
            server.process(0.1)
    except KeyboardInterrupt:
        print("Shutting down...")
        driver.stop()
