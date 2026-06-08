'===============================================================
' MATH-PHYSICS BRIDGE
' Connects every mathematical concept to its physical principle
' Demonstrates that physics is applied mathematics
'===============================================================

Imports System
Imports System.Collections.Generic
Imports System.Linq

' ═══════════════════════════════════════════════════════════════
' MODULE: MathPhysics Bridge
' ═══════════════════════════════════════════════════════════════
Module MathPhysicsBridge

    Sub Main()
        ' Build the complete bridge
        Dim bridge As New BridgeBuilder()
        bridge.ConstructAllBridges()

        ' Inspect the bridge collection at this breakpoint
        Dim allConnections As List(Of MathPhysicsConnection) = bridge.Connections
    End Sub

End Module

' ═══════════════════════════════════════════════════════════════
' DATA STRUCTURE: Represents a single math-physics connection
' ═══════════════════════════════════════════════════════════════
Public Class MathPhysicsConnection
    Public Property MathConcept As String        ' e.g., "Multiplication (*)"
    Public Property MathCategory As String       ' e.g., "Arithmetic"
    Public Property MathFormula As String        ' e.g., "a * b"
    Public Property PhysicalPrinciple As String  ' e.g., "Newton's Second Law"
    Public Property PhysicalLaw As String        ' e.g., "F = m·a"
    Public Property PhysicalDomain As String     ' e.g., "Classical Mechanics"
    Public Property Description As String        ' Explanation of connection
    Public Property ExampleCalculation As Double ' Numerical example result

    Public Overrides Function ToString() As String
        Return $"[{MathCategory}] {MathConcept} → {PhysicalPrinciple} [{PhysicalDomain}]"
    End Function
End Class

' ═══════════════════════════════════════════════════════════════
' BRIDGE BUILDER: Constructs all math-physics connections
' ═══════════════════════════════════════════════════════════════
Public Class BridgeBuilder
    Public Property Connections As New List(Of MathPhysicsConnection)()

    ' ─── Physical Constants ───
    Private Const G As Double = 6.6743E-11          ' Gravitational constant
    Private Const G_ACC As Double = 9.80665         ' Standard gravity (m/s²)
    Private Const C_LIGHT As Double = 299792458.0   ' Speed of light (m/s)
    Private Const H_PLANCK As Double = 6.62607015E-34 ' Planck's constant (J·s)
    Private Const HBAR As Double = 1.054571817E-34  ' Reduced Planck constant
    Private Const K_BOLTZ As Double = 1.380649E-23  ' Boltzmann constant (J/K)
    Private Const R_GAS As Double = 8.314462618     ' Universal gas constant
    Private Const K_COULOMB As Double = 8.9875517923E9 ' Coulomb constant
    Private Const EPSILON_0 As Double = 8.8541878128E-12 ' Vacuum permittivity
    Private Const MU_0 As Double = 1.25663706212E-6 ' Vacuum permeability
    Private Const E_CHARGE As Double = 1.602176634E-19 ' Elementary charge
    Private Const M_ELECTRON As Double = 9.1093837015E-31 ' Electron mass
    Private Const SIGMA_SB As Double = 5.670374419E-8 ' Stefan-Boltzmann constant

    ' ═══════════════════════════════════════════════════════════
    ' MASTER BRIDGE CONSTRUCTION
    ' ═══════════════════════════════════════════════════════════
    Public Sub ConstructAllBridges()
        Bridge_Addition()
        Bridge_Subtraction()
        Bridge_Multiplication()
        Bridge_Division()
        Bridge_Exponentiation()
        Bridge_SquareRoot()
        Bridge_Sine_Cosine()
        Bridge_Tangent()
        Bridge_InverseTrig()
        Bridge_Logarithms()
        Bridge_Differential()
        Bridge_Integral()
        Bridge_VectorOperations()
        Bridge_CrossProduct()
        Bridge_DotProduct()
        Bridge_Proportionality()
        Bridge_InverseProportion()
        Bridge_LinearEquations()
        Bridge_QuadraticEquations()
        Bridge_ExponentialDecay()
        Bridge_LogarithmicScaling()
        Bridge_AbsoluteValue()
        Bridge_TrigonometricIdentities()
        Bridge_Hyperbolic()
        Bridge_ComplexNumbers()
        Bridge_Probability()
        Bridge_Statistics()
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 1. ADDITION → SUPERPOSITION
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_Addition()
        ' Addition in math maps to superposition, vector addition, series circuits
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Addition (+)",
            .MathCategory = "Arithmetic",
            .MathFormula = "a + b + c + ...",
            .PhysicalPrinciple = "Principle of Superposition",
            .PhysicalLaw = "F_net = F₁ + F₂ + F₃ + ...",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "The net force on an object is the vector sum of all individual forces. In waves, amplitudes add via superposition.",
            .ExampleCalculation = 10.0 + 5.0 - 3.0 ' F_net = 10N + 5N - 3N = 12N
        }
        Connections.Add(conn)

        ' Resistors in series
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Addition (+)",
            .MathCategory = "Arithmetic",
            .MathFormula = "R_eq = R₁ + R₂ + R₃",
            .PhysicalPrinciple = "Resistors in Series",
            .PhysicalLaw = "R_total = ΣRᵢ",
            .PhysicalDomain = "Electromagnetism",
            .Description = "Total resistance in series is the sum of individual resistances.",
            .ExampleCalculation = 100.0 + 220.0 + 330.0 ' 650 Ω
        }
        Connections.Add(conn2)

        ' Capacitors in parallel
        Dim conn3 As New MathPhysicsConnection With {
            .MathConcept = "Addition (+)",
            .MathCategory = "Arithmetic",
            .MathFormula = "C_eq = C₁ + C₂",
            .PhysicalPrinciple = "Capacitors in Parallel",
            .PhysicalLaw = "C_total = ΣCᵢ",
            .PhysicalDomain = "Electromagnetism",
            .Description = "Total capacitance in parallel adds directly.",
            .ExampleCalculation = 10E-6 + 22E-6 ' 32 µF
        }
        Connections.Add(conn3)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 2. SUBTRACTION → POTENTIAL DIFFERENCE, RELATIVE MOTION
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_Subtraction()
        ' Potential difference is subtraction of potentials
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Subtraction (-)",
            .MathCategory = "Arithmetic",
            .MathFormula = "ΔV = V_A - V_B",
            .PhysicalPrinciple = "Electric Potential Difference (Voltage)",
            .PhysicalLaw = "V = ΔU/q = (U_A - U_B)/q",
            .PhysicalDomain = "Electromagnetism",
            .Description = "Voltage is the difference in electric potential between two points.",
            .ExampleCalculation = 12.0 - 5.0 ' 7.0 V
        }
        Connections.Add(conn)

        ' Relative velocity
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Subtraction (-)",
            .MathCategory = "Arithmetic",
            .MathFormula = "v_rel = v_object - v_observer",
            .PhysicalPrinciple = "Relative Velocity",
            .PhysicalLaw = "v_AB = v_A - v_B",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Relative velocity is the vector difference between two velocities.",
            .ExampleCalculation = 60.0 - 50.0 ' 10 m/s
        }
        Connections.Add(conn2)

        ' Temperature difference
        Dim conn3 As New MathPhysicsConnection With {
            .MathConcept = "Subtraction (-)",
            .MathCategory = "Arithmetic",
            .MathFormula = "ΔT = T_hot - T_cold",
            .PhysicalPrinciple = "Heat Transfer Driving Force",
            .PhysicalLaw = "Q = mcΔT",
            .PhysicalDomain = "Thermodynamics",
            .Description = "Heat flows from higher to lower temperature due to the temperature difference.",
            .ExampleCalculation = 373.15 - 293.15 ' 80 K
        }
        Connections.Add(conn3)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 3. MULTIPLICATION → FORCE, MOMENTUM, ENERGY
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_Multiplication()
        ' F = ma
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Multiplication (*)",
            .MathCategory = "Arithmetic",
            .MathFormula = "F = m * a",
            .PhysicalPrinciple = "Newton's Second Law of Motion",
            .PhysicalLaw = "F = m·a",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Force equals mass multiplied by acceleration. This is the fundamental bridge between multiplication and dynamics.",
            .ExampleCalculation = 10.0 * 9.80665 ' 98.07 N (1 kg mass under gravity)
        }
        Connections.Add(conn)

        ' Momentum p = mv
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Multiplication (*)",
            .MathCategory = "Arithmetic",
            .MathFormula = "p = m * v",
            .PhysicalPrinciple = "Linear Momentum",
            .PhysicalLaw = "p = m·v",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Momentum is the product of mass and velocity.",
            .ExampleCalculation = 1500.0 * 20.0 ' 30,000 kg·m/s (car)
        }
        Connections.Add(conn2)

        ' KE = ½mv²
        Dim conn3 As New MathPhysicsConnection With {
            .MathConcept = "Multiplication (*)",
            .MathCategory = "Arithmetic",
            .MathFormula = "KE = 0.5 * m * v * v",
            .PhysicalPrinciple = "Kinetic Energy",
            .PhysicalLaw = "KE = ½mv²",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Kinetic energy involves multiplication of mass with velocity squared.",
            .ExampleCalculation = 0.5 * 1500.0 * 20.0 * 20.0 ' 300,000 J
        }
        Connections.Add(conn3)

        ' Work W = F·d
        Dim conn4 As New MathPhysicsConnection With {
            .MathConcept = "Multiplication (*)",
            .MathCategory = "Arithmetic",
            .MathFormula = "W = F * d * cos(θ)",
            .PhysicalPrinciple = "Work-Energy Theorem",
            .PhysicalLaw = "W = F·d·cos(θ)",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Work is force multiplied by displacement in the direction of force.",
            .ExampleCalculation = 100.0 * 5.0 * Math.Cos(0) ' 500 J
        }
        Connections.Add(conn4)

        ' Ideal gas law PV = nRT
        Dim conn5 As New MathPhysicsConnection With {
            .MathConcept = "Multiplication (*)",
            .MathCategory = "Arithmetic",
            .MathFormula = "P * V = n * R * T",
            .PhysicalPrinciple = "Ideal Gas Law",
            .PhysicalLaw = "PV = nRT",
            .PhysicalDomain = "Thermodynamics",
            .Description = "Pressure times volume equals the product of moles, gas constant, and temperature.",
            .ExampleCalculation = 1.0 * R_GAS * 300.0 / 0.024 ' ~103,930 Pa (1 mole at 300K in 24L)
        }
        Connections.Add(conn5)

        ' Coulomb's Law F = kq₁q₂/r²
        Dim conn6 As New MathPhysicsConnection With {
            .MathConcept = "Multiplication (*)",
            .MathCategory = "Arithmetic",
            .MathFormula = "F = k * q₁ * q₂ / (r * r)",
            .PhysicalPrinciple = "Coulomb's Law of Electrostatics",
            .PhysicalLaw = "F = k·q₁·q₂/r²",
            .PhysicalDomain = "Electromagnetism",
            .Description = "Electric force is proportional to the product of charges.",
            .ExampleCalculation = K_COULOMB * E_CHARGE * E_CHARGE / (1E-10 * 1E-10) ' Force between 2 electrons at 1Å
        }
        Connections.Add(conn6)

        ' E = mc²
        Dim conn7 As New MathPhysicsConnection With {
            .MathConcept = "Multiplication (*)",
            .MathCategory = "Arithmetic",
            .MathFormula = "E = m * c * c",
            .PhysicalPrinciple = "Mass-Energy Equivalence",
            .PhysicalLaw = "E = mc²",
            .PhysicalDomain = "Relativity",
            .Description = "Einstein's famous equation showing energy equals mass times speed of light squared.",
            .ExampleCalculation = 1.0 * C_LIGHT * C_LIGHT ' 8.988E16 J per kg
        }
        Connections.Add(conn7)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 4. DIVISION → RATE CONCEPTS
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_Division()
        ' Velocity v = Δx/Δt
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Division (/)",
            .MathCategory = "Arithmetic",
            .MathFormula = "v = Δx / Δt",
            .PhysicalPrinciple = "Velocity (Rate of Change of Position)",
            .PhysicalLaw = "v = dx/dt",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Velocity is displacement divided by time—the fundamental rate concept in physics.",
            .ExampleCalculation = 100.0 / 10.0 ' 10 m/s
        }
        Connections.Add(conn)

        ' Density ρ = m/V
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Division (/)",
            .MathCategory = "Arithmetic",
            .MathFormula = "ρ = m / V",
            .PhysicalPrinciple = "Density",
            .PhysicalLaw = "ρ = m/V",
            .PhysicalDomain = "Fluid Dynamics",
            .Description = "Density is mass per unit volume—a fundamental intensive property.",
            .ExampleCalculation = 1000.0 / 1.0 ' 1000 kg/m³ (water)
        }
        Connections.Add(conn2)

        ' Resistance R = V/I
        Dim conn3 As New MathPhysicsConnection With {
            .MathConcept = "Division (/)",
            .MathCategory = "Arithmetic",
            .MathFormula = "R = V / I",
            .PhysicalPrinciple = "Ohm's Law (Resistance Definition)",
            .PhysicalLaw = "R = V/I",
            .PhysicalDomain = "Electromagnetism",
            .Description = "Electrical resistance is voltage divided by current.",
            .ExampleCalculation = 12.0 / 2.0 ' 6 Ω
        }
        Connections.Add(conn3)

        ' Refractive index n = c/v
        Dim conn4 As New MathPhysicsConnection With {
            .MathConcept = "Division (/)",
            .MathCategory = "Arithmetic",
            .MathFormula = "n = c / v",
            .PhysicalPrinciple = "Index of Refraction",
            .PhysicalLaw = "n = c/v",
            .PhysicalDomain = "Optics",
            .Description = "Refractive index is the ratio of light speed in vacuum to that in medium.",
            .ExampleCalculation = C_LIGHT / (C_LIGHT / 1.5) ' 1.5 (typical glass)
        }
        Connections.Add(conn4)

        ' Efficiency η = W_out/W_in
        Dim conn5 As New MathPhysicsConnection With {
            .MathConcept = "Division (/)",
            .MathCategory = "Arithmetic",
            .MathFormula = "η = W_out / W_in",
            .PhysicalPrinciple = "Thermal Efficiency",
            .PhysicalLaw = "η = 1 - T_c/T_h",
            .PhysicalDomain = "Thermodynamics",
            .Description = "Efficiency is useful output divided by total input.",
            .ExampleCalculation = 400.0 / 500.0 ' 0.8 or 80%
        }
        Connections.Add(conn5)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 5. EXPONENTIATION → SQUARE LAWS
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_Exponentiation()
        ' Inverse square law
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Exponentiation (x^n)",
            .MathCategory = "Algebra",
            .MathFormula = "F ∝ 1/r², I ∝ 1/r²",
            .PhysicalPrinciple = "Inverse Square Law",
            .PhysicalLaw = "F_gravity ∝ 1/r², F_electric ∝ 1/r², I_light ∝ 1/r²",
            .PhysicalDomain = "Multiple (Gravity, EM, Optics)",
            .Description = "Gravity, electric force, and light intensity all follow inverse square law.",
            .ExampleCalculation = 1.0 / (2.0 * 2.0) ' 0.25 (at double distance)
        }
        Connections.Add(conn)

        ' Kinetic energy ∝ v²
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Exponentiation (x^n)",
            .MathCategory = "Algebra",
            .MathFormula = "KE = ½mv²",
            .PhysicalPrinciple = "Kinetic Energy (Velocity Squared)",
            .PhysicalLaw = "KE ∝ v²",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Kinetic energy scales with the square of velocity.",
            .ExampleCalculation = 20.0 * 20.0 ' v² contribution
        }
        Connections.Add(conn2)

        ' Stefan-Boltzmann T⁴
        Dim conn3 As New MathPhysicsConnection With {
            .MathConcept = "Exponentiation (x^n)",
            .MathCategory = "Algebra",
            .MathFormula = "P = εσAT⁴",
            .PhysicalPrinciple = "Stefan-Boltzmann Law (Radiation)",
            .PhysicalLaw = "P ∝ T⁴",
            .PhysicalDomain = "Thermodynamics",
            .Description = "Radiative power scales with the fourth power of absolute temperature.",
            .ExampleCalculation = Math.Pow(300.0, 4) ' T⁴ at 300K
        }
        Connections.Add(conn3)

        ' Einstein's E = mc²
        Dim conn4 As New MathPhysicsConnection With {
            .MathConcept = "Exponentiation (x^n)",
            .MathCategory = "Algebra",
            .MathFormula = "E = mc²",
            .PhysicalPrinciple = "Mass-Energy Equivalence",
            .PhysicalLaw = "E = m·c²",
            .PhysicalDomain = "Relativity",
            .Description = "Energy is proportional to mass times the square of light speed.",
            .ExampleCalculation = C_LIGHT * C_LIGHT ' c² ≈ 8.988E16
        }
        Connections.Add(conn4)

        ' Power in circuits P = I²R
        Dim conn5 As New MathPhysicsConnection With {
            .MathConcept = "Exponentiation (x^n)",
            .MathCategory = "Algebra",
            .MathFormula = "P = I²R",
            .PhysicalPrinciple = "Joule Heating",
            .PhysicalLaw = "P = I²R = V²/R",
            .PhysicalDomain = "Electromagnetism",
            .Description = "Power dissipated in a resistor scales with the square of current.",
            .ExampleCalculation = 2.0 * 2.0 * 10.0 ' 40 W
        }
        Connections.Add(conn5)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 6. SQUARE ROOT → WAVE SPEED, RMS, ESCAPE VELOCITY
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_SquareRoot()
        ' Wave speed on string v = √(T/μ)
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Square Root (√)",
            .MathCategory = "Algebra",
            .MathFormula = "v = √(T/μ)",
            .PhysicalPrinciple = "Wave Speed on a String",
            .PhysicalLaw = "v = √(T/μ)",
            .PhysicalDomain = "Wave Phenomena",
            .Description = "Wave propagation speed depends on the square root of tension divided by linear density.",
            .ExampleCalculation = Math.Sqrt(100.0 / 0.01) ' 100 m/s
        }
        Connections.Add(conn)

        ' RMS velocity v_rms = √(3RT/M)
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Square Root (√)",
            .MathCategory = "Algebra",
            .MathFormula = "v_rms = √(3RT/M)",
            .PhysicalPrinciple = "Root Mean Square Velocity",
            .PhysicalLaw = "v_rms = √(3k_B·T/m)",
            .PhysicalDomain = "Thermodynamics",
            .Description = "RMS speed of gas molecules involves square root of temperature.",
            .ExampleCalculation = Math.Sqrt(3.0 * R_GAS * 300.0 / 0.028) ' ~517 m/s (N₂ at 300K)
        }
        Connections.Add(conn2)

        ' Escape velocity v_esc = √(2GM/r)
        Dim conn3 As New MathPhysicsConnection With {
            .MathConcept = "Square Root (√)",
            .MathCategory = "Algebra",
            .MathFormula = "v_esc = √(2GM/r)",
            .PhysicalPrinciple = "Escape Velocity",
            .PhysicalLaw = "v_esc = √(2GM/R)",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Escape velocity from a planet depends on square root of mass/radius ratio.",
            .ExampleCalculation = Math.Sqrt(2.0 * G * 5.972E24 / 6.371E6) ' ~11,186 m/s (Earth)
        }
        Connections.Add(conn3)

        ' Pendulum period T = 2π√(L/g)
        Dim conn4 As New MathPhysicsConnection With {
            .MathConcept = "Square Root (√)",
            .MathCategory = "Algebra",
            .MathFormula = "T = 2π√(L/g)",
            .PhysicalPrinciple = "Period of a Simple Pendulum",
            .PhysicalLaw = "T = 2π√(L/g)",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Pendulum period is proportional to square root of length.",
            .ExampleCalculation = 2.0 * Math.PI * Math.Sqrt(1.0 / G_ACC) ' ~2.006 s
        }
        Connections.Add(conn4)

        ' Lorentz factor γ = 1/√(1-v²/c²)
        Dim conn5 As New MathPhysicsConnection With {
            .MathConcept = "Square Root (√)",
            .MathCategory = "Algebra",
            .MathFormula = "γ = 1/√(1 - v²/c²)",
            .PhysicalPrinciple = "Lorentz Factor (Time Dilation)",
            .PhysicalLaw = "γ = 1/√(1-β²)",
            .PhysicalDomain = "Relativity",
            .Description = "Time dilation factor involves square root of relativistic correction.",
            .ExampleCalculation = 1.0 / Math.Sqrt(1.0 - 0.9 * 0.9) ' ~2.294 at 0.9c
        }
        Connections.Add(conn5)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 7. SINE & COSINE → OSCILLATIONS, WAVES
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_Sine_Cosine()
        ' Simple harmonic motion
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Sine/Cosine",
            .MathCategory = "Trigonometry",
            .MathFormula = "x(t) = A·cos(ωt + φ)",
            .PhysicalPrinciple = "Simple Harmonic Motion",
            .PhysicalLaw = "x(t) = A·cos(ωt + φ)",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "The position of an oscillating mass on a spring follows cosine function.",
            .ExampleCalculation = Math.Cos(2.0 * Math.PI * 1.0) ' 1.0 (one complete cycle)
        }
        Connections.Add(conn)

        ' Projectile motion
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Sine/Cosine",
            .MathCategory = "Trigonometry",
            .MathFormula = "x = v₀cos(θ)·t, y = v₀sin(θ)·t - ½gt²",
            .PhysicalPrinciple = "Projectile Motion",
            .PhysicalLaw = "Range = v₀²sin(2θ)/g",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Projectile trajectory decomposition uses sine and cosine components.",
            .ExampleCalculation = 20.0 * Math.Sin(Math.PI / 4) ' ~14.14 m/s vertical component
        }
        Connections.Add(conn2)

        ' AC voltage V(t) = V₀sin(ωt)
        Dim conn3 As New MathPhysicsConnection With {
            .MathConcept = "Sine/Cosine",
            .MathCategory = "Trigonometry",
            .MathFormula = "V(t) = V_peak·sin(ωt)",
            .PhysicalPrinciple = "Alternating Current (AC)",
            .PhysicalLaw = "V(t) = V₀·sin(2πft)",
            .PhysicalDomain = "Electromagnetism",
            .Description = "AC voltage oscillates sinusoidally with time.",
            .ExampleCalculation = 170.0 * Math.Sin(2.0 * Math.PI * 60.0 * 0.00417) ' ~170V at peak
        }
        Connections.Add(conn3)

        ' Wave function y(x,t) = A·sin(kx - ωt)
        Dim conn4 As New MathPhysicsConnection With {
            .MathConcept = "Sine/Cosine",
            .MathCategory = "Trigonometry",
            .MathFormula = "y(x,t) = A·sin(kx - ωt)",
            .PhysicalPrinciple = "Traveling Wave",
            .PhysicalLaw = "y(x,t) = A·sin(2π(x/λ - ft))",
            .PhysicalDomain = "Wave Phenomena",
            .Description = "All wave phenomena (sound, light, water) are described by sinusoidal functions.",
            .ExampleCalculation = Math.Sin(2.0 * Math.PI * 0.5) ' 0.0
        }
        Connections.Add(conn4)

        ' Snell's Law involves sine
        Dim conn5 As New MathPhysicsConnection With {
            .MathConcept = "Sine/Cosine",
            .MathCategory = "Trigonometry",
            .MathFormula = "n₁·sin(θ₁) = n₂·sin(θ₂)",
            .PhysicalPrinciple = "Snell's Law of Refraction",
            .PhysicalLaw = "sin(θ₂) = (n₁/n₂)·sin(θ₁)",
            .PhysicalDomain = "Optics",
            .Description = "Refraction angle is determined by ratio of sines.",
            .ExampleCalculation = Math.Asin(1.0 * Math.Sin(Math.PI / 6) / 1.5) ' ~19.47°
        }
        Connections.Add(conn5)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 8. TANGENT → INCLINED PLANES, BREWSTER ANGLE
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_Tangent()
        ' Inclined plane
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Tangent (tan)",
            .MathCategory = "Trigonometry",
            .MathFormula = "F_parallel = mg·sin(θ)",
            .PhysicalPrinciple = "Inclined Plane Dynamics",
            .PhysicalLaw = "a = g·sin(θ)",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Component of gravity along incline uses sine; normal force uses cosine.",
            .ExampleCalculation = G_ACC * Math.Sin(Math.PI / 6) ' ~4.9 m/s² (30° incline)
        }
        Connections.Add(conn)

        ' Brewster angle
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Tangent (tan)",
            .MathCategory = "Trigonometry",
            .MathFormula = "θ_B = arctan(n₂/n₁)",
            .PhysicalPrinciple = "Brewster's Angle (Polarization)",
            .PhysicalLaw = "tan(θ_B) = n₂/n₁",
            .PhysicalDomain = "Optics",
            .Description = "Brewster angle where reflected light is fully polarized involves tangent.",
            .ExampleCalculation = Math.Atan(1.5 / 1.0) ' ~56.31° for glass
        }
        Connections.Add(conn2)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 9. INVERSE TRIG → ANGLE CALCULATION
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_InverseTrig()
        ' Critical angle
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Inverse Sine (arcsin)",
            .MathCategory = "Trigonometry",
            .MathFormula = "θ_c = arcsin(n₂/n₁)",
            .PhysicalPrinciple = "Critical Angle (Total Internal Reflection)",
            .PhysicalLaw = "θ_c = arcsin(n₂/n₁)",
            .PhysicalDomain = "Optics",
            .Description = "Critical angle for total internal reflection uses inverse sine.",
            .ExampleCalculation = Math.Asin(1.0 / 1.5) ' ~41.81° (glass to air)
        }
        Connections.Add(conn)

        ' Vector direction
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Inverse Tangent (arctan)",
            .MathCategory = "Trigonometry",
            .MathFormula = "θ = arctan(y/x)",
            .PhysicalPrinciple = "Vector Direction",
            .PhysicalLaw = "θ = arctan(F_y/F_x)",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Direction of a resultant force uses inverse tangent of components.",
            .ExampleCalculation = Math.Atan2(3.0, 4.0) * 180 / Math.PI ' ~36.87°
        }
        Connections.Add(conn2)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 10. LOGARITHMS → SOUND, ENTROPY, DECAY
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_Logarithms()
        ' Sound level (decibels)
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Logarithm (log10)",
            .MathCategory = "Logarithms",
            .MathFormula = "β = 10·log₁₀(I/I₀)",
            .PhysicalPrinciple = "Sound Intensity Level (Decibels)",
            .PhysicalLaw = "β(dB) = 10·log₁₀(I/10⁻¹²)",
            .PhysicalDomain = "Wave Phenomena",
            .Description = "Human hearing perception is logarithmic, measured in decibels.",
            .ExampleCalculation = 10.0 * Math.Log10(1E-6 / 1E-12) ' 60 dB
        }
        Connections.Add(conn)

        ' Boltzmann entropy S = k·ln(W)
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Logarithm (ln)",
            .MathCategory = "Logarithms",
            .MathFormula = "S = k_B·ln(W)",
            .PhysicalPrinciple = "Statistical Entropy",
            .PhysicalLaw = "S = k_B·ln(Ω)",
            .PhysicalDomain = "Thermodynamics",
            .Description = "Entropy is proportional to the natural logarithm of microstates.",
            .ExampleCalculation = K_BOLTZ * Math.Log(1E23) ' ~7.31E-23 J/K
        }
        Connections.Add(conn2)

        ' Radioactive decay N = N₀·e^(-λt)
        Dim conn3 As New MathPhysicsConnection With {
            .MathConcept = "Logarithm (ln)",
            .MathCategory = "Logarithms",
            .MathFormula = "t = ln(N₀/N)/λ",
            .PhysicalPrinciple = "Radioactive Decay (Half-life)",
            .PhysicalLaw = "t_half = ln(2)/λ",
            .PhysicalDomain = "Nuclear Physics",
            .Description = "Decay time calculations require natural logarithms.",
            .ExampleCalculation = Math.Log(2) / 0.693 ' ~1.0 (half-life calculation)
        }
        Connections.Add(conn3)

        ' pH scale pH = -log₁₀[H⁺]
        Dim conn4 As New MathPhysicsConnection With {
            .MathConcept = "Logarithm (log10)",
            .MathCategory = "Logarithms",
            .MathFormula = "pH = -log₁₀[H⁺]",
            .PhysicalPrinciple = "Acidity (pH Scale)",
            .PhysicalLaw = "pH = -log₁₀[H⁺]",
            .PhysicalDomain = "Chemistry/Physics",
            .Description = "pH is the negative logarithm of hydrogen ion concentration.",
            .ExampleCalculation = -Math.Log10(1E-7) ' 7.0 (neutral)
        }
        Connections.Add(conn4)

        ' Richter scale M = log₁₀(A/A₀)
        Dim conn5 As New MathPhysicsConnection With {
            .MathConcept = "Logarithm (log10)",
            .MathCategory = "Logarithms",
            .MathFormula = "M = log₁₀(A/A₀)",
            .PhysicalPrinciple = "Earthquake Magnitude (Richter Scale)",
            .PhysicalLaw = "M_L = log₁₀(A) - log₁₀(A₀)",
            .PhysicalDomain = "Geophysics",
            .Description = "Earthquake magnitude is logarithmic—each unit is 10x amplitude.",
            .ExampleCalculation = Math.Log10(1E4 / 1.0) ' 4.0 magnitude
        }
        Connections.Add(conn5)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 11. DIFFERENTIAL → VELOCITY, ACCELERATION
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_Differential()
        ' Velocity as derivative
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Differentiation (d/dt)",
            .MathCategory = "Calculus",
            .MathFormula = "v = dx/dt",
            .PhysicalPrinciple = "Instantaneous Velocity",
            .PhysicalLaw = "v = lim(Δt→0) Δx/Δt = dx/dt",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Velocity is the first time derivative of position.",
            .ExampleCalculation = 10.0 ' Constant velocity: dx/dt = v
        }
        Connections.Add(conn)

        ' Acceleration
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Differentiation (d²/dt²)",
            .MathCategory = "Calculus",
            .MathFormula = "a = dv/dt = d²x/dt²",
            .PhysicalPrinciple = "Acceleration",
            .PhysicalLaw = "a = dv/dt = d²x/dt²",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Acceleration is the second derivative of position.",
            .ExampleCalculation = G_ACC ' Constant acceleration: d²x/dt² = g
        }
        Connections.Add(conn2)

        ' Faraday's Law ε = -dΦ/dt
        Dim conn3 As New MathPhysicsConnection With {
            .MathConcept = "Differentiation (d/dt)",
            .MathCategory = "Calculus",
            .MathFormula = "ε = -dΦ_B/dt",
            .PhysicalPrinciple = "Faraday's Law of Induction",
            .PhysicalLaw = "ε = -dΦ_B/dt",
            .PhysicalDomain = "Electromagnetism",
            .Description = "Induced EMF is the negative time derivative of magnetic flux.",
            .ExampleCalculation = -(0.01 - 0.0) / 0.1 ' 0.1 V (flux change 0.01 Wb in 0.1s)
        }
        Connections.Add(conn3)

        ' Force from potential F = -dU/dx
        Dim conn4 As New MathPhysicsConnection With {
            .MathConcept = "Differentiation (d/dx)",
            .MathCategory = "Calculus",
            .MathFormula = "F = -dU/dx",
            .PhysicalPrinciple = "Force from Potential Energy",
            .PhysicalLaw = "F = -∇U",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Conservative force is the negative gradient of potential energy.",
            .ExampleCalculation = -(0.0 - 100.0) / 2.0 ' 50 N (spring force)
        }
        Connections.Add(conn4)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 12. INTEGRAL → WORK, IMPULSE, FLUX
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_Integral()
        ' Work as integral of force
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Integration (∫)",
            .MathCategory = "Calculus",
            .MathFormula = "W = ∫F·dx",
            .PhysicalPrinciple = "Work-Energy Theorem",
            .PhysicalLaw = "W = ∫F(x)·dx",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Total work is the integral of force over displacement.",
            .ExampleCalculation = 100.0 * 5.0 ' 500 J (constant force)
        }
        Connections.Add(conn)

        ' Impulse J = ∫F·dt
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Integration (∫)",
            .MathCategory = "Calculus",
            .MathFormula = "J = ∫F·dt = Δp",
            .PhysicalPrinciple = "Impulse-Momentum Theorem",
            .PhysicalLaw = "J = Δp = ∫F·dt",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Impulse is the time integral of force, equal to change in momentum.",
            .ExampleCalculation = 50.0 * 0.1 ' 5 N·s
        }
        Connections.Add(conn2)

        ' Gauss's Law ∮E·dA = Q/ε₀
        Dim conn3 As New MathPhysicsConnection With {
            .MathConcept = "Integration (∮)",
            .MathCategory = "Calculus",
            .MathFormula = "Φ_E = ∮E·dA",
            .PhysicalPrinciple = "Gauss's Law (Electric Flux)",
            .PhysicalLaw = "∮E·dA = Q_enclosed/ε₀",
            .PhysicalDomain = "Electromagnetism",
            .Description = "Total electric flux through a closed surface is the surface integral of E.",
            .ExampleCalculation = E_CHARGE / EPSILON_0 ' Flux from one electron
        }
        Connections.Add(conn3)

        ' Ampère's Law ∮B·dl = μ₀I_enc
        Dim conn4 As New MathPhysicsConnection With {
            .MathConcept = "Integration (∮)",
            .MathCategory = "Calculus",
            .MathFormula = "∮B·dl = μ₀I_enc",
            .PhysicalPrinciple = "Ampère's Law (Magnetic Circulation)",
            .PhysicalLaw = "∮B·dl = μ₀·I_enclosed",
            .PhysicalDomain = "Electromagnetism",
            .Description = "Line integral of magnetic field around a closed loop gives enclosed current.",
            .ExampleCalculation = MU_0 * 1.0 ' 1.257E-6 T·m
        }
        Connections.Add(conn4)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 13. VECTOR OPERATIONS → FORCE COMPOSITION
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_VectorOperations()
        ' Vector addition → Net force
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Vector Addition",
            .MathCategory = "Vector Algebra",
            .MathFormula = "F_net = F₁ + F₂",
            .PhysicalPrinciple = "Superposition of Forces",
            .PhysicalLaw = "ΣF = F₁ + F₂ + ...",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Forces add as vectors—both magnitude and direction matter.",
            .ExampleCalculation = Math.Sqrt(3.0 * 3.0 + 4.0 * 4.0) ' 5 N (3N⊥4N)
        }
        Connections.Add(conn)

        ' Vector components
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Vector Decomposition",
            .MathCategory = "Vector Algebra",
            .MathFormula = "F_x = F·cos(θ), F_y = F·sin(θ)",
            .PhysicalPrinciple = "Resolution of Forces",
            .PhysicalLaw = "Components: F_x = F·cos(θ), F_y = F·sin(θ)",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Any force can be resolved into orthogonal components using trigonometry.",
            .ExampleCalculation = 10.0 * Math.Cos(Math.PI / 3) ' 5.0 N (horizontal component)
        }
        Connections.Add(conn2)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 14. CROSS PRODUCT → TORQUE, MAGNETIC FORCE
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_CrossProduct()
        ' Torque τ = r × F
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Cross Product (×)",
            .MathCategory = "Vector Algebra",
            .MathFormula = "τ = r × F",
            .PhysicalPrinciple = "Torque",
            .PhysicalLaw = "|τ| = r·F·sin(θ)",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Torque is the cross product of position vector and force.",
            .ExampleCalculation = 0.5 * 20.0 * Math.Sin(Math.PI / 2) ' 10 N·m
        }
        Connections.Add(conn)

        ' Magnetic force F = q(v × B)
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Cross Product (×)",
            .MathCategory = "Vector Algebra",
            .MathFormula = "F = q·(v × B)",
            .PhysicalPrinciple = "Lorentz Force (Magnetic)",
            .PhysicalLaw = "F = q·v·B·sin(θ)",
            .PhysicalDomain = "Electromagnetism",
            .Description = "Magnetic force on a moving charge is the cross product of velocity and B-field.",
            .ExampleCalculation = E_CHARGE * 1E6 * 1.0 * Math.Sin(Math.PI / 2) ' 1.602E-13 N
        }
        Connections.Add(conn2)

        ' Angular momentum L = r × p
        Dim conn3 As New MathPhysicsConnection With {
            .MathConcept = "Cross Product (×)",
            .MathCategory = "Vector Algebra",
            .MathFormula = "L = r × p = r × mv",
            .PhysicalPrinciple = "Angular Momentum",
            .PhysicalLaw = "L = r·p·sin(θ)",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Angular momentum is the cross product of position and linear momentum.",
            .ExampleCalculation = 1.0 * (2.0 * 3.0) * Math.Sin(Math.PI / 2) ' 6 kg·m²/s
        }
        Connections.Add(conn3)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 15. DOT PRODUCT → WORK, FLUX
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_DotProduct()
        ' Work W = F·d
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Dot Product (·)",
            .MathCategory = "Vector Algebra",
            .MathFormula = "W = F·d = |F||d|cos(θ)",
            .PhysicalPrinciple = "Mechanical Work",
            .PhysicalLaw = "W = F·d·cos(θ)",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Work is the dot product of force and displacement vectors.",
            .ExampleCalculation = 100.0 * 5.0 * Math.Cos(0) ' 500 J (force parallel to displacement)
        }
        Connections.Add(conn)

        ' Electric flux Φ_E = E·A
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Dot Product (·)",
            .MathCategory = "Vector Algebra",
            .MathFormula = "Φ_E = E·A = EA·cos(θ)",
            .PhysicalPrinciple = "Electric Flux",
            .PhysicalLaw = "Φ_E = E·A·cos(θ)",
            .PhysicalDomain = "Electromagnetism",
            .Description = "Electric flux through a surface is the dot product of E-field and area vector.",
            .ExampleCalculation = 1000.0 * 0.01 * Math.Cos(0) ' 10 V·m
        }
        Connections.Add(conn2)

        ' Power P = F·v
        Dim conn3 As New MathPhysicsConnection With {
            .MathConcept = "Dot Product (·)",
            .MathCategory = "Vector Algebra",
            .MathFormula = "P = F·v",
            .PhysicalPrinciple = "Instantaneous Power",
            .PhysicalLaw = "P = F·v·cos(θ)",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Power delivered by a force is the dot product of force and velocity.",
            .ExampleCalculation = 50.0 * 10.0 * Math.Cos(0) ' 500 W
        }
        Connections.Add(conn3)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 16. PROPORTIONALITY → OHM'S LAW, HOOKE'S LAW
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_Proportionality()
        ' Ohm's Law V ∝ I
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Direct Proportionality (y ∝ x)",
            .MathCategory = "Algebra",
            .MathFormula = "V = I·R (V ∝ I)",
            .PhysicalPrinciple = "Ohm's Law",
            .PhysicalLaw = "V = IR (linear relationship)",
            .PhysicalDomain = "Electromagnetism",
            .Description = "Voltage is directly proportional to current (ohmic materials).",
            .ExampleCalculation = 2.0 * 10.0 ' 20 V
        }
        Connections.Add(conn)

        ' Hooke's Law F ∝ x
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Direct Proportionality (y ∝ x)",
            .MathCategory = "Algebra",
            .MathFormula = "F = -k·x",
            .PhysicalPrinciple = "Hooke's Law (Spring Force)",
            .PhysicalLaw = "F = -k·x (linear elastic)",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Spring force is proportional to displacement from equilibrium.",
            .ExampleCalculation = 100.0 * 0.05 ' 5 N (spring stretched 5 cm)
        }
        Connections.Add(conn2)

        ' Newton's Second Law F ∝ a
        Dim conn3 As New MathPhysicsConnection With {
            .MathConcept = "Direct Proportionality (y ∝ x)",
            .MathCategory = "Algebra",
            .MathFormula = "F = m·a (F ∝ a)",
            .PhysicalPrinciple = "Newton's Second Law",
            .PhysicalLaw = "a = F/m",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Acceleration is directly proportional to net force.",
            .ExampleCalculation = 5.0 / 2.0 ' 2.5 m/s² per Newton
        }
        Connections.Add(conn3)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 17. INVERSE PROPORTION → BOYLE'S LAW
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_InverseProportion()
        ' Boyle's Law P ∝ 1/V
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Inverse Proportionality (y ∝ 1/x)",
            .MathCategory = "Algebra",
            .MathFormula = "P₁V₁ = P₂V₂",
            .PhysicalPrinciple = "Boyle's Law (Isothermal Process)",
            .PhysicalLaw = "PV = constant (at constant T)",
            .PhysicalDomain = "Thermodynamics",
            .Description = "Pressure is inversely proportional to volume at constant temperature.",
            .ExampleCalculation = 100000.0 * 0.002 / 0.004 ' 50,000 Pa (doubling volume)
        }
        Connections.Add(conn)

        ' Frequency-period relation
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Inverse Proportionality (y ∝ 1/x)",
            .MathCategory = "Algebra",
            .MathFormula = "f = 1/T",
            .PhysicalPrinciple = "Frequency-Period Relationship",
            .PhysicalLaw = "f = 1/T, T = 1/f",
            .PhysicalDomain = "Wave Phenomena",
            .Description = "Frequency and period are reciprocals of each other.",
            .ExampleCalculation = 1.0 / 0.02 ' 50 Hz
        }
        Connections.Add(conn2)

        ' Wavelength-frequency relation λ = c/f
        Dim conn3 As New MathPhysicsConnection With {
            .MathConcept = "Inverse Proportionality (y ∝ 1/x)",
            .MathCategory = "Algebra",
            .MathFormula = "λ = c/f",
            .PhysicalPrinciple = "Wave Equation",
            .PhysicalLaw = "c = λf, so λ ∝ 1/f",
            .PhysicalDomain = "Electromagnetism/Optics",
            .Description = "Wavelength is inversely proportional to frequency for constant wave speed.",
            .ExampleCalculation = C_LIGHT / 5E14 ' 600 nm (visible light)
        }
        Connections.Add(conn3)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 18. LINEAR EQUATIONS → KINEMATICS
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_LinearEquations()
        ' v = u + at (y = mx + b form)
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Linear Equation (y = mx + b)",
            .MathCategory = "Algebra",
            .MathFormula = "v = u + a·t",
            .PhysicalPrinciple = "Constant Acceleration Kinematics",
            .PhysicalLaw = "v(t) = v₀ + a·t",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Velocity under constant acceleration is linear in time (y=mx+b).",
            .ExampleCalculation = 0.0 + G_ACC * 3.0 ' 29.42 m/s after 3s free fall
        }
        Connections.Add(conn)

        ' Temperature conversion F = (9/5)C + 32
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Linear Equation (y = mx + b)",
            .MathCategory = "Algebra",
            .MathFormula = "F = (9/5)·C + 32",
            .PhysicalPrinciple = "Temperature Scale Conversion",
            .PhysicalLaw = "T(°F) = 1.8·T(°C) + 32",
            .PhysicalDomain = "Thermodynamics",
            .Description = "Fahrenheit to Celsius conversion is a linear transformation.",
            .ExampleCalculation = 1.8 * 100.0 + 32.0 ' 212 °F (boiling point)
        }
        Connections.Add(conn2)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 19. QUADRATIC → PROJECTILE, FREE FALL
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_QuadraticEquations()
        ' Free fall y = ½gt²
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Quadratic Equation (y = ax²)",
            .MathCategory = "Algebra",
            .MathFormula = "y = ½gt²",
            .PhysicalPrinciple = "Free Fall Under Gravity",
            .PhysicalLaw = "y(t) = y₀ + v₀t - ½gt²",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Distance fallen under gravity is quadratic in time (parabolic).",
            .ExampleCalculation = 0.5 * G_ACC * 2.0 * 2.0 ' ~19.61 m after 2s
        }
        Connections.Add(conn)

        ' Energy in spring ½kx²
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Quadratic Equation (y = ax²)",
            .MathCategory = "Algebra",
            .MathFormula = "U = ½kx²",
            .PhysicalPrinciple = "Elastic Potential Energy",
            .PhysicalLaw = "U_spring = ½k·x²",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Energy stored in a spring is quadratic in displacement.",
            .ExampleCalculation = 0.5 * 200.0 * 0.1 * 0.1 ' 1 J
        }
        Connections.Add(conn2)

        ' Kinetic energy ½mv²
        Dim conn3 As New MathPhysicsConnection With {
            .MathConcept = "Quadratic Equation (y = ax²)",
            .MathCategory = "Algebra",
            .MathFormula = "KE = ½mv²",
            .PhysicalPrinciple = "Kinetic Energy",
            .PhysicalLaw = "KE = ½m·v²",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Kinetic energy depends quadratically on velocity.",
            .ExampleCalculation = 0.5 * 1000.0 * 10.0 * 10.0 ' 50,000 J
        }
        Connections.Add(conn3)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 20. EXPONENTIAL DECAY → RADIOACTIVITY, RC CIRCUITS
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_ExponentialDecay()
        ' Radioactive decay N = N₀e^(-λt)
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Exponential Decay (e^(-λt))",
            .MathCategory = "Exponential Functions",
            .MathFormula = "N(t) = N₀·e^(-λt)",
            .PhysicalPrinciple = "Radioactive Decay",
            .PhysicalLaw = "N = N₀·e^(-λt)",
            .PhysicalDomain = "Nuclear Physics",
            .Description = "Number of radioactive nuclei decays exponentially with time.",
            .ExampleCalculation = 1000.0 * Math.Exp(-0.693 * 2.0) ' 250 after 2 half-lives
        }
        Connections.Add(conn)

        ' RC circuit discharge V = V₀e^(-t/RC)
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Exponential Decay (e^(-t/τ))",
            .MathCategory = "Exponential Functions",
            .MathFormula = "V(t) = V₀·e^(-t/RC)",
            .PhysicalPrinciple = "Capacitor Discharge",
            .PhysicalLaw = "V = V₀·e^(-t/RC)",
            .PhysicalDomain = "Electromagnetism",
            .Description = "Voltage across a discharging capacitor decays exponentially.",
            .ExampleCalculation = 12.0 * Math.Exp(-1.0) ' 4.41 V after 1 time constant
        }
        Connections.Add(conn2)

        ' Beer-Lambert I = I₀e^(-αx)
        Dim conn3 As New MathPhysicsConnection With {
            .MathConcept = "Exponential Decay (e^(-αx))",
            .MathCategory = "Exponential Functions",
            .MathFormula = "I = I₀·e^(-αx)",
            .PhysicalPrinciple = "Beer-Lambert Law (Absorption)",
            .PhysicalLaw = "I(x) = I₀·e^(-αx)",
            .PhysicalDomain = "Optics",
            .Description = "Light intensity decays exponentially through absorbing medium.",
            .ExampleCalculation = 100.0 * Math.Exp(-0.5 * 3.0) ' ~22.3 after 3 absorption lengths
        }
        Connections.Add(conn3)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 21. LOGARITHMIC SCALING → DECIBELS, RICHTER, PH
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_LogarithmicScaling()
        ' Sound level
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Logarithmic Scale",
            .MathCategory = "Logarithms",
            .MathFormula = "β = 10·log₁₀(I/I₀)",
            .PhysicalPrinciple = "Perceived Loudness (Decibel Scale)",
            .PhysicalLaw = "Loudness ∝ log(I)",
            .PhysicalDomain = "Wave Phenomena",
            .Description = "Human perception of sound intensity follows Weber-Fechner logarithmic law.",
            .ExampleCalculation = 10.0 * Math.Log10(1000.0) ' 30 dB
        }
        Connections.Add(conn)

        ' Stellar magnitude
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Logarithmic Scale",
            .MathCategory = "Logarithms",
            .MathFormula = "m₁ - m₂ = -2.5·log₁₀(F₁/F₂)",
            .PhysicalPrinciple = "Apparent Magnitude (Star Brightness)",
            .PhysicalLaw = "Magnitude ∝ -2.5·log(Flux)",
            .PhysicalDomain = "Astronomy",
            .Description = "Stellar brightness magnitude scale is logarithmic (Pogson's ratio).",
            .ExampleCalculation = -2.5 * Math.Log10(100.0) ' -5 magnitude difference
        }
        Connections.Add(conn2)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 22. ABSOLUTE VALUE → DISTANCE, ENERGY MAGNITUDE
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_AbsoluteValue()
        ' Displacement magnitude
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Absolute Value (|x|)",
            .MathCategory = "Algebra",
            .MathFormula = "|Δx| = |x₂ - x₁|",
            .PhysicalPrinciple = "Distance (Path Length)",
            .PhysicalLaw = "Distance = |Δx| (scalar, always positive)",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Distance traveled is the absolute value of displacement (ignoring direction).",
            .ExampleCalculation = Math.Abs(-5.0) ' 5 m distance
        }
        Connections.Add(conn)

        ' Kinetic energy (always positive)
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Absolute Value (squared)",
            .MathCategory = "Algebra",
            .MathFormula = "KE = ½m|v|²",
            .PhysicalPrinciple = "Kinetic Energy (Always Positive)",
            .PhysicalLaw = "KE ≥ 0 (scalar energy)",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "Kinetic energy depends on speed squared (direction irrelevant).",
            .ExampleCalculation = 0.5 * 2.0 * (-3.0) * (-3.0) ' 9 J (negative velocity same KE)
        }
        Connections.Add(conn2)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 23. TRIG IDENTITIES → WAVE INTERFERENCE
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_TrigonometricIdentities()
        ' sin²θ + cos²θ = 1 → Energy conservation
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Trigonometric Identity (sin²θ + cos²θ = 1)",
            .MathCategory = "Trigonometry",
            .MathFormula = "sin²θ + cos²θ = 1",
            .PhysicalPrinciple = "Energy Conservation in Projectile Motion",
            .PhysicalLaw = "(v_x)² + (v_y)² = v² (constant horizontal + vertical)",
            .PhysicalDomain = "Classical Mechanics",
            .Description = "The identity sin²+cos²=1 corresponds to conservation of total velocity magnitude.",
            .ExampleCalculation = Math.Sin(Math.PI / 4) * Math.Sin(Math.PI / 4) +
                                 Math.Cos(Math.PI / 4) * Math.Cos(Math.PI / 4) ' 1.0
        }
        Connections.Add(conn)

        ' Superposition of waves sin A + sin B = 2sin((A+B)/2)cos((A-B)/2)
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Sum-to-Product Identity",
            .MathCategory = "Trigonometry",
            .MathFormula = "sin A + sin B = 2sin((A+B)/2)cos((A-B)/2)",
            .PhysicalPrinciple = "Wave Interference (Beats)",
            .PhysicalLaw = "y_total = y₁ + y₂",
            .PhysicalDomain = "Wave Phenomena",
            .Description = "Trigonometric sum-to-product formulas describe beat patterns in wave interference.",
            .ExampleCalculation = Math.Sin(10.0) + Math.Sin(12.0) ' Beat pattern
        }
        Connections.Add(conn2)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 24. HYPERBOLIC → SPECIAL RELATIVITY
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_Hyperbolic()
        ' Lorentz transformation uses hyperbolic functions
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Hyperbolic Functions (sinh, cosh)",
            .MathCategory = "Advanced Functions",
            .MathFormula = "x' = x·cosh(φ) - ct·sinh(φ)",
            .PhysicalPrinciple = "Lorentz Transformation (Rapidity)",
            .PhysicalLaw = "Rapidity φ = artanh(v/c)",
            .PhysicalDomain = "Relativity",
            .Description = "Lorentz boosts are hyperbolic rotations in spacetime.",
            .ExampleCalculation = Math.Tanh(0.5) ' rapidity example
        }
        Connections.Add(conn)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 25. COMPLEX NUMBERS → AC CIRCUITS
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_ComplexNumbers()
        ' Impedance Z = R + jX
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Complex Numbers (a + bi)",
            .MathCategory = "Complex Analysis",
            .MathFormula = "Z = R + j(ωL - 1/ωC)",
            .PhysicalPrinciple = "Electrical Impedance (AC Circuits)",
            .PhysicalLaw = "V = I·Z (phasor domain)",
            .PhysicalDomain = "Electromagnetism",
            .Description = "AC circuit analysis uses complex numbers for phase relationships.",
            .ExampleCalculation = Math.Sqrt(10.0 * 10.0 + 5.0 * 5.0) ' |Z| = 11.18 Ω
        }
        Connections.Add(conn)

        ' Quantum wavefunction ψ = A·e^(i(kx-ωt))
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Complex Exponential (e^(iθ))",
            .MathCategory = "Complex Analysis",
            .MathFormula = "ψ = A·e^(i(kx-ωt))",
            .PhysicalPrinciple = "Quantum Wavefunction",
            .PhysicalLaw = "|ψ|² = probability density",
            .PhysicalDomain = "Quantum Mechanics",
            .Description = "Quantum states are described by complex-valued wavefunctions.",
            .ExampleCalculation = Math.Cos(2.0 * Math.PI * 0.5) ' Real part of e^(iπ) = -1
        }
        Connections.Add(conn2)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 26. PROBABILITY → QUANTUM MECHANICS
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_Probability()
        ' Born rule P = |ψ|²
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Probability",
            .MathCategory = "Statistics/Probability",
            .MathFormula = "P(x) = |ψ(x)|²",
            .PhysicalPrinciple = "Born Rule (Quantum Measurement)",
            .PhysicalLaw = "Probability = |wavefunction|²",
            .PhysicalDomain = "Quantum Mechanics",
            .Description = "The probability of finding a particle is the square of the wavefunction amplitude.",
            .ExampleCalculation = 0.5 * 0.5 ' 0.25 = 25% probability
        }
        Connections.Add(conn)

        ' Boltzmann distribution
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Probability Distribution",
            .MathCategory = "Statistics/Probability",
            .MathFormula = "P(E) ∝ e^(-E/kT)",
            .PhysicalPrinciple = "Boltzmann Distribution",
            .PhysicalLaw = "P_i = e^(-E_i/kT) / Z",
            .PhysicalDomain = "Statistical Mechanics",
            .Description = "Probability of energy states follows exponential Boltzmann distribution.",
            .ExampleCalculation = Math.Exp(-1.0 / (K_BOLTZ * 300)) ' Probability ratio
        }
        Connections.Add(conn2)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' 27. STATISTICS → THERMODYNAMICS
    ' ═══════════════════════════════════════════════════════════
    Private Sub Bridge_Statistics()
        ' RMS velocity
        Dim conn As New MathPhysicsConnection With {
            .MathConcept = "Root Mean Square (RMS)",
            .MathCategory = "Statistics",
            .MathFormula = "v_rms = √(⟨v²⟩)",
            .PhysicalPrinciple = "Kinetic Theory of Gases",
            .PhysicalLaw = "v_rms = √(3kT/m)",
            .PhysicalDomain = "Thermodynamics",
            .Description = "RMS speed emerges from statistical averaging of molecular velocities.",
            .ExampleCalculation = Math.Sqrt(3.0 * K_BOLTZ * 300.0 / M_ELECTRON) ' electron thermal speed
        }
        Connections.Add(conn)

        ' Expectation value
        Dim conn2 As New MathPhysicsConnection With {
            .MathConcept = "Expected Value (⟨x⟩)",
            .MathCategory = "Statistics",
            .MathFormula = "⟨x⟩ = ∫x·|ψ|² dx",
            .PhysicalPrinciple = "Quantum Expectation Value",
            .PhysicalLaw = "⟨A⟩ = ⟨ψ|Â|ψ⟩",
            .PhysicalDomain = "Quantum Mechanics",
            .Description = "Quantum expectation values are statistical averages of measurements.",
            .ExampleCalculation = 0.5 * 1.0 + 0.5 * (-1.0) ' 0 (symmetric distribution)
        }
        Connections.Add(conn2)
    End Sub

End Class