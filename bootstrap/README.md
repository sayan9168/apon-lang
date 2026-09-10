# Stage-0 bootstrap

`apon.py` is the host-language seed: lexer, parser, and tree-walk interpreter.

```bash
python3 bootstrap/apon.py ../examples/hello.apon
python3 bootstrap/apon.py --repl
```

The complete interpreter lives in this folder. After Stage-0 can run `.apon` files, new work happens in `../src/` written in Apon itself.
