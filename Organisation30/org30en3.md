# The Feedback Loop in Sequential Logic – What It Enables

**The common element is the loop (feedback).**  
With it you can not only **store, count and switch**, but much more.  
Instead of pure **formulas** you get real **algorithms** in hardware.

## What becomes possible with a feedback loop

| Capability                     | What the loop enables                                | Practical examples                                   | Typical circuit                     |
|--------------------------------|------------------------------------------------------|------------------------------------------------------|-------------------------------------|
| **Storing**                    | State is held permanently                            | 1-bit memory, registers, RAM                         | SR-Latch, SRAM cell                 |
| **Counting**                   | Pulses are added / decremented                       | Binary counters, frequency dividers                  | Chain of T-Flipflops                |
| **Switching / Controlling**    | State changes according to rules                     | Traffic lights, automata, control units              | Finite State Machine (FSM)          |
| **Synchronizing**              | Everything happens at the same clock                 | Processors, buses, pipelines                         | Clocked flip-flops + clock generator|
| **Sequencing**                 | Steps are executed one after another                 | Instruction execution in a CPU                       | Program Counter + control unit      |
| **Delaying / Timing**          | Signals are shifted in time                          | One-clock delay, pipeline stages                     | Shift register                      |
| **Oscillating**                | Permanent oscillation (clock generation)             | Ring oscillators, on-chip clocks                     | 3–5 inverted loops                  |
| **Multi-step computation**     | Complex operations over multiple clock cycles        | Multiplication, division, floating-point arithmetic  | ALU + registers + FSM               |
| **Executing algorithms**       | Hardware runs real programs / algorithms             | Every microprocessor, microcontroller                | CPU (registers + ALU + FSM)         |

## Yes – Algorithms instead of formulas!

- **Combinational logic** = **Formula**  
  → One input → immediate output (like a mathematical equation).

- **Sequential logic (with loop)** = **Algorithm**  
  → Input + current state → new state + output  
  → The system has a “memory” and can compute something over multiple steps.

**Example:**  
An ALU alone is just a formula (A + B).  
But ALU + registers + program counter + FSM = a processor that executes a real **algorithm** (e.g. “multiply two numbers with shift-and-add”) step by step.

## Is there anything else?

Yes, two more important things that only become possible through loops:

1. **Turing completeness** (theoretically)  
   With enough flip-flops, an ALU and an FSM you can execute **any algorithm** a computer can run. The loop is the reason why hardware can be universally programmable at all.

2. **Self-modification / learning capability** (with extensions)  
   In modern systems (e.g. with reconfigurable logic blocks like FPGAs) the loop can even change its own rules – but that is already more “Reconfigurable Computing”.

**In short:**  
The feedback loop is the “ghost in the machine”. Without it there would only be rigid formulas. With it everything arises that we understand as “digital technology”, “computers” and “programmable hardware”.
