# TTL RISC-V

RISC-V processor & peripherals made (almost) entirely with 74-series TTL logic chips.

This repository contains the KiCAD schematics and PCB drawings of the processor, along with the related software source code.

## Current Features

* Implements the `RV32IM` instruction set.
* Runs at least `10MHz` clock speed.
* 5-stage pipeline.
* Operand forwarding.
* Mostly single clock cycle instructions.
* Supports the 6800 bus interface (e.g. R/W and STROBE signals).
* Bus mastering to support external DMA controllers.

## Future Design Goals (maybe)

* Higher clock speed?
* Deeper pipelines?
* Superscalar? It might require too many chips to implement :(
* Out-of-order? I havn't figured out how to implement it yet :(
