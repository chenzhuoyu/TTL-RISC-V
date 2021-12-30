.section .text.isr
.global  isr_entry
.type    isr_entry, @function

isr_entry:
    li      t0, -1
    csrr    a2, mcause
    beq     t0, a2, reset
    call    isr_main
    csrr    t0, mepc
    addi    t0, t0, 4
    csrw    mepc, t0
    mret

reset:
    li      sp, 0x08004000
    li      t0, 0x800
    csrs    mie, t0
    la      t0, main
    csrw    mepc, t0
    csrsi   mstatus, 0x08
    mret
