from Devices.Detectors.Counters import BeamlineCounters
from ophyd import Device, Component as Cpt, EpicsSignal

def init_BL172_counters(
    counters_prefix='BL17-2:'
):

    # Instantiate and configure Counters and Photodiode
    beamline_counters = BeamlineCounters(prefix=counters_prefix, name='beamline_counters')

    print(f"Photodiode   ", beamline_counters.beamstop_pd.get())
    print(f"i0           ", beamline_counters.i0.get())
    print(f"i1           ", beamline_counters.i1.get())
    print(f"i2           ", beamline_counters.i2.get())

    print(f"Counters and Photodiode initialized successfully.")
    return beamline_counters 

