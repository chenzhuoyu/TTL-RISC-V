MEMORY {
    isr     (rx) : ORIGIN = 0xffffff00, LENGTH = 256
    rom     (rx) : ORIGIN = 0xfffc0000, LENGTH = 256000
    ram     (rw) : ORIGIN = 0x08000000, LENGTH = 262144
    iospace (rw) : ORIGIN = 0xc0000000, LENGTH = 268435456
}

SECTIONS {
    .isr  : { *(.isr)  } > isr
    .text : { *(.text) } > rom

    .data : {
        *(.data)
        *(.bss)
        . = 0x40000;
        STACK = .;
    } > ram

    .iospace : {
        . = 0x8000;
        DISPLAY = .;
    } > iospace
}
