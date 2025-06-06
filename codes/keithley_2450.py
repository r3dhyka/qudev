import pyvisa
import sys
import time
import csv
import datetime
import numpy as np

def connect_keithley(mode, address):
    """Connects to the Keithley 2450 using Ethernet or GPIB."""
    rm = pyvisa.ResourceManager()
    if mode.lower() == 'ethernet':
        resource_string = f"TCPIP0::{address}::INSTR"
    elif mode.lower() == 'gpib':
        resource_string = f"GPIB0::{address}::INSTR"
    else:
        raise ValueError("Invalid mode. Use 'ethernet' or 'gpib'.")

    try:
        instrument = rm.open_resource(resource_string)
        print(f"Connected to Keithley 2450 via {mode.upper()} at {address}")
        return instrument
    except Exception as e:
        print("Error connecting:", e)
        sys.exit(1)

def configure_current_source(instrument, current_level, voltage_limit, wiring_mode):
    """Configures the instrument for sourcing current and measuring voltage."""
    instrument.write("*RST")
    instrument.write("*CLS")

    # **Corrected 4-wire mode command**
    instrument.write(f":SENS:REM {'ON' if wiring_mode == 'four-wire' else 'OFF'}")

    instrument.write(":SOUR:FUNC CURR")
    instrument.write(f":SOUR:CURR {current_level}")
    
    # **Corrected compliance setting**
    instrument.write(f":SOUR:CURR:VLIM {voltage_limit}")

    # **Corrected measurement setup**
    instrument.write(':SENS:FUNC "VOLT"')
    time.sleep(1)
    print("Configured for CURRENT SOURCE / MEASURE VOLTAGE.")

def configure_voltage_source(instrument, voltage_level, current_limit, wiring_mode):
    """Configures the instrument for sourcing voltage and measuring current."""
    instrument.write("*RST")
    instrument.write("*CLS")

    # **Corrected 4-wire mode command**
    instrument.write(f":SENS:REM {'ON' if wiring_mode == 'four-wire' else 'OFF'}")

    instrument.write(":SOUR:FUNC VOLT")
    instrument.write(f":SOUR:VOLT {voltage_level}")

    # **Corrected compliance setting**
    instrument.write(f":SOUR:VOLT:ILIM {current_limit}")

    # **Corrected measurement setup**
    instrument.write(':SENS:FUNC "CURR"')
    time.sleep(1)
    print("Configured for VOLTAGE SOURCE / MEASURE CURRENT.")

def measure_voltage(instrument):
    """Reads voltage measurement."""
    voltage = instrument.query(":READ?").strip()  # **Fixed unnecessary INIT command**
    return voltage

def measure_current(instrument):
    """Reads current measurement."""
    current = instrument.query(":READ?").strip()  # **Fixed unnecessary INIT command**
    return current

def sweep_current_source(instrument, start, stop, step, voltage_limit, wiring_mode):
    """Sweeps current and measures voltage at each step."""
    instrument.write("*RST")
    instrument.write("*CLS")

    instrument.write(f":SENS:REM {'ON' if wiring_mode == 'four-wire' else 'OFF'}")
    instrument.write(":SOUR:FUNC CURR")
    instrument.write(':SENS:FUNC "VOLT"')
    instrument.write(f":SOUR:CURR:VLIM {voltage_limit}")

    results = []
    for current in np.arange(start, stop + step, step):
        instrument.write(f":SOUR:CURR {current}")
        time.sleep(0.2)
        voltage = instrument.query(":READ?").strip()
        print(f"Current: {current} A, Voltage: {voltage} V")
        results.append((current, voltage))
    return results

def sweep_voltage_source(instrument, start, stop, step, current_limit, wiring_mode):
    """Sweeps voltage and measures current at each step."""
    instrument.write("*RST")
    instrument.write("*CLS")

    instrument.write(f":SENS:REM {'ON' if wiring_mode == 'four-wire' else 'OFF'}")
    instrument.write(":SOUR:FUNC VOLT")
    instrument.write(':SENS:FUNC "CURR"')
    instrument.write(f":SOUR:VOLT:ILIM {current_limit}")

    results = []
    for voltage in np.arange(start, stop + step, step):
        instrument.write(f":SOUR:VOLT {voltage}")
        time.sleep(0.2)
        current = instrument.query(":READ?").strip()
        print(f"Voltage: {voltage} V, Current: {current} A")
        results.append((voltage, current))
    return results

def save_results(filename, data, mode):
    """Saves the sweep data to a CSV file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    full_filename = f"{filename}_{timestamp}.csv"

    with open(full_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Source", "Measured"])
        writer.writerows(data)
    
    print(f"Results saved to {full_filename}")

def main():
    mode = input("Enter connection mode (ethernet/gpib): ").strip().lower()
    address = input("Enter instrument address: ").strip()
    instrument = connect_keithley(mode, address)

    sweep_choice = input("Perform a sweep measurement? (y/n): ").strip().lower()
    wiring_mode = "four-wire" if input("Enter wiring mode (two-wire/four-wire): ").strip().lower() == "four-wire" else "two-wire"

    if sweep_choice == 'y':
        sweep_mode = input("Select sweep mode: 1 (Current Source / Measure Voltage), 2 (Voltage Source / Measure Current): ").strip()

        start_val = float(input("Enter start value: ").strip())
        stop_val = float(input("Enter stop value: ").strip())
        step_val = float(input("Enter step value: ").strip())

        filename = input("Enter filename for saving results: ").strip()

        if sweep_mode == "1":
            voltage_limit = float(input("Enter voltage compliance limit (V): ").strip())  # **Added voltage limit input**
            results = sweep_current_source(instrument, start_val, stop_val, step_val, voltage_limit, wiring_mode)
            save_results(filename, results, "Current Sweep")
        elif sweep_mode == "2":
            current_limit = float(input("Enter current compliance limit (A): ").strip())  # **Added current limit input**
            results = sweep_voltage_source(instrument, start_val, stop_val, step_val, current_limit, wiring_mode)
            save_results(filename, results, "Voltage Sweep")

if __name__ == "__main__":
    main()
