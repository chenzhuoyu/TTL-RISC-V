MEMORY {
    isr (rx) : ORIGIN = 0xffffff00, LENGTH = 256
    rom (rx) : ORIGIN = 0xfffc0000, LENGTH = 256000
    ram (rw) : ORIGIN = 0x08000000, LENGTH = 262144
}

SECTIONS {
    .text.isr : {
        *(.text.isr)
        *(.text.isr.*)
    } > isr

    .text : {
        *(.text)
        *(.text.*)
    } > rom

    .data : {
        *(.data)
        *(.data.*)
        *(.bss)
        *(.bss.*)
    } > ram
}
