use std::pin::Pin;

use bitvec::BitArr;
use ftd2xx_embedded_hal::{
    embedded_hal::{
        digital::v2::OutputPin as OutputPinTrait, prelude::_embedded_hal_blocking_spi_Transfer,
    },
    libftd2xx::{Ft2232h, MpsseSettings},
    Ft2232hHal, Initialized, OutputPin, Spi,
};
use ouroboros::self_referencing;

pub type Unit = Maybe<()>;
pub type Error = Box<dyn std::error::Error + Sync + Send>;
pub type Maybe<T> = Result<T, Error>;

#[inline]
pub fn as_err<T: std::error::Error + Sync + Send + 'static>(e: T) -> Error {
    Box::new(e) as Error
}

#[self_referencing]
struct PinIoInternal {
    hal: Ft2232hHal<Initialized>,
    #[borrows(hal)]
    #[covariant]
    spi: Spi<'this, Ft2232h>,
    #[borrows(hal)]
    #[covariant]
    sel: OutputPin<'this, Ft2232h>,
}

pub type PinState = BitArr!(for 64, in u8);

pub struct PinIo {
    m: Pin<Box<PinIoInternal>>,
}

impl PinIo {
    pub fn new() -> Maybe<Self> {
        Ok(Self {
            m: Box::pin(
                PinIoInternalTryBuilder {
                    hal: Ft2232hHal::new()?.init(&MpsseSettings {
                        clock_frequency: Some(30_000_000),
                        ..Default::default()
                    })?,
                    spi_builder: |hal| hal.spi(),
                    sel_builder: |hal| Ok(hal.ad3()),
                }
                .try_build()?,
            ),
        })
    }
}

impl PinIo {
    pub fn transfer(&mut self, v: &PinState) -> Maybe<PinState> {
        let mut m = v.clone();
        self.m.with_sel_mut(|s| s.set_low())?;
        self.m.with_spi_mut(|s| s.transfer(m.as_raw_mut_slice()))?;
        self.m.with_sel_mut(|s| s.set_high())?;
        Ok(m)
    }
}
