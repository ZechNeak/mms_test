'''
usage: python3 test.py [mac_address]

Description:
    The purpose of this code is to be a proof-of-concept for possibly using a wireless
    (Bluetooth) IMU to aid in implementing visual-inerial SLAM on an HMD.
    The hardware this code is designed for is Mbientlab's MetaMotionS (MMS) board. As of
    this writing, the MMS uses a BM270 for its accelerometer and gyroscope, and a BMM150 
    for its magnetometer.

    The code is derived from examples/stream_acc_gyro_bmi270.py, and examples/stream_mag.py.
'''

from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from time import sleep
from threading import Event

import platform
import sys
import faulthandler

faulthandler.enable()

if sys.version_info[0] == 2:
    range = xrange

class State:
    def __init__(self, device):
        self.device = device
        self.samples = 0
        self.acc_samples = 0
        self.gyro_samples = 0
        self.mag_samples = 0

        # When button is True (pressed), toggle sampling on and off
        self.button = False
        self.is_sampling = False

        self.accCallback = FnVoid_VoidP_DataP(self.acc_data_handler)
        self.gyroCallback = FnVoid_VoidP_DataP(self.gyro_data_handler)
        self.magCallback = FnVoid_VoidP_DataP(self.mag_data_handler)
        self.buttonCallback = FnVoid_VoidP_DataP(self.button_data_handler)

    # For accelerometer callback
    def acc_data_handler(self, ctx, data):
        print("ACC: %s " % (parse_value(data)))
        self.acc_samples += 1
        self.samples += 1

    # For gyroscope callback
    def gyro_data_handler(self, ctx, data):
        print("GYRO: %s " % (parse_value(data)))
        self.gyro_samples += 1
        self.samples += 1

    # For magnetometer callback
    def mag_data_handler(self, ctx, data):
        print("MAG: %s " % (parse_value(data)))
        self.mag_samples+= 1
        self.samples += 1

    # For push button switch callback
    def button_data_handler(self, ctx, data):
        self.button = parse_value(data)

        if self.button == True:
            self.is_sampling = not self.is_sampling
            print("[ButtonPressed] Ending sampling...")

print("\n[NOTE] According to Mbientlab, the src/blestatemachine.cc error can be ignored.\n")

try:
    # Connect to MMS
    d = MetaWear(sys.argv[1])
    d.connect()
    state = State(d)
    print("[STATUS] Connected to " + d.address + " over BLE")

    # Configure MMS
    print("[STATUS] Configuring MMS device")
    libmetawear.mbl_mw_settings_set_connection_parameters(state.device.board, 7.5, 7.5, 0, 6000)
    sleep(1.5)

    # Setup LED status indicator
    pattern = LedPattern(repeat_count= Const.LED_REPEAT_INDEFINITELY)
    libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.SOLID)
    libmetawear.mbl_mw_led_write_pattern(state.device.board, byref(pattern), LedColor.BLUE)
    libmetawear.mbl_mw_led_play(state.device.board)

    # Setup accelerometer
    libmetawear.mbl_mw_acc_bmi270_set_odr(state.device.board, AccBmi270Odr._100Hz)
    libmetawear.mbl_mw_acc_bosch_set_range(state.device.board, AccBoschRange._4G)
    libmetawear.mbl_mw_acc_write_acceleration_config(state.device.board)

    # Setup gyroscope
    libmetawear.mbl_mw_gyro_bmi270_set_odr(state.device.board, GyroBoschOdr._100Hz)
    libmetawear.mbl_mw_gyro_bmi270_set_range(state.device.board, GyroBoschRange._1000dps)
    libmetawear.mbl_mw_gyro_bmi270_write_config(state.device.board)

    # Setup magnetometer 
    # (ODR for HIGH_ACCURACY preset is 20Hz; 10Hz for every other option)
    libmetawear.mbl_mw_mag_bmm150_stop(state.device.board)
    libmetawear.mbl_mw_mag_bmm150_set_preset(state.device.board, MagBmm150Preset.HIGH_ACCURACY)

    # Prepare to read from accelerometer, gyroscope, and magnetometer
    acc = libmetawear.mbl_mw_acc_get_acceleration_data_signal(state.device.board)
    libmetawear.mbl_mw_datasignal_subscribe(acc, None, state.accCallback)

    gyro = libmetawear.mbl_mw_gyro_bmi270_get_rotation_data_signal(state.device.board)
    libmetawear.mbl_mw_datasignal_subscribe(gyro, None, state.gyroCallback)

    mag = libmetawear.mbl_mw_mag_bmm150_get_b_field_data_signal(state.device.board)
    libmetawear.mbl_mw_datasignal_subscribe(mag, None, state.magCallback)

    # Prepare to read state of push button switch
    button = libmetawear.mbl_mw_switch_get_state_data_signal(state.device.board)
    libmetawear.mbl_mw_datasignal_subscribe(button, None, state.buttonCallback)

    # Start accelerometer, gyroscope, and magnetometer
    libmetawear.mbl_mw_acc_enable_acceleration_sampling(state.device.board)
    libmetawear.mbl_mw_acc_start(state.device.board)

    libmetawear.mbl_mw_gyro_bmi270_enable_rotation_sampling(state.device.board)
    libmetawear.mbl_mw_gyro_bmi270_start(state.device.board)

    libmetawear.mbl_mw_mag_bmm150_enable_b_field_sampling(state.device.board)
    libmetawear.mbl_mw_mag_bmm150_start(state.device.board)

    state.is_sampling = True

    print("[STATUS] Device ready")

    # LED indicating sampling is active
    libmetawear.mbl_mw_led_stop_and_clear(state.device.board)
    libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.BLINK)
    libmetawear.mbl_mw_led_write_pattern(state.device.board, byref(pattern), LedColor.GREEN)
    libmetawear.mbl_mw_led_play(state.device.board)

    # Stream indefinitely until interrupted
    while state.is_sampling:
        sleep(0.25)

except KeyboardInterrupt:
    print("\n[KeyboardInterrupt] Stopping device now...\n")

except NameError:
    print("[NameError] Ignoring variables not yet defined...\n")

finally:

    try:
        # LED indicating teardown process
        libmetawear.mbl_mw_led_stop_and_clear(state.device.board)
        libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.SOLID)
        libmetawear.mbl_mw_led_write_pattern(state.device.board, byref(pattern), LedColor.RED)
        libmetawear.mbl_mw_led_play(state.device.board)

        # Stop accelerometer, gyroscope, and magnetometer
        libmetawear.mbl_mw_acc_stop(state.device.board)
        libmetawear.mbl_mw_acc_disable_acceleration_sampling(state.device.board)

        libmetawear.mbl_mw_gyro_bmi270_stop(state.device.board)
        libmetawear.mbl_mw_gyro_bmi270_disable_rotation_sampling(state.device.board)

        libmetawear.mbl_mw_mag_bmm150_stop(state.device.board)
        libmetawear.mbl_mw_mag_bmm150_disable_b_field_sampling(state.device.board)

        libmetawear.mbl_mw_datasignal_unsubscribe(acc)
        libmetawear.mbl_mw_datasignal_unsubscribe(gyro)
        libmetawear.mbl_mw_datasignal_unsubscribe(mag)

    except NameError:
        print("[NameError] Ignoring variables not yet defined...\n")

    finally:
        # Turn off LED
        libmetawear.mbl_mw_led_stop_and_clear(d.board)

        # Put device into "sleep" mode, where it can only be woken by button press
        # or plugging in a USB charger
        # TODO: Does this work as expected?
        libmetawear.mbl_mw_debug_enable_power_save(d.board)

        # Disconnect from MMS
        libmetawear.mbl_mw_debug_disconnect(d.board)
        print("[STATUS] Device disconnected")

        try:
            # Display results
            print("[RESULT] Total samples received:")

            print("acc --> %d" % (state.acc_samples))
            print("gyro -> %d" % (state.gyro_samples))
            print("mag --> %d" % (state.mag_samples))
            print("Total -> %d" % (state.samples))

        except NameError:
            print("\n[NameError] No samples; state is undefined\n")