from abc import ABC, abstractmethod


class Endpoint(ABC):
	# Abstract base class of all Endpoints
	
	@property
	@abstractmethod
	def hardware_type(self):
		...
	
	@property
	@abstractmethod
	def battery_threshold(self):
		...
	
	def __init__(self, serial_number, battery, version, backlog, node_uuid):
		self.serial_number = serial_number
		self.battery = battery
		self.version = version
		self.backlog = backlog
		self.node_uuid = node_uuid


class EP1(Endpoint):
	hardware_type = "EP1"
	battery_threshold = 2500


class EP2(Endpoint):
	hardware_type = "EP2"
	battery_threshold = 2500


class Canary_A(Endpoint):
	hardware_type = "Canary_A"
	battery_threshold = 3600
