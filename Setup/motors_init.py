from bluesky import RunEngine, plan_stubs as bps
from bluesky.preprocessors import run_decorator
from ophyd import EpicsMotor
from Devices.Motors.Stepper import StepperEpicsMotor
import time

def init_BL172_motor(
    motor_prefix='BL172:MDrive:m1'
):

    # Connect to motor
    m1 = EpicsMotor(motor_prefix, name='m1')
    m1.wait_for_connection(timeout=1)

    print(f"MDriver motor m1 initialized successfully.")
    return m1

def init_BL172_stepper(
    stepper_prefix='BL111:WAXS_1:MOTOR1'
):

    # Connect to stpper motor
    stepper = StepperEpicsMotor(stepper_prefix, name='stepper')
#    zaber = EpicsMotor(zaber_prefix, name='zaber')

#  the PV 'direction_of_travel' seems not implemented in customized controller developed by Dehong
    if 'direction_of_travel' in stepper.read_attrs:
        stepper.read_attrs.remove('direction_of_travel')

    print(f"Stepper motor initialized successfully.")
    return stepper

def init_BL172_beamstop(
    beamstop_prefix='BL172:Beamstop:m1'
):
    # Connect to Beamstop
    beamstop = EpicsMotor(beamstop_prefix, name='beamstop')

    print(f"Beamstop motor initialized successfully.")
    return beamstop

