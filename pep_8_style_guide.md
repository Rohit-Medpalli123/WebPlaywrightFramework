# PEP 8 – Style Guide for Python Code

> This document follows the official [PEP 8](https://peps.python.org/pep-0008/) Python style guide. Use these rules when writing or reviewing Python code.

---

## General Guidelines

- Write clean, readable, and consistent code.
- Code should be understandable to someone else reading it later.

## File & Encoding

- Use UTF-8 encoding.
- Files should end with a newline.

## Indentation

- Use **4 spaces per indentation level**.
- Never use tabs. Use spaces consistently.

## Line Length

- Limit all lines to a **maximum of 79 characters**.
- For docstrings/comments, limit lines to **72 characters**.

## Blank Lines

- Use **2 blank lines** between top-level functions and class definitions.
- Use **1 blank line** between methods within a class.
- Avoid multiple blank lines in a row.

## Imports

- Imports should be on separate lines:
  ```python
  import os
  import sys
  ```
- Use absolute imports when possible.
- Group imports in the following order:
  1. Standard library
  2. Third-party packages
  3. Local application imports
  Add a **blank line between groups**.

## Naming Conventions

- **Variables, functions, methods**: `lower_case_with_underscores`
- **Classes**: `CapWords`
- **Constants**: `ALL_CAPS_WITH_UNDERSCORES`
- **Private members**: start with `_` (e.g. `_internal`)
- Avoid single-character names except in small scopes (`i`, `j`, `k` in loops).

## Whitespace Rules

- No spaces inside parentheses, brackets, or braces:
  ```python
  correct = my_function(a, b)
  wrong = my_function( a, b )
  ```
- Use 1 space after `,`, `:`, `;` — but **no space before**.
- No space before parentheses when calling functions:
  ```python
  correct = foo(42)
  wrong = foo (42)
  ```
- Avoid extra spaces around `=`, `==`, etc. unless aligning multiple assignments:
  ```python
  x = 1
  y = 2
  ```

## Comments

- Comments should be **complete sentences**, capitalized.
- Block comments: use `#` followed by a space and the comment.
- Inline comments: place after at least **2 spaces** from code.
- Update comments if the code changes.

## Docstrings

- Use **triple double quotes** for docstrings (`"""Example"""`).
- All public modules, functions, classes, and methods **must** have docstrings.
- Follow [PEP 257](https://peps.python.org/pep-0257/) conventions.

## Function and Class Definitions

- Use a single blank line before function/class inside a class.
- No space between function name and parentheses:
  ```python
  def my_function(x):
      pass
  ```

## Other Best Practices

- Don’t compare boolean values to `True` or `False`:
  ```python
  if is_valid:  # not if is_valid == True
  ```
- Use `is` or `is not` for `None` comparisons:
  ```python
  if x is None:
  ```
- Avoid using backslash `\` for line continuation. Prefer parentheses.
- Avoid using `from module import *`.

