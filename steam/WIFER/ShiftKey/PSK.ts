// psk_modem.ts
enum PSKType {
    BPSK = 'BPSK',  // 2-PSK
    QPSK = 'QPSK',  // 4-PSK
    PSK8 = '8PSK'   // 8-PSK
}

class PSKModem {
    private carrierFrequency: number;
    private sampleRate: number;
    private symbolDuration: number;
    private amplitude: number;
    private pskType: PSKType;
    private bitsPerSymbol: number;

    constructor(
        carrierFreq: number = 1800,
        sampleRate: number = 44100,
        symbolDuration: number = 0.01,
        amplitude: number = 1.0,
        pskType: PSKType = PSKType.BPSK
    ) {
        this.carrierFrequency = carrierFreq;
        this.sampleRate = sampleRate;
        this.symbolDuration = symbolDuration;
        this.amplitude = amplitude;
        this.pskType = pskType;
        this.bitsPerSymbol = this.getBitsPerSymbol();
    }

    private getBitsPerSymbol(): number {
        switch (this.pskType) {
            case PSKType.BPSK: return 1;
            case PSKType.QPSK: return 2;
            case PSKType.PSK8: return 3;
            default: return 1;
        }
    }

    // 将比特转换为符号
    private bitsToSymbols(bits: number[]): number[] {
        const symbols: number[] = [];
        
        for (let i = 0; i < bits.length; i += this.bitsPerSymbol) {
            let symbolValue = 0;
            for (let j = 0; j < this.bitsPerSymbol; j++) {
                if (i + j < bits.length) {
                    symbolValue = (symbolValue << 1) | bits[i + j];
                }
            }
            symbols.push(symbolValue);
        }
        
        return symbols;
    }

    // 获取符号对应的相位偏移
    private getPhaseShift(symbol: number): number {
        switch (this.pskType) {
            case PSKType.BPSK:
                return symbol === 0 ? 0 : Math.PI;
            case PSKType.QPSK:
                return (Math.PI / 4) + (symbol * Math.PI / 2);
            case PSKType.PSK8:
                return symbol * Math.PI / 4;
            default:
                return 0;
        }
    }

    // 调制
    modulate(bits: number[]): Float32Array {
        const symbols = this.bitsToSymbols(bits);
        const samplesPerSymbol = Math.floor(this.sampleRate * this.symbolDuration);
        const totalSamples = symbols.length * samplesPerSymbol;
        const signal = new Float32Array(totalSamples);

        for (let i = 0; i < symbols.length; i++) {
            const phaseShift = this.getPhaseShift(symbols[i]);
            const startSample = i * samplesPerSymbol;
            
            for (let j = 0; j < samplesPerSymbol; j++) {
                const t = (startSample + j) / this.sampleRate;
                signal[startSample + j] = this.amplitude * 
                    Math.sin(2 * Math.PI * this.carrierFrequency * t + phaseShift);
            }
        }
        
        return signal;
    }

    // BPSK解调
    private bpskDemodulate(signal: Float32Array, samplesPerSymbol: number): number[] {
        const numSymbols = Math.floor(signal.length / samplesPerSymbol);
        const bits: number[] = [];

        for (let i = 0; i < numSymbols; i++) {
            const startSample = i * samplesPerSymbol;
            let inPhase = 0;

            for (let j = 0; j < samplesPerSymbol; j++) {
                const t = (startSample + j) / this.sampleRate;
                const sample = signal[startSample + j];
                inPhase += sample * Math.sin(2 * Math.PI * this.carrierFrequency * t);
            }

            bits.push(inPhase >= 0 ? 0 : 1);
        }

        return bits;
    }

    // QPSK解调
    private qpskDemodulate(signal: Float32Array, samplesPerSymbol: number): number[] {
        const numSymbols = Math.floor(signal.length / samplesPerSymbol);
        const bits: number[] = [];

        for (let i = 0; i < numSymbols; i++) {
            const startSample = i * samplesPerSymbol;
            let inPhase = 0;
            let quadrature = 0;

            for (let j = 0; j < samplesPerSymbol; j++) {
                const t = (startSample + j) / this.sampleRate;
                const sample = signal[startSample + j];
                
                inPhase += sample * Math.sin(2 * Math.PI * this.carrierFrequency * t);
                quadrature += sample * Math.cos(2 * Math.PI * this.carrierFrequency * t);
            }

            // 符号决策
            const bits2 = this.qpskDecision(inPhase, quadrature);
            bits.push(...bits2);
        }

        return bits;
    }

    private qpskDecision(i: number, q: number): number[] {
        if (i >= 0 && q >= 0) return [0, 0];
        if (i < 0 && q >= 0) return [0, 1];
        if (i >= 0 && q < 0) return [1, 0];
        return [1, 1];
    }

    // 8PSK解调
    private psk8Demodulate(signal: Float32Array, samplesPerSymbol: number): number[] {
        const numSymbols = Math.floor(signal.length / samplesPerSymbol);
        const bits: number[] = [];

        for (let i = 0; i < numSymbols; i++) {
            const startSample = i * samplesPerSymbol;
            let inPhase = 0;
            let quadrature = 0;

            for (let j = 0; j < samplesPerSymbol; j++) {
                const t = (startSample + j) / this.sampleRate;
                const sample = signal[startSample + j];
                
                inPhase += sample * Math.sin(2 * Math.PI * this.carrierFrequency * t);
                quadrature += sample * Math.cos(2 * Math.PI * this.carrierFrequency * t);
            }

            // 计算相位角
            const phase = Math.atan2(quadrature, inPhase);
            const normalizedPhase = phase < 0 ? phase + 2 * Math.PI : phase;
            
            // 找到最近的星座点
            const symbol = Math.round(normalizedPhase / (Math.PI / 4)) % 8;
            
            // 符号转二进制
            const bits3 = symbol.toString(2).padStart(3, '0').split('').map(Number);
            bits.push(...bits3);
        }

        return bits;
    }

    // 解调
    demodulate(signal: Float32Array): number[] {
        const samplesPerSymbol = Math.floor(this.sampleRate * this.symbolDuration);

        switch (this.pskType) {
            case PSKType.BPSK:
                return this.bpskDemodulate(signal, samplesPerSymbol);
            case PSKType.QPSK:
                return this.qpskDemodulate(signal, samplesPerSymbol);
            case PSKType.PSK8:
                return this.psk8Demodulate(signal, samplesPerSymbol);
            default:
                return [];
        }
    }

    // 载波恢复（Costas环）
    carrierRecovery(signal: Float32Array): number {
        let phase = 0;
        let frequency = this.carrierFrequency;
        const damping = 0.707;
        const loopBandwidth = 100;

        const samplesPerSymbol = Math.floor(this.sampleRate * this.symbolDuration);
        const numSymbols = Math.floor(signal.length / samplesPerSymbol);

        for (let i = 0; i < numSymbols; i++) {
            const startSample = i * samplesPerSymbol;
            let phaseError = 0;

            for (let j = 0; j < samplesPerSymbol; j++) {
                const t = (startSample + j) / this.sampleRate;
                const sample = signal[startSample + j];
                
                const iComponent = sample * Math.sin(2 * Math.PI * frequency * t + phase);
                const qComponent = sample * Math.cos(2 * Math.PI * frequency * t + phase);
                
                // Costas环相位误差检测
                phaseError += iComponent * qComponent;
            }

            // 更新相位和频率
            phase += 2 * Math.PI * frequency * this.symbolDuration;
            frequency += loopBandwidth * phaseError;
        }

        return frequency;
    }

    // 差分编码（用于DBPSK/DQPSK）
    differentialEncode(bits: number[]): number[] {
        const encoded: number[] = [];
        let previous = 0;

        for (const bit of bits) {
            previous = previous ^ bit;
            encoded.push(previous);
        }

        return encoded;
    }

    // 差分解码
    differentialDecode(bits: number[]): number[] {
        const decoded: number[] = [];
        let previous = 0;

        for (const bit of bits) {
            decoded.push(previous ^ bit);
            previous = bit;
        }

        return decoded;
    }
}

// 使用示例
console.log("=== BPSK Test ===");
const bpskModem = new PSKModem(2000, 44100, 0.01, 1.0, PSKType.BPSK);
const bpskBits = [0, 1, 0, 0, 1, 1, 0, 1];
const bpskSignal = bpskModem.modulate(bpskBits);
const bpskOutput = bpskModem.demodulate(bpskSignal);
console.log(`Input:  ${bpskBits.join('')}`);
console.log(`Output: ${bpskOutput.join('')}`);

console.log("\n=== QPSK Test ===");
const qpskModem = new PSKModem(2000, 44100, 0.01, 1.0, PSKType.QPSK);
const qpskBits = [0, 0, 0, 1, 1, 0, 1, 1];
const qpskSignal = qpskModem.modulate(qpskBits);
const qpskOutput = qpskModem.demodulate(qpskSignal);
console.log(`Input:  ${qpskBits.join('')}`);
console.log(`Output: ${qpskOutput.join('')}`);