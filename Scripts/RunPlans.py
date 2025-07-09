from bluesky import RunEngine
from bluesky.plan_stubs import mv, trigger_and_read, stage, unstage, sleep
from bluesky.preprocessors import run_decorator
from bluesky.plans import count, scan, list_scan
from ophyd import EpicsMotor as motor
from Eiger import MyEigerDetector as det
import numpy as np

"""
    Configure Eiger for a burst scan using external triggers at one fixed position.
"""

@run_decorator()
def ext_trig_burst(det, burst_size, ntriggers=1):

    total_images = burst_size * ntriggers

    # Stage detector
    yield from stage(det)

    # Wait for all external triggers to arrive
    print(f"Waiting for {ntriggers} external triggers...")
    yield from sleep(0.1)  # give time for triggers to arrive

    # Bluesky must still trigger+read once to complete the run
    yield from trigger_and_read([det])

    # Unstage detector (closes HDF5 file, etc.)
    yield from unstage(det)


"""
    Scan over positions, collecting multiple images per position
    using external triggering (one TTL pulse per image).
"""

@run_decorator()
def ext_trig_multi_scan(det, motor, positions, images_per_point=1):
    
    total_images = len(positions) * images_per_point

    yield from stage(det)
  
    image_counter = 0

    for pos in positions:
        yield from mv(motor, pos)

        for i in range(images_per_point):
            print(f"Waiting for trigger {i+1}/{images_per_point} at position {pos}")
            yield from sleep(0.01)  # Let hardware settle
            yield from trigger_and_read([det])
            image_counter += 1

    yield from unstage(det)

    print(f"Total images captured: {image_counter}")

