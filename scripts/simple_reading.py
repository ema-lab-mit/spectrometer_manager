import rgbdriverkit as rgbdriverkit
from rgbdriverkit.qseriesdriver import Qseries
from rgbdriverkit.spectrometer import SpectrometerStatus
from rgbdriverkit.calibratedspectrometer import SpectrumData
from rgbdriverkit.calibratedspectrometer import SpectrometerProcessing
import time

READ_TIME = 60 # s
EXPOSURE_TIME = 0.1 # S

def read_data(q):
    nm = q.get_wavelengths()
    # Set exposure time and start exposure
    print("Starting exposure with t=" + str(q.exposure_time) + "s")
    q.processing_steps = SpectrometerProcessing.AdjustOffset # only adjust offset
    q.start_exposure(1)
    while not q.available_spectra:
        print("No spectrum available")
        time.sleep(0.1)
    spec = q.get_spectrum_data() # Get spectrum with meta data
    return spec


if __name__=="__main__":
    dev = Qseries.search_devices()
    if (dev != None):
        print("Device found.")
    else:
        sys.exit("No device found.")
    q = Qseries(dev[0]) # Create instance of first spectrometer found

    print("Model name:", q.model_name)
    print("Manufacturer:", q.manufacturer)
    print("Serial Number:", q.serial_number)
    # q.exposure_time = 0.1 # in seconds
    
    time_start = time.time()
    q.open() # Open device connection
    while True:
        print(read_data(q).Temperature)
        
        time.sleep(0.5)
        if time.time() - time_start >READ_TIME:
            break
    q.close()
