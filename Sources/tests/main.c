#include <stdint.h>

#define IOV_BASE    ((volatile char *)(0xc0000000))
#define IOV_DISPLAY (IOV_BASE + 0x8000)

#define DISPLAY     (*(volatile uint32_t *)IOV_DISPLAY)

#define RESET       0x0000003f
#define ECALL       0x0000000b

#define MIE         (1 << 3)
#define MEIE        (1 << 11)

#define SYS_DISPLAY 1

void display(uint32_t val) {
    asm volatile (
        "li a0, 1\n"
        "mv a1, %0\n"
        "ecall\n"
        :: "r"(val)
    );
}

void main() {
    uint32_t a;
    uint32_t b;
    uint32_t c;
    for (;;) {
        a = 1;
        b = 1;
        display(a);
        display(b);
        while (!__builtin_uaddl_overflow(a, b, &c)) {
            display(c);
            a = b;
            b = c;
        }
    }
}

/** Interrupt & ECALL Handling **/

void sys_display(uint32_t val) {
    DISPLAY = val;
}

void isr_syscall(uint32_t id, uint32_t a1) {
    switch (id) {
        case SYS_DISPLAY: sys_display(a1); break;
    }
}

void isr_main(uint32_t a0, uint32_t a1, uint32_t cause) {
    switch (cause) {
        case ECALL: isr_syscall(a0, a1); break;
    }
}
