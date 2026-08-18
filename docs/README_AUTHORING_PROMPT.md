# README documentation authoring prompt

Use the root `README.md` as the canonical source for renderer-sensitive Markdown/HTML structure. When editing or translating documentation, preserve these rules exactly:

1. **Ordered-list items that contain inline HTML (especially `<img>` tags) must remain on one physical source line.** Do not split the list-item text, `<br />`, image tag, continuation text, or spacing helpers across source lines. HACS/Home Assistant Markdown rendering can lose the image or break the list when these fragments are separated.
2. **Never emit two consecutive `<br />` tags.** When two visual line breaks are required, use `<br />&nbsp;<br />`. The non-breaking space is an intentional renderer workaround and must not be removed as “cleanup”.
3. **Treat `<br />` placement as layout logic, not cosmetic formatting.** Preserve the exact number and position of `<br />` and `&nbsp;` tokens from the canonical root README. Do not prettify, wrap, reflow, normalize, or convert these renderer-sensitive lines.
4. **For localized README files, translate only human-readable text.** Keep list numbering, inline HTML structure, image URLs, image widths, `<br />` positions, `&nbsp;`, anchors, and other technical tokens structurally identical to the root README unless a deliberate renderer fix is being made.
5. **When an image belongs to a numbered-list step, keep the image inside the same list-item source line.** Do not move it to a standalone Markdown paragraph merely for readability.
6. **Use absolute image URLs for README images rendered by HACS.** Preserve the existing `raw.githubusercontent.com` URLs and explicit pixel widths where present.
7. Before committing documentation changes, compare the affected renderer-sensitive list items against the root README character-for-character for HTML/layout tokens, and verify that no `<br /><br />` sequence was introduced.

Current canonical pattern for the two brightness-mode steps is intentionally shaped like this:

```md
5. ...<br /><img ... /><br />...<br />&nbsp;
6. ...<br /><img ... /><br />&nbsp;<br />
7. ...
```

Do not simplify this structure even if another Markdown renderer appears to accept a cleaner form.
