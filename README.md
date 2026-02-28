# E++ Programming Language

**E++** is a playful, English‑like programming language designed to be easy to read and write. It comes with its own interpreter, a REPL, and a collection of sample programs demonstrating language features such as variables, control flow, functions, and pseudo‑code constructs.

---

## 📦 Project Structure

- `epp_interpreter.py` – Core interpreter that parses and executes E++ source files.
- `epp_ui.py` – Simple UI utilities for running E++ programs in a browser‑like window.
- `epp.py` – Entry‑point script that launches the REPL.
- `setup.py` – Package metadata for installing the language as a Python package.
- `*.epp` files – Example programs (e.g., `hello_world.epp`, `fizzbuzz.epp`, `pseudo_demo.epp`).
- `LANGUAGE_GUIDE.md` – Language specification and grammar.
- `REFERENCE_GUIDE.md` – Reference documentation for built‑in functions and keywords.

---

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/yourusername/epp.git
cd epp

# Install the package (editable mode)
python -m pip install -e .

# Run the REPL
python epp.py
```

You can also execute a specific E++ file directly:

```bash
python epp.py path/to/your_program.epp
```

---

## ✨ Features

- **English‑like syntax** – Write code that reads like natural language.
- **Pseudo‑code support** – Keywords such as `DECLARE`, `PRINT`, `IF/THEN/ELSE`, `FOR/TO/STEP`, `WHILE`, `SWITCH/CASE`.
- **REPL** – Interactive prompt for rapid experimentation.
- **Cross‑platform UI** – Minimal UI built on Tkinter for quick demos.
- **Extensible** – Easy to add new keywords or built‑in functions.

---

## 📚 Documentation

- `LANGUAGE_GUIDE.md` – Full language specification.
- `REFERENCE_GUIDE.md` – Detailed reference for all built‑in commands.
- Inline comments in the source files provide additional context.

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests. Please follow the existing code style and update the documentation when adding new features.

---

## 📜 License

This project is licensed under the MIT License – see the `LICENSE` file for details.
