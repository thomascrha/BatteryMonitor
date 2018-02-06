#!/usr/bin/env python3

import sys, time
from daemon import config, LogginSystem, Daemon
import yaml
import argparse
import datetime
from gpiozero import Button
from gpiozero.pins.rpigpio import RPiGPIOPin
import os
import subprocess
import Adafruit_ADS1x15
import shlex
import psutil

'''
percentage:
        100%: 4.09  # 4.09
        75%: 3.68   # 3.76
        50%: 3.46   # 3.63
        25%: 3.35    # 3.5
        0%: 3.25     # 3.2
voltage:
        4.09: 100 # 4.09
        3.68: 75  # 3.76
        3.46: 50  # 3.63
        3.35: 25 # 3.5
        3.25: 0  # 3.2
'''


def arguments_reader():

        parser = argparse.ArgumentParser(description='battery-monitor runner')
        parser.add_argument('operation',
                metavar='OPERATION',
                type=str,
                help='Operation with BatteryMonitor agent. Accepts any of these values: start, stop, restart, status',
                choices=['start', 'stop', 'restart', 'status'])
        args = parser.parse_args()
        operation = args.operation
        return operation
logfile = open('./battery-monitor.log', 'a+')                

class BatteryMonitor(Daemon):
        def run(self):
		# change this to be implied form the config
		self.adc = Adafruit_ADS1x15.ADS1015()
                #create setup_pins method allowing fornamic loading
                shutdown_btn = Button(int(config['button']['shutdown']))#, hold_time=1)
                monitor_btn = Button(int(config['button']['monitor'])) #, hold_time=2)
                self.logger = logfile
                while True:
                            self.battery_percent()
                            shutdown_btn.when_pressed = self.shutdown
                            monitor_btn.when_pressed = self.display_icon
        def process_spawner(self, subprocess_call):

                self.pngprocess = psutil.Process(subprocess_call.pid)
                try:
                        self.pngprocess.wait(timeout=3.0)
                except psutil.TimeoutExpired:
                        self.pngprocess.kill()
                        self.pngprocess = None
                        pass #raise

        def read_battery_voltage(self):
                total = 0.0
                loops = 0.0
                start = time.time()
                while (time.time() - start) <= 1.0:
                        # Read the last ADC conversion value and print it out.
                        try:
				value = self.adc.read_adc(0, gain=config['gain'])
			except IOError:
				return None
						
                        total += float(value)
                        loops += 1.0
                        time.sleep(0.2)

                value = total/loops

                return round(value, 2)
        def display_icon(self):
                self.logger.write('display_icon')
                if not self.percent:
                        self.percent = battery_percent
                command = '{}/pngview -b 0 -l 3000{} -x {} -y {} {}/battery{}.png &'.format(config['png']['path'], self.percent, 
                                                                                            config['png']['x'],config['png']['y'],
                                                                                            config['png']['icon'], self.percent)
                subprocess_call = subprocess.Popen(shlex.split(command))
                self.process_spawner(subprocess_call)
                #time.sleep(3)
                if self.pngprocess:
                        self.pngprocess.kill()                 
    
        def battery_percent(self):
                raw_voltage = self.read_battery_voltage()
                self.logger.write('Raw Votage ' + str(raw_voltage)+ '\n')
		if raw_voltage:
                	self.voltage = round(raw_voltage * config['converstion-ratio'], 2)
                        self.logger.write('Votage ' + str(self.voltage) + '\n')
                        
		else:   
                        #add new state for non configured : create icon
			self.percent = 100
                for key in config['voltages']:
                        if self.voltage in key:
                                self.percent = config['voltages'][key] 
                                break
                        self.percent = None 
                #display appropriate icon.

        def shutdown(self):
                command = 'shutdown -h now'
                subprocess.Popen(shlex.split(command))


if __name__ == "__main__":

        action = arguments_reader()
        daemon = BatteryMonitor()

        if action == 'start':
                print("Starting BatteryMonitor agent")
                daemon.start()
                pid = daemon.get_pid()
                if not pid:
                        print("Unable run BatteryMonitor agent")
                else:
                        print("BatteryMonitor agent is running")

        elif action == 'stop':
                print("Stoping BatteryMonitor agent")
                daemon.stop()

        elif action == 'restart':
                print("Restarting BatteryMonitor agent")
                daemon.restart()

        elif action == 'status':
                print("Viewing BatteryMonitor agent status")
                pid = daemon.get_pid()

                if not pid:
                        print("BatteryMonitor agent isn't running")
                else:
                        print("BatteryMonitor agent is running")

        #sys.exit(0)
