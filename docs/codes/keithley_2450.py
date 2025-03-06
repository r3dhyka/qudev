import pyvisa
import sys
import time
import csv
import datetime
import numpy as np

def connect_keithley(mode, address):
    """
    Connect to the Keithley 2450 instrument using the specified mode.
    
    Parameters:
        mode (str): 'ethernet' or 'gpib'
        address (str): IP address if ethernet, or GPIB address (typically an integer as a string)
    
    Returns:
        instrument: A PyVISA instrument session.
    """
    rm = pyvisa.ResourceManager()
    if mode.lower() == 'ethernet':
        resource_string = f"TCPIP0::{address}::INSTR"
    elif mode.lower() == 'gpib':
        resource_string = f"GPIB0::{address}::INSTR"
    else:
        raise ValueError("Unsupported connection mode. Use 'ethernet' or 'gpib'.")
    
    try:
        instrument = rm.open_resource(resource_string)
        print(f"Connected to Keithley 2450 using {mode.upper()} at address: {address}")
        return instrument
    except Exception as e:
        print("Error connecting to instrument:", e)
        sys.exit(1)

def save_to_csv(result, filename='measurement_results.csv'):
    """
    Save a single measurement result to a CSV file with a timestamp.
    
    The CSV file will have two columns: Timestamp and Result.
    If the file does not exist, it will be created with a header row.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = ['Timestamp', 'Result']
    
    try:
        with open(filename, 'r') as f:
            file_exists = True
    except FileNotFoundError:
        file_exists = False
        
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(header)
        writer.writerow([timestamp, result])
    print(f"Result saved to {filename}")

def save_sweep_to_csv(results, header, filename='sweep_results.csv'):
    """
    Save the sweep results to a CSV file.
    
    Parameters:
        results (list of tuples): Each tuple contains a source value and the measured result.
        header (list): The CSV header.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(filename, 'r') as f:
            file_exists = True
    except FileNotFoundError:
        file_exists = False
        
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(header)
        for row in results:
            writer.writerow([timestamp] + list(row))
    print(f"Sweep results saved to {filename}")

def configure_current_source(instrument, current_level, wiring_mode):
    """
    Configures the instrument for a single-point current source and voltage measurement.
    
    Parameters:
        instrument: The connected instrument.
        current_level (float): The current level to source in Amps.
        wiring_mode (str): 'two-wire' or 'four-wire'
    """
    instrument.write("*RST")
    instrument.write("*CLS")
    
    # Set wiring mode: remote sense ON for four-wire, OFF for two-wire
    if wiring_mode == "four-wire":
        instrument.write(":SYST:RSEN ON")
    else:
        instrument.write(":SYST:RSEN OFF")
    
    # Configure as current source
    instrument.write(":SOUR:FUNC CURR")
    instrument.write(f":SOUR:CURR:LEV {current_level}")
    
    # Configure to measure voltage
    instrument.write(":SENS:FUNC 'VOLT'")
    instrument.write(":SENS:VOLT:PROT 10")
    instrument.write(":SENS:VOLT:NPLC 10")
    
    time.sleep(1)
    print("Configured for CURRENT SOURCE / MEASURE VOLTAGE mode.")

def configure_voltage_source(instrument, voltage_level, wiring_mode):
    """
    Configures the instrument for a single-point voltage source and current measurement.
    
    Parameters:
        instrument: The connected instrument.
        voltage_level (float): The voltage level to source in Volts.
        wiring_mode (str): 'two-wire' or 'four-wire'
    """
    instrument.write("*RST")
    instrument.write("*CLS")
    
    if wiring_mode == "four-wire":
        instrument.write(":SYST:RSEN ON")
    else:
        instrument.write(":SYST:RSEN OFF")
    
    # Configure as voltage source
    instrument.write(":SOUR:FUNC VOLT")
    instrument.write(f":SOUR:VOLT:LEV {voltage_level}")
    
    # Configure to measure current
    instrument.write(":SENS:FUNC 'CURR'")
    instrument.write(":SENS:CURR:PROT 0.1")
    instrument.write(":SENS:CURR:NPLC 10")
    
    time.sleep(1)
    print("Configured for VOLTAGE SOURCE / MEASURE CURRENT mode.")

def measure_voltage(instrument):
    """
    Initiates a measurement and reads the voltage value.
    
    Returns:
        str: The measured voltage value.
    """
    instrument.write(":INIT")
    time.sleep(0.5)
    reading = instrument.query(":READ?")
    return reading.strip()

def measure_current(instrument):
    """
    Initiates a measurement and reads the current value.
    
    Returns:
        str: The measured current value.
    """
    instrument.write(":INIT")
    time.sleep(0.5)
    reading = instrument.query(":READ?")
    return reading.strip()

def sweep_current_source(instrument, start, stop, step, wiring_mode):
    """
    Sweeps the current source level from start to stop (with the given step)
    while measuring voltage at each point.
    
    Returns:
        list: A list of tuples (current, measured voltage)
    """
    instrument.write("*RST")
    instrument.write("*CLS")
    
    if wiring_mode == "four-wire":
        instrument.write(":SYST:RSEN ON")
    else:
        instrument.write(":SYST:RSEN OFF")
        
    instrument.write(":SOUR:FUNC CURR")
    instrument.write(":SENS:FUNC 'VOLT'")
    instrument.write(":SENS:VOLT:PROT 10")
    instrument.write(":SENS:VOLT:NPLC 10")
    time.sleep(1)
    
    print("Starting sweep for CURRENT SOURCE / MEASURE VOLTAGE")
    results = []
    current_values = np.arange(start, stop + step, step)
    for current in current_values:
        instrument.write(f":SOUR:CURR:LEV {current}")
        time.sleep(0.2)
        voltage = instrument.query(":READ?")
        voltage = voltage.strip()
        print(f"Current: {current} A, Measured Voltage: {voltage} V")
        results.append((current, voltage))
        time.sleep(0.5)
    return results

def sweep_voltage_source(instrument, start, stop, step, wiring_mode):
    """
    Sweeps the voltage source level from start to stop (with the given step)
    while measuring current at each point.
    
    Returns:
        list: A list of tuples (voltage, measured current)
    """
    instrument.write("*RST")
    instrument.write("*CLS")
    
    if wiring_mode == "four-wire":
        instrument.write(":SYST:RSEN ON")
    else:
        instrument.write(":SYST:RSEN OFF")
    
    instrument.write(":SOUR:FUNC VOLT")
    instrument.write(":SENS:FUNC 'CURR'")
    instrument.write(":SENS:CURR:PROT 0.1")
    instrument.write(":SENS:CURR:NPLC 10")
    time.sleep(1)
    
    print("Starting sweep for VOLTAGE SOURCE / MEASURE CURRENT")
    results = []
    voltage_values = np.arange(start, stop + step, step)
    for voltage in voltage_values:
        instrument.write(f":SOUR:VOLT:LEV {voltage}")
        time.sleep(0.2)
        current = instrument.query(":READ?")
        current = current.strip()
        print(f"Voltage: {voltage} V, Measured Current: {current} A")
        results.append((voltage, current))
        time.sleep(0.5)
    return results

def main():
    # Connect to the instrument
    mode = input("Enter connection mode (ethernet/gpib): ").strip().lower()
    address = input("Enter the instrument address (IP for ethernet or GPIB address for gpib): ").strip()
    instrument = connect_keithley(mode, address)
    
    sweep_choice = input("Do you want to perform a sweep measurement? (y/n): ").strip().lower()
    if sweep_choice == 'y':
        print("\nSelect sweep measurement mode:")
        print("1: Current Source / Measure Voltage")
        print("2: Voltage Source / Measure Current")
        sweep_mode = input("Enter mode (1 or 2): ").strip()
        
        wiring_mode_input = input("Enter wiring mode (two-wire/four-wire): ").strip().lower()
        wiring_mode = "four-wire" if "four" in wiring_mode_input else "two-wire"
        
        try:
            start_val = float(input("Enter sweep start value: ").strip())
            stop_val = float(input("Enter sweep stop value: ").strip())
            step_val = float(input("Enter sweep step value: ").strip())
        except ValueError:
            print("Invalid numeric input for sweep parameters.")
            sys.exit(1)
        
        if sweep_mode == "1":
            results = sweep_current_source(instrument, start_val, stop_val, step_val, wiring_mode)
            header = ['Timestamp', 'Current (A)', 'Measured Voltage (V)']
        elif sweep_mode == "2":
            results = sweep_voltage_source(instrument, start_val, stop_val, step_val, wiring_mode)
            header = ['Timestamp', 'Voltage (V)', 'Measured Current (A)']
        else:
            print("Invalid sweep mode selected.")
            sys.exit(1)
        
        save_sweep_to_csv(results, header)
    
    else:
        # Single-point measurement mode
        print("\nSelect measurement mode:")
        print("1: Current Source / Measure Voltage")
        print("2: Voltage Source / Measure Current")
        measurement_mode = input("Enter mode (1 or 2): ").strip()
        
        wiring_mode_input = input("Enter wiring mode (two-wire/four-wire): ").strip().lower()
        wiring_mode = "four-wire" if "four" in wiring_mode_input else "two-wire"
        
        if measurement_mode == "1":
            current_level_input = input("Enter the current source level (in A): ").strip()
            try:
                current_level = float(current_level_input)
            except ValueError:
                print("Invalid current level")
                sys.exit(1)
            configure_current_source(instrument, current_level, wiring_mode)
            voltage = measure_voltage(instrument)
            print("Measured Voltage:", voltage)
            save_to_csv(voltage)
        elif measurement_mode == "2":
            voltage_level_input = input("Enter the voltage source level (in V): ").strip()
            try:
                voltage_level = float(voltage_level_input)
            except ValueError:
                print("Invalid voltage level")
                sys.exit(1)
            configure_voltage_source(instrument, voltage_level, wiring_mode)
            current = measure_current(instrument)
            print("Measured Current:", current)
            save_to_csv(current)
        else:
            print("Invalid measurement mode selected.")
            sys.exit(1)

if __name__ == '__main__':
    main()
