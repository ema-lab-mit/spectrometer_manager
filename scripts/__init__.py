import rgbdriverkit as rgbdriverkit
from rgbdriverkit.qseriesdriver import Qseries
from rgbdriverkit.spectrometer import SpectrometerStatus
from rgbdriverkit.calibratedspectrometer import SpectrumData
from rgbdriverkit.calibratedspectrometer import SpectrometerProcessing
import time
import epics

READ_TIME = 60  # s
EXPOSURE_TIME = 0.1  # s
PV_NAME = "SPECTROMETER:SPECTRUM"  # EPICS PV name for the spectrum data

def read_data(q):
    nm = q.get_wavelengths()
    # Set exposure time and start exposure
    print("Starting exposure with t=" + str(q.exposure_time) + "s")
    q.processing_steps = SpectrometerProcessing.AdjustOffset  # only adjust offset
    q.start_exposure(1)
    while not q.available_spectra:
        print("No spectrum available")
        time.sleep(0.1)
    spec = q.get_spectrum_data()  # Get spectrum with meta data
    return spec

def publish_spectrum_data(q, pv):
    """Reads data from the spectrometer and publishes it to the EPICS PV."""
    spectrum_data = read_data(q).Spectrum
    pv.put(spectrum_data)
    print("Published spectrum data to EPICS PV:", spectrum_data)