import json

topics = []

# ==============================================================================
# TOPIC 1: Kotlin Core & Advanced
# ==============================================================================
topics.append({
    "id": "topic-1",
    "num": "01",
    "title": "Kotlin Core & Advanced (with Collections)",
    "icon": "⚡",
    "badge": "Kotlin",
    "desc": "Master scope functions, inline/crossinline/noinline, reified type parameters, property & class delegation, sealed & value classes, and lazy collection pipelines.",
    "subtopics": [
        {
            "title": "Scope Functions (let, apply, run, with, also)",
            "what": "Scope functions execute a block of code within the context of an object. They differ across two fundamental axes: how the context object is accessed ('this' receiver vs 'it' argument) and what the expression returns (the context object itself vs the lambda result).",
            "why": "They eliminate repetitive temporary variable boilerplate, enable expressive builder/configuration pipelines, enforce null-safety, and isolate side-effects cleanly without polluting outer scopes.",
            "how": "Use 'apply' for object configuration (returns this), 'let' for null-checks and transformations (returns lambda result), 'also' for non-intrusive side-effects like logging or metrics (returns this), 'run' for computing a result from an object context (returns result), and 'with' for non-null receiver call grouping.",
            "code": """// Production Banking Token & OkHttp Builder Example
val secureClient = OkHttpClient.Builder().apply {
    connectTimeout(30, TimeUnit.SECONDS)
    readTimeout(30, TimeUnit.SECONDS)
    addInterceptor(AuthHeaderInterceptor())
    certificatePinner(CertificatePinner.Builder().add("api.bank.com", "sha256/k2v...").build())
}.build()

// Secure Token Extraction with 'let' and 'also'
fun handleAuthToken(encryptedToken: String?): SessionState {
    return encryptedToken?.let { raw ->
        val decrypted = keystoreDecrypt(raw)
        sessionManager.setAccessToken(decrypted)
        SessionState.Authenticated(decrypted.expiryTimestamp)
    }?.also { session ->
        auditLogger.logSecurityEvent("SessionActivated", session.expiry)
    } ?: run {
        auditLogger.logSecurityAlert("TokenMissingOrCorrupt")
        SessionState.Unauthenticated
    }
}""",
            "realworld": "In banking and fintech apps, scope functions prevent mutable token leakage. Using 'apply' guarantees atomic client construction with certificate pinners, while chaining 'let' with 'also' ensures every token decryption is paired with PCI-DSS audit logging without intermediate variable exposure."
        },
        {
            "title": "inline, crossinline, and noinline Bytecode Mechanics",
            "what": "In Kotlin, passing a lambda to a standard higher-order function compiles to an anonymous Function class instance on the heap. 'inline' tells the compiler to copy the function body and lambda directly into the call-site, eliminating object allocation. 'noinline' prevents inlining for specific lambda parameters, while 'crossinline' disallows non-local returns when a lambda executes in a different execution context (like a worker thread or nested lambda).",
            "why": "In performance-critical paths (Compose render loops at 60/90/120fps, RecyclerView binders, or CAN-bus telemetry in automotive), allocating thousands of lambda objects causes high garbage collector pressure, frame drops, and micro-stutters. 'inline' eliminates this heap overhead.",
            "how": "Mark hot utility functions with 'inline'. If one of the lambdas needs to be stored in a field or passed to another non-inlined function, mark it 'noinline'. If the lambda is executed inside an asynchronous callback or Runnable, mark it 'crossinline' to prevent the caller from issuing an invalid non-local 'return'.",
            "code": """// Automotive CAN-Bus / High-Frequency Event Loop
inline fun <T> measureAndProcess(
    data: T,
    crossinline onAsyncProcessed: (T) -> Unit,
    noinline errorRegistry: ((Throwable) -> Unit)?
) {
    val startNs = System.nanoTime()
    // Inlined synchronous processing: zero object allocation
    val filtered = sanitizePayload(data)
    
    // crossinline protects async boundary (non-local return forbidden)
    workerPool.execute {
        try {
            onAsyncProcessed(filtered)
        } catch (t: Throwable) {
            errorRegistry?.invoke(t) // noinline allows holding function reference
        }
    }
}""",
            "realworld": "In Automotive IVI clusters rendering at 60fps, high-frequency CAN sensor streams run at 100Hz. Using standard higher-order functions triggers frequent Dalvik/ART GC pauses (causing visible speedometer stutter). Inlining event dispatches keeps heap churn near zero."
        },
        {
            "title": "Reified Generics (Overcoming JVM Type Erasure)",
            "what": "Due to JVM type erasure, generic type arguments (like T in List<T>) are erased at runtime and replaced with Object. The 'reified' modifier, combined with 'inline', forces the compiler to inline the actual concrete class type into the bytecode at each specific call site, allowing runtime operations like 'T::class.java' and 'is T'.",
            "why": "Eliminates passing verbose 'Class<T>' or 'KClass<T>' arguments across your API, repository, and JSON parsing layers. Enables elegant, type-safe reflection, bundle extraction, and polymorphic deserialization.",
            "how": "Declare functions as 'inline fun <reified T>'. You can now directly query 'T::class.java', perform type checks like 'value is T', or safely cast with 'as? T'.",
            "code": """// Generic Type-Safe Polymorphic Parser for Healthcare FHIR
inline fun <reified T : FhirResource> parseFhirResponse(jsonPayload: String): Result<T> {
    return runCatching {
        val typeToken = object : com.google.gson.reflect.TypeToken<T>() {}.type
        gson.fromJson<T>(jsonPayload, typeToken)
    }.onFailure { ex ->
        Timber.e(ex, "Failed to parse FHIR payload into %s", T::class.java.simpleName)
    }
}

// Bundle Safe Extraction
inline fun <reified T : Parcelable> Bundle.getParcelableExtraCompat(key: String): T? {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        getParcelable(key, T::class.java)
    } else {
        @Suppress("DEPRECATION") getParcelable(key) as? T
    }
}""",
            "realworld": "In Healthcare (eHealth) apps consuming FHIR standards, identical API endpoints return polymorphic medical entities (Patient, Observation, DiagnosticReport). Reified extensions eliminate fragile when-type trees and Class<T> parameter passing across 40+ use cases."
        },
        {
            "title": "Property & Class Delegation (lazy, observable, vetoable, by delegate)",
            "what": "Delegation allows an object or property to forward its implementation to another helper. Property delegates implement ReadOnlyProperty or ReadWriteProperty via 'getValue'/'setValue'. Class delegation ('class B(a: A) : A by a') implements the Decorator pattern natively without boilerplate.",
            "why": "Promotes composition over inheritance (SOLID principle), enables thread-safe deferred initialization, reactive property listeners, and validation guards.",
            "how": "'lazy' supports three thread-safety modes: SYNCHRONIZED (double-checked locking, default), PUBLICATION (concurrent computation, first win), and NONE (single-threaded UI thread optimization). 'observable' executes after value modification, and 'vetoable' can reject a state mutation before it is applied.",
            "code": """// Custom Encrypted SharedPreferences Property Delegate
class EncryptedPref<T>(
    private val prefs: SharedPreferences,
    private val key: String,
    private val default: T
) : ReadWriteProperty<Any?, T> {
    @Suppress("UNCHECKED_CAST")
    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        return when (default) {
            is String -> prefs.getString(key, default) as T
            is Boolean -> prefs.getBoolean(key, default) as T
            is Int -> prefs.getInt(key, default) as T
            else -> throw IllegalArgumentException("Unsupported type")
        }
    }
    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        prefs.edit().apply {
            when (value) {
                is String -> putString(key, value)
                is Boolean -> putBoolean(key, value)
                is Int -> putInt(key, value)
            }
        }.apply()
    }
}

// Vetoable Security Guard for Banking Daily Transfer Limit
var dailyTransferLimit: Double by Delegates.vetoable(5000.0) { _, oldValue, newValue ->
    if (newValue > 25000.0) {
        securityAuditLogger.logFlaggedLimitChange(oldValue, newValue)
        false // VETO: Mutation rejected
    } else {
        true  // APPROVED
    }
}""",
            "realworld": "In digital banking apps, 'vetoable' property delegates guard against runtime tampering of transactional parameters before hitting backend APIs. Class delegation ('by delegate') allows decorating repository caches with biometric gating without modifying core repository logic."
        },
        {
            "title": "Kotlin Collections vs Sequences & Value Classes",
            "what": "Iterable collection operations (map, filter) are eager—each step instantiates a new intermediate List on the heap. 'Sequence' processes elements lazily one item at a time through the entire pipeline (pipelining), avoiding intermediate collections. Value classes (@JvmInline value class) wrap primitive types with zero heap allocation overhead at runtime.",
            "why": "Processing large lists (e.g. 5,000 transactions or medical logs) with eager chained operations creates massive temporary heap allocations that trigger GC churn. Value classes provide type safety (preventing AccNumber vs UserId bugs) with primitive runtime performance.",
            "how": "Use .asSequence() on large collections or unbounded streams before chaining multi-step transformations, and call .toList() at the terminal operator. Use '@JvmInline value class' for domain identifiers and currency amounts.",
            "code": """@JvmInline
value class AccountNumber(val value: String) {
    init { require(value.length == 10 && value.all { it.isDigit() }) { "Invalid account number" } }
}

// Processing 10,000 Transactions Efficiently via Sequence
fun processHighVolumeLedger(transactions: List<Transaction>): List<AuditRecord> {
    return transactions.asSequence()
        .filter { it.status == TransactionStatus.SETTLED }
        .filter { it.amount > 1000.0 }
        .map { txn -> AuditRecord(txn.id, txn.amount, hashPayload(txn)) }
        .take(50) // Terminal evaluation stops immediately once 50 matches are found!
        .toList()
}""",
            "realworld": "In high-throughput e-commerce checkouts or banking statement generation, using Sequence with .take(N) stops evaluating immediately when the target count is satisfied—saving hundreds of milliseconds compared to filtering the entire list eagerly."
        }
    ],
    "quizQuestions": [
        {
            "id": "q1-1",
            "question": "What is the exact bytecode difference between an inline function and a standard higher-order function? When does using 'inline' hurt performance?",
            "difficulty": "Senior",
            "thinkPrompt": "Consider what the Kotlin compiler generates under the hood (Java synthetic classes) and how inlining impacts binary DEX size.",
            "principalAnswer": "A standard higher-order function compiles each lambda argument into an anonymous class instance implementing kotlin.jvm.functions.FunctionN (e.g., new Function0() { public Object invoke() { ... } }). In hot paths, this allocates heap memory and causes virtual method dispatch. When marked 'inline', the compiler copies the actual bytecode instructions of both the function and lambda directly into the call site, eliminating heap allocation completely.\n\nHowever, inlining hurts performance when applied to large function bodies called from dozens or hundreds of locations. This causes binary bloat (expanded DEX size), increases the application's method count, pollutes the instruction cache (I-cache), and slows down compilation. Inlining should strictly be reserved for small functions taking lambda arguments in hot paths.",
            "keyPoints": ["FunctionN anonymous class instantiation", "Virtual method dispatch vs direct instruction inlining", "Zero heap allocation in hot paths", "DEX method bloat / instruction cache misses on large functions"],
            "pitfalls": ["Claiming inline should be added to every function", "Not knowing that lambdas generate anonymous classes", "Forgetting the DEX size trade-off"]
        },
        {
            "id": "q1-2",
            "question": "Explain 'crossinline' vs 'noinline'. Under what exact compiler error condition is 'crossinline' required?",
            "difficulty": "Lead / Staff",
            "thinkPrompt": "Think about non-local returns and thread execution boundaries. Why does the compiler reject a standard inlined lambda inside a Runnable?",
            "principalAnswer": "By default, an inlined lambda supports 'non-local return'—calling 'return' inside the lambda exits not just the lambda, but the enclosing calling function. However, if the inlined function passes the lambda into an execution context that runs outside the current stack frame—such as inside a Runnable, a local object expression, or a coroutine dispatcher—a non-local return is physically impossible because the calling function's stack frame has already unmounted or belongs to another thread.\n\nThe Kotlin compiler detects this and raises an error: 'Can't inline 'block' here: it may contain non-local returns'. Marking the parameter 'crossinline' resolves this by strictly forbidding the caller from placing a non-local 'return' inside the lambda while still allowing the function body to be inlined.\n\n'noinline' is different: it completely opts a lambda out of inlining, keeping it as an instance of FunctionN so it can be stored in a variable, passed to a non-inlined function, or returned.",
            "keyPoints": ["Non-local return mechanics", "Stack frame unmounting / asynchronous thread boundaries", "crossinline forbids non-local return while keeping call-site inlining", "noinline retains concrete FunctionN instance for storage/passing"],
            "pitfalls": ["Confusing crossinline with noinline", "Believing crossinline changes threading behavior (it only changes language return rules)"]
        },
        {
            "id": "q1-3",
            "question": "How does LazyThreadSafetyMode.SYNCHRONIZED work internally, and when should you choose PUBLICATION or NONE instead in Android?",
            "difficulty": "Senior",
            "thinkPrompt": "Consider double-checked locking, volatile memory barriers, and the thread context of UI vs Background.",
            "principalAnswer": "'lazy(LazyThreadSafetyMode.SYNCHRONIZED)' is the default. It uses double-checked locking with an internal synchronization monitor lock and a volatile backing field to guarantee that only one thread ever executes the initialization lambda, and all threads see the fully constructed instance.\n\n'LazyThreadSafetyMode.PUBLICATION' allows multiple threads to execute the initializer concurrently without blocking locks, but only the first thread that completes writes to the atomic reference; other results are discarded. Use this when the initializer is thread-safe, computationally cheap, and lock contention on a mutex is undesirable.\n\n'LazyThreadSafetyMode.NONE' performs zero thread synchronization and uses no locks. It is unsafe in multi-threaded contexts. In Android, you should explicitly use LazyThreadSafetyMode.NONE for properties accessed solely on the Main Thread (e.g. View binding references, formatters in Composable state holders, or Fragment-scoped UI helpers). This completely bypasses synchronization monitor overhead.",
            "keyPoints": ["SYNCHRONIZED uses double-checked locking & volatile barrier", "PUBLICATION uses compare-and-set atomic publication", "NONE removes all synchronization overhead for UI/MainThread-bound single thread contexts"],
            "pitfalls": ["Assuming lazy is always completely free of overhead", "Not knowing how to optimize lazy properties on the main thread with mode NONE"]
        }
    ]
})

# Output check
print(f"Generated Topic 1 with {len(topics[0]['subtopics'])} subtopics and {len(topics[0]['quizQuestions'])} quiz questions.")

with open("/Users/satdevkumar/.gemini/antigravity/scratch/android-interview-prep/js/topics-data.js", "w") as f:
    f.write("// Auto-generated Comprehensive Android Mastery Database\n")
    f.write("window.ANDROID_TOPICS = " + json.dumps(topics, indent=2) + ";\n")

print("Successfully initialized topics-data.js")
