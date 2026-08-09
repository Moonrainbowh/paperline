# LaTeX Workflow

## Input and Output

Read the manuscript's source tree and write translated sources without overwriting the original. For a single file, write `<stem>-en.tex`. For a multi-file project, mirror the source tree under a separate `*-en` directory and keep relative paths stable.

## Translate

- document title, abstract, headings, prose, list items, table text, captions, footnotes, and acknowledgements;
- natural-language macro arguments only when the macro's semantic role is known;
- natural-language content inside `\text{...}`, `\mathrm{...}`, or similar formula containers only when it is a label or explanation rather than a mathematical identifier.

## Protect

- command names, environment names, braces, options, comments used as build directives, and preamble logic;
- `\label`, `\ref`, `\pageref`, `\eqref`, `\cite`, bibliography keys, paths, URLs, DOI, and identifiers;
- equation operators, variables, indices, arrays, alignment points, numbering, and delimiters;
- `verbatim`, `lstlisting`, `minted`, and code-like environments;
- `\includegraphics` files and image-internal text.

Do not translate the contents of an unknown macro until its definition and role are inspected. Preserve source encoding and line endings when practical.

## Required QA

1. Compare heading, table, equation, image, label, reference, and citation inventories.
2. Compile the translated source with the project's existing build route.
3. Treat undefined control sequences, missing labels, citation failures, overfull boxes, and font/glyph failures as blockers.
4. Render the compiled PDF and inspect every page, especially equations, tables, floats, captions, and page breaks.
