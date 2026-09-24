/// Unit bindings for greeting.feature: the shell runs in-process with its
/// output writer injected, so no OS-facing resource is touched.
module AccountLedgerCli.Tests.Unit.Steps.GreetingSteps

open System.IO
open TickSpec
open Xunit
open AccountLedgerCli

let mutable private output: string = ""
let mutable private exitCode: int = -1

[<When>]
let ``I run the CLI with no arguments`` () =
    use writer = new StringWriter()
    exitCode <- Program.run writer
    output <- writer.ToString()

[<Then>]
let ``the output is "(.*)"`` (expected: string) =
    Assert.Equal(expected, output.TrimEnd('\r', '\n'))

[<Then>]
let ``the exit code is (\d+)`` (expected: int) = Assert.Equal(expected, exitCode)
