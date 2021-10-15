# TTL RISC-V

RISC-V processor & peripherals made (almost) entirely with 74-series TTL logic chips.

This repository contains the KiCAD schematics and PCB drawings of the processor, along with the related software source code.

## Current Design Goals

* Supports the `RV32IM` instruction set.
* Runs at `16MHz` clock speed.
* Multi-stage pipeline.
* Single clock cycle instructions.
* Supports the 6800 bus interface (e.g. R/W and STROBE signals).

## Future Design Goals (maybe)

* Out-of-order, I havn't figured out how to implement it yet :(
