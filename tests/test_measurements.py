import rgbdriverkit as rgbdriverkit
from rgbdriverkit.qseriesdriver import Qseries
from rgbdriverkit.spectrometer import SpectrometerStatus
from rgbdriverkit.calibratedspectrometer import SpectrumData
from rgbdriverkit.calibratedspectrometer import SpectrometerProcessing
import time

dev = Qseries.search_devices()
if (dev != None):
    print("Device found.")
else:
    sys.exit("No device found.")
q = Qseries(dev[0]) # Create instance of first spectrometer found

print("Model name:", q.model_name)
print("Manufacturer:", q.manufacturer)
print("Serial Number:", q.serial_number)

q.open() # Open device connection

if __name__=="__main__":
    nm = q.get_wavelengths()
    # Set exposure time and start exposure
    q.exposure_time = 0.1 # in seconds
    print("Starting exposure with t=" + str(q.exposure_time) + "s")
    q.processing_steps = SpectrometerProcessing.AdjustOffset # only adjust offset
    q.start_exposure(1)
    print("Waiting for spectrum...")
    if not q.available_spectra:
        print("No spectrum available")
        time.sleep(0.1)
    spec = q.get_spectrum_data() # Get spectrum with meta data
    q.close()
    print(spec.Spectrum)
