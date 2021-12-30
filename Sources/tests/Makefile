ABI	    = ilp32
ARCH    = rv32im
CFLAGS  = -mabi=${ABI} -march=${ARCH} -O3
LDFLAGS = -mabi=${ABI} -march=${ARCH} -static -nostdlib -Wl,-Tttl-risc-v.ld

.PHONY: all

all:
	riscv64-unknown-elf-gcc ${CFLAGS} -c -o init.o init.s
	riscv64-unknown-elf-gcc ${CFLAGS} -c -o main.o main.c
	riscv64-unknown-elf-gcc ${LDFLAGS} -o main.elf init.o main.o
	riscv64-unknown-elf-objcopy -j .text -j .text.isr -O binary main.elf main.bin
	riscv64-unknown-elf-objdump -Mno-aliases -Mnumeric -d main.elf
