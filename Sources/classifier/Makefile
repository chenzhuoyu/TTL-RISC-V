TARGET = classifier

.PHONY: all jed flash clean

all: flash

jed: ${TARGET}.jed

clean:
	rm -vrf ${TARGET}.{chp,fus,jed,pin}

flash: jed
	minipro -p 'GAL22V10D' -w ${TARGET}.jed

${TARGET}.jed: ${TARGET}.pld
	galasm ${TARGET}.pld
