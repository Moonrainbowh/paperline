# File-Format Routing

## Output Contract

| Source | Required output | Editable companion | Layout authority |
| --- | --- | --- | --- |
| Markdown `.md` | `<stem>-en.md` | Same file | Markdown structure and source diff |
| Word `.docx` | `<stem>-en.docx` | Same file | Original DOCX plus rendered-page comparison |
| LaTeX `.tex` | `<stem>-en.tex` | Same file | LaTeX source plus compiled PDF comparison |
| PDF `.pdf` | `<stem>-en.pdf` | `<stem>-en.docx` | Editable DOCX plus final rendered PDF |

Never overwrite the source. Keep temporary extraction, OCR, render, and segment files outside the deliverable folder.

## Common Content Scope

Translate:

- titles, headings, body paragraphs, list items, callouts, and appendices;
- table headers, cell prose, table notes, captions, and source notes;
- figure captions and figure notes outside the image object;
- footnotes, endnotes, headers, and footers containing manuscript prose;
- natural-language labels or explanations attached to formulas;
- supplementary text.

Preserve without translation:

- text embedded inside figures or other image pixels;
- mathematical symbols, variables, operators, indices, and equation structure;
- citation keys, bookmarks, labels, field codes, URLs, DOI, and file paths;
- numbers, signs, ranges, units, statistical symbols, and identifiers;
- bibliography metadata unless an official author/publisher English title is available and the task explicitly includes reference-title translation.

## Required Passes

1. Inventory the source before translation.
2. Extract or segment translatable text without destroying container structure.
3. Translate using the terminology ledger and section rules.
4. Write a new output container in the required format.
5. Run semantic and structure audits.
6. Render DOCX, PDF, or compiled LaTeX output and inspect every page.
7. Deliver the final artifact(s), terminology ledger, and only material warnings.

Use `scripts/audit_document_structure.py --input <file>` for the source inventory and `--source <source> --translation <output>` for same-format comparison. For PDF plus DOCX, inventory the two files separately because cross-format counts are not directly comparable.
