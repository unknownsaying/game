// mimo.ts
/**
 * MIMO (Multiple Input Multiple Output) – 2×2 spatial multiplexing with Zero‑Forcing detection.
 * Models a narrowband MIMO channel matrix H (N_rx × N_tx) and stream demultiplexing.
 */

// Minimal complex number class (duplicated for independence)
class ComplexM {
  constructor(public re: number = 0, public im: number = 0) {}

  add(c: ComplexM): ComplexM {
    return new ComplexM(this.re + c.re, this.im + c.im);
  }

  sub(c: ComplexM): ComplexM {
    return new ComplexM(this.re - c.re, this.im - c.im);
  }

  mul(c: ComplexM): ComplexM {
    return new ComplexM(
      this.re * c.re - this.im * c.im,
      this.re * c.im + this.im * c.re
    );
  }

  div(c: ComplexM): ComplexM {
    const den = c.re * c.re + c.im * c.im;
    return new ComplexM(
      (this.re * c.re + this.im * c.im) / den,
      (this.im * c.re - this.re * c.im) / den
    );
  }

  scale(s: number): ComplexM {
    return new ComplexM(this.re * s, this.im * s);
  }

  conj(): ComplexM {
    return new ComplexM(this.re, -this.im);
  }
}

// Simple 2×2 matrix operations
type Matrix2x2 = [[ComplexM, ComplexM], [ComplexM, ComplexM]];

function matMul(A: Matrix2x2, B: Matrix2x2): Matrix2x2 {
  return [
    [
      A[0][0].mul(B[0][0]).add(A[0][1].mul(B[1][0])),
      A[0][0].mul(B[0][1]).add(A[0][1].mul(B[1][1]))
    ],
    [
      A[1][0].mul(B[0][0]).add(A[1][1].mul(B[1][0])),
      A[1][0].mul(B[0][1]).add(A[1][1].mul(B[1][1]))
    ]
  ];
}

function matVecMul(A: Matrix2x2, v: [ComplexM, ComplexM]): [ComplexM, ComplexM] {
  return [
    A[0][0].mul(v[0]).add(A[0][1].mul(v[1])),
    A[1][0].mul(v[0]).add(A[1][1].mul(v[1]))
  ];
}

function inverse2x2(H: Matrix2x2): Matrix2x2 {
  const a = H[0][0], b = H[0][1], c = H[1][0], d = H[1][1];
  const det = a.mul(d).sub(b.mul(c));
  // inverse = 1/det * [[d, -b], [-c, a]]
  return [
    [d.div(det), b.mul(new ComplexM(-1, 0)).div(det)],
    [c.mul(new ComplexM(-1, 0)).div(det), a.div(det)]
  ];
}

class MIMOSystem {
  private Nt: number; // number of transmit antennas
  private Nr: number; // number of receive antennas

  constructor(Nt: number = 2, Nr: number = 2) {
    this.Nt = Nt;
    this.Nr = Nr;
  }

  /**
   * Simulate MIMO transmission over a given channel matrix H.
   * @param symbols array of Nt complex symbols to transmit
   * @param H channel matrix (Nr x Nt) as 2D array of ComplexM
   * @returns received vector (Nr elements)
   */
  transmit(symbols: ComplexM[], H: ComplexM[][]): ComplexM[] {
    if (symbols.length !== this.Nt || H.length !== this.Nr || H[0].length !== this.Nt) {
      throw new Error('Dimension mismatch');
    }
    const rx: ComplexM[] = new Array(this.Nr).fill(new ComplexM(0, 0));
    for (let i = 0; i < this.Nr; i++) {
      let sum = new ComplexM(0, 0);
      for (let j = 0; j < this.Nt; j++) {
        sum = sum.add(H[i][j].mul(symbols[j]));
      }
      rx[i] = sum;
    }
    return rx;
  }

  /**
   * Zero‑Forcing (ZF) detection.
   * Computes estimated transmitted symbols: ŝ = pinv(H) * y
   */
  zeroForcingDetect(received: ComplexM[], H: ComplexM[][]): ComplexM[] {
    if (this.Nt !== 2 || this.Nr !== 2) {
      throw new Error('ZF demo only implemented for 2×2');
    }
    const H2: Matrix2x2 = [[H[0][0], H[0][1]], [H[1][0], H[1][1]]];
    const invH = inverse2x2(H2);
    const estimated = matVecMul(invH, [received[0], received[1]]);
    return [estimated[0], estimated[1]];
  }

  /**
   * Minimal Mean Square Error (MMSE) detection (2×2 only)
   * ŝ = inv(H^H H + SNR^{-1} I) H^H y
   */
  MMSE(received: ComplexM[], H: ComplexM[][], snrLinear: number): ComplexM[] {
    if (this.Nt !== 2 || this.Nr !== 2) {
      throw new Error('MMSE demo only implemented for 2×2');
    }
    // H^H * H + (1/snr)*I
    const h00 = H[0][0], h01 = H[0][1], h10 = H[1][0], h11 = H[1][1];
    const h00c = h00.conj(), h10c = h10.conj(), h01c = h01.conj(), h11c = h11.conj();
    const a = h00c.mul(h00).add(h10c.mul(h10)).add(new ComplexM(1/snrLinear, 0));
    const b = h00c.mul(h01).add(h10c.mul(h11));
    const c = h01c.mul(h00).add(h11c.mul(h10));
    const d = h01c.mul(h01).add(h11c.mul(h11)).add(new ComplexM(1/snrLinear, 0));
    const G: Matrix2x2 = [[a, b], [c, d]];
    const invG = inverse2x2(G);

    // H^H y
    const y = received;
    const Hh_y = [
      h00c.mul(y[0]).add(h10c.mul(y[1])),
      h01c.mul(y[0]).add(h11c.mul(y[1]))
    ];
    const estimated = matVecMul(invG, Hh_y);
    return [estimated[0], estimated[1]];
  }
}

// ---------- demonstration ----------
function demoMIMO() {
  const mimo = new MIMOSystem(2, 2);

  // Channel matrix H (Rayleigh-like, but static for demo)
  const H: ComplexM[][] = [
    [new ComplexM(1.2, -0.5), new ComplexM(0.3, 0.1)],
    [new ComplexM(0.2, 0.4), new ComplexM(0.9, -0.2)]
  ];

  // Transmitted symbols (e.g., QPSK)
  const txSymbols = [
    new ComplexM(1, 0),   // bit pair 00
    new ComplexM(0, 1)    // bit pair 01
  ];

  console.log('MIMO 2×2 Demo');
  console.log('Transmitted symbols:');
  txSymbols.forEach((s, i) => console.log(`  s${i}: ${s.re.toFixed(2)} + j${s.im.toFixed(2)}`));

  const rx = mimo.transmit(txSymbols, H);
  console.log('Received vector (without noise):');
  rx.forEach((r, i) => console.log(`  y${i}: ${r.re.toFixed(2)} + j${r.im.toFixed(2)}`));

  // ZF detection
  const recoveredZF = mimo.zeroForcingDetect(rx, H);
  console.log('Zero‑Forcing recovered symbols:');
  recoveredZF.forEach((s, i) => console.log(`  ŝ${i}: ${s.re.toFixed(4)} + j${s.im.toFixed(4)}`));

  // MMSE with high SNR
  const recoveredMMSE = mimo.MMSE(rx, H, 100); // SNR = 20 dB
  console.log('MMSE recovered symbols (SNR 20 dB):');
  recoveredMMSE.forEach((s, i) => console.log(`  ŝ${i}: ${s.re.toFixed(4)} + j${s.im.toFixed(4)}`));
}

demoMIMO();

export { MIMOSystem, ComplexM };