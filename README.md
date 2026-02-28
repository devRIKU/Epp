# E++ Programming Language

**E++** is a playful, English‑like programming language designed to be easy to read and write. It comes with its own interpreter, a REPL, and a collection of sample programs demonstrating language features such as variables, control flow, functions, and pseudo‑code constructs.

---

## 🚀 Quick Start (One-liner)

The fastest way to install E++ and its native `epp` command is using [uv](https://astral.sh/uv):

```bash
uv tool install git+https://github.com/devRIKU/Epp.git
```

This will automatically handle the environment and install the `epp` command to your system path.

---

## 📦 Manual Installation

If you prefer to install it manually using `pip`:

```bash
# Clone the repository
git clone https://github.com/devRIKU/Epp.git
cd Epp

# Install the package (editable mode recommended for development)
python -m pip install -e .
```

---

## 🎮 Usage

Once installed, you can launch the interactive REPL by just typing:

```bash
epp
```

Or execute a specific E++ file directly:

```bash
epp hello_world.epp
```

---

## 📂 Project Structure

- `epp_interpreter.py` – Core interpreter that parses and executes E++ source files.
- `epp_ui.py` – Simple UI utilities for running E++ programs in a browser‑like window.
- `epp.py` – Entry‑point script that launches the REPL.
- `setup.py` – Package metadata for installing the language and defining the `epp` command.
- `*.epp` files – Example programs (e.g., `hello_world.epp`, `fizzbuzz.epp`, `pseudo_demo.epp`).
- `LANGUAGE_GUIDE.md` – Language specification and grammar.
- `REFERENCE_GUIDE.md` – Reference documentation for built‑in functions and keywords.

---

## ✨ Features

- **English‑like syntax** – Write code that reads like natural language.
- **Pseudo‑code support** – Keywords such as `DECLARE`, `PRINT`, `IF/THEN/ELSE`, `FOR/TO/STEP`, `WHILE`, `SWITCH/CASE`.
- **REPL** – Interactive prompt for rapid experimentation.
- **Cross‑platform UI** – Minimal UI built on Tkinter for quick demos.
- **Extensible** – Easy to add new keywords or built‑in functions.

---

## 📚 Documentation

Detailed documentation is available in our **[Official Wiki](https://github.com/devRIKU/Epp/wiki)**:
- **[Home](https://github.com/devRIKU/Epp/wiki/Home)** – Overview and Quick Start.
- **[Language Guide](https://github.com/devRIKU/Epp/wiki/Language-Guide)** – Philosophy and Core Syntax.
- **[Full Reference](https://github.com/devRIKU/Epp/wiki/Full-Reference)** – Complete Keyword List.
- **[Pseudo-Code Support](https://github.com/devRIKU/Epp/wiki/Pseudo-Code)** – For algorithmic writing.
- **[Examples](https://github.com/devRIKU/Epp/wiki/Examples)** – Ready-to-run E++ scripts.

You can also find raw guides in the repository:
- `LANGUAGE_GUIDE.md` – Full language specification.
- `REFERENCE_GUIDE.md` – Detailed reference for all built‑in commands.
- Inline comments in the source files provide additional context.

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests. Please follow the existing code style and update the documentation when adding new features.

---

## 📜 License

This project is licensed under the MIT License – see the `LICENSE` file for details.
