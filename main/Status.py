#!/usr/bin/python3
import time
import can
import RPi.GPIO as GPIO
import cantools
import os
import csv
import socket
import pickle
import logging



class Status(object):
	"""docstring for Status"""
	def __init__(self):
		super(Status, self).__init__()
		self.temperature_voliated_battery = [];
		self.battery_cell_voltage_voilated = [];

		self.isvolLimited = False;
        self.istempHigh = False; 
        self.isCVViolated = False;
		