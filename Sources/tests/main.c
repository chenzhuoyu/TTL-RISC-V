#include <stdint.h>

void isr_handler() __attribute__((interrupt, section(".isr")));
void isr_handler() {
    asm volatile (
        "LA     sp, STACK\n"
        "LI     t0, 0x800\n"
        "CSRS   mie, t0\n"
        "LA     t1, main\n"
        "CSRW   mepc, t1\n"
        "LI     t2, 0x88\n"
        "CSRS   mstatus, t2\n"
    );
}

extern volatile uint32_t DISPLAY;

void main() {
    uint32_t a;
    uint32_t b;
    uint32_t c;
    for (;;) {
        a = 1;
        b = 1;
        DISPLAY = a;
        DISPLAY = b;
        while (!__builtin_uaddl_overflow(a, b, &c)) {
            DISPLAY = c;
            a = b;
            b = c;
        }
    }
}