# Augury Home Assignment – Hardware Validation & Automation

A local simulation of an IoT system (Nodes and Endpoints), a fake API (AuguryAPI),
and end-to-end tests in Robot Framework. No real hardware or cloud is used.

## Design decisions and assumptions

### Endpoint as an abstract base class

"Endpoint" inherits from "abc.ABC" and declares "hardware_type" and "battery_threshold"
as abstract properties. Each concrete type (EP1, EP2, Canary_A) defines them as class attributes.

Why:
- There is no generic Endpoint in the system, only specific types, so "Endpoint" itself
  cannot be made.
- Every EP type is forced to define its hardware type and battery threshold. A new type that
  forgets one of them fails immediately with "TypeError" when it is created, instead of
  silently running with a missing threshold.
- The values belong to the type, not to each device, so they are class attributes and are not
  passed to the constructor.
- Adding a new EP type means adding one small subclass; existing code does not change.

Python has no syntax for an "abstract attribute", so I found a pattern that does an abstract
property in the base class, overridden by a plain class attribute in each subclass.

### Node as an abstract base class

"Node" is also an abstract base class. Every concrete type (AHN2, Cassia, Moxa) defines its
"hardware_type" and "api_host", since these are the same for every Node of that type.

- "uuid" and "version" are passed to the constructor; "endpoints" starts as an empty list and
  "last_error" as an empty string (no error), because every new Node starts that way.
- "ota_channel" is a read-only property derived from the UUID ("OTA_<uuid>"), so it always
  matches the UUID and cannot be overwritten.

## Encapsulation

Fields that must not be changed from outside the class are stored with a
leading underscore (for example `_version`) and exposed through a
read-only `@property`.

- **Identity fields** never change after creation: `serial_number` and
  `node_uuid` (Endpoint), `uuid` (Node).
- **State fields** change only through the class's own methods, which
  will enforce the domain rules: `version` (Endpoint and Node) and
  `last_error` (Node).

Why: Python has no truly private attributes, so the underscore is a
convention that means "internal, do not touch". The property has no
setter, so `ep.version = 99` raises `AttributeError`. This stops DFU
gating and OTA artifact validation from being bypassed by assigning a
value directly. I chose `@property` over `get_x()` methods because it
is the idiomatic Python way and keeps access simple (`ep.version`).