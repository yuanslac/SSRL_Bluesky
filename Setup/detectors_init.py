from bluesky import RunEngine, plan_stubs as bps
from bluesky.preprocessors import run_decorator
from Eiger import MyEigerDetector
from ophyd import Device, Component as Cpt, EpicsSignal
from ophyd.areadetector.cam import CamBase
from ophyd.areadetector.plugins import HDF5Plugin
from ophyd.areadetector.trigger_mixins import SingleTrigger
import time

def init_BL172_detectors(
    eiger_prefix='BL172:eiger4M:'
):

    # Instantiate and configure Eiger detector
    eiger = MyEigerDetector(prefix=eiger_prefix, name='eiger')
    eiger.wait_for_connection(timeout=1)

    print(f"Eiger detector initialized successfully.")
    return eiger


