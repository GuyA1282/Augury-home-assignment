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
