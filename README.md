# TTL RISC-V

RISC-V processor & peripherals made (almost) entirely with 74-series TTL logic chips.

This repository contains the KiCAD schematics and PCB drawings of the processor, along with the related software source code.

This is designed to be as simple as possible, but it should be a practical processor rather than a pure-educational one.

## Current Design Goals

* Implements the `RV32IMZicsr_Zifencei` instruction set.
* Runs at least `8MHz` clock speed.
* 2-stage pipelines.
* Interrupts.
* Mostly single clock cycle instructions.
* Supports the 6800 bus interface (e.g. R/W and STROBE signals).
* Bus arbitration to support external DMA controllers or co-processors.

## Future Design Goals (maybe)

* Higher clock speed?
* Deeper pipelines?
* Out-of-order?
* Superscalar? It might require too many chips to implement :(
