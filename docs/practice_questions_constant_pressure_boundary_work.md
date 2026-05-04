# Practice Questions: Constant Pressure Boundary Work

---

## Question 1: Conceptual Understanding

### Question
A container of gas at constant pressure is heated. A student claims: "Since the pressure is constant, the work done by the gas must be zero." 

**Is this statement true or false? Explain your reasoning and describe what actually happens to the work during heating.**

---

### Answer

**False.** This is a common misconception.

### Explanation

**Why the student's reasoning is wrong:**
- The student confuses "constant pressure" with "no volume change"
- Constant pressure does NOT mean volume is fixed
- At constant pressure, volume DOES change (especially when heat is added)

**What actually happens:**

1. **During heating at constant pressure:**
   - Temperature increases: $T_2 > T_1$
   - From ideal gas law at constant P: $\frac{V}{T} = \text{constant}$
   - Volume must increase: $V_2 > V_1$
   - Therefore: $\Delta V = V_2 - V_1 > 0$

2. **Work calculation:**
   $$W = P\Delta V = P(V_2 - V_1) > 0$$
   - Work IS done BY the system
   - This work goes into pushing against the external pressure
   - The system expands as it's heated

3. **Energy flow:**
   $$Q = \Delta U + W$$
   - Heat added: $Q > 0$
   - Internal energy increase: $\Delta U > 0$ (temperature rises)
   - Work output: $W > 0$ (expansion work)
   - All three are positive

**Physical interpretation:**
When you heat gas at constant pressure (like in a balloon under atmospheric pressure), the gas expands and does work pushing back the surroundings. The more it expands, the more work it does. Zero work only occurs if volume doesn't change (constant volume process, not constant pressure).

**Key concept to remember:**
- **Constant pressure** = pressure doesn't change
- **Constant volume** = volume doesn't change (work = 0)
- These are different things!

---

## Question 2: Calculation Problem

### Question
A piston-cylinder device contains 0.5 kg of steam at 200 kPa and 150°C. The steam is heated at constant pressure until its temperature reaches 300°C.

**Given data (from steam tables):**
- At 200 kPa, 150°C: $v_1 = 1.0528 \text{ m}^3/\text{kg}$
- At 200 kPa, 300°C: $v_2 = 1.4163 \text{ m}^3/\text{kg}$

**Calculate:**
1. The change in volume
2. The boundary work done by the steam
3. The change in internal energy (given: $u_1 = 2768.8 \text{ kJ/kg}$, $u_2 = 3071.2 \text{ kJ/kg}$)
4. The heat transferred to the steam (using First Law)

---

### Answer

#### Step 1: Calculate Change in Volume

**Initial volume:**
$$V_1 = m \cdot v_1 = 0.5 \text{ kg} \times 1.0528 \text{ m}^3/\text{kg} = 0.5264 \text{ m}^3$$

**Final volume:**
$$V_2 = m \cdot v_2 = 0.5 \text{ kg} \times 1.4163 \text{ m}^3/\text{kg} = 0.7082 \text{ m}^3$$

**Change in volume:**
$$\Delta V = V_2 - V_1 = 0.7082 - 0.5264 = 0.1818 \text{ m}^3$$

#### Step 2: Calculate Boundary Work

$$W = P\Delta V = 200 \text{ kPa} \times 0.1818 \text{ m}^3$$

$$W = 200 \times 0.1818 = 36.36 \text{ kJ}$$

**Note:** $1 \text{ kPa} \cdot m^3 = 1 \text{ kJ}$

#### Step 3: Calculate Change in Internal Energy

$$\Delta U = m(u_2 - u_1)$$

$$\Delta U = 0.5 \text{ kg} \times (3071.2 - 2768.8) \text{ kJ/kg}$$

$$\Delta U = 0.5 \times 302.4 = 151.2 \text{ kJ}$$

#### Step 4: Calculate Heat Transfer (First Law)

$$Q = \Delta U + W$$

$$Q = 151.2 + 36.36 = 187.56 \text{ kJ}$$

**Or using specific heat:**
$$q = m(h_2 - h_1)$$
where $h$ is specific enthalpy (can be read from steam tables)

---

### Summary of Results

| Quantity | Value | Unit |
|----------|-------|------|
| Change in volume | 0.1818 | m³ |
| Boundary work | 36.36 | kJ |
| Change in internal energy | 151.2 | kJ |
| Heat transferred | 187.56 | kJ |

**Physical interpretation:**
- System expands by 0.1818 m³
- Steam does 36.36 kJ of work pushing the piston
- Only 151.2 kJ increases the internal energy (temperature rise)
- The remaining energy (36.36 kJ) goes into expansion work
- Total heat input needed: 187.56 kJ

---

## Question 3: Tricky Exam-Style Question

### Question
Two identical cylinders contain the same amount of ideal gas initially at the same state (1 atm, 300 K, 1 mole).

**Cylinder A:** Piston is free to move. Gas is heated slowly by 100 K.  
**Cylinder B:** Piston is locked. Gas is heated by the same amount (100 K).

**Which statement is correct?**

A) Both cylinders require the same heat input because they have the same initial and final internal energy changes.

B) Cylinder A requires MORE heat than B because it must do expansion work.

C) Cylinder B requires MORE heat than A, but work done on the gas is different.

D) Both cylinders have the same heat input and same work because the temperature change is identical.

**Show your calculations and explain why other options are wrong.**

---

### Answer

**Correct Answer: B**

### Detailed Explanation

#### Cylinder A: Constant Pressure (Free Piston)

**Process:** Isobaric (constant pressure at 1 atm)

**Given:**
- Initial state: P₁ = 1 atm, T₁ = 300 K, n = 1 mole
- Final state: P₂ = 1 atm, T₂ = 400 K
- External pressure: constant at 1 atm = 101,325 Pa

**Step 1: Find volumes**
$$V_1 = \frac{nRT_1}{P} = \frac{1 \times 8.314 \times 300}{101,325} = 0.0246 \text{ m}^3$$

$$V_2 = \frac{nRT_2}{P} = \frac{1 \times 8.314 \times 400}{101,325} = 0.0328 \text{ m}^3$$

**Step 2: Calculate work done BY gas**
$$W_A = P\Delta V = P(V_2 - V_1)$$
$$W_A = 101,325 \times (0.0328 - 0.0246) = 101,325 \times 0.0082 = 831.5 \text{ J} = 0.83 \text{ kJ}$$

Or using ideal gas relation:
$$W_A = nR\Delta T = 1 \times 8.314 \times 100 = 831.4 \text{ J}$$

**Step 3: Calculate internal energy change**
$$\Delta U_A = nC_v\Delta T$$

For diatomic gas (e.g., air): $C_v = \frac{5}{2}R = 20.785 \text{ J/(mol·K)}$

$$\Delta U_A = 1 \times 20.785 \times 100 = 2078.5 \text{ J} = 2.08 \text{ kJ}$$

**Step 4: Calculate heat (First Law)**
$$Q_A = \Delta U_A + W_A = 2.08 + 0.83 = 2.91 \text{ kJ}$$

Or using:
$$Q_A = nC_p\Delta T$$
where $C_p = C_v + R = 20.785 + 8.314 = 29.099 \text{ J/(mol·K)}$

$$Q_A = 1 \times 29.099 \times 100 = 2909.9 \text{ J} \approx 2.91 \text{ kJ}$$ ✓

---

#### Cylinder B: Constant Volume (Locked Piston)

**Process:** Isochoric (constant volume)

**Given:**
- Initial state: P₁ = 1 atm, T₁ = 300 K, n = 1 mole
- Final state: T₂ = 400 K, V = constant
- Volume: $V = 0.0246 \text{ m}^3$ (same as initial volume in A)

**Step 1: Work done**
$$W_B = 0 \text{ (no volume change)}$$

**Step 2: Internal energy change**
$$\Delta U_B = nC_v\Delta T = 1 \times 20.785 \times 100 = 2078.5 \text{ J} = 2.08 \text{ kJ}$$

(Same as Cylinder A because temperature change is identical)

**Step 3: Calculate heat (First Law)**
$$Q_B = \Delta U_B + W_B = 2.08 + 0 = 2.08 \text{ kJ}$$

Or:
$$Q_B = nC_v\Delta T = 1 \times 20.785 \times 100 = 2.08 \text{ kJ}$$

---

### Comparison

| Parameter | Cylinder A | Cylinder B | Difference |
|-----------|-----------|-----------|-----------|
| Process | Constant Pressure | Constant Volume |
| Pressure change | No | Yes (P increases) |
| Volume change | Yes | No |
| $\Delta U$ | 2.08 kJ | 2.08 kJ | Same |
| Work done | +0.83 kJ | 0 kJ | A does work |
| **Heat input** | **2.91 kJ** | **2.08 kJ** | **A needs MORE** |
| Ratio $Q_A/Q_B$ | 2.91/2.08 = 1.40 | — | = $C_p/C_v$ = 1.40 ✓ |

---

### Why Each Option is Wrong/Right

**Option A: ❌ WRONG**
- True that $\Delta U$ is the same in both cylinders
- BUT wrong that heat input is the same
- First Law: $Q = \Delta U + W$
- Cylinder A does work, so needs more heat

**Option B: ✓ CORRECT**
- Cylinder A requires MORE heat (2.91 kJ vs 2.08 kJ)
- Correct reason: A must do expansion work (0.83 kJ)
- Heat must provide both: energy rise + expansion work

**Option C: ❌ WRONG**
- Says "Cylinder B requires MORE heat" — this is backwards
- Work on gas is: 0 in A, but significant pressure work in B
- The statement is inverted

**Option D: ❌ WRONG**
- Heat input is NOT the same
- Work is NOT the same
- Only internal energy change is the same
- Temperature change alone doesn't determine heat input

---

### Key Insight

**The tricky part:** Students often think:
- "Both have same temperature change → same $\Delta U$ → same $Q$"

**The reality:**
- Same temperature change → same $\Delta U$ ✓
- BUT heat also depends on work done
- Process type matters! Different processes with same $\Delta T$ need different $Q$

$$Q_{\text{constant P}} = nC_p\Delta T > Q_{\text{constant V}} = nC_v\Delta T$$

Always because $C_p > C_v$ (expansion work added).

---

## Summary of Key Concepts Tested

| Question | Concept | Learning Outcome |
|----------|---------|------------------|
| Q1 | Constant P vs Constant V | Distinguish process types |
| Q2 | Real substance calculations | Apply steam tables and First Law |
| Q3 | Process comparison | Understand role of work in thermodynamics |

**Difficulty progression:** Conceptual → Applied → Analysis/Synthesis

**Time estimates:**
- Q1: 5-10 minutes (conceptual discussion)
- Q2: 15-20 minutes (calculation with reference data)
- Q3: 20-30 minutes (comparison and critical thinking)

---

## Study Tips

1. **For Q1-type questions:** Always distinguish between process constraints (P, V, T fixed)
2. **For Q2-type questions:** Be careful with unit conversions; always check if substance is single-phase
3. **For Q3-type questions:** Compare different processes systematically using First Law

Remember: $Q = \Delta U + W$ is your universal tool for all thermodynamic processes!
