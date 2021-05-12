import serial
import time
from ctypes import *

# EPOS Command Library path
path='.\EposCmd64.dll'

# Load library
cdll.LoadLibrary(path)
epos = CDLL(path)

# Defining return variables from Library Functions
ret = 0
pErrorCode = c_uint()
pDeviceErrorCode = c_uint()

# Defining a variable NodeID and configuring connection
nodeID = 1
baudrate = 1000000
timeout = 500

# Configure desired motion profile
acceleration = 30000 # rpm/s, up to 1e7 would be possible
deceleration = 30000 # rpm/s

# Query motor position
def GetPositionIs():
    pPositionIs=c_long()
    pErrorCode=c_uint()
    ret=epos.VCS_GetPositionIs(keyHandle, nodeID, byref(pPositionIs), byref(pErrorCode))
    return pPositionIs.value # motor steps

# Move to position at speed
def MoveToPositionSpeed(target_position,target_speed):
    while True:
        if target_speed != 0:
            epos.VCS_SetPositionProfile(keyHandle, nodeID, target_speed, acceleration, deceleration, byref(pErrorCode)) # set profile parameters
            epos.VCS_MoveToPosition(keyHandle, nodeID, target_position, True, True, byref(pErrorCode)) # move to position
        elif target_speed == 0:
            epos.VCS_HaltPositionMovement(keyHandle, nodeID, byref(pErrorCode)) # halt motor
        true_position = GetPositionIs()
        if true_position == target_position:
            break

if __name__ == "__main__":
    # Initiating connection and setting motion profile
    keyHandle = epos.VCS_OpenDevice(b'EPOS2', b'MAXON SERIAL V2', b'USB', b'USB0', byref(pErrorCode)) # specify EPOS version and interface
    epos.VCS_SetProtocolStackSettings(keyHandle, baudrate, timeout, byref(pErrorCode)) # set baudrate
    epos.VCS_ClearFault(keyHandle, nodeID, byref(pErrorCode)) # clear all faults
    epos.VCS_ActivateProfilePositionMode(keyHandle, nodeID, byref(pErrorCode)) # activate profile position mode
    epos.VCS_SetEnableState(keyHandle, nodeID, byref(pErrorCode)) # enable device

    MoveToPositionSpeed(20000,5000) # move to position 20,000 steps at 5000 rpm/s
    print('Motor position: %s' % (GetPositionIs()))
    time.sleep(1)

    MoveToPositionSpeed(0,2000) # move to position 0 steps at 2000 rpm/s
    print('Motor position: %s' % (GetPositionIs()))
    time.sleep(1)

    epos.VCS_SetDisableState(keyHandle, nodeID, byref(pErrorCode)) # disable device
    epos.VCS_CloseDevice(keyHandle, byref(pErrorCode)) # close device
