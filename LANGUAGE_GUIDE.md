# E++ Language Official Documentation

Welcome to **E++**, a Turing-complete programming language designed to be read and written like plain English. This document provides a complete guide to the language's philosophy, grammar, and usage.

---

## 🏛 Philosophy

E++ is built on the idea that code should be as accessible as a written recipe. By removing all mathematical symbols, brackets, and cryptic punctuation, E++ allows anyone with a basic grasp of English to understand exactly what a program is doing. It is a "Literal Instruction Language."

---

## 📜 Core Rules and Syntax

Every line of E++ code must end with a **period (.)**. Commas (,) are ignored by the parser and can be used for natural readability.

### 1. Variables and Assignment
Variables are declared using phrases like `let` and `be`, or simply `let` and `=`. Reassignment uses `set` and `to`, or `set` and `=`.
- **Declaration:** `let age be 25.` or `let age = 25.`
- **Reassignment:** `set age to age plus 1.` or `set age = age + 1.`
- **Input Storage:** `ask "Name?" and store it in user name.`

### 2. Arithmetic and Logic
E++ uses English words for all operations by default, but it **also fully supports standard programming symbols**. You can mix and match them!
- **Math:** `plus` (`+`), `minus` (`-`), `times` (`*`), `divided by` (`/`), `modulo` (`%`)
- **Logic:** `and` (`&&`), `or` (`||`), `not` (`!`)
- **Comparisons:** `equals` (`==`), `is` (`==`), `is not` (`!=`), `is greater than` (`>`), `is less than` (`<`), `is at least` (`>=`), `is at most` (`<=`)

### 3. Input and Output
- **Output:** `say "Hello world."` or `display result.`
- **Input:** `ask "Prompt string" and store it in variable.`

### 4. Conditionals
Blocks start with `if`, `else if`, or `else`, and must end with `end if`.
```text
if score is at least 90.
    say "Grade: A".
else.
    say "Keep trying!".
end if.
```

### 5. Loops
Two primary loop types are supported:
- **Condition-based:** `while [condition]. ... end while.`
- **Count-based:** `repeat [number] times. ... end repeat.`
- **Early Exit:** `break out` or `stop`.

### 6. Functions
Functions are modular and reusable.
```text
define greeting, accepting name.
    say "Hello, " plus name.
end define.

call greeting with "Alice".
```

### 7. Collections (Lists)
E++ supports dynamic lists.
- **Creation:** `let inventory be a new list.`
- **Adding:** `add "sword" to inventory.`
- **Removing:** `remove "shield" from inventory.`
- **Access:** `say item 1 of inventory.`
- **Size:** `say the size of inventory.`

### 8. Error Handling
Protect your code against crashes using the `attempt` block.
```text
attempt.
    let x be 10 divided by 0.
if it fails.
    say "Mathematical error caught.".
end attempt.
```

---

## 🛠 Running E++ Code

E++ is currently implemented as a **Python Transpiler**. To run E++ code, you use the `epp.py` script.

### Installation
Ensure you have Python 3 installed on your system.

### Execution
Save your E++ code with a `.epp` extension and run:
```bash
python epp.py your_program.epp
```
This will:
1. Parse your English instructions.
2. Generate a corresponding `.py` file.
3. Execute the code and display the output in your terminal.

---

## 🚀 Examples

### FizzBuzz
```text
let number be 1.
while number is at most 20.
    if number modulo 15 equals 0.
        say "FizzBuzz".
    else if number modulo 3 equals 0.
        say "Fizz".
    else if number modulo 5 equals 0.
        say "Buzz".
    else.
        say number.
    end if.
    set number to number plus 1.
end while.
```

### Recursive Factorial
```text
define factorial, accepting n.
    if n is at most 1.
        return 1.
    end if.
    let smaller be n minus 1.
    let sub result be call factorial with smaller.
    return n times sub result.
end define.

let result be call factorial with 5.
say result.
```

---

## 🔍 How It Works (The Parser)

E++ resolves English ambiguity using a **Longest Match** rule.
- It looks for the longest known keyword first (e.g., `is greater than` is identified before `is`).
- It extracts **Identifiers** (variable/function names) by looking at the text between structural keywords. This allows multi-word variable names like `user account balance`.
- The period `.` acts as the absolute separator for instructions, preventing "run-on" code confusion.

---
*Developed by the E++ Language Committee.*
