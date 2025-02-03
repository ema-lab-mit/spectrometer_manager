import rgbdriverkit as rgbdriverkit
from rgbdriverkit.qseriesdriver import Qseries
from rgbdriverkit.calibratedspectrometer import SpectrometerProcessing
import time
import epics
import os
import os
import epics
os.environ['EPICS_CA_ADDR_LIST'] = '172.29.160.1 127.0.0.1'
os.environ['EPICS_CA_AUTO_ADDR_LIST'] = 'NO'

class SpectrometerEpicsServer:
    """
    A professional EPICS server for publishing spectrometer data to the network.
    """

    def __init__(self, pv_name="SPECTROMETER:SPECTRUM", exposure_time=0.1, read_interval=0.5):
        """
        Initialize the spectrometer EPICS server.

        Args:
            pv_name (str): Name of the EPICS PV to publish spectrum data.
            exposure_time (float): Exposure time for the spectrometer in seconds.
            read_interval (float): Time interval between data reads in seconds.
        """
        self.pv_name = pv_name
        self.exposure_time = exposure_time
        self.read_interval = read_interval
        self.spectrometer = None
        self.spectrum_pv = None
        os.system("")

    def initialize_spectrometer(self):
        """
        Initialize the spectrometer device.
        """
        devices = Qseries.search_devices()
        if not devices:
            raise RuntimeError("No spectrometer device found.")
        self.spectrometer = Qseries(devices[0])  # Use the first device found
        try:
            self.spectrometer.exposure_time = self.exposure_time
        except Exception as e:
            print("Could not set exposure time")

        print("Spectrometer initialized:")
        print(f"Model: {self.spectrometer.model_name}")
        print(f"Manufacturer: {self.spectrometer.manufacturer}")
        print(f"Serial Number: {self.spectrometer.serial_number}")

    def initialize_epics_pv(self):
        """
        Initialize the EPICS PV for publishing spectrum data.
        """
        self.spectrum_pv = epics.PV(self.pv_name)
        print(f"EPICS PV '{self.pv_name}' initialized.")

    def read_spectrum_data(self):
        """
        Read spectrum data from the spectrometer.

        Returns:
            SpectrumData: The spectrum data with metadata.
        """
        self.spectrometer.processing_steps = SpectrometerProcessing.AdjustOffset  # Only adjust offset
        self.spectrometer.start_exposure(1)
        while not self.spectrometer.available_spectra:
            print("Waiting for spectrum data...")
            time.sleep(0.1)
        return self.spectrometer.get_spectrum_data()

    def publish_spectrum_data(self):
        """
        Read and publish spectrum data to the EPICS PV.
        """
        spectrum_data = self.read_spectrum_data().Spectrum
        #self.spectrum_pv.caput(spectrum_data)
        epics.caput(self.pv_name, spectrum_data)
        print(f"Published spectrum data to EPICS PV '{self.pv_name}'")

    def run(self, run_time=60):
        """
        Run the EPICS server for a specified duration.

        Args:
            run_time (float): Total time to run the server in seconds.
        """
        if not self.spectrometer:
            raise RuntimeError("Spectrometer not initialized.")
        if not self.spectrum_pv:
            raise RuntimeError("EPICS PV not initialized.")

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