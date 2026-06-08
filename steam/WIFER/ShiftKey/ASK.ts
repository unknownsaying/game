// ask_modem.ts
class ASKModem {
    private carrierFrequency: number; // 载波频率 (Hz)
    private sampleRate: number;       // 采样率 (Hz)
    private amplitude1: number;       // 比特1的幅度
    private amplitude0: number;       // 比特0的幅度
    private bitDuration: number;      // 比特持续时间 (秒)

    constructor(
        carrierFreq: number = 1000,
        sampleRate: number = 44100,
        amp1: number = 1.0,
        amp0: number = 0.3,
        bitDuration: number = 0.01
    ) {
        this.carrierFrequency = carrierFreq;
        this.sampleRate = sampleRate;
        this.amplitude1 = amp1;
        this.amplitude0 = amp0;
        this.bitDuration = bitDuration;
    }

    // 调制：数字比特流 -> 模拟信号
    modulate(bits: number[]): Float32Array {
        const samplesPerBit = Math.floor(this.sampleRate * this.bitDuration);
        const totalSamples = bits.length * samplesPerBit;
        const signal = new Float32Array(totalSamples);

        for (let i = 0; i < bits.length; i++) {
            const amplitude = bits[i] === 1 ? this.amplitude1 : this.amplitude0;
            const startSample = i * samplesPerBit;
            
            for (let j = 0; j < samplesPerBit; j++) {
                const t = (startSample + j) / this.sampleRate;
                signal[startSample + j] = amplitude * 
                    Math.sin(2 * Math.PI * this.carrierFrequency * t);
            }
        }
        
        return signal;
    }

    // 解调：模拟信号 -> 数字比特流
    demodulate(signal: Float32Array, threshold?: number): number[] {
        if (!threshold) {
            threshold = (this.amplitude1 + this.amplitude0) / 2;
        }

        const samplesPerBit = Math.floor(this.sampleRate * this.bitDuration);
        const numBits = Math.floor(signal.length / samplesPerBit);
        const bits: number[] = [];

        for (let i = 0; i < numBits; i++) {
            const startSample = i * samplesPerBit;
            let envelope = 0;

            // 包络检波
            for (let j = 0; j < samplesPerBit; j++) {
                envelope += Math.abs(signal[startSample + j]);
            }
            envelope /= samplesPerBit;

            // 归一化包络
            envelope = envelope * 2; // 补偿半波整流
            
            bits.push(envelope > threshold ? 1 : 0);
        }

        return bits;
    }

    // 生成同步前导码
    generatePreamble(): number[] {
        return [1, 0, 1, 0, 1, 0, 1, 0]; // 交替比特用于同步
    }

    // 计算误码率
    calculateBER(originalBits: number[], receivedBits: number[]): number {
        let errors = 0;
        const length = Math.min(originalBits.length, receivedBits.length);
        
        for (let i = 0; i < length; i++) {
            if (originalBits[i] !== receivedBits[i]) {
                errors++;
            }
        }
        
        return errors / length;
    }
}

// 使用示例
const askModem = new ASKModem(2000, 44100, 1.0, 0.2, 0.005);

// 调制
const testBits = [1, 0, 1, 1, 0, 0, 1, 0];
const modulatedSignal = askModem.modulate(testBits);
console.log(`Modulated signal length: ${modulatedSignal.length} samples`);

// 添加噪声模拟
const noisySignal = new Float32Array(modulatedSignal.length);
const noiseLevel = 0.1;
for (let i = 0; i < modulatedSignal.length; i++) {
    noisySignal[i] = modulatedSignal[i] + (Math.random() - 0.5) * noiseLevel;
}

// 解调
const demodulatedBits = askModem.demodulate(noisySignal);
console.log(`Original bits: ${testBits.join('')}`);
console.log(`Demodulated bits: ${demodulatedBits.join('')}`);
console.log(`BER: ${askModem.calculateBER(testBits, demodulatedBits)}`);