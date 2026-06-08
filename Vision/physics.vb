'===============================================================
' PHYSICAL PRINCIPLES AND EQUATIONS
' Comprehensive VB.NET implementation of fundamental physics
' Each principle is encapsulated as a class with equations
'===============================================================

Imports System
Imports System.Collections.Generic
Imports System.Linq

' ═══════════════════════════════════════════════════════════════
' MODULE: Physics Engine
' ═══════════════════════════════════════════════════════════════
Module PhysicsEngine

    Sub Main()
        ' Instantiate and demonstrate physics principles
        Dim mechanics As New ClassicalMechanics()
        Dim thermo As New Thermodynamics()
        Dim em As New Electromagnetism()
        Dim waves As New WavePhenomena()
        Dim optics As New Optics()
        Dim relativity As New Relativity()
        Dim quantum As New QuantumMechanics()
        Dim fluids As New FluidDynamics()

        ' Place breakpoint here to inspect all objects
        Dim allPhysics As Object = {
            mechanics, thermo, em, waves, optics, relativity, quantum, fluids
        }
    End Sub

End Module

' ═══════════════════════════════════════════════════════════════
' 1. CLASSICAL MECHANICS
' ═══════════════════════════════════════════════════════════════
Public Class ClassicalMechanics
    ' -- Fundamental Constants --
    Public Const GRAVITY As Double = 9.80665       ' m/s² (standard gravity)
    Public Const G As Double = 6.6743E-11          ' m³/(kg·s²) gravitational constant

    ' -- Kinematics --
    ''' Displacement with constant acceleration: s = ut + ½at²
    Function DisplacementUT(u As Double, t As Double, a As Double)
        Return u * t + 0.5 * a * t * t
    End Function

    ''' Final velocity: v = u + at
    Function FinalVelocity(u As Double, a As Double, t As Double)
        Return u + a * t
    End Function

    ''' Velocity squared: v² = u² + 2as
    Function VelocitySquared(u As Double, a As Double, s As Double)
        Return Math.Sqrt(u * u + 2.0 * a * s)
    End Function

    ''' Average velocity: v_avg = (u + v) / 2
    Function AverageVelocity(u As Double, v As Double)
        Return (u + v) / 2.0
    End Function

    ' -- Newton's Laws --
    ''' Newton's Second Law: F = ma
    Function Force(mass As Double, acceleration As Double)
        Return mass * acceleration
    End Function

    ''' Acceleration from force: a = F/m
    Function Acceleration(force As Double, mass As Double)
        Return force / mass
    End Function

    ''' Newton's Third Law: F₁₂ = -F₂₁
    Function ReactionForce(actionForce As Double)
        Return -actionForce
    End Function

    ' -- Momentum --
    ''' Linear momentum: p = mv
    Function LinearMomentum(mass As Double, velocity As Double)
        Return mass * velocity
    End Function

    ''' Impulse: J = FΔt = Δp
    Function Impulse(force As Double, timeInterval As Double)
        Return force * timeInterval
    End Function

    ''' Conservation of momentum: m₁u₁ + m₂u₂ = m₁v₁ + m₂v₂
    Function ConservationOfMomentum(m1 As Double, u1 As Double, m2 As Double, u2 As Double,
                                           v1 As Double)
        ' Returns v2 given v1 after collision
        Return (m1 * u1 + m2 * u2 - m1 * v1) / m2
    End Function

    ' -- Work, Energy, Power --
    ''' Work done: W = F·d·cos(θ)
    Function WorkDone(force As Double, displacement As Double, angleRad As Double)
        Return force * displacement * Math.Cos(angleRad)
    End Function

    ''' Kinetic energy: KE = ½mv²
    Function KineticEnergy(mass As Double, velocity As Double)
        Return 0.5 * mass * velocity * velocity
    End Function

    ''' Gravitational potential energy: PE = mgh
    Function PotentialEnergy(mass As Double, height As Double)
        Return mass * GRAVITY * height
    End Function

    ''' Elastic potential energy: PE_spring = ½kx²
    Function SpringPotentialEnergy(k As Double, x As Double)
        Return 0.5 * k * x * x
    End Function

    ''' Power: P = W/t = F·v
    Function Power(work As Double, time As Double)
        Return work / time
    End Function

    ''' Power from force and velocity: P = F·v
    Function PowerFromForce(force As Double, velocity As Double)
        Return force * velocity
    End Function

    ' -- Rotational Motion --
    ''' Angular velocity: ω = Δθ/Δt
    Function AngularVelocity(angleChangeRad As Double, time As Double)
        Return angleChangeRad / time
    End Function

    ''' Angular acceleration: α = Δω/Δt
    Function AngularAcceleration(omegaChange As Double, time As Double)
        Return omegaChange / time
    End Function

    ''' Torque: τ = r × F = I·α
    Function Torque(momentOfInertia As Double, angularAccel As Double)
        Return momentOfInertia * angularAccel
    End Function

    ''' Moment of inertia (point mass): I = mr²
    Function MomentOfInertiaPoint(mass As Double, radius As Double)
        Return mass * radius * radius
    End Function

    ''' Moment of inertia (solid sphere): I = (2/5)mr²
    Function MomentOfInertiaSolidSphere(mass As Double, radius As Double)
        Return 0.4 * mass * radius * radius  ' 2/5 = 0.4
    End Function

    ''' Moment of inertia (solid cylinder): I = (1/2)mr²
    Function MomentOfInertiaSolidCylinder(mass As Double, radius As Double)
        Return 0.5 * mass * radius * radius
    End Function

    ''' Rotational kinetic energy: KE_rot = ½Iω²
    Function RotationalKineticEnergy(I As Double, omega As Double)
        Return 0.5 * I * omega * omega
    End Function

    ''' Angular momentum: L = I·ω = r × p
    Function AngularMomentum(I As Double, omega As Double)
        Return I * omega
    End Function

    ' -- Gravitation --
    ''' Newton's Law of Gravitation: F = Gm₁m₂/r²
    Function GravitationalForce(m1 As Double, m2 As Double, distance As Double)
        Return G * m1 * m2 / (distance * distance)
    End Function

    ''' Gravitational potential energy: U = -Gm₁m₂/r
    Function GravitationalPotentialEnergy(m1 As Double, m2 As Double, distance As Double)
        Return -G * m1 * m2 / distance
    End Function

    ''' Escape velocity: v_esc = √(2GM/r)
    Function EscapeVelocity(planetMass As Double, planetRadius As Double)
        Return Math.Sqrt(2.0 * G * planetMass / planetRadius)
    End Function

    ' -- Simple Harmonic Motion --
    ''' Displacement in SHM: x(t) = A·cos(ωt + φ)
    Function SHM_Displacement(amplitude As Double, omega As Double, t As Double, phase As Double)
        Return amplitude * Math.Cos(omega * t + phase)
    End Function

    ''' Period of spring-mass: T = 2π√(m/k)
    Function PeriodSpringMass(mass As Double, springConstant As Double)
        Return 2.0 * Math.PI * Math.Sqrt(mass / springConstant)
    End Function

    ''' Period of simple pendulum: T = 2π√(L/g)
    Function PeriodPendulum(length As Double)
        Return 2.0 * Math.PI * Math.Sqrt(length / GRAVITY)
    End Function

    ''' Frequency: f = 1/T, ω = 2πf
    Function AngularFrequencyFromPeriod(period As Double)
        Return 2.0 * Math.PI / period
    End Function
End Class

' ═══════════════════════════════════════════════════════════════
' 2. THERMODYNAMICS
' ═══════════════════════════════════════════════════════════════
Public Class Thermodynamics
    ' -- Constants --
    Public Const R_GAS As Double = 8.314462618   ' J/(mol·K) universal gas constant
    Public Const K_BOLTZMANN As Double = 1.380649E-23 ' J/K Boltzmann constant
    Public Const N_AVOGADRO As Double = 6.02214076E+23 ' mol⁻¹ Avogadro's number
    Public Const STEFAN_BOLTZMANN As Double = 5.670374419E-8 ' W/(m²·K⁴)
    Public Const ZERO_CELSIUS As Double = 273.15 ' K

    ' -- Temperature Conversion --
    Function CelsiusToKelvin(celsius As Double)
        Return celsius + ZERO_CELSIUS
    End Function

    Function KelvinToCelsius(kelvin As Double)
        Return kelvin - ZERO_CELSIUS
    End Function

    Function CelsiusToFahrenheit(celsius As Double)
        Return celsius * 9.0 / 5.0 + 32.0
    End Function

    Function FahrenheitToCelsius(fahrenheit As Double)
        Return (fahrenheit - 32.0) * 5.0 / 9.0
    End Function

    ' -- Ideal Gas Law --
    ''' Ideal gas law: PV = nRT
    Function IdealGasPressure(moles As Double, temperatureK As Double, volume As Double)
        Return moles * R_GAS * temperatureK / volume
    End Function

    Function IdealGasVolume(moles As Double, temperatureK As Double, pressure As Double)
        Return moles * R_GAS * temperatureK / pressure
    End Function

    Function IdealGasMoles(pressure As Double, volume As Double, temperatureK As Double)
        Return pressure * volume / (R_GAS * temperatureK)
    End Function

    ' -- Kinetic Theory --
    ''' Average kinetic energy per molecule: KE_avg = (3/2)k_B·T
    Function AverageKineticEnergyPerMolecule(temperatureK As Double)
        Return 1.5 * K_BOLTZMANN * temperatureK
    End Function

    ''' RMS speed of gas molecules: v_rms = √(3RT/M)
    Function RMSSpeed(molarMassKgPerMol As Double, temperatureK As Double)
        Return Math.Sqrt(3.0 * R_GAS * temperatureK / molarMassKgPerMol)
    End Function

    ' -- Laws of Thermodynamics --
    ''' First Law: ΔU = Q - W
    Function FirstLaw_InternalEnergyChange(heatAdded As Double, workDoneBySystem As Double)
        Return heatAdded - workDoneBySystem
    End Function

    ''' Work done in isothermal expansion: W = nRT·ln(V₂/V₁)
    Function IsothermalWork(moles As Double, temperatureK As Double, v1 As Double, v2 As Double)
        Return moles * R_GAS * temperatureK * Math.Log(v2 / v1)
    End Function

    ''' Work done in isobaric process: W = P·ΔV
    Function IsobaricWork(pressure As Double, deltaV As Double)
        Return pressure * deltaV
    End Function

    ''' Heat capacity at constant volume: C_V = (f/2)R (f = degrees of freedom)
    Function HeatCapacityConstantVolume(degreesOfFreedom As Double)
        Return degreesOfFreedom * R_GAS / 2.0
    End Function

    ''' Heat capacity at constant pressure: C_P = C_V + R
    Function HeatCapacityConstantPressure(degreesOfFreedom As Double)
        Return HeatCapacityConstantVolume(degreesOfFreedom) + R_GAS
    End Function

    ''' Adiabatic index: γ = C_P / C_V
    Function AdiabaticIndex(degreesOfFreedom As Double)
        Return HeatCapacityConstantPressure(degreesOfFreedom) / HeatCapacityConstantVolume(degreesOfFreedom)
    End Function

    ''' Adiabatic process: TV^(γ-1) = constant
    Function AdiabaticFinalTemperature(t1 As Double, v1 As Double, v2 As Double, gamma As Double)
        Return t1 * Math.Pow(v1 / v2, gamma - 1.0)
    End Function

    ''' Efficiency of Carnot engine: η = 1 - T_cold/T_hot
    Function CarnotEfficiency(tColdK As Double, tHotK As Double)
        Return 1.0 - tColdK / tHotK
    End Function

    ' -- Entropy --
    ''' Entropy change in isothermal process: ΔS = Q/T
    Function EntropyChangeIsothermal(heatTransferred As Double, temperatureK As Double)
        Return heatTransferred / temperatureK
    End Function

    ''' Boltzmann entropy: S = k_B·ln(W)
    Function BoltzmannEntropy(microstates As Double)
        Return K_BOLTZMANN * Math.Log(microstates)
    End Function

    ' -- Heat Transfer --
    ''' Heat transfer: Q = mcΔT
    Function HeatTransfer(mass As Double, specificHeat As Double, deltaT As Double)
        Return mass * specificHeat * deltaT
    End Function

    ''' Latent heat: Q = mL
    Function LatentHeat(mass As Double, latentHeatCoefficient As Double)
        Return mass * latentHeatCoefficient
    End Function

    ''' Thermal conduction (Fourier's Law): dQ/dt = -kA·dT/dx
    Function ConductionRate(thermalConductivity As Double, area As Double,
                                   deltaT As Double, thickness As Double)
        Return thermalConductivity * area * deltaT / thickness
    End Function

    ''' Stefan-Boltzmann Law: P = εσAT⁴
    Function RadiativePower(emissivity As Double, area As Double, temperatureK As Double)
        Return emissivity * STEFAN_BOLTZMANN * area * Math.Pow(temperatureK, 4)
    End Function

    ''' Wien's Displacement Law: λ_max = b/T
    Function WiensDisplacement(temperatureK As Double)
        Const b As Double = 2.897771955E-3 ' m·K
        Return b / temperatureK
    End Function
End Class

' ═══════════════════════════════════════════════════════════════
' 3. ELECTROMAGNETISM
' ═══════════════════════════════════════════════════════════════
Public Class Electromagnetism
    ' -- Constants --
    Public Const K_COULOMB As Double = 8.9875517923E9        ' N·m²/C²
    Public Const EPSILON_0 As Double = 8.8541878128E-12      ' F/m (vacuum permittivity)
    Public Const MU_0 As Double = 1.25663706212E-6           ' N/A² (vacuum permeability)
    Public Const E_CHARGE As Double = 1.602176634E-19         ' C (elementary charge)
    Public Const SPEED_OF_LIGHT As Double = 299792458.0       ' m/s

    ' -- Coulomb's Law --
    ''' Coulomb's Law: F = k·q₁q₂/r²
    Function CoulombForce(q1 As Double, q2 As Double, distance As Double)
        Return K_COULOMB * q1 * q2 / (distance * distance)
    End Function

    ''' Electric field: E = F/q = kQ/r²
    Function ElectricField(charge As Double, distance As Double)
        Return K_COULOMB * charge / (distance * distance)
    End Function

    ''' Electric potential: V = kQ/r
    Function ElectricPotential(charge As Double, distance As Double)
        Return K_COULOMB * charge / distance
    End Function

    ''' Potential energy of two charges: U = k·q₁q₂/r
    Function ElectricPotentialEnergy(q1 As Double, q2 As Double, distance As Double)
        Return K_COULOMB * q1 * q2 / distance
    End Function

    ' -- Capacitance --
    ''' Capacitance: C = Q/V
    Function Capacitance(charge As Double, voltage As Double)
        Return charge / voltage
    End Function

    ''' Parallel plate capacitor: C = ε₀A/d
    Function ParallelPlateCapacitance(area As Double, distance As Double)
        Return EPSILON_0 * area / distance
    End Function

    ''' Energy stored in capacitor: U = ½CV²
    Function CapacitorEnergy(capacitance As Double, voltage As Double)
        Return 0.5 * capacitance * voltage * voltage
    End Function

    ''' Capacitors in series: 1/C_eq = 1/C₁ + 1/C₂
    Function CapacitorsInSeries(capacitances As Double())
        Dim sumReciprocals As Double = 0
        For Each c In capacitances
            sumReciprocals += 1.0 / c
        Next
        Return 1.0 / sumReciprocals
    End Function

    ''' Capacitors in parallel: C_eq = C₁ + C₂ + ...
    Function CapacitorsInParallel(capacitances As Double())
        Return capacitances.Sum()
    End Function

    ' -- Ohm's Law and Circuits --
    ''' Ohm's Law: V = IR
    Function OhmsLaw_Voltage(current As Double, resistance As Double)
        Return current * resistance
    End Function

    ''' Current from Ohm's Law: I = V/R
    Function OhmsLaw_Current(voltage As Double, resistance As Double)
        Return voltage / resistance
    End Function

    ''' Power in circuit: P = IV = I²R = V²/R
    Function ElectricPower(voltage As Double, current As Double)
        Return voltage * current
    End Function

    ''' Joule heating: P = I²R
    Function JouleHeating(current As Double, resistance As Double)
        Return current * current * resistance
    End Function

    ''' Resistors in series: R_eq = R₁ + R₂ + ...
    Function ResistorsInSeries(resistances As Double())
        Return resistances.Sum()
    End Function

    ''' Resistors in parallel: 1/R_eq = 1/R₁ + 1/R₂ + ...
    Function ResistorsInParallel(resistances As Double())
        Dim sumReciprocals As Double = 0
        For Each r In resistances
            sumReciprocals += 1.0 / r
        Next
        Return 1.0 / sumReciprocals
    End Function

    ''' Kirchhoff's Current Law: ΣI_in = ΣI_out
    Function KirchhoffCurrent(enteringCurrents As Double(), leavingCurrents As Double()) As Boolean
        Return Math.Abs(enteringCurrents.Sum() - leavingCurrents.Sum()) < 1E-10
    End Function

    ''' Kirchhoff's Voltage Law: ΣV_loop = 0
    Function KirchhoffVoltage(voltages As Double())
        Return voltages.Sum() ' Should be zero for closed loop
    End Function

    ' -- Magnetism --
    ''' Magnetic force on moving charge: F = qvB·sin(θ)
    Function MagneticForce(charge As Double, velocity As Double,
                                  magneticField As Double, angleRad As Double)
        Return charge * velocity * magneticField * Math.Sin(angleRad)
    End Function

    ''' Magnetic force on current-carrying wire: F = ILB·sin(θ)
    Function MagneticForceOnWire(current As Double, length As Double,
                                        magneticField As Double, angleRad As Double)
        Return current * length * magneticField * Math.Sin(angleRad)
    End Function

    ''' Biot-Savart Law for infinite straight wire: B = μ₀I/(2πr)
    Function MagneticFieldWire(current As Double, distance As Double)
        Return MU_0 * current / (2.0 * Math.PI * distance)
    End Function

    ''' Magnetic field inside solenoid: B = μ₀nI
    Function MagneticFieldSolenoid(turnsPerMeter As Double, current As Double)
        Return MU_0 * turnsPerMeter * current
    End Function

    ''' Magnetic flux: Φ_B = BA·cos(θ)
    Function MagneticFlux(magneticField As Double, area As Double, angleRad As Double)
        Return magneticField * area * Math.Cos(angleRad)
    End Function

    ' -- Electromagnetic Induction --
    ''' Faraday's Law: ε = -dΦ_B/dt
    Function InducedEMF(fluxChange As Double, timeInterval As Double)
        Return -fluxChange / timeInterval
    End Function

    ''' Motional EMF: ε = BLv
    Function MotionalEMF(magneticField As Double, length As Double, velocity As Double)
        Return magneticField * length * velocity
    End Function

    ''' Self-inductance: ε = -L·dI/dt
    Function SelfInducedEMF(inductance As Double, currentChange As Double, timeInterval As Double)
        Return -inductance * currentChange / timeInterval
    End Function

    ''' Energy stored in inductor: U = ½LI²
    Function InductorEnergy(inductance As Double, current As Double)
        Return 0.5 * inductance * current * current
    End Function

    ' -- Maxwell's Equations (Integral Form) --
    ''' Gauss's Law for electricity: ∮E·dA = Q_enclosed/ε₀
    Function GaussLawElectric(chargeEnclosed As Double)
        Return chargeEnclosed / EPSILON_0 ' Returns flux
    End Function

    ''' Gauss's Law for magnetism: ∮B·dA = 0
    Function GaussLawMagnetic()
        Return 0.0 ' Magnetic monopoles don't exist
    End Function

    ''' Faraday's Law (Maxwell): ∮E·dl = -dΦ_B/dt
    Function FaradayMaxwell(magneticFluxChange As Double, timeInterval As Double)
        Return -magneticFluxChange / timeInterval
    End Function

    ''' Ampère-Maxwell Law: ∮B·dl = μ₀(I + ε₀·dΦ_E/dt)
    Function AmpereMaxwell(conductionCurrent As Double, electricFluxChange As Double,
                                  timeInterval As Double)
        Return MU_0 * (conductionCurrent + EPSILON_0 * electricFluxChange / timeInterval)
    End Function

    ' -- Electromagnetic Waves --
    ''' Speed of EM wave: c = 1/√(ε₀μ₀)
    Function SpeedOfEMWave()
        Return 1.0 / Math.Sqrt(EPSILON_0 * MU_0)
    End Function

    ''' Wave equation: c = λf
    Function Wavelength(frequency As Double)
        Return SPEED_OF_LIGHT / frequency
    End Function

    ''' Frequency from wavelength: f = c/λ
    Function Frequency(wavelength As Double)
        Return SPEED_OF_LIGHT / wavelength
    End Function

    ''' Energy of photon: E = hf = hc/λ
    Function PhotonEnergy(frequency As Double)
        Const PLANCK As Double = 6.62607015E-34 ' J·s
        Return PLANCK * frequency
    End Function

    ''' Poynting vector: S = (1/μ₀)E×B
    Function PoyntingVector(electricField As Double, magneticField As Double)
        Return electricField * magneticField / MU_0
    End Function
End Class

' ═══════════════════════════════════════════════════════════════
' 4. WAVE PHENOMENA
' ═══════════════════════════════════════════════════════════════
Public Class WavePhenomena
    ' -- Wave Equation --
    ''' Wave speed: v = f·λ
    Function WaveSpeed(frequency As Double, wavelength As Double)
        Return frequency * wavelength
    End Function

    ''' Wave number: k = 2π/λ
    Function WaveNumber(wavelength As Double)
        Return 2.0 * Math.PI / wavelength
    End Function

    ''' Angular frequency: ω = 2πf
    Function AngularFrequency(frequency As Double)
        Return 2.0 * Math.PI * frequency
    End Function

    ''' General wave function: y(x,t) = A·sin(kx - ωt + φ)
    Function WaveFunction(amplitude As Double, waveNumber As Double,
                                 angularFreq As Double, x As Double, t As Double, phase As Double)
        Return amplitude * Math.Sin(waveNumber * x - angularFreq * t + phase)
    End Function

    ''' Wave on a string: v = √(T/μ)
    Function WaveSpeedOnString(tension As Double, linearDensity As Double)
        Return Math.Sqrt(tension / linearDensity)
    End Function

    ' -- Sound Waves --
    ''' Speed of sound in air (approximate): v = 331.3 + 0.606·T(°C)
    Function SpeedOfSound(celsius As Double)
        Return 331.3 + 0.606 * celsius
    End Function

    ''' Sound intensity level: β = 10·log₁₀(I/I₀) dB
    Function SoundLevelDB(intensity As Double)
        Const I0 As Double = 1.0E-12 ' W/m² threshold of hearing
        Return 10.0 * Math.Log10(intensity / I0)
    End Function

    ''' Doppler effect (moving source): f' = f·(v/(v±v_s))
    Function DopplerEffect_Source(frequency As Double, waveSpeed As Double,
                                         sourceSpeed As Double, movingToward As Boolean)
        If movingToward Then
            Return frequency * waveSpeed / (waveSpeed - sourceSpeed)
        Else
            Return frequency * waveSpeed / (waveSpeed + sourceSpeed)
        End If
    End Function

    ''' Doppler effect (moving observer): f' = f·((v±v_o)/v)
    Function DopplerEffect_Observer(frequency As Double, waveSpeed As Double,
                                           observerSpeed As Double, movingToward As Boolean)
        If movingToward Then
            Return frequency * (waveSpeed + observerSpeed) / waveSpeed
        Else
            Return frequency * (waveSpeed - observerSpeed) / waveSpeed
        End If
    End Function

    ' -- Interference --
    ''' Constructive interference: d·sin(θ) = mλ
    Function ConstructiveInterferenceAngle(d As Double, order As Integer, wavelength As Double)
        Return Math.Asin(order * wavelength / d)
    End Function

    ''' Destructive interference: d·sin(θ) = (m+½)λ
    Function DestructiveInterferenceAngle(d As Double, order As Integer, wavelength As Double)
        Return Math.Asin((order + 0.5) * wavelength / d)
    End Function

    ''' Beat frequency: f_beat = |f₁ - f₂|
    Function BeatFrequency(f1 As Double, f2 As Double)
        Return Math.Abs(f1 - f2)
    End Function

    ' -- Standing Waves --
    ''' Standing wave on fixed string: λ_n = 2L/n
    Function StandingWaveWavelength(length As Double, harmonic As Integer)
        Return 2.0 * length / harmonic
    End Function

    ''' Frequency of standing wave: f_n = n·v/(2L)
    Function StandingWaveFrequency(length As Double, waveSpeed As Double, harmonic As Integer)
        Return harmonic * waveSpeed / (2.0 * length)
    End Function

    ''' Fundamental frequency: f₁ = v/(2L)
    Function FundamentalFrequency(length As Double, waveSpeed As Double)
        Return waveSpeed / (2.0 * length)
    End Function
End Class

' ═══════════════════════════════════════════════════════════════
' 5. OPTICS
' ═══════════════════════════════════════════════════════════════
Public Class Optics
    ' -- Snell's Law and Refraction --
    ''' Snell's Law: n₁sin(θ₁) = n₂sin(θ₂)
    Function SnellsLaw(n1 As Double, theta1Rad As Double, n2 As Double)
        Return Math.Asin(n1 * Math.Sin(theta1Rad) / n2)
    End Function

    ''' Critical angle: θ_c = arcsin(n₂/n₁)
    Function CriticalAngle(n1 As Double, n2 As Double)
        Return Math.Asin(n2 / n1)
    End Function

    ''' Index of refraction: n = c/v
    Function RefractiveIndex(speedInMedium As Double)
        Return Electromagnetism.SPEED_OF_LIGHT / speedInMedium
    End Function

    ' -- Lenses and Mirrors --
    ''' Thin lens equation: 1/f = 1/do + 1/di
    Function ThinLens_ImageDistance(focalLength As Double, objectDistance As Double)
        Return 1.0 / (1.0 / focalLength - 1.0 / objectDistance)
    End Function

    ''' Magnification: m = -di/do = hi/ho
    Function Magnification(imageDistance As Double, objectDistance As Double)
        Return -imageDistance / objectDistance
    End Function

    ''' Mirror equation: 1/f = 1/do + 1/di
    Function MirrorImageDistance(focalLength As Double, objectDistance As Double)
        Return 1.0 / (1.0 / focalLength - 1.0 / objectDistance)
    End Function

    ''' Lens maker's formula: 1/f = (n-1)(1/R₁ - 1/R₂)
    Function LensMaker(n As Double, r1 As Double, r2 As Double)
        Return 1.0 / ((n - 1.0) * (1.0 / r1 - 1.0 / r2))
    End Function

    ' -- Wave Optics --
    ''' Double-slit bright fringe: d·sin(θ) = mλ
    Function DoubleSlitBrightAngle(slitSeparation As Double, order As Integer,
                                          wavelength As Double)
        Return Math.Asin(order * wavelength / slitSeparation)
    End Function

    ''' Single-slit dark fringe: a·sin(θ) = mλ
    Function SingleSlitDarkAngle(slitWidth As Double, order As Integer,
                                        wavelength As Double)
        Return Math.Asin(order * wavelength / slitWidth)
    End Function

    ''' Diffraction grating: d·sin(θ) = mλ
    Function GratingAngle(linesPerMeter As Double, order As Integer, wavelength As Double)
        Dim d As Double = 1.0 / linesPerMeter
        Return Math.Asin(order * wavelength / d)
    End Function

    ''' Rayleigh criterion: θ_min = 1.22λ/D
    Function RayleighCriterion(wavelength As Double, apertureDiameter As Double)
        Return 1.22 * wavelength / apertureDiameter
    End Function

    ''' Brewster's angle: θ_B = arctan(n₂/n₁)
    Function BrewsterAngle(n1 As Double, n2 As Double)
        Return Math.Atan(n2 / n1)
    End Function

    ''' Malus's Law: I = I₀cos²(θ)
    Function MalusLaw(initialIntensity As Double, angleRad As Double)
        Return initialIntensity * Math.Cos(angleRad) * Math.Cos(angleRad)
    End Function

    ' -- Optical Power and Magnification --
    ''' Optical power (diopters): P = 1/f (f in meters)
    Function OpticalPower(focalLengthMeters As Double)
        Return 1.0 / focalLengthMeters
    End Function

    ''' Angular magnification (magnifying glass): M = 25/f (f in cm)
    Function AngularMagnification(focalLengthCm As Double)
        Return 25.0 / focalLengthCm
    End Function

    ''' Telescope magnification: M = f_o/f_e
    Function TelescopeMagnification(objectiveFocalLength As Double,
                                           eyepieceFocalLength As Double)
        Return objectiveFocalLength / eyepieceFocalLength
    End Function
End Class

' ═══════════════════════════════════════════════════════════════
' 6. RELATIVITY
' ═══════════════════════════════════════════════════════════════
Public Class Relativity
    Private Const C As Double = 299792458.0 ' m/s speed of light

    ' -- Special Relativity --
    ''' Lorentz factor: γ = 1/√(1 - v²/c²)
    Function LorentzFactor(velocity As Double)
        Return 1.0 / Math.Sqrt(1.0 - (velocity * velocity) / (C * C))
    End Function

    ''' Time dilation: Δt' = γ·Δt₀
    Function TimeDilation(properTime As Double, velocity As Double)
        Return LorentzFactor(velocity) * properTime
    End Function

    ''' Length contraction: L' = L₀/γ
    Function LengthContraction(properLength As Double, velocity As Double)
        Return properLength / LorentzFactor(velocity)
    End Function

    ''' Relativistic mass: m = γ·m₀
    Function RelativisticMass(restMass As Double, velocity As Double)
        Return LorentzFactor(velocity) * restMass
    End Function

    ''' Relativistic momentum: p = γ·m₀v
    Function RelativisticMomentum(restMass As Double, velocity As Double)
        Return LorentzFactor(velocity) * restMass * velocity
    End Function

    ''' Mass-Energy Equivalence: E = mc²
    Function MassEnergy(mass As Double)
        Return mass * C * C
    End Function

    ''' Relativistic energy: E² = (pc)² + (m₀c²)²
    Function RelativisticEnergy(restMass As Double, velocity As Double)
        Dim pc As Double = RelativisticMomentum(restMass, velocity) * C
        Dim mc2 As Double = restMass * C * C
        Return Math.Sqrt(pc * pc + mc2 * mc2)
    End Function

    ''' Kinetic energy (relativistic): KE = (γ-1)m₀c²
    Function RelativisticKineticEnergy(restMass As Double, velocity As Double)
        Return (LorentzFactor(velocity) - 1.0) * restMass * C * C
    End Function

    ''' Velocity addition: u' = (u+v)/(1+uv/c²)
    Function VelocityAddition(u As Double, v As Double)
        Return (u + v) / (1.0 + u * v / (C * C))
    End Function

    ''' Relativistic Doppler effect: f' = f·√((1+β)/(1-β))
    Function RelativisticDoppler(frequency As Double, velocity As Double)
        Dim beta As Double = velocity / C
        Return frequency * Math.Sqrt((1.0 + beta) / (1.0 - beta))
    End Function

    ' -- General Relativity --
    ''' Schwarzschild radius: R_s = 2GM/c²
    Function SchwarzschildRadius(mass As Double)
        Const G As Double = 6.6743E-11
        Return 2.0 * G * mass / (C * C)
    End Function

    ''' Gravitational time dilation: Δt' = Δt·√(1 - R_s/r)
    Function GravitationalTimeDilation(properTime As Double, mass As Double, distance As Double)
        Dim rs As Double = SchwarzschildRadius(mass)
        Return properTime * Math.Sqrt(1.0 - rs / distance)
    End Function

    ''' Gravitational redshift: z = Δλ/λ ≈ GM/(rc²)
    Function GravitationalRedshift(mass As Double, distance As Double, wavelength As Double)
        Const G As Double = 6.6743E-11
        Dim deltaLambda As Double = G * mass * wavelength / (distance * C * C)
        Return deltaLambda
    End Function
End Class

' ═══════════════════════════════════════════════════════════════
' 7. QUANTUM MECHANICS
' ═══════════════════════════════════════════════════════════════
Public Class QuantumMechanics
    ' -- Constants --
    Public Const H_PLANCK As Double = 6.62607015E-34      ' J·s
    Public Const HBAR As Double = 1.054571817E-34          ' J·s (h/2π)
    Public Const M_ELECTRON As Double = 9.1093837015E-31   ' kg
    Public Const M_PROTON As Double = 1.67262192369E-27    ' kg
    Public Const BOHR_RADIUS As Double = 5.29177210903E-11 ' m
    Public Const RYDBERG As Double = 1.097373156816E7      ' m⁻¹

    ' -- Wave-Particle Duality --
    ''' De Broglie wavelength: λ = h/p = h/(mv)
    Function DeBroglieWavelength(mass As Double, velocity As Double)
        Return H_PLANCK / (mass * velocity)
    End Function

    ''' Photon energy: E = hf = hc/λ
    Function PhotonEnergyFromFrequency(frequency As Double)
        Return H_PLANCK * frequency
    End Function

    ''' Photon energy from wavelength: E = hc/λ
    Function PhotonEnergyFromWavelength(wavelength As Double)
        Return H_PLANCK * 299792458.0 / wavelength
    End Function

    ''' Photon momentum: p = h/λ = E/c
    Function PhotonMomentum(wavelength As Double)
        Return H_PLANCK / wavelength
    End Function

    ' -- Heisenberg Uncertainty Principle --
    ''' Position-momentum: Δx·Δp ≥ ℏ/2
    Function HeisenbergPositionMomentum(deltaX As Double)
        Return HBAR / (2.0 * deltaX) ' Returns minimum Δp
    End Function

    ''' Energy-time: ΔE·Δt ≥ ℏ/2
    Function HeisenbergEnergyTime(deltaT As Double)
        Return HBAR / (2.0 * deltaT) ' Returns minimum ΔE
    End Function

    ' -- Bohr Model --
    ''' Bohr radius: a₀ = 4πε₀ℏ²/(m_e·e²)
    Function BohrRadius()
        Return BOHR_RADIUS
    End Function

    ''' Energy level: E_n = -13.6eV/n²
    Function BohrEnergyLevel(n As Integer)
        Return -13.6 / (n * n) ' in eV
    End Function

    ''' Rydberg formula: 1/λ = R(1/n₁² - 1/n₂²)
    Function RydbergWavelength(n1 As Integer, n2 As Integer)
        Return 1.0 / (RYDBERG * (1.0 / (n1 * n1) - 1.0 / (n2 * n2)))
    End Function

    ' -- Schrödinger Equation --
    ''' Time-independent Schrödinger (1D): -(ℏ²/2m)d²ψ/dx² + Vψ = Eψ
    Function Schrodinger_SecondDerivative(mass As Double, potential As Double,
                                                  energy As Double, psi As Double)
        ' Returns d²ψ/dx² = -(2m/ℏ²)(E-V)ψ
        Return -(2.0 * mass / (HBAR * HBAR)) * (energy - potential) * psi
    End Function

    ' -- Particle in a Box --
    ''' Energy levels: E_n = n²h²/(8mL²)
    Function ParticleInBoxEnergy(n As Integer, mass As Double, length As Double)
        Return n * n * H_PLANCK * H_PLANCK / (8.0 * mass * length * length)
    End Function

    ''' Wavefunction: ψ_n(x) = √(2/L)·sin(nπx/L)
    Function ParticleInBoxWavefunction(n As Integer, length As Double, x As Double)
        Return Math.Sqrt(2.0 / length) * Math.Sin(n * Math.PI * x / length)
    End Function

    ' -- Quantum Harmonic Oscillator --
    ''' Energy levels: E_n = ℏω(n + ½)
    Function HarmonicOscillatorEnergy(n As Integer, omega As Double)
        Return HBAR * omega * (n + 0.5)
    End Function

    ''' Zero-point energy: E₀ = ½ℏω
    Function ZeroPointEnergy(omega As Double)
        Return 0.5 * HBAR * omega
    End Function

    ' -- Photoelectric Effect --
    ''' Einstein's photoelectric equation: KE_max = hf - Φ
    Function PhotoelectricMaxKE(frequency As Double, workFunction As Double)
        Return H_PLANCK * frequency - workFunction
    End Function

    ''' Threshold frequency: f₀ = Φ/h
    Function ThresholdFrequency(workFunction As Double)
        Return workFunction / H_PLANCK
    End Function

    ''' Stopping potential: eV_s = KE_max
    Function StoppingPotential(maxKE As Double)
        Return maxKE / 1.602176634E-19 ' Convert J to eV
    End Function

    ' -- Compton Scattering --
    ''' Compton shift: Δλ = (h/(m_e·c))·(1-cos(θ))
    Function ComptonShift(scatteringAngleRad As Double)
        Const COMPTON_WAVELENGTH As Double = 2.4263102389E-12 ' m
        Return COMPTON_WAVELENGTH * (1.0 - Math.Cos(scatteringAngleRad))
    End Function

    ' -- Tunneling --
    ''' Transmission coefficient (approximate): T ≈ e^(-2κL), κ = √(2m(V-E))/ℏ
    Function TunnelingProbability(mass As Double, barrierHeight As Double,
                                         energy As Double, barrierWidth As Double)
        Dim kappa As Double = Math.Sqrt(2.0 * mass * (barrierHeight - energy)) / HBAR
        Return Math.Exp(-2.0 * kappa * barrierWidth)
    End Function

    ' -- Pauli Exclusion Principle --
    ''' Fermi energy (electron gas): E_F = (ℏ²/2m)(3π²n)^(2/3)
    Function FermiEnergy(electronDensity As Double, mass As Double)
        Dim factor As Double = 3.0 * Math.PI * Math.PI * electronDensity
        Return (HBAR * HBAR / (2.0 * mass)) * Math.Pow(factor, 2.0 / 3.0)
    End Function
End Class

' ═══════════════════════════════════════════════════════════════
' 8. FLUID DYNAMICS
' ═══════════════════════════════════════════════════════════════
Public Class FluidDynamics
    ' -- Constants --
    Public Const WATER_DENSITY As Double = 1000.0       ' kg/m³
    Public Const AIR_DENSITY As Double = 1.225          ' kg/m³ (at sea level)
    Public Const ATMOSPHERIC_PRESSURE As Double = 101325.0 ' Pa

    ' -- Density and Pressure --
    ''' Density: ρ = m/V
    Function Density(mass As Double, volume As Double)
        Return mass / volume
    End Function

    ''' Pressure: P = F/A
    Function Pressure(force As Double, area As Double)
        Return force / area
    End Function

    ''' Hydrostatic pressure: P = ρgh
    Function HydrostaticPressure(density As Double, height As Double)
        Return density * ClassicalMechanics.GRAVITY * height
    End Function

    ''' Absolute pressure at depth: P = P₀ + ρgh
    Function AbsolutePressure(surfacePressure As Double, density As Double, depth As Double)
        Return surfacePressure + density * ClassicalMechanics.GRAVITY * depth
    End Function

    ' -- Pascal's Principle --
    ''' Pascal's law: F₁/A₁ = F₂/A₂
    Function PascalForce(force1 As Double, area1 As Double, area2 As Double)
        Return force1 * area2 / area1
    End Function

    ' -- Buoyancy (Archimedes' Principle) --
    ''' Buoyant force: F_B = ρ_fluid·V_displaced·g
    Function BuoyantForce(fluidDensity As Double, displacedVolume As Double)
        Return fluidDensity * displacedVolume * ClassicalMechanics.GRAVITY
    End Function

    ''' Fraction submerged: f = ρ_object/ρ_fluid
    Function FractionSubmerged(objectDensity As Double, fluidDensity As Double)
        Return objectDensity / fluidDensity
    End Function

    ' -- Bernoulli's Equation --
    ''' Bernoulli's equation: P + ½ρv² + ρgh = constant
    Function BernoullisConstant(pressure As Double, density As Double,
                                        velocity As Double, height As Double)
        Return pressure + 0.5 * density * velocity * velocity + density * ClassicalMechanics.GRAVITY * height
    End Function

    ''' Velocity from pressure difference (Torricelli): v = √(2(P₁-P₂)/ρ)
    Function TorricelliVelocity(pressureDiff As Double, density As Double)
        Return Math.Sqrt(2.0 * pressureDiff / density)
    End Function

    ''' Efflux speed (Torricelli's Law): v = √(2gh)
    Function EffluxSpeed(height As Double)
        Return Math.Sqrt(2.0 * ClassicalMechanics.GRAVITY * height)
    End Function

    ' -- Continuity Equation --
    ''' Continuity: A₁v₁ = A₂v₂
    Function Continuity_Velocity(area1 As Double, velocity1 As Double, area2 As Double)
        Return area1 * velocity1 / area2
    End Function

    ''' Volumetric flow rate: Q = Av
    Function FlowRate(area As Double, velocity As Double)
        Return area * velocity
    End Function

    ''' Mass flow rate: ṁ = ρAv
    Function MassFlowRate(density As Double, area As Double, velocity As Double)
        Return density * area * velocity
    End Function

    ' -- Viscosity --
    ''' Newton's law of viscosity: τ = μ·du/dy
    Function ShearStress(viscosity As Double, velocityGradient As Double)
        Return viscosity * velocityGradient
    End Function

    ''' Reynolds number: Re = ρvL/μ
    Function ReynoldsNumber(density As Double, velocity As Double,
                                    characteristicLength As Double, viscosity As Double)
        Return density * velocity * characteristicLength / viscosity
    End Function

    ''' Stokes' Law: F_d = 6πμrv
    Function StokesDrag(viscosity As Double, radius As Double, velocity As Double)
        Return 6.0 * Math.PI * viscosity * radius * velocity
    End Function

    ''' Terminal velocity (sphere): v_t = (2r²(ρ_s-ρ_f)g)/(9μ)
    Function TerminalVelocity(sphereRadius As Double, sphereDensity As Double,
                                      fluidDensity As Double, viscosity As Double)
        Return 2.0 * sphereRadius * sphereRadius * (sphereDensity - fluidDensity) *
               ClassicalMechanics.GRAVITY / (9.0 * viscosity)
    End Function

    ' -- Poiseuille's Law --
    ''' Poiseuille flow: Q = πr⁴ΔP/(8μL)
    Function PoiseuilleFlow(radius As Double, pressureDrop As Double,
                                    length As Double, viscosity As Double)
        Return Math.PI * Math.Pow(radius, 4) * pressureDrop / (8.0 * viscosity * length)
    End Function

    ' -- Surface Tension --
    ''' Capillary rise: h = 2γcos(θ)/(ρgr)
    Function CapillaryRise(surfaceTension As Double, contactAngleRad As Double,
                                   density As Double, radius As Double)
        Return 2.0 * surfaceTension * Math.Cos(contactAngleRad) /
               (density * ClassicalMechanics.GRAVITY * radius)
    End Function

    ''' Laplace pressure: ΔP = 2γ/r (spherical)
    Function LaplacePressure(surfaceTension As Double, radius As Double)
        Return 2.0 * surfaceTension / radius
    End Function

    ' -- Drag Force --
    ''' Drag force: F_d = ½ρv²C_d·A
    Function DragForce(density As Double, velocity As Double,
                               dragCoefficient As Double, area As Double)
        Return 0.5 * density * velocity * velocity * dragCoefficient * area
    End Function

    ' -- Mach Number --
    ''' Mach number: M = v/v_sound
    Function MachNumber(velocity As Double, speedOfSound As Double)
        Return velocity / speedOfSound
    End Function

    ' -- Compressibility --
    ''' Bulk modulus: B = -V·dP/dV
    Function BulkModulus(volume As Double, pressureChange As Double, volumeChange As Double)
        Return -volume * pressureChange / volumeChange
    End Function

    ''' Speed of sound in fluid: v = √(B/ρ)
    Function SpeedOfSoundInFluid(bulkModulus As Double, density As Double)
        Return Math.Sqrt(bulkModulus / density)
    End Function
End Class
