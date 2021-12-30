ABI	   = ilp32
ARCH   = rv32im
CFLAGS = -mabi=${ABI} -march=${ARCH} -static -nostdlib -e main -O3

.PHONY: all

all:
	riscv64-unknown-elf-gcc ${CFLAGS} -Wl,-Tttl-risc-v.ld -o main.elf main.c
	riscv64-unknown-elf-objcopy -j .isr -j '.text.*' -O binary main.elf main.bin
	riscv64-unknown-elf-objdump -Mno-aliases -Mnumeric -d main.elf
