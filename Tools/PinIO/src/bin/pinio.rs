use pin_io::{PinIo, PinState};

fn main() {
    let mut pio = PinIo::new().unwrap();
    let buf = PinState::from([0xff, 0x00, 0x55, 0xaa, 0x80, 0x08, 0x10, 0x01]);
    loop {
        pio.transfer(&buf).unwrap();
    }
}
