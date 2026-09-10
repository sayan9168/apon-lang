#!/usr/bin/env python3
"""Apon Stage-0 bootstrap interpreter. See repository README."""
from __future__ import annotations
import math, os, sys
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

class AponError(Exception):
    def __init__(self, message: str, line: int = 0, col: int = 0, source: str = ""):
        self.message, self.line, self.col, self.source = message, line, col, source
        loc = f"{source}:{line}:{col}" if source else f"line {line}:{col}"
        super().__init__(f"{loc}: {message}")

class T(Enum):
    EOF=auto(); NEWLINE=auto(); INDENT=auto(); DEDENT=auto(); IDENT=auto(); NUMBER=auto(); STRING=auto()
    TRUE=auto(); FALSE=auto(); NIL=auto(); LET=auto(); FN=auto(); RETURN=auto(); IF=auto(); ELIF=auto(); ELSE=auto()
    WHILE=auto(); FOR=auto(); IN=auto(); BREAK=auto(); CONTINUE=auto(); AND=auto(); OR=auto(); NOT=auto()
    IMPORT=auto(); FROM=auto(); AS=auto(); PLUS=auto(); MINUS=auto(); STAR=auto(); SLASH=auto(); PERCENT=auto()
    EQ=auto(); EQEQ=auto(); NEQ=auto(); LT=auto(); GT=auto(); LTE=auto(); GTE=auto()
    LPAREN=auto(); RPAREN=auto(); LBRACK=auto(); RBRACK=auto(); LBRACE=auto(); RBRACE=auto(); COMMA=auto(); COLON=auto(); DOT=auto()

KEYWORDS = {"let":T.LET,"fn":T.FN,"return":T.RETURN,"if":T.IF,"elif":T.ELIF,"else":T.ELSE,"while":T.WHILE,"for":T.FOR,"in":T.IN,"break":T.BREAK,"continue":T.CONTINUE,"and":T.AND,"or":T.OR,"not":T.NOT,"true":T.TRUE,"false":T.FALSE,"nil":T.NIL,"import":T.IMPORT,"from":T.FROM,"as":T.AS}

@dataclass
class Token:
    kind: T; value: Any; line: int; col: int

class Lexer:
    def __init__(self, source: str, filename: str = "<stdin>"):
        self.source = source.replace("\r\n","\n").replace("\r","\n")
        if self.source and not self.source.endswith("\n"): self.source += "\n"
        self.filename=filename; self.i=0; self.line=1; self.col=1; self.indent_stack=[0]; self.at_line_start=True; self.pending=[]
    def peek(self, n=0):
        j=self.i+n; return self.source[j] if j < len(self.source) else ""
    def advance(self):
        if self.i>=len(self.source): return ""
        ch=self.source[self.i]; self.i+=1
        if ch=="\n": self.line+=1; self.col=1
        else: self.col+=1
        return ch
    def error(self, msg): raise AponError(msg, self.line, self.col, self.filename)
    def skip_spaces_and_comments(self):
        while True:
            chs=self.peek()
            while chs and chs in " \t": self.advance(); chs=self.peek()
            if self.peek()=="#":
                while self.peek() and self.peek()!="\n": self.advance()
            else: break
    def handle_indent(self):
        spaces=0; chs=self.peek()
        while chs and chs in " \t":
            if chs=="\t": self.error("tabs are not allowed; use 4 spaces")
            spaces+=1; self.advance(); chs=self.peek()
        if self.peek() in ("#","\n",""): return
        current=self.indent_stack[-1]
        if spaces==current: return
        if spaces>current:
            self.indent_stack.append(spaces); self.pending.append(Token(T.INDENT, spaces, self.line, 1)); return
        while spaces < self.indent_stack[-1]:
            self.indent_stack.pop(); self.pending.append(Token(T.DEDENT, spaces, self.line, 1))
        if spaces != self.indent_stack[-1]: self.error("inconsistent indentation")
    def string(self):
        quote=self.advance(); line,col=self.line,self.col-1; chars=[]
        while True:
            ch=self.peek()
            if ch=="": self.error("unterminated string")
            if ch==quote: self.advance(); break
            if ch=="\\":
                self.advance(); esc=self.peek()
                mapping={"n":"\n","t":"\t","r":"\r","\\":"\\","\"":"\"","'":"'"}
                chars.append(mapping[esc] if esc in mapping else self.advance())
                if esc in mapping: self.advance()
            else: chars.append(self.advance())
        return Token(T.STRING, "".join(chars), line, col)
    def number(self):
        line,col=self.line,self.col; raw=""
        while self.peek().isdigit() or self.peek()==".": raw += self.advance()
        if raw.count(".")>1: self.error(f"invalid number {raw}")
        value=float(raw) if "." in raw else int(raw)
        return Token(T.NUMBER, value, line, col)
    def ident(self):
        line,col=self.line,self.col; raw=""
        while self.peek().isalnum() or self.peek()=="_": raw += self.advance()
        kind=KEYWORDS.get(raw, T.IDENT); value=raw
        if kind is T.TRUE: value=True
        elif kind is T.FALSE: value=False
        elif kind is T.NIL: value=None
        return Token(kind, value, line, col)
    def next_token(self):
        if self.pending: return self.pending.pop(0)
        if self.at_line_start:
            self.at_line_start=False; self.handle_indent()
            if self.pending: return self.pending.pop(0)
        self.skip_spaces_and_comments(); ch=self.peek()
        if ch=="":
            while len(self.indent_stack)>1:
                self.indent_stack.pop(); self.pending.append(Token(T.DEDENT, 0, self.line, self.col))
            self.pending.append(Token(T.EOF, None, self.line, self.col)); return self.pending.pop(0)
        if ch=="\n":
            tok=Token(T.NEWLINE, "\n", self.line, self.col); self.advance(); self.at_line_start=True; return tok
        line,col=self.line,self.col; two=ch+self.peek(1)
        if two=="==": self.advance(); self.advance(); return Token(T.EQEQ, two, line, col)
        if two=="!=": self.advance(); self.advance(); return Token(T.NEQ, two, line, col)
        if two=="<=": self.advance(); self.advance(); return Token(T.LTE, two, line, col)
        if two==">=": self.advance(); self.advance(); return Token(T.GTE, two, line, col)
        singles={"+" :T.PLUS,"-":T.MINUS,"*":T.STAR,"/":T.SLASH,"%":T.PERCENT,"=":T.EQ,"<":T.LT,">":T.GT,"(":T.LPAREN,")":T.RPAREN,"[":T.LBRACK,"]":T.RBRACK,"{":T.LBRACE,"}":T.RBRACE,",":T.COMMA,":":T.COLON,".":T.DOT}
        if ch in singles: self.advance(); return Token(singles[ch], ch, line, col)
        if ch in "\"'": return self.string()
        if ch.isdigit(): return self.number()
        if ch.isalpha() or ch=="_": return self.ident()
        self.error(f"unexpected character {ch!r}"); raise AssertionError
    def tokenize(self):
        tokens=[]
        while True:
            tok=self.next_token(); tokens.append(tok)
            if tok.kind is T.EOF: break
        return tokens
