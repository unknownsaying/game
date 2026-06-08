'==========================================================
' VB.NET Complete Keyword Connection Demo
' This file demonstrates all VB.NET keywords and their relationships
'==========================================================

Option Explicit On
Option Strict On
Option Compare Binary
Option Infer On

' ───── Namespace declaration ─────
Namespace KeywordConnections

    ' ───── Module (static container) ─────
    Module MainModule

        ' ───── Entry point ─────
        Sub Main()
            ' Literal constants
            Dim truth As Boolean = True
            Dim falsity As Boolean = False
            Dim nothingObj As Object = Nothing

            ' Demonstrate type keywords
            Call DemoTypes()
            Call DemoControlFlow()
            Call DemoExceptionHandling()
            Call DemoResourceManagement()
            Call DemoOperators()
            Call DemoConversions()
            Call DemoAsyncAwait()
            Call DemoLINQ()
            Call DemoArrays()
            Call DemoWithEvents()
            Call DemoXML()

            Stop ' Breakpoint-like behavior in debug mode
        End Sub

        ' ───── Type declarations ─────
        Private Sub DemoTypes()
            Dim b As Boolean                    ' Boolean
            Dim by As Byte = 255                ' Byte
            Dim sb As SByte = -128              ' SByte
            Dim sh As Short = -32768            ' Short
            Dim us As UShort = 65535            ' UShort
            Dim i As Integer = 42               ' Integer
            Dim ui As UInteger = 4294967295     ' UInteger
            Dim l As Long = 9223372036854775807 ' Long
            Dim ul As ULong = 0                 ' ULong
            Dim si As Single = 3.14!            ' Single
            Dim d As Double = 3.14159#          ' Double
            Dim de As Decimal = 19.99@          ' Decimal
            Dim dt As Date = #1/1/2025#         ' Date
            Dim c As Char = "A"c                ' Char
            Dim s As String = "Hello"           ' String
            Dim o As Object = New Object()      ' Object

            ' Const declaration
            Const PI As Double = 3.14159

            ' Enum declaration
            DemoEnumDemo()
        End Sub

        ' ───── Enum ─────
        Private Sub DemoEnumDemo()
            Dim today As Days = Days.Monday
            If today = Days.Monday Then
                Console.WriteLine("Start of week")
            End If
        End Sub

        ' ───── Control flow connections ─────
        Private Sub DemoControlFlow()
            Dim x As Integer = 10

            ' If...Then...ElseIf...Else...End If
            If x > 10 Then
                Console.WriteLine("Greater")
            ElseIf x = 10 Then
                Console.WriteLine("Equal")
            Else
                Console.WriteLine("Less")
            End If

            ' Select...Case...End Select (with Is, To)
            Select Case x
                Case 1 To 5
                    Console.WriteLine("1-5")
                Case Is > 5
                    Console.WriteLine(">5")
                Case Else
                    Console.WriteLine("Other")
            End Select

            ' For...To...Step...Next
            For i As Integer = 1 To 5 Step 1
                If i = 3 Then Continue For
                Console.Write(i & " ")
            Next
            Console.WriteLine()

            ' For Each...In...Next
            Dim items() As Integer = {1, 2, 3}
            For Each item As Integer In items
                Console.Write(item & " ")
            Next
            Console.WriteLine()

            ' Do While...Loop / Do...Loop While
            Dim counter As Integer = 0
            Do While counter < 3
                counter += 1
            Loop

            counter = 0
            Do
                counter += 1
            Loop While counter < 3

            ' Do Until...Loop / Do...Loop Until
            counter = 0
            Do Until counter = 3
                counter += 1
            Loop

            counter = 0
            Do
                counter += 1
            Loop Until counter = 3

            ' While...End While
            While counter > 0
                counter -= 1
            End While

            ' GoTo and label
            Dim goFlag As Boolean = False
            If Not goFlag Then GoTo SkipSection
            Console.WriteLine("Not skipped")
SkipSection:
            Console.WriteLine("Skipped to here")

            ' Return, Exit
            If True Then Return ' Exit Sub (in Sub context)
        End Sub

        ' ───── Exception handling connections ─────
        Private Sub DemoExceptionHandling()
            Try
                Throw New ArgumentException("Demo error")
            Catch ex As ArgumentException When ex.Message.Contains("Demo")
                Console.WriteLine("Caught filtered exception: " & ex.Message)
            Catch ex As Exception
                Console.WriteLine("General catch")
            Finally
                Console.WriteLine("Finally block executed")
            End Try
        End Sub

        ' ───── Resource management ─────
        Private Sub DemoResourceManagement()
            ' Using...End Using (disposes resource)
            Using writer As New System.IO.StringWriter()
                writer.Write("Resource managed")
            End Using

            ' SyncLock...End SyncLock (thread synchronization)
            Dim lockObj As New Object()
            SyncLock lockObj
                Console.WriteLine("Thread-safe block")
            End SyncLock

            ' With...End With (object member shorthand)
            Dim sb As New System.Text.StringBuilder()
            With sb
                .Append("Hello")
                .Append(" ")
                .Append("World")
            End With
        End Sub

        ' ───── Operators ─────
        Private Sub DemoOperators()
            Dim a As Integer = 5, b As Integer = 3

            ' Arithmetic: Mod
            Console.WriteLine("Mod: " & (a Mod b))

            ' Comparison: Is, IsNot, Like
            Dim obj1 As Object = "test"
            Dim obj2 As Object = "test"
            Console.WriteLine("Is: " & (obj1 Is obj2).ToString())
            Console.WriteLine("IsNot: " & (obj1 IsNot Nothing).ToString())
            Console.WriteLine("Like: " & ("abc123" Like "abc###"))

            ' Logical: And, Or, Xor, Not, AndAlso, OrElse
            Dim bool1 As Boolean = True, bool2 As Boolean = False
            Console.WriteLine("And: " & (bool1 And bool2))
            Console.WriteLine("Or: " & (bool1 Or bool2))
            Console.WriteLine("Xor: " & (bool1 Xor bool2))
            Console.WriteLine("Not: " & (Not bool1))
            Console.WriteLine("AndAlso: " & (bool1 AndAlso bool2)) ' Short-circuit
            Console.WriteLine("OrElse: " & (bool1 OrElse bool2))   ' Short-circuit

            ' Type checking: TypeOf...Is, GetType
            Dim obj As Object = "Hello"
            Console.WriteLine("TypeOf...Is: " & (TypeOf obj Is String))
            Console.WriteLine("GetType: " & GetType(String).Name)

            ' AddressOf (delegate creation)
            Dim handler As EventHandler = AddressOf DemoEventHandler
        End Sub

        Private Sub DemoEventHandler(sender As Object, e As EventArgs)
            ' Event handler for AddressOf demo
        End Sub

        ' ───── Conversion keywords ─────
        Private Sub DemoConversions()
            ' Conversion functions
            Dim cBool As Boolean = CBool(1)
            Dim cByte As Byte = CByte(255)
            Dim cChar As Char = CChar("A")
            Dim cDate As Date = CDate("2025-01-01")
            Dim cDbl As Double = CDbl(3.14)
            Dim cDec As Decimal = CDec(19.99)
            Dim cInt As Integer = CInt(42.7)
            Dim cLng As Long = CLng(123456)
            Dim cObj As Object = CObj("test")
            Dim cSByte As SByte = CSByte(-128)
            Dim cShort As Short = CShort(100)
            Dim cSng As Single = CSng(3.14)
            Dim cStr As String = CStr(42)
            Dim cUInt As UInteger = CUInt(100)
            Dim cULng As ULong = CULng(100)
            Dim cUShort As UShort = CUShort(100)

            ' DirectCast, TryCast, CType
            Dim baseObj As Object = "Test"
            Dim directResult As String = DirectCast(baseObj, String)
            Dim tryResult As String = TryCast(baseObj, String) ' Returns Nothing if fails
            Dim ctypeResult As String = CType(baseObj, String)
        End Sub

        ' ───── Async and Await ─────
        Private Async Sub DemoAsyncAwait()
            Console.WriteLine("Before await")
            Await Task.Delay(1) ' Await suspends execution
            Console.WriteLine("After await")

            ' Iterator with Yield
            For Each num As Integer In DemoIterator()
                Console.Write(num & " ")
            Next
            Console.WriteLine()
        End Sub

        Private Iterator Function DemoIterator() As IEnumerable(Of Integer)
            Yield 1 ' Yield returns one element at a time
            Yield 2
            Yield 3
        End Function

        ' ───── LINQ connections ─────
        Private Sub DemoLINQ()
            Dim numbers() As Integer = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

            ' From...In...Where...Select
            Dim evenNumbers = From n In numbers
                              Where n Mod 2 = 0
                              Select n

            ' Order By with Ascending/Descending
            Dim orderedDesc = From n In numbers
                              Order By n Descending
                              Select n

            ' Group...By...Into
            Dim groups = From n In numbers
                         Group By parity = n Mod 2
                         Into Group, Count()

            ' Join...On...Equals...Into
            Dim names() As String = {"One", "Two", "Three"}
            Dim joined = From n In numbers
                         Join name In names
                         On n Equals Array.IndexOf(names, name) + 1
                         Select n, name

            ' Aggregate...Into
            Dim sum = Aggregate n In numbers
                      Into Sum(n)

            ' Let (query variable)
            Dim squares = From n In numbers
                          Let sq = n * n
                          Where sq > 10
                          Select sq

            ' Distinct
            Dim duplicates = {1, 1, 2, 2, 3, 3}
            Dim unique = From n In duplicates
                         Distinct
                         Select n

            ' Skip, Take, Skip While, Take While
            Dim skipTake = (From n In numbers
                           Skip 3
                           Take 4
                           Select n).ToList()

            ' Group Join
            Dim groupJoin = From n In numbers
                            Group Join name In names
                            On n Equals Array.IndexOf(names, name) + 1
                            Into Group
                            Select n, Group
        End Sub

        ' ───── Array connections ─────
        Private Sub DemoArrays()
            ' Array declaration with To
            Dim arr(0 To 4) As Integer

            ' ReDim with Preserve
            ReDim arr(0 To 9) ' Resize (loses data)
            ReDim Preserve arr(0 To 14) ' Resize preserving existing data

            ' Erase (clears array)
            Erase arr ' Releases reference, sets to Nothing
        End Sub

        ' ───── Events and Handles ─────
        Private WithEvents button As New Button ' WithEvents enables Handles

        Private Sub DemoWithEvents()
            ' RaiseEvent triggers declared event
            RaiseEvent CustomEvent(Me, EventArgs.Empty)
        End Sub

        Private Event CustomEvent As EventHandler ' Event declaration

        ' Handles connects event handler to WithEvents variable
        Private Sub button_Click(sender As Object, e As EventArgs) Handles button.Click
            Console.WriteLine("Button clicked")
        End Sub

        ' ───── XML connections ─────
        Private Sub DemoXML()
            ' XML literal
            Dim xml As XElement = <book>
                                      <title>VB.NET</title>
                                      <author>Microsoft</author>
                                  </book>

            ' GetXmlNamespace
            Dim ns As XNamespace = GetXmlNamespace()

            ' Embedded expression in XML
            Dim name As String = "John"
            Dim xmlWithExpr As XElement = <greeting>Hello <%= name %></greeting>

            ' XML axis properties
            Console.WriteLine("Title: " & xml.<title>.Value)
            Console.WriteLine("Author attribute: ")
        End Sub

        ' ───── Removed/obsolete keywords (commented) ─────
        ' Wend (replaced by End While)
        ' Let (obsolete assignment)
        ' Variant (obsolete type)
        ' GoSub...Return (obsolete subroutine call)
        ' REM (old comment syntax, replaced by ')
        ' On Error (replaced by Try...Catch)

    End Module

    ' ───── Class declarations with modifiers ─────
    Public Class BaseDemo
        ' Access modifiers demonstrated
        Public publicField As Integer
        Private privateField As Integer
        Protected protectedField As Integer
        Friend friendField As Integer
        Protected Friend protFriendField As Integer
        Private Protected privProtField As Integer

        ' Shared member (class-level, not instance)
        Public Shared SharedField As Integer = 100

        ' Const member
        Public Const ConstantValue As Integer = 42

        ' Overridable member (can be overridden)
        Public Overridable Sub VirtualMethod()
            Console.WriteLine("Base virtual")
        End Sub

        ' Non-overridable
        Public NotOverridable Sub NonVirtualMethod()
            Console.WriteLine("Cannot override")
        End Sub
    End Class

    ' MustInherit (abstract class)
    Public MustInherit Class AbstractDemo
        ' MustOverride (abstract method, no implementation)
        Public MustOverride Sub AbstractMethod()
    End Class

    ' NotInheritable (sealed class, cannot be inherited)
    Public NotInheritable Class SealedDemo
        ' Implementation
    End Class

    ' Inheritance with Inherits and Implements
    Public Class DerivedDemo
        Inherits BaseDemo ' Inherits connects to base class
        Implements IDisposable ' Implements connects to interface

        ' Overrides (overrides base virtual member)
        Public Overrides Sub VirtualMethod()
            MyBase.VirtualMethod() ' MyBase calls base implementation
            Console.WriteLine("Derived override")
        End Sub

        ' Shadows (hides base member)
        Public Shadows Sub NonVirtualMethod()
            MyClass.NonVirtualMethod() ' MyClass ensures non-virtual call
            Console.WriteLine("Shadowed method")
        End Sub

        ' Overloads (multiple versions with different signatures)
        Public Overloads Sub OverloadedMethod(x As Integer)
            Console.WriteLine("Integer version")
        End Sub

        Public Overloads Sub OverloadedMethod(x As String)
            Console.WriteLine("String version")
        End Sub

        ' Me reference (current instance)
        Public Sub ShowMe()
            Console.WriteLine(Me.ToString())
        End Sub

        ' IDisposable implementation
        Private disposed As Boolean = False
        Protected Overridable Sub Dispose(disposing As Boolean)
            If Not disposed Then
                If disposing Then
                    ' Free managed resources
                End If
                disposed = True
            End If
        End Sub

        Public Sub Dispose() Implements IDisposable.Dispose
            Dispose(True)
            GC.SuppressFinalize(Me)
        End Sub
    End Class

    ' ───── Structure ─────
    Public Structure DemoStructure
        Public X As Integer
        Public Y As Integer

        ' Constructor (parameterized)
        Public Sub New(x As Integer, y As Integer)
            Me.X = x
            Me.Y = y
        End Sub
    End Structure

    ' ───── Interface ─────
    Public Interface IDemoInterface
        Sub Method1()
        Function Method2() As Integer
        Property Value As String
        Event Changed As EventHandler
    End Interface

    ' ───── Delegate ─────
    Public Delegate Sub DemoDelegate(message As String) ' Delegate type definition

    ' ───── Property with getters/setters ─────
    Public Class PropertyDemo
        Private _name As String

        ' Full property with Get/Set
        Public Property Name As String
            Get
                Return _name
            End Get
            Set(value As String)
                _name = value
            End Set
        End Property

        ' ReadOnly property (only Get)
        Public ReadOnly Property Id As Integer = 1

        ' WriteOnly property (only Set)
        Private _password As String
        Public WriteOnly Property Password As String
            Set(value As String)
                _password = value
            End Set
        End Property

        ' Default property (indexer)
        Default Public Property Item(index As Integer) As String
            Get
                Return "Item " & index
            End Get
            Set(value As String)
                ' Set implementation
            End Set
        End Property

        ' Auto-implemented property
        Public Property Age As Integer
    End Class

    ' ───── Operator overloading ─────
    Public Structure ComplexNumber
        Public Real As Double
        Public Imaginary As Double

        ' Widening/Narrowing conversion operators
        Public Shared Widening Operator CType(value As Double) As ComplexNumber
            Return New ComplexNumber With {.Real = value, .Imaginary = 0}
        End Operator

        Public Shared Narrowing Operator CType(value As ComplexNumber) As Double
            Return value.Real
        End Operator

        ' Arithmetic operator
        Public Shared Operator +(a As ComplexNumber, b As ComplexNumber) As ComplexNumber
            Return New ComplexNumber With {
                .Real = a.Real + b.Real,
                .Imaginary = a.Imaginary + b.Imaginary
            }
        End Operator
    End Structure

    ' ───── Custom Event ─────
    Public Class CustomEventDemo
        Private _handlers As EventHandler

        ' Custom event with AddHandler/RemoveHandler
        Public Custom Event StatusChanged As EventHandler
            AddHandler(value As EventHandler)
                _handlers = DirectCast([Delegate].Combine(_handlers, value), EventHandler)
            End AddHandler
            RemoveHandler(value As EventHandler)
                _handlers = DirectCast([Delegate].Remove(_handlers, value), EventHandler)
            End RemoveHandler
            RaiseEvent(sender As Object, e As EventArgs)
                _handlers?.Invoke(sender, e)
            End RaiseEvent
        End Event
    End Class

    ' ───── Region for organization ─────
    #Region "COM Interop Demo"
    ' Declare statement for external functions
    Public Class InteropDemo
        ' Declare...Lib...Alias connections
        ' Declare Auto Function MessageBox Lib "user32.dll" Alias "MessageBoxW" (
        '    ByVal hWnd As IntPtr,
        '    ByVal text As String,
        '    ByVal caption As String,
        '    ByVal type As UInteger) As Integer
        '
        ' Note: Commented as actual P/Invoke would require platform-specific handling
    End Class
    #End Region

    ' ───── Enum ─────
    Public Enum Days
        Sunday = 0
        Monday = 1
        Tuesday = 2
        Wednesday = 3
        Thursday = 4
        Friday = 5
        Saturday = 6
    End Enum

    ' ───── Partial class ─────
    Partial Public Class PartialDemo
        Public Sub Method1()
            Console.WriteLine("Part 1")
        End Sub
    End Class

    Partial Public Class PartialDemo
        Public Sub Method2()
            Console.WriteLine("Part 2")
        End Sub
    End Class

    ' ───── Module with Static variable ─────
    Module StaticDemo
        Public Sub DemoStatic()
            Static counter As Integer ' Static preserves value between calls
            counter += 1
            Console.WriteLine("Call count: " & counter)
        End Sub
    End Module

End Namespace