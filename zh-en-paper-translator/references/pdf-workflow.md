# PDF Workflow

## Required Deliverables

For `source.pdf`, deliver both:

- `source-en.docx` as the editable authoritative translation;
- `source-en.pdf` rendered from the editable translation.

Do not promise pixel-identical or line-identical pagination. English length changes require controlled reflow. Preserve the source PDF unchanged.

## Classify the PDF

- **Born-digital:** reliable selectable text with a plausible reading order.
- **Scanned:** image-only or insufficient text layer; use OCR.
- **Hybrid:** mixed text pages, scanned pages, or rasterized tables/equations; handle per page.

Use text extraction for content recovery, not layout fidelity. Render every source page to inspect columns, tables, equations, footnotes, and reading order before translation.

## Born-Digital Route

1. Extract text blocks and page geometry.
2. Reconstruct reading order using the rendered pages, not extraction order alone.
3. Rebuild an editable DOCX with the same logical section, paragraph, table, caption, equation, and figure sequence.
4. Preserve embedded figures unchanged; do not translate image-internal text.
5. Render the DOCX to PDF and inspect every final page.

## Scanned or Hybrid Route

1. Render pages at sufficient resolution and OCR only manuscript text and tables.
2. Exclude figure-internal text from the translation scope.
3. Treat every OCR-derived number, unit, citation, table cell, symbol, and equation as unverified until checked against the page image.
4. Reconstruct equations manually or preserve a verified equation crop unchanged when safe reconstruction is impossible; disclose any non-editable equation.
5. Require human review of OCR-derived prose, every table, and every formula before calling the translation final.

## Required QA

- Inventory source and outputs separately; cross-format counts are diagnostic, not directly equal.
- Confirm every source page and content block is accounted for in the editable DOCX.
- Confirm table rows/columns, equation numbering, figure order, captions, footnotes, citations, and references.
- Render `source-en.pdf` to PNG and inspect every page at 100% zoom.
- Reject output with clipped text, overlap, missing glyphs, unreadable formulas, broken tables, or an unexplained omitted block.
