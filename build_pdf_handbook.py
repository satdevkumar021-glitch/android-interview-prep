import re
import html

# Read index.html
with open('index.html', 'r', encoding='utf-8') as f:
    raw_html = f.read()

# Extract title and description
title_match = re.search(r'<title>(.*?)</title>', raw_html)
title = title_match.group(1) if title_match else "Android Staff Engineer Interview Mastery"

# Extract all topic-section blocks (topic-1 to topic-12)
topic_sections = re.findall(r'<section class="topic-section.*?" id="topic-(1[0-2]|[1-9])">(.*?)</section>', raw_html, re.DOTALL)

print(f"Extracted {len(topic_sections)} topic sections.")

# Clean each section:
# - Remove interactive checkboxes/trackers
# - Ensure syntax highlight classes are retained
# - Structure QA nicely
cleaned_sections = []
for topic_num, sec_content in topic_sections:
    # Remove progress tracker checklist
    sec_content = re.sub(r'<div class="topic-progress-tracker".*?</div>\s*</div>', '', sec_content, flags=re.DOTALL)
    # Remove expand-icon
    sec_content = re.sub(r'<span class="expand-icon">.*?</span>', '', sec_content)
    cleaned_sections.append(sec_content)

# Build Executive Document HTML
pdf_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Android Staff & Lead Engineer Interview Mastery Handbook</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300..800;1,14..32,300..800&family=JetBrains+Mono:wght@400;500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400..700;1,6..72,400..700&display=swap" rel="stylesheet">
  <style>
    /* ==========================================================================
       PAGINATION & DOCUMENT GEOMETRY
       ========================================================================== */
    @page {{
      size: A4 portrait;
      margin: 18mm 16mm 20mm 16mm;
      @bottom-right {{
        content: counter(page);
        font-family: 'Inter', sans-serif;
        font-size: 8.5pt;
        color: #64748b;
      }};
      @bottom-left {{
        content: "Android Interview Mastery — Staff & Lead Engineer Edition";
        font-family: 'Inter', sans-serif;
        font-size: 8.5pt;
        color: #94a3b8;
      }};
      @top-right {{
        content: "CONFIDENTIAL / INTERVIEW PREP";
        font-family: 'JetBrains Mono', monospace;
        font-size: 7.5pt;
        color: #cbd5e1;
        letter-spacing: 0.5px;
      }};
    }}

    /* ==========================================================================
       TYPOGRAPHY & ROOT VARIABLES
       ========================================================================== */
    :root {{
      --font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      --font-serif: 'Newsreader', Georgia, serif;
      --font-code: 'JetBrains Mono', 'Fira Code', Menlo, monospace;
      
      --c-text: #0f172a;
      --c-text-muted: #475569;
      --c-text-light: #64748b;
      --c-border: #e2e8f0;
      --c-bg-subtle: #f8fafc;
      --c-bg-card: #ffffff;
      
      --accent-blue: #0284c7;
      --accent-indigo: #4f46e5;
      --accent-amber: #d97706;
      --accent-emerald: #059669;
      --accent-purple: #7c3aed;
      --accent-rose: #e11d48;
      --accent-orange: #ea580c;
    }}

    * {{
      box-sizing: border-box;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }}

    body {{
      font-family: var(--font-body);
      color: var(--c-text);
      background: #ffffff;
      line-height: 1.6;
      font-size: 10pt;
      margin: 0;
      padding: 0;
    }}

    /* ==========================================================================
       COVER / TITLE PAGE
       ========================================================================== */
    .cover-page {{
      page-break-after: always;
      height: 92vh;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 2.5rem 1.5rem 1.5rem 1.5rem;
      border: 1px solid var(--c-border);
      border-radius: 12px;
      background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
      position: relative;
    }}

    .cover-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: #0f172a;
      color: #38bdf8;
      font-family: var(--font-code);
      font-size: 8.5pt;
      font-weight: 600;
      padding: 6px 14px;
      border-radius: 9999px;
      text-transform: uppercase;
      letter-spacing: 1px;
      width: fit-content;
    }}

    .cover-title {{
      font-size: 32pt;
      font-weight: 800;
      line-height: 1.15;
      color: #0f172a;
      margin: 1.5rem 0 0.75rem 0;
      letter-spacing: -0.03em;
    }}

    .cover-subtitle {{
      font-family: var(--font-serif);
      font-size: 15pt;
      color: #334155;
      font-style: italic;
      line-height: 1.4;
      margin-bottom: 2rem;
    }}

    .cover-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin: 1.5rem 0;
    }}

    .cover-grid-item {{
      background: #ffffff;
      border: 1px solid var(--c-border);
      padding: 10px 14px;
      border-radius: 8px;
      font-size: 8.5pt;
      box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }}

    .cover-grid-item strong {{
      display: block;
      color: #0f172a;
      font-size: 9.5pt;
      margin-bottom: 2px;
    }}

    .cover-footer {{
      border-top: 2px solid #0f172a;
      padding-top: 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: var(--font-code);
      font-size: 8pt;
      color: var(--c-text-muted);
    }}

    /* ==========================================================================
       SECTION HEADERS & SUBTOPICS
       ========================================================================== */
    .topic-section {{
      page-break-before: always;
      padding-top: 0.5rem;
    }}

    .topic-header {{
      background: #0f172a;
      color: #ffffff;
      padding: 1.25rem 1.5rem;
      border-radius: 8px;
      margin-bottom: 1.5rem;
      page-break-inside: avoid;
    }}

    .topic-number {{
      font-family: var(--font-code);
      font-size: 9pt;
      font-weight: 700;
      color: #38bdf8;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      display: block;
      margin-bottom: 4px;
    }}

    .topic-header h1 {{
      font-size: 18pt;
      font-weight: 800;
      margin: 0 0 6px 0;
      color: #ffffff;
      line-height: 1.25;
      letter-spacing: -0.02em;
    }}

    .topic-desc {{
      font-size: 9.5pt;
      color: #cbd5e1;
      margin: 0;
      line-height: 1.5;
    }}

    .topic-tags {{
      display: flex;
      gap: 6px;
      margin-top: 10px;
    }}

    .tag {{
      font-family: var(--font-code);
      font-size: 7.5pt;
      padding: 2px 8px;
      border-radius: 4px;
      background: rgba(255,255,255,0.15);
      color: #f1f5f9;
      font-weight: 600;
    }}

    .subtopic {{
      margin-bottom: 2rem;
      page-break-inside: auto;
    }}

    .subtopic h2 {{
      font-size: 13pt;
      font-weight: 700;
      color: #0f172a;
      border-bottom: 2px solid #0f172a;
      padding-bottom: 4px;
      margin: 1.5rem 0 1rem 0;
      page-break-after: avoid;
      letter-spacing: -0.01em;
    }}

    /* ==========================================================================
       5-PILLAR ARCHITECTURAL CARDS
       ========================================================================== */
    .card {{
      background: #ffffff;
      border: 1px solid var(--c-border);
      border-radius: 8px;
      padding: 1rem 1.15rem;
      margin-bottom: 0.9rem;
      page-break-inside: avoid;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }}

    .card h3 {{
      font-size: 10.5pt;
      font-weight: 700;
      margin: 0 0 0.5rem 0;
      display: flex;
      align-items: center;
      gap: 6px;
      letter-spacing: -0.01em;
    }}

    .card p {{
      margin: 0 0 0.5rem 0;
      font-size: 9.5pt;
      line-height: 1.6;
      color: #1e293b;
    }}

    .card p:last-child {{
      margin-bottom: 0;
    }}

    .card ul {{
      margin: 0.35rem 0 0.5rem 1.25rem;
      padding: 0;
      font-size: 9.2pt;
    }}

    .card li {{
      margin-bottom: 0.35rem;
      line-height: 1.5;
      color: #334155;
    }}

    /* Specific Card Accents */
    .card-what {{
      border-left: 4px solid var(--accent-blue);
      background: #f0f9ff;
    }}
    .card-what h3 {{ color: #0369a1; }}

    .card-why {{
      border-left: 4px solid var(--accent-amber);
      background: #fffbeb;
    }}
    .card-why h3 {{ color: #b45309; }}

    .card-how {{
      border-left: 4px solid var(--accent-emerald);
      background: #f0fdf4;
    }}
    .card-how h3 {{ color: #047857; }}

    .card-realworld {{
      border-left: 4px solid var(--accent-purple);
      background: #faf5ff;
    }}
    .card-realworld h3 {{ color: #6d28d9; }}

    .card-presenter {{
      border-left: 4px solid var(--accent-orange);
      background: #fff7ed;
      border: 1px solid #fed7aa;
    }}
    .card-presenter h3 {{ color: #c2410c; }}

    .pitch-quote {{
      font-family: var(--font-serif);
      font-size: 10pt;
      font-style: italic;
      line-height: 1.6;
      color: #7c2d12;
      background: #ffedd5;
      padding: 0.85rem 1.15rem;
      border-radius: 6px;
      border-left: 3px solid #ea580c;
      margin-top: 0.4rem;
    }}

    /* ==========================================================================
       CODE BLOCKS (SYNTAX & READABILITY)
       ========================================================================== */
    .code-block {{
      background: #0f172a !important;
      border: 1px solid #1e293b;
      border-radius: 6px;
      padding: 0.85rem 1rem;
      margin: 0.5rem 0;
      page-break-inside: avoid;
      overflow-x: hidden;
    }}

    .code-block pre {{
      margin: 0;
      padding: 0;
      font-family: var(--font-code);
      font-size: 8.2pt;
      line-height: 1.45;
      color: #e2e8f0;
      tab-size: 2;
      white-space: pre-wrap;
      word-break: break-word;
    }}

    code {{
      font-family: var(--font-code);
      font-size: 8.5pt;
      background: #f1f5f9;
      color: #0f172a;
      padding: 2px 5px;
      border-radius: 4px;
      border: 1px solid #e2e8f0;
    }}

    .code-block code {{
      background: transparent !important;
      border: none !important;
      color: #e2e8f0 !important;
      padding: 0 !important;
    }}

    /* Inline Code Highlighting Colors */
    .token-keyword {{ color: #f43f5e; font-weight: 600; }}
    .token-function {{ color: #38bdf8; }}
    .token-string {{ color: #a3e635; }}
    .token-comment {{ color: #64748b; font-style: italic; }}
    .token-type {{ color: #fbbf24; }}

    /* ==========================================================================
       SENIOR & STAFF INTERVIEW Q&A SECTION
       ========================================================================== */
    .qa-section {{
      margin-top: 2rem;
      page-break-inside: auto;
    }}

    .qa-section h2 {{
      font-size: 13pt;
      font-weight: 800;
      color: #0f172a;
      background: #f1f5f9;
      padding: 0.6rem 1rem;
      border-radius: 6px;
      border-left: 4px solid #0f172a;
      margin: 1.5rem 0 1rem 0;
      page-break-after: avoid;
    }}

    .qa-item {{
      background: #ffffff;
      border: 1px solid var(--c-border);
      border-radius: 8px;
      padding: 1rem 1.15rem;
      margin-bottom: 0.85rem;
      page-break-inside: avoid;
      box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }}

    .qa-question {{
      display: flex;
      align-items: baseline;
      gap: 8px;
      margin-bottom: 0.6rem;
      border-bottom: 1px dashed #cbd5e1;
      padding-bottom: 0.4rem;
    }}

    .qa-number {{
      font-family: var(--font-code);
      font-size: 8.5pt;
      font-weight: 700;
      background: #0f172a;
      color: #ffffff;
      padding: 2px 7px;
      border-radius: 4px;
    }}

    .qa-question p {{
      margin: 0;
      font-weight: 700;
      font-size: 10pt;
      color: #0f172a;
      line-height: 1.4;
    }}

    .badge {{
      font-family: var(--font-code);
      font-size: 7pt;
      font-weight: 700;
      text-transform: uppercase;
      padding: 2px 6px;
      border-radius: 4px;
      letter-spacing: 0.5px;
    }}

    .badge-basic {{ background: #e0f2fe; color: #0369a1; }}
    .badge-advanced {{ background: #fef3c7; color: #b45309; }}
    .badge-scenario {{ background: #fae8ff; color: #86198f; }}

    .qa-answer {{
      font-size: 9.3pt;
      color: #1e293b;
      line-height: 1.6;
    }}

    .qa-answer p {{
      margin: 0 0 0.5rem 0;
    }}
    .qa-answer p:last-child {{
      margin-bottom: 0;
    }}
    .qa-answer strong {{
      color: #0f172a;
    }}

    /* ==========================================================================
       TABLES
       ========================================================================== */
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 0.75rem 0;
      font-size: 8.5pt;
      page-break-inside: avoid;
    }}

    th, td {{
      border: 1px solid var(--c-border);
      padding: 6px 10px;
      text-align: left;
    }}

    th {{
      background: #f1f5f9;
      color: #0f172a;
      font-weight: 700;
    }}

    /* Utility */
    .text-center {{ text-align: center; }}
    .font-mono {{ font-family: var(--font-code); }}
  </style>
</head>
<body>

  <!-- ==========================================================================
       COVER / EXECUTIVE SUMMARY PAGE
       ========================================================================== -->
  <div class="cover-page">
    <div>
      <div class="cover-badge">⚡ Senior & Staff Engineering Architecture</div>
      <h1 class="cover-title">Android Interview Mastery Handbook</h1>
      <p class="cover-subtitle">A Comprehensive, Bytecode-to-Architecture Study Guide for Senior, Staff, and Principal Android Engineers.</p>
      
      <div style="margin: 1.5rem 0; padding: 1rem 1.25rem; background: #ffffff; border: 1px solid var(--c-border); border-left: 4px solid #0284c7; border-radius: 6px;">
        <div style="font-weight: 700; font-size: 10.5pt; color: #0f172a; margin-bottom: 4px;">🎯 Architectural Framework (What • Why • How • Real-World • Pitch)</div>
        <div style="font-size: 9pt; color: #475569; line-height: 1.5;">
          Every topic in this handbook is presented with strict engineering rigor: (1) Core mechanics & bytecode definitions, (2) Root problem & GC/memory trade-offs, (3) Production-ready code, (4) Scaled enterprise architectures (FinTech, Healthcare, Automotive), and (5) The precise verbal pitch for senior technical rounds.
        </div>
      </div>

      <div class="cover-grid">
        <div class="cover-grid-item">
          <strong>01. Kotlin Core & Bytecode</strong>
          <span>Scope functions, inlining mechanics, reified generics & delegation.</span>
        </div>
        <div class="cover-grid-item">
          <strong>02. Android Lifecycles & Process Death</strong>
          <span>Component trees, Intent flags, process termination & state restoration.</span>
        </div>
        <div class="cover-grid-item">
          <strong>03. Background Services & WorkManager</strong>
          <span>Android 14 service types, expedited jobs & persistent worker pools.</span>
        </div>
        <div class="cover-grid-item">
          <strong>04. Jetpack Compose Internals</strong>
          <span>SlotTable, compiler stability, recomposition loops & SideEffects.</span>
        </div>
        <div class="cover-grid-item">
          <strong>05. ViewModel, Room & Local State</strong>
          <span>ViewModelStore, complex SQL schema migrations & Tink encryption.</span>
        </div>
        <div class="cover-grid-item">
          <strong>06. Retrofit, OkHttp & Network Layer</strong>
          <span>Chain interceptors, token refresh mutex locks & custom CallAdapters.</span>
        </div>
        <div class="cover-grid-item">
          <strong>07. Dagger Hilt & Dependency Injection</strong>
          <span>Scope graphs, multi-module bindings & assisted injection factories.</span>
        </div>
        <div class="cover-grid-item">
          <strong>08. Architecture Patterns (MVP, MVVM, MVI)</strong>
          <span>Clean boundaries, state-event contracts & Unidirectional Data Flow.</span>
        </div>
        <div class="cover-grid-item">
          <strong>09. Concurrency, Coroutines & Flow</strong>
          <span>Structured concurrency, backpressure operators & lifecycle collectors.</span>
        </div>
        <div class="cover-grid-item">
          <strong>10. Hardware KeyStore & Security</strong>
          <span>TEE/StrongBox hardware enclaves, BiometricPrompt AES-GCM & Play Integrity.</span>
        </div>
        <div class="cover-grid-item">
          <strong>11. Performance & CI/CD Benchmarking</strong>
          <span>16ms/8.3ms VSYNC, LeakCanary triage, Baseline Profiles & Macrobenchmarks.</span>
        </div>
        <div class="cover-grid-item">
          <strong>12. AOSP, Binder IPC & On-Device AI</strong>
          <span>One-copy mmap, oneway AIDL contracts, Gemini Nano & agentic tools.</span>
        </div>
      </div>
    </div>

    <div class="cover-footer">
      <span>Android Engineering Mastery Curriculum</span>
      <span>60 Deep-Dive Interview Questions Included</span>
      <span>Senior / Staff Edition</span>
    </div>
  </div>

  <!-- ==========================================================================
       TECHNICAL CONTENT SECTIONS
       ========================================================================== -->
"""

# Append all cleaned topic sections
for section_html in cleaned_sections:
    pdf_html += f"""
  <div class="topic-section">
    {section_html}
  </div>
"""

pdf_html += """
</body>
</html>
"""

# Write to formatted-handbook.html
with open('formatted-handbook.html', 'w', encoding='utf-8') as f:
    f.write(pdf_html)

print("Created formatted-handbook.html successfully!")
