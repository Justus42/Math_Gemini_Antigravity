/// Deterministic SplitMix64 + Xoshiro256** PRNG (zero external crates).
#[derive(Clone, Debug)]
pub struct Rng {
    s: [u64; 4],
}

#[inline]
pub fn splitmix64(x: &mut u64) -> u64 {
    *x = x.wrapping_add(0x9e3779b97f4a7c15);
    let mut z = *x;
    z = (z ^ (z >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94d049bb133111eb);
    z ^ (z >> 31)
}

impl Rng {
    pub fn from_seed(mut seed: u64) -> Self {
        let s0 = splitmix64(&mut seed);
        let s1 = splitmix64(&mut seed);
        let s2 = splitmix64(&mut seed);
        let s3 = splitmix64(&mut seed);
        Self {
            s: [s0, s1, s2, s3],
        }
    }

    #[inline(always)]
    pub fn next_u64(&mut self) -> u64 {
        let result = self.s[1].wrapping_mul(5).rotate_left(7).wrapping_mul(9);
        let t = self.s[1] << 17;
        self.s[2] ^= self.s[0];
        self.s[3] ^= self.s[1];
        self.s[1] ^= self.s[2];
        self.s[0] ^= self.s[3];
        self.s[2] ^= t;
        self.s[3] = self.s[3].rotate_left(45);
        result
    }

    #[inline(always)]
    pub fn gen_usize(&mut self, bound: usize) -> usize {
        debug_assert!(bound > 0);
        // Fast Lemire-style reduction for 64-bit -> usize
        ((self.next_u64() as u128 * bound as u128) >> 64) as usize
    }

    #[inline(always)]
    pub fn gen_f64(&mut self) -> f64 {
        // Uniform in [0, 1)
        ((self.next_u64() >> 11) as f64) * (1.0 / ((1u64 << 53) as f64))
    }

    #[inline(always)]
    pub fn chance(&mut self, prob: f64) -> bool {
        if prob <= 0.0 {
            return false;
        }
        if prob >= 1.0 {
            return true;
        }
        self.gen_f64() < prob
    }
}
