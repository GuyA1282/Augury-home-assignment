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


class Node(ABC):
	# Abstract base class of all Nodes
	
	@property
	@abstractmethod
	def hardware_type(self):
		...
	
	@property
	@abstractmethod
	def api_host(self):
		...
	
	def __init__(self, uuid, version):
		self.uuid = uuid
		self.version = version
		self.endpoints = []  # EPs connected to this Node
		self.last_error = ""  # if empty = no error
	
	@property
	def ota_channel(self):
		return f"OTA_{self.uuid}"


class AHN2(Node):
	hardware_type = "AHN2"
	api_host = "buildroot_api.azure"


class Cassia(Node):
	hardware_type = "CASSIA"
	api_host = "buildroot_api.azure"


class Moxa(Node):
	hardware_type = "MOXA"
	api_host = "moxa_api.azure"
