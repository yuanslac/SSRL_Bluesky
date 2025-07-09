from bluesky import RunEngine, plan_stubs as bps
from bluesky.preprocessors import run_decorator
from Eiger import MyEigerDetector
from ophyd import Device, Component as Cpt, EpicsSignal
from ophyd.areadetector.cam import CamBase
from ophyd.areadetector.plugins import HDF5Plugin
from ophyd.areadetector.trigger_mixins import SingleTrigger
import time

def get_eiger_config(eiger):
    print(f"\nname_pattern = {''.join(chr(c) for c in eiger.cam.FWNamePattern.get() if c != 0)}")
    print(f"data_directory = {eiger.hdf1.file_path.get()}")

    print(f"\nacquire_time = {eiger.cam.acquire_time.get()}")
    print(f"frame_time = {eiger.cam.acquire_period.get()}")

    print(f"\nimages = {eiger.cam.num_images.get()}")
    print(f"images_per_file = {eiger.cam.FWNImagesPerFile.get()}")

    print(f"\ntrigger = {eiger.cam.trigger_mode.get()}")
    print(f"ntriggers = {eiger.cam.num_triggers.get()}")

def eiger_set_fname(eiger, fname):
    eiger.cam.FWNamePattern.put(fname)
    return fname

def eiger_set_dir(eiger, dir_path):
    if dir_path is None:
        dir_path = eiger.hdf1.file_path.get()
    eiger.hdf1.file_path.put(dir_path)
    return dir_path

def eiger_set_frametime(eiger, frametime):
    eiger.cam.acquire_period.put(frametime)
    return frametime

def eiger_set_acqtime(eiger, acqtime):
    if acqtime is None or acqtime == 0:
        acqtime = eiger.cam.acquire_time.get()
    eiger.cam.acquire_time.put(acqtime)
    return acqtime

def eiger_set_nimages(eiger, nimages):
    if nimages is None or nimages == 0:
        nimages = eiger.cam.num_images.get()
    eiger.cam.num_images.put(nimages)
    return nimages

def eiger_set_nimages_per_file(eiger, nimages_per_file):
    if nimages_per_file is None or nimages_per_file == 0:
        nimages_per_file = 1000
    eiger.cam.FWNImagesPerFile.put(nimages_per_file)
    return nimages_per_file

def eiger_set_trigger_mode(eiger, trigger_mode):
    eiger.cam.trigger_mode.put(trigger_mode)
    return trigger_mode

def eiger_set_ntriggers(eiger, ntriggers):
    if ntriggers is None or ntriggers == 0:
        ntriggers = 1
    eiger.cam.num_triggers.put(ntriggers)
    return ntriggers

def eiger_set_image_mode(eiger, image_mode):
    eiger.cam.image_mode.put(image_mode)
    return image_mode

def set_int_trig(
    eiger: MyEigerDetector,
    fname: str,
    dir_path: str,
    acqtime: float,
    frametime: float,
    nimagesperfile: int,
    nimages: int,
    savemode: int = None
):
    # Set file name and data directory
    eiger.cam.stage_sigs["FWNamePattern"] = [ord(c) for c in fname] + [0]
    eiger.hdf1.stage_sigs["file_path"] = dir_path

    # Set acquisition parameters
    eiger.cam.stage_sigs["acquire_time"] = acqtime
    eiger.cam.stage_sigs["acquire_period"] = frametime
    eiger.cam.stage_sigs["num_images"] = nimages
    eiger.cam.stage_sigs["trigger_mode"] = 0  # Internal software trigger
    eiger.cam.stage_sigs["image_mode"] = 1  # Multiple
    eiger.cam.stage_sigs["num_triggers"] = 1
    eiger.cam.stage_sigs["array_callbacks"] = 1
    eiger.cam.stage_sigs["FWNImagesPerFile"] = nimagesperfile
    eiger.cam.stage_sigs["acquire"] = 1

    eiger.hdf1.stage_sigs["compression"] = "LZ4"
    eiger.hdf1.stage_sigs["file_write_mode"] = 1 # "Capture"
    eiger.hdf1.stage_sigs["file_template"] = "%s%s_%6.6d.h5"
    eiger.hdf1.stage_sigs["blocking_callbacks"] = "Yes"
    eiger.hdf1.stage_sigs["enable"] = 1
    eiger.hdf1.array_callbacks.put(1)
    eiger.hdf1.capture.put(1)
    eiger.hdf1.stage_sigs["file_name"] = fname
    eiger.hdf1.stage_sigs["num_capture"] = nimages  

# Set save mode
    if savemode is not None:
        eiger.hdf1.auto_save.put(savemode)


def set_ext_trig_burst(
    eiger: MyEigerDetector,
    fname: str,
    dir_path: str,
    acqtime: float,
    frametime: float,
    trigger_mode: str,
    burst_size: int,
    nimagesperfile: int,
    ntriggers: int,
    savemode: int = None
):
    # Set file name and data directory
    eiger.cam.stage_sigs["FWNamePattern"] = [ord(c) for c in fname] + [0]
    eiger.hdf1.stage_sigs["file_path"] = dir_path

    # Set acquisition parameters
    eiger.cam.stage_sigs["acquire_time"] = acqtime
    eiger.cam.stage_sigs["acquire_period"] = frametime
    nimages = burst_size * ntriggers
    eiger.cam.stage_sigs["num_images"] = nimages
    eiger.cam.stage_sigs["FWNImagesPerFile"] = nimagesperfile
    eiger.cam.stage_sigs["trigger_mode"] = 3 #  3 = Burst mode 
    eiger.cam.stage_sigs["image_mode"] = 1 # Multiple
    eiger.cam.stage_sigs["num_triggers"] = ntriggers

    eiger.hdf1.stage_sigs["compression"] = "LZ4"
    eiger.hdf1.stage_sigs["file_write_mode"] = "Capture"
    eiger.hdf1.stage_sigs["file_template"] = "%s%s_%6.6d.h5"
    eiger.hdf1.stage_sigs["blocking_callbacks"] = "Yes"
    eiger.hdf1.stage_sigs["num_capture"] = nimages
    eiger.hdf1.stage_sigs['capture'] = 1
    eiger.hdf1.stage_sigs["enable"] = 1
    eiger.hdf1.stage_sigs["array_callbacks"] = 1
    eiger.hdf1.stage_sigs["file_name"] = fname

    # Set save mode
    if savemode is not None:
        eiger.hdf1.auto_save.put(savemode)

def set_ext_trig_multi_scan(
    eiger: MyEigerDetector,
    fname: str,
    dir_path: str,
    acqtime: float,
    frametime: float,
    trigger_mode: str,
    images_per_point: int,
    nimagesperfile: int,
    npositions: int,
    savemode: int = None
):
    # Set file name and data directory
    eiger.cam.stage_sigs["FWNamePattern"] = [ord(c) for c in fname] + [0]
    eiger.hdf1.stage_sigs["file_path"] = dir_path

    # Set acquisition parameters
    eiger.cam.stage_sigs["acquire_time"] = acqtime
    eiger.cam.stage_sigs["acquire_period"] = frametime

    nimages = images_per_point * npositions
    eiger.cam.stage_sigs["num_images"] = nimages
    eiger.cam.stage_sigs["FWNImagesPerFile"] = nimagesperfile
    eiger.cam.stage_sigs["trigger_mode"] = 1 #  1 =  External trigger Enable
    eiger.cam.stage_sigs["image_mode"] = 2 # Continuous (accept multiple triggers)

    eiger.hdf1.stage_sigs["compression"] = "LZ4"
    eiger.hdf1.stage_sigs["file_write_mode"] = "Capture"
    eiger.hdf1.stage_sigs["file_template"] = "%s%s_%6.6d.h5"
    eiger.hdf1.stage_sigs["blocking_callbacks"] = "Yes"
    eiger.hdf1.stage_sigs["num_capture"] = nimages
    eiger.hdf1.stage_sigs['capture'] = 1
    eiger.hdf1.stage_sigs["enable"] = 1
    eiger.hdf1.stage_sigs["array_callbacks"] = 1
    eiger.hdf1.stage_sigs["file_name"] = fname

 
    # Set save mode
    if savemode is not None:
        eiger.hdf1.auto_save.put(savemode)

def ready_detector(
    eiger: MyEigerDetector,
    fname: str,
    dir_path: str,
    acqtime: float,
    frametime: float,
    nimages: int,
    trigger_mode: str,
    ntriggers: int,
    savemode: int = None,
):
    # Set file name and data directory
    eiger_set_fname(eiger, fname)
    eiger_set_dir(eiger, dir_path)

    # Set acquisition parameters
    eiger_set_acqtime(eiger, acqtime)
    eiger_set_frametime(eiger, frametime)
    eiger_set_nimages(eiger, nimages)
    eiger_set_trigger_mode(eiger, trigger_mode)
    eiger_set_ntriggers(eiger, ntriggers)

    # Set save mode
    if savemode is not None:
        eiger.hdf1.auto_save.put(savemode)
    get_eiger_config(eiger)

def eiger_arm(eiger):
    print("Arming Eiger detector...")
    eiger.cam.acquire.put(1, wait=True)
    print(f"Armed (Trigger Mode - {eiger.cam.trigger_mode.get()})")

def eiger_trigger(eiger, wait_for_input=False, wait_till_finished=True):
    acqtime = eiger.cam.acquire_time.get()
    nimages = eiger.cam.num_images.get()
    ntriggers = eiger.cam.num_triggers.get()

    if wait_for_input:
        input("Hit ENTER to trigger...")

    print(f"\nTriggering: {nimages} images, {acqtime:.3f}s/frame, {ntriggers} triggers")

    if eiger.cam.trigger_mode.get() == 1:
        print("External trigger ON")
    else:
        eiger.cam.trigger_mode.put(1)

    if wait_till_finished:
        total_time = acqtime * nimages + 1
        print(f"Waiting {total_time:.2f}s for acquisition to complete...")
        time.sleep(total_time)
        print("Acquisition finished.\n")

def eiger_disarm(eiger):
    print("Disarming Eiger detector ...")
    eiger.cam.acquire.put(0)

def eiger_transfer_last(eiger):
    print("Transferring last dataset...")
    time.sleep(2)
    print("Transfer complete.\n")

# High-Level Acquisition Plans
def arm_and_trigger(eiger, wait_for_input=False, wait_till_finished=True):
    eiger_arm(eiger)
    eiger_trigger(eiger, wait_for_input, wait_till_finished)
    eiger_disarm(eiger)
    eiger_transfer_last(eiger)


def eiger_acquire(eiger, fname, dir_path, acqtime, frametime, nimages, trigger_mode, ntriggers, savemode, wait_for_input=False):
    ready_detector(
        eiger,
        fname,
        dir_path,
        acqtime,
        frametime,
        nimages,
        trigger_mode,
        ntriggers,
        savemode
    )
    arm_and_trigger(eiger, wait_for_input)

def estart(eiger, cnt_time: float = 0.5):
    print("Starting continuous acquisition (streaming)...")

    # Save current values 
    saved_config = {
        'acqtime': eiger.cam.acquire_time.get(),
        'nimages': eiger.cam.num_images.get(),
        'trigger_mode': eiger.cam.trigger_mode.get(),
        'ntriggers': eiger.cam.num_triggers.get(),
    }

    # Disable saving (if applicable)
    if hasattr(eiger, 'savemode'):
        eiger.hdf1.auto_save.put(0)
          _eiger_wait_ready()

    # Set new values
    eiger_set_acqtime(eiger, cnt_time)
    eiger_set_nimages(eiger, 100)
    eiger_set_trigger_mode(eiger, 0)
    eiger_set_ntriggers(eiger, 1)

    eiger_arm(eiger)
    eiger_trigger(eiger, wait_for_input=False, wait_till_finished=True)

    return saved_config  # For use in estop

def estop(eiger, saved_config=None):
    print("Stopping streaming acquisition...")
    eiger_disarm(eiger)

    # Restore previous settings if available
    if saved_config:
        eiger_set_acqtime(eiger, saved_config.get('acqtime', 0.1))
        eiger_set_nimages(eiger, 1)
        eiger_set_trigger_mode(eiger, saved_config.get('trigger_mode', 0))
        eiger_set_ntriggers(eiger, saved_config.get('ntriggers', 1))

    get_eiger_config(eiger)

def eigerburst_ext(
    eiger: MyEigerDetector,
    fname: str,
    dir_path: str,
    acqtime: float,
    frametime: float,
    delay: float,
    nimages: int,
    trigger_mode: str,
    ntriggers: int,
    savemode: int
):
    ready_detector(
        eiger,
        fname,
        dir_path,
        acqtime,
        frametime,
        nimages,
        trigger_mode,
        ntriggers,
        savemode
    )

    time.sleep(1)
    eiger_arm(eiger)
    time.sleep(4)

    # Simulated delay generator trigger
    print(f"Setting delay generator delay to {delay:.5f} s")

    input("Press ENTER to trigger...")

    # Simulate motor move and shutter open
    print("Trigger ON")
    time.sleep(nimages * frametime + 2)

    eiger_disarm(eiger)
    time.sleep(2)
    eiger_transfer_last(eiger)
