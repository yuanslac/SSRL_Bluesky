from ophyd.areadetector.detectors import EigerDetector
from ophyd import EpicsMotor
from ophyd import Device, Component as Cpt,  EpicsSignal
from ophyd.areadetector.cam import CamBase
from ophyd.areadetector.plugins import HDF5Plugin
from ophyd.areadetector.trigger_mixins import SingleTrigger

import warnings
import numpy as np

class MyEigerCam(CamBase):
    acquire = Cpt(EpicsSignal, 'Acquire') 
    acquire_time = Cpt(EpicsSignal, 'AcquireTime')  
    acquire_period = Cpt(EpicsSignal, 'AcquirePeriod') 
    threshold_energy = Cpt(EpicsSignal, 'ThresholdEnergy')  
    threshold_energy_RBV = Cpt(EpicsSignal, 'ThresholdEnergy_RBV')  
    photon_energy = Cpt(EpicsSignal, 'PhotonEnergy')  
    num_images = Cpt(EpicsSignal, 'NumImages')  
    trigger_mode = Cpt(EpicsSignal, 'TriggerMode')  
    trigger_exposure = Cpt(EpicsSignal, 'TriggerExposure')  
    manual_trigger = Cpt(EpicsSignal, 'ManualTrigger')  
    num_triggers = Cpt(EpicsSignal, 'NumTriggers')  
    num_queued_arrays = Cpt(EpicsSignal, 'NumQueuedArrays')  
    wait_for_plugins = Cpt(EpicsSignal, 'WaitForPlugins')  
    acquire_busy = Cpt(EpicsSignal, 'AcquireBusy')  
    status_message = Cpt(EpicsSignal, 'StatusMessage_RBV')  
    detector_state = Cpt(EpicsSignal, 'DetectorState_RBV')  
    bit_depth_image = Cpt(EpicsSignal, 'BitDepthImage_RBV')  
    dead_time = Cpt(EpicsSignal, 'DeadTime_RBV')  
    count_cutoff = Cpt(EpicsSignal, 'CountCutoff_RBV')  
    num_images_counter = Cpt(EpicsSignal, 'NumImagesCounter_RBV')  
    array_counter = Cpt(EpicsSignal, 'ArrayCounter')  
    array_rate = Cpt(EpicsSignal, 'ArrayRate_RBV')  
    driver_version = Cpt(EpicsSignal, 'DriverVersion_RBV')  
    roi_mode = Cpt(EpicsSignal, 'ROIMode')  

    image_mode = Cpt(EpicsSignal, 'ImageMode')  

    SequenceId = Cpt(EpicsSignal, "SequenceId") 

    FWNamePattern = Cpt(EpicsSignal, "FWNamePattern")
    FWNImagesPerFile = Cpt(EpicsSignal, "FWNImagesPerFile")

    def variable_list(self, skip_lazy=True):
        print("Valid settings and current values:")
        valid_attrs = []

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)

            for attr in dir(self):
                try:
                    signal = getattr(self, attr)
                except Exception as outer_e:
                    if not skip_lazy:
                        print(f" - {attr}: <Error initializing: {outer_e}>")
                    continue

                if isinstance(signal, EpicsSignal):
                    try:
                        value = signal.get(timeout=1.0)
                    except Exception as e:
                        value = f"<Error reading: {e}>"

                    # Decode ASCII arrays to strings if possible
                    if isinstance(value, (list, np.ndarray)):
                        try:
                            value = ''.join(chr(int(v)) for v in value if 0 < int(v) < 128)
                        except Exception:
                            pass

                    print(f" - {attr}: {value}")
                    valid_attrs.append(attr)

        return valid_attrs

    def update_variables(self, **kwargs):
    """Update EPICS signal values for valid EpicsSignal attributes."""
        for key, value in kwargs.items():
            try:
               signal = getattr(self, key)
              if isinstance(signal, EpicsSignal):
                try:
                    signal.put(value)
                    print(f"Set {key} = {value}")
                except Exception as e:
                    print(f"Failed to set {key}: {e}")
            else:
                print(f"'{key}' is not an EpicsSignal; cannot set value.")
            except AttributeError:
                print(f"'{key}' is not a valid attribute of the camera.")
            except Exception as outer_e:
                print(f"Error accessing '{key}': {outer_e}")


class Eiger_SSRL(SingleTrigger, EigerDetector):
    cam = Cpt(MyEigerCam, 'cam1:')
    hdf1 = Cpt(HDF5Plugin, 'HDF1:')


def MyEigerDetector(prefix="BL172:eiger4M:", *, name="eiger") -> Eiger_SSRL :
    det = Eiger_SSRL(prefix, name=name)

    det.read_attrs = ["hdf1"]
    det.hdf1.read_attrs = []

# Set directory where files will be saved
    det.hdf1.file_path.put("/data/eiger/")

# Set file naming pattern (e.g., run number with zero-padded digits)
    det.hdf1.file_template.put("%s%s_%6.6d.h5")  # Usually "%s%s_%6.6d.h5"

# Enable auto save and auto increment
    det.hdf1.auto_save.put(1)
    det.hdf1.auto_increment.put(1)

    det.configuration_attrs += ["cam.trigger_mode", "cam.num_images"]
    return det
