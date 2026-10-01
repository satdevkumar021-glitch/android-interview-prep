import os
import sys

print("Assembling master index.html — 41 modules, 9-Pillar structure...")

# ── Import existing topic generators (topics 1-12) ─────────────────────────
from html_topic_1_to_3 import get_topics_1_to_3_html
from html_topic_4_to_6 import get_topics_4_to_6_html
from html_topic_7_to_9 import get_topics_7_to_9_html
from html_topic_10_to_12 import get_topics_10_to_12_html

# ── Import new topic generators (topics 13-41) ─────────────────────────────
try:
    from html_topic_13_to_17 import get_topics_13_to_17_html
except ImportError as e:
    print(f"WARNING: {e}"); get_topics_13_to_17_html = lambda: "<!-- Topics 13-17 coming soon -->"

try:
    from html_topic_18_to_22 import get_topics_18_to_22_html
except ImportError as e:
    print(f"WARNING: {e}"); get_topics_18_to_22_html = lambda: "<!-- Topics 18-22 coming soon -->"

try:
    from html_topic_23_to_27 import get_topics_23_to_27_html
except ImportError as e:
    print(f"WARNING: {e}"); get_topics_23_to_27_html = lambda: "<!-- Topics 23-27 coming soon -->"

try:
    from html_topic_28_to_32 import get_topics_28_to_32_html
except ImportError as e:
    print(f"WARNING: {e}"); get_topics_28_to_32_html = lambda: "<!-- Topics 28-32 coming soon -->"

try:
    from html_topic_33_to_37 import get_topics_33_to_37_html
except ImportError as e:
    print(f"WARNING: {e}"); get_topics_33_to_37_html = lambda: "<!-- Topics 33-37 coming soon -->"

try:
    from html_topic_38_to_40 import get_topics_38_to_40_html
except ImportError as e:
    print(f"WARNING: {e}"); get_topics_38_to_40_html = lambda: "<!-- Topics 38-41 coming soon -->"

# ── HTML header + sidebar (41 topics) ─────────────────────────────────────
html_header = '''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Android Interview Mastery — Complete 41-Module Senior Edition</title>
  <meta name="description" content="Complete Android interview prep: Kotlin, Coroutines, Flow, Jetpack Compose, MVVM/MVI, Hilt, Retrofit, Room, WorkManager, Security, Testing, CI/CD, System Design, DSA — all with 9-pillar deep dive.">

  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">

  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤖</text></svg>">
  <link rel="stylesheet" href="css/style.css">
</head>
<body>

  <!-- Scroll Progress Bar -->
  <div id="scroll-progress"></div>

  <!-- Mobile Hamburger -->
  <button class="hamburger" aria-label="Toggle navigation" aria-expanded="false">
    <span class="hamburger-line"></span>
    <span class="hamburger-line"></span>
    <span class="hamburger-line"></span>
  </button>

  <!-- Sidebar Overlay -->
  <div class="sidebar-overlay"></div>

  <!-- Master Sidebar Navigation -->
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="sidebar-logo">
        <span class="logo-icon">🤖</span>
        <div>
          <h2 class="sidebar-title">Android Prep</h2>
          <p class="sidebar-subtitle">Senior / Staff Architect</p>
        </div>
      </div>
    </div>

    <!-- Live Interview Readiness Score Card -->
    <div class="readiness-box" style="margin: 0 1rem 0.75rem 1rem;">
      <div class="readiness-title">🎯 Interview Readiness</div>
      <div class="readiness-score">0%</div>
      <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 2px;">Live score across all 41 modules</div>
    </div>

    <!-- Quick Filter in Sidebar -->
    <div class="sidebar-filter-wrapper">
      <input type="text" class="sidebar-filter-input" placeholder="Filter topics..." autocomplete="off">
    </div>

    <nav class="sidebar-nav">
      <a class="nav-link active" data-topic="0">
        <span class="nav-icon">🏠</span>
        <span class="nav-text">Executive Dashboard</span>
      </a>

      <div class="nav-section-label">Kotlin Language</div>
      <a class="nav-link" data-topic="1">
        <span class="nav-icon">⚡</span>
        <span class="nav-text">1. Kotlin Core &amp; Advanced</span>
        <span class="topic-progress" data-topic-progress="1">0%</span>
      </a>

      <div class="nav-section-label">Android Framework</div>
      <a class="nav-link" data-topic="2">
        <span class="nav-icon">📱</span>
        <span class="nav-text">2. Components &amp; Lifecycles</span>
        <span class="topic-progress" data-topic-progress="2">0%</span>
      </a>
      <a class="nav-link" data-topic="3">
        <span class="nav-icon">⚙️</span>
        <span class="nav-text">3. Services &amp; WorkManager</span>
        <span class="topic-progress" data-topic-progress="3">0%</span>
      </a>

      <div class="nav-section-label">Modern Android</div>
      <a class="nav-link" data-topic="4">
        <span class="nav-icon">🎨</span>
        <span class="nav-text">4. Jetpack Compose Internals</span>
        <span class="topic-progress" data-topic-progress="4">0%</span>
      </a>
      <a class="nav-link" data-topic="5">
        <span class="nav-icon">🏛️</span>
        <span class="nav-text">5. ViewModel, Room &amp; State</span>
        <span class="topic-progress" data-topic-progress="5">0%</span>
      </a>
      <a class="nav-link" data-topic="6">
        <span class="nav-icon">🌐</span>
        <span class="nav-text">6. Retrofit, OkHttp &amp; Coil</span>
        <span class="topic-progress" data-topic-progress="6">0%</span>
      </a>
      <a class="nav-link" data-topic="7">
        <span class="nav-icon">💉</span>
        <span class="nav-text">7. Dependency Injection (Hilt)</span>
        <span class="topic-progress" data-topic-progress="7">0%</span>
      </a>
      <a class="nav-link" data-topic="8">
        <span class="nav-icon">📐</span>
        <span class="nav-text">8. Architecture MVP/MVVM/MVI</span>
        <span class="topic-progress" data-topic-progress="8">0%</span>
      </a>
      <a class="nav-link" data-topic="9">
        <span class="nav-icon">🔄</span>
        <span class="nav-text">9. Concurrency &amp; Coroutines</span>
        <span class="topic-progress" data-topic-progress="9">0%</span>
      </a>
      <a class="nav-link" data-topic="10">
        <span class="nav-icon">🔒</span>
        <span class="nav-text">10. Hardware KeyStore &amp; Security</span>
        <span class="topic-progress" data-topic-progress="10">0%</span>
      </a>
      <a class="nav-link" data-topic="11">
        <span class="nav-icon">🚀</span>
        <span class="nav-text">11. Performance &amp; CI/CD</span>
        <span class="topic-progress" data-topic-progress="11">0%</span>
      </a>
      <a class="nav-link" data-topic="12">
        <span class="nav-icon">🤖</span>
        <span class="nav-text">12. AOSP &amp; On-Device AI</span>
        <span class="topic-progress" data-topic-progress="12">0%</span>
      </a>

      <div class="nav-section-label">Deep Dive — Syllabus</div>
      <a class="nav-link" data-topic="13">
        <span class="nav-icon">📱</span>
        <span class="nav-text">13. Android Fundamentals</span>
        <span class="topic-progress" data-topic-progress="13">0%</span>
      </a>
      <a class="nav-link" data-topic="14">
        <span class="nav-icon">🔁</span>
        <span class="nav-text">14. Kotlin Coroutines 🔥</span>
        <span class="topic-progress" data-topic-progress="14">0%</span>
      </a>
      <a class="nav-link" data-topic="15">
        <span class="nav-icon">🌊</span>
        <span class="nav-text">15. Kotlin Flow 🔥</span>
        <span class="topic-progress" data-topic-progress="15">0%</span>
      </a>
      <a class="nav-link" data-topic="16">
        <span class="nav-icon">🏗️</span>
        <span class="nav-text">16. Android Architecture</span>
        <span class="topic-progress" data-topic-progress="16">0%</span>
      </a>
      <a class="nav-link" data-topic="17">
        <span class="nav-icon">📏</span>
        <span class="nav-text">17. SOLID Principles</span>
        <span class="topic-progress" data-topic-progress="17">0%</span>
      </a>
      <a class="nav-link" data-topic="18">
        <span class="nav-icon">🧩</span>
        <span class="nav-text">18. Design Patterns</span>
        <span class="topic-progress" data-topic-progress="18">0%</span>
      </a>
      <a class="nav-link" data-topic="19">
        <span class="nav-icon">💉</span>
        <span class="nav-text">19. DI — Hilt &amp; Dagger 2</span>
        <span class="topic-progress" data-topic-progress="19">0%</span>
      </a>
      <a class="nav-link" data-topic="20">
        <span class="nav-icon">🌐</span>
        <span class="nav-text">20. Networking Deep Dive</span>
        <span class="topic-progress" data-topic-progress="20">0%</span>
      </a>
      <a class="nav-link" data-topic="21">
        <span class="nav-icon">🗄️</span>
        <span class="nav-text">21. Room &amp; Local Storage</span>
        <span class="topic-progress" data-topic-progress="21">0%</span>
      </a>
      <a class="nav-link" data-topic="22">
        <span class="nav-icon">⚙️</span>
        <span class="nav-text">22. WorkManager Deep Dive</span>
        <span class="topic-progress" data-topic-progress="22">0%</span>
      </a>

      <div class="nav-section-label">Android Components</div>
      <a class="nav-link" data-topic="23">
        <span class="nav-icon">🔧</span>
        <span class="nav-text">23. Android Services</span>
        <span class="topic-progress" data-topic-progress="23">0%</span>
      </a>
      <a class="nav-link" data-topic="24">
        <span class="nav-icon">📡</span>
        <span class="nav-text">24. BroadcastReceiver</span>
        <span class="topic-progress" data-topic-progress="24">0%</span>
      </a>
      <a class="nav-link" data-topic="25">
        <span class="nav-icon">📂</span>
        <span class="nav-text">25. ContentProvider</span>
        <span class="topic-progress" data-topic-progress="25">0%</span>
      </a>
      <a class="nav-link" data-topic="26">
        <span class="nav-icon">🗺️</span>
        <span class="nav-text">26. Navigation &amp; Deep Linking</span>
        <span class="topic-progress" data-topic-progress="26">0%</span>
      </a>

      <div class="nav-section-label">Security &amp; Quality</div>
      <a class="nav-link" data-topic="27">
        <span class="nav-icon">🔐</span>
        <span class="nav-text">27. Android Security</span>
        <span class="topic-progress" data-topic-progress="27">0%</span>
      </a>
      <a class="nav-link" data-topic="28">
        <span class="nav-icon">🧪</span>
        <span class="nav-text">28. Testing (JUnit, MockK, Espresso)</span>
        <span class="topic-progress" data-topic-progress="28">0%</span>
      </a>
      <a class="nav-link" data-topic="29">
        <span class="nav-icon">⚡</span>
        <span class="nav-text">29. Android Performance</span>
        <span class="topic-progress" data-topic-progress="29">0%</span>
      </a>
      <a class="nav-link" data-topic="30">
        <span class="nav-icon">🧠</span>
        <span class="nav-text">30. Memory Management</span>
        <span class="topic-progress" data-topic-progress="30">0%</span>
      </a>

      <div class="nav-section-label">Build &amp; Distribution</div>
      <a class="nav-link" data-topic="31">
        <span class="nav-icon">🔨</span>
        <span class="nav-text">31. Gradle &amp; Build System</span>
        <span class="topic-progress" data-topic-progress="31">0%</span>
      </a>
      <a class="nav-link" data-topic="32">
        <span class="nav-icon">📦</span>
        <span class="nav-text">32. App Modularization</span>
        <span class="topic-progress" data-topic-progress="32">0%</span>
      </a>
      <a class="nav-link" data-topic="33">
        <span class="nav-icon">🚦</span>
        <span class="nav-text">33. CI/CD Pipelines</span>
        <span class="topic-progress" data-topic-progress="33">0%</span>
      </a>
      <a class="nav-link" data-topic="34">
        <span class="nav-icon">🔑</span>
        <span class="nav-text">34. Android Permissions</span>
        <span class="topic-progress" data-topic-progress="34">0%</span>
      </a>

      <div class="nav-section-label">UI &amp; Data</div>
      <a class="nav-link" data-topic="35">
        <span class="nav-icon">📋</span>
        <span class="nav-text">35. RecyclerView &amp; Lists</span>
        <span class="topic-progress" data-topic-progress="35">0%</span>
      </a>
      <a class="nav-link" data-topic="36">
        <span class="nav-icon">📄</span>
        <span class="nav-text">36. Paging 3 Library</span>
        <span class="topic-progress" data-topic-progress="36">0%</span>
      </a>
      <a class="nav-link" data-topic="37">
        <span class="nav-icon">🔥</span>
        <span class="nav-text">37. Firebase in Android</span>
        <span class="topic-progress" data-topic-progress="37">0%</span>
      </a>

      <div class="nav-section-label">Senior Level</div>
      <a class="nav-link" data-topic="38">
        <span class="nav-icon">🏛️</span>
        <span class="nav-text">38. Android System Design</span>
        <span class="topic-progress" data-topic-progress="38">0%</span>
      </a>
      <a class="nav-link" data-topic="39">
        <span class="nav-icon">📦</span>
        <span class="nav-text">39. App Release &amp; Distribution</span>
        <span class="topic-progress" data-topic-progress="39">0%</span>
      </a>
      <a class="nav-link" data-topic="40">
        <span class="nav-icon">💻</span>
        <span class="nav-text">40. DSA Coding (Kotlin)</span>
        <span class="topic-progress" data-topic-progress="40">0%</span>
      </a>
      <a class="nav-link" data-topic="41">
        <span class="nav-icon">🎤</span>
        <span class="nav-text">41. Behavioral &amp; Leadership</span>
        <span class="topic-progress" data-topic-progress="41">0%</span>
      </a>
    </nav>

    <div class="sidebar-footer">
      <div class="overall-progress-label">
        <span>Curriculum Mastery</span>
        <span class="overall-progress-text">0%</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill overall-progress" style="width: 0%">0%</div>
      </div>
      <button class="theme-toggle" type="button" aria-label="Toggle theme">☀️ Light Mode</button>
    </div>
  </aside>

  <!-- Main Content Area -->
  <main class="main-content">

    <!-- Global Instant Search -->
    <div class="search-box">
      <span class="search-icon">🔍</span>
      <input type="text" id="search-input" placeholder="Search across all 41 modules, code, and interview questions... (Ctrl+K / ⌘K)" autocomplete="off">
      <div id="search-results" class="search-results"></div>
    </div>

    <!-- ============================================= -->
    <!-- TOPIC 0: EXECUTIVE DASHBOARD & OVERVIEW       -->
    <!-- ============================================= -->
    <section class="topic-section active" id="topic-0">
      <div class="hero">
        <h1>🤖 Android Senior Interview Mastery</h1>
        <p class="hero-subtitle">
          The most comprehensive Android interview preparation platform. Covers <strong>41 modules</strong> across Kotlin, Coroutines, Flow, Jetpack Compose, Clean Architecture, Hilt, Retrofit, Room, WorkManager, Security, Testing, Performance, CI/CD, System Design, DSA &amp; Behavioral — all with 9-pillar deep dive.
        </p>
        <div class="hero-stats flex gap-3 flex-wrap mt-3">
          <div class="stat-card">
            <span class="stat-number">41</span>
            <span class="stat-label">Master Modules</span>
          </div>
          <div class="stat-card">
            <span class="stat-number">200+</span>
            <span class="stat-label">Interview Q&amp;As (3D Flip Cards)</span>
          </div>
          <div class="stat-card">
            <span class="stat-number">9</span>
            <span class="stat-label">Pillars Per Topic</span>
          </div>
          <div class="stat-card">
            <span class="stat-number">7+ YoE</span>
            <span class="stat-label">Target Interview Bar</span>
          </div>
        </div>
      </div>

      <!-- The 9 Pillars -->
      <div class="card card-what mt-4">
        <h3>🏛️ The 9 Pillars of Every Topic</h3>
        <p>To master any Android topic at a Senior / Staff level, each section is structured into 9 foundational pillars:</p>
        <ul style="margin-left: 1.25rem; line-height: 1.9; margin-top: 0.5rem;">
          <li><strong>1. ❓ Why?</strong> — The architectural problem or failure mode this solves.</li>
          <li><strong>2. 🔷 What?</strong> — Technical definition with internal mechanism.</li>
          <li><strong>3. 🛠️ How?</strong> — Production-ready Kotlin code with comments.</li>
          <li><strong>4. 📝 Syntax &amp; Key APIs</strong> — Core syntax patterns and API reference.</li>
          <li><strong>5. 🏭 Real-World Example</strong> — FinTech / Healthcare / Automotive / E-Commerce case study.</li>
          <li><strong>6. ⚠️ Common Mistakes</strong> — Bugs and gotchas you MUST know and how to fix them.</li>
          <li><strong>7. 🎤 Senior-Level Pitch</strong> — The 60-second answer a staff engineer gives in interviews.</li>
          <li><strong>8. 🎯 Interview Q&amp;As</strong> — 3D flip card questions (Basic → Advanced → Scenario).</li>
          <li><strong>9. 💻 Coding Challenge</strong> — Real coding problem with complete Kotlin solution.</li>
        </ul>
      </div>

      <!-- Comprehensive 41-Module Curriculum Grid -->
      <h2 class="mt-4 mb-2">📚 Master Curriculum — All 41 Modules</h2>
      <div class="topic-grid">
        <!-- 1-12 -->
        <div class="card" onclick="document.querySelector('[data-topic=&quot;1&quot;]').click();">
          <h3>⚡ 1. Kotlin Core &amp; Advanced</h3>
          <p class="text-secondary">inline/reified/noinline, sealed classes, sequences, delegation, coroutines, generics, variance.</p>
          <div class="category-badge-group"><span class="cat-pill">Kotlin</span><span class="cat-pill">Bytecode</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;2&quot;]').click();">
          <h3>📱 2. Components &amp; Lifecycles</h3>
          <p class="text-secondary">Activity/Fragment lifecycles, viewLifecycleOwner, Process Death vs Rotation, SavedStateHandle.</p>
          <div class="category-badge-group"><span class="cat-pill">Android SDK</span><span class="cat-pill">Lifecycle</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;3&quot;]').click();">
          <h3>⚙️ 3. Services &amp; WorkManager</h3>
          <p class="text-secondary">Started/Bound/Foreground Services, Android 14 requirements, WorkManager chaining, Doze mode.</p>
          <div class="category-badge-group"><span class="cat-pill">Services</span><span class="cat-pill">WorkManager</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;4&quot;]').click();">
          <h3>🎨 4. Jetpack Compose Internals 🔥</h3>
          <p class="text-secondary">Slot tables, stability, recomposition compiler bitmasks, derivedStateOf, side effects.</p>
          <div class="category-badge-group"><span class="cat-pill">Compose</span><span class="cat-pill">Tier 1</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;5&quot;]').click();">
          <h3>🏛️ 5. ViewModel, Room &amp; State</h3>
          <p class="text-secondary">ViewModelStore retain mechanism, StateFlow vs SharedFlow, Room relational schemas, safe migrations.</p>
          <div class="category-badge-group"><span class="cat-pill">Room</span><span class="cat-pill">StateFlow</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;6&quot;]').click();">
          <h3>🌐 6. Retrofit, OkHttp &amp; Coil</h3>
          <p class="text-secondary">Thread-safe 401 token refresh Authenticator, offline caching with CacheControl, Coil vs Glide.</p>
          <div class="category-badge-group"><span class="cat-pill">Networking</span><span class="cat-pill">OkHttp</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;7&quot;]').click();">
          <h3>💉 7. Dependency Injection (Hilt)</h3>
          <p class="text-secondary">Hilt component hierarchy, @Binds vs @Provides, multibindings, testing with Hilt.</p>
          <div class="category-badge-group"><span class="cat-pill">Hilt</span><span class="cat-pill">DI</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;8&quot;]').click();">
          <h3>📐 8. Architecture (MVP, MVVM, MVI)</h3>
          <p class="text-secondary">Evolution from MVP to MVVM and MVI, Clean Architecture layer boundaries, Domain purity.</p>
          <div class="category-badge-group"><span class="cat-pill">Clean Arch</span><span class="cat-pill">MVI</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;9&quot;]').click();">
          <h3>🔄 9. Concurrency &amp; Coroutines</h3>
          <p class="text-secondary">coroutineScope vs supervisorScope failure isolation, Flow backpressure, repeatOnLifecycle.</p>
          <div class="category-badge-group"><span class="cat-pill">Coroutines</span><span class="cat-pill">Turbine</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;10&quot;]').click();">
          <h3>🔒 10. Hardware KeyStore &amp; Security</h3>
          <p class="text-secondary">TEE/StrongBox hardware keys, biometric gating, zero-downtime SSL Pinning, Play Integrity.</p>
          <div class="category-badge-group"><span class="cat-pill">KeyStore</span><span class="cat-pill">Security</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;11&quot;]').click();">
          <h3>🚀 11. Performance &amp; CI/CD Gates</h3>
          <p class="text-secondary">Baseline Profiles AOT pre-compilation, Macrobenchmark P99 frame duration gates, LeakCanary.</p>
          <div class="category-badge-group"><span class="cat-pill">Performance</span><span class="cat-pill">Baseline</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;12&quot;]').click();">
          <h3>🤖 12. AOSP &amp; On-Device AI</h3>
          <p class="text-secondary">Binder single-copy IPC, AIDL oneway, clearCallingIdentity privilege escalation fixes, Gemini Nano.</p>
          <div class="category-badge-group"><span class="cat-pill">Binder IPC</span><span class="cat-pill">Gemini Nano</span></div>
        </div>

        <!-- 13-22 -->
        <div class="card" onclick="document.querySelector('[data-topic=&quot;13&quot;]').click();">
          <h3>📱 13. Android Fundamentals</h3>
          <p class="text-secondary">Activity &amp; Fragment lifecycles, Intent flags, launchModes, Back Stack, Task Affinity, Context types.</p>
          <div class="category-badge-group"><span class="cat-pill">Lifecycle</span><span class="cat-pill">Core</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;14&quot;]').click();">
          <h3>🔁 14. Kotlin Coroutines Deep Dive 🔥</h3>
          <p class="text-secondary">Dispatchers, Job hierarchy, supervisorScope, async/await, Structured Concurrency, cancellation.</p>
          <div class="category-badge-group"><span class="cat-pill">Coroutines</span><span class="cat-pill">Tier 1</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;15&quot;]').click();">
          <h3>🌊 15. Kotlin Flow Deep Dive 🔥</h3>
          <p class="text-secondary">Cold flows vs Hot streams, StateFlow vs SharedFlow vs LiveData, buffer, conflate, flatMapLatest.</p>
          <div class="category-badge-group"><span class="cat-pill">Flow</span><span class="cat-pill">Tier 1</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;16&quot;]').click();">
          <h3>🏗️ 16. Architecture Evolution</h3>
          <p class="text-secondary">From MVC to MVP, MVVM, MVI and Clean Architecture. Unidirectional Data Flow &amp; State machines.</p>
          <div class="category-badge-group"><span class="cat-pill">UDF</span><span class="cat-pill">MVI</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;17&quot;]').click();">
          <h3>📏 17. SOLID Principles in Android</h3>
          <p class="text-secondary">SRP, OCP, LSP, ISP, DIP applied with concrete Android scenarios, repository patterns, interface segregation.</p>
          <div class="category-badge-group"><span class="cat-pill">SOLID</span><span class="cat-pill">Clean Code</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;18&quot;]').click();">
          <h3>🧩 18. Design Patterns in Android</h3>
          <p class="text-secondary">Creational (Factory/Builder/Singleton), Structural (Adapter/Decorator/Facade), Behavioral (Observer/Strategy/Command).</p>
          <div class="category-badge-group"><span class="cat-pill">Patterns</span><span class="cat-pill">GoF</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;19&quot;]').click();">
          <h3>💉 19. DI — Hilt &amp; Dagger 2 Deep Dive</h3>
          <p class="text-secondary">Component hierarchy, @Binds vs @Provides, qualifiers, multibindings, AssistedInject, TestInstallIn.</p>
          <div class="category-badge-group"><span class="cat-pill">Hilt</span><span class="cat-pill">Dagger 2</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;20&quot;]').click();">
          <h3>🌐 20. Networking Deep Dive</h3>
          <p class="text-secondary">Retrofit + Moshi, custom OkHttp Interceptors, mutex token refresh, SSL Pinning, Offline cache.</p>
          <div class="category-badge-group"><span class="cat-pill">Retrofit</span><span class="cat-pill">OkHttp</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;21&quot;]').click();">
          <h3>🗄️ 21. Room &amp; Local Storage</h3>
          <p class="text-secondary">Entities, DAOs, 1:N &amp; M:N relationships, AutoMigration, DataStore vs Room vs SharedPreferences.</p>
          <div class="category-badge-group"><span class="cat-pill">Room</span><span class="cat-pill">DataStore</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;22&quot;]').click();">
          <h3>⚙️ 22. WorkManager &amp; Background Processing</h3>
          <p class="text-secondary">CoroutineWorker, Constraints, Chaining, Expedited work, Doze Mode, Hilt worker injection.</p>
          <div class="category-badge-group"><span class="cat-pill">WorkManager</span><span class="cat-pill">Background</span></div>
        </div>

        <!-- 23-32 -->
        <div class="card" onclick="document.querySelector('[data-topic=&quot;23&quot;]').click();">
          <h3>🔧 23. Android Services</h3>
          <p class="text-secondary">Started, Bound &amp; Foreground services, AIDL IPC, Messenger, Android 14 foregroundServiceType.</p>
          <div class="category-badge-group"><span class="cat-pill">Services</span><span class="cat-pill">AIDL</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;24&quot;]').click();">
          <h3>📡 24. BroadcastReceiver</h3>
          <p class="text-secondary">Static vs Dynamic registration, ordered broadcasts, security permissions, Android 14 export requirements.</p>
          <div class="category-badge-group"><span class="cat-pill">Broadcast</span><span class="cat-pill">Android 14</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;25&quot;]').click();">
          <h3>📂 25. ContentProvider &amp; File Sharing</h3>
          <p class="text-secondary">CRUD with ContentResolver, UriMatcher, FileProvider secure URI grant, inter-app data sharing.</p>
          <div class="category-badge-group"><span class="cat-pill">ContentProvider</span><span class="cat-pill">FileProvider</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;26&quot;]').click();">
          <h3>🗺️ 26. Navigation &amp; Deep Linking</h3>
          <p class="text-secondary">NavController, NavGraph, Safe Args, Deep Links, Nested Graphs, back stack saveState/restoreState.</p>
          <div class="category-badge-group"><span class="cat-pill">Navigation</span><span class="cat-pill">Deep Links</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;27&quot;]').click();">
          <h3>🔐 27. Android Security</h3>
          <p class="text-secondary">Hardware KeyStore, Biometric auth, SSL Pinning, ProGuard/R8, EncryptedSharedPreferences, Play Integrity.</p>
          <div class="category-badge-group"><span class="cat-pill">KeyStore</span><span class="cat-pill">Biometrics</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;28&quot;]').click();">
          <h3>🧪 28. Testing (Unit, Turbine, Espresso, Compose)</h3>
          <p class="text-secondary">JUnit5, MockK, Turbine for Flow testing, Compose TestRule, CoroutineTestRule, MockWebServer.</p>
          <div class="category-badge-group"><span class="cat-pill">Testing</span><span class="cat-pill">Turbine</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;29&quot;]').click();">
          <h3>⚡ 29. Android Performance</h3>
          <p class="text-secondary">ANR diagnosis, 16ms frame budget, Systrace, Perfetto, Baseline Profiles, Macrobenchmark, Overdraw.</p>
          <div class="category-badge-group"><span class="cat-pill">Performance</span><span class="cat-pill">ANR</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;30&quot;]').click();">
          <h3>🧠 30. Memory Management</h3>
          <p class="text-secondary">GC types, Strong/Weak/Soft references, LeakCanary internals, Bitmap pooling, onTrimMemory.</p>
          <div class="category-badge-group"><span class="cat-pill">Memory</span><span class="cat-pill">LeakCanary</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;31&quot;]').click();">
          <h3>🔨 31. Gradle &amp; Build System</h3>
          <p class="text-secondary">Gradle lifecycle, AGP, build variants, product flavors, buildConfig, Kotlin DSL, build cache.</p>
          <div class="category-badge-group"><span class="cat-pill">Gradle</span><span class="cat-pill">Kotlin DSL</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;32&quot;]').click();">
          <h3>📦 32. App Modularization</h3>
          <p class="text-secondary">Feature modules, :core vs :feature vs :app, api/impl pattern, dynamic delivery, build parallelization.</p>
          <div class="category-badge-group"><span class="cat-pill">Modularization</span><span class="cat-pill">Architecture</span></div>
        </div>

        <!-- 33-41 -->
        <div class="card" onclick="document.querySelector('[data-topic=&quot;33&quot;]').click();">
          <h3>🚦 33. CI/CD Pipelines</h3>
          <p class="text-secondary">GitHub Actions / GitLab CI, Fastlane lanes, automated test gates, signing configs, Play Store release.</p>
          <div class="category-badge-group"><span class="cat-pill">CI/CD</span><span class="cat-pill">Fastlane</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;34&quot;]').click();">
          <h3>🔑 34. Android Permissions</h3>
          <p class="text-secondary">Runtime permissions flow, Activity Result API, rationale dialog, Android 13+ granular media, background location.</p>
          <div class="category-badge-group"><span class="cat-pill">Permissions</span><span class="cat-pill">Android 13</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;35&quot;]').click();">
          <h3>📋 35. RecyclerView &amp; Lists</h3>
          <p class="text-secondary">ViewHolder pattern, DiffUtil payloads, ListAdapter, multiple view types, ConcatAdapter, ItemDecoration.</p>
          <div class="category-badge-group"><span class="cat-pill">RecyclerView</span><span class="cat-pill">DiffUtil</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;36&quot;]').click();">
          <h3>📄 36. Paging 3 Library</h3>
          <p class="text-secondary">PagingSource, RemoteMediator, PagingData, LoadState UI, offline-first network+cache pagination.</p>
          <div class="category-badge-group"><span class="cat-pill">Paging 3</span><span class="cat-pill">RemoteMediator</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;37&quot;]').click();">
          <h3>🔥 37. Firebase in Android</h3>
          <p class="text-secondary">Firebase Auth, Firestore real-time listeners, FCM notifications, Remote Config, Crashlytics custom keys.</p>
          <div class="category-badge-group"><span class="cat-pill">Firebase</span><span class="cat-pill">FCM</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;38&quot;]').click();">
          <h3>🏛️ 38. Android System Design</h3>
          <p class="text-secondary">Design News Feed, Offline-First Architecture, Real-Time Chat with WebSocket, Resilient Payment SDK.</p>
          <div class="category-badge-group"><span class="cat-pill">System Design</span><span class="cat-pill">Staff</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;39&quot;]').click();">
          <h3>📦 39. App Release &amp; Distribution</h3>
          <p class="text-secondary">APK vs AAB, R8/ProGuard shrinking, Keystore signing, Play Store staged rollouts, In-App Updates.</p>
          <div class="category-badge-group"><span class="cat-pill">Release</span><span class="cat-pill">Play Console</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;40&quot;]').click();">
          <h3>💻 40. DSA Coding in Kotlin</h3>
          <p class="text-secondary">Two Sum, LRU Cache, Linked List cycle &amp; reversal, Binary Search, Sliding Window, DP in idiomatic Kotlin.</p>
          <div class="category-badge-group"><span class="cat-pill">DSA</span><span class="cat-pill">LeetCode</span></div>
        </div>
        <div class="card" onclick="document.querySelector('[data-topic=&quot;41&quot;]').click();">
          <h3>🎤 41. Senior Behavioral &amp; Leadership</h3>
          <p class="text-secondary">STAR method interview responses: Conflict resolution, technical debt tradeoffs, mentoring, incident handling.</p>
          <div class="category-badge-group"><span class="cat-pill">Leadership</span><span class="cat-pill">STAR</span></div>
        </div>
      </div>
    </section>
'''

html_footer = '''
  </main>

  <!-- Master JavaScript Application Controller -->
  <script src="js/app.js"></script>
</body>
</html>
'''

print("Building topic HTML sections...")
parts = [
    html_header,
    get_topics_1_to_3_html(),
    get_topics_4_to_6_html(),
    get_topics_7_to_9_html(),
    get_topics_10_to_12_html(),
    get_topics_13_to_17_html(),
    get_topics_18_to_22_html(),
    get_topics_23_to_27_html(),
    get_topics_28_to_32_html(),
    get_topics_33_to_37_html(),
    get_topics_38_to_40_html(),
    html_footer,
]

full_html = "".join(parts)

output_path = "/Users/satdevkumar/.gemini/antigravity/scratch/android-interview-prep/index.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(full_html)

size_kb = len(full_html) // 1024
print(f"Successfully assembled index.html! Total size: {len(full_html)} bytes ({size_kb} KB)")
print(f"Topics covered: 41 modules, 9-pillar structure")
print(f"Server URL: http://localhost:8080")
