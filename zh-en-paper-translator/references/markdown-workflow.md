# Markdown Workflow

## Input and Output

Read UTF-8 or UTF-8-with-BOM Markdown and write UTF-8 `<stem>-en.md`. Preserve the original newline convention when practical.

## Translate

- YAML frontmatter values that are natural-language title, abstract, description, or keywords fields;
- headings, paragraphs, blockquotes, list items, table text, captions, footnotes, and visible link labels;
- natural-language content in explicitly textual math constructs only when its boundary is clear.

## Protect

- frontmatter keys and machine-readable identifiers;
- fenced and indented code blocks, inline code, HTML tags, link destinations, anchors, and reference IDs;
- Markdown table separators and alignment markers;
- math delimiters and mathematical content;
- image syntax and image paths; do not translate image-internal text;
- citation keys and bibliography identifiers.

Keep the same heading count and order, paragraph order, table geometry, image count, links, footnotes, and math-block count. Do not wrap translated prose in a second Markdown code fence.

Run both translation and structure audits. Inspect the rendered Markdown when the host environment provides a renderer, especially tables, equations, and nested lists.
