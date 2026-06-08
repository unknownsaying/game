// psk_modem.ts
type PSKMode = 'BPSK' | 'QPSK' | '8PSK';

export class PSKModem {
  private bitsPerSymbol: number;

  constructor(
    private carrierFreq: number = 1800,
    private sampleRate: number = 44100,
    private symbolDuration: number = 0.01,
    private amplitude: number = 1.0,
    private mode: PSKMode = 'BPSK'
  ) {
    this.bitsPerSymbol = { BPSK: 1, QPSK: 2, '8PSK': 3 }[mode];
  }

  /** Map bits to phase shifts */
  private phaseMap(symbol: number): number {
    switch (this.mode) {
      case 'BPSK': return symbol === 0 ? 0 : Math.PI;
      case 'QPSK': return Math.PI / 4 + symbol * Math.PI / 2;
      case '8PSK': return symbol * Math.PI / 4;
      default: return 0;
    }
  }

  /** Modulate bits into PSK signal */
  modulate(bits: number[]): Float32Array {
    const symbols: number[] = [];
    for (let i = 0; i < bits.length; i += this.bitsPerSymbol) {
      let sym = 0;
      for (let j = 0; j < this.bitsPerSymbol && i + j < bits.length; j++) {
        sym = (sym << 1) | bits[i + j];
      }
      symbols.push(sym);
    }

    const sps = Math.floor(this.sampleRate * this.symbolDuration);
    const signal = new Float32Array(symbols.length * sps);

    for (let i = 0; i < symbols.length; i++) {
      const phase = this.phaseMap(symbols[i]);
      const offset = i * sps;
      for (let j = 0; j < sps; j++) {
        const t = (offset + j) / this.sampleRate;
        signal[offset + j] = this.amplitude * Math.sin(2 * Math.PI * this.carrierFreq * t + phase);
      }
    }
    return signal;
  }

  /** Demodulate using coherent correlation */
  demodulate(signal: Float32Array): number[] {
    const sps = Math.floor(this.sampleRate * this.symbolDuration);
    const numSymbols = Math.floor(signal.length / sps);
    const bits: number[] = [];

    for (let i = 0; i < numSymbols; i++) {
      let I = 0, Q = 0;
      const offset = i * sps;
      for (let j = 0; j < sps; j++) {
        const t = (offset + j) / this.sampleRate;
        const s = signal[offset + j];
        I += s * Math.sin(2 * Math.PI * this.carrierFreq * t);
        Q += s * Math.cos(2 * Math.PI * this.carrierFreq * t);
      }

      switch (this.mode) {
        case 'BPSK':
          bits.push(I >= 0 ? 0 : 1);
          break;
        case 'QPSK':
          bits.push(...this.qpskDecision(I, Q));
          break;
        case '8PSK':
          bits.push(...this.psk8Decision(I, Q));
          break;
      }
    }
    return bits.slice(0, Math.floor(signal.length / sps) * this.bitsPerSymbol); // trim
  }

  private qpskDecision(I: number, Q: number): number[] {
    if (I >= 0 && Q >= 0) return [0, 0];
    if (I < 0 && Q >= 0) return [0, 1];
    if (I >= 0 && Q < 0) return [1, 0];
    return [1, 1];
  }

  private psk8Decision(I: number, Q: number): number[] {
    const phase = Math.atan2(Q, I) + (Q < 0 ? 2 * Math.PI : 0);
    const sym = Math.round(phase / (Math.PI / 4)) % 8;
    return sym.toString(2).padStart(3, '0').split('').map(Number);
  }
}