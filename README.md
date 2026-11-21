# Augury Home Assignment – Hardware Validation & Automation

A local simulation of an IoT system (Nodes and Endpoints), a fake API (AuguryAPI),
and end-to-end tests in Robot Framework. No real hardware or cloud is used.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Tested with Python 3.9 and Robot Framework 7.5.1.

## Project structure

- `models.py`: the IoT model (Node and Endpoint types and their rules)
- `augury_api.py`: the fake AuguryAPI used by the tests
- `tests/augury.robot`: the Robot Framework suite
- `docs/signal_processing.md`: answers to the signal-processing questions

## Design decisions and assumptions

### Endpoint as an abstract base class

`Endpoint` inherits from `abc.ABC` and declares `hardware_type` and `battery_threshold`
as abstract properties. Each concrete type (EP1, EP2, Canary_A) defines them as class attributes.

Why:

- There is no generic Endpoint in the system, only specific types, so `Endpoint` itself
  cannot be created.
- Every EP type is forced to define its hardware type and battery threshold. A new type that
  forgets one of them fails immediately with `TypeError` when it is created, instead of
  silently running with a missing threshold.
- The values belong to the type, not to each device, so they are class attributes and are not
  passed to the constructor.
- Adding a new EP type means adding one small subclass; existing code does not change.

Python has no syntax for an "abstract attribute", so I used an abstract property in the base
class, overridden by a plain class attribute in each subclass.

### Node as an abstract base class

`Node` is also an abstract base class. Every concrete type (AHN2, Cassia, Moxa) defines its
`hardware_type` and `api_host`, since these are the same for every Node of that type.

- `uuid` and `version` are passed to the constructor. Linked Endpoints are stored in a dict
  keyed by serial number, which starts empty, and `last_error` starts as an empty string (no error), because every new
  Node starts that way.
- `ota_channel` is a read-only property derived from the UUID (`OTA_<uuid>`), so it always
  matches the UUID and cannot be overwritten.

### Assumptions

- Artifact names are well-formed (`<hardware_type>_<version>.swu`), as defined in the spec.
  The hardware type is compared case-insensitively.
- Versions are whole numbers. There is no downgrade protection: any matching artifact or DFU
  version is accepted.
- DFU is a single attempt: if the gating rules block it, nothing changes, and the test
  triggers it again after the backlog drains.
- `battery` and `backlog` are inputs to the DFU rules, so they stay public and tests can set them.

## Encapsulation

Fields that must not be changed from outside the class are stored with a
leading underscore (for example `_version`) and exposed through a
read-only `@property`.

- **Identity fields** never change after creation: `serial_number` and
  `node_uuid` (Endpoint), `uuid` (Node).
- **State fields** change only through the class's own methods, which
  enforce the domain rules: `version` (Endpoint and Node) and
  `last_error` (Node).

Why: Python has no truly private attributes, so the underscore is a
convention that means "internal, do not touch". The property has no
setter, so `ep.version = 99` raises `AttributeError`. This stops DFU
gating and OTA artifact validation from being bypassed by assigning a
value directly. I chose `@property` over `get_x()` methods because it
is the idiomatic Python way and keeps access simple (`ep.version`).

## Model API (`models.py`)

### Node (AHN2, Cassia, Moxa)

- `apply_artifact(artifact)`: processes an artifact name such as `moxa_34.swu`.
  If the hardware type matches the Node (case-insensitive), the version is
  updated. Otherwise the version stays unchanged and the reason is stored in
  `last_error`.
- `add_endpoint(ep)`: links an Endpoint to the Node. Raises `ValueError` if the
  Endpoint belongs to a different Node, or if its serial number is already linked.
- `endpoints`: a list copy of the linked Endpoints, so the Node's data cannot be
  changed from outside.
- `ota_channel`: the channel name, `OTA_<uuid>`.
- `uuid`, `version`, `last_error`: read-only.

### Endpoint (EP1, EP2, Canary_A)

- `start_dfu(new_version)`: a single DFU attempt. The version is updated only if
  `backlog == 0` and `battery >= battery_threshold`; otherwise nothing changes.
- `drain_backlog()`: simulates the Endpoint uploading its pending samples, so
  `backlog` becomes 0.
- `serial_number`, `node_uuid`, `version`: read-only.

## Fake API (`augury_api.py`)

The fake API plays the role of the Augury cloud. Tests (Python or Robot) talk
only to these functions, using simple values (strings, numbers, dicts), and never
touch the model objects directly. The domain rules stay in `models.py`; the API
finds the right object and calls its methods.

### State

Each API call is independent (Robot calls them one by one), so the objects must
live somewhere between calls. The API keeps them in module-level dictionaries,
acting as the backend's storage:

- `nodes`: uuid -> Node
- `endpoints`: serial number -> Endpoint
- `channels`: OTA channel name -> the artifact waiting in it (one per channel)

The values are the objects themselves, so all data and rules stay in the model.

### Type lookup

Tests pass a hardware type as a string (for example `"MOXA"`). `NODE_TYPES` and
`EP_TYPES` map each type name to its class. Adding a new type means adding one
line to the dictionary; the create functions do not change (no `if`/`elif` chain).

### Required functions

- `api_get_endpoint_by_serial(serial_number)`: returns the Endpoint's data as a
  dict (`serial_number`, `battery`, `hardware_type`, `uuid`, `version`, plus
  `backlog`).
- `api_get_node_by_uuid(uuid)`: returns the Node's data as a dict (`uuid`,
  `ota_channel`, `version`, `endpoints` as a list of serials, plus `last_error`).
- `api_post_version_to_ota_channel(ota_channel, version_artifact)`: puts the
  artifact in the channel. Returns 400 if no existing Node owns that channel,
  otherwise 200. A channel holds one artifact; posting a new one replaces it.
  Posting does not update the Node: the Node updates only when it polls its channel.
- `api_clear_ota_channel(ota_channel, version_artifact)`: removes the artifact
  from the channel. Returns 200 if that artifact was in the channel, otherwise 400.

### Test helpers

These simulate things that happen on their own in the real system, so the tests
can set up and drive scenarios. They return nothing; a wrong setup raises an
exception, which fails the test. Status codes (200/400) are used only by the two
OTA channel functions, as the spec defines.

- `api_create_node(node_type, uuid, version)`: simulates a Node being installed
  and registering with the cloud.
- `api_create_endpoint(ep_type, serial_number, battery, version, backlog, node_uuid)`:
  simulates an Endpoint being paired with its Node. It is linked with
  `add_endpoint` before being stored, so a wrong setup raises `ValueError` and
  leaves the state unchanged.
- `api_poll_ota(uuid)`: simulates the Node checking its OTA channel. If an
  artifact is waiting, the Node applies it and it is removed from the channel,
  so each artifact is processed once.
- `api_drain_backlog(serial_number)`: simulates the Endpoint uploading its pending
  samples (backlog becomes 0).
- `api_trigger_dfu(serial_number, new_version)`: asks the Endpoint to start a DFU.
  The gating rules decide inside the model, and the test checks the version afterwards.
- `api_reset()`: clears all Nodes, Endpoints and channels. Used as the Robot
  test setup, so tests do not depend on each other.

## Error handling

- **Expected outcomes are not exceptions.** A mismatched OTA artifact stores a
  message in `last_error`, and a deferred DFU simply changes nothing. Tests check
  the result (`version`, `last_error`).
- **Programming errors raise exceptions.** Linking an Endpoint to the wrong Node,
  or linking the same serial twice, raises `ValueError`. Looking up an unknown
  uuid or serial raises `KeyError`. A wrong setup fails loudly instead of leaving
  the state inconsistent.

## Tests (`tests/augury.robot`)

- Written in BDD style (Given / When / Then), with readable keywords built on the API.
- `Api Reset` runs before each test (`Test Setup`), so tests are independent of
  each other and of their order.
- **OTA retries:** OTA results are checked with `Wait Until Keyword Succeeds`,
  3 retries, 1 second apart (`${RETRIES}` and `${INTERVAL}`). Each retry polls the
  Node's channel and checks the result; if it never appears, the test fails.
- Negative tests pass when the system rejects correctly: a bad artifact, a
  deferred DFU, or a post to an unknown channel.


## What I would add with more time
- **Boundary tests for battery thresholds** for each Endpoint type: exactly at the
  threshold (DFU allowed) and one below it (DFU deferred).
- **Case-insensitivity tests**: artifacts such as `MOXA_34.swu` and `Moxa_34.swu`.
- **`last_error` on Endpoints**, so a deferred DFU reports its reason (backlog or
  battery). Each reason needs a different action: wait for the upload, or charge
  the battery.