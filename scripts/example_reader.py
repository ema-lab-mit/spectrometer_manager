import epics
import time

# Configuration
PV_NAME = "SPECTROMETER:SPECTRUM"  # EPICS PV name to read from
POLL_INTERVAL = 1.0  # Time interval between reads in seconds

def read_spectrum_data(pv_name):
    """
    Read spectrum data from the specified EPICS PV.

    Args:
        pv_name (str): Name of the EPICS PV to read from.

    Returns:
        list: The spectrum data as a list of values.
    """
    pv = epics.PV(pv_name)
    if not pv.connect():
        raise RuntimeError(f"Failed to connect to EPICS PV '{pv_name}'.")
    return pv.get()

def monitor_spectrum_data(pv_name, poll_interval=1.0):
    """
    Continuously monitor and print spectrum data from the EPICS PV.

    Args:
        pv_name (str): Name of the EPICS PV to monitor.
        poll_interval (float): Time interval between reads in seconds.
    """
    print(f"Monitoring EPICS PV '{pv_name}'...")
    try:
        while True:
            spectrum_data = read_spectrum_data(pv_name)
            if spectrum_data is not None:
                print(f"Spectrum data: {spectrum_data}")
            else:
                print("No data available.")
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        print("Monitoring stopped.")

if __name__ == "__main__":
    monitor_spectrum_data(PV_NAME, POLL_INTERVAL)