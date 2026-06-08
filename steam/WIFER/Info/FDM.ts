// fdm.ts
/**
 * Frequency Division Multiplexing (FDM)
 * Combines multiple independent signals by shifting them to different carrier frequencies.
 * No guard bands are inserted – in a real system they would be added to avoid inter-channel interference.
 */

class FDMSystem {
  private carriers: number[];  // carrier frequencies in Hz
  private sampleRate: number;

  constructor(carriers: number[], sampleRate: number = 44100) {
    this.carriers = carriers;
    this.sampleRate = sampleRate;
  }

  /**
   * Modulate/FDM‑multiplex several baseband signals onto distinct carriers.
   * @param signals Array of baseband signals (each a Float32Array of the same length)
   * @returns composite FDM signal
   */
  multiplex(signals: Float32Array[]): Float32Array {
    const length = signals[0].length;
    const composite = new Float32Array(length);

    for (let ch = 0; ch < signals.length; ch++) {
      const freq = this.carriers[ch];
      const sig = signals[ch];
      for (let n = 0; n < length; n++) {
        const t = n / this.sampleRate;
        composite[n] += sig[n] * Math.cos(2 * Math.PI * freq * t);
      }
    }
    return composite;
  }

  /**
   * Demultiplex a composite FDM signal back into individual baseband channels.
   * Uses simple synchronous demodulation (multiply by carrier + low‑pass filter via moving average).
   */
  demultiplex(composite: Float32Array, channelCount: number): Float32Array[] {
    const length = composite.length;
    const signals: Float32Array[] = [];

    for (let ch = 0; ch < channelCount; ch++) {
      const freq = this.carriers[ch];
      const demoded = new Float32Array(length);

      // Multiply by carrier (coherent demodulation)
      for (let n = 0; n < length; n++) {
        const t = n / this.sampleRate;
        demoded[n] = composite[n] * Math.cos(2 * Math.PI * freq * t);
      }

      // Simple moving‑average low‑pass filter (remove 2× carrier component)
      const filterSize = Math.floor(this.sampleRate / (2 * freq)); // one period of carrier
      const filtered = new Float32Array(length);
      for (let n = 0; n < length; n++) {
        let sum = 0;
        const start = Math.max(0, n - filterSize);
        for (let k = start; k <= n; k++) {
          sum += demoded[k];
        }
        filtered[n] = (2 * sum) / (n - start + 1); // amplitude scaling
      }

      signals.push(filtered);
    }
    return signals;
  }
}

// ---------- demonstration ----------
function demoFDM() {
  const sampleRate = 44100;
  const carriers = [1000, 3000, 5000]; // Hz
  const fdm = new FDMSystem(carriers, sampleRate);

  // Generate three different baseband tones (300, 600, 900 Hz)
  const duration = 0.01; // 10 ms
  const samples = Math.floor(sampleRate * duration);
  const signal1 = new Float32Array(samples);
  const signal2 = new Float32Array(samples);
  const signal3 = new Float32Array(samples);

  for (let i = 0; i < samples; i++) {
    const t = i / sampleRate;
    signal1[i] = Math.sin(2 * Math.PI * 300 * t);
    signal2[i] = Math.sin(2 * Math.PI * 600 * t);
    signal3[i] = Math.sin(2 * Math.PI * 900 * t);
  }

  const composite = fdm.multiplex([signal1, signal2, signal3]);
  const recovered = fdm.demultiplex(composite, 3);

  console.log('FDM Demo:');
  console.log(`  Composite signal length: ${composite.length} samples`);
  console.log(`  Recovered channel 1 first sample: ${recovered[0][0].toFixed(4)}`);
  console.log(`  Recovered channel 2 first sample: ${recovered[1][0].toFixed(4)}`);
  console.log(`  Recovered channel 3 first sample: ${recovered[2][0].toFixed(4)}`);
}

demoFDM();

export { FDMSystem };