// ask_modem.ts
export class ASKModem {
  constructor(
    private carrierFreq: number = 1000,
    private sampleRate: number = 44100,
    private amp1: number = 1.0,      // amplitude for bit 1
    private amp0: number = 0.3,      // amplitude for bit 0
    private bitDuration: number = 0.01
  ) {}

  /** Convert a bit array into a baseband ASK signal */
  modulate(bits: number[]): Float32Array {
    const samplesPerBit = Math.floor(this.sampleRate * this.bitDuration);
    const signal = new Float32Array(bits.length * samplesPerBit);

    for (let i = 0; i < bits.length; i++) {
      const amp = bits[i] === 1 ? this.amp1 : this.amp0;
      const offset = i * samplesPerBit;
      for (let j = 0; j < samplesPerBit; j++) {
        const t = (offset + j) / this.sampleRate;
        signal[offset + j] = amp * Math.sin(2 * Math.PI * this.carrierFreq * t);
      }
    }
    return signal;
  }

  /** Recover bits from an ASK signal using envelope detection */
  demodulate(signal: Float32Array, threshold?: number): number[] {
    if (threshold === undefined) threshold = (this.amp1 + this.amp0) / 2;
    const samplesPerBit = Math.floor(this.sampleRate * this.bitDuration);
    const bits: number[] = [];

    for (let i = 0; i < Math.floor(signal.length / samplesPerBit); i++) {
      const start = i * samplesPerBit;
      let envelope = 0;
      for (let j = 0; j < samplesPerBit; j++) {
        envelope += Math.abs(signal[start + j]);
      }
      envelope = (envelope / samplesPerBit) * 2; // rectify
      bits.push(envelope > threshold ? 1 : 0);
    }
    return bits;
  }
}