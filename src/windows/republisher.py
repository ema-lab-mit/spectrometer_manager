import os
import time
import threading
import epics
from pcaspy import SimpleServer, Driver
os.environ["EPICS_CA_MAX_ARRAY_BYTES"] = "100000"
time.sleep(1)

# Define source and destination PVs
WSL2_PV_NAME = "LaserLab:spectrum"  # Original PV in WSL2
PREFIX = "LaserLab:"  # New prefix for network-accessible PV
PVDB = {
    "spectrum_peak": {
        "type":"string"
    }
}

class RelayDriver(Driver):
    def __init__(self, read_interval=0.5):
        super().__init__()
        self.read_interval = read_interval
        self.running = False

    def start_relay(self):
        """Continuously fetch data from WSL2 and update the new PV."""
        self.running = True
        while self.running:
            try:
                spec_data = epics.caget(WSL2_PV_NAME)  # Get data from WSL2
                if spec_data is not None:
                    self.setParam("spectrum_peak", spec_data)
                    self.updatePVs()
                    print("Updated", spec_data)
                else:
                    print("Failed to fetch spectrum from WSL2")
            except Exception as e:
                print("Error fetching data from WSL2:", e)
            time.sleep(self.read_interval)

    def stop(self):
        """Stop the relay loop."""
        self.running = False

if __name__ == "__main__":
    # Create an EPICS server on Windows that is visible to the network
    server = SimpleServer()
    server.createPV(PREFIX, PVDB)

    # Start the relay
    driver = RelayDriver(read_interval=0.5)
    relay_thread = threading.Thread(target=driver.start_relay)
    relay_thread.daemon = True  # Exit when the main process exits
    relay_thread.start()

    print("EPICS Relay started. Press Ctrl+C to exit.")
    try:
        while True:
            server.process(0.1)
    except KeyboardInterrupt:
        print("Shutting down...")
        driver.stop()
