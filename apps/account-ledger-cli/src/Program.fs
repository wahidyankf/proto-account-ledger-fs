/// The imperative shell: owns every effect and delegates decisions to the core.
module AccountLedgerCli.Program

open System
open System.IO

/// Writes the greeting to the given writer and returns the process exit code.
/// Taking the writer as a parameter keeps the shell testable in-process.
let run (out: TextWriter) : int =
    out.WriteLine(Greeting.greeting ())
    0

[<EntryPoint>]
let main (_argv: string array) : int = run Console.Out
