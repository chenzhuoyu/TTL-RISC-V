TARGET = wbdec

.PHONY: all jed pld flash clean

all: flash

jed: ${TARGET}.jed

pld: ${TARGET}.pld

clean:
	rm -vrf ${TARGET}.{chp,fus,jed,pin}

flash: jed
	minipro -p 'GAL22V10D' -w ${TARGET}.jed

${TARGET}.jed: ${TARGET}.pld
	galasm ${TARGET}.pld

${TARGET}.pld: ${TARGET}.logic
	../../Tools/LogicGen/logen.py ${TARGET}.logic