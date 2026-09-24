Feature: Greeting
  As a developer checking a fresh checkout
  I want the CLI to print a greeting and exit cleanly
  So that I know the build and both test levels work end to end

  Scenario: Running the CLI with no arguments greets the world
    When I run the CLI with no arguments
    Then the output is "Hello, world!"
    And the exit code is 0
