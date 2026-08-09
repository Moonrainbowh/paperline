# Tables and Formulas

## Tables

Translate every human-readable table component:

- table title and caption;
- column and row headers;
- prose or categorical cell content;
- table notes, abbreviations, significance notes, and source notes.

Preserve:

- table number, row/column order, merged cells, spans, alignment roles, and header designation;
- all numeric values, signs, decimal precision, ranges, confidence intervals, units, sample sizes, and significance symbols;
- formulas, variable names, dataset/model identifiers, and citation attachment.

Do not convert a table into prose or rebuild it with a different geometry merely because English text is longer. Adjust wrapping and widths only after preserving the logical table. Run a cell-by-cell completeness check and visually inspect every rendered table.

## Formulas

Treat the mathematical expression as protected content. Preserve:

- variables, operators, functions, indices, superscripts, subscripts, matrices, arrays, delimiters, and alignment;
- equation numbering, labels, references, punctuation attachment, and display/inline status;
- Word OMML objects and LaTeX math environments.

Translate:

- equation titles and explanatory prose outside the equation;
- natural-language labels inside explicit text containers when their meaning is unambiguous;
- words such as boundary-condition labels only after terminology confirmation when they are domain-specific.

Do not translate conventional operators or identifiers merely because they resemble words. Do not flatten editable equations. For OCR-derived formulas, compare every symbol against the page image and require human approval.

## Minimum Audit

Before delivery, require:

- source and output table counts accounted for;
- source and output formula counts accounted for;
- unchanged numeric-token multiset unless the user approved a source correction;
- unchanged equation identifiers and cross-references;
- no omitted cell, caption, note, or equation-adjacent sentence;
- rendered visual review for every table and formula.
