# Using the Footer and Table of Contents Style

This document provides instructions on how to integrate the new footer and improved table of contents styling into your Markdown documents.

## Including the Footer

To include the footer in your Markdown documents, add the following HTML at the end of your file:

```html
<div class="footer">
    <div class="footer-doc-name">Document Name</div>
    <img class="footer-logo" src="../style/TechShare_logo.svg" alt="TechShare Logo">
</div>

<script>
    // Update document name in footer
    document.addEventListener('DOMContentLoaded', function() {
        const docPath = window.location.pathname;
        const docName = docPath.split('/').pop().replace('.md', '');
        const docNameElement = document.querySelector('.footer-doc-name');
        if (docNameElement) {
            docNameElement.textContent = docName;
        }
    });
</script>
```

## Creating a Table of Contents Page

To create a styled table of contents page, add the following at the beginning of your document:

```html
<div class="toc-page" data-date="">
    <h1 class="toc-page-title">Contents</h1>
    <div class="toc">
        <div class="toc-title">Table of Contents</div>
        <!-- Your TOC items will go here -->
    </div>
</div>

<div class="page-break"></div>

<script>
    // Set current date
    document.addEventListener('DOMContentLoaded', function() {
        const tocPageElement = document.querySelector('.toc-page');
        if (tocPageElement) {
            const today = new Date();
            const dateString = today.toLocaleDateString();
            tocPageElement.setAttribute('data-date', dateString);
        }
    });
</script>
```

## Automatically Generating a Table of Contents

You can also use tools like markdown-toc or a script to auto-generate your table of contents. Here's a simple example:

```html
<div class="toc-page" data-date="">
    <h1 class="toc-page-title">Contents</h1>
    <div class="toc">
        <div class="toc-title">Table of Contents</div>
        <div id="generated-toc"></div>
    </div>
</div>

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
        const toc = document.createElement('ul');
        
        headings.forEach(function(heading) {
            if (!heading.id) {
                heading.id = heading.textContent.toLowerCase().replace(/\s+/g, '-');
            }
            
            const listItem = document.createElement('li');
            const link = document.createElement('a');
            link.href = '#' + heading.id;
            link.textContent = heading.textContent;
            listItem.appendChild(link);
            
            if (heading.tagName === 'H2') {
                toc.appendChild(listItem);
            } else if (heading.tagName === 'H3') {
                // Find the last H2 list item and append to its UL or create one
                const lastH2Item = Array.from(toc.children).pop();
                if (lastH2Item) {
                    let ulH3 = lastH2Item.querySelector('ul');
                    if (!ulH3) {
                        ulH3 = document.createElement('ul');
                        lastH2Item.appendChild(ulH3);
                    }
                    ulH3.appendChild(listItem);
                }
            }
        });
        
        tocContainer.appendChild(toc);
    });
</script>
```

## For PDF Conversion

When converting to PDF (using tools like Prince or wkhtmltopdf), ensure you add a reference to the style.css file in your document:

```html
<link rel="stylesheet" href="../style/style.css">
```

And use the page-break class wherever you need to force a new page:

```html
<div class="page-break"></div>
```

The footer will automatically appear on each page in PDF output thanks to the CSS page rules.
