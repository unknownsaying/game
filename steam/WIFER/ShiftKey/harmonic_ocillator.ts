// ifft_and_harmonic_oscillator.ts

/**
 * WiFi Router Signal Processing Chain
 * IFFT-based OFDM Modulation & Harmonic Oscillator Circuits
 */

// ============================================================================
// PART 1: COMPLEX NUMBER UTILITIES
// ============================================================================

class Complex {
    constructor(
        public real: number = 0,
        public imag: number = 0
    ) {}

    add(other: Complex): Complex {
        return new Complex(this.real + other.real, this.imag + other.imag);
    }

    subtract(other: Complex): Complex {
        return new Complex(this.real - other.real, this.imag - other.imag);
    }

    multiply(other: Complex): Complex {
        return new Complex(
            this.real * other.real - this.imag * other.imag,
            this.real * other.imag + this.imag * other.real
        );
    }

    scale(scalar: number): Complex {
        return new Complex(this.real * scalar, this.imag * scalar);
    }

    conjugate(): Complex {
        return new Complex(this.real, -this.imag);
    }

    magnitude(): number {
        return Math.sqrt(this.real * this.real + this.imag * this.imag);
    }

    phase(): number {
        return Math.atan2(this.imag, this.real);
    }

    static exp(theta: number): Complex {
        return new Complex(Math.cos(theta), Math.sin(theta));
    }

    static fromPolar(magnitude: number, phase: number): Complex {
        return new Complex(
            magnitude * Math.cos(phase),
            magnitude * Math.sin(phase)
        );
    }

    toString(): string {
        const sign = this.imag >= 0 ? '+' : '-';
        return `${this.real.toFixed(3)} ${sign} j${Math.abs(this.imag).toFixed(3)}`;
    }
}

// ============================================================================
// PART 2: INVERSE FAST FOURIER TRANSFORM (IFFT)
// ============================================================================

class IFFTProcessor {
    private fftSize: number;
    private twiddleFactors: Complex[][];
    private bitReversedIndices: number[];

    constructor(fftSize: number = 64) {
        // WiFi typically uses 64-point FFT for 20MHz channels
        this.fftSize = fftSize;
        this.twiddleFactors = this.precomputeTwiddleFactors();
        this.bitReversedIndices = this.precomputeBitReversal();
    }

    /**
     * Precompute twiddle factors W_N^n = e^(j*2*pi*n/N) for IFFT
     * Note: IFFT uses e^(j*2*pi*n/N) while FFT uses e^(-j*2*pi*n/N)
     */
    private precomputeTwiddleFactors(): Complex[][] {
        const factors: Complex[][] = [];
        let size = 2;

        while (size <= this.fftSize) {
            const stageFactors: Complex[] = [];
            for (let k = 0; k < size / 2; k++) {
                // IFFT twiddle factor: W_N^k = e^(j*2*pi*k/N)
                const angle = (2 * Math.PI * k) / size;
                stageFactors.push(Complex.exp(angle));
            }
            factors.push(stageFactors);
            size *= 2;
        }

        return factors;
    }

    /**
     * Bit reversal for Cooley-Tukey FFT algorithm
     */
    private precomputeBitReversal(): number[] {
        const indices: number[] = [];
        const bitsNeeded = Math.log2(this.fftSize);

        for (let i = 0; i < this.fftSize; i++) {
            let reversed = 0;
            for (let j = 0; j < bitsNeeded; j++) {
                if (i & (1 << j)) {
                    reversed |= (1 << (bitsNeeded - 1 - j));
                }
            }
            indices.push(reversed);
        }

        return indices;
    }

    /**
     * Perform Inverse FFT using Cooley-Tukey algorithm (Decimation-in-Time)
     * Converts frequency domain subcarriers to time domain signal
     */
    performIFFT(frequencyDomain: Complex[]): Complex[] {
        if (frequencyDomain.length !== this.fftSize) {
            // Zero-pad or truncate to match FFT size
            const padded = new Array(this.fftSize).fill(null).map(() => new Complex());
            const copyLength = Math.min(frequencyDomain.length, this.fftSize);
            for (let i = 0; i < copyLength; i++) {
                padded[i] = frequencyDomain[i];
            }
            frequencyDomain = padded;
        }

        // Bit-reversal permutation
        let timeDomain = this.bitReversedIndices.map(i => frequencyDomain[i]);

        // Iterative FFT stages
        let size = 2;
        let stageIndex = 0;

        while (size <= this.fftSize) {
            const halfSize = size / 2;
            const twiddles = this.twiddleFactors[stageIndex];

            for (let i = 0; i < this.fftSize; i += size) {
                for (let j = 0; j < halfSize; j++) {
                    const even = timeDomain[i + j];
                    const odd = timeDomain[i + j + halfSize].multiply(twiddles[j]);

                    // Butterfly operation
                    timeDomain[i + j] = even.add(odd);
                    timeDomain[i + j + halfSize] = even.subtract(odd);
                }
            }

            size *= 2;
            stageIndex++;
        }

        // Normalize by N for IFFT
        return timeDomain.map(sample => sample.scale(1.0 / this.fftSize));
    }

    /**
     * Generate OFDM symbol with cyclic prefix
     * Typical WiFi: 64 subcarriers, 16 sample cyclic prefix
     */
    generateOFDMSymbol(dataSubcarriers: Complex[], pilotSubcarriers?: Map<number, Complex>): Float32Array {
        // Create frequency domain representation (64 subcarriers for WiFi)
        const freqDomain = new Array(this.fftSize).fill(null).map(() => new Complex());

        // WiFi 802.11a/g subcarrier mapping:
        // Subcarriers -26 to -1 and 1 to 26: Data and pilots
        // Subcarrier 0: DC (null)
        // Subcarriers -32 to -27 and 27 to 31: Guard bands (null)

        const dataStart = Math.floor(this.fftSize / 2) - 26;
        
        // Place data subcarriers
        for (let i = 0; i < dataSubcarriers.length && i < 52; i++) {
            let position = dataStart + i;
            if (position >= this.fftSize / 2) position++; // Skip DC
            if (position < this.fftSize) {
                freqDomain[position] = dataSubcarriers[i];
            }
        }

        // Place pilot subcarriers if provided
        if (pilotSubcarriers) {
            pilotSubcarriers.forEach((value, position) => {
                const mappedPos = position < 0 ? 
                    this.fftSize / 2 + position : 
                    this.fftSize / 2 + position + 1;
                if (mappedPos >= 0 && mappedPos < this.fftSize) {
                    freqDomain[mappedPos] = value;
                }
            });
        }

        // Perform IFFT
        const timeDomain = this.performIFFT(freqDomain);

        // Add cyclic prefix (last 16 samples prepended)
        const cpLength = Math.floor(this.fftSize / 4); // Standard WiFi: 1/4 of symbol
        const withCP = new Float32Array((this.fftSize + cpLength) * 2); // I/Q interleaved

        // Copy cyclic prefix
        for (let i = 0; i < cpLength; i++) {
            const sample = timeDomain[this.fftSize - cpLength + i];
            withCP[i * 2] = sample.real;
            withCP[i * 2 + 1] = sample.imag;
        }

        // Copy main symbol
        for (let i = 0; i < this.fftSize; i++) {
            const sample = timeDomain[i];
            withCP[(i + cpLength) * 2] = sample.real;
            withCP[(i + cpLength) * 2 + 1] = sample.imag;
        }

        return withCP;
    }
}

// ============================================================================
// PART 3: HARMONIC OSCILLATOR CIRCUITS
// ============================================================================

/**
 * Base Harmonic Oscillator - The foundation of local oscillators in WiFi
 * Models a simple LC oscillator: d²x/dt² + ω²x = 0
 */
abstract class HarmonicOscillator {
    protected frequency: number;      // Resonant frequency in Hz
    protected amplitude: number;      // Oscillation amplitude
    protected phase: number;          // Current phase in radians
    protected dampingFactor: number;  // ζ (zeta) for damped oscillations
    protected qualityFactor: number;  // Q factor

    constructor(frequency: number, amplitude: number = 1.0, phase: number = 0) {
        this.frequency = frequency;
        this.amplitude = amplitude;
        this.phase = phase;
        this.dampingFactor = 0;
        this.qualityFactor = Infinity;
    }

    abstract getOutput(time: number): number;
    
    setDamping(damping: number): void {
        this.dampingFactor = damping;
        if (damping > 0) {
            this.qualityFactor = this.frequency / (2 * damping);
        }
    }
}

/**
 * Colpitts Oscillator - Common in WiFi RF frontends
 * Uses capacitive voltage divider for feedback
 */
class ColpittsOscillator extends HarmonicOscillator {
    private c1: number;  // Capacitor 1 (Farads)
    private c2: number;  // Capacitor 2 (Farads)
    private L: number;   // Inductor (Henries)

    constructor(
        frequency: number = 2.4e9,  // 2.4 GHz WiFi band
        c1: number = 1e-12,          // 1 pF
        c2: number = 10e-12,         // 10 pF
        amplitude: number = 1.0
    ) {
        // Calculate required inductance for resonance
        const cTotal = (c1 * c2) / (c1 + c2); // Series combination
        const L = 1 / (4 * Math.PI * Math.PI * frequency * frequency * cTotal);
        
        super(frequency, amplitude);
        this.c1 = c1;
        this.c2 = c2;
        this.L = L;
    }

    getOutput(time: number): number {
        const decayFactor = Math.exp(-this.dampingFactor * time);
        const oscillation = Math.sin(2 * Math.PI * this.frequency * time + this.phase);
        return this.amplitude * decayFactor * oscillation;
    }

    getFeedbackVoltage(output: number): number {
        // Capacitive voltage divider feedback
        return output * (this.c1 / (this.c1 + this.c2));
    }

    getComponentValues(): { inductor: number; cap1: number; cap2: number } {
        return {
            inductor: this.L,
            cap1: this.c1,
            cap2: this.c2
        };
    }
}

/**
 * Phase-Locked Loop (PLL) Oscillator - Used for frequency synthesis in WiFi
 * Models a VCO with phase detector and loop filter
 */
class PLLOscillator extends HarmonicOscillator {
    private referenceFrequency: number;
    private vcoGain: number;          // Kvco in Hz/V
    private phaseDetectorGain: number; // Kd in V/rad
    private loopFilter: number[];     // Loop filter coefficients
    private currentFrequency: number;
    private phaseError: number;

    constructor(
        referenceFreq: number = 20e6,  // 20 MHz crystal reference
        targetFreq: number = 2.4e9,    // 2.4 GHz output
        vcoGain: number = 100e6        // 100 MHz/V tuning sensitivity
    ) {
        super(targetFreq);
        this.referenceFrequency = referenceFreq;
        this.vcoGain = vcoGain;
        this.phaseDetectorGain = 0.3;  // Typical PFD gain
        this.loopFilter = [0.5, 0.1];  // Simple PI filter coefficients
        this.currentFrequency = targetFreq * 0.95; // Start slightly off
        this.phaseError = 0;
    }

    getOutput(time: number): number {
        // VCO output with current frequency
        const integralPhase = 2 * Math.PI * this.currentFrequency * time;
        return this.amplitude * Math.sin(integralPhase + this.phase);
    }

    updatePLL(referencePhase: number, vcoPhase: number): void {
        // Phase detector
        this.phaseError = referencePhase - vcoPhase;
        
        // Loop filter (simple PI controller)
        const controlVoltage = this.phaseDetectorGain * (
            this.loopFilter[0] * this.phaseError + 
            this.loopFilter[1] * this.phaseError
        );

        // Update VCO frequency
        this.currentFrequency += this.vcoGain * controlVoltage;
        
        // Clamp to reasonable range
        this.currentFrequency = Math.max(
            this.frequency * 0.5,
            Math.min(this.frequency * 1.5, this.currentFrequency)
        );
    }

    lockStatus(): { locked: boolean; frequencyError: number; phaseError: number } {
        const freqError = Math.abs(this.currentFrequency - this.frequency);
        return {
            locked: freqError < 1000 && Math.abs(this.phaseError) < 0.01,
            frequencyError: freqError,
            phaseError: this.phaseError
        };
    }
}

/**
 * IQ Modulator using two harmonic oscillators (Direct Conversion)
 * Critical for WiFi OFDM upconversion
 */
class IQModulator {
    private localOscillator: HarmonicOscillator;
    private ninetyDegreePhaseShift: number = Math.PI / 2;
    private carrierFrequency: number;
    private amplitudeImbalance: number;  // Gain mismatch between I and Q
    private phaseImbalance: number;      // Phase error from 90 degrees

    constructor(
        carrierFreq: number = 2.4e9,
        oscillator: HarmonicOscillator
    ) {
        this.carrierFrequency = carrierFreq;
        this.localOscillator = oscillator;
        this.amplitudeImbalance = 0;  // Ideal case
        this.phaseImbalance = 0;      // Ideal case
    }

    /**
     * Upconvert baseband I/Q signals to RF
     * RF(t) = I(t)*cos(ωt) - Q(t)*sin(ωt)
     */
    upconvert(iSignal: Float32Array, qSignal: Float32Array, sampleRate: number): Float32Array {
        const rfSignal = new Float32Array(iSignal.length);

        for (let n = 0; n < iSignal.length; n++) {
            const t = n / sampleRate;
            const cos_lo = Math.cos(2 * Math.PI * this.carrierFrequency * t);
            
            // Q channel with possible phase imbalance
            const phaseShift = this.ninetyDegreePhaseShift + this.phaseImbalance;
            const sin_lo = Math.sin(2 * Math.PI * this.carrierFrequency * t + phaseShift);

            // Apply amplitude imbalance
            const iComponent = iSignal[n] * cos_lo;
            const qComponent = qSignal[n] * sin_lo * (1 + this.amplitudeImbalance);

            rfSignal[n] = iComponent - qComponent;
        }

        return rfSignal;
    }

    setImbalance(amplitudeImbalance: number, phaseImbalance: number): void {
        this.amplitudeImbalance = amplitudeImbalance;
        this.phaseImbalance = phaseImbalance * Math.PI / 180; // Convert degrees to radians
    }

    /**
     * Generate test I/Q signals
     */
    static generateTestSignals(
        frequency: number,
        sampleRate: number,
        duration: number
    ): { i: Float32Array; q: Float32Array } {
        const numSamples = Math.floor(sampleRate * duration);
        const i = new Float32Array(numSamples);
        const q = new Float32Array(numSamples);

        for (let n = 0; n < numSamples; n++) {
            const t = n / sampleRate;
            i[n] = Math.cos(2 * Math.PI * frequency * t);
            q[n] = Math.sin(2 * Math.PI * frequency * t);
        }

        return { i, q };
    }
}

// ============================================================================
// PART 4: CRYSTAL OSCILLATOR (WiFi Reference Clock)
// ============================================================================

/**
 * Quartz Crystal Oscillator Model
 * Provides the stable 20-40 MHz reference for WiFi PLLs
 * Equivalent circuit: Series RLC with parallel capacitance
 */
class CrystalOscillator {
    private seriesResistance: number;   // Rs - typically 10-100 ohms
    private seriesInductance: number;   // Ls - motional inductance
    private seriesCapacitance: number;  // Cs - motional capacitance (fF range)
    private parallelCapacitance: number; // Cp - holder capacitance (pF range)
    
    private seriesResonantFreq: number;
    private parallelResonantFreq: number;
    private qualityFactor: number;

    constructor(
        frequency: number = 20e6,       // 20 MHz WiFi reference
        seriesR: number = 50,
        qualityFactor: number = 50000   // Typical quartz Q factor
    ) {
        this.seriesResistance = seriesR;
        this.qualityFactor = qualityFactor;
        
        // Calculate motional parameters
        this.seriesInductance = (qualityFactor * seriesR) / (2 * Math.PI * frequency);
        this.seriesCapacitance = 1 / (4 * Math.PI * Math.PI * frequency * frequency * this.seriesInductance);
        this.parallelCapacitance = 5e-12; // 5 pF typical holder capacitance
        
        this.seriesResonantFreq = frequency;
        // Parallel resonance is slightly higher due to Cp
        const cTotal = (this.seriesCapacitance * this.parallelCapacitance) / 
                       (this.seriesCapacitance + this.parallelCapacitance);
        this.parallelResonantFreq = 1 / (2 * Math.PI * Math.sqrt(this.seriesInductance * cTotal));
    }

    /**
     * Crystal impedance at given frequency
     */
    getImpedance(frequency: number): Complex {
        const omega = 2 * Math.PI * frequency;
        
        // Motional arm impedance
        const zmotional = new Complex(
            this.seriesResistance,
            omega * this.seriesInductance - 1 / (omega * this.seriesCapacitance)
        );
        
        // Parallel capacitance admittance
        const yParallel = new Complex(0, omega * this.parallelCapacitance);
        
        // Total impedance: Zmotional || Zparallel
        const zParallel = new Complex(0, -1 / (omega * this.parallelCapacitance));
        const numerator = zmotional.multiply(zParallel);
        const denominator = zmotional.add(zParallel);
        
        return new Complex(
            numerator.real / denominator.real,
            numerator.imag / denominator.imag
        );
    }

    getSpecifications(): object {
        return {
            seriesResonantFrequency: this.seriesResonantFreq / 1e6 + ' MHz',
            parallelResonantFrequency: this.parallelResonantFreq / 1e6 + ' MHz',
            qualityFactor: this.qualityFactor,
            loadCapacitance: this.parallelCapacitance * 1e12 + ' pF',
            motionalCapacitance: this.seriesCapacitance * 1e15 + ' fF',
            motionalInductance: this.seriesInductance * 1e3 + ' mH'
        };
    }
}

// ============================================================================
// PART 5: WiFi ROUTER INTEGRATION
// ============================================================================

/**
 * Complete WiFi Router Baseband + RF Chain
 * Integrates IFFT-based OFDM and harmonic oscillators
 */
class WiFiRouterSignalChain {
    private ifftProcessor: IFFTProcessor;
    private crystal: CrystalOscillator;
    private pll: PLLOscillator;
    private colpittsOscillator: ColpittsOscillator;
    private iqModulator: IQModulator;
    
    // WiFi physical layer parameters
    private readonly FFT_SIZE = 64;
    private readonly CYCLIC_PREFIX_RATIO = 0.25;
    private readonly CARRIER_FREQUENCY = 2.4e9; // 2.4 GHz band
    private readonly SAMPLE_RATE = 20e6;         // 20 MHz bandwidth
    private readonly SUBCARRIER_SPACING = 312.5e3; // 312.5 kHz

    constructor() {
        // Initialize signal processing chain
        this.ifftProcessor = new IFFTProcessor(this.FFT_SIZE);
        this.crystal = new CrystalOscillator(20e6, 50, 50000);
        this.pll = new PLLOscillator(20e6, this.CARRIER_FREQUENCY, 100e6);
        this.colpittsOscillator = new ColpittsOscillator(this.CARRIER_FREQUENCY);
        this.iqModulator = new IQModulator(this.CARRIER_FREQUENCY, this.colpittsOscillator);
    }

    /**
     * Transmit data through complete WiFi chain
     */
    transmit(dataBits: number[]): {
        ofdmBaseband: Float32Array;
        rfSignal: Float32Array;
        oscillatorOutput: number[];
    } {
        // Step 1: Map bits to QAM symbols (simplified BPSK shown)
        const qamSymbols = this.mapBitsToQAM(dataBits);
        
        // Step 2: Generate OFDM symbol using IFFT
        const complexSymbols = qamSymbols.map(sym => 
            new Complex(sym.real, sym.imag)
        );
        
        const ofdmBaseband = this.ifftProcessor.generateOFDMSymbol(complexSymbols);
        
        // Step 3: Extract I and Q components from interleaved baseband
        const iBaseband = new Float32Array(ofdmBaseband.length / 2);
        const qBaseband = new Float32Array(ofdmBaseband.length / 2);
        
        for (let i = 0; i < ofdmBaseband.length / 2; i++) {
            iBaseband[i] = ofdmBaseband[i * 2];     // Real part = I
            qBaseband[i] = ofdmBaseband[i * 2 + 1]; // Imag part = Q
        }
        
        // Step 4: Upconvert to RF using IQ modulator (harmonic oscillator)
        const rfSignal = this.iqModulator.upconvert(
            iBaseband, 
            qBaseband, 
            this.SAMPLE_RATE
        );
        
        // Step 5: Sample oscillator output for analysis
        const oscSamples: number[] = [];
        const totalTime = ofdmBaseband.length / (2 * this.SAMPLE_RATE);
        const numOscSamples = 100;
        
        for (let i = 0; i < numOscSamples; i++) {
            const t = (i / numOscSamples) * totalTime;
            oscSamples.push(this.colpittsOscillator.getOutput(t));
        }
        
        return {
            ofdmBaseband,
            rfSignal,
            oscillatorOutput: oscSamples
        };
    }

    /**
     * Map bits to QAM constellation points
     * Simplified BPSK: 0 -> -1, 1 -> +1
     */
    private mapBitsToQAM(bits: number[]): Array<{real: number; imag: number}> {
        return bits.map(bit => ({
            real: bit === 0 ? -1 : 1,
            imag: 0  // BPSK only uses I axis
        }));
    }

    /**
     * Monitor system performance
     */
    getSystemMetrics(): object {
        const pllStatus = this.pll.lockStatus();
        const crystalSpecs = this.crystal.getSpecifications();
        const colpittsComponents = this.colpittsOscillator.getComponentValues();
        
        return {
            carrierFrequency: this.CARRIER_FREQUENCY / 1e6 + ' MHz',
            sampleRate: this.SAMPLE_RATE / 1e6 + ' MHz',
            fftSize: this.FFT_SIZE,
            pllLocked: pllStatus.locked,
            pllFrequencyError: pllStatus.frequencyError.toFixed(2) + ' Hz',
            oscillatorType: 'Colpitts (LC) with Crystal PLL reference',
            ...crystalSpecs,
            colpittsInductor: (colpittsComponents.inductor * 1e9).toFixed(2) + ' nH',
            colpittsCapacitor1: (colpittsComponents.cap1 * 1e12).toFixed(2) + ' pF',
            colpittsCapacitor2: (colpittsComponents.cap2 * 1e12).toFixed(2) + ' pF'
        };
    }
}

// ============================================================================
// PART 6: DEMONSTRATION & VISUALIZATION
// ============================================================================

class WiFiSignalChainDemo {
    static run() {
        console.log('=== WiFi Router IFFT & Harmonic Oscillator Demo ===\n');

        // Initialize the complete signal chain
        const router = new WiFiRouterSignalChain();
        
        // Display system metrics
        console.log('System Configuration:');
        console.log(JSON.stringify(router.getSystemMetrics(), null, 2));
        
        // Generate test data
        const testData = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0];
        console.log(`\nTransmitting ${testData.length} bits: ${testData.join(' ')}`);
        
        // Process through complete chain
        const result = router.transmit(testData);
        
        console.log(`\nOFDM Baseband Signal: ${result.ofdmBaseband.length} samples`);
        console.log(`RF Signal: ${result.rfSignal.length} samples`);
        
        // Show IFFT output samples
        console.log('\nIFFT Output (first 10 complex samples):');
        for (let i = 0; i < 10 && i * 2 < result.ofdmBaseband.length; i++) {
            const real = result.ofdmBaseband[i * 2].toFixed(4);
            const imag = result.ofdmBaseband[i * 2 + 1].toFixed(4);
            console.log(`  Sample ${i}: ${real} + j${imag}`);
        }
        
        // Show oscillator output
        console.log('\nHarmonic Oscillator Output (first 10 samples):');
        for (let i = 0; i < 10 && i < result.oscillatorOutput.length; i++) {
            console.log(`  t=${(i * 0.1).toFixed(1)}ns: ${result.oscillatorOutput[i].toFixed(4)}V`);
        }

        // Demonstrate PLL locking
        console.log('\n=== PLL Frequency Synthesis ===');
        const pll = new PLLOscillator(20e6, 2.4e9);
        
        console.log('Simulating PLL lock acquisition...');
        for (let step = 0; step < 5; step++) {
            const refPhase = 2 * Math.PI * 20e6 * step * 1e-9;
            const vcoPhase = 2 * Math.PI * 2.4e9 * step * 1e-9;
            pll.updatePLL(refPhase, vcoPhase);
            
            const status = pll.lockStatus();
            console.log(`  Step ${step + 1}: Locked=${status.locked}, ` +
                       `Freq Error=${status.frequencyError.toFixed(0)}Hz, ` +
                       `Phase Error=${status.phaseError.toFixed(4)}rad`);
        }
        
        // Crystal oscillator analysis
        console.log('\n=== Crystal Oscillator Analysis ===');
        const crystal = new CrystalOscillator(20e6);
        const testFrequencies = [19.9e6, 19.99e6, 20e6, 20.01e6, 20.1e6];
        
        console.log('Impedance vs Frequency:');
        testFrequencies.forEach(freq => {
            const impedance = crystal.getImpedance(freq);
            console.log(`  ${freq/1e6} MHz: Z = ${impedance.magnitude().toFixed(2)}Ω ` +
                       `at ${(impedance.phase() * 180 / Math.PI).toFixed(2)}°`);
        });
        
        console.log('\n✓ WiFi Router Signal Chain Demonstration Complete');
    }
}

// Run the demonstration
WiFiSignalChainDemo.run();

export {
    Complex,
    IFFTProcessor,
    HarmonicOscillator,
    ColpittsOscillator,
    PLLOscillator,
    CrystalOscillator,
    IQModulator,
    WiFiRouterSignalChain,
    WiFiSignalChainDemo
};