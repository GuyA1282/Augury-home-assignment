import models

nodes = {}  # a dict to save all nodes (uuid : Node object)
endpoints = {}  # a dict to save all EPs (serial : EP object)
channels = {}  # a dict to save all the channels (channel name : artifact file name)
EP_TYPES = {"EP1": models.EP1, "EP2": models.EP2, "Canary_A": models.Canary_A}
NODE_TYPES = {"AHN2": models.AHN2, "CASSIA": models.Cassia, "MOXA": models.Moxa}


def api_get_endpoint_by_serial(serial_number):
	ep = endpoints[serial_number]
	return {
		"serial_number": ep.serial_number,
		"battery": ep.battery,
		"hardware_type": ep.hardware_type,
		"uuid": ep.node_uuid,
		"version": ep.version,
		"backlog": ep.backlog,
	}


def api_get_node_by_uuid(uuid):
	node = nodes[uuid]
	return {
		"uuid": node.uuid,
		"ota_channel": node.ota_channel,
		"version": node.version,
		"endpoints": [e.serial_number for e in node.endpoints],
		"last_error": node.last_error,
	}


def api_create_endpoint(ep_type, serial_number, battery, version, backlog, node_uuid):
	ep_class = EP_TYPES[ep_type]
	ep = ep_class(serial_number, battery, version, backlog, node_uuid)
	nodes[node_uuid].add_endpoint(ep)
	endpoints[serial_number] = ep
	return 200


def api_create_node(node_type, uuid, version):
	node_class = NODE_TYPES[node_type]
	nodes[uuid] = node_class(uuid, version)
	return 200


def api_drain_backlog(serial_number):
	ep = endpoints[serial_number]
	ep.drain_backlog()
	return 200


def api_trigger_dfu(serial_number, new_version):
	ep = endpoints[serial_number]
	ep.start_dfu(new_version)
	return 200


def api_post_version_to_ota_channel(ota_channel, version_artifact):
	known_channels = [node.ota_channel for node in nodes.values()]
	if ota_channel not in known_channels:
		return 400
	channels[ota_channel] = version_artifact
	return 200


def api_clear_ota_channel(ota_channel, version_artifact):
	if ota_channel in channels and channels[ota_channel] == version_artifact:
		del channels[ota_channel]
		return 200
	else:
		return 400
