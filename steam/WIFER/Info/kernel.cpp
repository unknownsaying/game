// mimo_ofdm_kernel.cpp
// A self-contained MIMO-OFDM baseband processing library (kernel-friendly)
#include <cmath>
#include <array>
#include <vector>
#include <complex>
#include <iostream>
#include <algorithm>

using Complex = std::complex<double>;
constexpr double PI = 3.1415926;

// ----------------------------------------------------------------------
// 1. Fast Fourier Transform (in‑place, radix‑2, decimation‑in‑time)
//    Works on std::vector<Complex> or raw pointers.
// ----------------------------------------------------------------------
namespace FFT {
    // Bit‑reverse an array of length N (N must be a power of 2).
    template <size_t N>
    void bitReverse(Complex* data) {
        constexpr size_t bits = static_cast<size_t>(std::log2(N));
        for (size_t i = 0; i < N; ++i) {
            size_t rev = 0;
            for (size_t j = 0; j < bits; ++j) {
                if (i & (1u << j))
                    rev |= (1u << (bits - 1 - j));
            }
            if (i < rev)
                std::swap(data[i], data[rev]);
        }
    }

    // Forward FFT: X[k] = sum_n x[n] * exp(-j*2*pi*k*n/N)
    template <size_t N>
    void fft(Complex* data) {
        bitReverse<N>(data);
        for (size_t size = 2; size <= N; size <<= 1) {
            double angle = -2.0 * PI / size;
            Complex wlen(std::cos(angle), std::sin(angle));
            for (size_t i = 0; i < N; i += size) {
                Complex w(1.0, 0.0);
                for (size_t j = 0; j < size / 2; ++j) {
                    Complex even = data[i + j];
                    Complex odd  = data[i + j + size / 2] * w;
                    data[i + j]               = even + odd;
                    data[i + j + size / 2]    = even - odd;
                    w *= wlen;
                }
            }
        }
    }

    // Inverse FFT: x[n] = (1/N) * sum_k X[k] * exp(+j*2*pi*k*n/N)
    template <size_t N>
    void ifft(Complex* data) {
        // Conjugate input, run FFT, conjugate output, scale by 1/N
        for (size_t i = 0; i < N; ++i) data[i] = std::conj(data[i]);
        fft<N>(data);
        for (size_t i = 0; i < N; ++i) data[i] = std::conj(data[i]) / static_cast<double>(N);
    }
}

// ----------------------------------------------------------------------
// 2. OFDM modulator / demodulator (fixed size, N = 64 subcarriers,
//    cyclic prefix length = 16 – typical 802.11a/g/n)
// ----------------------------------------------------------------------
template <size_t N = 64, size_t CP = 16>
class OFDMModem {
public:
    static constexpr size_t NUM_DATA_CARRIERS = 52; // 802.11a-style
    static constexpr size_t SYMBOL_SAMPLES = N + CP;

    // Modulate: place 52 complex symbols on subcarriers [-26:-1, 1:26], IFFT, add CP
    void modulate(const std::array<Complex, NUM_DATA_CARRIERS>& symbols,
                  std::array<Complex, SYMBOL_SAMPLES>& out) {
        std::array<Complex, N> freqDom{};
        const size_t half = N / 2;
        for (size_t i = 0; i < NUM_DATA_CARRIERS; ++i) {
            size_t idx = (i < half) ? i + 1 : i + 2; // skip DC at N/2
            if (idx < N) freqDom[idx] = symbols[i];
        }

        // IFFT
        FFT::ifft<N>(freqDom.data());

        // Add cyclic prefix
        for (size_t i = 0; i < CP; ++i)
            out[i] = freqDom[N - CP + i];
        for (size_t i = 0; i < N; ++i)
            out[CP + i] = freqDom[i];
    }

    // Demodulate: remove CP, FFT, extract data subcarriers
    void demodulate(const std::array<Complex, SYMBOL_SAMPLES>& in,
                    std::array<Complex, NUM_DATA_CARRIERS>& symbols) {
        std::array<Complex, N> timeDom;
        for (size_t i = 0; i < N; ++i)
            timeDom[i] = in[CP + i]; // discard cyclic prefix

        FFT::fft<N>(timeDom.data());

        const size_t half = N / 2;
        for (size_t i = 0; i < NUM_DATA_CARRIERS; ++i) {
            size_t idx = (i < half) ? i + 1 : i + 2;
            if (idx < N)
                symbols[i] = timeDom[idx];
            else
                symbols[i] = Complex(0,0);
        }
    }
};

// ----------------------------------------------------------------------
// 3. MIMO detector (2×2, linear detectors)
// ----------------------------------------------------------------------
struct MIMOChannel {
    std::array<std::array<Complex, 2>, 2> H; // H[nr][nt]
};

// Zero‑Forcing detection: s_hat = inv(H) * y
std::array<Complex, 2> zeroForcing(const MIMOChannel& ch,
                                   const std::array<Complex, 2>& y) {
    const auto& H = ch.H;
    Complex a = H[0][0], b = H[0][1];
    Complex c = H[1][0], d = H[1][1];
    Complex det = a * d - b * c;

    // inv(H) = 1/det * [[d, -b], [-c, a]]
    Complex inv00 = d / det, inv01 = -b / det;
    Complex inv10 = -c / det, inv11 = a / det;

    std::array<Complex, 2> s;
    s[0] = inv00 * y[0] + inv01 * y[1];
    s[1] = inv10 * y[0] + inv11 * y[1];
    return s;
}

// MMSE detection: s_hat = inv(H^H H + sigma^2 I) H^H y
// sigma2 = noise power (assuming equal per antenna, same modulation)
std::array<Complex, 2> MMSE(const MIMOChannel& ch,
                            const std::array<Complex, 2>& y,
                            double noisePower) {
    const auto& H = ch.H;
    Complex h00 = H[0][0], h01 = H[0][1];
    Complex h10 = H[1][0], h11 = H[1][1];

    Complex h00c = std::conj(h00), h10c = std::conj(h10);
    Complex h01c = std::conj(h01), h11c = std::conj(h11);

    // G = H^H H + sigma^2 I
    Complex g00 = h00c * h00 + h10c * h10 + noisePower;
    Complex g01 = h00c * h01 + h10c * h11;
    Complex g10 = std::conj(g01); // g01c
    Complex g11 = h01c * h01 + h11c * h11 + noisePower;

    Complex det = g00 * g11 - g01 * g10;
    Complex invG00 = g11 / det, invG01 = -g01 / det;
    Complex invG10 = -g10 / det, invG11 = g00 / det;

    // y_filt = H^H y
    Complex y0_filt = h00c * y[0] + h10c * y[1];
    Complex y1_filt = h01c * y[0] + h11c * y[1];

    std::array<Complex, 2> s;
    s[0] = invG00 * y0_filt + invG01 * y1_filt;
    s[1] = invG10 * y0_filt + invG11 * y1_filt;
    return s;
}

// ----------------------------------------------------------------------
// 4. Kernel‑driver‑style wrapper: one OFDM symbol per MIMO stream
//    Combine OFDM + MIMO for a 2×2 spatial multiplexing system.
// ----------------------------------------------------------------------
template <size_t N = 64, size_t CP = 16>
class WiFiBaseband {
public:
    using OFDM = OFDMModem<N, CP>;
    using SymbolArray = std::array<Complex, OFDM::NUM_DATA_CARRIERS>;

    // Transmit one MIMO‑OFDM symbol:
    // Input: 2 streams, each with 52 QAM symbols
    // Output: 2 time‑domain signals (one per TX antenna), each N+CP samples
    void transmit(const std::array<SymbolArray, 2>& txSymbols,
                  std::array<std::array<Complex, N+CP>, 2>& txSignals) {
        OFDM ofdm;
        for (size_t ant = 0; ant < 2; ++ant) {
            ofdm.modulate(txSymbols[ant], txSignals[ant]);
        }
        // In a real radio, txSignals would be sent to DAC.
        // Here we just pass them through the channel for the demo.
    }

    // Receive one MIMO‑OFDM symbol:
    // Input: 2 time‑domain receive signals (after channel propagation)
    // Channel: known H matrix (per subcarrier in practice)
    // NoisePower: per‑receive‑antenna noise variance
    // Output: detected transmitted symbols (2 streams of 52 symbols)
    void receive(const std::array<std::array<Complex, N+CP>, 2>& rxSignals,
                 const MIMOChannel& ch, double noisePower,
                 std::array<SymbolArray, 2>& rxSymbols) {
        OFDM ofdm;
        // Step 1: OFDM demodulate each antenna
        std::array<SymbolArray, 2> freqSignals; // freqSignals[ant][subcarrier]
        for (size_t ant = 0; ant < 2; ++ant) {
            ofdm.demodulate(rxSignals[ant], freqSignals[ant]);
        }

        // Step 2: MIMO detection per subcarrier
        // (In Wi‑Fi the channel matrix varies per subcarrier;
        //  here we use the same H for all for simplicity.)
        for (size_t sc = 0; sc < OFDM::NUM_DATA_CARRIERS; ++sc) {
            std::array<Complex, 2> y;
            y[0] = freqSignals[0][sc];
            y[1] = freqSignals[1][sc];
            std::array<Complex, 2> s_hat;
            // Choose detector:
            s_hat = MMSE(ch, y, noisePower);   // or zeroForcing(ch, y)
            rxSymbols[0][sc] = s_hat[0];
            rxSymbols[1][sc] = s_hat[1];
        }
    }
};

// ----------------------------------------------------------------------
// 5. Demonstration
// ----------------------------------------------------------------------
int main() {
    using Baseband = WiFiBaseband<64, 16>;
    using SymbolArray = Baseband::SymbolArray;

    // Prepare transmitted symbols (BPSK: +1/-1 on each stream, first few carriers)
    SymbolArray txStream0{}, txStream1{};
    for (size_t i = 0; i < 52; ++i) {
        txStream0[i] = Complex((i % 2 == 0) ? 1.0 : -1.0, 0);
        txStream1[i] = Complex((i % 3 == 0) ? 1.0 : -1.0, 0);
    }

    // MIMO channel matrix (example, static for all subcarriers)
    MIMOChannel ch;
    ch.H[0][0] = Complex(1.2, -0.5); ch.H[0][1] = Complex(0.3, 0.1);
    ch.H[1][0] = Complex(0.2, 0.4);  ch.H[1][1] = Complex(0.9, -0.2);

    Baseband baseband;
    std::array<std::array<Complex, 64+16>, 2> txSignals;
    baseband.transmit({txStream0, txStream1}, txSignals);

    // Simulate channel propagation (no noise for simplicity)
    std::array<std::array<Complex, 64+16>, 2> rxSignals;
    for (size_t ant = 0; ant < 2; ++ant) {
        for (size_t i = 0; i < 64+16; ++i) {
            rxSignals[ant][i] = ch.H[ant][0] * txSignals[0][i] +
                                ch.H[ant][1] * txSignals[1][i];
        }
    }

    // Receiver side
    SymbolArray rxStream0{}, rxStream1{};
    baseband.receive(rxSignals, ch, 0.0 /* noisePower */, {rxStream0, rxStream1});

    // Print a few recovered symbols
    std::cout << "Recovered stream 0 (first 4 subcarriers):\n";
    for (size_t i = 0; i < 4; ++i)
        std::cout << rxStream0[i].real() << " + j" << rxStream0[i].imag() << "\n";
    std::cout << "Recovered stream 1 (first 4 subcarriers):\n";
    for (size_t i = 0; i < 4; ++i)
        std::cout << rxStream1[i].real() << " + j" << rxStream1[i].imag() << "\n";

    // For a perfect channel and detector, the recovered should be very close to original.
    return 0;
}
