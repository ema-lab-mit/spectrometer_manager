import rgbdriverkit as rgbdriverkit
from rgbdriverkit.qseriesdriver import Qseries
from rgbdriverkit.calibratedspectrometer import SpectrometerProcessing
import time
import json
import os

# Set EPICS env variables if you need them later
os.environ['EPICS_CA_ADDR_LIST'] = '172.29.160.1 127.0.0.1'
os.environ['EPICS_CA_AUTO_ADDR_LIST'] = 'NO'

SHARED_FILE_PATH = "/home/laserlab/TMP/spectrum_data.json"

def write_spectrum_data_to_file(data, filepath=SHARED_FILE_PATH):
    """Atomically write spectrum data (as JSON) to a shared file."""
    temp_filepath = filepath + '.tmp'
    try:
        with open(temp_filepath, 'w') as f:
            json.dump(data, f)
        # Atomically replace the target file with the temporary file.
        os.replace(temp_filepath, filepath)
    except Exception as e:
        print(f"Error writing file: {e}")

class SpectrometerEpicsServer:
    """
    A hacked EPICS server: it writes spectrometer data to a file shared with Windows.
    """

    def __init__(self, exposure_time=0.1, read_interval=0.5):
        self.exposure_time = exposure_time
        self.read_interval = read_interval
        self.spectrometer = None

    def initialize_spectrometer(self):
        devices = Qseries.search_devices()
        if not devices:
            raise RuntimeError("No spectrometer device found.")
        self.spectrometer = Qseries(devices[0])  # Use the first device found
        try:
            self.spectrometer.exposure_time = self.exposure_time
        except Exception as e:
            print("Could not set exposure time:", e)
        print("Spectrometer initialized:")
        print(f"Model: {self.spectrometer.model_name}")
        print(f"Manufacturer: {self.spectrometer.manufacturer}")
        print(f"Serial Number: {self.spectrometer.serial_number}")

    def read_spectrum_data(self):
        """
        Read spectrum data from the spectrometer.
        Returns the raw spectrum data (e.g., list of values).
        """
        # Only adjust offset in the processing steps.
        self.spectrometer.processing_steps = SpectrometerProcessing.AdjustOffset  
        self.spectrometer.start_exposure(1)
        while not self.spectrometer.available_spectra:
            print("Waiting for spectrum data...")
            time.sleep(0.1)
        return self.spectrometer.get_spectrum_data().Spectrum

    def publish_spectrum_data(self):
        """
        Read spectrum data and write it atomically to the shared file.
        """
        spectrum_data = self.read_spectrum_data()
        write_spectrum_data_to_file(spectrum_data)
        print("Wrote spectrum data to shared file.")

    def run(self, run_time=60):
        """
        Run for a specified duration.
        """
        if not self.spectrometer:
            raise RuntimeError("Spectrometer not initialized.")
        self.spectrometer.open()
        print("Spectrometer connection opened.")
        start_time = time.time()
        try:
            while time.time() - start_time < run_time:
                self.publish_spectrum_data()
                time.sleep(self.read_interval)
        finally:
            self.spectrometer.close()
            print("Spectrometer connection closed.")

if __name__ == "__main__":
    server = SpectrometerEpicsServer(exposure_time=0.1, read_interval=0.5)
    server.initialize_spectrometer()
    server.run(run_time=60)
