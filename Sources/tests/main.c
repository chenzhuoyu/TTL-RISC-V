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

typedef struct _frame_t {
    uint32_t pc;
    uint32_t ra;
    uint32_t sp;
    uint32_t gp;
    uint32_t tp;
    uint32_t t0;
    uint32_t t1;
    uint32_t t2;
    uint32_t fp;
    uint32_t s1;
    uint32_t a0;
    uint32_t a1;
    uint32_t a2;
    uint32_t a3;
    uint32_t a4;
    uint32_t a5;
    uint32_t a6;
    uint32_t a7;
    uint32_t s2;
    uint32_t s3;
    uint32_t s4;
    uint32_t s5;
    uint32_t s6;
    uint32_t s7;
    uint32_t s8;
    uint32_t s9;
    uint32_t s10;
    uint32_t s11;
    uint32_t t3;
    uint32_t t4;
    uint32_t t5;
    uint32_t t6;
} frame_t;

void sys_display(uint32_t val) {
    DISPLAY = val;
}

void isr_syscall(frame_t *frame) {
    switch (frame->a0) {
        case SYS_DISPLAY: sys_display(frame->a1); break;
    }
}

void isr_handler(frame_t *frame, uint32_t cause) {
    switch (cause) {
        case ECALL: isr_syscall(frame); break;
    }
}
