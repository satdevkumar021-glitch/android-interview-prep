import re

# Read index.html and create a print-optimized single-document HTML version
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Insert print styles to make all sections visible, expanded, and beautifully formatted for PDF
print_css = """
<style>
@media print {
  @page {
    size: A4;
    margin: 1.5cm;
  }
  body {
    background: #ffffff !important;
    color: #0f172a !important;
    font-size: 11pt !important;
    line-height: 1.5 !important;
  }
  /* Hide interactive SPA elements */
  .sidebar, .hamburger, .sidebar-overlay, #scroll-progress, .search-box, 
  .theme-toggle, .qa-view-switcher, .flip-deck-container, .topic-progress-tracker,
  .quick-tools-fab, .flashcard-modal {
    display: none !important;
  }
  .main-content {
    margin-left: 0 !important;
    padding: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
  }
  /* Make all topic sections visible and break pages cleanly */
  .topic-section {
    display: block !important;
    opacity: 1 !important;
    visibility: visible !important;
    page-break-before: always;
    margin-bottom: 2rem !important;
  }
  .topic-section:first-of-type {
    page-break-before: avoid;
  }
  /* Expand all QA accordion items */
  .qa-item {
    display: block !important;
    page-break-inside: avoid;
    margin-bottom: 1.25rem !important;
    border: 1px solid #cbd5e1 !important;
    background: #f8fafc !important;
    padding: 1rem !important;
    border-radius: 8px !important;
  }
  .qa-answer {
    display: block !important;
    max-height: none !important;
    padding-top: 0.75rem !important;
  }
  .expand-icon {
    display: none !important;
  }
  /* Cards formatting */
  .card {
    page-break-inside: avoid;
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: none !important;
    margin-bottom: 1rem !important;
    color: #1e293b !important;
  }
  .card h3 {
    color: #0f172a !important;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 0.3rem;
  }
  .card-what { border-left: 5px solid #0284c7 !important; }
  .card-why { border-left: 5px solid #d97706 !important; }
  .card-how { border-left: 5px solid #16a34a !important; }
  .card-realworld { border-left: 5px solid #9333ea !important; }
  .card-presenter { border-left: 5px solid #ea580c !important; background: #fff7ed !important; }
  
  .pitch-quote {
    background: #ffedd5 !important;
    color: #7c2d12 !important;
    border-left: 4px solid #ea580c !important;
    font-style: italic;
  }
  
  /* Code blocks in print */
  .code-block {
    background: #f1f5f9 !important;
    border: 1px solid #cbd5e1 !important;
    page-break-inside: avoid;
  }
  .code-block pre, .code-block code {
    color: #0f172a !important;
    font-size: 9.5pt !important;
    text-shadow: none !important;
  }
  .code-copy-btn, .code-lang-tag {
    display: none !important;
  }
  h1, h2, h3, h4 {
    page-break-after: avoid;
    color: #0f172a !important;
  }
  h1 { font-size: 20pt !important; }
  h2 { font-size: 15pt !important; border-bottom: 2px solid #0f172a; padding-bottom: 0.2rem; margin-top: 1.5rem; }
  h3 { font-size: 12pt !important; }
  
  a { text-decoration: none !important; color: #0284c7 !important; }
}
</style>
"""

# Also ensure on non-print render (for direct browser view of printable file) everything is displayed
screen_override_css = """
<style>
body { background: #0b0f19; color: #e2e8f0; }
.sidebar, .hamburger, .sidebar-overlay, #scroll-progress, .search-box, .theme-toggle, .qa-view-switcher, .flip-deck-container, .topic-progress-tracker { display: none !important; }
.main-content { margin-left: 0 !important; width: 100% !important; max-width: 1000px !important; margin: 0 auto !important; padding: 2rem !important; }
.topic-section { display: block !important; margin-bottom: 4rem !important; border-bottom: 2px solid var(--border-color); padding-bottom: 3rem; }
.qa-item { display: block !important; margin-bottom: 1rem !important; }
.qa-answer { display: block !important; max-height: none !important; }
.expand-icon { display: none !important; }
</style>
"""

# Inject before </head>
modified_html = html.replace('</head>', print_css + screen_override_css + '</head>')
# Remove js/app.js script to prevent runtime accordion collapsing in static PDF view
modified_html = re.sub(r'<script\s+src="js/app.js"></script>', '', modified_html)

with open('printable-handbook.html', 'w', encoding='utf-8') as f:
    f.write(modified_html)

print("Created printable-handbook.html successfully!")
