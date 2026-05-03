# Logic Circuits That Cannot Be Formalized as a Static Boolean Formula

The condition mentioned („**cannot be formalized as a static boolean formula** \( Q = f(\text{inputs}) \)") applies **exclusively to sequential logic circuits**.

**Reason:** There is **feedback** or an internal **state memory**. The output therefore depends not only on the current inputs, but also on the previous state.  
Formula:  
`Output(t) = f(Inputs(t), State(t-1))`

## 1. ALU – **No**, it does **not** meet the condition!
An **ALU** (Arithmetic Logic Unit) is **purely combinational**.  
It has no feedback and no internal memory. Every result can be fully described as a Boolean formula or truth table.

## 2. Other Sequential Logic Circuits (Examples)

| Circuit                            | Why no pure formula?                             | Typical Complexity   | Example Input/Output |
|------------------------------------|--------------------------------------------------|----------------------|----------------------|
| **D-Latch / D-Flipflop**           | Feedback + clock → state memory                  | Small                | D + CLK → Q stores D on clock edge |
| **JK-Flipflop**                    | Feedback + J/K → toggle mode                     | Medium               | J=1, K=1 → toggles on clock |
| **T-Flipflop**                     | Feedback → toggles when T=1                      | Small                | T=1 + clock → Q changes |
| **Shift Register** (e.g. 4-Bit)    | Chain of flip-flops with shift                   | Medium               | Serial input → parallel output |
| **Binary Counter**                 | Chain of flip-flops with feedback                | Medium–large         | CLK pulses → counts 0…15 |
| **Finite State Machine (FSM)**     | Internal states + transition table               | Medium–very large    | State + input → new state + output |
| **Register** (e.g. 8-Bit)          | Multiple flip-flops in parallel + CLK            | Medium               | 8 data + CLK → stores byte |
| **SRAM Memory Cell**               | Cross-coupled inverters                          | Very small           | Write/read stores 1 bit |
| **Full Microprocessor / CPU**      | Registers + FSM + pipeline                       | Very large           | Instructions → sequential state changes |

## Rule of Thumb
- **With feedback or clock + memory** → **no formula possible**  
- **Without feedback (combinational)** → **always possible as formula** (ALU, adder, multiplexer …)

All these circuits are sequential and require a state description (e.g. state diagram or next-state equations).
