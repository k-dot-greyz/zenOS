//! `keel.sos` / `keel.ir` emit. Little-endian, documented headers.

use crate::CoeffsF64;

const SOS_MAGIC: &[u8; 8] = b"KEELSOS\n";
const IR_MAGIC: &[u8; 8] = b"KEELIR\n\0";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Phase {
    Linear = 0,
    Min = 1,
    Mixed = 2,
}

impl Phase {
    fn from_u8(v: u8) -> Option<Self> {
        match v {
            0 => Some(Self::Linear),
            1 => Some(Self::Min),
            2 => Some(Self::Mixed),
            _ => None,
        }
    }
}

#[derive(Clone, Debug, PartialEq)]
pub struct SosFile {
    pub sections: Vec<CoeffsF64>,
}

impl SosFile {
    pub fn encode(&self) -> Vec<u8> {
        let mut o = Vec::with_capacity(8 + 4 + self.sections.len() * 20);
        o.extend_from_slice(SOS_MAGIC);
        o.extend_from_slice(&(self.sections.len() as u32).to_le_bytes());
        for s in &self.sections {
            for x in [
                s.b0 as f32,
                s.b1 as f32,
                s.b2 as f32,
                s.a1 as f32,
                s.a2 as f32,
            ] {
                o.extend_from_slice(&x.to_le_bytes());
            }
        }
        o
    }

    pub fn decode(bytes: &[u8]) -> Result<Self, &'static str> {
        if bytes.len() < 12 || &bytes[..8] != SOS_MAGIC {
            return Err("bad keel.sos magic");
        }
        let n = u32::from_le_bytes(bytes[8..12].try_into().unwrap()) as usize;
        let need = 12 + n * 20;
        if bytes.len() < need {
            return Err("truncated keel.sos");
        }
        let mut sections = Vec::with_capacity(n);
        let mut off = 12;
        for _ in 0..n {
            let mut f = [0.0f32; 5];
            for slot in &mut f {
                *slot = f32::from_le_bytes(bytes[off..off + 4].try_into().unwrap());
                off += 4;
            }
            sections.push(CoeffsF64 {
                b0: f[0] as f64,
                b1: f[1] as f64,
                b2: f[2] as f64,
                a1: f[3] as f64,
                a2: f[4] as f64,
            });
        }
        Ok(Self { sections })
    }
}

#[derive(Clone, Debug, PartialEq)]
pub struct IrFile {
    pub sr: f32,
    pub latency: f32,
    pub phase: Phase,
    pub samples: Vec<f32>,
}

impl IrFile {
    pub fn encode(&self) -> Vec<u8> {
        let mut o = Vec::with_capacity(8 + 16 + self.samples.len() * 4);
        o.extend_from_slice(IR_MAGIC);
        o.extend_from_slice(&self.sr.to_le_bytes());
        o.extend_from_slice(&self.latency.to_le_bytes());
        o.push(self.phase as u8);
        o.extend_from_slice(&[0u8, 0, 0]);
        o.extend_from_slice(&(self.samples.len() as u32).to_le_bytes());
        for s in &self.samples {
            o.extend_from_slice(&s.to_le_bytes());
        }
        o
    }

    pub fn decode(bytes: &[u8]) -> Result<Self, &'static str> {
        if bytes.len() < 24 || &bytes[..8] != IR_MAGIC {
            return Err("bad keel.ir magic");
        }
        let sr = f32::from_le_bytes(bytes[8..12].try_into().unwrap());
        let latency = f32::from_le_bytes(bytes[12..16].try_into().unwrap());
        let phase = Phase::from_u8(bytes[16]).ok_or("bad phase")?;
        let n = u32::from_le_bytes(bytes[20..24].try_into().unwrap()) as usize;
        let need = 24 + n * 4;
        if bytes.len() < need {
            return Err("truncated keel.ir");
        }
        let mut samples = Vec::with_capacity(n);
        let mut off = 24;
        for _ in 0..n {
            samples.push(f32::from_le_bytes(bytes[off..off + 4].try_into().unwrap()));
            off += 4;
        }
        Ok(Self {
            sr,
            latency,
            phase,
            samples,
        })
    }

    /// Mono IEEE-float WAV. Header carries sr; latency/phase live in `keel.ir` only.
    pub fn encode_wav(&self) -> Vec<u8> {
        let data_bytes = (self.samples.len() * 4) as u32;
        let mut o = Vec::with_capacity(44 + data_bytes as usize);
        o.extend_from_slice(b"RIFF");
        o.extend_from_slice(&(36 + data_bytes).to_le_bytes());
        o.extend_from_slice(b"WAVE");
        o.extend_from_slice(b"fmt ");
        o.extend_from_slice(&16u32.to_le_bytes());
        o.extend_from_slice(&3u16.to_le_bytes()); // IEEE float
        o.extend_from_slice(&1u16.to_le_bytes());
        let sr = self.sr as u32;
        o.extend_from_slice(&sr.to_le_bytes());
        o.extend_from_slice(&(sr * 4).to_le_bytes());
        o.extend_from_slice(&4u16.to_le_bytes());
        o.extend_from_slice(&32u16.to_le_bytes());
        o.extend_from_slice(b"data");
        o.extend_from_slice(&data_bytes.to_le_bytes());
        for s in &self.samples {
            o.extend_from_slice(&s.to_le_bytes());
        }
        o
    }
}
