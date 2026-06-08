// fsk_modem.ts
export class FSKModem {
  constructor(
    private freq1: number = 1200,    // mark frequency (bit 1)
    private freq0: number = 2200,    // space frequency (bit 0)
    private sampleRate: number = 44100,
    private bitDuration: number = 0.01,
    private amplitude: number = 1.0
  ) {}

  /** Modulate bits into continuous‑phase FSK signal */
  modulate(bits: number[]): Float32Array {
    const samplesPerBit = Math.floor(this.sampleRate * this.bitDuration);
    const signal = new Float32Array(bits.length * samplesPerBit);
    let phase = 0;

    for (let i = 0; i < bits.length; i++) {
      const freq = bits[i] === 1 ? this.freq1 : this.freq0;
      const offset = i * samplesPerBit;
      for (let j = 0; j < samplesPerBit; j++) {
        const t = (offset + j) / this.sampleRate;
        signal[offset + j] = this.amplitude * Math.sin(2 * Math.PI * freq * t + phase);
      }
      phase += 2 * Math.PI * freq * this.bitDuration;
      phase %= 2 * Math.PI; // keep phase continuous
    }
    return signal;
  }

  /** Non‑coherent demodulation using Goertzel filters */
  demodulate(signal: Float32Array): number[] {
    const samplesPerBit = Math.floor(this.sampleRate * this.bitDuration);
    const bits: number[] = [];
    const k1 = Math.round((samplesPerBit * this.freq1) / this.sampleRate);
    const k0 = Math.round((samplesPerBit * this.freq0) / this.sampleRate);
    const coeff1 = 2 * Math.cos((2 * Math.PI * k1) / samplesPerBit);
    const coeff0 = 2 * Math.cos((2 * Math.PI * k0) / samplesPerBit);

    for (let i = 0; i < Math.floor(signal.length / samplesPerBit); i++) {
      let q1_0 = 0, q1_1 = 0, q1_2 = 0;
      let q0_0 = 0, q0_1 = 0, q0_2 = 0;

      for (let j = 0; j < samplesPerBit; j++) {
        const s = signal[i * samplesPerBit + j];
        // Goertzel for f1
        q1_0 = coeff1 * q1_1 - q1_2 + s;
        q1_2 = q1_1; q1_1 = q1_0;
        // Goertzel for f0
        q0_0 = coeff0 * q0_1 - q0_2 + s;
        q0_2 = q0_1; q0_1 = q0_0;
      }

      const energy1 = q1_1 * q1_1 + q1_2 * q1_2 - coeff1 * q1_1 * q1_2;
      const energy0 = q0_1 * q0_1 + q0_2 * q0_2 - coeff0 * q0_1 * q0_2;
      bits.push(energy1 > energy0 ? 1 : 0);
    }
    return bits;
  }
}