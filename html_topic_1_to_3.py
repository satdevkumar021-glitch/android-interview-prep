# Generator for Topics 1, 2, 3

def get_topics_1_to_3_html():
    return """
    <!-- ============================================= -->
    <!-- TOPIC 1: KOTLIN CORE & ADVANCED               -->
    <!-- ============================================= -->
    <section class="topic-section" id="topic-1">
      <div class="topic-header">
        <span class="topic-number">01</span>
        <h1>Kotlin Core & Advanced (with Collections)</h1>
        <p class="topic-desc">Scope functions, inlining mechanics, reified generics, delegation patterns, sealed & value classes, and functional Sequence pipelines.</p>
        <div class="topic-tags">
          <span class="tag tag-kotlin">Kotlin</span>
          <span class="tag tag-architecture">Bytecode</span>
          <span class="tag tag-performance">Senior / Staff</span>
        </div>
      </div>

      <!-- Subtopic 1.1 -->
      <div class="subtopic" id="subtopic-1-1">
        <h2>1.1 Scope Functions (let, apply, run, with, also)</h2>
        
        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p>Scope functions execute a block of code within the context of an object, providing a temporary scope. They differ across two fundamental axes:
          <strong>(1) Context Object Access</strong> (<code>this</code> as extension receiver vs <code>it</code> as lambda argument), and 
          <strong>(2) Return Value</strong> (returns the context object itself vs returns the lambda result).</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> Without scope functions, configuring objects or performing consecutive transformations requires repetitive temporary local variables, introduces risk of mutable state leakage, and produces verbose null-check pyramids (e.g. <code>if (x != null) { ... }</code>).</p>
          <ul>
            <li><strong>Eliminates Mutable Intermediate State:</strong> Encapsulates initialization inside a distinct block so partially initialized objects are never leaked to the enclosing scope.</li>
            <li><strong>Enforces Immutability & Thread-Safety:</strong> Chaining <code>?.let { ... }</code> operates on an immutable snapshot, preventing race conditions where another thread nullifies a mutable field mid-execution.</li>
            <li><strong>Clean Separation of Side-Effects:</strong> <code>also</code> allows attaching logging, telemetry, or metric audits without breaking method chaining pipelines.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>// 1. apply: Object configuration (returns 'this')
val secureHttpClient = OkHttpClient.Builder().apply {
    connectTimeout(30, TimeUnit.SECONDS)
    readTimeout(30, TimeUnit.SECONDS)
    addInterceptor(AuthHeaderInterceptor())
    certificatePinner(CertificatePinner.Builder().add("api.bank.com", "sha256/k2v...").build())
}.build()

// 2. let + also + run: Safe token decryption, audit logging & fallback
fun processSessionToken(encryptedToken: String?): SessionState {
    return encryptedToken?.let { raw ->
        // Transform nullable raw string -> Decrypted Token
        val decrypted = keystoreDecrypt(raw)
        sessionStorage.saveAccessToken(decrypted)
        SessionState.Authenticated(decrypted.expiryEpoch)
    }?.also { session ->
        // Non-intrusive side-effect: audit logging (returns 'this')
        securityAuditLogger.logEvent("SESSION_ACTIVATED", session.expiryEpoch)
    } ?: run {
        // Fallback computation when encryptedToken is null
        securityAuditLogger.logAlert("TOKEN_MISSING_ABORT")
        SessionState.Unauthenticated
    }
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>FinTech / Banking:</strong> In high-security payment SDKs, user credentials and decrypted session tokens must never sit in accessible temporary variables on the stack. Chaining <code>?.let</code> guarantees the decrypted byte array is immediately consumed by the Keystore cipher and zeroed out in memory via <code>.also { bytes.fill(0) }</code>, complying with PCI-DSS data sanitization rules.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "When an interviewer asks about Scope Functions, I explain them across two axes: Receiver (<code>this</code> vs <code>it</code>) and Return value (context object vs lambda result). I highlight that <code>apply</code> is my default for builder configurations because it returns the receiver, while <code>let</code> is essential for null-safety transformations. Crucially, I point out that in multi-threaded environments, <code>nullableVar?.let { it.doSomething() }</code> is thread-safe because it copies the reference to a local parameter, unlike <code>if (nullableVar != null)</code> which can fail with a NullPointerException if another thread nullifies the backing field before execution."
          </div>
        </div>
      </div>

      <!-- Subtopic 1.2 -->
      <div class="subtopic" id="subtopic-1-2">
        <h2>1.2 Inlining Mechanics: inline, crossinline, and noinline</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p>In standard Kotlin, every higher-order function taking a lambda compiles down to an anonymous class on the heap implementing <code>FunctionN</code> (e.g. <code>Function0</code>, <code>Function1</code>). The <code>inline</code> modifier instructs the compiler to copy the function body and lambda bytecode directly into the call-site, eliminating object allocations. <code>noinline</code> exempts specific lambdas, while <code>crossinline</code> forbids non-local returns when a lambda executes in a different thread or execution context.</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> In hot loops (e.g. 60/90/120fps UI render passes in Compose, RecyclerView scrolling, or real-time sensor streams), allocating thousands of <code>FunctionN</code> instances creates severe Dalvik/ART Garbage Collection pressure, resulting in frame drops, micro-stutters, and battery drain.</p>
          <ul>
            <li><strong>Zero Heap Allocation:</strong> Completely eliminates object allocation and virtual method invocation overhead in performance-critical code.</li>
            <li><strong>Enables Non-Local Returns:</strong> Allows an inlined lambda to call <code>return</code> to exit the enclosing function early.</li>
            <li><strong>When NOT to use:</strong> Inlining large functions called across hundreds of sites causes severe DEX method count bloat and pollutes CPU instruction caches (I-cache).</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>// Automotive IVI / High-Frequency Telemetry Dispatcher
inline fun <T> dispatchVehicleTelemetry(
    data: T,
    crossinline onProcessedAsync: (T) -> Unit, // crossinline: prevents non-local return across thread boundary
    noinline errorObserver: ((Throwable) -> Unit)? // noinline: stored in a property / passed to another function
) {
    // 1. Inlined synchronous sanitization: zero object allocation
    val sanitized = sanitizeCanBusFrame(data)

    // 2. Offload to background worker pool
    backgroundWorkerPool.execute {
        try {
            // crossinline protects against illegal stack unmounting
            onProcessedAsync(sanitized)
        } catch (t: Throwable) {
            errorObserver?.invoke(t) // noinline allows holding function reference
        }
    }
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>Automotive IVI (AOSP):</strong> In Android Automotive digital clusters running at 60Hz, vehicle CAN-bus sensors emit engine speed, battery temperature, and ADAS telemetry at 100Hz. Inlining the telemetry filter pipelines prevents hundreds of thousands of heap allocations per minute, ensuring zero speedometer rendering lag.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "I explain that <code>inline</code> is not magic—it's a deliberate trade-off between memory allocation and binary size. In bytecode, standard lambdas create synthetic <code>FunctionN</code> instances. Inlining copies the bytecode directly to the call site. I explicitly call out <code>crossinline</code> as a compiler safety lock: when a lambda executes in another execution context (like inside a <code>Runnable</code> or Coroutine), non-local return is physically impossible because the caller's stack frame has already exited. <code>crossinline</code> forbids non-local return while preserving call-site inlining."
          </div>
        </div>
      </div>

      <!-- Subtopic 1.3 -->
      <div class="subtopic" id="subtopic-1-3">
        <h2>1.3 Reified Generics & Overcoming JVM Type Erasure</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p>On the JVM, generic type arguments (like <code>T</code> in <code>List&lt;T&gt;</code>) are erased at runtime due to backward compatibility. You cannot execute <code>T::class.java</code> or <code>value is T</code>. By combining <code>inline</code> with <code>reified</code>, the Kotlin compiler substitutes the concrete class type directly into the inlined call-site bytecode, making the type parameter accessible at runtime.</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> Without reified types, developers must explicitly pass clumsy <code>clazz: Class&lt;T&gt;</code> parameters through every API layer, repository, and JSON parser, introducing boilerplate and type casting errors.</p>
          <ul>
            <li><strong>Type-Safe Reflection & Deserialization:</strong> Direct access to <code>T::class.java</code> inside JSON parsers (Gson, Moshi) and Intent/Bundle extractors.</li>
            <li><strong>Type-Safe Casting:</strong> Enables natural type assertions like <code>if (item is T)</code> without <code>@Suppress("UNCHECKED_CAST")</code>.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>// 1. Polymorphic JSON Deserializer for Healthcare FHIR Resources
inline fun <reified T : FhirMedicalResource> parseFhirResponse(rawJson: String): Result<T> {
    return runCatching {
        // T::class.java is fully preserved and accessible!
        val typeToken = object : com.google.gson.reflect.TypeToken<T>() {}.type
        gson.fromJson<T>(rawJson, typeToken)
    }.onFailure { ex ->
        Timber.e(ex, "Failed to deserialize into %s", T::class.java.simpleName)
    }
}

// 2. Type-Safe Bundle Extra Extractor with Android 13 (Tiramisu) Compatibility
inline fun <reified T : Parcelable> Intent.getParcelableCompat(key: String): T? {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        getParcelableExtra(key, T::class.java)
    } else {
        @Suppress("DEPRECATION") getParcelableExtra(key) as? T
    }
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>Healthcare (eHealth / FHIR):</strong> Telemedicine platforms consume HL7/FHIR endpoints where a single resource endpoint polymorphically returns <code>Patient</code>, <code>DiagnosticReport</code>, or <code>MedicationRequest</code>. Reified generic parsers eliminate giant <code>when</code> branching trees and manual <code>Class&lt;T&gt;</code> plumbing across 30+ domain use cases.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "I frame reified types as the solution to Java's historic type erasure compromise. Because <code>inline</code> functions duplicate bytecode directly into the call-site where the exact type argument is already known to the compiler, Kotlin can substitute the concrete <code>Class&lt;T&gt;</code> directly into the generated bytecode. This gives us zero-overhead, type-safe reflection, clean Bundle extraction, and generic JSON parsing without passing redundant <code>Class&lt;T&gt;</code> tokens."
          </div>
        </div>
      </div>

      <!-- Q&A Section -->
      <div class="qa-section">
        <h2>🎯 Senior/Lead Interview Q&A (Kotlin Core & Advanced)</h2>

        <div class="qa-item" data-difficulty="basic">
          <div class="qa-question">
            <span class="qa-number">Q1</span>
            <span class="badge badge-basic">Basic</span>
            <p>What is the exact functional and bytecode difference between apply and also?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> Both functions return the receiver object. The distinction is in the lambda argument signature: <code>apply</code> accepts an extension lambda <code>T.() -> Unit</code>, binding the context object as <code>this</code> (ideal for multi-property object configuration). In contrast, <code>also</code> accepts <code>(T) -> Unit</code>, binding the context object as argument <code>it</code>. In bytecode, <code>also</code> avoids shadowing the outer class's <code>this</code> reference, making it the superior choice for non-intrusive side effects like logging, validation, and analytics.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="advanced">
          <div class="qa-question">
            <span class="qa-number">Q2</span>
            <span class="badge badge-advanced">Advanced</span>
            <p>What is the bytecode consequence of inlining higher-order functions? When should you avoid using inline?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> Non-inlined higher-order functions compile every lambda into a synthetic class implementing <code>kotlin.jvm.functions.FunctionN</code>, allocating an object on the heap and performing virtual method dispatch. Inlining copies the bytecode of both the caller and the lambda directly into the call site, eliminating heap allocations and method overhead.\n\nYou should avoid inlining when: (1) The function body is large and called from dozens of sites (causing severe DEX method bloat), (2) The function has no lambda parameters (inlining provides zero benefit here and compiler emits a warning), or (3) The lambda needs to be stored in a field or passed to another non-inlined function.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="advanced">
          <div class="qa-question">
            <span class="qa-number">Q3</span>
            <span class="badge badge-advanced">Advanced</span>
            <p>Compare LazyThreadSafetyMode: SYNCHRONIZED, PUBLICATION, and NONE. Which should you use in Android UI?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> <code>SYNCHRONIZED</code> (default) uses double-checked locking with a monitor lock and a volatile backing field to guarantee that exactly one thread initializes the value. <code>PUBLICATION</code> allows concurrent threads to run the initializer simultaneously without locks, using atomic CAS to write only the first completed result. <code>NONE</code> has zero thread synchronization and no locks. In Android, any property accessed strictly on the Main Thread (e.g., ViewBindings, UI formatters, ViewModel state holders) should explicitly use <code>LazyThreadSafetyMode.NONE</code> to completely bypass synchronization monitor overhead.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="scenario">
          <div class="qa-question">
            <span class="qa-number">Q4</span>
            <span class="badge badge-scenario">Scenario</span>
            <p>How do inline value classes eliminate heap allocation, and under what conditions does boxing occur?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> An <code>@JvmInline value class AccountId(val value: String)</code> replaces all usages with the underlying primitive or reference type (<code>String</code>) at the bytecode level, giving domain type safety with zero object wrapper overhead. Boxing occurs when: (1) The value class is used as a generic type argument (e.g. <code>List<AccountId></code>), (2) It is cast to an interface it implements, or (3) It is marked nullable (e.g. <code>AccountId?</code>), forcing the JVM to instantiate a wrapper object on the heap.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="scenario">
          <div class="qa-question">
            <span class="qa-number">Q5</span>
            <span class="badge badge-scenario">Scenario</span>
            <p>Design a zero-allocation high-frequency event bus using reified types and CopyOnWriteArrayList.</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <div class="code-block" data-language="kotlin">
              <pre><code>object FastEventBus {
    val subscribers = ConcurrentHashMap<KClass<*>, CopyOnWriteArrayList<(Any) -> Unit>>()

    inline fun <reified T : Any> subscribe(noinline observer: (T) -> Unit) {
        val list = subscribers.getOrPut(T::class) { CopyOnWriteArrayList() }
        @Suppress("UNCHECKED_CAST")
        list.add(observer as (Any) -> Unit)
    }

    inline fun <reified T : Any> publish(event: T) {
        subscribers[T::class]?.forEach { observer ->
            observer(event)
        }
    }
}</code></pre>
            </div>
          </div>
        </div>
      </div>

      <!-- Checklist -->
      <div class="topic-progress-tracker">
        <h3>✅ Topic 1 Mastery Checklist</h3>
        <label class="progress-check"><input type="checkbox" data-topic="1" data-item="0"> Scope Functions bytecode & usage differences</label>
        <label class="progress-check"><input type="checkbox" data-topic="1" data-item="1"> Mastered inline, crossinline, noinline & reified</label>
        <label class="progress-check"><input type="checkbox" data-topic="1" data-item="2"> LazyThreadSafetyMode (SYNCHRONIZED vs PUBLICATION vs NONE)</label>
        <label class="progress-check"><input type="checkbox" data-topic="1" data-item="3"> Value Classes (@JvmInline) & Bytecode Boxing</label>
        <label class="progress-check"><input type="checkbox" data-topic="1" data-item="4"> Answered & Mastered all 5 Topic 1 Q&As</label>
      </div>
    </section>

    <!-- ============================================= -->
    <!-- TOPIC 2: ANDROID COMPONENT LIFECYCLES         -->
    <!-- ============================================= -->
    <section class="topic-section" id="topic-2">
      <div class="topic-header">
        <span class="topic-number">02</span>
        <h1>Android Component Lifecycles & Process Death</h1>
        <p class="topic-desc">Activity/Fragment lifecycles, viewLifecycleOwner leak prevention, Configuration Change vs OS Process Death, SavedStateHandle, and PendingIntent security.</p>
        <div class="topic-tags">
          <span class="tag tag-architecture">Android SDK</span>
          <span class="tag tag-security">Security</span>
          <span class="tag tag-performance">Senior / Staff</span>
        </div>
      </div>

      <!-- Subtopic 2.1 -->
      <div class="subtopic" id="subtopic-2-1">
        <h2>2.1 Activity & Fragment Lifecycle & viewLifecycleOwner</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p>Activities manage 7 lifecycle states (<code>onCreate</code>, <code>onStart</code>, <code>onResume</code>, <code>onPause</code>, <code>onStop</code>, <code>onDestroy</code>, <code>onRestart</code>). Fragments possess TWO decoupled lifecycles: the <strong>Fragment instance lifecycle</strong> and the <strong>Fragment View lifecycle</strong> (represented by <code>viewLifecycleOwner</code>). When navigating backstacks, a Fragment's View is destroyed while its instance remains alive.</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> Registering LiveData or Flow observers with <code>this</code> (the Fragment instance) creates catastrophic memory leaks. When the Fragment moves to the backstack, its View is destroyed, but the observer remains registered. Upon returning, <code>onViewCreated</code> runs again, registering a second observer that holds onto the detached dead Views.</p>
          <ul>
            <li><strong>Prevents View Hierarchy Leaks:</strong> Binding observers to <code>viewLifecycleOwner</code> guarantees observation is automatically terminated when <code>onDestroyView()</code> fires.</li>
            <li><strong>Prevents NullPointerException on View Binding:</strong> Nullifying <code>_binding = null</code> in <code>onDestroyView()</code> releases references to garbage-collected Android views.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>class TransferConfirmationFragment : Fragment(R.layout.fragment_transfer) {
    private var _binding: FragmentTransferBinding? = null
    private val binding get() = _binding!! // Non-null accessor safe only between onCreateView and onDestroyView

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentTransferBinding.bind(view)

        // CRITICAL: Observe using viewLifecycleOwner, NEVER 'this'
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.transferState.collect { state ->
                    renderTransferUI(state)
                }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // MANDATORY: Nullify binding to allow GC of the entire View hierarchy
        _binding = null
    }
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>E-Commerce Checkout Funnel:</strong> In a multi-step checkout funnel (Cart &rarr; Address &rarr; Payment &rarr; Review), users frequently step backward and forward through the backstack. Forgetting to nullify ViewBinding or observing with <code>this</code> retains 4 complete screen view hierarchies in memory, causing OutOfMemory (OOM) crashes on low-RAM devices during high-resolution payment receipt generation.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "I emphasize to the interviewer that Fragments have two distinct lifecycles: the Fragment object lifecycle and the View lifecycle. When a transaction adds a Fragment to the backstack, <code>onDestroyView</code> destroys the UI widgets, but the Fragment object survives. If an engineer observes LiveData or Flow using <code>this</code> instead of <code>viewLifecycleOwner</code>, the observer survives the View destruction, retaining references to detached views and registering duplicate listeners on every re-entry. In my projects, I mandate <code>viewLifecycleOwner</code> and enforce ViewBinding nullification via strict Detekt/Lint rules."
          </div>
        </div>
      </div>

      <!-- Subtopic 2.2 -->
      <div class="subtopic" id="subtopic-2-2">
        <h2>2.2 Configuration Change vs OS Process Death (State Survival Matrix)</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p>During a <strong>Configuration Change</strong> (screen rotation, dark mode, locale), the Activity is destroyed and recreated, but the OS Linux process remains alive. During <strong>OS Process Death</strong>, the Android Low Memory Killer (LMK) forcibly terminates the backgrounded app process to reclaim RAM. The user later returns via Recents, and the OS recreates the task stack using the saved <code>Bundle</code>.</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> ViewModels survive rotation because they are retained via <code>NonConfigurationInstances</code>. However, ViewModels DO NOT survive process death. Relying entirely on ViewModel memory state causes app crashes or lost user input when returning from SMS/OTP apps.</p>
          <ul>
            <li><strong>State Survival Tier 1 (Runtime):</strong> ViewModel in-memory state for volatile UI state.</li>
            <li><strong>State Survival Tier 2 (Process Death):</strong> <code>SavedStateHandle</code> (backed by savedInstanceState Bundle) for critical IDs and user form inputs (&lt; 1MB limit).</li>
            <li><strong>State Survival Tier 3 (Persistent):</strong> Room database / DataStore for durable offline business data.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>// Resilient ViewModel Surviving Both Rotation and Process Death
@HiltViewModel
class SendMoneyViewModel @Inject constructor(
    private val savedStateHandle: SavedStateHandle, // Automatically restored after process death!
    private val transferRepo: TransferRepository
) : ViewModel() {

    // Backed by SavedStateHandle: Survives BOTH configuration change AND process death
    val recipientIban: StateFlow<String> = savedStateHandle.getStateFlow(KEY_IBAN, "")
    val transferAmount: StateFlow<Double> = savedStateHandle.getStateFlow(KEY_AMOUNT, 0.0)

    fun onIbanChanged(newIban: String) {
        savedStateHandle[KEY_IBAN] = newIban
    }

    fun onAmountChanged(amount: Double) {
        savedStateHandle[KEY_AMOUNT] = amount
    }

    companion object {
        private const val KEY_IBAN = "saved_iban_key"
        private const val KEY_AMOUNT = "saved_amount_key"
    }
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>FinTech Wire Transfers:</strong> A user enters an IBAN and $10,000 transfer amount, then switches to their banking SMS app to copy a 6-digit OTP. The OS kills the banking app due to background RAM pressure. When the user returns via Recents, <code>SavedStateHandle</code> immediately restores the exact transfer wizard state, preventing user frustration and abandoned transactions.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "I explain the State Survival Hierarchy: ViewModels survive configuration changes because the <code>ViewModelStore</code> is retained across activity destruction via non-configuration instances. But when the OS kills the process to reclaim RAM, all memory—including ViewModels and static singletons—is wiped. To guarantee resilience, I store UI navigation arguments and form inputs in <code>SavedStateHandle</code>, while persisting heavy business state in Room. I verify this in development by backgrounding the app and running <code>adb shell am kill <package_name></code>."
          </div>
        </div>
      </div>

      <!-- Q&A Section -->
      <div class="qa-section">
        <h2>🎯 Senior/Lead Interview Q&A (Component Lifecycles & Process Death)</h2>

        <div class="qa-item" data-difficulty="basic">
          <div class="qa-question">
            <span class="qa-number">Q1</span>
            <span class="badge badge-basic">Basic</span>
            <p>What is the difference between onStop() and onDestroy()?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> <code>onStop()</code> is called when the Activity is no longer visible to the user (e.g., navigated to another activity, app sent to background). Heavy resources like camera hardware, location updates, and UI animations should be released here. <code>onDestroy()</code> is called before the activity instance is destroyed (either finishing via <code>finish()</code> or during configuration change). In low-memory scenarios, the OS may kill the process directly after <code>onStop()</code> without ever calling <code>onDestroy()</code>.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="advanced">
          <div class="qa-question">
            <span class="qa-number">Q2</span>
            <span class="badge badge-advanced">Advanced</span>
            <p>Why do ViewModels survive configuration changes but NOT OS process death?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> During a configuration change, the Activity's <code>ViewModelStore</code> is preserved by the Android framework using <code>Activity.onRetainNonConfigurationInstance()</code> and re-injected into the new Activity instance. However, during OS Process Death, the OS terminates the entire Linux process hosting the application. All JVM heap memory—including ViewModels, static singletons, and thread pools—is completely destroyed. Only data written to the <code>savedInstanceState</code> Bundle (or SavedStateHandle) and persistent storage (Room/Disk) survives.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="advanced">
          <div class="qa-question">
            <span class="qa-number">Q3</span>
            <span class="badge badge-advanced">Advanced</span>
            <p>What is PendingIntent mutability in Android 12+ (API 31) and what vulnerability does it address?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> A PendingIntent delegates authorization to another application to execute an Intent with your app's permissions. Prior to Android 12, PendingIntents were mutable by default. A malicious application could intercept a mutable PendingIntent and overwrite its internal extras, action, or data URI (PendingIntent Injection), gaining unauthorized access to unexported components. Starting in Android 12, developers must explicitly declare either <code>FLAG_IMMUTABLE</code> (recommended for notifications) or <code>FLAG_MUTABLE</code> (only if external apps need to populate inputs, like inline notification replies).</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="scenario">
          <div class="qa-question">
            <span class="qa-number">Q4</span>
            <span class="badge badge-scenario">Scenario</span>
            <p>A user reports that opening their banking app from Recents crashes with a NullPointerException after 15 minutes of inactivity. What is the root cause and architectural fix?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> <strong>Root Cause:</strong> OS Process Death. While backgrounded, the OS killed the process. Upon return via Recents, Android recreated the top Fragment from the backstack, but the in-memory singleton or ViewModel holding the authenticated user session was wiped, causing a NullPointerException when accessing <code>sessionManager.currentUser.id</code>.\n\n<strong>Fix:</strong> (1) Inject <code>SavedStateHandle</code> into the ViewModel to restore the active user account ID and wizard state, (2) If the session token has expired, detect unauthenticated state in the ViewModel's initialization block and trigger a clean navigation redirect to the Login screen with a 'Session Expired' banner.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="scenario">
          <div class="qa-number">Q5</div>
          <div class="qa-question">
            <span class="badge badge-scenario">Scenario</span>
            <p>How do you test OS Process Death deterministically on an Android test device or emulator?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> (1) Navigate to the target screen and enter form data. (2) Press the Home button to place the app in the background (forcing <code>onSaveInstanceState</code> to execute and save the Bundle to the OS). (3) In terminal, run: <code>adb shell am kill &lt;package_name&gt;</code>. (4) Reopen the app from Recents. If the app crashes or fails to restore the user's entered state, process death restoration is broken. (Note: Do NOT press the red 'Stop' button in Android Studio, as that kills the task completely without saving state).</p>
          </div>
        </div>
      </div>

      <!-- Checklist -->
      <div class="topic-progress-tracker">
        <h3>✅ Topic 2 Mastery Checklist</h3>
        <label class="progress-check"><input type="checkbox" data-topic="2" data-item="0"> Activity & Fragment lifecycle state transitions</label>
        <label class="progress-check"><input type="checkbox" data-topic="2" data-item="1"> viewLifecycleOwner vs this leak prevention</label>
        <label class="progress-check"><input type="checkbox" data-topic="2" data-item="2"> SavedStateHandle vs ViewModelStore retention</label>
        <label class="progress-check"><input type="checkbox" data-topic="2" data-item="3"> PendingIntent FLAG_IMMUTABLE security requirement</label>
        <label class="progress-check"><input type="checkbox" data-topic="2" data-item="4"> Answered & Mastered all 5 Topic 2 Q&As</label>
      </div>
    </section>

    <!-- ============================================= -->
    <!-- TOPIC 3: SERVICES & BACKGROUND PROCESSING    -->
    <!-- ============================================= -->
    <section class="topic-section" id="topic-3">
      <div class="topic-header">
        <span class="topic-number">03</span>
        <h1>Services & Background Processing</h1>
        <p class="topic-desc">Started, Bound, and Foreground Services, Android 14 foregroundServiceType requirements, WorkManager chaining and constraints, and Doze mode policies.</p>
        <div class="topic-tags">
          <span class="tag tag-architecture">Services</span>
          <span class="tag tag-performance">WorkManager</span>
          <span class="tag tag-security">Senior / Staff</span>
        </div>
      </div>

      <!-- Subtopic 3.1 -->
      <div class="subtopic" id="subtopic-3-1">
        <h2>3.1 Foreground Services & Android 14 (API 34) Strict Typing</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p>A Foreground Service executes tasks that are actively noticeable to the user and displays an ongoing, non-dismissible notification. In Android 14 (API 34), Google mandates that every Foreground Service explicitly declare an <code>android:foregroundServiceType</code> (e.g. <code>dataSync</code>, <code>location</code>, <code>mediaPlayback</code>, <code>connectedDevice</code>) in the Manifest and request a corresponding runtime permission.</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> In Android 8.0+, background services cannot be started when the app is backgrounded. Normal background tasks are aggressively killed by Android's Low Memory Killer (LMK). Foreground services elevate process priority, guaranteeing the OS will not kill the process during long-running tasks.</p>
          <ul>
            <li><strong>Process Priority Elevation:</strong> Places the app process in the Foreground Priority bucket, preventing termination during heavy memory pressure.</li>
            <li><strong>User Transparency:</strong> Enforces transparency through ongoing status bar notifications so rogue apps cannot secretly drain battery or capture GPS in the background.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>// 1. AndroidManifest.xml (Android 14 Requirements)
<service
    android:name=".upload.DocumentUploadService"
    android:foregroundServiceType="dataSync"
    android:exported="false" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />

// 2. Service Implementation with Notification
class DocumentUploadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createPersistentNotification("Uploading encrypted medical record...")
        
        // Android 14 Compliant Foreground Invocation
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            ServiceCompat.startForeground(
                this,
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }

        serviceScope.launch(Dispatchers.IO) {
            performUpload()
            stopSelf(startId) // Always stop with startId to avoid terminating newer concurrent requests
        }
        return START_NOT_STICKY
    }
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>Healthcare Telemedicine:</strong> Uploading 500MB DICOM radiological imaging scans from mobile clinics to hospital cloud archives requires a Foreground Service of type <code>dataSync</code>. If the physician switches to another app or the device screen turns off, the upload continues uninterrupted without LMK termination.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "I explain that background processing in Android has evolved into two clear paradigms: <strong>WorkManager</strong> for persistent, deferrable work, and <strong>Foreground Services</strong> for immediate, user-facing active work. In Android 14, Foreground Services now enforce strict type declarations—you cannot simply launch a generic service. You must declare types like <code>dataSync</code> or <code>mediaPlayback</code> and justify their usage during Play Store review. I also emphasize calling <code>stopSelf(startId)</code> rather than <code>stopSelf()</code> to prevent terminating newer incoming upload intents."
          </div>
        </div>
      </div>

      <!-- Subtopic 3.2 -->
      <div class="subtopic" id="subtopic-3-2">
        <h2>3.2 WorkManager Chaining, Constraints & CoroutineWorker</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p>WorkManager is Google's recommended library for persistent, deferrable background tasks. It automatically delegates work to <code>JobScheduler</code> (API 23+) or legacy AlarmManager/BroadcastReceiver pipelines while persisting job definitions in an internal SQLite database. <code>CoroutineWorker</code> integrates natively with Kotlin Coroutines for asynchronous work.</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> Standard Coroutines in ViewModels die when the process is killed. AlarmManager is designed for exact wall-clock alarms, not network tasks. JobScheduler requires complex API branching. WorkManager guarantees execution even if the app process is terminated or the device reboots.</p>
          <ul>
            <li><strong>Guaranteed Persistent Execution:</strong> Tasks persist across device reboots and low-memory process kills.</li>
            <li><strong>Hardware-Aware Constraints:</strong> Executes work only when battery is not low, device is charging, or connection is unmetered (Wi-Fi).</li>
            <li><strong>Automatic Exponential Backoff:</strong> Intelligently retries failed network jobs with randomized jitter.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>// 1. CoroutineWorker Implementation
class LedgerSyncWorker(
    appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        return@withContext try {
            val syncRepository = EntryPointAccessors.fromApplication(
                applicationContext, WorkerEntryPoint::class.java
            ).syncRepository()

            syncRepository.uploadPendingTransactions()
            Result.success()
        } catch (e: IOException) {
            // Transient network error: retry with exponential backoff
            Result.retry()
        } catch (e: Exception) {
            // Fatal business error: do not retry
            Result.failure()
        }
    }
}

// 2. Chained Execution Pipeline with Constraints
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED) // Wi-Fi only
    .setRequiresBatteryNotLow(true)
    .build()

val compressWork = OneTimeWorkRequestBuilder<CompressLogsWorker>().build()
val encryptWork = OneTimeWorkRequestBuilder<EncryptLogsWorker>().build()
val uploadWork = OneTimeWorkRequestBuilder<LedgerSyncWorker>()
    .setConstraints(constraints)
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.SECONDS)
    .build()

WorkManager.getInstance(context)
    .beginUniqueWork("ledger_sync_pipeline", ExistingWorkPolicy.KEEP, compressWork)
    .then(encryptWork)
    .then(uploadWork)
    .enqueue()</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>E-Commerce / FinTech:</strong> In an offline-first payment app where users perform transactions in areas with intermittent connectivity (e.g. underground subways), WorkManager queues transaction payloads with <code>ExistingWorkPolicy.APPEND_OR_REPLACE</code>, guaranteeing they are pushed to banking ledgers the moment an unmetered network connection is detected.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "I describe WorkManager as the single source of truth for persistent background work in Android. I outline the decision matrix: if work is deferrable and must survive reboots, use WorkManager. If work is immediate and requires ongoing user awareness, use a Foreground Service. If it's an exact time-based trigger like an alarm clock, use AlarmManager. In production, I always use <code>CoroutineWorker</code>, set explicit backoff criteria, and use unique work chains (<code>beginUniqueWork</code>) to prevent duplicate background execution."
          </div>
        </div>
      </div>

      <!-- Q&A Section -->
      <div class="qa-section">
        <h2>🎯 Senior/Lead Interview Q&A (Services & WorkManager)</h2>

        <div class="qa-item" data-difficulty="basic">
          <div class="qa-question">
            <span class="qa-number">Q1</span>
            <span class="badge badge-basic">Basic</span>
            <p>What thread does a Service run on by default? How do you avoid ANR in a Service?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> A Service runs on the <strong>Main (UI) Thread</strong> by default! It does not create its own thread or process. If you execute blocking disk I/O, heavy crypto, or network calls directly inside <code>onStartCommand()</code>, you will trigger an Application Not Responding (ANR) error after 20 seconds. To avoid ANRs, you must explicitly launch background coroutines on <code>Dispatchers.IO</code> or use WorkManager for asynchronous task execution.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="advanced">
          <div class="qa-question">
            <span class="qa-number">Q2</span>
            <span class="badge badge-advanced">Advanced</span>
            <p>Explain the difference between START_STICKY, START_NOT_STICKY, and START_REDELIVER_INTENT.</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> When the OS kills a Started Service under memory pressure:\n1. <code>START_NOT_STICKY</code>: The OS will NOT recreate the service unless there are new pending start intents. Ideal for transient tasks like periodic polling.\n2. <code>START_STICKY</code>: The OS recreates the service and calls <code>onStartCommand</code> with a <strong>null Intent</strong>. Ideal for continuous services that manage their own state (e.g., audio playback, background socket managers).\n3. <code>START_REDELIVER_INTENT</code>: The OS recreates the service and redelivers the exact original Intent that was executing prior to the kill. Ideal for critical file downloads or transactional operations where the intent payload is mandatory to complete the job.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="advanced">
          <div class="qa-question">
            <span class="qa-number">Q3</span>
            <span class="badge badge-advanced">Advanced</span>
            <p>How does Doze Mode affect background execution and how does WorkManager navigate it?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> Doze Mode activates when an unplugged device is stationary with screen off for a prolonged period. It imposes restrictions: network access is suspended, wakelocks are ignored, and standard alarms/JobScheduler jobs are deferred until periodic 'Maintenance Windows'. WorkManager automatically respects Doze Mode: its jobs are batched into these maintenance windows. If critical immediate execution is required, WorkManager supports 'Expedited Work' (using Foreground Service quotas under the hood) to bypass standard Doze deferrals.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="scenario">
          <div class="qa-number">Q4</div>
          <div class="qa-question">
            <span class="badge badge-scenario">Scenario</span>
            <p>Why did Android 14 introduce strict Foreground Service Types, and what happens if you call startForeground() with an undeclared type?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> Google introduced strict Foreground Service Types in Android 14 to eliminate battery abuses where apps launched generic foreground services to keep processes permanently alive in the background. If you attempt to call <code>startForeground()</code> with a type (like <code>dataSync</code> or <code>location</code>) that was not explicitly declared in the Manifest's <code>android:foregroundServiceType</code> attribute, the framework throws a fatal <code>SecurityException: Starting FGS with type ... that was not declared in manifest</code>, immediately crashing the app.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="scenario">
          <div class="qa-number">Q5</div>
          <div class="qa-question">
            <span class="badge badge-scenario">Scenario</span>
            <p>Design a zero-loss offline file upload engine using WorkManager with retry limits and exponential backoff.</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <div class="code-block" data-language="kotlin">
              <pre><code>val uploadWorkRequest = OneTimeWorkRequestBuilder<SecureFileUploadWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        WorkRequest.MIN_BACKOFF_MILLIS, // 10 seconds
        TimeUnit.MILLISECONDS
    )
    .setInputData(workDataOf("FILE_URI" to fileUri.toString()))
    .build()

WorkManager.getInstance(context).enqueueUniqueWork(
    "upload_${fileId}",
    ExistingWorkPolicy.KEEP, // Prevent duplicate upload jobs
    uploadWorkRequest
)</code></pre>
            </div>
          </div>
        </div>
      </div>

      <!-- Checklist -->
      <div class="topic-progress-tracker">
        <h3>✅ Topic 3 Mastery Checklist</h3>
        <label class="progress-check"><input type="checkbox" data-topic="3" data-item="0"> Services run on Main Thread by default</label>
        <label class="progress-check"><input type="checkbox" data-topic="3" data-item="1"> Android 14 foregroundServiceType requirements</label>
        <label class="progress-check"><input type="checkbox" data-topic="3" data-item="2"> START_STICKY vs START_NOT_STICKY vs START_REDELIVER_INTENT</label>
        <label class="progress-check"><input type="checkbox" data-topic="3" data-item="3"> WorkManager CoroutineWorker with exponential backoff</label>
        <label class="progress-check"><input type="checkbox" data-topic="3" data-item="4"> Answered & Mastered all 5 Topic 3 Q&As</label>
      </div>
    </section>
    """

if __name__ == '__main__':
    print("html_topic_1_to_3 loaded successfully.")
