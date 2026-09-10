# Apon

**Apon** (আপন — “one’s own”) is a small programming language with its own syntax, lexer, parser, runtime, and standard library.

Easy to read. Indentation-based. Designed to grow into a self-hosted language.

```apon
fn greet(name):
    print("Namaskar,", name)

greet("Sayan")
```

## Why a host seed exists

A language cannot be born already written in itself. That is the compiler bootstrap problem.

1. **Stage 0** — `bootstrap/apon.py` (Python seed). The only non-Apon code.
2. **Stage 1** — Apon programs run on Stage 0 (`examples/`, `src/`).
3. **Stage 2** — Rewrite lexer / parser / evaluator in Apon (`src/selfhost_demo.apon` is the first seed).
4. **Stage 3** — Use the Apon implementation to run Apon. Then the Python seed is optional.

This is how every serious self-hosted language starts (C, Go, Rust, Python’s early days).

## Quick start

Requires Python 3.9+.

```bash
git clone https://github.com/sayan9168/apon-lang.git
cd apon-lang

python3 bootstrap/apon.py examples/hello.apon
python3 bootstrap/apon.py examples/fib.apon
python3 bootstrap/apon.py examples/control.apon
python3 bootstrap/apon.py src/selfhost_demo.apon

python3 bootstrap/apon.py --repl
```

Windows:

```bat
py bootstrap\apon.py examples\hello.apon
```

## Repository layout

```
bootstrap/apon.py      Stage-0 interpreter (lexer + parser + runtime)
src/                   Apon-in-Apon sources
std/core.apon          Standard library written in Apon
examples/              Sample programs
docs/LANGUAGE.md       Language spec
bin/apon               Convenience launcher
```

## Syntax snapshot

```apon
let n = 10
let words = ["apon", "language"]
let person = {"name": "Apon", "age": 1}

fn add(a, b):
    return a + b

if n > 5:
    print("big", add(n, 1))
else:
    print("small")

for i in range(3):
    print(i)
```

## Features in v0.1

- Own lexer (indent / dedent tokens)
- Own recursive-descent parser
- Own AST and tree-walk interpreter
- Functions, closures (functions capture environment)
- `if / elif / else`, `while`, `for`, `break`, `continue`
- Lists and maps
- String + number operators
- Built-in library
- REPL
- Line/column errors

## Next steps for true self-hosting

1. Port the lexer in `bootstrap/apon.py` to Apon (`src/lexer.apon`).
2. Port the parser to Apon.
3. Port the evaluator to Apon.
4. Run those files with Stage 0.
5. Freeze a Stage-1 binary / script that no longer needs new Python features.

## License

MIT — see `LICENSE`.
