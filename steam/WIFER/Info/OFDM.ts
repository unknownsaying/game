// ofdm.ts
/**
 * Orthogonal Frequency Division Multiplexing (OFDM)
 * Uses IFFT/FFT to create orthogonal subcarriers, plus cyclic prefix for ISI mitigation.
 */

// Minimal complex number class
class Complex {
  constructor(public re: number = 0, public im: number = 0) {}

  add(c: Complex): Complex {
    return new Complex(this.re + c.re, this.im + c.im);
  }

  sub(c: Complex): Complex {
    return new Complex(this.re - c.re, this.im - c.im);
  }

  mul(c: Complex): Complex {
    return new Complex(
      this.re * c.re - this.im * c.im,
      this.re * c.im + this.im * c.re
    );
  }

  scale(s: number): Complex {
    return new Complex(this.re * s, this.im * s);
  }
}

class OFDMSystem {
  private N: number;        // number of subcarriers (IFFT size)
  private cpLen: number;    // cyclic prefix length
  private sampleRate: number;

  constructor(N: number = 64, cpRatio: number = 0.25, sampleRate: number = 20e6) {
    this.N = N;
    this.cpLen = Math.floor(N * cpRatio);
    this.sampleRate = sampleRate;
  }

  /**
   * IFFT (Cooley‑Tukey, Decimation‑in‑Time)
   */
  private ifft(input: Complex[]): Complex[] {
    const N = input.length;
    // Bit‑reverse copy
    const bits = Math.log2(N);
    const x: Complex[] = new Array(N);
    for (let i = 0; i < N; i++) {
      let rev = 0;
      for (let j = 0; j < bits; j++) {
        if (i & (1 << j)) rev |= 1 << (bits - 1 - j);
      }
      x[rev] = input[i];
    }

    // Butterfly stages
    for (let size = 2; size <= N; size *= 2) {
      const half = size / 2;
      const twiddleAngle = (2 * Math.PI) / size; // IFFT uses +j
      for (let i = 0; i < N; i += size) {
        for (let j = 0; j < half; j++) {
          const w = new Complex(Math.cos(twiddleAngle * j), Math.sin(twiddleAngle * j));
          const even = x[i + j];
          const odd = x[i + j + half].mul(w);
          x[i + j] = even.add(odd);
          x[i + j + half] = even.sub(odd);
        }
      }
    }
    // Scale by 1/N
    return x.map(s => s.scale(1 / N));
  }

  /**
   * FFT (same structure, with negative twiddle and no final scaling)
   */
  private fft(input: Complex[]): Complex[] {
    const N = input.length;
    const bits = Math.log2(N);
    const x: Complex[] = new Array(N);
    for (let i = 0; i < N; i++) {
      let rev = 0;
      for (let j = 0; j < bits; j++) {
        if (i & (1 << j)) rev |= 1 << (bits - 1 - j);
      }
      x[rev] = input[i];
    }

    for (let size = 2; size <= N; size *= 2) {
      const half = size / 2;
      const twiddleAngle = (-2 * Math.PI) / size; // FFT uses -j
      for (let i = 0; i < N; i += size) {
        for (let j = 0; j < half; j++) {
          const w = new Complex(Math.cos(twiddleAngle * j), Math.sin(twiddleAngle * j));
          const even = x[i + j];
          const odd = x[i + j + half].mul(w);
          x[i + j] = even.add(odd);
          x[i + j + half] = even.sub(odd);
        }
      }
    }
    return x;
  }

  /**
   * OFDM modulation: map QAM symbols to subcarriers, IFFT, add cyclic prefix.
   * @param symbols complex symbols (length <= N) placed on subcarriers (DC null)
   * @returns interleaved I/Q time‑domain signal with CP
   */
  modulate(symbols: Complex[]): Float32Array {
    // Build frequency‑domain vector of length N, DC (index 0) is null
    const freqDom = new Array<Complex>(this.N);
    for (let i = 0; i < this.N; i++) freqDom[i] = new Complex(0, 0);

    // Place symbols on positive and negative subcarriers, skipping DC
    const halfN = this.N / 2;
    for (let k = 0; k < symbols.length && k < this.N - 1; k++) {
      let index = k + 1;
      if (index >= halfN) index++; // skip DC at halfN
      if (index < this.N) {
        freqDom[index] = symbols[k];
      }
    }

    // IFFT
    const timeDom = this.ifft(freqDom);

    // Add cyclic prefix
    const totalLen = this.N + this.cpLen;
    const signal = new Float32Array(totalLen * 2); // IQ interleaved
    for (let i = 0; i < this.cpLen; i++) {
      const s = timeDom[this.N - this.cpLen + i];
      signal[2 * i] = s.re;
      signal[2 * i + 1] = s.im;
    }
    for (let i = 0; i < this.N; i++) {
      const s = timeDom[i];
      signal[2 * (i + this.cpLen)] = s.re;
      signal[2 * (i + this.cpLen) + 1] = s.im;
    }

    return signal;
  }

  /**
   * OFDM demodulation: remove cyclic prefix, FFT, extract subcarriers.
   * @param signal interleaved I/Q time‑domain signal with CP
   * @returns complex symbols (length N‑1, DC excluded)
   */
  demodulate(signal: Float32Array): Complex[] {
    const totalSamples = signal.length / 2;
    if (totalSamples !== this.N + this.cpLen) {
      throw new Error(`Expected ${this.N + this.cpLen} IQ samples, got ${totalSamples}`);
    }

    // Remove CP
    const timeDom = new Array<Complex>(this.N);
    for (let i = 0; i < this.N; i++) {
      const re = signal[2 * (i + this.cpLen)];
      const im = signal[2 * (i + this.cpLen) + 1];
      timeDom[i] = new Complex(re, im);
    }

    // FFT
    const freqDom = this.fft(timeDom);

    // Extract subcarriers (skip DC at index halfN)
    const halfN = this.N / 2;
    const symbols: Complex[] = [];
    for (let k = 1; k < this.N; k++) {
      if (k === halfN) continue;
      symbols.push(freqDom[k]);
    }
    return symbols;
  }
}

// ---- demonstration ----
function demoOFDM() {
  const ofdm = new OFDMSystem(64, 0.25, 20e6);

  // BPSK symbols: [1, -1, 1, -1, ...] on 10 subcarriers
  const numSymbols = 10;
  const bpskSymbols = Array.from({ length: numSymbols }, (_, i) => {
    const bit = i % 2; // 0 or 1
    return new Complex(bit === 0 ? -1 : 1, 0); // BPSK: 0 -> -1, 1 -> +1
  });

  const txSignal = ofdm.modulate(bpskSymbols);
  console.log('OFDM Modulated signal (first 10 IQ samples):');
  for (let i = 0; i < 10 && i * 2 < txSignal.length; i++) {
    console.log(`  ${txSignal[2 * i].toFixed(4)} + j${txSignal[2 * i + 1].toFixed(4)}`);
  }

  // Demodulate (perfect channel)
  const received = ofdm.demodulate(txSignal);
  console.log('Demodulated symbols (first 4):');
  for (let i = 0; i < 4; i++) {
    console.log(`  ${received[i].re.toFixed(4)} + j${received[i].im.toFixed(4)}`);
  }
}

demoOFDM();

export { OFDMSystem };