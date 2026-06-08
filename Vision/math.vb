'===============================================================
' VB.NET Complete Math Functions Illustration
' Demonstrates all System.Math methods, MathF equivalents,
' constants, and VB-specific numeric helpers.
'===============================================================

Imports System.Math

Module MathFunctionsDemo

    Sub Main()
        Console.Title = "VB.NET Math Functions"
        Console.WriteLine("═══════════════════════════════════════════════════════════════")
        Console.WriteLine("                VB.NET MATHEMATICAL FUNCTIONS                ")
        Console.WriteLine("═══════════════════════════════════════════════════════════════")

        ShowConstants()
        ShowTrigonometric()
        ShowHyperbolic()
        ShowInverseTrigonometric()
        ShowExponentialAndLog()
        ShowRoundingAndTruncation()
        ShowAbsoluteAndSign()
        ShowMinMax()
        ShowDivisionAndRemainder()
        ShowMiscellaneous()
        ShowRandomNumbers()
        ShowVBSpecific()

        Console.WriteLine(vbCrLf & "Press any key to exit...")
        Console.ReadKey()
    End Sub

    ' ─── Constants ────────────────────────────────────────────
    Sub ShowConstants()
        Console.WriteLine(vbCrLf & "── Constants ──")
        Console.WriteLine($"Math.PI  = {Math.PI}")
        Console.WriteLine($"Math.E   = {Math.E}")
#If NETCOREAPP3_0_OR_GREATER Then
        Console.WriteLine($"Math.Tau = {Math.Tau}")   ' 2 * PI, available from .NET Core 3.0
#End If
    End Sub

    ' ─── Trigonometric Functions ──────────────────────────────
    Sub ShowTrigonometric()
        Dim angleDeg As Double = 30.0
        Dim angleRad As Double = angleDeg * Math.PI / 180.0

        Console.WriteLine(vbCrLf & "── Trigonometric (angle = 30°) ──")
        Console.WriteLine($"Sin({angleDeg:F1}°) = {Math.Sin(angleRad):F6}")
        Console.WriteLine($"Cos({angleDeg:F1}°) = {Math.Cos(angleRad):F6}")
        Console.WriteLine($"Tan({angleDeg:F1}°) = {Math.Tan(angleRad):F6}")

        ' Single-precision equivalents (MathF)
        Console.WriteLine($"MathF.Sin({angleDeg:F1}°) = {MathF.Sin(CSng(angleRad)):F6}")
        Console.WriteLine($"MathF.Cos({angleDeg:F1}°) = {MathF.Cos(CSng(angleRad)):F6}")
        Console.WriteLine($"MathF.Tan({angleDeg:F1}°) = {MathF.Tan(CSng(angleRad)):F6}")
    End Sub

    ' ─── Hyperbolic Functions ─────────────────────────────────
    Sub ShowHyperbolic()
        Dim x As Double = 1.0
        Console.WriteLine(vbCrLf & "── Hyperbolic (x = 1) ──")
        Console.WriteLine($"Sinh({x}) = {Math.Sinh(x):F6}")
        Console.WriteLine($"Cosh({x}) = {Math.Cosh(x):F6}")
        Console.WriteLine($"Tanh({x}) = {Math.Tanh(x):F6}")

        Console.WriteLine($"MathF.Sinh({x}) = {MathF.Sinh(CSng(x)):F6}")
        Console.WriteLine($"MathF.Cosh({x}) = {MathF.Cosh(CSng(x)):F6}")
        Console.WriteLine($"MathF.Tanh({x}) = {MathF.Tanh(CSng(x)):F6}")
    End Sub

    ' ─── Inverse Trigonometric Functions ──────────────────────
    Sub ShowInverseTrigonometric()
        Dim value As Double = 0.5
        Console.WriteLine(vbCrLf & "── Inverse Trigonometric (value = 0.5) ──")
        Console.WriteLine($"Asin(0.5) = {Math.Asin(value):F6} rad ({Math.Asin(value) * 180 / Math.PI:F1}°)")
        Console.WriteLine($"Acos(0.5) = {Math.Acos(value):F6} rad ({Math.Acos(value) * 180 / Math.PI:F1}°)")
        Console.WriteLine($"Atan(0.5) = {Math.Atan(value):F6} rad ({Math.Atan(value) * 180 / Math.PI:F1}°)")

        ' Atan2(y, x) - returns angle whose tangent is y/x
        Dim y As Double = 1.0, x As Double = 1.0
        Console.WriteLine($"Atan2(y={y}, x={x}) = {Math.Atan2(y, x):F6} rad ({Math.Atan2(y, x) * 180 / Math.PI:F1}°)")
    End Sub

    ' ─── Exponential and Logarithmic Functions ────────────────
    Sub ShowExponentialAndLog()
        Dim val As Double = 2.0
        Console.WriteLine(vbCrLf & "── Exponential & Logarithms (base e / 10 / 2) ──")
        Console.WriteLine($"Exp({val}) = {Math.Exp(val):F6}")       ' e^2
        Console.WriteLine($"Pow(2, 3) = {Math.Pow(2, 3)}")         ' 2^3
        Console.WriteLine($"Sqrt(16) = {Math.Sqrt(16)}")           ' √16

        Console.WriteLine($"Log(e²) = {Math.Log(Math.Exp(2)):F6}") ' natural log
        Console.WriteLine($"Log10(1000) = {Math.Log10(1000)}")     ' log base 10
#If NETCOREAPP3_0_OR_GREATER Then
        Console.WriteLine($"Log2(8) = {Math.Log2(8)}")             ' log base 2 (Core 3.0+)
#End If

        ' MathF versions
        Console.WriteLine($"MathF.Exp({val}) = {MathF.Exp(CSng(val)):F6}")
        Console.WriteLine($"MathF.Pow(2, 3) = {MathF.Pow(2, 3)}")
        Console.WriteLine($"MathF.Sqrt(16) = {MathF.Sqrt(16)}")
    End Sub

    ' ─── Rounding and Truncation Functions ────────────────────
    Sub ShowRoundingAndTruncation()
        Dim numbers() As Double = {3.4, 3.5, 3.6, -3.4, -3.5, -3.6}
        Console.WriteLine(vbCrLf & "── Rounding & Truncation ──")
        Console.WriteLine("Value      Ceiling   Floor     Truncate  Round(Midpoint.ToEven)  Round(Midpoint.AwayFromZero)")
        For Each n In numbers
            Console.WriteLine($"{n,6:F1}    {Math.Ceiling(n),8:F0}    {Math.Floor(n),8:F0}    {Math.Truncate(n),8:F0}    {Math.Round(n, MidpointRounding.ToEven),-22:F0}  {Math.Round(n, MidpointRounding.AwayFromZero),8:F0}")
        Next

        ' VB-specific Int and Fix
        Console.WriteLine(vbCrLf & "VB-specific rounding:")
        Console.WriteLine($"Int(3.7) = {Int(3.7)}    ' Returns 3 (floor for positive, but floor for negative as well: Int(-3.7) = {Int(-3.7)})")
        Console.WriteLine($"Fix(3.7) = {Fix(3.7)}    ' Truncates toward zero (Fix(-3.7) = {Fix(-3.7)})")
    End Sub

    ' ─── Absolute Value and Sign ──────────────────────────────
    Sub ShowAbsoluteAndSign()
        Dim values() As Double = {-5, 0, 3.14}
        Console.WriteLine(vbCrLf & "── Abs & Sign ──")
        For Each v In values
            Console.WriteLine($"Abs({v}) = {Math.Abs(v),5},  Sign({v}) = {Math.Sign(v)}")
        Next

        ' CopySign (returns first argument with sign of second) - .NET Core 3.0+
#If NETCOREAPP3_0_OR_GREATER Then
        Console.WriteLine($"CopySign(10, -1) = {Math.CopySign(10, -1)}")
#End If
    End Sub

    ' ─── Minimum and Maximum ──────────────────────────────────
    Sub ShowMinMax()
        Dim a As Double = 2.5, b As Double = 3.7
        Console.WriteLine(vbCrLf & "── Min & Max ──")
        Console.WriteLine($"Min({a}, {b}) = {Math.Min(a, b)}")
        Console.WriteLine($"Max({a}, {b}) = {Math.Max(a, b)}")

        ' MinMagnitude / MaxMagnitude (compares absolute values) - .NET Core 3.0+
#If NETCOREAPP3_0_OR_GREATER Then
        Console.WriteLine($"MinMagnitude(-2.5, 3.7) = {Math.MinMagnitude(-2.5, 3.7)}")
        Console.WriteLine($"MaxMagnitude(-2.5, 3.7) = {Math.MaxMagnitude(-2.5, 3.7)}")
#End If
    End Sub

    ' ─── Division and Remainder ───────────────────────────────
    Sub ShowDivisionAndRemainder()
        Dim dividend As Integer = 17, divisor As Integer = 5
        Console.WriteLine(vbCrLf & "── Division & Remainder ──")

        ' DivRem (quotient and remainder)
        Dim remainder As Integer
        Dim quotient As Integer = Math.DivRem(dividend, divisor, remainder)
        Console.WriteLine($"DivRem({dividend}, {divisor}) -> quotient = {quotient}, remainder = {remainder}")

        ' IEEERemainder (remainder per IEEE 754)
        Dim ieee As Double = Math.IEEERemainder(17.0, 5.0)
        Console.WriteLine($"IEEERemainder(17.0, 5.0) = {ieee}")

        ' VB Mod operator
        Console.WriteLine($"17 Mod 5 = {17 Mod 5}")
    End Sub

    ' ─── Miscellaneous Math Functions ─────────────────────────
    Sub ShowMiscellaneous()
        Console.WriteLine(vbCrLf & "── Miscellaneous ──")

        ' BigMul (produces full 64-bit product of two 32-bit integers)
        Dim lo As Integer = Integer.MaxValue, hi As Integer = 2
        Dim product As Long = Math.BigMul(lo, hi)
        Console.WriteLine($"BigMul(Int32.MaxValue, 2) = {product}")

        ' Clamp (restricts value to a range) - .NET Core 2.0+
#If NETCOREAPP2_0_OR_GREATER Then
        Console.WriteLine($"Clamp(10, 1, 5) = {Math.Clamp(10, 1, 5)}")
        Console.WriteLine($"Clamp(-2, 1, 5) = {Math.Clamp(-2, 1, 5)}")
#End If

        ' FusedMultiplyAdd (a*b + c with one rounding) - .NET Core 3.0+
#If NETCOREAPP3_0_OR_GREATER Then
        Console.WriteLine($"FusedMultiplyAdd(2, 3, 4) = {Math.FusedMultiplyAdd(2.0, 3.0, 4.0)}")
#End If

        ' ScaleB (x * 2^n efficiently) - .NET Core 3.0+
#If NETCOREAPP3_0_OR_GREATER Then
        Console.WriteLine($"ScaleB(3.0, 4) = {Math.ScaleB(3.0, 4)}")  ' 3 * 2^4 = 48
#End If

        ' ILogB (integral log base 2) - .NET Core 3.0+
#If NETCOREAPP3_0_OR_GREATER Then
        Console.WriteLine($"ILogB(8.0) = {Math.ILogB(8.0)}")          ' log2(8) = 3
#End If

        ' BitDecrement / BitIncrement (next smaller/larger floating-point value)
#If NETCOREAPP3_0_OR_GREATER Then
        Dim d As Double = 1.0
        Console.WriteLine($"BitDecrement(1.0) = {Math.BitDecrement(d):E16}")
        Console.WriteLine($"BitIncrement(1.0) = {Math.BitIncrement(d):E16}")
#End If
    End Sub

    ' ─── Random Number Generation ─────────────────────────────
    Sub ShowRandomNumbers()
        Console.WriteLine(vbCrLf & "── Random Numbers ──")

        ' VB-specific: Randomize and Rnd
        Randomize()
        Console.WriteLine("VB Rnd (0-1): " & Rnd())
        Console.WriteLine("Random integer 1-6: " & CInt(Int((6 * Rnd()) + 1)))

        ' System.Random class (preferred)
        Dim rng As New Random()
        Console.WriteLine($"Random.Next()        = {rng.Next()}")
        Console.WriteLine($"Random.Next(1, 100)  = {rng.Next(1, 101)}")
        Console.WriteLine($"Random.NextDouble()  = {rng.NextDouble():F4}")
    End Sub

    ' ─── VB-Specific Helpers ──────────────────────────────────
    Sub ShowVBSpecific()
        Console.WriteLine(vbCrLf & "── VB-Specific Numeric Helpers ──")

        ' Hex and Oct (not strictly math, but related)
        Console.WriteLine($"Hex(255) = {Hex(255)}")
        Console.WriteLine($"Oct(255) = {Oct(255)}")

        ' Conversion functions already shown in previous examples,
        ' but here we highlight the numeric ones again.
        Console.WriteLine($"CInt(3.7) = {CInt(3.7)}")
        Console.WriteLine($"CDbl(""123.45"") = {CDbl("123.45")}")
    End Sub

End Module