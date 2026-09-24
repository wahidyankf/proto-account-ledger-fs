/// Integration bindings for greeting.feature: the real entry point runs
/// against the process's real console, whose output stream is redirected so
/// the step can read what the CLI wrote. No network is involved.
module AccountLedgerCli.Tests.Integration.Steps.GreetingSteps

open System
open System.IO
open TickSpec
open Xunit
open AccountLedgerCli

let mutable private output: string = ""
let mutable private exitCode: int = -1

[<When>]
let ``I run the CLI with no arguments`` () =
    let original = Console.Out
    use writer = new StringWriter()
    Console.SetOut writer

    try
        exitCode <- Program.main [||]
    finally
        Console.SetOut original

    output <- writer.ToString()

[<Then>]
let ``the output is "(.*)"`` (expected: string) =
    Assert.Equal(expected, output.TrimEnd('\r', '\n'))

[<Then>]
let ``the exit code is (\d+)`` (expected: int) = Assert.Equal(expected, exitCode)
