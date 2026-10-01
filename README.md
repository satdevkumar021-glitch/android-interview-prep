# 🤖 Android Senior & Staff Interview Mastery Platform

> The definitive end-to-end Android Senior & Staff Engineer Interview Preparation platform.
> Featuring **41 Master Modules**, **74 Subtopics**, **234 Interactive 3D Flip Cards**, **292 Production Code Blocks**, and **205 Dynamic Progress Tracking Items** built with an encyclopedic **9-Pillar** technical breakdown.

---

## 🌟 The 9-Pillar Structure for Every Topic

Every single concept in this curriculum is broken down into 9 foundational pillars:

1. **❓ Why do we need this?** — The architectural pain point, concurrency race condition, or memory leak it solves.
2. **🔷 What is it?** — Technical definition, memory model, and internal framework mechanics.
3. **🛠️ How do we use it?** — Production-ready, fully commented Kotlin and Android code.
4. **📝 Syntax & Key APIs** — Core syntax patterns, annotations, and API reference.
5. **🏭 Real-World Production Example** — Concrete production case studies in FinTech (PCI-DSS), Healthcare (HIPAA/FHIR), Automotive (AOSP/IVI), and E-Commerce.
6. **⚠️ Common Mistakes & Gotchas** — Subtle production bugs, anti-patterns, and verified fixes.
7. **🎤 Senior-Level Pitch** — 60-second elevator pitch to articulate like a Principal/Staff Engineer.
8. **🎯 Interview Questions & Answers** — Interactive 3D Flip Cards (`Basic`, `Advanced`, `Scenario`).
9. **💻 Coding Challenge** — Real interview coding problems with idiomatic Kotlin solutions and complexity analysis.

---

## 📚 Complete 41-Module Curriculum Index

### Section 1: Kotlin & Core Architecture
- **Topic 1:** Kotlin Core & Advanced (`inline`/`crossinline`/`noinline`, `reified`, `LazyThreadSafetyMode`, Value Classes, Sequences)
- **Topic 2:** Component Lifecycles & Process Death (`viewLifecycleOwner`, `SavedStateHandle`, `FLAG_IMMUTABLE`, state survival)
- **Topic 3:** Services & Background Processing (Started/Bound/Foreground, Android 14 `foregroundServiceType`, `WorkManager` chaining)
- **Topic 4:** Jetpack Compose Internals (Slot Tables, `$changed` bitmask, `@Immutable`/`@Stable`, recomposition storms, SideEffects)
- **Topic 5:** ViewModel, Room & StateFlow (`ViewModelStore`, `StateFlow` vs `SharedFlow` vs Channels, Room migrations, `DataStore`)
- **Topic 6:** Retrofit, OkHttp & Coil (Thread-safe 401 token refresh `Authenticator`, `CacheControl`, Coil vs Glide, Moshi vs Serialization)
- **Topic 7:** Dependency Injection (Hilt & Dagger) (Component hierarchy, `@Binds` vs `@Provides`, multibindings, test isolation)
- **Topic 8:** Architecture (MVP, MVVM, MVI) (Clean Architecture, Inward Dependency Rule, Domain purity, `:api`/`:impl` pattern)
- **Topic 9:** Concurrency & Coroutines (`coroutineScope` vs `supervisorScope`, Flow backpressure, `repeatOnLifecycle`, Turbine testing)
- **Topic 10:** Hardware KeyStore & Security (TEE/StrongBox hardware keys, biometric gating, SSL Pinning with backup pins, Play Integrity)
- **Topic 11:** Performance & CI/CD Gates (Baseline Profiles AOT, Macrobenchmark P99 gates, LeakCanary internals, Fastlane)
- **Topic 12:** AOSP & On-Device AI (Binder single-copy IPC, AIDL `oneway`, `clearCallingIdentity`, Gemini Nano on-device AI)

### Section 2: Deep Dive Syllabus
- **Topic 13:** Android Fundamentals (Activity/Fragment lifecycles, Intent flags, launchModes, Back Stack, Task Affinity, Context types)
- **Topic 14:** Kotlin Coroutines Deep Dive (Dispatchers, Job hierarchy, structured concurrency, cancellation, exception handling)
- **Topic 15:** Kotlin Flow Deep Dive (Cold flows vs Hot streams, `StateFlow` vs `SharedFlow` vs `LiveData`, `buffer`, `conflate`, `flatMapLatest`)
- **Topic 16:** Architecture Evolution (MVC &rarr; MVP &rarr; MVVM &rarr; MVI &rarr; Clean Architecture, UDF state machines)
- **Topic 17:** SOLID Principles in Android (SRP, OCP, LSP, ISP, DIP applied with concrete Android repositories and UseCases)
- **Topic 18:** Design Patterns in Android (Creational: Factory/Builder/Singleton; Structural: Adapter/Decorator/Facade; Behavioral: Observer/Strategy/Command)
- **Topic 19:** DI — Hilt & Dagger 2 Deep Dive (Component hierarchy, scopes, qualifiers, multibindings, `@AssistedInject`, `@TestInstallIn`)
- **Topic 20:** Networking Deep Dive (Retrofit + Moshi, custom OkHttp Interceptors, mutex token refresh, SSL Pinning, offline cache)
- **Topic 21:** Room & Local Storage (Entities, DAOs, 1:N & M:N relationships, AutoMigration, DataStore vs Room vs SharedPreferences)
- **Topic 22:** WorkManager & Background Processing (`CoroutineWorker`, constraints, chaining, expedited work, Doze Mode, Hilt worker injection)

### Section 3: Android Components & Framework
- **Topic 23:** Android Services (Started, Bound & Foreground services, AIDL IPC, Messenger, Android 14 `foregroundServiceType`)
- **Topic 24:** BroadcastReceiver (Static vs Dynamic registration, ordered broadcasts, security permissions, Android 14 export requirements)
- **Topic 25:** ContentProvider & File Sharing (CRUD with `ContentResolver`, `UriMatcher`, `FileProvider` secure URI grant, inter-app data sharing)
- **Topic 26:** Navigation Component & Deep Linking (`NavController`, `NavGraph`, Safe Args, Deep Links, Nested Graphs, back stack save/restore)
- **Topic 27:** Android Security (Hardware KeyStore, Biometric auth, SSL Pinning, ProGuard/R8, `EncryptedSharedPreferences`, Play Integrity)

### Section 4: Quality, Performance & Build Systems
- **Topic 28:** Testing (JUnit5, MockK, Turbine for Flow testing, Compose TestRule, CoroutineTestRule, MockWebServer)
- **Topic 29:** Android Performance (ANR diagnosis, 16ms frame budget, Systrace, Perfetto, Baseline Profiles, Macrobenchmark, Overdraw)
- **Topic 30:** Memory Management (GC types, Strong/Weak/Soft references, LeakCanary internals, Bitmap pooling, `onTrimMemory`)
- **Topic 31:** Gradle & Build System (Gradle lifecycle, AGP, build variants, product flavors, `buildConfig`, Kotlin DSL, build cache)
- **Topic 32:** App Modularization (Feature modules, `:core` vs `:feature` vs `:app`, `api`/`impl` pattern, dynamic delivery, build parallelization)

### Section 5: Distribution, Lists, Cloud & Senior Level
- **Topic 33:** CI/CD Pipelines (GitHub Actions / GitLab CI, Fastlane lanes, automated test gates, signing configs, Play Store release)
- **Topic 34:** Android Permissions (Runtime permissions flow, Activity Result API, rationale dialog, Android 13+ granular media, background location)
- **Topic 35:** RecyclerView & Lists (`ViewHolder` pattern, `DiffUtil` payloads, `ListAdapter`, multiple view types, `ConcatAdapter`, `ItemDecoration`)
- **Topic 36:** Paging 3 Library (`PagingSource`, `RemoteMediator`, `PagingData`, `LoadState` UI, offline-first network+cache pagination)
- **Topic 37:** Firebase in Android (Firebase Auth, Firestore real-time listeners, FCM notifications, Remote Config, Crashlytics custom keys)
- **Topic 38:** Android System Design (Design News Feed, Offline-First Architecture, Real-Time Chat with WebSocket, Resilient Payment SDK)
- **Topic 39:** App Release & Distribution (APK vs AAB, R8/ProGuard shrinking, Keystore signing, Play Store staged rollouts, In-App Updates)
- **Topic 40:** DSA Coding in Kotlin (Two Sum, LRU Cache, Linked List cycle & reversal, Binary Search, Sliding Window, DP in idiomatic Kotlin)
- **Topic 41:** Senior Behavioral & Leadership (STAR method interview responses: Conflict resolution, technical debt tradeoffs, mentoring, incident handling)

---

## 🎮 Interactive Features

- **3D Interactive Flip Cards**: First test yourself with the question and difficulty badge, then click or press Spacebar to flip the card and reveal the Staff-level explanation and Kotlin code.
- **🎴 Fullscreen Anki-Style Practice Deck**: Distraction-free practice mode with keyboard shortcuts (`Space` to flip, `ArrowLeft`/`ArrowRight` to step, `Esc` to exit).
- **📊 Real-Time Dynamic Progress Tracking**: Topic percentage badges update from `0%` &rarr; `100%` in the sidebar and persist across browser reloads via `localStorage`.
- **🔍 Global Instant Search (`Ctrl+K` / `⌘K`)**: Debounced real-time search across all 41 modules, subtopics, code blocks, and 234 Q&As.
- **📋 One-Click Code Copy**: Copy any Kotlin snippet to clipboard.
- **🌓 Dark / Light Mode**: Seamless theme switching with persistent settings.

---

## 🚀 Running Locally

```bash
# Clone the repository
git clone https://github.com/satdevkumar021-glitch/android-interview-prep.git
cd android-interview-prep

# Start local server
./start.sh
# Or with Python:
python3 -m http.server 8080
```
Open [http://localhost:8080](http://localhost:8080) in your browser.
