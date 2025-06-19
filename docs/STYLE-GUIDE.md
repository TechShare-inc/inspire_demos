# TechShare Document Style Guide

This repository contains styling and templates for creating consistent technical documentation for TechShare Inc.

## Features

- Responsive styling for both web and print formats
- Automatic page numbering in PDFs
- Document footers with document name and company logo
- Styled table of contents page
- Auto-generated in-page table of contents
- Special styling for Japanese text
- Tokyo theme option for dark mode
- Print optimization with page breaks and margins
- Copyright notice styling

## How to Use

### Adding the Footer

Every document should have a footer with the document name and company logo. Add the following HTML at the end of your Markdown file:

```html
<!-- Footer -->
<div class="footer">
    <div class="footer-doc-name">Document Name</div>
    <img class="footer-logo" src="../../style/TechShare_logo.svg" alt="TechShare Logo">
</div>

<script>
    // Update document name in footer
    document.addEventListener('DOMContentLoaded', function() {
        const docPath = window.location.pathname;
        const docName = docPath.split('/').pop().replace('.md', '');
        const docNameElement = document.querySelector('.footer-doc-name');
        if (docNameElement) {
            docNameElement.textContent = docName.replace('_', ' ');
        }
    });
</script>
```

### Creating a Table of Contents Page

To create a styled table of contents page at the beginning of your document:

```html
<div class="toc-page" data-date="">
    <h1 class="toc-page-title">Contents</h1>
    <div class="toc">
        <div class="toc-title">Table of Contents</div>
        <div id="generated-toc"></div>
    </div>
</div>

<div class="page-break"></div>

<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Set current date
        const tocPageElement = document.querySelector('.toc-page');
        if (tocPageElement) {
            const today = new Date();
            const dateString = today.toLocaleDateString();
            tocPageElement.setAttribute('data-date', dateString);
        }
        
        // Generate TOC
        const headings = document.querySelectorAll('h2, h3, h4');
        const tocContainer = document.getElementById('generated-toc');
        if (tocContainer) {
            const toc = document.createElement('ul');
            // TOC generation code...
            tocContainer.appendChild(toc);
        }
    });
</script>
```

### Converting to PDF

Use the provided PowerShell script to convert Markdown files to PDF:

```powershell
.\Convert-MarkdownToPDF.ps1
```

Requirements:
- [Pandoc](https://pandoc.org/installing.html)
- [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)

## CSS Classes

### Base Styling
- General typography, margins, and colors
- Headers (h1-h6) with proper spacing and color
- Links, code blocks, blockquotes, tables, lists, images

### Special Elements
- `.copyright` - Styled copyright notice
- `.toc` - Table of contents container
- `.toc-title` - Title for table of contents
- `.toc-page` - Full-page table of contents
- `.toc-page-title` - Title for the TOC page
- `.page-break` - Forces a page break in PDF output
- `.footer` - Document footer
- `.footer-doc-name` - Document name in footer
- `.footer-logo` - Logo in footer

### Language-Specific
- `.jp` - Japanese text styling with appropriate fonts
- `.tokyo-theme` - Dark mode styling inspired by VS Code Tokyo Night theme

## Examples

See the `docs` directory for example documents that use these styles.

## Best Practices

1. Always include the CSS stylesheet link at the top of your document:
   ```html
   <link rel="stylesheet" href="../../style/style.css">
   ```

2. Use the footer on all pages for consistent branding

3. Start long documents with a table of contents page

4. Use page breaks before major sections:
   ```html
   <div class="page-break"></div>
   ```

5. For Japanese documents, wrap text in the `.jp` class for better typography
