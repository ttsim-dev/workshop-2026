---
theme: academic
class: text-center
highlighter: shiki
lineNumbers: false
info: |
  GETTSIM Workshop 2026 — Stage 1, the policy environment
drawings:
  persist: false
transition: fade
title: Stage 1 — The Policy Environment
mdc: true
defaults:
  layout: center
---

# Stage 1 — The Policy Environment

### Review the policy env's status quo, implement the reform

---

# Where You Are

<div class="pipeline">
  <div class="stage on">
    <div class="box">gettsim</div>
    <div class="what">the law</div>
  </div>
  <div class="arrow">→</div>
  <div class="stage">
    <div class="box">gettsim-personas</div>
    <div class="what">one household</div>
  </div>
  <div class="arrow">→</div>
  <div class="stage">
    <div class="box">soep-preparation</div>
    <div class="what">real households</div>
  </div>
</div>

<br/>

---

# The Policy Environment

GETTSIM's **policy environment** collects

- policy functions,
- parameters, and
- parameter functions

for a given **policy date**. 

It is fully customizable: you can change any parameter or function, and see what
happens.

---

# The Policy Environment Is a Tree

The policy environment is an ordinary nested dictionary of python objects:

- Each object belongs to a **namespace**
- You can add new paths to this tree, or change existing tree objects

You can see how to manipulate the policy environment in the tutorial (How to Guides ->
Taxes & Transfers Objects and Modifications of the Policy Environment)


---

# Suggested Workflow

1. Look at the implementation of the current law in your local clone of GETTSIM. Find
   out which parameters you need to change.
1. Create some input data. Pass it to GETTSIM using the status quo environment. Get
   familiar with how the output looks like.
1. Call `gettsim.main` with the policy environment as target.
1. Create the new functions and parameters. Add them to the policy environment you got
   in the last step.
1. Use the input data from the second step and pass it to `gettsim.main`, this time with
   the modified policy environment.

---
layout: default
---

# Task

**Until 14:45 — the status quo**

1. Open `cp notebooks/01_policy_environment.ipynb`
2. Find your namespace in `sorted(status_quo)`. Print its parameters and functions.
3. Which leaf is your reform? Read it. `type()` it.
4. Use some fake input data to get tax/transfer results.

<br/>

**15:30–16:30 — the reform**

5. `copy_environment`, change the leaf, run again.
6. Keep both environments around. Tomorrow picks them up.

<br/>

Stuck? Ask Hans-Martin or me.

