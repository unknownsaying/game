using System;

namespace WirelessCommunication
{

    //Provides methods for computing the Shannon–Hartley channel capacity.
    //C = B * log2(1 + S/N)

    public static class ShannonCapacity
    {
    
        // Calculates the channel capacity in bits per second (bps) given the bandwidth
        //and the signal-to-noise ratio expressed as a linear power ratio (SNR = S/N).
    
        //<param name="bandwidthHz">Bandwidth in Hertz (must be > 0).</param>
        //<param name="snrLinear">Linear SNR (must be >= 0). 0 means no signal, capacity = 0.</param>
        //<returns>Capacity in bps.</returns>
        //<exception cref="ArgumentOutOfRangeException">Thrown if bandwidth <= 0 or snrLinear < 0.</exception>
        public static double CapacityFromLinear(double bandwidthHz, double snrLinear)
        {
            if (bandwidthHz <= 0)
                throw new ArgumentOutOfRangeException(nameof(bandwidthHz), "Bandwidth must be greater than 0 Hz.");
            if (snrLinear < 0)
                throw new ArgumentOutOfRangeException(nameof(snrLinear), "Linear SNR cannot be negative.");

            if (snrLinear == 0.0)
                return 0.0; // log2(1+0)=0

            // C = B * log2(1 + S/N)
            return bandwidthHz * Math.Log2(1.0 + snrLinear);
        }

    
        //Calculates the channel capacity using SNR expressed in decibels (dB).
    
        //<param name="bandwidthHz">Bandwidth in Hertz (must be > 0).</param>
        //<param name="snrDb">SNR in dB. Typical values range from -∞ to +∞.</param>
        //<returns>Capacity in bps.</returns>
        //<exception cref="ArgumentOutOfRangeException">Thrown if bandwidth <= 0.</exception>
        public static double CapacityFromDecibel(double bandwidthHz, double snrDb)
        {
            if (bandwidthHz <= 0)
                throw new ArgumentOutOfRangeException(nameof(bandwidthHz), "Bandwidth must be greater than 0 Hz.");

            // Convert dB to linear: SNR_linear = 10^(dB/10)
            double snrLinear = Math.Pow(10.0, snrDb / 10.0);
            return CapacityFromLinear(bandwidthHz, snrLinear);
        }

    
        //Converts a linear SNR value to decibels (dB).
    
        public static double LinearToDb(double snrLinear)
        {
            if (snrLinear <= 0)
                throw new ArgumentOutOfRangeException(nameof(snrLinear), "Linear SNR must be > 0 to convert to dB.");
            return 10.0 * Math.Log10(snrLinear);
        }

    
        //Converts a decibel SNR value to a linear ratio.
    
        public static double DbToLinear(double snrDb) => Math.Pow(10.0, snrDb / 10.0);

    
        //Returns the minimum SNR (linear) required to achieve a given capacity.
        //Rearranged from Shannon: S/N = 2^(C/B) - 1
    
        public static double RequiredLinearSnr(double capacityBps, double bandwidthHz)
        {
            if (bandwidthHz <= 0)
                throw new ArgumentOutOfRangeException(nameof(bandwidthHz), "Bandwidth must be > 0.");
            if (capacityBps < 0)
                throw new ArgumentOutOfRangeException(nameof(capacityBps), "Capacity cannot be negative.");
            return Math.Pow(2.0, capacityBps / bandwidthHz) - 1.0;
        }
    }


    //Extension methods for computing Shannon capacity directly on numeric types.

    public static class ShannonExtensions
    {
        //<returns>Capacity in bps for a given bandwidth and linear SNR.</returns>
        public static double ShannonCapacity(this double bandwidthHz, double snrLinear)
            => ShannonCapacity.CapacityFromLinear(bandwidthHz, snrLinear);

    
        //Computes capacity using bandwidth (Hz) and SNR in dB.
    
        public static double ShannonCapacityDb(this double bandwidthHz, double snrDb)
            => ShannonCapacity.CapacityFromDecibel(bandwidthHz, snrDb);
    }


    //MIMO capacity approximation: for N_t transmit and N_r receive antennas,
    //the capacity multiplies the SISO Shannon capacity by min(N_t, N_r) under
    //ideal uncorrelated channels.
    //More precise water‑filling formulas exist but are not shown here.

    public static class MimoCapacity
    {
    
        //Approximate MIMO channel capacity (spatial multiplexing bound).
    
        //<param name="bandwidthHz">Bandwidth in Hz.</param>
        //<param name="snrLinear">Linear SNR per receiver antenna.</param>
        //<param name="numTransmitAntennas">Number of transmit antennas (Nt).</param>
        //<param name="numReceiveAntennas">Number of receive antennas (Nr).</param>
        //<returns>Capacity in bps.</returns>
        public static double CapacityApproximation(double bandwidthHz, double snrLinear,
                                                   int numTransmitAntennas, int numReceiveAntennas)
        {
            int minStreams = Math.Min(numTransmitAntennas, numReceiveAntennas);
            if (minStreams <= 0)
                throw new ArgumentException("Number of antennas must be positive.");

            double sisocapacity = ShannonCapacity.CapacityFromLinear(bandwidthHz, snrLinear);
            return sisocapacity * minStreams;
        }
    }

    // ==========================
    // Self‑contained usage example
    // ==========================
    public static class Program
    {
        public static void Main()
        {
            // Example 1: WiFi 20 MHz channel, SNR = 25 dB
            double bw = 20e6; // 20 MHz
            double snrDb = 25;
            double capacity = ShannonCapacity.CapacityFromDecibel(bw, snrDb);
            Console.WriteLine($"WiFi 20 MHz, SNR {snrDb} dB => {capacity / 1e6:F2} Mbps");

            // Example 2: Linear SNR
            double snrLinear = 100; // 20 dB
            capacity = ShannonCapacity.CapacityFromLinear(bw, snrLinear);
            Console.WriteLine($"Linear SNR {snrLinear} => {capacity / 1e6:F2} Mbps");

            // Example 3: Using extension method
            capacity = bw.ShannonCapacityDb(snrDb);
            Console.WriteLine($"Extension method => {capacity / 1e6:F2} Mbps");

            // Example 4: MIMO 2x2
            double mimoCap = MimoCapacity.CapacityApproximation(bw, snrLinear, 2, 2);
            Console.WriteLine($"2x2 MIMO approx => {mimoCap / 1e6:F2} Mbps");

            // Example 5: Required SNR to achieve 100 Mbps with 20 MHz
            double requiredSnr = ShannonCapacity.RequiredLinearSnr(100e6, bw);
            Console.WriteLine($"Required linear SNR for 100 Mbps: {requiredSnr:F2} " +
                              $"(~{ShannonCapacity.LinearToDb(requiredSnr):F1} dB)");
        }
    }
}