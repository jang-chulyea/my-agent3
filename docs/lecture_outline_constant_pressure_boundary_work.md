# Lecture Outline: Constant Pressure Boundary Work

## Topic
Constant Pressure Boundary Work (Isobaric Process)

---

## 1. Concept Explanation

### Definition
Constant pressure boundary work refers to the mechanical energy transfer (work) that occurs when a system experiences expansion or compression while maintaining a **constant external pressure**. This is also known as **isobaric work** or **flow work**.

### Context
- Occurs in systems where pressure remains constant throughout the process
- Common in:
  - Piston-cylinder systems with external atmospheric pressure
  - Heating water in an open container
  - Turbines and compressors operating at steady state
  - Industrial processes with rigid pressure constraints

### Key Distinction
- **Boundary work**: Energy transferred across system boundaries due to volume change
- **Constant pressure**: External pressure $P_{ext} = P$ remains unchanged during the process

---

## 2. Intuition

### Visual Picture
Imagine a piston in a cylinder with a constant external force (weight + atmospheric pressure) pressing down:
- When the gas heats up → it expands → piston moves up
- External force remains the same throughout
- Work is done against this constant external pressure

### Analogy
Think of inflating a balloon in the open air:
- The atmospheric pressure remains constant at 1 atm
- As you pump air in, the balloon expands
- Work must be done against this constant atmospheric pressure
- The more volume increase, the more work required

### Energy Flow
```
Heat Input → Internal Energy Change + Work Output
Q = ΔU + W_boundary
```

At constant pressure, work is proportional to volume change:
- **Large volume expansion** = Large work output
- **Small volume expansion** = Small work output
- **Volume compression** = Work input (negative work output)

---

## 3. Formula

### Basic Formula
$$W = P \cdot \Delta V = P(V_2 - V_1)$$

Where:
- $W$ = boundary work (J or kJ)
- $P$ = constant external pressure (Pa or kPa)
- $\Delta V$ = change in volume (m³)
- $V_2$ = final volume
- $V_1$ = initial volume

### Sign Convention
- **Expansion** ($V_2 > V_1$): $W > 0$ (system does work on surroundings)
- **Compression** ($V_2 < V_1$): $W < 0$ (surroundings do work on system)

### For Ideal Gas at Constant Pressure
Since $PV = nRT$:

$$W = P(V_2 - V_1) = nR(T_2 - T_1)$$

Or using specific volume:
$$w = P(v_2 - v_1)$$

where $w$ is specific work (work per unit mass).

### First Law of Thermodynamics (Constant Pressure)
$$Q = \Delta U + W = \Delta U + P\Delta V$$

At constant pressure, the heat capacity relation:
$$Q = nC_p\Delta T$$

---

## 4. Typical Exam Question Patterns

### Pattern 1: Direct Calculation
**Example:** A rigid piston-cylinder device contains 0.5 kg of water at 100°C and 1 atm. Heat is added until the temperature reaches 150°C. Calculate the boundary work done.

**Solution approach:**
1. Identify: constant pressure, need $\Delta V$
2. Find initial and final volumes from steam tables
3. Apply $W = P(V_2 - V_1)$

### Pattern 2: Energy Balance
**Example:** A gas undergoes an isobaric process. 500 kJ of heat is added. The internal energy increases by 350 kJ. Calculate the boundary work done.

**Solution approach:**
1. Use First Law: $Q = \Delta U + W$
2. Solve for W: $W = Q - \Delta U = 500 - 350 = 150$ kJ

### Pattern 3: Combined with Other Processes
**Example:** A process consists of two stages:
- Stage 1: Constant volume heating
- Stage 2: Constant pressure expansion

Calculate total work done.

**Solution approach:**
1. Stage 1: $W_1 = 0$ (constant volume)
2. Stage 2: $W_2 = P(V_2 - V_1)$
3. Total: $W_{total} = W_1 + W_2$

### Pattern 4: Finding Final State
**Example:** Starting at 25°C and 1 atm, air is heated at constant pressure until volume doubles. Find the final temperature and work done.

**Solution approach:**
1. Use ideal gas law at constant pressure: $\frac{V_1}{T_1} = \frac{V_2}{T_2}$
2. If $V_2 = 2V_1$, then $T_2 = 2T_1$
3. Calculate $W = P(V_2 - V_1) = nR(T_2 - T_1)$

---

## 5. Common Mistakes

### Mistake 1: Forgetting Sign Convention
❌ **Wrong:** Calculating $W = |P\Delta V|$ without considering direction
✓ **Correct:** Remember negative work means work done ON the system

### Mistake 2: Using Wrong Pressure
❌ **Wrong:** Using system pressure $P_{system}$ instead of external pressure $P_{ext}$
✓ **Correct:** Boundary work uses external (applied) pressure, which is constant

### Mistake 3: Unit Conversion Errors
❌ **Wrong:** Mixing Pa and kPa without conversion
✓ **Correct:** Ensure consistent units: 
- $1 \text{ kPa} \cdot m^3 = 1 \text{ kJ}$
- $1 \text{ Pa} \cdot m^3 = 1 \text{ J}$

### Mistake 4: Confusing Constant Pressure with Reversible
❌ **Wrong:** "Constant pressure means reversible process"
✓ **Correct:** Constant pressure processes can be reversible or irreversible

### Mistake 5: Neglecting Phase Changes
❌ **Wrong:** Using ideal gas law for vapors without checking two-phase region
✓ **Correct:** Use steam tables or property data for accurate volumes during phase change

### Mistake 6: Assuming Negligible Work
❌ **Wrong:** Ignoring boundary work because "it seems small"
✓ **Correct:** Even small pressure × large volume = significant work

### Mistake 7: Wrong Heat Capacity
❌ **Wrong:** Using $C_v$ instead of $C_p$ in $Q = nC_p\Delta T$
✓ **Correct:** For constant pressure: $Q = nC_p\Delta T$

### Mistake 8: Pressure Units in Joules
❌ **Wrong:** $W = 100 \text{ atm} \times 2 \text{ m}^3 = 200 \text{ (wrong units)}$
✓ **Correct:** Convert to Pa first:
$$W = 100 \times 101325 \text{ Pa} \times 2 \text{ m}^3 = 20,265,000 \text{ J}$$

---

## Summary Table

| Aspect | Details |
|--------|---------|
| **Definition** | Work done by/on system at constant external pressure |
| **Formula** | $W = P\Delta V = P(V_2 - V_1)$ |
| **For ideal gas** | $W = nR(T_2 - T_1)$ |
| **Expansion** | $W > 0$ (work output) |
| **Compression** | $W < 0$ (work input) |
| **First Law** | $Q = \Delta U + P\Delta V$ |
| **Heat transfer** | $Q = nC_p\Delta T$ |
| **Unit conversion** | $1 \text{ kPa} \cdot m^3 = 1 \text{ kJ}$ |

---

## Practice Problems

1. **Basic Calculation**: A cylinder contains 2 moles of ideal gas at 300 K and 200 kPa. The gas is heated at constant pressure to 600 K. Calculate the work done.

2. **Energy Balance**: In a constant pressure process, 1000 J of heat is supplied to a system. If the system's internal energy increases by 600 J, what is the boundary work?

3. **Phase Change**: 1 kg of water at 100°C and 1 atm is completely vaporized at constant pressure. (Use steam table values: $v_f = 0.001043 m³/kg$, $v_g = 1.673 m³/kg$). Calculate the work done.

4. **Multi-step Process**: A gas undergoes: (1) constant volume heating from 300K to 600K at 100 kPa, then (2) constant pressure expansion back to original volume. Find total work done for 1 mole of gas.

---

**Subject:** Thermodynamics  
**Topic:** Constant Pressure Boundary Work (Isobaric Process)  
**Difficulty Level:** Intermediate  
**Prerequisite Knowledge:** First Law of Thermodynamics, Ideal Gas Law, PV Diagrams
