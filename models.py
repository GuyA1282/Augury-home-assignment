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
		self._serial_number = serial_number
		self.battery = battery
		self._version = version
		self.backlog = backlog
		self._node_uuid = node_uuid
	
	@property
	def serial_number(self):
		return self._serial_number
	
	@property
	def version(self):
		return self._version
	
	@property
	def node_uuid(self):
		return self._node_uuid
	
	def drain_backlog(self):
		self.backlog = 0
	
	def start_dfu(self, new_version):
		if self.backlog == 0 and self.battery >= self.battery_threshold:
			self._version = new_version


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
		self._uuid = uuid
		self._version = version
		self._endpoints = []  # EPs connected to this Node
		self._last_error = ""  # if empty = no error
	
	@property
	def ota_channel(self):
		return f"OTA_{self.uuid}"
	
	@property
	def uuid(self):
		return self._uuid
	
	@property
	def version(self):
		return self._version
	
	@property
	def last_error(self):
		return self._last_error
	
	@property
	def endpoints(self):
		return list(self._endpoints)
	
	def add_endpoint(self, ep):
		if ep.node_uuid != self._uuid:
			raise ValueError(f"Endpoint {ep.serial_number} belongs to {ep.node_uuid}, not {self._uuid}")
		self._endpoints.append(ep)
	
	def apply_artifact(self, artifact):
		artifact_parts = artifact[:-4].split("_")
		artifact_name, artifact_version = artifact_parts[0], artifact_parts[1]
		if artifact_name.lower() == self.hardware_type.lower():
			self._version = int(artifact_version)
		else:
			self._last_error = f"Artifact {artifact} does not match Node type {self.hardware_type}"


class AHN2(Node):
	hardware_type = "AHN2"
	api_host = "buildroot_api.azure"


class Cassia(Node):
	hardware_type = "CASSIA"
	api_host = "buildroot_api.azure"


class Moxa(Node):
	hardware_type = "MOXA"
	api_host = "moxa_api.azure"
