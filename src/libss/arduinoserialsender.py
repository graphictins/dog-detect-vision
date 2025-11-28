
import serial
import time

def openSerial(com='COM17', verbose=False) :
    
    openserial = serial.Serial(com, 9600, timeout=10, write_timeout=1)

    return openserial

def closeSerial(openserial, verbose=False) :

    if verbose : print("attemp to close")

    openserial.close()

def sendOutput(openserial, pin=1, value=0.0, verbose=False) :

    data = f"pin({pin})value({value})\n"

    if verbose : print(f"attemp to write {data.encode()}")

    openserial.write(data.encode())