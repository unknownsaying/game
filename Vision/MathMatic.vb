'===============================================================
' VB.NET Math Functions Enumeration
' Calls every System.Math, MathF, and VB math helper without
' writing to the console. Results are stored in variables or
' a collection for inspection.
'===============================================================

Imports System
Imports System.Collections.Generic

Module MathEnumeration

    ' A simple class to hold a function name and its string result
    Public Class MathResult
        Public Property Name As String
        Public Property Value As String
        Public Overrides Function ToString() As String
            Return $"{Name} = {Value}"
        End Function
    End Class

    Sub Main()
        ' Collection to hold all results
        Dim results As New List(Of MathResult)()

        ' ─── Constants ───
        Dim pi As Double = Math.PI
        Dim e As Double = Math.E
#If NETCOREAPP3_0_OR_GREATER Then
        Dim tau As Double = Math.Tau
#End If
        results.Add(New MathResult With {.Name = "Math.PI", .Value = pi.ToString()})
        results.Add(New MathResult With {.Name = "Math.E", .Value = e.ToString()})
#If NETCOREAPP3_0_OR_GREATER Then
        results.Add(New MathResult With {.Name = "Math.Tau", .Value = tau.ToString()})
#End If

        ' ─── Trigonometric ───
        Dim angleDeg As Double = 30.0
        Dim angleRad As Double = angleDeg * Math.PI / 180.0
        Dim sinResult As Double = Math.Sin(angleRad)
        Dim cosResult As Double = Math.Cos(angleRad)
        Dim tanResult As Double = Math.Tan(angleRad)
        Dim sinF As Single = MathF.Sin(CSng(angleRad))
        Dim cosF As Single = MathF.Cos(CSng(angleRad))
        Dim tanF As Single = MathF.Tan(CSng(angleRad))
        results.Add(New MathResult With {.Name = "Math.Sin(30°)", .Value = sinResult.ToString()})
        results.Add(New MathResult With {.Name = "Math.Cos(60°)", .Value = cosResult.ToString()})
        results.Add(New MathResult With {.Name = "Math.Tan(45°)", .Value = tanResult.ToString()})
        results.Add(New MathResult With {.Name = "MathF.Sin(20°)", .Value = sinF.ToString()})
        results.Add(New MathResult With {.Name = "MathF.Cos(40°)", .Value = cosF.ToString()})
        results.Add(New MathResult With {.Name = "MathF.Tan(60°)", .Value = tanF.ToString()})

        ' ─── Hyperbolic ───
        Dim hVal As Double = 1.0
        Dim sinhVal As Double = Math.Sinh(hVal)
        Dim coshVal As Double = Math.Cosh(hVal)
        Dim tanhVal As Double = Math.Tanh(hVal)
        Dim sinhF As Single = MathF.Sinh(CSng(hVal))
        Dim coshF As Single = MathF.Cosh(CSng(hVal))
        Dim tanhF As Single = MathF.Tanh(CSng(hVal))
        results.Add(New MathResult With {.Name = "Math.Sinh(1)", .Value = sinhVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.Cosh(2)", .Value = coshVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.Tanh(3)", .Value = tanhVal.ToString()})
        results.Add(New MathResult With {.Name = "MathF.Sinh(4)", .Value = sinhF.ToString()})
        results.Add(New MathResult With {.Name = "MathF.Cosh(5)", .Value = coshF.ToString()})
        results.Add(New MathResult With {.Name = "MathF.Tanh(6)", .Value = tanhF.ToString()})

        ' ─── Inverse Trigonometric ───
        Dim invVal As Double = 0.5
        Dim asinVal As Double = Math.Asin(invVal)
        Dim acosVal As Double = Math.Acos(invVal)
        Dim atanVal As Double = Math.Atan(invVal)
        Dim atan2Val As Double = Math.Atan2(1.0, 1.0)
        results.Add(New MathResult With {.Name = "Math.Asin(7)", .Value = asinVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.Acos(8)", .Value = acosVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.Atan(9)", .Value = atanVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.Atan2(1,1)", .Value = atan2Val.ToString()})

        ' ─── Exponential & Log ───
        Dim expVal As Double = Math.Exp(2.0)
        Dim powVal As Double = Math.Pow(2.0, 3.0)
        Dim sqrtVal As Double = Math.Sqrt(16.0)
        Dim logVal As Double = Math.Log(Math.Exp(2))
        Dim log10Val As Double = Math.Log10(1000.0)
#If NETCOREAPP3_0_OR_GREATER Then
        Dim log2Val As Double = Math.Log2(8.0)
#End If
        results.Add(New MathResult With {.Name = "Math.Exp(2)", .Value = expVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.Pow(2,3)", .Value = powVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.Sqrt(16)", .Value = sqrtVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.Log(e²)", .Value = logVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.Log10(1000)", .Value = log10Val.ToString()})
#If NETCOREAPP3_0_OR_GREATER Then
        results.Add(New MathResult With {.Name = "Math.Log2(8)", .Value = log2Val.ToString()})
#End If

        ' MathF exponential
        Dim expF As Single = MathF.Exp(2.0F)
        Dim powF As Single = MathF.Pow(2.0F, 3.0F)
        Dim sqrtF As Single = MathF.Sqrt(16.0F)
        results.Add(New MathResult With {.Name = "MathF.Exp(2)", .Value = expF.ToString()})
        results.Add(New MathResult With {.Name = "MathF.Pow(2,3)", .Value = powF.ToString()})
        results.Add(New MathResult With {.Name = "MathF.Sqrt(16)", .Value = sqrtF.ToString()})

        ' ─── Rounding & Truncation ───
        Dim ceilVal As Double = Math.Ceiling(3.4)
        Dim floorVal As Double = Math.Floor(3.4)
        Dim truncVal As Double = Math.Truncate(3.7)
        Dim roundEvenVal As Double = Math.Round(3.5, MidpointRounding.ToEven)
        Dim roundAwayVal As Double = Math.Round(3.5, MidpointRounding.AwayFromZero)
        ' VB‑specific Int and Fix
        Dim intPos As Double = Int(3.7)
        Dim intNeg As Double = Int(-3.7)
        Dim fixPos As Double = Fix(3.7)
        Dim fixNeg As Double = Fix(-3.7)
        results.Add(New MathResult With {.Name = "Math.Ceiling(3.4)", .Value = ceilVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.Floor(5.6)", .Value = floorVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.Truncate(8.9)", .Value = truncVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.Round(3.5,ToEven)", .Value = roundEvenVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.Round(3.5,AwayFromZero)", .Value = roundAwayVal.ToString()})
        results.Add(New MathResult With {.Name = "Int(3.7)", .Value = intPos.ToString()})
        results.Add(New MathResult With {.Name = "Int(-3.7)", .Value = intNeg.ToString()})
        results.Add(New MathResult With {.Name = "Fix(3.7)", .Value = fixPos.ToString()})
        results.Add(New MathResult With {.Name = "Fix(-3.7)", .Value = fixNeg.ToString()})

        ' ─── Abs & Sign ───
        Dim absVal As Double = Math.Abs(-5.0)
        Dim signVal As Integer = Math.Sign(-5.0)
#If NETCOREAPP3_0_OR_GREATER Then
        Dim copySignVal As Double = Math.CopySign(10.0, -1.0)
#End If
        results.Add(New MathResult With {.Name = "Math.Abs(-5)", .Value = absVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.Sign(-5)", .Value = signVal.ToString()})
#If NETCOREAPP3_0_OR_GREATER Then
        results.Add(New MathResult With {.Name = "Math.CopySign(10,-1)", .Value = copySignVal.ToString()})
#End If

        ' ─── Min & Max ───
        Dim minVal As Double = Math.Min(2.5, 3.7)
        Dim maxVal As Double = Math.Max(2.5, 3.7)
#If NETCOREAPP3_0_OR_GREATER Then
        Dim minMagVal As Double = Math.MinMagnitude(-2.5, 3.7)
        Dim maxMagVal As Double = Math.MaxMagnitude(-2.5, 3.7)
#End If
        results.Add(New MathResult With {.Name = "Math.Min(2.5,3.7)", .Value = minVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.Max(2.5,3.7)", .Value = maxVal.ToString()})
#If NETCOREAPP3_0_OR_GREATER Then
        results.Add(New MathResult With {.Name = "Math.MinMagnitude(-2.5,3.7)", .Value = minMagVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.MaxMagnitude(-2.5,3.7)", .Value = maxMagVal.ToString()})
#End If

        ' ─── Division & Remainder ───
        Dim divRemRemainder As Integer
        Dim divRemQuotient As Integer = Math.DivRem(17, 5, divRemRemainder)
        Dim ieeeRemainder As Double = Math.IEEERemainder(17.0, 5.0)
        Dim modResult As Integer = 17 Mod 5
        results.Add(New MathResult With {.Name = "Math.DivRem(17,5) quotient", .Value = divRemQuotient.ToString()})
        results.Add(New MathResult With {.Name = "Math.DivRem(17,5) remainder", .Value = divRemRemainder.ToString()})
        results.Add(New MathResult With {.Name = "Math.IEEERemainder(17,5)", .Value = ieeeRemainder.ToString()})
        results.Add(New MathResult With {.Name = "17 Mod 5", .Value = modResult.ToString()})

        ' ─── Miscellaneous ───
        Dim bigMulVal As Long = Math.BigMul(Integer.MaxValue, 2)
        results.Add(New MathResult With {.Name = "Math.BigMul(Int32.MaxValue,2)", .Value = bigMulVal.ToString()})

#If NETCOREAPP2_0_OR_GREATER Then
        Dim clampLow As Integer = Math.Clamp(10, 1, 5)
        Dim clampIn As Integer = Math.Clamp(3, 1, 5)
        Dim clampHigh As Integer = Math.Clamp(-2, 1, 5)
        results.Add(New MathResult With {.Name = "Math.Clamp(10,1,5)", .Value = clampLow.ToString()})
        results.Add(New MathResult With {.Name = "Math.Clamp(3,1,5)", .Value = clampIn.ToString()})
        results.Add(New MathResult With {.Name = "Math.Clamp(-2,1,5)", .Value = clampHigh.ToString()})
#End If

#If NETCOREAPP3_0_OR_GREATER Then
        Dim fmaVal As Double = Math.FusedMultiplyAdd(2.0, 3.0, 4.0)
        Dim scaleBVal As Double = Math.ScaleB(3.0, 4)
        Dim iLogBVal As Integer = Math.ILogB(8.0)
        Dim bitDecVal As Double = Math.BitDecrement(1.0)
        Dim bitIncVal As Double = Math.BitIncrement(1.0)
        results.Add(New MathResult With {.Name = "Math.FusedMultiplyAdd(2,3,4)", .Value = fmaVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.ScaleB(3,4)", .Value = scaleBVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.ILogB(8)", .Value = iLogBVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.BitDecrement(1)", .Value = bitDecVal.ToString()})
        results.Add(New MathResult With {.Name = "Math.BitIncrement(1)", .Value = bitIncVal.ToString()})
#End If

        ' ─── Random ───
        Randomize()
        Dim rndVal As Double = Rnd()
        Dim rndInt As Integer = CInt(Int((6 * Rnd()) + 1))
        Dim rng As New Random()
        Dim sysNext As Integer = rng.Next()
        Dim sysNextRange As Integer = rng.Next(1, 101)
        Dim sysNextDouble As Double = rng.NextDouble()
        results.Add(New MathResult With {.Name = "VB Rnd()", .Value = rndVal.ToString()})
        results.Add(New MathResult With {.Name = "VB Random 1-6", .Value = rndInt.ToString()})
        results.Add(New MathResult With {.Name = "Random.Next()", .Value = sysNext.ToString()})
        results.Add(New MathResult With {.Name = "Random.Next(1,100)", .Value = sysNextRange.ToString()})
        results.Add(New MathResult With {.Name = "Random.NextDouble()", .Value = sysNextDouble.ToString()})

        ' ─── VB Helpers ───
        Dim hexVal As String = Hex(255)
        Dim octVal As String = Oct(255)
        Dim cintVal As Integer = CInt(3.7)
        Dim cdblVal As Double = CDbl("123.45")
        results.Add(New MathResult With {.Name = "Hex(255)", .Value = hexVal})
        results.Add(New MathResult With {.Name = "Oct(255)", .Value = octVal})
        results.Add(New MathResult With {.Name = "CInt(3.7)", .Value = cintVal.ToString()})
        results.Add(New MathResult With {.Name = "CDbl(""123.45"")", .Value = cdblVal.ToString()})

        ' All math results are now stored in the 'results' collection.
        ' Place a breakpoint on the next line to inspect them.
        Dim allResults As List(Of MathResult) = results
    End Sub

End Module