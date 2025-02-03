from src.server import SpectrometerEpicsServer

if __name__ == "__main__":
    # Configuration
    PV_NAME = "SPECTROMETER:SPECTRUM"  # EPICS PV name
    EXPOSURE_TIME = 0.1  # Exposure time in seconds
    READ_INTERVAL = 0.5  # Time interval between reads in seconds
    RUN_TIME = 6_000_000  # Total run time in seconds

    # Create and run the EPICS server
    try:
        server = SpectrometerEpicsServer(
            pv_name=PV_NAME,
            exposure_time=EXPOSURE_TIME,
            read_interval=READ_INTERVAL
        )
        server.initialize_spectrometer()
        server.initialize_epics_pv()
        server.run(run_time=RUN_TIME)
    except Exception as e:
        print(f"An error occurred: {e}")