# Jinja Document Generation (Python): Best Practices for AI Coder (Sparse Priming Representation)

## Core Jinja Principles

### Organization

  * **DIR\_STRUCTURE:** Use `templates/` for `.j2` or `.jinja` template files.
  * **INHERITANCE:** Use `{% extends 'base.j2' %}` and `{% block name %}` for DRY (Don't Repeat Yourself) base layouts and inheritable sections.
  * **INCLUDES:** Use `{% include '_partial.j2' %}` for small, reusable template components.
  * **NAMING:** Conventionally, prefix partials with `_` (e.g., `_header.html.j2`) to indicate they aren't standalone templates.

### Data & Logic Flow

  * **LOGIC\_PYTHON\_SIDE:** Keep complex data transformations and business logic in your Python code. Templates are for presentation.
  * **CONTEXT\_TO\_TEMPLATE:** Pass clean, well-structured Python dictionaries or objects as context to templates.
  * **FILTERS\_USAGE:** Use for presentation-layer formatting (e.g., dates, numbers, string manipulations like `{{ my_var | upper }}`). Create custom filters for specific, reusable formatting tasks. **AVOID:** Overuse or implementing complex logic within filters.
  * **TESTS\_USAGE:** Use built-in tests (e.g., `is defined`, `is even`) for conditional logic (`{% if my_var is divisibleby 2 %}`). Create custom tests for specific checks.
  * **MACROS\_USAGE:** Define `{% macro name(args) %}` ... `{% endmacro %}` for reusable template functions that generate parameterized snippets of markup/text.

### Readability & Maintainability

  * **VARS\_NAMING:** Use clear and consistent variable names in Python context and within templates.
  * **COMMENTS:** Use `{# Jinja comment #}` for non-obvious logic or to document sections within templates. These are not outputted.
  * **WHITESPACE\_CONTROL:** Use `{{- ... -}}`, `{%- ... %}`, and `{% ... -%}` to control leading/trailing whitespace. **CRITICAL** for structured non-HTML formats (like CSV, plain text) and for generating clean HTML/XML.

### Security (**CRITICAL**)

  * **AUTOESCAPE\_HTML\_XML:** Initialize Jinja Environment with autoescaping for HTML/XML contexts: `Environment(autoescape=select_autoescape(['html', 'xml', 'htm']))`. **MANDATORY** to prevent XSS.
  * **SANITIZE\_ALL\_UNTRUSTED\_INPUT:** All data from external/user sources must be sanitized appropriately *before* rendering, or via trusted custom filters if context demands. This applies even with autoescaping (defense-in-depth) and is vital for non-HTML contexts (e.g., generating JS, CSS, SQL, LaTeX) where HTML escaping is irrelevant or insufficient.
  * **SANDBOX\_UNTRUSTED\_TEMPLATES:** If template definitions themselves come from untrusted sources, use Jinja's `SandboxedEnvironment`. Be aware this restricts available functionality.
  * **INCLUDE\_VALIDATION:** If `{% include var_template_name %}` is used and `var_template_name` can be influenced by external input, rigorously validate the variable to prevent Local File Inclusion (LFI) or access to unintended templates.

### Performance

  * **CACHING\_ENABLED:** By default, Jinja's `Environment` caches compiled templates. `FileSystemLoader` with `auto_reload=True` (default in some setups or good for dev) checks for template changes on each access. For production, `auto_reload=False` is often better. Configure `cache_size` if needed.
  * **PRECOMPILE\_TEMPLATES:** For high-load production environments, consider pre-compiling templates into Python modules for maximum speed.
  * **MINIMIZE\_TEMPLATE\_LOGIC:** Especially complex operations or calculations within loops. Pre-process data in Python.

## PDF Generation Strategies

**Workflow Overview:** `Jinja_HTML_Template -> Rendered_HTML_String/File -> PDF_Conversion_Library -> PDF_Document`

### WeasyPrint

  * **HTML\_DESIGN:** Create modular, print-focused HTML structures with Jinja.
  * **CSS\_STYLING:**
      * Use `@media print {}` CSS rules for PDF-specific styles.
      * Employ `@page {}` CSS rules for page margins, size (e.g., `A4`, `Letter`), orientation, page numbers, headers, and footers.
      * Leverage CSS Flexbox or Grid for robust layout.
  * **ASSET\_PATHS:** When rendering, ensure the PDF engine can find assets (images, fonts, external CSS). For WeasyPrint, providing a `base_url` can help resolve relative paths in your HTML template.

### xhtml2pdf

  * **Notes:** Often uses the ReportLab toolkit as its backend.
  * **HTML\_DESIGN:** Structure Jinja HTML templates for compatibility with xhtml2pdf's parsing.
  * **CSS\_PAGE\_BREAKS:** Use CSS properties like `page-break-before: always;` or `page-break-after: always;` in your Jinja-generated HTML.
  * **XHTML2PDF\_TAGS:** Utilize specific tags like `<pdf:nextpage />` directly in the HTML for explicit page breaks.
  * **ENCODING:** Ensure UTF-8 encoding for HTML templates and data to support international characters.

### General HTML-to-PDF Libraries (e.g., PDFKit, Pyppeteer, Playwright)

  * **INPUT\_HTML\_QUALITY:** The primary focus for Jinja is to produce clean, W3C-compliant HTML.
  * **LIB\_OPTIONS:** Consult the specific library's documentation for PDF conversion options (page size, margins, quality, JavaScript execution for browser-based tools).

## DOCX Generation Strategies

### `python-docx-template`

  * **TEMPLATE\_FILE:** Prepare a standard `.docx` Word document. Embed Jinja2-like tags (e.g., `{{ placeholder }}`, `{% for item in items %}`, `{% if condition %}`) directly where dynamic content is needed.
  * **RICH\_CONTENT:** Leverage Word's native formatting (styles, bold, italics, colors), tables, images, headers, footers directly within the `.docx` template. Jinja tags will insert data while preserving surrounding formatting.
  * **PYTHON\_INTEGRATION:**
    ```python
    from docxtpl import DocxTemplate
    doc = DocxTemplate('your_template.docx')
    context = { 'variable_name' : 'Dynamic Value', 'items_list': [...] }
    doc.render(context)
    doc.save('output_document.docx')
    ```
  * **JINJA\_TAGS\_IN\_WORD:** Ensure Jinja tags are correctly formatted. Editing complex tags directly in Word can sometimes be tricky; ensure no smart quotes or unintended Word formatting corrupts the tags. Test dynamic table rows and conditional blocks thoroughly.

## Error Handling & Common Pitfalls

### Error Mitigation In Template

  * **UNDEFINED\_VARS:** Gracefully handle potentially missing variables:
      * `{{ my_variable | default('N/A') }}`
      * `{% if my_variable is defined %} ... {% endif %}`

### Error Handling In Python

  * **TRY\_EXCEPT\_BLOCKS:** Wrap template loading and rendering calls (`env.get_template()`, `template.render()`) in `try...except` blocks to catch Jinja exceptions like `TemplateNotFound`, `UndefinedError`, `TemplateSyntaxError`.

### Debugging Tips

  * **INSPECT\_CONTEXT:** Log or print the context dictionary being passed to `template.render()` to verify data.
  * **INTERMEDIATE\_HTML:** For HTML-to-PDF workflows, save and inspect the intermediate rendered HTML output before it's passed to the PDF converter.
  * **JINJA\_DEBUG\_STMT:** Use `{% debug %}` inside a template during development to dump current context variables (use with caution, remove for production).

### Scaling Considerations

  * **DATA\_PREP\_EFFICIENCY:** Optimize data fetching and pre-processing in Python before template rendering.
  * **ASYNC\_OPERATIONS:** For web services or applications generating many/large documents, consider asynchronous task execution (e.g., using `asyncio` with compatible libraries, or task queues like Celery) to prevent blocking.

### Pitfalls To Avoid

  * **SYNTAX\_ERRORS:** Double-check Jinja delimiters (`{{ }}`, `{% %}`, `{# #}`), tag names, filter syntax.
  * **OVERLY\_COMPLEX\_TEMPLATES:** **PRIORITY -\>** Move complex logic, calculations, and data manipulation to Python code. Templates should focus on presentation.
  * **UNCONTROLLED\_WHITESPACE:** Can break layout in sensitive formats (CSV, plain text) or add subtle issues in HTML/XML. Actively use whitespace control: `{{-`, `-%}`, etc.
  * **SECURITY\_LAPSES:** Failing to enable autoescaping for HTML/XML; not sanitizing user-provided or external input. **REVIEW** the security section thoroughly.
  * **PERFORMANCE\_ISSUES:** Inefficient loops with complex operations inside templates; not being aware of or misconfiguring template caching in high-load scenarios.
  * **ENVIRONMENT\_INCONSISTENCY:** E.g., font availability for PDF generation (server environment might lack fonts present in development). Ensure consistency or embed fonts.
  * **JINJA\_COMMENTS\_EVALUATION:** Be aware that Jinja comments `{# ... #}` are processed. If a Jinja expression (e.g., `{{ unsafe_var }}`) is inside a Jinja comment, the variable `unsafe_var` might still be accessed/evaluated. For full "commenting out" of template logic, ensure the entire block is syntactically a comment or remove the code.
