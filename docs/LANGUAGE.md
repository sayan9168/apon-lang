# Apon language specification (v0.1)

Apon is an indentation-based dynamic language. Files use the `.apon` extension.

## Tokens

- Identifiers: `[A-Za-z_][A-Za-z0-9_]*`
- Integers and floats
- Strings in `"..."` or `'...'` with `\n \t \r \\ \" \'`
- Comments: `#` to end of line
- Indentation: **4 spaces**. Tabs are errors.

## Keywords

`let fn return if elif else while for in break continue and or not true false nil import from as`

## Types

`nil`, `bool`, `int`, `float`, `str`, `list`, `map`, `fn`

## Statements

```
let name = expr

fn name(a, b):
    body
    return expr

if cond:
    body
elif cond:
    body
else:
    body

while cond:
    body

for x in expr:
    body

name = expr
list[i] = expr
map[key] = expr
```

## Expressions

Precedence (high to low): postfix `() [] .` → unary `+ - not` → `* / %` → `+ -` → comparisons → `and` → `or`

Lists: `[1, 2, 3]`
Maps: `{"a": 1, "b": 2}`

## Builtins

`print len str int float range type push pop keys values has read write abs min max sqrt floor ceil join split upper lower`

## Bootstrap truth

A brand-new language cannot start written only in itself. Stage-0 lives in `bootstrap/apon.py`. After Stage-0 runs `.apon` files, the language is developed in Apon (`src/`). That is the standard self-hosting path used by C, Go, Rust, and others.
