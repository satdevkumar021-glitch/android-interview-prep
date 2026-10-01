# html_topic_33_to_37.py
# Topics: CI/CD, Android Permissions, RecyclerView, Paging 3, Firebase

def get_topics_33_to_37_html():
    return '''
<!-- ==================== TOPIC 33: CI/CD for Android ==================== -->
<section class="topic-section" id="topic-33">
  <div class="topic-header">
    <div class="topic-header-icon">🔄</div>
    <div class="topic-header-text">
      <h1>CI/CD for Android</h1>
      <p class="topic-tagline">Automate everything: build, test, sign, and ship Android apps at scale</p>
      <div class="category-badge-group">
        <span class="cat-pill">DevOps</span>
        <span class="cat-pill">GitHub Actions</span>
        <span class="cat-pill">Fastlane</span>
        <span class="cat-pill">Play Store</span>
      </div>
    </div>
  </div>

  <div class="subtopic" id="subtopic-33-1">
    <h2>GitHub Actions &amp; GitLab CI Pipelines</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need CI/CD?</h3>
      <p>Without CI/CD, Android teams hit a wall: builds break silently, PRs merge with failing tests, signing keys are shared manually, and releases take days of manual effort. In a team of 10+ engineers pushing code daily, a broken master branch can cost hours of debugging time. CI/CD solves this by enforcing a repeatable, automated pipeline: every commit triggers compilation, lint, unit tests, instrumented tests, security scanning, signing, and deployment—all without human intervention. For production apps (FinTech, Healthcare), CI/CD gates prevent regressions from reaching millions of users and provide an audit trail for every release artifact.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is CI/CD for Android?</h3>
      <p><strong>Continuous Integration (CI)</strong> automatically validates code quality on every push/PR: compiles the project, runs lint checks, executes unit tests, and optionally runs instrumented tests on Firebase Test Lab or emulators. <strong>Continuous Delivery/Deployment (CD)</strong> automatically packages and distributes the app: signs the AAB/APK with production keys stored as CI secrets, uploads to Google Play internal/alpha/beta tracks via the Play Developer API, or distributes to QA via Firebase App Distribution. The pipeline is defined as code (YAML) and versioned alongside source code.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <p>A GitHub Actions workflow triggers on push/PR, spins up an Ubuntu runner, checks out code, sets up the JDK, restores Gradle caches, runs tests, and on the main branch also signs and uploads the bundle. Secrets (keystore, API keys) are stored encrypted in GitHub Settings and injected as environment variables at runtime.</p>
      <pre class="code-block"><code class="language-yaml"># .github/workflows/android-ci.yml
name: Android CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  JAVA_VERSION: '17'
  GRADLE_OPTS: "-Dorg.gradle.daemon=false -Dorg.gradle.parallel=true"

jobs:
  # ─── CI: Build + Test ───────────────────────────────────────────────
  build-and-test:
    runs-on: ubuntu-latest
    timeout-minutes: 45

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for Sonar analysis

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: ${{ env.JAVA_VERSION }}
          distribution: 'temurin'

      # ── Gradle cache: key = wrapper + build files ──────────────────
      - name: Cache Gradle packages
        uses: actions/cache@v4
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: gradle-${{ runner.os }}-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties', '**/libs.versions.toml') }}
          restore-keys: gradle-${{ runner.os }}-

      - name: Grant execute permission to gradlew
        run: chmod +x gradlew

      - name: Run lint
        run: ./gradlew lint --stacktrace

      - name: Run unit tests
        run: ./gradlew testDebugUnitTest --stacktrace

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: '**/build/reports/tests/'

      - name: Build debug APK
        run: ./gradlew assembleDebug --stacktrace

  # ─── CD: Sign + Deploy (main branch only) ───────────────────────────
  deploy:
    needs: build-and-test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    timeout-minutes: 30

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: ${{ env.JAVA_VERSION }}
          distribution: 'temurin'

      - name: Cache Gradle packages
        uses: actions/cache@v4
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: gradle-${{ runner.os }}-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}

      # Decode keystore from base64 secret
      - name: Decode keystore
        run: |
          echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 --decode > keystore.jks

      - name: Build release bundle
        env:
          KEYSTORE_PATH: keystore.jks
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
          STORE_PASSWORD: ${{ secrets.STORE_PASSWORD }}
        run: ./gradlew bundleRelease --stacktrace

      - name: Upload AAB to Play Store (internal track)
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.SERVICE_ACCOUNT_JSON }}
          packageName: com.company.myapp
          releaseFiles: app/build/outputs/bundle/release/*.aab
          track: internal
          status: completed</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 build.gradle Signing Config</h3>
      <pre class="code-block"><code class="language-kotlin">// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            // Read from environment variables injected by CI
            storeFile = file(System.getenv("KEYSTORE_PATH") ?: "keystore.jks")
            storePassword = System.getenv("STORE_PASSWORD") ?: properties["storePassword"].toString()
            keyAlias = System.getenv("KEY_ALIAS") ?: properties["keyAlias"].toString()
            keyPassword = System.getenv("KEY_PASSWORD") ?: properties["keyPassword"].toString()
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            signingConfig = signingConfigs.getByName("release")
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}

// Build output naming: app-1.2.3-release.aab
android.applicationVariants.all {
    val variant = this
    variant.outputs.all {
        val output = this as? com.android.build.gradle.internal.api.BaseVariantOutputImpl
        output?.outputFileName = "app-${variant.versionName}-${variant.buildType.name}.apk"
    }
}</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World: FinTech App CI/CD with Security Gates</h3>
      <p>A banking app pipeline adds security scanning (MobSF, Snyk) and requires code coverage thresholds before merging. It also uses matrix builds to test against multiple API levels.</p>
      <pre class="code-block"><code class="language-yaml"># .github/workflows/fintech-ci.yml
jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Snyk to check for vulnerabilities
        uses: snyk/actions/gradle@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

  instrumented-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        api-level: [26, 31, 34]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - name: AVD cache
        uses: actions/cache@v4
        with:
          path: ~/.android/avd/*
          key: avd-${{ matrix.api-level }}
      - name: Run instrumented tests on API ${{ matrix.api-level }}
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: ${{ matrix.api-level }}
          arch: x86_64
          profile: Nexus 6
          script: ./gradlew connectedDebugAndroidTest --stacktrace

  enforce-coverage:
    needs: [security-scan, instrumented-tests]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate coverage report
        run: ./gradlew jacocoTestReport
      - name: Enforce 80% coverage
        run: |
          COVERAGE=$(python3 scripts/parse_coverage.py)
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "Coverage $COVERAGE% is below 80% threshold"
            exit 1
          fi</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Committing keystore or passwords to Git:</strong> Even in private repos, this is a critical security breach — ✅ Fix: Store keystore as a base64-encoded GitHub/GitLab secret, decode at runtime, delete after build</li>
        <li>❌ <strong>Not caching Gradle dependencies:</strong> Each run downloads all dependencies (~5-15 min) — ✅ Fix: Cache <code>~/.gradle/caches</code> keyed on build files hash; saves 5-10 min per run</li>
        <li>❌ <strong>Using APK instead of AAB for Play Store:</strong> Play Store requires AAB since August 2021 — ✅ Fix: Use <code>bundleRelease</code> task, not <code>assembleRelease</code></li>
        <li>❌ <strong>Running full instrumented tests on every PR:</strong> 20+ minute wait kills developer velocity — ✅ Fix: Run instrumented tests only on main branch; use unit tests + Robolectric for PRs</li>
        <li>❌ <strong>Not pinning action versions:</strong> <code>uses: actions/checkout@main</code> is unpredictable — ✅ Fix: Always pin to a specific SHA or version tag like <code>@v4</code></li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Our CI/CD pipeline is a multi-stage quality gate. On every PR, GitHub Actions runs lint, unit tests, and Kotlin compilation in parallel—taking about 8 minutes total with Gradle caching. We use matrix builds to validate against API 26, 31, and 34. PRs cannot merge unless all gates pass and code coverage stays above 80%. On main branch merge, the CD pipeline takes over: it decodes the keystore from an encrypted GitHub secret, builds the release AAB with R8 minification, and uploads to Play Store's internal track via the Google Play Developer API service account. We also run MobSF security scanning nightly and Snyk dependency checks. The entire release from merged PR to Play Store internal track takes under 15 minutes with zero manual steps. This gives us confidence to ship multiple times per week."</p>
      </div>
    </div>
  </div>

  <div class="subtopic" id="subtopic-33-2">
    <h2>Fastlane Automation</h2>

    <div class="card card-why">
      <h3>❓ Why Fastlane?</h3>
      <p>GitHub Actions YAML handles the orchestration but is verbose for complex mobile-specific tasks like screenshots, changelog generation, and multi-track Play Store deployment. Fastlane provides a Ruby DSL specifically designed for mobile CI/CD: a single <code>lane</code> encapsulates screenshot capture across 6 locales, beta distribution to Firebase App Distribution, and Play Store submission with changelogs from git history—all in readable, maintainable code.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ Fastlane Configuration</h3>
      <pre class="code-block"><code class="language-ruby"># fastlane/Fastfile
default_platform(:android)

platform :android do

  # ── Beta distribution lane ──────────────────────────────────────────
  lane :beta do
    # Increment version code automatically
    increment_version_code(
      gradle_file_path: "app/build.gradle.kts"
    )

    gradle(
      task: "bundle",
      build_type: "Release",
      properties: {
        "android.injected.signing.store.file" => ENV["KEYSTORE_PATH"],
        "android.injected.signing.store.password" => ENV["STORE_PASSWORD"],
        "android.injected.signing.key.alias" => ENV["KEY_ALIAS"],
        "android.injected.signing.key.password" => ENV["KEY_PASSWORD"],
      }
    )

    firebase_app_distribution(
      app: ENV["FIREBASE_APP_ID"],
      groups: "qa-team, product-managers",
      release_notes: changelog_from_git_commits(
        commits_count: 10,
        pretty: "- %s"
      ),
      service_credentials_file: "firebase-service-account.json"
    )
  end

  # ── Production release lane ─────────────────────────────────────────
  lane :production do
    gradle(
      task: "bundle",
      build_type: "Release"
    )

    upload_to_play_store(
      track: "production",
      aab: "app/build/outputs/bundle/release/app-release.aab",
      skip_upload_apk: true,
      rollout: "0.1",  # 10% staged rollout
      release_status: "inProgress"
    )

    # Tag the release in git
    add_git_tag(tag: "v#{get_version_name}/#{get_version_code}")
    push_git_tags
  end

  # ── Screenshot automation lane ──────────────────────────────────────
  lane :screenshots do
    capture_android_screenshots(
      locales: ["en-US", "fr-FR", "de-DE", "es-ES", "ja-JP", "ko-KR"],
      clear_previous_screenshots: true,
      tests_product_flavor: "screenshots"
    )
    upload_to_play_store(
      skip_upload_apk: true,
      skip_upload_aab: true,
      skip_upload_metadata: true
    )
  end
end</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Fastlane Mistakes</h3>
      <ul>
        <li>❌ <strong>Storing Fastlane credentials in Fastfile:</strong> Service account JSON in code is a breach — ✅ Fix: Use environment variables or CI secrets, reference via <code>ENV["KEY"]</code></li>
        <li>❌ <strong>Not pinning the Gemfile:</strong> <code>gem "fastlane"</code> without version picks up breaking changes — ✅ Fix: Use <code>gem "fastlane", "~> 2.220"</code> and commit Gemfile.lock</li>
        <li>❌ <strong>Forgetting to increment versionCode:</strong> Play Store rejects duplicate version codes — ✅ Fix: Use <code>increment_version_code</code> action or derive from CI build number</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"We use Fastlane as the action layer on top of GitHub Actions. The YAML handles trigger logic and environment setup; Fastlane lanes handle the mobile-specific complexity. Our <code>beta</code> lane increments the version code, builds a signed AAB, and distributes to Firebase App Distribution with an auto-generated changelog from git commits. Our <code>production</code> lane does a 10% staged rollout to Play Store. This separation means our Fastfile is reusable locally—any developer can run <code>fastlane beta</code> from their machine with the right credentials to do a manual beta release."</p>
      </div>
    </div>
  </div>

  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers — CI/CD for Android</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the difference between an APK and an AAB, and why does it matter for CI/CD?</div>
      <div class="qa-answer">
        <p><strong>APK (Android Package Kit)</strong> is a complete, self-contained installable file. <strong>AAB (Android App Bundle)</strong> is a publishing format that contains all compiled code and resources, but defers APK generation to Google Play. Play uses Dynamic Delivery to generate optimized APKs per device configuration (ABI, screen density, language)—reducing app size by 15-40%. Since August 2021, Play Store requires AAB for new apps. In CI/CD: use <code>assembleRelease</code> to build APKs for direct distribution (Firebase App Distribution, sideloading), and <code>bundleRelease</code> for Play Store uploads. Never upload APKs to Play Store for new releases.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q2</span>How do you securely manage signing keys in a CI/CD pipeline?</div>
      <div class="qa-answer">
        <p>Never commit keystore files or passwords to the repository. The secure approach:</p>
        <ol>
          <li>Base64-encode the keystore: <code>base64 -i release.jks | pbcopy</code></li>
          <li>Store the encoded string as an encrypted CI secret (GitHub: Settings → Secrets and variables → Actions)</li>
          <li>In the pipeline, decode it: <code>echo "$KEYSTORE_BASE64" | base64 --decode > keystore.jks</code></li>
          <li>Store passwords (storePassword, keyPassword, keyAlias) as separate secrets</li>
          <li>Pass them to Gradle via environment variables in build.gradle.kts: <code>System.getenv("STORE_PASSWORD")</code></li>
          <li>Delete the decoded keystore after the build step</li>
        </ol>
        <p>For enterprise setups, use HashiCorp Vault or AWS Secrets Manager to centrally manage secrets with audit logging and rotation policies.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>How do you optimize Gradle build times in CI?</div>
      <div class="qa-answer">
        <p>Key optimizations in order of impact:</p>
        <ul>
          <li><strong>Gradle cache:</strong> Cache <code>~/.gradle/caches</code> and <code>~/.gradle/wrapper</code> keyed on build file hashes. Saves 5-15 minutes per run.</li>
          <li><strong>Configuration cache:</strong> Enable with <code>org.gradle.configuration-cache=true</code> in gradle.properties. Caches the build configuration phase.</li>
          <li><strong>Parallel execution:</strong> <code>org.gradle.parallel=true</code> and <code>org.gradle.workers.max=4</code></li>
          <li><strong>Incremental builds:</strong> Gradle's up-to-date checks skip unchanged modules. Modular architecture benefits significantly.</li>
          <li><strong>Build scan:</strong> Use <code>./gradlew build --scan</code> to identify bottlenecks.</li>
          <li><strong>Remote build cache:</strong> Share compiled artifacts across CI runs using Gradle Enterprise or a custom cache node.</li>
          <li><strong>Module isolation:</strong> With <code>./gradlew :feature:login:testDebugUnitTest</code>, only test the changed module on PRs.</li>
        </ul>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q4</span>Your Play Store upload fails with "Version code already exists." How do you prevent this in CI?</div>
      <div class="qa-answer">
        <p>This happens when the versionCode in build.gradle doesn't auto-increment. Solutions:</p>
        <ul>
          <li><strong>Use CI build number:</strong> <code>versionCode = System.getenv("BUILD_NUMBER")?.toInt() ?: 1</code> — GitHub Actions provides <code>GITHUB_RUN_NUMBER</code></li>
          <li><strong>Fastlane:</strong> Use <code>increment_version_code</code> action before building, which reads and increments the current value</li>
          <li><strong>Git commit count:</strong> <code>versionCode = "git rev-list --count HEAD".execute().text.trim().toInt()</code> — always increases with new commits</li>
          <li><strong>Date-based:</strong> <code>versionCode = (new Date()).format("yyMMddHHmm").toInteger()</code></li>
        </ul>
        <p>Best practice: Use <code>GITHUB_RUN_NUMBER</code> for simplicity and monotonic increase guarantee. Store the mapping between versionCode and human-readable versionName separately.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q5</span>How would you set up CI for a multi-module Android project to avoid running all tests on every PR?</div>
      <div class="qa-answer">
        <p>The key is <strong>affected module detection</strong>:</p>
        <pre class="code-block"><code class="language-bash"># Script to find affected modules
CHANGED_FILES=$(git diff --name-only origin/main...HEAD)
AFFECTED_MODULES=""

for file in $CHANGED_FILES; do
  # Extract module from path (e.g., feature/login/src -> :feature:login)
  MODULE=$(echo $file | grep -oP "^[^/]+/[^/]+" | head -1 | tr '/' ':')
  AFFECTED_MODULES="$AFFECTED_MODULES :$MODULE:testDebugUnitTest"
done

./gradlew $AFFECTED_MODULES</code></pre>
        <p>Tools like <strong>Gradle's build scan</strong> and <strong>Dropbox's focus-android</strong> or <strong>affected-module-detector</strong> library automate this. Only the changed module and its dependents are tested on PRs, while the full suite runs nightly or on main branch merges.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q6</span>What is a staged rollout and how do you implement it in CI/CD?</div>
      <div class="qa-answer">
        <p>A staged rollout gradually increases the percentage of users receiving a new app version, allowing monitoring for crashes before full exposure.</p>
        <p>In Fastlane: <code>upload_to_play_store(track: "production", rollout: "0.10")</code> — starts at 10%.</p>
        <p>In GitHub Actions with Google Play API:</p>
        <pre class="code-block"><code class="language-yaml">- uses: r0adkll/upload-google-play@v1
  with:
    track: production
    status: inProgress
    userFraction: 0.1  # 10% initial rollout</code></pre>
        <p>After monitoring Crashlytics for 24-48 hours, increase: <code>status: inProgress, userFraction: 0.5</code>, then <code>status: completed</code> for 100%. Automate rollout increase with Crashlytics API: if crash-free rate stays above threshold (e.g., 99.5%), automatically increase rollout percentage.</p>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge — Dynamic versionCode from Git</h3>
    <p><strong>Problem:</strong> Write a Gradle Kotlin DSL snippet that automatically sets versionCode from the git commit count and versionName from a git tag, with fallback defaults for environments without git.</p>
    <pre class="code-block"><code class="language-kotlin">// app/build.gradle.kts

fun gitCommitCount(): Int {
    return try {
        val process = ProcessBuilder("git", "rev-list", "--count", "HEAD")
            .redirectErrorStream(true)
            .start()
        val count = process.inputStream.bufferedReader().readLine()?.trim()?.toIntOrNull() ?: 1
        process.waitFor()
        count
    } catch (e: Exception) {
        // Fallback: use CI build number, then 1
        System.getenv("GITHUB_RUN_NUMBER")?.toIntOrNull() ?: 1
    }
}

fun gitVersionName(): String {
    return try {
        val process = ProcessBuilder("git", "describe", "--tags", "--abbrev=0")
            .redirectErrorStream(true)
            .start()
        val tag = process.inputStream.bufferedReader().readLine()?.trim() ?: "1.0.0"
        process.waitFor()
        // Remove leading 'v' if present: "v1.2.3" -> "1.2.3"
        tag.removePrefix("v")
    } catch (e: Exception) {
        "1.0.0"
    }
}

android {
    defaultConfig {
        versionCode = gitCommitCount()      // e.g., 1547
        versionName = gitVersionName()      // e.g., "2.4.1"

        // Embed version info in BuildConfig for crash reporting
        buildConfigField("String", "GIT_COMMIT", "\"${gitCommitHash()}\"")
    }
}

fun gitCommitHash(): String {
    return try {
        val process = ProcessBuilder("git", "rev-parse", "--short", "HEAD")
            .redirectErrorStream(true)
            .start()
        val hash = process.inputStream.bufferedReader().readLine()?.trim() ?: "unknown"
        process.waitFor()
        hash
    } catch (e: Exception) {
        "unknown"
    }
}
// Time/Space: O(1) — git commands are fast; no collection traversal.
// Production note: Always ensure git is available in CI environment.
// For monorepo, use separate commit ranges per product if needed.</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="33" data-item="0"> ✅ Understood Why &amp; What</label>
    <label class="progress-check"><input type="checkbox" data-topic="33" data-item="1"> ✅ Can explain GitHub Actions pipeline structure</label>
    <label class="progress-check"><input type="checkbox" data-topic="33" data-item="2"> ✅ Reviewed Signing Config &amp; secrets management</label>
    <label class="progress-check"><input type="checkbox" data-topic="33" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="33" data-item="4"> ✅ Solved Coding Challenge</label>
  </div>
</section>

<!-- ==================== TOPIC 34: Android Permissions ==================== -->
<section class="topic-section" id="topic-34">
  <div class="topic-header">
    <div class="topic-header-icon">🔐</div>
    <div class="topic-header-text">
      <h1>Android Permissions</h1>
      <p class="topic-tagline">Master the permission model: runtime grants, rationale dialogs, and Android 13+ granular access</p>
      <div class="category-badge-group">
        <span class="cat-pill">Security</span>
        <span class="cat-pill">Runtime Permissions</span>
        <span class="cat-pill">Android 13+</span>
        <span class="cat-pill">Privacy</span>
      </div>
    </div>
  </div>

  <div class="subtopic" id="subtopic-34-1">
    <h2>Permission Types &amp; Runtime Flow</h2>

    <div class="card card-why">
      <h3>❓ Why Does the Permission Model Exist?</h3>
      <p>Prior to Android 6.0 (API 23), apps declared permissions at install time and were granted all-or-nothing. Users had no visibility into what an app accessed during runtime. This led to widespread abuse: flashlight apps requesting contacts, games requesting SMS. The runtime permission model (introduced in API 23) gives users granular, contextual control—granting camera access exactly when the app needs it, not blindly at install. For apps targeting API 33+, Google further granularized media access so users can grant access to selected photos without giving blanket gallery permission. Understanding this model is essential for apps that won't be rejected from Play Store or sued for privacy violations.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 Permission Categories</h3>
      <p><strong>Normal permissions</strong> are auto-granted at install; they have low privacy risk (INTERNET, VIBRATE, ACCESS_NETWORK_STATE). <strong>Dangerous permissions</strong> require explicit user approval at runtime and can be revoked (CAMERA, RECORD_AUDIO, READ_CONTACTS, ACCESS_FINE_LOCATION). <strong>Signature permissions</strong> are auto-granted to apps signed with the same certificate—used for inter-app IPC between apps from the same developer. <strong>Special permissions</strong> require the user to navigate to system settings (MANAGE_EXTERNAL_STORAGE, SYSTEM_ALERT_WINDOW). Permission groups cluster related dangerous permissions: granting READ_CONTACTS also grants WRITE_CONTACTS within the same group (though you still must request individually).</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ Runtime Permission Flow with Activity Result API</h3>
      <pre class="code-block"><code class="language-kotlin">// Preferred modern approach: Activity Result API (no requestCode boilerplate)
class CameraFragment : Fragment() {

    // Single permission launcher
    private val requestCameraPermission = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        when {
            isGranted -> openCamera()
            shouldShowRequestPermissionRationale(Manifest.permission.CAMERA) -> {
                // User denied but didn't check "Don't ask again"
                showRationaleDialog()
            }
            else -> {
                // User checked "Don't ask again" — must direct to Settings
                showPermissionPermanentlyDeniedDialog()
            }
        }
    }

    // Multiple permissions launcher
    private val requestMultiplePermissions = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions: Map<String, Boolean> ->
        val allGranted = permissions.values.all { it }
        val cameraGranted = permissions[Manifest.permission.CAMERA] ?: false
        val audioGranted = permissions[Manifest.permission.RECORD_AUDIO] ?: false

        when {
            allGranted -> startVideoRecording()
            !cameraGranted -> showCameraRequiredMessage()
            !audioGranted -> startVideoRecordingWithoutAudio()
        }
    }

    private fun checkAndRequestCameraPermission() {
        when {
            // Already granted
            ContextCompat.checkSelfPermission(
                requireContext(), Manifest.permission.CAMERA
            ) == PackageManager.PERMISSION_GRANTED -> openCamera()

            // Should show rationale (denied once, but not permanently)
            shouldShowRequestPermissionRationale(Manifest.permission.CAMERA) -> {
                showRationaleDialog()
            }

            // First time or permanently denied check is done in callback
            else -> requestCameraPermission.launch(Manifest.permission.CAMERA)
        }
    }

    private fun showRationaleDialog() {
        MaterialAlertDialogBuilder(requireContext())
            .setTitle("Camera Access Required")
            .setMessage("This feature requires camera access to scan QR codes for payments. Your camera is not used for any other purpose.")
            .setPositiveButton("Grant Access") { _, _ ->
                requestCameraPermission.launch(Manifest.permission.CAMERA)
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun showPermissionPermanentlyDeniedDialog() {
        MaterialAlertDialogBuilder(requireContext())
            .setTitle("Permission Required")
            .setMessage("Camera permission was permanently denied. Please enable it in Settings to use this feature.")
            .setPositiveButton("Open Settings") { _, _ ->
                // Navigate to app settings
                val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                    data = Uri.fromParts("package", requireContext().packageName, null)
                }
                startActivity(intent)
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Android 13+ Granular Media Permissions</h3>
      <pre class="code-block"><code class="language-kotlin">// Android 13 (API 33) introduced granular media permissions
// OLD (before API 33): READ_EXTERNAL_STORAGE = access to all media
// NEW (API 33+): Separate permissions per media type

object MediaPermissionHelper {

    fun getRequiredMediaPermissions(context: Context): Array<String> {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            // API 33+: Granular permissions
            arrayOf(
                Manifest.permission.READ_MEDIA_IMAGES,   // Photos
                Manifest.permission.READ_MEDIA_VIDEO,    // Videos
                Manifest.permission.READ_MEDIA_AUDIO     // Music/Audio
            )
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            // API 30-32: READ_EXTERNAL_STORAGE (MANAGE_EXTERNAL_STORAGE for full access)
            arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE)
        } else {
            // API 29 and below
            arrayOf(
                Manifest.permission.READ_EXTERNAL_STORAGE,
                Manifest.permission.WRITE_EXTERNAL_STORAGE
            )
        }
    }

    // Android 14 (API 34): PHOTO_PICKER — user selects specific photos
    // No permission needed! Use ActivityResultContracts.PickMultipleVisualMedia()
    // This is the preferred approach for photo/video selection
}

// Photo picker (no permission required — Android 14+)
class PhotoPickerFragment : Fragment() {
    private val pickMedia = registerForActivityResult(
        ActivityResultContracts.PickMultipleVisualMedia(maxItems = 5)
    ) { uris: List<Uri> ->
        // User selected specific photos — no READ_MEDIA_IMAGES needed
        uris.forEach { uri -> processSelectedPhoto(uri) }
    }

    fun launchPhotoPicker() {
        pickMedia.launch(
            PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageAndVideo)
        )
    }
}

// Background location — API 29+ requires separate permission
// Must request ACCESS_FINE_LOCATION first, then separately ask for background
class LocationPermissionManager(private val activity: AppCompatActivity) {

    private val requestForegroundLocation = activity.registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) requestBackgroundLocationIfNeeded()
    }

    fun requestBackgroundLocationIfNeeded() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            // Must explain WHY background location is needed before requesting
            // Play Store policy: must have foreground location first
            activity.registerForActivityResult(
                ActivityResultContracts.RequestPermission()
            ) { granted ->
                if (!granted) showBackgroundLocationDeniedUI()
            }.launch(Manifest.permission.ACCESS_BACKGROUND_LOCATION)
        }
    }
}</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World: Healthcare App Permission Strategy</h3>
      <p>A telemedicine app needs camera (video consult), microphone, contacts (emergency contacts), and location (nearest clinic). The strategy: request permissions contextually, never upfront, with clear medical rationale.</p>
      <pre class="code-block"><code class="language-kotlin">// PermissionManager.kt — centralized permission handling
class PermissionManager(
    private val activity: AppCompatActivity,
    private val analytics: AnalyticsService
) {
    // Track permission state for analytics
    private val permissionStates = mutableMapOf<String, PermissionState>()

    sealed class PermissionState {
        object Granted : PermissionState()
        object Denied : PermissionState()
        object PermanentlyDenied : PermissionState()
        object NotRequested : PermissionState()
    }

    private val videoConsultPermissions = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { results ->
        val camera = results[Manifest.permission.CAMERA] ?: false
        val audio = results[Manifest.permission.RECORD_AUDIO] ?: false

        // Track for compliance/analytics
        analytics.logEvent("permission_result", mapOf(
            "camera" to camera,
            "audio" to audio,
            "context" to "video_consult"
        ))

        when {
            camera && audio -> activity.startVideoConsult()
            !camera && !audio -> showBothDeniedEducation()
            !camera -> showCameraOnlyDeniedUI()
            else -> showAudioOnlyDeniedUI()
        }
    }

    fun requestVideoConsultPermissions() {
        val needed = listOf(
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO
        ).filter {
            ContextCompat.checkSelfPermission(activity, it) != PackageManager.PERMISSION_GRANTED
        }

        if (needed.isEmpty()) {
            activity.startVideoConsult()
            return
        }

        // Show medical context before requesting
        MaterialAlertDialogBuilder(activity)
            .setTitle("Enable Video Consultation")
            .setMessage("Your doctor needs to see and hear you during the consultation. Camera and microphone access are required. This data is encrypted and HIPAA-compliant.")
            .setIcon(R.drawable.ic_medical_video)
            .setPositiveButton("Enable") { _, _ ->
                videoConsultPermissions.launch(needed.toTypedArray())
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Requesting all permissions at app launch:</strong> Users deny everything when prompted before context — ✅ Fix: Request permissions lazily, exactly when the feature needs them, with clear rationale</li>
        <li>❌ <strong>Not handling "Don't ask again" state:</strong> After permanent denial, <code>requestPermissions()</code> silently does nothing — ✅ Fix: Check <code>shouldShowRequestPermissionRationale()</code> returning false after denial = permanently denied; redirect to Settings</li>
        <li>❌ <strong>Using deprecated <code>onRequestPermissionsResult</code>:</strong> Boilerplate-prone and fragile with requestCode — ✅ Fix: Use <code>ActivityResultContracts.RequestPermission()</code> API</li>
        <li>❌ <strong>Assuming permission group grants all:</strong> Granting READ_CONTACTS doesn't auto-grant WRITE_CONTACTS on all API levels — ✅ Fix: Request each permission individually even within the same group</li>
        <li>❌ <strong>Using READ_EXTERNAL_STORAGE on API 33+:</strong> Deprecated and ignored — ✅ Fix: Use READ_MEDIA_IMAGES, READ_MEDIA_VIDEO, READ_MEDIA_AUDIO or Photo Picker API</li>
        <li>❌ <strong>Requesting background location without foreground location first:</strong> Crashes with SecurityException on API 30+ — ✅ Fix: Always obtain foreground location permission before requesting ACCESS_BACKGROUND_LOCATION</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Android's permission model has evolved significantly. Pre-API 23 was install-time all-or-nothing. API 23 added runtime dangerous permissions with the rationale dialog flow. API 29 added background location as a separate permission. API 33 split READ_EXTERNAL_STORAGE into media-type-specific permissions. API 34 introduced the Photo Picker which needs no permission at all. In production, I centralize permission handling in a PermissionManager class that tracks state, shows contextual rationale before requesting, handles the permanent denial case by redirecting to Settings, and logs all permission events to analytics for monitoring grant rates. Grant rate is a product metric—if your camera permission grant rate drops below 70%, your rationale dialog probably isn't compelling enough."</p>
      </div>
    </div>
  </div>

  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers — Android Permissions</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the difference between Normal, Dangerous, and Signature permissions?</div>
      <div class="qa-answer">
        <p><strong>Normal permissions</strong> (e.g., INTERNET, VIBRATE): Low privacy risk. Automatically granted at install. User doesn't see a dialog.</p>
        <p><strong>Dangerous permissions</strong> (e.g., CAMERA, READ_CONTACTS, ACCESS_FINE_LOCATION): High privacy risk. Must be declared in manifest AND requested at runtime on API 23+. User sees a system dialog. Can be revoked anytime from Settings.</p>
        <p><strong>Signature permissions</strong> (e.g., custom permissions with <code>protectionLevel="signature"</code>): Auto-granted to apps signed with the same certificate. Used for trusted inter-app communication between apps from the same publisher without user involvement.</p>
        <p><strong>Special permissions</strong>: Not in these categories — require user to manually go to Settings. Examples: SYSTEM_ALERT_WINDOW (draw over other apps), MANAGE_EXTERNAL_STORAGE (full file access).</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q2</span>How does <code>shouldShowRequestPermissionRationale()</code> work and what are its states?</div>
      <div class="qa-answer">
        <p>This method returns a boolean that reflects whether the user has previously denied the permission:</p>
        <ul>
          <li><strong>First request (never asked):</strong> Returns <code>false</code> — show no rationale, just request</li>
          <li><strong>After first denial (without "Don't ask again"):</strong> Returns <code>true</code> — show rationale explaining WHY, then re-request</li>
          <li><strong>After "Don't ask again" / permanent denial:</strong> Returns <code>false</code> — user won't see a dialog if you request; must redirect to Settings</li>
        </ul>
        <p>The key insight: distinguish "never asked" from "permanently denied" by tracking state yourself. One approach: use SharedPreferences to track if you've ever requested, then if <code>checkSelfPermission == DENIED</code> AND <code>shouldShowRationale == false</code> AND you've previously requested = permanently denied.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>What changed with media permissions in Android 13 (API 33)?</div>
      <div class="qa-answer">
        <p>Before API 33: <code>READ_EXTERNAL_STORAGE</code> granted access to ALL media files.</p>
        <p>API 33+ replaced it with three granular permissions:</p>
        <ul>
          <li><code>READ_MEDIA_IMAGES</code> — photos and images</li>
          <li><code>READ_MEDIA_VIDEO</code> — video files</li>
          <li><code>READ_MEDIA_AUDIO</code> — audio/music files</li>
        </ul>
        <p>Users can now grant photo access without audio access. Apps must request only what they need. Additionally, Android 14 added <code>READ_MEDIA_VISUAL_USER_SELECTED</code> for apps that want to let users pick specific photos rather than grant full library access. The Photo Picker API (<code>PickVisualMedia</code>) requires NO permission at all since Android 11+ (via backport via Google Play services).</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q4</span>A user reports your app can't access the camera even though they previously granted permission. What do you investigate?</div>
      <div class="qa-answer">
        <p>Several possible causes:</p>
        <ol>
          <li><strong>Auto-revocation (API 30+):</strong> Android auto-revokes permissions for apps not used for months. Check if the app was idle. Solution: re-request permissions and handle gracefully.</li>
          <li><strong>Permission revoked in Settings:</strong> User manually revoked it. Always call <code>checkSelfPermission()</code> before using the camera, not just on first launch.</li>
          <li><strong>Device admin policy:</strong> Enterprise MDM might restrict camera. Check <code>CameraManager</code> availability.</li>
          <li><strong>Another app using camera:</strong> <code>CameraDevice.StateCallback.onError</code> with <code>ERROR_CAMERA_IN_USE</code>.</li>
          <li><strong>Physical camera disabled:</strong> Some privacy-focused ROMs or enterprise policies disable the camera entirely.</li>
        </ol>
        <p>Best practice: Always check permission state in <code>onResume()</code> or before each camera access, not just once. Use <code>ContextCompat.checkSelfPermission()</code> every time.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q5</span>How do background location permissions work differently from foreground location?</div>
      <div class="qa-answer">
        <p><strong>Foreground location</strong> (<code>ACCESS_FINE_LOCATION</code> or <code>ACCESS_COARSE_LOCATION</code>): App gets location when the app is visible or has a foreground service with location type.</p>
        <p><strong>Background location</strong> (<code>ACCESS_BACKGROUND_LOCATION</code>, API 29+): App gets location even when not in foreground.</p>
        <p>Rules:</p>
        <ul>
          <li>Must hold foreground location permission FIRST before requesting background</li>
          <li>On API 30+, background location must be requested SEPARATELY (not in the same <code>requestMultiplePermissions</code> call)</li>
          <li>Play Store requires a declaration and video demonstrating legitimate use</li>
          <li>System dialog for background location says "Allow all the time" vs "Allow only while using the app"</li>
          <li>On API 29+, background location shows as a separate Settings option</li>
        </ul>
        <p>Google Play policy: Background location must be core to the app's primary function (e.g., navigation, geofencing). Misuse results in app removal.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>How do you build a reusable permission utility that works across your entire app?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">// Reusable permission extension functions
fun Fragment.requestPermission(
    permission: String,
    onGranted: () -> Unit,
    onDenied: () -> Unit = {},
    onPermanentlyDenied: () -> Unit = { navigateToSettings() }
) {
    if (ContextCompat.checkSelfPermission(requireContext(), permission)
        == PackageManager.PERMISSION_GRANTED) {
        onGranted()
        return
    }
    val launcher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        when {
            isGranted -> onGranted()
            shouldShowRequestPermissionRationale(permission) -> onDenied()
            else -> onPermanentlyDenied()
        }
    }
    launcher.launch(permission)
}

// Usage in Fragment
checkCameraButton.setOnClickListener {
    requestPermission(
        permission = Manifest.permission.CAMERA,
        onGranted = { openCamera() },
        onDenied = { showCameraRationale() },
        onPermanentlyDenied = { showSettingsDialog() }
    )
}</code></pre>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge — Permission State Machine</h3>
    <p><strong>Problem:</strong> Implement a PermissionStateMachine that correctly identifies all permission states (NotDetermined, Granted, Denied, PermanentlyDenied) using SharedPreferences to track request history.</p>
    <pre class="code-block"><code class="language-kotlin">enum class PermissionStatus {
    NOT_DETERMINED,   // Never requested
    GRANTED,          // Currently granted
    DENIED,           // Denied but can re-request
    PERMANENTLY_DENIED // "Don't ask again" selected
}

class PermissionStateMachine(
    private val context: Context,
    private val activity: Activity,
    private val prefs: SharedPreferences = context.getSharedPreferences(
        "permission_prefs", Context.MODE_PRIVATE
    )
) {
    private val PREF_REQUESTED_PREFIX = "requested_"

    fun getStatus(permission: String): PermissionStatus {
        val granted = ContextCompat.checkSelfPermission(context, permission) ==
            PackageManager.PERMISSION_GRANTED
        if (granted) return PermissionStatus.GRANTED

        val hasBeenRequested = prefs.getBoolean("$PREF_REQUESTED_PREFIX$permission", false)
        val shouldShowRationale = ActivityCompat.shouldShowRequestPermissionRationale(
            activity, permission
        )

        return when {
            !hasBeenRequested -> PermissionStatus.NOT_DETERMINED
            shouldShowRationale -> PermissionStatus.DENIED
            else -> PermissionStatus.PERMANENTLY_DENIED
        }
    }

    fun markAsRequested(permission: String) {
        prefs.edit().putBoolean("$PREF_REQUESTED_PREFIX$permission", true).apply()
    }

    // Usage:
    // when (stateMachine.getStatus(Manifest.permission.CAMERA)) {
    //   NOT_DETERMINED -> requestDirectly()
    //   DENIED -> showRationale()
    //   PERMANENTLY_DENIED -> openSettings()
    //   GRANTED -> useCamera()
    // }
}
// Time: O(1) — SharedPreferences lookup is constant time
// Space: O(n) — n = number of tracked permissions (small, bounded)</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="34" data-item="0"> ✅ Understood permission types (Normal/Dangerous/Signature)</label>
    <label class="progress-check"><input type="checkbox" data-topic="34" data-item="1"> ✅ Can implement runtime permission flow with Activity Result API</label>
    <label class="progress-check"><input type="checkbox" data-topic="34" data-item="2"> ✅ Understood Android 13+ granular media permissions</label>
    <label class="progress-check"><input type="checkbox" data-topic="34" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="34" data-item="4"> ✅ Solved Coding Challenge</label>
  </div>
</section>

<!-- ==================== TOPIC 35: RecyclerView & Lists ==================== -->
<section class="topic-section" id="topic-35">
  <div class="topic-header">
    <div class="topic-header-icon">📋</div>
    <div class="topic-header-text">
      <h1>RecyclerView &amp; Lists</h1>
      <p class="topic-tagline">Efficient, smooth, production-grade list rendering at any scale</p>
      <div class="category-badge-group">
        <span class="cat-pill">RecyclerView</span>
        <span class="cat-pill">DiffUtil</span>
        <span class="cat-pill">ListAdapter</span>
        <span class="cat-pill">ViewHolder</span>
      </div>
    </div>
  </div>

  <div class="subtopic" id="subtopic-35-1">
    <h2>RecyclerView Internals &amp; ViewHolder Pattern</h2>

    <div class="card card-why">
      <h3>❓ Why RecyclerView?</h3>
      <p>ListView (the predecessor) created a new View object for every list item and held all items in memory. For a list of 10,000 transactions in a FinTech app, that's 10,000 inflated Views—causing massive memory pressure, janky scrolling (dropped frames below 60fps), and OOM crashes. RecyclerView solves this with <strong>view recycling</strong>: it maintains a small pool of View objects (enough to fill the screen plus a buffer), and as items scroll off-screen, their Views are recycled and bound with new data for incoming items. The ViewHolder pattern pre-caches all <code>findViewById</code> calls in a typed object, eliminating the single biggest cause of ListView jank.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 RecyclerView Architecture</h3>
      <p>RecyclerView is a <strong>ViewGroup</strong> that delegates layout to a <strong>LayoutManager</strong> (LinearLayoutManager, GridLayoutManager, StaggeredGridLayoutManager), item animation to an <strong>ItemAnimator</strong>, and data management to an <strong>Adapter</strong>. The <strong>RecycledViewPool</strong> stores scrapped Views by view type. The <strong>Recycler</strong> (internal class) handles the two-level cache: a 2-item scrap cache for recently scrolled views (no rebinding needed), and the RecycledViewPool for older views (requires <code>onBindViewHolder</code>). The <strong>ViewHolder</strong> caches View references and holds position/payload metadata.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ ListAdapter with DiffUtil</h3>
      <pre class="code-block"><code class="language-kotlin">// Data class — must implement equals() for DiffUtil
data class Transaction(
    val id: String,
    val amount: Double,
    val merchant: String,
    val timestamp: Long,
    val status: TransactionStatus
)

// DiffUtil callback — tells RecyclerView what changed
class TransactionDiffCallback : DiffUtil.ItemCallback<Transaction>() {

    // Are these the same item? (same identity, e.g., same database ID)
    override fun areItemsTheSame(oldItem: Transaction, newItem: Transaction): Boolean {
        return oldItem.id == newItem.id
    }

    // Are these items' contents the same? (used for change animations)
    override fun areContentsTheSame(oldItem: Transaction, newItem: Transaction): Boolean {
        return oldItem == newItem  // Data class equals() checks all fields
    }

    // Optional: return payload for partial rebind (only update changed fields)
    override fun getChangePayload(oldItem: Transaction, newItem: Transaction): Any? {
        return if (oldItem.status != newItem.status) {
            "STATUS_CHANGED"  // Only rebind status view, not whole item
        } else null
    }
}

// ListAdapter: built-in DiffUtil on background thread
class TransactionAdapter(
    private val onItemClick: (Transaction) -> Unit,
    private val onLongPress: (Transaction) -> Boolean
) : ListAdapter<Transaction, TransactionAdapter.ViewHolder>(TransactionDiffCallback()) {

    inner class ViewHolder(
        private val binding: ItemTransactionBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        // Bind full item
        fun bind(transaction: Transaction) = with(binding) {
            merchantName.text = transaction.merchant
            amount.text = formatCurrency(transaction.amount)
            timestamp.text = formatRelativeTime(transaction.timestamp)
            statusChip.apply {
                text = transaction.status.displayName
                setChipBackgroundColorResource(transaction.status.colorRes)
            }
            root.setOnClickListener { onItemClick(transaction) }
            root.setOnLongClickListener { onLongPress(transaction) }
        }

        // Partial rebind using payload — much more efficient
        fun bindPayload(payloads: List<Any>, transaction: Transaction) {
            payloads.forEach { payload ->
                when (payload) {
                    "STATUS_CHANGED" -> binding.statusChip.apply {
                        text = transaction.status.displayName
                        setChipBackgroundColorResource(transaction.status.colorRes)
                    }
                }
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemTransactionBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    // Called when payload is non-empty — enables partial updates
    override fun onBindViewHolder(
        holder: ViewHolder,
        position: Int,
        payloads: MutableList<Any>
    ) {
        if (payloads.isEmpty()) {
            super.onBindViewHolder(holder, position, payloads)
        } else {
            holder.bindPayload(payloads, getItem(position))
        }
    }
}

// In ViewModel: submit new list — DiffUtil runs on background thread automatically
class TransactionViewModel : ViewModel() {
    private val _transactions = MutableStateFlow<List<Transaction>>(emptyList())
    val transactions = _transactions.asStateFlow()

    fun updateTransactions(newList: List<Transaction>) {
        _transactions.value = newList
    }
}

// In Fragment
class TransactionFragment : Fragment() {
    private val adapter = TransactionAdapter(
        onItemClick = { transaction -> navigateToDetail(transaction) },
        onLongPress = { transaction -> showContextMenu(transaction); true }
    )

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        binding.recyclerView.apply {
            this.adapter = this@TransactionFragment.adapter
            layoutManager = LinearLayoutManager(context)
            setHasFixedSize(true)  // Optimization: RecyclerView size doesn't change with content
            addItemDecoration(DividerItemDecoration(context, LinearLayoutManager.VERTICAL))
        }
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.transactions.collect { transactions ->
                adapter.submitList(transactions)
            }
        }
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Multiple View Types &amp; ConcatAdapter</h3>
      <pre class="code-block"><code class="language-kotlin">// Multiple view types in a single adapter
class FeedAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    sealed class FeedItem {
        data class StoryItem(val story: Story) : FeedItem()
        data class AdItem(val ad: Advertisement) : FeedItem()
        data class SectionHeader(val title: String) : FeedItem()
    }

    companion object {
        const val VIEW_TYPE_STORY = 0
        const val VIEW_TYPE_AD = 1
        const val VIEW_TYPE_HEADER = 2
    }

    private val items = mutableListOf<FeedItem>()

    override fun getItemViewType(position: Int): Int = when (items[position]) {
        is FeedItem.StoryItem -> VIEW_TYPE_STORY
        is FeedItem.AdItem -> VIEW_TYPE_AD
        is FeedItem.SectionHeader -> VIEW_TYPE_HEADER
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) = when (viewType) {
        VIEW_TYPE_STORY -> StoryViewHolder(/* inflate story layout */)
        VIEW_TYPE_AD -> AdViewHolder(/* inflate ad layout */)
        VIEW_TYPE_HEADER -> HeaderViewHolder(/* inflate header layout */)
        else -> throw IllegalArgumentException("Unknown view type: $viewType")
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (val item = items[position]) {
            is FeedItem.StoryItem -> (holder as StoryViewHolder).bind(item.story)
            is FeedItem.AdItem -> (holder as AdViewHolder).bind(item.ad)
            is FeedItem.SectionHeader -> (holder as HeaderViewHolder).bind(item.title)
        }
    }

    override fun getItemCount() = items.size
}

// ConcatAdapter: compose multiple adapters (e.g., header + content + footer + loading)
class ProductListFragment : Fragment() {
    private val headerAdapter = ProductHeaderAdapter()
    private val productAdapter = ProductAdapter()
    private val loadingAdapter = LoadingFooterAdapter()

    private val concatAdapter = ConcatAdapter(
        ConcatAdapter.Config.Builder()
            .setIsolateViewTypes(false)  // Share view type pool for efficiency
            .build(),
        headerAdapter,
        productAdapter,
        loadingAdapter
    )

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        binding.recyclerView.adapter = concatAdapter

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.products.collect { products ->
                productAdapter.submitList(products)
            }
        }
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.isLoading.collect { isLoading ->
                loadingAdapter.setVisible(isLoading)
            }
        }
    }
}

// SnapHelper for carousel-like snapping
binding.recyclerView.apply {
    layoutManager = LinearLayoutManager(context, LinearLayoutManager.HORIZONTAL, false)
    PagerSnapHelper().attachToRecyclerView(this)  // Page-by-page snapping
    // OR: LinearSnapHelper().attachToRecyclerView(this)  // Snap to nearest
}</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World: E-Commerce Product Feed with ItemDecoration</h3>
      <pre class="code-block"><code class="language-kotlin">// Custom ItemDecoration for spacing + category dividers
class ProductGridDecoration(
    private val spanCount: Int,
    private val spacing: Int,
    private val includeEdge: Boolean = true
) : RecyclerView.ItemDecoration() {

    override fun getItemOffsets(
        outRect: Rect,
        view: View,
        parent: RecyclerView,
        state: RecyclerView.State
    ) {
        val position = parent.getChildAdapterPosition(view)
        val column = position % spanCount

        if (includeEdge) {
            outRect.left = spacing - column * spacing / spanCount
            outRect.right = (column + 1) * spacing / spanCount
            if (position < spanCount) outRect.top = spacing
            outRect.bottom = spacing
        } else {
            outRect.left = column * spacing / spanCount
            outRect.right = spacing - (column + 1) * spacing / spanCount
            if (position >= spanCount) outRect.top = spacing
        }
    }
}

// Grid layout with section headers (SpanSizeLookup)
val gridLayoutManager = GridLayoutManager(context, 2).apply {
    spanSizeLookup = object : GridLayoutManager.SpanSizeLookup() {
        override fun getSpanSize(position: Int): Int {
            // Headers span full width, products take 1 column
            return when (adapter.getItemViewType(position)) {
                FeedAdapter.VIEW_TYPE_HEADER -> 2  // Full width
                else -> 1                           // Half width
            }
        }
    }
}

binding.recyclerView.apply {
    layoutManager = gridLayoutManager
    addItemDecoration(ProductGridDecoration(spanCount = 2, spacing = 16.dp))
    // Optimize: tell RecyclerView the pool size per view type
    recycledViewPool.setMaxRecycledViews(FeedAdapter.VIEW_TYPE_HEADER, 2)
    recycledViewPool.setMaxRecycledViews(FeedAdapter.VIEW_TYPE_PRODUCT, 10)
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Calling <code>notifyDataSetChanged()</code> always:</strong> Forces full rebind of all visible items, causes flicker and loses animations — ✅ Fix: Use ListAdapter with DiffUtil, or call granular notify methods (notifyItemChanged, notifyItemInserted)</li>
        <li>❌ <strong>Doing heavy work in <code>onBindViewHolder</code>:</strong> This is called on the main thread during scroll — ✅ Fix: Pre-process data in ViewModel/background thread; bind only pre-computed values</li>
        <li>❌ <strong>Storing position in ViewHolder field:</strong> Position changes on scroll without rebind — ✅ Fix: Use <code>holder.bindingAdapterPosition</code> or <code>holder.absoluteAdapterPosition</code> in click listeners</li>
        <li>❌ <strong>Not calling <code>setHasStableIds(true)</code> with override of <code>getItemId()</code>:</strong> Missing optimization for animations — ✅ Fix: If items have unique stable IDs, enable this for smoother animations</li>
        <li>❌ <strong>Not using ViewBinding in ViewHolder:</strong> Using <code>findViewByld</code> in <code>onBindViewHolder</code> traverses the whole view tree each time — ✅ Fix: Use ViewBinding in ViewHolder constructor; bind once, reference always</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"RecyclerView's power comes from its separation of concerns: LayoutManager handles placement, Adapter handles data binding, ItemAnimator handles transitions, and the Recycler pool handles view reuse. In production, I always use ListAdapter over raw Adapter because DiffUtil runs on a background thread and applies minimal change operations—this is the difference between 60fps smooth scrolling and janky flickering. For complex feeds with headers, ads, and content, I use ConcatAdapter to compose independent adapters rather than cramming everything into one giant adapter with multiple view types. For performance: setHasFixedSize(true) when the RecyclerView doesn't resize with content, payload-based partial binds for frequent status updates (like real-time price changes), and pre-load images in background before binding."</p>
      </div>
    </div>
  </div>

  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers — RecyclerView &amp; Lists</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>Explain the ViewHolder pattern and why it's critical for performance.</div>
      <div class="qa-answer">
        <p>The ViewHolder pattern stores references to all Views within a list item as fields in a class. Without it, <code>onBindViewHolder</code> would call <code>findViewById()</code> on every bind—which traverses the entire View hierarchy. For a list item with 5 views scrolling at 60fps with 15 binds/second, that's 75 hierarchy traversals per second, causing serious jank.</p>
        <p>With ViewHolder: Views are inflated once in <code>onCreateViewHolder</code>, references cached in the ViewHolder. <code>onBindViewHolder</code> simply updates the already-found view properties. With ViewBinding, this is even cleaner:</p>
        <pre class="code-block"><code class="language-kotlin">class ProductViewHolder(
    private val binding: ItemProductBinding  // All views pre-cached
) : RecyclerView.ViewHolder(binding.root) {
    fun bind(product: Product) {
        binding.name.text = product.name  // No find needed
        binding.price.text = product.formattedPrice
    }
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q2</span>How does DiffUtil work internally? What is its time complexity?</div>
      <div class="qa-answer">
        <p>DiffUtil uses the <strong>Myers diff algorithm</strong> — the same algorithm used by git for text diffs. It compares old and new lists to find the minimum edit script (insertions, deletions, moves).</p>
        <p><strong>Time complexity:</strong> O(N + M + D²) where N = old list size, M = new list size, D = number of differences. For small D (few changes), this is essentially O(N + M).</p>
        <p><strong>Space complexity:</strong> O(N + M)</p>
        <p><strong>Execution:</strong> DiffUtil.calculateDiff() is CPU-intensive for large lists and MUST NOT run on the main thread. ListAdapter handles this automatically by running diff in a background thread via <code>AsyncListDiffer</code> — this is why <code>submitList()</code> is non-blocking.</p>
        <p><strong>Move detection:</strong> DiffUtil.calculateDiff() has an optional <code>detectMoves</code> parameter. When true, it detects item moves in addition to insertions/deletions — but doubles the computation time. Set to false for simple lists without reordering.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>What are DiffUtil payloads and when should you use them?</div>
      <div class="qa-answer">
        <p>Payloads allow <strong>partial rebinding</strong> of a ViewHolder — only updating the changed part of a view instead of rebinding the entire item. This is critical for items that frequently update a small part of their content (e.g., live stock prices, like counts, delivery status).</p>
        <pre class="code-block"><code class="language-kotlin">// 1. DiffCallback returns a payload
override fun getChangePayload(old: StockItem, new: StockItem): Any? {
    return if (old.price != new.price) Bundle().apply {
        putDouble("PRICE", new.price)
        putBoolean("UP", new.price > old.price)
    } else null
}

// 2. Adapter handles payload
override fun onBindViewHolder(holder: ViewHolder, pos: Int, payloads: MutableList<Any>) {
    if (payloads.isEmpty()) { super.onBindViewHolder(holder, pos, payloads); return }
    payloads.filterIsInstance<Bundle>().forEach { bundle ->
        bundle.getDouble("PRICE").takeIf { it != 0.0 }?.let { price ->
            holder.updatePrice(price, bundle.getBoolean("UP"))
        }
    }
}</code></pre>
        <p>Without payloads: entire item fades out and back in. With payloads: only the price TextView updates with a smooth color flash animation. This is the difference between a professional trading app and an amateur one.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q4</span>Your RecyclerView with 10,000 items scrolls smoothly but causes ANR when submitting new data. What's wrong?</div>
      <div class="qa-answer">
        <p>The most likely cause: you're using a raw <code>RecyclerView.Adapter</code> and calling <code>DiffUtil.calculateDiff()</code> on the <strong>main thread</strong>. For 10,000 items, this can take 200-500ms — well over the 16ms frame budget, causing an ANR.</p>
        <p>Solutions:</p>
        <ol>
          <li><strong>Switch to ListAdapter:</strong> Runs DiffUtil on a background thread automatically via AsyncListDiffer. Just call <code>submitList(newList)</code> from the main thread.</li>
          <li><strong>Manual background thread:</strong>
          <pre class="code-block"><code class="language-kotlin">viewModelScope.launch(Dispatchers.Default) {
    val diff = DiffUtil.calculateDiff(MyDiffCallback(oldList, newList))
    withContext(Dispatchers.Main) {
        adapter.updateList(newList)
        diff.dispatchUpdatesTo(adapter)
    }
}</code></pre>
          </li>
          <li><strong>Paging 3:</strong> For truly large datasets, use Paging 3 which lazily loads data and has built-in DiffUtil on background thread.</li>
        </ol>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q5</span>How does RecyclerView's view recycling work at the cache level?</div>
      <div class="qa-answer">
        <p>RecyclerView uses a <strong>multi-level cache hierarchy</strong>:</p>
        <ol>
          <li><strong>Scrap cache (mAttachedScrap + mChangedScrap):</strong> Holds views that are still attached during layout pass. Used during notifyItemChanged — the view is scrapped, layout manager re-lays out, then re-attaches it without rebinding if position unchanged.</li>
          <li><strong>RecyclerView cache (mCachedViews, default size: 2):</strong> Holds recently scrolled-off views BY POSITION. If the user scrolls back, these views can be reattached without <code>onBindViewHolder</code> — data is still bound.</li>
          <li><strong>ViewCacheExtension:</strong> Optional custom cache you can implement (rarely needed).</li>
          <li><strong>RecycledViewPool:</strong> Shared pool of views BY VIEW TYPE (default: 5 per type). Views here need rebinding via <code>onBindViewHolder</code>. Can be shared between multiple RecyclerViews (e.g., nested lists).</li>
        </ol>
        <p>Tune with: <code>recyclerView.setItemViewCacheSize(10)</code> to increase the mCachedViews size for smoother back-scrolling at the cost of memory.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>How do you implement swipe-to-delete and drag-to-reorder in RecyclerView?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">val itemTouchHelper = ItemTouchHelper(object : ItemTouchHelper.SimpleCallback(
    ItemTouchHelper.UP or ItemTouchHelper.DOWN,  // Drag directions
    ItemTouchHelper.LEFT or ItemTouchHelper.RIGHT // Swipe directions
) {
    override fun onMove(
        rv: RecyclerView, 
        dragged: RecyclerView.ViewHolder, 
        target: RecyclerView.ViewHolder
    ): Boolean {
        val from = dragged.bindingAdapterPosition
        val to = target.bindingAdapterPosition
        adapter.moveItem(from, to)  // Update data + call notifyItemMoved
        return true
    }

    override fun onSwiped(holder: RecyclerView.ViewHolder, direction: Int) {
        val position = holder.bindingAdapterPosition
        val item = adapter.getItem(position)
        adapter.removeItem(position)
        // Show Snackbar with Undo
        Snackbar.make(binding.root, "Item deleted", Snackbar.LENGTH_LONG)
            .setAction("Undo") { adapter.insertItem(position, item) }
            .show()
    }

    override fun onChildDraw(c: Canvas, rv: RecyclerView, vh: RecyclerView.ViewHolder,
        dX: Float, dY: Float, actionState: Int, isActive: Boolean) {
        // Draw red background + delete icon while swiping
        if (actionState == ItemTouchHelper.ACTION_STATE_SWIPE) {
            val itemView = vh.itemView
            val paint = Paint().apply { color = Color.RED }
            c.drawRect(itemView.left.toFloat(), itemView.top.toFloat(),
                dX, itemView.bottom.toFloat(), paint)
        }
        super.onChildDraw(c, rv, vh, dX, dY, actionState, isActive)
    }
})
itemTouchHelper.attachToRecyclerView(binding.recyclerView)</code></pre>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge — Sticky Headers with ItemDecoration</h3>
    <p><strong>Problem:</strong> Implement a sticky header decoration for a RecyclerView that shows group headers (e.g., date headers in a chat app) that "stick" to the top as you scroll past the group.</p>
    <pre class="code-block"><code class="language-kotlin">// StickyHeaderDecoration.kt
class StickyHeaderDecoration(
    private val adapter: StickyHeaderInterface
) : RecyclerView.ItemDecoration() {

    interface StickyHeaderInterface {
        fun getHeaderId(position: Int): Long
        fun isHeader(position: Int): Boolean
        fun bindHeaderView(header: View, position: Int)
        fun getHeaderLayout(parent: ViewGroup): View
    }

    override fun onDrawOver(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        val topChild = parent.getChildAt(0) ?: return
        val topChildPosition = parent.getChildAdapterPosition(topChild)
        if (topChildPosition == RecyclerView.NO_ID) return

        val headerView = getHeaderViewForItem(topChildPosition, parent)
        val contactPoint = headerView.bottom
        val childInContact = getChildInContact(parent, contactPoint, topChildPosition)

        // If next child is a header, push current header up
        if (childInContact != null && adapter.isHeader(parent.getChildAdapterPosition(childInContact))) {
            moveHeader(c, headerView, childInContact)
            return
        }
        drawHeader(c, headerView)
    }

    private fun getHeaderViewForItem(itemPosition: Int, parent: ViewGroup): View {
        val header = adapter.getHeaderLayout(parent)
        adapter.bindHeaderView(header, itemPosition)
        measureAndLayoutHeader(header, parent)
        return header
    }

    private fun measureAndLayoutHeader(header: View, parent: ViewGroup) {
        val widthSpec = View.MeasureSpec.makeMeasureSpec(parent.width, View.MeasureSpec.EXACTLY)
        val heightSpec = View.MeasureSpec.makeMeasureSpec(parent.height, View.MeasureSpec.UNSPECIFIED)
        val childWidth = ViewGroup.getChildMeasureSpec(widthSpec, parent.paddingLeft + parent.paddingRight, header.layoutParams.width)
        val childHeight = ViewGroup.getChildMeasureSpec(heightSpec, parent.paddingTop + parent.paddingBottom, header.layoutParams.height)
        header.measure(childWidth, childHeight)
        header.layout(0, 0, header.measuredWidth, header.measuredHeight)
    }

    private fun drawHeader(c: Canvas, header: View) {
        c.save()
        c.translate(0f, 0f)
        header.draw(c)
        c.restore()
    }

    private fun moveHeader(c: Canvas, header: View, nextHeader: View) {
        c.save()
        c.translate(0f, (nextHeader.top - header.height).toFloat())
        header.draw(c)
        c.restore()
    }

    private fun getChildInContact(parent: RecyclerView, contactPoint: Int, currentHeaderPos: Int): View? {
        return (0 until parent.childCount).map { parent.getChildAt(it) }
            .firstOrNull { it.bottom > contactPoint && it.top < contactPoint &&
                parent.getChildAdapterPosition(it) != currentHeaderPos }
    }
}
// Time: O(n) per draw frame where n = visible children (typically ~10-15)
// Space: O(1) — header view is created once and reused</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="35" data-item="0"> ✅ Understood RecyclerView internals &amp; view recycling cache</label>
    <label class="progress-check"><input type="checkbox" data-topic="35" data-item="1"> ✅ Can implement ListAdapter with DiffUtil &amp; payloads</label>
    <label class="progress-check"><input type="checkbox" data-topic="35" data-item="2"> ✅ Reviewed multiple view types, ConcatAdapter, SnapHelper</label>
    <label class="progress-check"><input type="checkbox" data-topic="35" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="35" data-item="4"> ✅ Solved Coding Challenge</label>
  </div>
</section>

<!-- ==================== TOPIC 36: Paging 3 Library ==================== -->
<section class="topic-section" id="topic-36">
  <div class="topic-header">
    <div class="topic-header-icon">📄</div>
    <div class="topic-header-text">
      <h1>Paging 3 Library</h1>
      <p class="topic-tagline">Efficiently load and display large datasets from network and database with built-in loading states</p>
      <div class="category-badge-group">
        <span class="cat-pill">Paging 3</span>
        <span class="cat-pill">PagingSource</span>
        <span class="cat-pill">RemoteMediator</span>
        <span class="cat-pill">Jetpack</span>
      </div>
    </div>
  </div>

  <div class="subtopic" id="subtopic-36-1">
    <h2>PagingSource &amp; RemoteMediator</h2>

    <div class="card card-why">
      <h3>❓ Why Paging 3?</h3>
      <p>Loading all data at once from a REST API or database is impractical at scale. A social feed with 100,000 posts, or an e-commerce catalog with 50,000 products — fetching everything crashes the app (OOM) and destroys user experience (long initial load). Manual pagination is brittle: tracking page numbers, handling edge cases (race conditions, rotation, back-stack), retrying failed pages, and integrating with RecyclerView's DiffUtil is error-prone boilerplate. Paging 3 encapsulates all of this: it provides a clean API for incremental loading, automatic load-state handling (loading indicators, error states, retry), and first-class coroutine/Flow support.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 Paging 3 Architecture</h3>
      <p><strong>PagingSource&lt;Key, Value&gt;</strong>: Defines how to load data from a single source (network OR database). The Key is the page key (Int for page numbers, String for cursor-based), Value is the data type. <strong>RemoteMediator</strong>: Orchestrates loading from network + caching to database (room). Used for offline-first: load from DB, fetch from network on exhaustion or invalidation. <strong>Pager</strong>: Constructs a Flow&lt;PagingData&lt;Value&gt;&gt; from a PagingSource and PagingConfig. <strong>PagingData&lt;Value&gt;</strong>: Immutable snapshot of paged data. <strong>PagingDataAdapter</strong>: RecyclerView adapter that consumes PagingData with built-in DiffUtil on background thread. <strong>LoadState</strong>: Reflects the loading state of each end of the list (prepend, append) and refresh.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ Network-Only Paging with PagingSource</h3>
      <pre class="code-block"><code class="language-kotlin">// 1. Data model
data class Article(
    val id: String,
    val title: String,
    val summary: String,
    val imageUrl: String,
    val publishedAt: String
)

// 2. PagingSource — defines how to load one page of data
class ArticlePagingSource(
    private val api: NewsApi,
    private val query: String
) : PagingSource<Int, Article>() {

    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, Article> {
        val page = params.key ?: 1  // Start from page 1

        return try {
            val response = api.searchArticles(
                query = query,
                page = page,
                pageSize = params.loadSize  // Respects PagingConfig.pageSize
            )

            LoadResult.Page(
                data = response.articles,
                prevKey = if (page == 1) null else page - 1,
                nextKey = if (response.articles.isEmpty() || page >= response.totalPages) {
                    null  // null = end of data
                } else {
                    page + 1
                }
            )
        } catch (e: IOException) {
            LoadResult.Error(e)  // Network error — Paging will surface via LoadState
        } catch (e: HttpException) {
            LoadResult.Error(e)
        }
    }

    // Called when underlying data is invalidated (e.g., refresh)
    override fun getRefreshKey(state: PagingState<Int, Article>): Int? {
        // Return the key of the anchor page so we reload from current position
        return state.anchorPosition?.let { anchorPosition ->
            state.closestPageToPosition(anchorPosition)?.prevKey?.plus(1)
                ?: state.closestPageToPosition(anchorPosition)?.nextKey?.minus(1)
        }
    }
}

// 3. Repository — exposes Flow<PagingData<Article>>
class ArticleRepository(private val api: NewsApi) {

    fun getArticleStream(query: String): Flow<PagingData<Article>> {
        return Pager(
            config = PagingConfig(
                pageSize = 20,           // Items per page
                prefetchDistance = 5,    // Load next page when 5 items from end
                enablePlaceholders = false, // No placeholder items (true = show empty cells)
                initialLoadSize = 40     // Load more on first fetch for fast initial display
            ),
            pagingSourceFactory = { ArticlePagingSource(api, query) }
        ).flow
    }
}

// 4. ViewModel — survives rotation, caches PagingData
class ArticleViewModel(private val repository: ArticleRepository) : ViewModel() {

    private val currentQuery = MutableStateFlow("android")

    val articles: Flow<PagingData<Article>> = currentQuery
        .flatMapLatest { query ->
            repository.getArticleStream(query)
        }
        .cachedIn(viewModelScope)  // CRITICAL: cache in ViewModel scope to survive rotation

    fun search(query: String) {
        currentQuery.value = query
    }
}

// 5. PagingDataAdapter
class ArticleAdapter : PagingDataAdapter<Article, ArticleAdapter.ViewHolder>(
    object : DiffUtil.ItemCallback<Article>() {
        override fun areItemsTheSame(a: Article, b: Article) = a.id == b.id
        override fun areContentsTheSame(a: Article, b: Article) = a == b
    }
) {
    inner class ViewHolder(private val binding: ItemArticleBinding)
        : RecyclerView.ViewHolder(binding.root) {
        fun bind(article: Article?) {
            article ?: return  // Handle placeholder (null) items
            binding.title.text = article.title
            binding.summary.text = article.summary
            Glide.with(itemView).load(article.imageUrl).into(binding.thumbnail)
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
        ViewHolder(ItemArticleBinding.inflate(LayoutInflater.from(parent.context), parent, false))

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
}

// 6. Fragment — observe and display
class ArticleFragment : Fragment() {
    private val adapter = ArticleAdapter()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        setupRecyclerView()
        observePagingData()
        observeLoadState()
    }

    private fun setupRecyclerView() {
        binding.recyclerView.adapter = adapter.withLoadStateFooter(
            footer = LoadingStateAdapter { adapter.retry() }
        )
    }

    private fun observePagingData() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.articles.collect { pagingData ->
                    adapter.submitData(pagingData)
                }
            }
        }
    }

    private fun observeLoadState() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                adapter.loadStateFlow.collect { loadStates ->
                    // Show/hide initial loading spinner
                    binding.progressBar.isVisible =
                        loadStates.refresh is LoadState.Loading

                    // Show error state
                    val refreshError = loadStates.refresh as? LoadState.Error
                    binding.errorView.isVisible = refreshError != null
                    refreshError?.let { binding.errorMessage.text = it.error.message }

                    // Scroll to top on refresh
                    if (loadStates.refresh is LoadState.NotLoading) {
                        binding.recyclerView.scrollToPosition(0)
                    }
                }
            }
        }
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 RemoteMediator — Offline-First with Network + Room</h3>
      <pre class="code-block"><code class="language-kotlin">// RemoteMediator: network fetches + Room caching
@OptIn(ExperimentalPagingApi::class)
class ArticleRemoteMediator(
    private val db: AppDatabase,
    private val api: NewsApi,
    private val query: String
) : RemoteMediator<Int, ArticleEntity>() {

    private val articleDao = db.articleDao()
    private val remoteKeyDao = db.remoteKeyDao()

    override suspend fun initialize(): InitializeAction {
        // Check if data is stale (> 1 hour old) → REFRESH, else SKIP_INITIAL_REFRESH
        val lastUpdated = articleDao.getLastUpdated(query) ?: return InitializeAction.LAUNCH_INITIAL_REFRESH
        val isStale = (System.currentTimeMillis() - lastUpdated) > TimeUnit.HOURS.toMillis(1)
        return if (isStale) InitializeAction.LAUNCH_INITIAL_REFRESH
        else InitializeAction.SKIP_INITIAL_REFRESH
    }

    override suspend fun load(
        loadType: LoadType,
        state: PagingState<Int, ArticleEntity>
    ): MediatorResult {
        val page = when (loadType) {
            LoadType.REFRESH -> 1  // Always start from page 1 on refresh
            LoadType.PREPEND -> return MediatorResult.Success(endOfPaginationReached = true)
            LoadType.APPEND -> {
                val remoteKey = remoteKeyDao.getKey(query)
                    ?: return MediatorResult.Success(endOfPaginationReached = true)
                remoteKey.nextPage ?: return MediatorResult.Success(endOfPaginationReached = true)
            }
        }

        return try {
            val response = api.searchArticles(query, page, state.config.pageSize)

            db.withTransaction {
                if (loadType == LoadType.REFRESH) {
                    articleDao.clearAll(query)
                    remoteKeyDao.clearKey(query)
                }
                // Save remote key (next page number)
                remoteKeyDao.insertOrReplace(
                    RemoteKey(query = query, nextPage = if (response.articles.isEmpty()) null else page + 1)
                )
                // Save articles to Room
                articleDao.insertAll(response.articles.map { it.toEntity(query) })
            }

            MediatorResult.Success(endOfPaginationReached = response.articles.isEmpty())
        } catch (e: IOException) {
            MediatorResult.Error(e)
        } catch (e: HttpException) {
            MediatorResult.Error(e)
        }
    }
}

// Repository using RemoteMediator
class ArticleRepository(private val api: NewsApi, private val db: AppDatabase) {

    @OptIn(ExperimentalPagingApi::class)
    fun getArticleStream(query: String): Flow<PagingData<Article>> {
        return Pager(
            config = PagingConfig(pageSize = 20, enablePlaceholders = false),
            remoteMediator = ArticleRemoteMediator(db, api, query),
            pagingSourceFactory = { db.articleDao().getArticles(query) }
            // Room returns a PagingSource automatically
        ).flow.map { pagingData ->
            pagingData.map { entity -> entity.toArticle() }  // Entity -> Domain model
        }
    }
}</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World: E-Commerce Product Catalog with Separator Items</h3>
      <pre class="code-block"><code class="language-kotlin">// Insert separators between price categories in paged data
val articlesWithSeparators: Flow<PagingData<UiModel>> = viewModel.articles
    .map { pagingData ->
        pagingData.map { article -> UiModel.ArticleItem(article) }
    }
    .map { pagingData ->
        pagingData.insertSeparators { before, after ->
            // Insert a "FEATURED" header before the first item
            if (before == null) return@insertSeparators UiModel.SeparatorItem("TOP STORIES")

            // Insert separator when price category changes
            val beforeCategory = (before as? UiModel.ArticleItem)?.article?.category
            val afterCategory = (after as? UiModel.ArticleItem)?.article?.category
            if (beforeCategory != afterCategory && afterCategory != null) {
                UiModel.SeparatorItem(afterCategory.uppercase())
            } else null
        }
    }
    .cachedIn(viewModelScope)

sealed class UiModel {
    data class ArticleItem(val article: Article) : UiModel()
    data class SeparatorItem(val title: String) : UiModel()
}

// Adapter handles both types
class ArticleWithSeparatorAdapter : PagingDataAdapter<UiModel, RecyclerView.ViewHolder>(
    object : DiffUtil.ItemCallback<UiModel>() {
        override fun areItemsTheSame(a: UiModel, b: UiModel): Boolean = when {
            a is UiModel.ArticleItem && b is UiModel.ArticleItem -> a.article.id == b.article.id
            a is UiModel.SeparatorItem && b is UiModel.SeparatorItem -> a.title == b.title
            else -> false
        }
        override fun areContentsTheSame(a: UiModel, b: UiModel) = a == b
    }
) {
    override fun getItemViewType(position: Int) = when (getItem(position)) {
        is UiModel.ArticleItem -> VIEW_TYPE_ARTICLE
        is UiModel.SeparatorItem -> VIEW_TYPE_SEPARATOR
        null -> VIEW_TYPE_ARTICLE
    }
    // ... onCreateViewHolder and onBindViewHolder handle both types
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Not calling <code>cachedIn(viewModelScope)</code>:</strong> Without this, every new collector (screen rotation) restarts the entire pagination — ✅ Fix: Always apply <code>.cachedIn(viewModelScope)</code> in ViewModel</li>
        <li>❌ <strong>Collecting PagingData in <code>lifecycleScope.launch</code> without <code>repeatOnLifecycle</code>:</strong> Leaks coroutine when app goes to background — ✅ Fix: Always use <code>repeatOnLifecycle(Lifecycle.State.STARTED)</code></li>
        <li>❌ <strong>Returning wrong <code>prevKey</code>/<code>nextKey</code>:</strong> Non-null prevKey for first page causes infinite prepend loading — ✅ Fix: <code>prevKey = if (page == 1) null else page - 1</code></li>
        <li>❌ <strong>Not using Room PagingSource with RemoteMediator:</strong> Implementing your own in-memory PagingSource alongside RemoteMediator loses the offline-first benefit — ✅ Fix: Room's @Dao can return <code>PagingSource&lt;Int, Entity&gt;</code> directly</li>
        <li>❌ <strong>Missing LoadState footer for append loading:</strong> Users have no indication new items are loading — ✅ Fix: Use <code>adapter.withLoadStateFooter(LoadingStateAdapter { adapter.retry() })</code></li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Paging 3 is fundamentally about separation of concerns: PagingSource defines the data loading contract, RemoteMediator coordinates network-to-database synchronization, and PagingDataAdapter handles the RecyclerView integration with built-in background DiffUtil. The key insight is the two-tier architecture: RemoteMediator only loads from network and writes to Room; Room's PagingSource is the single source of truth for the UI. This means offline works automatically—the UI reads from Room whether or not network is available. In production, I always set <code>cachedIn(viewModelScope)</code> to survive rotation, use <code>repeatOnLifecycle(STARTED)</code> for safe collection, and implement <code>getRefreshKey</code> so users return to their scroll position after refresh. For insertSeparators, Paging 3 handles the async complexity of injecting non-data items into the stream without blocking the paging mechanism."</p>
      </div>
    </div>
  </div>

  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers — Paging 3</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the difference between PagingSource and RemoteMediator?</div>
      <div class="qa-answer">
        <p><strong>PagingSource</strong> is the primary data source for a Pager. It loads data from a SINGLE source — either network or database. Use it for pure network pagination (no offline) or when Room is your single source of truth and you have a <code>@Dao</code> method returning <code>PagingSource</code>.</p>
        <p><strong>RemoteMediator</strong> acts as a bridge between MULTIPLE sources: it fetches from network and caches to database, then the UI reads from the database via a Room PagingSource. This enables offline-first: the UI always reads from Room, RemoteMediator keeps it fresh. RemoteMediator receives LoadType (REFRESH, PREPEND, APPEND) to know which direction to fetch. It's experimental API (<code>@OptIn(ExperimentalPagingApi::class)</code>) but production-ready.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q2</span>Why is <code>cachedIn(viewModelScope)</code> critical and what happens without it?</div>
      <div class="qa-answer">
        <p>Without <code>cachedIn</code>: Each new subscriber to the Flow&lt;PagingData&gt; triggers a new Pager, which creates a new PagingSource, which reloads all data from scratch. On screen rotation, the Fragment re-subscribes, causing a full reload — user sees a loading spinner and loses scroll position.</p>
        <p>With <code>cachedIn(viewModelScope)</code>: The multicasted Flow replays the latest PagingData to new subscribers. On rotation, the new Fragment collects the same cached PagingData instantly — no reload, scroll position preserved.</p>
        <p>Additionally, <code>cachedIn</code> keeps pages alive in memory as long as the ViewModel is alive. When the user returns to a screen, previously loaded pages are immediately available. The tradeoff: increased memory usage proportional to loaded pages.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>What is <code>getRefreshKey()</code> and why must it be implemented correctly?</div>
      <div class="qa-answer">
        <p><code>getRefreshKey()</code> is called when Paging needs to restart loading (e.g., after invalidation, pull-to-refresh, or data change). It receives the current <code>PagingState</code> — which contains the list of loaded pages and the anchor position (the item currently visible to the user).</p>
        <p>The return value is the KEY from which to start reloading. If you return null, paging reloads from the beginning — the user sees all previously scrolled content disappear.</p>
        <p>Correct implementation: return the key corresponding to the anchor position so the user's current viewport is preserved:</p>
        <pre class="code-block"><code class="language-kotlin">override fun getRefreshKey(state: PagingState<Int, Article>): Int? {
    return state.anchorPosition?.let { anchorPos ->
        val anchorPage = state.closestPageToPosition(anchorPos)
        anchorPage?.prevKey?.plus(1) ?: anchorPage?.nextKey?.minus(1)
    }
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q4</span>Your Paging 3 list doesn't show new items when the user pulls-to-refresh. What's the bug?</div>
      <div class="qa-answer">
        <p>Several possible causes:</p>
        <ol>
          <li><strong>Not calling <code>adapter.refresh()</code>:</strong> Pull-to-refresh must trigger <code>adapter.refresh()</code> (or <code>viewModel.refresh()</code> which invalidates the PagingSource).</li>
          <li><strong>PagingSource not invalidated:</strong> When underlying data changes, call <code>pagingSource.invalidate()</code> or use Room (which invalidates automatically via LiveData/Flow observers).</li>
          <li><strong>RemoteMediator <code>initialize()</code> returns <code>SKIP_INITIAL_REFRESH</code>:</strong> When using RemoteMediator and the cache is not stale, it won't fetch. Make sure refresh calls properly set stale state.</li>
          <li><strong>Collecting without <code>repeatOnLifecycle</code>:</strong> If collection stopped (app in background), new PagingData is not received on return. Fix: use <code>repeatOnLifecycle(STARTED)</code>.</li>
          <li><strong>Not scrolling to top after refresh:</strong> New data is there but list is still scrolled down. Listen to <code>loadStateFlow</code> and scroll to 0 when refresh becomes NotLoading.</li>
        </ol>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q5</span>What are LoadState types and how do you use them to build a robust loading UI?</div>
      <div class="qa-answer">
        <p><code>LoadState</code> is a sealed class with three states:</p>
        <ul>
          <li><code>LoadState.Loading</code>: Data is being fetched</li>
          <li><code>LoadState.NotLoading(endOfPaginationReached: Boolean)</code>: Idle, with flag indicating if more data exists</li>
          <li><code>LoadState.Error(error: Throwable)</code>: Load failed with the exception</li>
        </ul>
        <p>Each is available for three directions via <code>CombinedLoadStates</code>: <code>refresh</code>, <code>prepend</code>, <code>append</code>.</p>
        <pre class="code-block"><code class="language-kotlin">adapter.addLoadStateListener { combinedLoadStates ->
    binding.apply {
        // Initial load / refresh
        shimmerLayout.isVisible = combinedLoadStates.refresh is LoadState.Loading
        recyclerView.isVisible = combinedLoadStates.refresh is LoadState.NotLoading
        errorView.isVisible = combinedLoadStates.refresh is LoadState.Error

        // Append (bottom of list) — handled by withLoadStateFooter
        val appendError = combinedLoadStates.append as? LoadState.Error
        appendErrorSnackbar.isVisible = appendError != null
    }
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>How does cursor-based pagination differ from page-number pagination in Paging 3?</div>
      <div class="qa-answer">
        <p>Page-number pagination (Key = Int): Simple but fragile — if items are inserted/deleted between page fetches, you get duplicate or skipped items. Good for stable datasets.</p>
        <p>Cursor-based pagination (Key = String): The API returns a cursor (opaque token) representing the position in the dataset. Each page response includes the next cursor. More robust for real-time feeds.</p>
        <pre class="code-block"><code class="language-kotlin">// Cursor-based PagingSource
class FeedPagingSource(private val api: SocialApi) : PagingSource<String, Post>() {
    override suspend fun load(params: LoadParams<String>): LoadResult<String, Post> {
        return try {
            val response = api.getFeed(
                cursor = params.key,  // null = first page
                limit = params.loadSize
            )
            LoadResult.Page(
                data = response.posts,
                prevKey = null,  // Cursor-based: no backward loading
                nextKey = response.nextCursor  // null = end of feed
            )
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }

    override fun getRefreshKey(state: PagingState<String, Post>): String? = null
    // For cursor-based, refresh from beginning (null cursor = first page)
}</code></pre>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge — Retry Logic with Exponential Backoff in PagingSource</h3>
    <p><strong>Problem:</strong> Implement a PagingSource that retries failed network requests up to 3 times with exponential backoff before reporting an error to Paging 3.</p>
    <pre class="code-block"><code class="language-kotlin">class RetryPagingSource(
    private val api: ProductApi
) : PagingSource<Int, Product>() {

    companion object {
        private const val MAX_RETRIES = 3
        private const val INITIAL_BACKOFF_MS = 1000L
    }

    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, Product> {
        val page = params.key ?: 1
        return loadWithRetry(page, params.loadSize)
    }

    private suspend fun loadWithRetry(
        page: Int,
        pageSize: Int,
        attempt: Int = 0
    ): LoadResult<Int, Product> {
        return try {
            val response = api.getProducts(page = page, size = pageSize)
            LoadResult.Page(
                data = response.products,
                prevKey = if (page == 1) null else page - 1,
                nextKey = if (response.products.isEmpty()) null else page + 1
            )
        } catch (e: IOException) {
            // Network error — retry with backoff
            if (attempt < MAX_RETRIES) {
                val backoffMs = INITIAL_BACKOFF_MS * (1L shl attempt)  // 1s, 2s, 4s
                delay(backoffMs)
                loadWithRetry(page, pageSize, attempt + 1)
            } else {
                LoadResult.Error(e)  // Exhausted retries
            }
        } catch (e: HttpException) {
            // HTTP error — don't retry 4xx (client error), only 5xx (server error)
            if (e.code() in 500..599 && attempt < MAX_RETRIES) {
                val backoffMs = INITIAL_BACKOFF_MS * (1L shl attempt)
                delay(backoffMs)
                loadWithRetry(page, pageSize, attempt + 1)
            } else {
                LoadResult.Error(e)
            }
        }
    }

    override fun getRefreshKey(state: PagingState<Int, Product>): Int? {
        return state.anchorPosition?.let { anchorPos ->
            state.closestPageToPosition(anchorPos)?.prevKey?.plus(1)
                ?: state.closestPageToPosition(anchorPos)?.nextKey?.minus(1)
        }
    }
}
// Time: O(1) per attempt — bounded by MAX_RETRIES = 3
// Total max delay: 1000 + 2000 + 4000 = 7000ms before error
// Space: O(1) — no additional data structures</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="36" data-item="0"> ✅ Understood PagingSource vs RemoteMediator</label>
    <label class="progress-check"><input type="checkbox" data-topic="36" data-item="1"> ✅ Can implement network-only and offline-first Paging</label>
    <label class="progress-check"><input type="checkbox" data-topic="36" data-item="2"> ✅ Reviewed LoadState handling &amp; cachedIn importance</label>
    <label class="progress-check"><input type="checkbox" data-topic="36" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="36" data-item="4"> ✅ Solved Coding Challenge</label>
  </div>
</section>

<!-- ==================== TOPIC 37: Firebase in Android ==================== -->
<section class="topic-section" id="topic-37">
  <div class="topic-header">
    <div class="topic-header-icon">🔥</div>
    <div class="topic-header-text">
      <h1>Firebase in Android</h1>
      <p class="topic-tagline">Auth, Firestore, FCM, Crashlytics, Remote Config — the complete Firebase production toolkit</p>
      <div class="category-badge-group">
        <span class="cat-pill">Firebase</span>
        <span class="cat-pill">Firestore</span>
        <span class="cat-pill">FCM</span>
        <span class="cat-pill">Crashlytics</span>
      </div>
    </div>
  </div>

  <div class="subtopic" id="subtopic-37-1">
    <h2>Firebase Auth &amp; Firestore</h2>

    <div class="card card-why">
      <h3>❓ Why Firebase?</h3>
      <p>Building a real-time backend from scratch — authentication with OAuth, a scalable NoSQL database with real-time listeners, push notification infrastructure, crash reporting with stack deobfuscation, and A/B testing config — would take months and significant infrastructure expertise. Firebase provides all of these as managed services that integrate directly with Android SDKs. A startup can have Google-authenticated users, real-time data sync, and push notifications in a single day. For production apps, Firebase's Crashlytics catches crashes with full stack traces and device context; Remote Config enables feature flags and A/B tests without app updates; Performance Monitoring identifies slow network requests and UI rendering bottlenecks.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 Firebase Services Overview</h3>
      <p><strong>Firebase Auth:</strong> Identity platform supporting Email/Password, Google, Facebook, Apple, Phone, and anonymous sign-in with JWT tokens. <strong>Firestore:</strong> Document-oriented NoSQL cloud database with real-time listeners, offline persistence, complex queries, and automatic scaling. <strong>Realtime Database:</strong> JSON tree-structured database, simpler than Firestore, best for chat/presence. <strong>FCM (Firebase Cloud Messaging):</strong> Push notification delivery infrastructure with topic subscriptions, device tokens, and data/notification messages. <strong>Remote Config:</strong> Server-side feature flags/parameter store with A/B testing support. <strong>Crashlytics:</strong> Real-time crash reporter with symbolication, user identification, and alerts. <strong>Performance Monitoring:</strong> Automatic HTTP request tracing and custom performance traces.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ Firebase Auth with Google Sign-In</h3>
      <pre class="code-block"><code class="language-kotlin">// AuthRepository.kt — centralized Firebase Auth management
class AuthRepository(
    private val auth: FirebaseAuth = FirebaseAuth.getInstance(),
    private val analytics: FirebaseAnalytics
) {
    // Current user as a Flow
    val currentUser: Flow<FirebaseUser?> = callbackFlow {
        val listener = FirebaseAuth.AuthStateListener { firebaseAuth ->
            trySend(firebaseAuth.currentUser)
        }
        auth.addAuthStateListener(listener)
        awaitClose { auth.removeAuthStateListener(listener) }
    }

    val isSignedIn: Boolean get() = auth.currentUser != null

    // Google Sign-In
    suspend fun signInWithGoogle(idToken: String): Result<FirebaseUser> {
        return try {
            val credential = GoogleAuthProvider.getCredential(idToken, null)
            val result = auth.signInWithCredential(credential).await()
            val user = result.user ?: throw Exception("Auth successful but no user")

            // Log to analytics
            analytics.logEvent(FirebaseAnalytics.Event.LOGIN) {
                param(FirebaseAnalytics.Param.METHOD, "google")
            }

            Result.success(user)
        } catch (e: FirebaseAuthInvalidCredentialsException) {
            Result.failure(Exception("Invalid Google credentials. Please try again."))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // Email/Password sign-in
    suspend fun signInWithEmail(email: String, password: String): Result<FirebaseUser> {
        return try {
            val result = auth.signInWithEmailAndPassword(email, password).await()
            Result.success(result.user!!)
        } catch (e: FirebaseAuthInvalidUserException) {
            Result.failure(Exception("No account found with this email."))
        } catch (e: FirebaseAuthInvalidCredentialsException) {
            Result.failure(Exception("Incorrect password."))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // Get ID token for API calls (auto-refreshes if expired)
    suspend fun getIdToken(forceRefresh: Boolean = false): String? {
        return auth.currentUser?.getIdToken(forceRefresh)?.await()?.token
    }

    fun signOut() {
        auth.signOut()
    }
}

// ViewModel
class AuthViewModel(private val authRepository: AuthRepository) : ViewModel() {
    val currentUser = authRepository.currentUser.stateIn(
        viewModelScope, SharingStarted.Eagerly, null
    )

    private val _authState = MutableStateFlow<AuthState>(AuthState.Idle)
    val authState = _authState.asStateFlow()

    fun signInWithGoogle(idToken: String) {
        viewModelScope.launch {
            _authState.value = AuthState.Loading
            authRepository.signInWithGoogle(idToken)
                .onSuccess { _authState.value = AuthState.Success(it) }
                .onFailure { _authState.value = AuthState.Error(it.message ?: "Sign-in failed") }
        }
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Firestore Real-Time Queries &amp; Security Rules</h3>
      <pre class="code-block"><code class="language-kotlin">// FirestoreRepository.kt — production Firestore patterns
class ChatRepository(
    private val db: FirebaseFirestore = FirebaseFirestore.getInstance(),
    private val auth: FirebaseAuth = FirebaseAuth.getInstance()
) {
    data class Message(
        val id: String = "",
        val text: String = "",
        val senderId: String = "",
        val senderName: String = "",
        val timestamp: Timestamp = Timestamp.now(),
        val roomId: String = ""
    )

    // Real-time listener as Flow
    fun getMessages(roomId: String): Flow<List<Message>> = callbackFlow {
        val query = db.collection("rooms")
            .document(roomId)
            .collection("messages")
            .orderBy("timestamp", Query.Direction.DESCENDING)
            .limit(50)

        val listener = query.addSnapshotListener { snapshot, error ->
            if (error != null) {
                close(error)
                return@addSnapshotListener
            }
            val messages = snapshot?.documents?.mapNotNull { doc ->
                doc.toObject(Message::class.java)?.copy(id = doc.id)
            } ?: emptyList()
            trySend(messages)
        }

        awaitClose { listener.remove() }
    }

    // Batch write — atomic operation
    suspend fun sendMessageAndUpdateRoomMeta(
        roomId: String,
        messageText: String
    ): Result<Unit> {
        val userId = auth.currentUser?.uid ?: return Result.failure(Exception("Not signed in"))

        return try {
            val messageRef = db.collection("rooms").document(roomId)
                .collection("messages").document()

            db.runBatch { batch ->
                // Add message
                batch.set(messageRef, Message(
                    id = messageRef.id,
                    text = messageText,
                    senderId = userId,
                    senderName = auth.currentUser?.displayName ?: "Unknown",
                    timestamp = Timestamp.now(),
                    roomId = roomId
                ))
                // Update room last-message metadata
                batch.update(
                    db.collection("rooms").document(roomId),
                    mapOf(
                        "lastMessage" to messageText,
                        "lastMessageAt" to Timestamp.now(),
                        "lastSenderId" to userId
                    )
                )
            }.await()
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // Pagination with Firestore (cursor-based)
    suspend fun getMoreMessages(
        roomId: String,
        lastDocument: DocumentSnapshot,
        limit: Long = 20
    ): List<Message> {
        return db.collection("rooms").document(roomId)
            .collection("messages")
            .orderBy("timestamp", Query.Direction.DESCENDING)
            .startAfter(lastDocument)  // Cursor-based pagination
            .limit(limit)
            .get()
            .await()
            .documents
            .mapNotNull { it.toObject(Message::class.java) }
    }
}

// Firestore Security Rules (firestore.rules)
/*
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own profile
    match /users/{userId} {
      allow read: if request.auth != null;
      allow write: if request.auth.uid == userId;
    }

    // Room messages: must be a member to read/write
    match /rooms/{roomId}/messages/{messageId} {
      allow read: if request.auth != null &&
        request.auth.uid in get(/databases/$(database)/documents/rooms/$(roomId)).data.members;
      allow create: if request.auth != null &&
        request.resource.data.senderId == request.auth.uid &&
        request.resource.data.text.size() <= 1000;
      allow update, delete: if false;  // Messages are immutable
    }
  }
}
*/</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World: FCM Push Notifications &amp; Remote Config</h3>
      <pre class="code-block"><code class="language-kotlin">// FCM Service — handles push notifications
class MyFirebaseMessagingService : FirebaseMessagingService() {

    // Called when a new FCM token is generated
    override fun onNewToken(token: String) {
        super.onNewToken(token)
        // Send token to your backend to store for this user
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val userId = FirebaseAuth.getInstance().currentUser?.uid ?: return@launch
                // Update token in Firestore
                FirebaseFirestore.getInstance()
                    .collection("users").document(userId)
                    .update("fcmToken", token)
                    .await()
            } catch (e: Exception) {
                Log.e("FCM", "Failed to update token", e)
            }
        }
    }

    // Called when a message is received while app is in foreground
    override fun onMessageReceived(message: RemoteMessage) {
        super.onMessageReceived(message)

        val title = message.notification?.title ?: message.data["title"] ?: return
        val body = message.notification?.body ?: message.data["body"] ?: return
        val deepLink = message.data["deepLink"]

        showNotification(title, body, deepLink)
    }

    private fun showNotification(title: String, body: String, deepLink: String?) {
        val notificationManager = getSystemService(NotificationManager::class.java)

        // Create channel (required for API 26+)
        val channel = NotificationChannel(
            CHANNEL_ID, "Push Notifications", NotificationManager.IMPORTANCE_HIGH
        ).apply { description = "App push notifications" }
        notificationManager.createNotificationChannel(channel)

        val intent = deepLink?.let {
            Intent(Intent.ACTION_VIEW, Uri.parse(it)).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            }
        } ?: packageManager.getLaunchIntentForPackage(packageName)

        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(body)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .build()

        notificationManager.notify(System.currentTimeMillis().toInt(), notification)
    }

    companion object { const val CHANNEL_ID = "main_channel" }
}

// Remote Config — feature flags and A/B testing
class RemoteConfigManager {
    private val remoteConfig = Firebase.remoteConfig

    init {
        // Set defaults from local XML (used before fetch)
        remoteConfig.setDefaultsAsync(R.xml.remote_config_defaults)

        remoteConfig.setConfigSettingsAsync(remoteConfigSettings {
            minimumFetchIntervalInSeconds = if (BuildConfig.DEBUG) 0 else 3600  // 1hr in prod
        })
    }

    suspend fun fetchAndActivate(): Boolean {
        return try {
            remoteConfig.fetchAndActivate().await()
        } catch (e: Exception) {
            Log.e("RemoteConfig", "Fetch failed, using cached/defaults", e)
            false
        }
    }

    // Feature flags
    val isNewCheckoutEnabled: Boolean
        get() = remoteConfig.getBoolean("new_checkout_enabled")

    val maxCartItems: Int
        get() = remoteConfig.getLong("max_cart_items").toInt()

    val welcomeMessage: String
        get() = remoteConfig.getString("welcome_message")

    // A/B test variant
    val checkoutVariant: String
        get() = remoteConfig.getString("checkout_ab_variant")  // "control" | "variant_a" | "variant_b"
}

// Crashlytics — custom logging and user identification
class CrashlyticsManager {
    private val crashlytics = Firebase.crashlytics

    fun setUser(userId: String, email: String) {
        crashlytics.setUserId(userId)
        crashlytics.setCustomKey("email", email)
    }

    fun logEvent(event: String, data: Map<String, String> = emptyMap()) {
        crashlytics.log("EVENT: $event | ${data.entries.joinToString()}")
    }

    fun recordNonFatalError(error: Throwable, context: Map<String, String> = emptyMap()) {
        context.forEach { (key, value) -> crashlytics.setCustomKey(key, value) }
        crashlytics.recordException(error)
    }

    // Performance trace for a network call
    fun traceNetworkCall(url: String, block: () -> Unit) {
        val trace = Firebase.performance.newHttpMetric(url, FirebasePerformance.HttpMethod.GET)
        trace.start()
        try {
            block()
            trace.httpResponseCode = 200
        } catch (e: Exception) {
            trace.httpResponseCode = 500
            throw e
        } finally {
            trace.stop()
        }
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Writing Firestore security rules as <code>allow read, write: if true</code>:</strong> Exposes all data publicly — ✅ Fix: Always require <code>request.auth != null</code> at minimum; restrict writes to document owners</li>
        <li>❌ <strong>Not handling FCM token refresh:</strong> Tokens change after app re-install or Firebase service resets — ✅ Fix: Always implement <code>onNewToken()</code> and sync to backend immediately</li>
        <li>❌ <strong>Using Firestore for large binary data:</strong> Documents have a 1MB limit — ✅ Fix: Store binary files in Firebase Storage, store the download URL in Firestore</li>
        <li>❌ <strong>Not enabling Firestore offline persistence:</strong> App crashes when offline and tries to read data — ✅ Fix: Call <code>FirebaseFirestore.getInstance().firestoreSettings = firestoreSettings { isPersistenceEnabled = true }</code></li>
        <li>❌ <strong>Fetching Remote Config on every app launch:</strong> Can hit rate limits — ✅ Fix: Use <code>minimumFetchIntervalInSeconds = 3600</code> (1 hour) in production; Firebase caches the last fetch</li>
        <li>❌ <strong>Not removing Firestore listeners:</strong> Listeners keep a connection open, charging reads and draining battery — ✅ Fix: Call <code>listener.remove()</code> in <code>onStop()</code> or use <code>callbackFlow</code> with <code>awaitClose { listener.remove() }</code></li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Firebase is a powerful accelerant but requires discipline. Firestore is not a relational database — you must design your data model around your read patterns, denormalize aggressively, and think about security rules before writing any application code. In production, I structure Firestore security rules to enforce: authentication required, users can only write their own documents, and sensitive collections require role-based access checked against a users/{uid}/roles subcollection. For Crashlytics, I always set userId on sign-in and log key events so when a crash comes in I know exactly what the user was doing. For Remote Config, I never query it synchronously — I fetch on app start asynchronously and use cached/default values immediately; this prevents A/B testing from blocking the UI. FCM data messages (not notification messages) give you full control over the notification appearance in foreground, and you must handle token rotation properly or your notification delivery rate drops silently."</p>
      </div>
    </div>
  </div>

  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers — Firebase in Android</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the difference between Firestore and Firebase Realtime Database?</div>
      <div class="qa-answer">
        <p><strong>Firebase Realtime Database:</strong></p>
        <ul>
          <li>Single large JSON tree</li>
          <li>Simpler structure, lower cost for basic operations</li>
          <li>Better for simple real-time use cases (presence, chat)</li>
          <li>Limited querying (one orderBy, one filter)</li>
          <li>All data at a node is returned (can't select fields)</li>
          <li>One database per project (in legacy — now supports multiple)</li>
        </ul>
        <p><strong>Firestore:</strong></p>
        <ul>
          <li>Document-collection hierarchy with subcollections</li>
          <li>Richer queries (multiple where clauses, compound indexes)</li>
          <li>Automatic scaling, multi-region support</li>
          <li>Offline persistence built-in and more robust</li>
          <li>More expensive per read/write but more powerful</li>
          <li>Transactions and batch writes</li>
        </ul>
        <p>Choose Firestore for new projects. Use Realtime Database for legacy or simple presence/chat needs.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q2</span>What is the difference between FCM notification messages and data messages?</div>
      <div class="qa-answer">
        <p><strong>Notification messages</strong> (display messages): Firebase SDK automatically shows a system notification when the app is in background. You configure title/body in Firebase Console or server payload. When the app is in foreground, <code>onMessageReceived()</code> is called and you must show the notification yourself.</p>
        <p><strong>Data messages</strong>: Always delivered to <code>onMessageReceived()</code> regardless of app state (foreground/background/killed). Your code handles everything — you decide whether/how to show a notification. Payload is a key-value map (max 4KB). Use these when you need custom notification layouts, badge counts, or silent background syncs.</p>
        <p><strong>Combination messages</strong>: Both notification + data. In background, the notification part is auto-displayed; data is available in the intent extras when user taps. In foreground, <code>onMessageReceived()</code> handles both.</p>
        <p>Best practice: Use data-only messages for maximum control. The downside: app must be running to receive them when killed (unlike notification messages which the FCM SDK handles at OS level).</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>How do Firestore security rules work, and how do you write rules for a social app?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-javascript">rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // Helper functions
    function isAuthenticated() { return request.auth != null; }
    function isOwner(userId) { return request.auth.uid == userId; }
    function isAdmin() {
      return isAuthenticated() &&
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
    }

    // User profiles
    match /users/{userId} {
      allow read: if isAuthenticated();
      allow create: if isOwner(userId) && validUserData();
      allow update: if isOwner(userId) || isAdmin();
      allow delete: if isAdmin();

      function validUserData() {
        return request.resource.data.keys().hasOnly(['name', 'email', 'photoUrl', 'createdAt']) &&
               request.resource.data.name is string &&
               request.resource.data.name.size() <= 50;
      }
    }

    // Posts — only author can delete
    match /posts/{postId} {
      allow read: if isAuthenticated();
      allow create: if isAuthenticated() &&
        request.resource.data.authorId == request.auth.uid;
      allow update: if isOwner(resource.data.authorId);
      allow delete: if isOwner(resource.data.authorId) || isAdmin();
    }
  }
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q4</span>Your app has high Firestore read costs. How do you debug and reduce them?</div>
      <div class="qa-answer">
        <p>Steps to debug and reduce:</p>
        <ol>
          <li><strong>Firebase Console → Usage tab:</strong> Check daily read counts. Firebase shows reads per document.</li>
          <li><strong>Enable Firestore debug logging:</strong> <code>FirebaseFirestore.setLoggingEnabled(true)</code> to see each read in Logcat.</li>
          <li><strong>Common causes and fixes:</strong>
            <ul>
              <li>Forgetting to remove listeners — they keep streaming reads. Use <code>callbackFlow</code> with <code>awaitClose</code>.</li>
              <li>Using <code>.get()</code> instead of listeners where real-time isn't needed.</li>
              <li>Querying parent documents when only subcollection data is needed.</li>
              <li>Not using offline persistence — same data fetched repeatedly. Enable <code>isPersistenceEnabled = true</code>.</li>
              <li>Fetching entire collections instead of filtered queries.</li>
            </ul>
          </li>
          <li><strong>Use collection group queries carefully:</strong> They read across all subcollections.</li>
          <li><strong>Denormalize data:</strong> Store frequently-read data in the same document instead of doing multiple reads.</li>
          <li><strong>Use Firestore's limit():</strong> Never read unbounded collections.</li>
        </ol>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q5</span>How do you use Crashlytics to track a critical user flow and non-fatal errors?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">// Track checkout flow for debugging
class CheckoutViewModel : ViewModel() {
    private val crashlytics = Firebase.crashlytics

    fun startCheckout(cartId: String, amount: Double) {
        crashlytics.log("Checkout started: cartId=$cartId, amount=$amount")
        crashlytics.setCustomKey("checkout_cart_id", cartId)
        crashlytics.setCustomKey("checkout_amount", amount)
    }

    fun processPayment(paymentMethod: String) {
        crashlytics.log("Payment processing: method=$paymentMethod")
        crashlytics.setCustomKey("payment_method", paymentMethod)

        viewModelScope.launch {
            try {
                paymentRepository.processPayment(cartId, paymentMethod)
                crashlytics.log("Payment successful")
            } catch (e: PaymentDeclinedException) {
                // Non-fatal — user's card declined, not a bug
                crashlytics.recordException(e)
                _state.value = CheckoutState.PaymentDeclined(e.declineReason)
            } catch (e: NetworkException) {
                // Non-fatal — network issue, user should retry
                crashlytics.log("Payment failed due to network: ${e.message}")
                crashlytics.recordException(e)
                _state.value = CheckoutState.NetworkError
            }
            // Fatal crashes are auto-reported — no code needed
        }
    }
}
// In Firebase Console, you see: crash log shows exactly which cart was being
// processed, what payment method, and the full stack trace with context.</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q6</span>How do you implement Remote Config with safe defaults and A/B testing?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">// res/xml/remote_config_defaults.xml
/*
&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;defaultsMap&gt;
  &lt;entry&gt;&lt;key&gt;new_checkout_enabled&lt;/key&gt;&lt;value&gt;false&lt;/value&gt;&lt;/entry&gt;
  &lt;entry&gt;&lt;key&gt;max_retries&lt;/key&gt;&lt;value&gt;3&lt;/value&gt;&lt;/entry&gt;
  &lt;entry&gt;&lt;key&gt;promo_banner_text&lt;/key&gt;&lt;value&gt;Free shipping on orders over $50&lt;/value&gt;&lt;/entry&gt;
&lt;/defaultsMap&gt;
*/

// Safe Remote Config initialization at app startup
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        // Init Remote Config with defaults immediately (no network wait)
        Firebase.remoteConfig.setDefaultsAsync(R.xml.remote_config_defaults)

        // Fetch in background — won't block UI
        CoroutineScope(Dispatchers.IO).launch {
            try {
                Firebase.remoteConfig.apply {
                    setConfigSettingsAsync(remoteConfigSettings {
                        minimumFetchIntervalInSeconds = 3600
                    }).await()
                    fetchAndActivate().await()
                }
            } catch (e: Exception) {
                // Defaults are already set — app works without fetch
                Firebase.crashlytics.recordException(e)
            }
        }
    }
}
// A/B test: In Firebase Console, create Remote Config parameter "checkout_variant"
// with conditions: "A/B Test Group A" -> "variant_a", "Group B" -> "variant_b"
// Track which variant converts better using Analytics events</code></pre>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge — Offline-First Firestore with Local Cache</h3>
    <p><strong>Problem:</strong> Implement a repository that reads from Firestore with offline persistence enabled, shows cached data immediately, and refreshes from network in background. Handle the case where the user is offline gracefully.</p>
    <pre class="code-block"><code class="language-kotlin">// OfflineFirstUserRepository.kt
class OfflineFirstUserRepository(
    private val db: FirebaseFirestore = FirebaseFirestore.getInstance()
) {
    init {
        // Enable offline persistence (do this ONCE before any Firestore calls)
        db.firestoreSettings = firestoreSettings {
            isPersistenceEnabled = true
            cacheSizeBytes = FirebaseFirestoreSettings.CACHE_SIZE_UNLIMITED
        }
    }

    sealed class DataState<out T> {
        data class Success<T>(val data: T, val fromCache: Boolean) : DataState<T>()
        data class Error(val exception: Exception, val cachedData: Any? = null) : DataState<Nothing>()
        object Loading : DataState<Nothing>()
    }

    // Returns Flow that emits cached data first, then live data
    fun getUserProfile(userId: String): Flow<DataState<UserProfile>> = callbackFlow {
        trySend(DataState.Loading)

        val docRef = db.collection("users").document(userId)

        // First: try to get from cache immediately (Source.CACHE)
        try {
            val cachedDoc = docRef.get(Source.CACHE).await()
            if (cachedDoc.exists()) {
                val profile = cachedDoc.toObject(UserProfile::class.java)!!
                trySend(DataState.Success(profile, fromCache = true))
            }
        } catch (e: Exception) {
            // No cache available — that's OK
        }

        // Then: real-time listener for live updates
        val listener = docRef.addSnapshotListener { snapshot, error ->
            when {
                error != null -> {
                    // Offline: Firestore returns cached data with hasPendingWrites
                    trySend(DataState.Error(error))
                }
                snapshot != null && snapshot.exists() -> {
                    val profile = snapshot.toObject(UserProfile::class.java)!!
                    // snapshot.metadata.isFromCache tells us if this is cached
                    trySend(DataState.Success(
                        data = profile,
                        fromCache = snapshot.metadata.isFromCache
                    ))
                }
            }
        }

        awaitClose { listener.remove() }
    }

    // Write with offline support — Firestore queues writes when offline
    suspend fun updateUserProfile(userId: String, updates: Map<String, Any>): Result<Unit> {
        return try {
            db.collection("users").document(userId)
                .update(updates)
                .await()
            // If offline: .await() completes immediately (write is queued locally)
            // Firestore syncs when connectivity is restored
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// Usage in Fragment: show cached badge to inform user
viewModel.userProfile.collect { state ->
    when (state) {
        is DataState.Loading -> showShimmer()
        is DataState.Success -> {
            hideShimmer()
            displayProfile(state.data)
            binding.offlineBadge.isVisible = state.fromCache
        }
        is DataState.Error -> showError(state.exception.message)
    }
}
// Time: O(1) for Firestore reads (server handles indexing)
// The offline-first pattern ensures users always see data, even without connectivity
// Firestore's local cache is an SQLite database under the hood</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="37" data-item="0"> ✅ Understood Firebase Auth flow &amp; token management</label>
    <label class="progress-check"><input type="checkbox" data-topic="37" data-item="1"> ✅ Can implement Firestore real-time listeners as Flow</label>
    <label class="progress-check"><input type="checkbox" data-topic="37" data-item="2"> ✅ Reviewed FCM, Crashlytics, Remote Config patterns</label>
    <label class="progress-check"><input type="checkbox" data-topic="37" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="37" data-item="4"> ✅ Solved Coding Challenge</label>
  </div>
</section>
'''
