# DOCX Workflow

## Input and Output

Preserve the source DOCX and write `<stem>-en.docx`. Use the host document runtime and its bundled Word/OOXML tools; do not depend on a system Python or global package installation.

## Preflight

Inventory body paragraphs, styles, tables, merged cells, headers, footers, footnotes, endnotes, captions, fields, hyperlinks, comments, tracked changes, content controls, text boxes, media, and OMML equations. Pause when tracked changes or comments make the authoritative visible text ambiguous.

## Translate

- visible paragraph and run text while preserving paragraph order and styles;
- table headers, cells, and notes without altering table geometry or merged cells;
- captions, footnotes, endnotes, headers, footers, text boxes, and accessible text that belongs to manuscript prose;
- natural-language text explicitly contained in equation text nodes when it can be separated safely.

Do not translate text inside embedded images. Preserve image bytes, crop, size, position, relationship IDs, and captions as separate objects.

## Protect OOXML

- Preserve OMML equation trees; never flatten equations to plain text or raster images.
- Preserve field instructions, bookmarks, `SEQ`/`REF` relationships, hyperlinks, comments plumbing, numbering definitions, styles, sections, page geometry, and relationship parts.
- Preserve run-level scientific formatting such as italic variables, bold vectors/matrices, subscripts, superscripts, and symbols.
- Do not replace a whole paragraph with one unformatted run when the paragraph contains mixed formatting, fields, links, equations, drawings, or revision markup.

## Required QA

1. Compare source/output structural inventories.
2. Reopen the written DOCX and confirm it is not corrupt.
3. Render the final DOCX to page PNGs using the host document renderer.
4. Inspect every page at 100% zoom for clipping, reflow defects, broken tables, displaced figures, missing equations, glyph failures, and header/footer drift.
5. Re-render after every layout-sensitive repair.

The output may have a different page count because English reflows differently, but section order, paragraph order, table count, equation count, image count, and cross-reference structure must remain accounted for.
