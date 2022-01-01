NAME	= main
SRCS    = isr.s main.c

ABI	    = ilp32
ARCH    = rv32im

CFLAGS  = -march=${ARCH} -mabi=${ABI} -O3
LDFLAGS = -march=${ARCH} -static -nostdlib -Wl,-Tttl-risc-v.ld

BIN		= ${NAME}.bin
ELF		= ${NAME}.elf
OBJS 	= $(SRCS:%=%.o)

.PHONY: all clean

all: ${BIN}
	riscv64-unknown-elf-objdump -Mno-aliases -Mnumeric -d ${ELF}

clean:
	rm -vrf ${BIN} ${ELF} ${OBJS}

${BIN}: ${ELF}
	riscv64-unknown-elf-objcopy -j .text -j .text.isr -O binary ${ELF} ${BIN}

${ELF}: ${OBJS}
	riscv64-unknown-elf-gcc ${LDFLAGS} -o ${ELF} ${OBJS}

%.c.o: %.c
	riscv64-unknown-elf-gcc ${CFLAGS} -c $< -o $@

%.s.o: %.s
	riscv64-unknown-elf-gcc ${CFLAGS} -c $< -o $@
