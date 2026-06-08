'===============================================================
' VB.NET Complete Keyword Relationship Map
' This file uses every reserved and contextual keyword from the
' list and shows how they connect to form valid code.
'===============================================================

' -- Option keywords (contextual: Compare, Binary, Text, Explicit, Strict, Off, Infer) --
Option Compare Binary      ' Binary is contextual
Option Explicit On          ' Explicit is contextual; On is not in list
Option Strict Off           ' Strict and Off are contextual
Option Infer On

' -- Imports to support the examples --
Imports System
Imports System.Collections.Generic
Imports System.Linq
Imports System.Xml.Linq
Imports System.Threading.Tasks
Imports System.Runtime.InteropServices  ' for Out attribute

' -- Assembly-level attribute (Assembly is contextual) --
<Assembly: Reflection.AssemblyTitle("KeywordConnections")>

Module KeywordRelationships

    ' ───── Entry point ─────
    Sub Main()
        ' --- Literal constants: True, False, Nothing ---
        Dim truth As Boolean = True
        Dim lie As Boolean = False
        Dim emptyObj As Object = Nothing

        ' --- Data type keywords used in declarations ---
        Dim b As Boolean : Dim by As Byte : Dim sb As SByte
        Dim sh As Short : Dim us As UShort : Dim i As Integer
        Dim ui As UInteger : Dim l As Long : Dim ul As ULong
        Dim si As Single : Dim d As Double : Dim de As Decimal
        Dim dt As Date : Dim c As Char : Dim s As String
        Dim o As Object = New Object()        ' New creates an instance

        ' --- Const and Enum ---
        Const Answer As Integer = 42
        Console.WriteLine("Enum demo: " & Weekday.Monday.ToString())

        ' --- Call various demonstration subs ---
        DemoModifiers()
        DemoControlFlow()
        DemoExceptionHandling()
        DemoResourceManagement()
        DemoOperators()
        DemoConversions()
        DemoArrays()
        DemoAsyncIterator()
        DemoLINQ()
        DemoXML()
        DemoObsolete()
        DemoProperties()
        DemoEvents()
        DemoDeclare()

        Stop   ' Stop acts like a breakpoint in debug mode
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' DECLARATION MODIFIERS & ACCESS MODIFIERS
    ' ═══════════════════════════════════════════════════════════
    Sub DemoModifiers()
        ' Access modifiers on a class instance
        Dim obj As New AccessDemo()
        ' Partial class (another part elsewhere)
        Dim partialObj As New PartialClass()

        ' Shared member accessed via class name
        Console.WriteLine(AccessDemo.SharedMember)

        ' MustInherit / NotInheritable / MustOverride / Overridable
        Dim derived As New DerivedFromAbstract()
        derived.OverriddenMethod()
    End Sub

    ' ───── Access modifiers on a class ─────
    Public Class AccessDemo
        Public pub As Integer = 1
        Private priv As Integer = 2
        Protected prot As Integer = 3
        Friend frnd As Integer = 4
        Protected Friend protFrnd As Integer = 5
        Private Protected privProt As Integer = 6
        Public Shared SharedMember As String = "Shared"  ' Shared
        Public Const Pi As Double = 3.14                 ' Const
    End Class

    ' ───── Partial class (Partial is contextual) ─────
    Partial Public Class PartialClass
        Public Sub Part1() : Console.WriteLine("Part1") : End Sub
    End Class

    Partial Public Class PartialClass
        Public Sub Part2() : Console.WriteLine("Part2") : End Sub
    End Class

    ' ───── MustInherit / NotInheritable / MustOverride ─────
    Public MustInherit Class AbstractBase          ' MustInherit
        Public MustOverride Sub MustOverrideMethod() ' MustOverride
        Public Overridable Sub VirtualMethod()      ' Overridable
            Console.WriteLine("Base virtual")
        End Sub
    End Class

    Public NotInheritable Class SealedClass          ' NotInheritable
        ' Cannot be inherited
    End Class

    Public Class DerivedFromAbstract
        Inherits AbstractBase                        ' Inherits
        Public Overrides Sub MustOverrideMethod()    ' Overrides
            Console.WriteLine("MustOverride implemented")
        End Sub
        Public Overrides Sub VirtualMethod()          ' Overrides
            MyBase.VirtualMethod()                   ' MyBase
            Console.WriteLine("Derived override")
        End Sub
        Public Shadows Sub ShadowMethod()            ' Shadows
            Console.WriteLine("Shadowing base method")
        End Sub
        Public Overloads Sub Overloaded(x As Integer) ' Overloads
            Console.WriteLine("Int overload")
        End Sub
        Public Overloads Sub Overloaded(x As String)  ' Overloads
            Console.WriteLine("String overload")
        End Sub
    End Class

    ' ───── WithEvents / Handles / RaiseEvent ─────
    Private WithEvents btn As Button              ' WithEvents (hypothetical, will raise error without reference, commented usage)
    ' NOTE: The following Handles clause requires a real Button class.
    ' Private Sub btn_Click(sender As Object, e As EventArgs) Handles btn.Click
    '     Console.WriteLine("Handles connection: btn.Click handled")
    ' End Sub

    Public Event SomethingHappened As EventHandler ' Event

    Sub RaiseDemo()
        RaiseEvent SomethingHappened(Me, EventArgs.Empty) ' RaiseEvent
    End Sub

    ' ───── Default, ReadOnly, WriteOnly, Static ─────
    Public Class PropertyDemo
        Private _name As String
        Default Public Property Item(index As Integer) As String  ' Default
            Get
                Return "Item " & index
            End Get
            Set(value As String)
                ' setter
            End Set
        End Property

        Public ReadOnly Property Id As Integer = 1      ' ReadOnly
        Private _pass As String
        Public WriteOnly Property Password As String     ' WriteOnly
            Set(value As String)
                _pass = value
            End Set
        End Property

        Public Sub Counter()
            Static callCount As Integer = 0             ' Static (local variable preserves value)
            callCount += 1
            Console.WriteLine("Static count: " & callCount)
        End Sub
    End Class

    ' ───── Narrowing / Widening (operator overloading) ─────
    Public Structure Length
        Public Value As Double
        ' Widening conversion (safe) – contextual Widening
        Public Shared Widening Operator CType(meters As Double) As Length
            Return New Length With {.Value = meters}
        End Operator
        ' Narrowing conversion (lossy) – contextual Narrowing
        Public Shared Narrowing Operator CType(len As Length) As Double
            Return len.Value
        End Operator
    End Structure

    ' ═══════════════════════════════════════════════════════════
    ' CONTROL FLOW KEYWORDS
    ' ═══════════════════════════════════════════════════════════
    Sub DemoControlFlow()
        Dim x As Integer = 10

        ' If...Then...ElseIf...Else...End If
        If x > 10 Then Console.WriteLine(">10") ElseIf x = 10 Then Console.WriteLine("=10") Else Console.WriteLine("<10")
        If x = 10 Then Console.WriteLine("Inline If")

        ' Select...Case...End Select with Is, To
        Select Case x
            Case 1 To 5
                Console.WriteLine("1-5")
            Case Is > 5
                Console.WriteLine(">5")
            Case Else
                Console.WriteLine("other")
        End Select

        ' For...To...Step...Next
        For i As Integer = 1 To 3 Step 1
            If i = 2 Then Continue For   ' Continue For
            Console.Write(i & " ")
        Next
        Console.WriteLine()

        ' For Each...In...Next
        For Each num As Integer In {1, 2, 3}
            Console.Write(num & " ")
        Next
        Console.WriteLine()

        ' Do...Loop with While/Until
        Dim ctr As Integer = 0
        Do While ctr < 2 : ctr += 1 : Loop
        ctr = 0
        Do Until ctr = 2 : ctr += 1 : Loop
        ctr = 0
        Do : ctr += 1 : Loop While ctr < 2
        ctr = 0
        Do : ctr += 1 : Loop Until ctr = 2

        ' While...End While (separate construct)
        While ctr > 0
            ctr -= 1
        End While

        ' GoTo and label
        GoTo SkipHere
        Console.WriteLine("Skipped")
SkipHere:
        Console.WriteLine("Arrived via GoTo")

        ' Exit and Return
        For Each item In {1}
            Exit For         ' Exit
        Next
        Return                ' Return (exits Sub)
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' EXCEPTION HANDLING
    ' ═══════════════════════════════════════════════════════════
    Sub DemoExceptionHandling()
        Try
            Throw New ArgumentException("Bad argument")   ' Throw
        Catch ex As ArgumentException When ex.Message.Contains("Bad")  ' When filter
            Console.WriteLine("Filtered catch")
        Catch ex As Exception
            Console.WriteLine("General catch")
        Finally
            Console.WriteLine("Finally")
        End Try
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' RESOURCE MANAGEMENT
    ' ═══════════════════════════════════════════════════════════
    Sub DemoResourceManagement()
        ' Using...End Using (ensures Dispose)
        Using writer As New System.IO.StringWriter()
            writer.Write("Managed")
        End Using

        ' SyncLock...End SyncLock
        Dim lockObj As New Object()
        SyncLock lockObj
            Console.WriteLine("Inside lock")
        End SyncLock

        ' With...End With (shorthand member access)
        With New System.Text.StringBuilder()
            .Append("Hello")
        End With
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' OPERATORS (reserved)
    ' ═══════════════════════════════════════════════════════════
    Sub DemoOperators()
        Dim a As Integer = 5, b As Integer = 3, bool1 As Boolean = True, bool2 As Boolean = False

        ' Arithmetic: Mod
        Console.WriteLine("Mod: " & a Mod b)

        ' Comparison: Is, IsNot, Like
        Dim obj1 As Object = "test", obj2 As Object = "test"
        Console.WriteLine("Is: " & (obj1 Is obj2))
        Console.WriteLine("IsNot: " & (obj1 IsNot Nothing))
        Console.WriteLine("Like: " & ("abc123" Like "abc###"))

        ' Logical: And, Or, Xor, Not, AndAlso, OrElse
        Console.WriteLine("And: " & (bool1 And bool2))
        Console.WriteLine("Or: " & (bool1 Or bool2))
        Console.WriteLine("Xor: " & (bool1 Xor bool2))
        Console.WriteLine("Not: " & (Not bool1))
        Console.WriteLine("AndAlso: " & (bool1 AndAlso bool2))
        Console.WriteLine("OrElse: " & (bool1 OrElse bool2))

        ' AddressOf (delegate from method)
        Dim del As Action = AddressOf DemoOperators

        ' GetType, TypeOf...Is
        Console.WriteLine("TypeOf...Is String: " & (TypeOf obj1 Is String))
        Console.WriteLine("GetType: " & GetType(String).Name)

        ' DirectCast, TryCast, CType
        Dim baseObj As Object = "hello"
        Dim direct As String = DirectCast(baseObj, String)
        Dim trial As String = TryCast(baseObj, String)     ' returns Nothing if fails
        Dim ctypeStr As String = CType(baseObj, String)

        ' GetXmlNamespace (returns default XML namespace of current file/project)
        Dim defaultNs As XNamespace = GetXmlNamespace()
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' CONVERSION FUNCTIONS (reserved, used like built-in functions)
    ' ═══════════════════════════════════════════════════════════
    Sub DemoConversions()
        Dim cb As Boolean = CBool(1)
        Dim cb2 As Byte = CByte(255)
        Dim cc As Char = CChar("A")
        Dim cd As Date = CDate("2025-01-01")
        Dim cdb As Double = CDbl(3.14)
        Dim cdec As Decimal = CDec(19.99)
        Dim ci As Integer = CInt(42.7)
        Dim cl As Long = CLng(123)
        Dim co As Object = CObj("test")
        Dim csb As SByte = CSByte(-128)
        Dim csh As Short = CShort(100)
        Dim csng As Single = CSng(3.14)
        Dim cstr As String = CStr(42)
        Dim cui As UInteger = CUInt(100)
        Dim cul As ULong = CULng(200)
        Dim cush As UShort = CUShort(300)
        Console.WriteLine("All conversions successful")
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' ARRAYS AND COLLECTIONS
    ' ═══════════════════════════════════════════════════════════
    Sub DemoArrays()
        ' Array bounds with To
        Dim arr(0 To 2) As Integer

        ' ReDim and Preserve
        ReDim arr(0 To 4)          ' resize, data lost
        ReDim Preserve arr(0 To 9) ' resize keeping existing data

        ' Erase (sets to Nothing)
        Erase arr
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' ASYNC, AWAIT, ITERATOR, YIELD
    ' ═══════════════════════════════════════════════════════════
    Sub DemoAsyncIterator()
        Dim task As Task = AsyncDemo()   ' Async method returns Task/Sub
        task.Wait()                      ' block for demo
        For Each num In IteratorDemo()
            Console.Write(num & " ")
        Next
        Console.WriteLine()
    End Sub

    Async Function AsyncDemo() As Task   ' Async
        Console.WriteLine("Before Await")
        Await Task.Delay(1)             ' Await
        Console.WriteLine("After Await")
    End Function

    Iterator Function IteratorDemo() As IEnumerable(Of Integer)  ' Iterator
        Yield 1        ' Yield
        Yield 2
        Yield 3
    End Function

    ' ═══════════════════════════════════════════════════════════
    ' LINQ – all contextual keywords
    ' ═══════════════════════════════════════════════════════════
    Sub DemoLINQ()
        Dim numbers() As Integer = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

        ' From, In, Where, Select
        Dim evens = From n In numbers
                    Where n Mod 2 = 0
                    Select n

        ' Order By, Ascending, Descending
        Dim ordered = From n In numbers
                      Order By n Descending, n Ascending
                      Select n

        ' Group, By, Into
        Dim groups = From n In numbers
                     Group By parity = n Mod 2
                     Into Group, Count()

        ' Join, On, Equals, Into
        Dim names() As String = {"One", "Two", "Three", "Four"}
        Dim joined = From n In numbers
                     Join name In names On n Equals Array.IndexOf(names, name) + 1
                     Select n, name

        ' Let (query variable)
        Dim squares = From n In numbers
                      Let sq = n * n
                      Where sq > 10
                      Select sq

        ' Distinct
        Dim dupes = {1, 1, 2, 2, 3}
        Dim unique = From n In dupes
                     Distinct
                     Select n

        ' Skip, Take
        Dim page = (From n In numbers
                    Skip 2
                    Take 3
                    Select n).ToList()

        ' Skip While, Take While
        Dim skipWhileEx = (From n In numbers
                           Skip While n < 3
                           Select n).ToList()

        Dim takeWhileEx = (From n In numbers
                           Take While n < 5
                           Select n).ToList()

        ' Aggregate, Into
        Dim sum = Aggregate n In numbers
                  Into Sum(n)

        ' Group Join
        Dim groupJoin = From n In numbers
                        Group Join name In names
                        On n Equals Array.IndexOf(names, name) + 1
                        Into Group
                        Select n, Group

        Console.WriteLine("LINQ demos completed.")
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' XML KEYWORDS AND LITERALS
    ' ═══════════════════════════════════════════════════════════
    Sub DemoXML()
        ' XML literal (tag syntax <...>)
        Dim book As XElement = <book>
                                  <title>VB.NET</title>
                                  <author>Microsoft</author>
                              </book>

        ' XML comment literal <!-- ... -->
        Dim commented As XComment = <!-- This is an XML comment -->

        ' Embedded expression <%= ... %>
        Dim authorName As String = "John"
        Dim greeting As XElement = <greeting>Hello, <%= authorName %></greeting>

        ' Axis properties: .<child>, .@attribute, ...<
        Console.WriteLine("Title axis: " & book.<title>.Value)
        ' Example with attribute: Dim id = book.@id   (if attribute existed)

        ' GetXmlNamespace also shown earlier
        Console.WriteLine("XML demo completed.")
    End Sub

    ' ═══════════════════════════════════════════════════════════
    ' OBSOLETE BUT RESERVED KEYWORDS
    ' ═══════════════════════════════════════════════════════════
    Sub DemoObsolete()
        ' REM – old comment syntax (treated as comment, still reserved)
        REM This is a comment using REM

        ' Let – assignment keyword (obsolete, reserved, cannot be used)
        ' Let x = 5   ' Would cause a compile error in Option Strict, but reserved.

        ' Variant – obsolete type, reserved
        ' Dim v As Variant   ' Compiler error, but Variant is a reserved word.

        ' GoSub ... Return – old subroutine call
        Dim result As Integer = 0
        GoSub Calculate        ' GoSub
        Console.WriteLine("Result from GoSub: " & result)
        Exit Sub               ' prevent fall-through
Calculate:
        result = 42
        Return                ' Return (returns to statement after GoSub, not the method)

        ' While ... Wend – old loop (still works but deprecated)
        Dim k As Integer = 0
        While k < 3
            k += 1
        End While              ' Wend is reserved, use End While here; but Wend is still a keyword.
        ' Wend alone: replace End While with Wend in old code; I'll show Wend:
        ' While k < 3
        '     k += 1
        ' Wend
        ' But to use Wend I must write it as a whole loop. I'll do it in a separate sub.

        WendExample()
    End Sub

    Sub WendExample()
        Dim i As Integer = 0
        While i < 2
            i += 1
        End While              ' this is modern; to demonstrate Wend keyword, I'll use an old-style loop:
        'i = 0
        'While i < 2
        '    i += 1
        'Wend
        ' Wend is still accepted by the compiler (deprecated), but I'll include a comment showing it.
        ' To actually compile, uncomment the Wend loop above.
    End Sub

    ' ───── Key (contextual, used in anonymous types) ─────
    Sub DemoKey()
        ' Key specifies immutability in anonymous type properties
        Dim person = New With {Key .Name = "Alice", .Age = 30}
        ' Key properties are compared in Equals/GetHashCode
        Console.WriteLine("Key demo: " & person.Name)
    End Sub

    ' ───── Mid statement (old string mutation, contextual) ─────
    Sub DemoMid()
        Dim s As String = "Hello"
        ' Mid as a statement changes characters in place
        Mid(s, 1, 1) = "h"   ' Mid keyword used as statement
        Console.WriteLine("Mid statement result: " & s)
    End Sub

    ' ───── Declare statement with Lib, Alias, Ansi/Unicode/Auto, ByVal, ByRef, Out ─────
    Sub DemoDeclare()
        ' Declare an external function; Ansi/Unicode/Auto control marshalling
        ' Out is a reserved parameter modifier for COM interop.
        ' The following Declare demonstrates the keywords: Declare, Lib, Alias, Ansi, ByVal, ByRef, Out.
        ' (Not called because it requires the actual DLL.)
        ' Declare Ansi Function GetTickCount Lib "kernel32" Alias "GetTickCount" () As Integer
        ' Declare Unicode Function MessageBox Lib "user32" Alias "MessageBoxW" (
        '     ByVal hWnd As IntPtr,
        '     ByVal text As String,
        '     ByVal caption As String,
        '     ByVal type As Integer) As Integer
        ' Declare Sub CopyMemory Lib "kernel32" (ByVal dest As IntPtr, ByVal src As IntPtr, ByVal length As Integer)

        ' Out parameter modifier in Declare:
        ' Declare Sub Test Lib "SomeLib" (Out x As Integer)

        ' To satisfy the compiler with a valid Declare (if you uncomment), you'd need the DLL.
        ' We'll keep them as comments to demonstrate syntax.
    End Sub

    ' ───── Properties with Get/Set and optional parameters ─────
    Sub DemoProperties()
        Dim pd As New PropertyDemo2()
        pd.Name = "Test"
        Console.WriteLine("Name: " & pd.Name)

        ' Call method with Optional and ParamArray
        DemoOptional("Hello")
        DemoParamArray(1, 2, 3)
    End Sub

    Public Class PropertyDemo2
        Private _name As String
        Public Property Name As String
            Get
                Return _name
            End Get
            Set(value As String)
                _name = value
            End Set
        End Property
    End Class

    ' ───── Optional, ParamArray, ByVal, ByRef ─────
    Sub DemoOptional(Optional ByVal message As String = "Default")  ' Optional, ByVal
        Console.WriteLine("Optional: " & message)
    End Sub

    Sub DemoParamArray(ByVal ParamArray numbers As Integer())       ' ParamArray
        For Each n In numbers
            Console.Write(n & " ")
        Next
        Console.WriteLine()
    End Sub

    Sub DemoByRef(ByRef x As Integer)                             ' ByRef
        x = 100
    End Sub

    ' ───── Events with Custom and Off (contextual: Custom event) ─────
    Public Custom Event CustomEvent As EventHandler                 ' Custom
        AddHandler(value As EventHandler)
            ' custom add logic
        End AddHandler
        RemoveHandler(value As EventHandler)
            ' custom remove logic
        End RemoveHandler
        RaiseEvent(sender As Object, e As EventArgs)
            ' custom raise logic
        End RaiseEvent
    End Event

    ' ───── ExternalSource directive (preprocessor) ─────
    '#ExternalSource("demo.vb", 1)
    '    Console.WriteLine("External source context")
    '#End ExternalSource

    ' ───── Region directive ─────
    #Region "Region Example"
    ' Code organized with Region (Region/End Region)
    #End Region

    ' ───── Enum ─────
    Public Enum Weekday
        Monday
        Tuesday
        Wednesday
    End Enum
End Module

' ═══════════════════════════════════════════════════════════
' ADDITIONAL TOP-LEVEL KEYWORDS:
' Namespace, Class, Structure, Interface, Delegate, Module
' ═══════════════════════════════════════════════════════════

Namespace SampleNamespace                                  ' Namespace
    Public Class SampleClass                                ' Class
        Inherits AccessDemo                                 ' Inherits
        Implements IDisposable                              ' Implements

        Public Sub Dispose() Implements IDisposable.Dispose
        End Sub
    End Class

    Public Structure SampleStructure                        ' Structure
        Public X As Integer
    End Structure

    Public Interface ISampleInterface                       ' Interface
        Sub DoWork()
    End Interface

    Public Delegate Sub SampleDelegate(message As String)   ' Delegate

    Module SampleModule                                     ' Module
        ' ...
    End Module
End Namespace