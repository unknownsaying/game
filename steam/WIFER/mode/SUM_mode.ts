import { ASKModem } from './ASK_modem';
import { FSKModem } from './FSK_modem';
import { PSKModem } from './PSK_modem';

class RouterBaseband {
  private modem: ASKModem | FSKModem | PSKModem;

  constructor(mode: string) {
    switch (mode) {
      case 'ASK': this.modem = new ASKModem(2000, 44100, 1, 0.2, 0.01); break;
      case 'FSK': this.modem = new FSKModem(1200, 2200, 44100, 0.01); break;
      default:    this.modem = new PSKModem(1800, 44100, 0.01, 1, 'QPSK');
    }
  }

  transmit(bits: number[]): Float32Array {
    return this.modem.modulate(bits);
  }

  receive(samples: Float32Array): number[] {
    return this.modem.demodulate(samples);
  }
}