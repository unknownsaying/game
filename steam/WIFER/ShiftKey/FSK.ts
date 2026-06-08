// fsk_modem.ts
class FSKModem {
    private frequency1: number;     // 比特1的频率 (Hz)
    private frequency0: number;     // 比特0的频率 (Hz)
    private sampleRate: number;     // 采样率 (Hz)
    private bitDuration: number;    // 比特持续时间 (秒)
    private amplitude: number;      // 信号幅度

    constructor(
        freq1: number = 1200,       // Mark频率
        freq0: number = 2200,       // Space频率
        sampleRate: number = 44100,
        bitDuration: number = 0.01,
        amplitude: number = 1.0
    ) {
        this.frequency1 = freq1;
        this.frequency0 = freq0;
        this.sampleRate = sampleRate;
        this.bitDuration = bitDuration;
        this.amplitude = amplitude;
    }

    // 调制：数字比特流 -> FSK信号
    modulate(bits: number[]): Float32Array {
        const samplesPerBit = Math.floor(this.sampleRate * this.bitDuration);
        const totalSamples = bits.length * samplesPerBit;
        const signal = new Float32Array(totalSamples);
        let phase = 0; // 连续相位

        for (let i = 0; i < bits.length; i++) {
            const frequency = bits[i] === 1 ? this.frequency1 : this.frequency0;
            const startSample = i * samplesPerBit;
            
            for (let j = 0; j < samplesPerBit; j++) {
                const t = (startSample + j) / this.sampleRate;
                signal[startSample + j] = this.amplitude * 
                    Math.sin(2 * Math.PI * frequency * t + phase);
            }
            
            // 更新相位以确保连续性
            phase += 2 * Math.PI * frequency * this.bitDuration;
            phase = phase % (2 * Math.PI);
        }
        
        return signal;
    }

    // 非相干解调（使用带通滤波器）
    demodulate(signal: Float32Array): number[] {
        const samplesPerBit = Math.floor(this.sampleRate * this.bitDuration);
        const numBits = Math.floor(signal.length / samplesPerBit);
        const bits: number[] = [];

        for (let i = 0; i < numBits; i++) {
            const startSample = i * samplesPerBit;
            let energy1 = 0;
            let energy0 = 0;

            // 使用Goertzel算法检测频率
            const k1 = Math.floor(0.5 + (samplesPerBit * this.frequency1) / this.sampleRate);
            const k0 = Math.floor(0.5 + (samplesPerBit * this.frequency0) / this.sampleRate);
            
            const coeff1 = 2 * Math.cos(2 * Math.PI * k1 / samplesPerBit);
            const coeff0 = 2 * Math.cos(2 * Math.PI * k0 / samplesPerBit);
            
            let q1_0 = 0, q1_1 = 0, q1_2 = 0;
            let q0_0 = 0, q0_1 = 0, q0_2 = 0;

            for (let j = 0; j < samplesPerBit; j++) {
                const sample = signal[startSample + j];
                
                // 频率1检测
                q1_0 = coeff1 * q1_1 - q1_2 + sample;
                q1_2 = q1_1;
                q1_1 = q1_0;
                
                // 频率0检测
                q0_0 = coeff0 * q0_1 - q0_2 + sample;
                q0_2 = q0_1;
                q0_1 = q0_0;
            }

            // 计算能量
            energy1 = q1_1 * q1_1 + q1_2 * q1_2 - coeff1 * q1_1 * q1_2;
            energy0 = q0_1 * q0_1 + q0_2 * q0_2 - coeff0 * q0_1 * q0_2;
            
            bits.push(energy1 > energy0 ? 1 : 0);
        }

        return bits;
    }

    // 相干解调（需要知道载波相位）
    coherentDemodulate(signal: Float32Array): number[] {
        const samplesPerBit = Math.floor(this.sampleRate * this.bitDuration);
        const numBits = Math.floor(signal.length / samplesPerBit);
        const bits: number[] = [];

        for (let i = 0; i < numBits; i++) {
            const startSample = i * samplesPerBit;
            let correlation1 = 0;
            let correlation0 = 0;

            for (let j = 0; j < samplesPerBit; j++) {
                const t = (startSample + j) / this.sampleRate;
                const sample = signal[startSample + j];
                
                correlation1 += sample * Math.sin(2 * Math.PI * this.frequency1 * t);
                correlation0 += sample * Math.sin(2 * Math.PI * this.frequency0 * t);
            }

            bits.push(correlation1 > correlation0 ? 1 : 0);
        }

        return bits;
    }

    // 自动频率控制
    autoFrequencyControl(signal: Float32Array, searchRange: number = 100): void {
        const samplesPerBit = Math.floor(this.sampleRate * this.bitDuration);
        let bestFreq1 = this.frequency1;
        let bestFreq0 = this.frequency0;
        let maxCorrelation1 = 0;
        let maxCorrelation0 = 0;

        // 搜索最佳频率1
        for (let freq = this.frequency1 - searchRange; freq <= this.frequency1 + searchRange; freq += 10) {
            let correlation = 0;
            for (let j = 0; j < Math.min(samplesPerBit * 10, signal.length); j++) {
                const t = j / this.sampleRate;
                correlation += signal[j] * Math.sin(2 * Math.PI * freq * t);
            }
            if (Math.abs(correlation) > maxCorrelation1) {
                maxCorrelation1 = Math.abs(correlation);
                bestFreq1 = freq;
            }
        }

        // 搜索最佳频率0
        for (let freq = this.frequency0 - searchRange; freq <= this.frequency0 + searchRange; freq += 10) {
            let correlation = 0;
            for (let j = 0; j < Math.min(samplesPerBit * 10, signal.length); j++) {
                const t = j / this.sampleRate;
                correlation += signal[j] * Math.sin(2 * Math.PI * freq * t);
            }
            if (Math.abs(correlation) > maxCorrelation0) {
                maxCorrelation0 = Math.abs(correlation);
                bestFreq0 = freq;
            }
        }

        this.frequency1 = bestFreq1;
        this.frequency0 = bestFreq0;
        console.log(`AFC adjusted: f1=${bestFreq1}Hz, f0=${bestFreq0}Hz`);
    }
}

// 贝尔202调制解调器标准
const bell202Modem = new FSKModem(1200, 2200, 44100, 0.008333, 1.0);

// 使用示例
const testData = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1];
const fskSignal = bell202Modem.modulate(testData);
const fskDemodulated = bell202Modem.demodulate(fskSignal);

console.log(`FSK Modulation Test:`);
console.log(`Input:  ${testData.join('')}`);
console.log(`Output: ${fskDemodulated.join('')}`);