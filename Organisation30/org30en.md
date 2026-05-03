# The Two Smallest Logic Circuits That Cannot Be Formalized as a Boolean Formula

**The two SR-Latches (also known as RS-Flip-Flops)** – one made from two NOR gates and one from two NAND gates.

## Explanation

All **combinational** logic circuits (AND, OR, NOT, NAND, NOR, XOR etc. and any combinations) can easily be formalized as Boolean formulas (e.g. in DNF/CNF, truth table or algebraic equation).

The two **smallest sequential** logic circuits, however, **cannot**:

### 1. NOR-based SR-Latch
Two cross-coupled NOR gates.  
The output \( Q \) depends not only on the current inputs \( S \) and \( R \), but also on the previous state (feedback loop). There is no static Boolean formula \( Q = f(S, R) \).

### 2. NAND-based SR-Latch
Two cross-coupled NAND gates.  
Exactly the same problem: memory behavior through feedback – no pure formula without state/time dependency.

These two circuits are the classic smallest examples in digital technology that can no longer be described purely combinatorially (i.e. as a simple formula).
