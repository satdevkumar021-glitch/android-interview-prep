// Android Interview Mastery Database - Complete 12 Comprehensive Modules
window.ANDROID_TOPICS = [
  {
    "id": "topic-1",
    "num": "01",
    "title": "Kotlin Core & Advanced (with Collections)",
    "icon": "\u26a1",
    "badge": "Kotlin",
    "desc": "Master scope functions, inline/crossinline/noinline, reified type parameters, property & class delegation, sealed & value classes, and lazy collection pipelines.",
    "subtopics": [
      {
        "title": "Scope Functions (let, apply, run, with, also)",
        "what": "Scope functions execute a block of code within the context of an object. They differ across two fundamental axes: how the context object is accessed ('this' receiver vs 'it' argument) and what the expression returns (the context object itself vs the lambda result).",
        "why": "They eliminate repetitive temporary variable boilerplate, enable expressive builder/configuration pipelines, enforce null-safety, and isolate side-effects cleanly without polluting outer scopes.",
        "how": "Use 'apply' for object configuration (returns this), 'let' for null-checks and transformations (returns lambda result), 'also' for non-intrusive side-effects like logging or metrics (returns this), 'run' for computing a result from an object context (returns result), and 'with' for non-null receiver call grouping.",
        "code": "// Production Banking Token & OkHttp Builder Example\nval secureClient = OkHttpClient.Builder().apply {\n    connectTimeout(30, TimeUnit.SECONDS)\n    readTimeout(30, TimeUnit.SECONDS)\n    addInterceptor(AuthHeaderInterceptor())\n    certificatePinner(CertificatePinner.Builder().add(\"api.bank.com\", \"sha256/k2v...\").build())\n}.build()\n\n// Secure Token Extraction with 'let' and 'also'\nfun handleAuthToken(encryptedToken: String?): SessionState {\n    return encryptedToken?.let { raw ->\n        val decrypted = keystoreDecrypt(raw)\n        sessionManager.setAccessToken(decrypted)\n        SessionState.Authenticated(decrypted.expiryTimestamp)\n    }?.also { session ->\n        auditLogger.logSecurityEvent(\"SessionActivated\", session.expiry)\n    } ?: run {\n        auditLogger.logSecurityAlert(\"TokenMissingOrCorrupt\")\n        SessionState.Unauthenticated\n    }\n}",
        "realworld": "In banking and fintech apps, scope functions prevent mutable token leakage. Using 'apply' guarantees atomic client construction with certificate pinners, while chaining 'let' with 'also' ensures every token decryption is paired with PCI-DSS audit logging without intermediate variable exposure."
      },
      {
        "title": "inline, crossinline, and noinline Bytecode Mechanics",
        "what": "In Kotlin, passing a lambda to a standard higher-order function compiles to an anonymous Function class instance on the heap. 'inline' tells the compiler to copy the function body and lambda directly into the call-site, eliminating object allocation. 'noinline' prevents inlining for specific lambda parameters, while 'crossinline' disallows non-local returns when a lambda executes in a different execution context (like a worker thread or nested lambda).",
        "why": "In performance-critical paths (Compose render loops at 60/90/120fps, RecyclerView binders, or CAN-bus telemetry in automotive), allocating thousands of lambda objects causes high garbage collector pressure, frame drops, and micro-stutters. 'inline' eliminates this heap overhead.",
        "how": "Mark hot utility functions with 'inline'. If one of the lambdas needs to be stored in a field or passed to another non-inlined function, mark it 'noinline'. If the lambda is executed inside an asynchronous callback or Runnable, mark it 'crossinline' to prevent the caller from issuing an invalid non-local 'return'.",
        "code": "// Automotive CAN-Bus / High-Frequency Event Loop\ninline fun <T> measureAndProcess(\n    data: T,\n    crossinline onAsyncProcessed: (T) -> Unit,\n    noinline errorRegistry: ((Throwable) -> Unit)?\n) {\n    val startNs = System.nanoTime()\n    // Inlined synchronous processing: zero object allocation\n    val filtered = sanitizePayload(data)\n    \n    // crossinline protects async boundary (non-local return forbidden)\n    workerPool.execute {\n        try {\n            onAsyncProcessed(filtered)\n        } catch (t: Throwable) {\n            errorRegistry?.invoke(t) // noinline allows holding function reference\n        }\n    }\n}",
        "realworld": "In Automotive IVI clusters rendering at 60fps, high-frequency CAN sensor streams run at 100Hz. Using standard higher-order functions triggers frequent Dalvik/ART GC pauses (causing visible speedometer stutter). Inlining event dispatches keeps heap churn near zero."
      },
      {
        "title": "Reified Generics (Overcoming JVM Type Erasure)",
        "what": "Due to JVM type erasure, generic type arguments (like T in List<T>) are erased at runtime and replaced with Object. The 'reified' modifier, combined with 'inline', forces the compiler to inline the actual concrete class type into the bytecode at each specific call site, allowing runtime operations like 'T::class.java' and 'is T'.",
        "why": "Eliminates passing verbose 'Class<T>' or 'KClass<T>' arguments across your API, repository, and JSON parsing layers. Enables elegant, type-safe reflection, bundle extraction, and polymorphic deserialization.",
        "how": "Declare functions as 'inline fun <reified T>'. You can now directly query 'T::class.java', perform type checks like 'value is T', or safely cast with 'as? T'.",
        "code": "// Generic Type-Safe Polymorphic Parser for Healthcare FHIR\ninline fun <reified T : FhirResource> parseFhirResponse(jsonPayload: String): Result<T> {\n    return runCatching {\n        val typeToken = object : com.google.gson.reflect.TypeToken<T>() {}.type\n        gson.fromJson<T>(jsonPayload, typeToken)\n    }.onFailure { ex ->\n        Timber.e(ex, \"Failed to parse FHIR payload into %s\", T::class.java.simpleName)\n    }\n}\n\n// Bundle Safe Extraction\ninline fun <reified T : Parcelable> Bundle.getParcelableExtraCompat(key: String): T? {\n    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {\n        getParcelable(key, T::class.java)\n    } else {\n        @Suppress(\"DEPRECATION\") getParcelable(key) as? T\n    }\n}",
        "realworld": "In Healthcare (eHealth) apps consuming FHIR standards, identical API endpoints return polymorphic medical entities (Patient, Observation, DiagnosticReport). Reified extensions eliminate fragile when-type trees and Class<T> parameter passing across 40+ use cases."
      },
      {
        "title": "Property & Class Delegation (lazy, observable, vetoable, by delegate)",
        "what": "Delegation allows an object or property to forward its implementation to another helper. Property delegates implement ReadOnlyProperty or ReadWriteProperty via 'getValue'/'setValue'. Class delegation ('class B(a: A) : A by a') implements the Decorator pattern natively without boilerplate.",
        "why": "Promotes composition over inheritance (SOLID principle), enables thread-safe deferred initialization, reactive property listeners, and validation guards.",
        "how": "'lazy' supports three thread-safety modes: SYNCHRONIZED (double-checked locking, default), PUBLICATION (concurrent computation, first win), and NONE (single-threaded UI thread optimization). 'observable' executes after value modification, and 'vetoable' can reject a state mutation before it is applied.",
        "code": "// Custom Encrypted SharedPreferences Property Delegate\nclass EncryptedPref<T>(\n    private val prefs: SharedPreferences,\n    private val key: String,\n    private val default: T\n) : ReadWriteProperty<Any?, T> {\n    @Suppress(\"UNCHECKED_CAST\")\n    override fun getValue(thisRef: Any?, property: KProperty<*>): T {\n        return when (default) {\n            is String -> prefs.getString(key, default) as T\n            is Boolean -> prefs.getBoolean(key, default) as T\n            is Int -> prefs.getInt(key, default) as T\n            else -> throw IllegalArgumentException(\"Unsupported type\")\n        }\n    }\n    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {\n        prefs.edit().apply {\n            when (value) {\n                is String -> putString(key, value)\n                is Boolean -> putBoolean(key, value)\n                is Int -> putInt(key, value)\n            }\n        }.apply()\n    }\n}\n\n// Vetoable Security Guard for Banking Daily Transfer Limit\nvar dailyTransferLimit: Double by Delegates.vetoable(5000.0) { _, oldValue, newValue ->\n    if (newValue > 25000.0) {\n        securityAuditLogger.logFlaggedLimitChange(oldValue, newValue)\n        false // VETO: Mutation rejected\n    } else {\n        true  // APPROVED\n    }\n}",
        "realworld": "In digital banking apps, 'vetoable' property delegates guard against runtime tampering of transactional parameters before hitting backend APIs. Class delegation ('by delegate') allows decorating repository caches with biometric gating without modifying core repository logic."
      },
      {
        "title": "Kotlin Collections vs Sequences & Value Classes",
        "what": "Iterable collection operations (map, filter) are eager\u2014each step instantiates a new intermediate List on the heap. 'Sequence' processes elements lazily one item at a time through the entire pipeline (pipelining), avoiding intermediate collections. Value classes (@JvmInline value class) wrap primitive types with zero heap allocation overhead at runtime.",
        "why": "Processing large lists (e.g. 5,000 transactions or medical logs) with eager chained operations creates massive temporary heap allocations that trigger GC churn. Value classes provide type safety (preventing AccNumber vs UserId bugs) with primitive runtime performance.",
        "how": "Use .asSequence() on large collections or unbounded streams before chaining multi-step transformations, and call .toList() at the terminal operator. Use '@JvmInline value class' for domain identifiers and currency amounts.",
        "code": "@JvmInline\nvalue class AccountNumber(val value: String) {\n    init { require(value.length == 10 && value.all { it.isDigit() }) { \"Invalid account number\" } }\n}\n\n// Processing 10,000 Transactions Efficiently via Sequence\nfun processHighVolumeLedger(transactions: List<Transaction>): List<AuditRecord> {\n    return transactions.asSequence()\n        .filter { it.status == TransactionStatus.SETTLED }\n        .filter { it.amount > 1000.0 }\n        .map { txn -> AuditRecord(txn.id, txn.amount, hashPayload(txn)) }\n        .take(50) // Terminal evaluation stops immediately once 50 matches are found!\n        .toList()\n}",
        "realworld": "In high-throughput e-commerce checkouts or banking statement generation, using Sequence with .take(N) stops evaluating immediately when the target count is satisfied\u2014saving hundreds of milliseconds compared to filtering the entire list eagerly."
      }
    ],
    "quizQuestions": [
      {
        "id": "q1-1",
        "question": "What is the exact bytecode difference between an inline function and a standard higher-order function? When does using 'inline' hurt performance?",
        "difficulty": "Senior",
        "thinkPrompt": "Consider what the Kotlin compiler generates under the hood (Java synthetic classes) and how inlining impacts binary DEX size.",
        "principalAnswer": "A standard higher-order function compiles each lambda argument into an anonymous class instance implementing kotlin.jvm.functions.FunctionN (e.g., new Function0() { public Object invoke() { ... } }). In hot paths, this allocates heap memory and causes virtual method dispatch. When marked 'inline', the compiler copies the actual bytecode instructions of both the function and lambda directly into the call site, eliminating heap allocation completely.\n\nHowever, inlining hurts performance when applied to large function bodies called from dozens or hundreds of locations. This causes binary bloat (expanded DEX size), increases the application's method count, pollutes the instruction cache (I-cache), and slows down compilation. Inlining should strictly be reserved for small functions taking lambda arguments in hot paths.",
        "keyPoints": [
          "FunctionN anonymous class instantiation",
          "Virtual method dispatch vs direct instruction inlining",
          "Zero heap allocation in hot paths",
          "DEX method bloat / instruction cache misses on large functions"
        ],
        "pitfalls": [
          "Claiming inline should be added to every function",
          "Not knowing that lambdas generate anonymous classes",
          "Forgetting the DEX size trade-off"
        ]
      },
      {
        "id": "q1-2",
        "question": "Explain 'crossinline' vs 'noinline'. Under what exact compiler error condition is 'crossinline' required?",
        "difficulty": "Lead / Staff",
        "thinkPrompt": "Think about non-local returns and thread execution boundaries. Why does the compiler reject a standard inlined lambda inside a Runnable?",
        "principalAnswer": "By default, an inlined lambda supports 'non-local return'\u2014calling 'return' inside the lambda exits not just the lambda, but the enclosing calling function. However, if the inlined function passes the lambda into an execution context that runs outside the current stack frame\u2014such as inside a Runnable, a local object expression, or a coroutine dispatcher\u2014a non-local return is physically impossible because the calling function's stack frame has already unmounted or belongs to another thread.\n\nThe Kotlin compiler detects this and raises an error: 'Can't inline 'block' here: it may contain non-local returns'. Marking the parameter 'crossinline' resolves this by strictly forbidding the caller from placing a non-local 'return' inside the lambda while still allowing the function body to be inlined.\n\n'noinline' is different: it completely opts a lambda out of inlining, keeping it as an instance of FunctionN so it can be stored in a variable, passed to a non-inlined function, or returned.",
        "keyPoints": [
          "Non-local return mechanics",
          "Stack frame unmounting / asynchronous thread boundaries",
          "crossinline forbids non-local return while keeping call-site inlining",
          "noinline retains concrete FunctionN instance for storage/passing"
        ],
        "pitfalls": [
          "Confusing crossinline with noinline",
          "Believing crossinline changes threading behavior (it only changes language return rules)"
        ]
      },
      {
        "id": "q1-3",
        "question": "How does LazyThreadSafetyMode.SYNCHRONIZED work internally, and when should you choose PUBLICATION or NONE instead in Android?",
        "difficulty": "Senior",
        "thinkPrompt": "Consider double-checked locking, volatile memory barriers, and the thread context of UI vs Background.",
        "principalAnswer": "'lazy(LazyThreadSafetyMode.SYNCHRONIZED)' is the default. It uses double-checked locking with an internal synchronization monitor lock and a volatile backing field to guarantee that only one thread ever executes the initialization lambda, and all threads see the fully constructed instance.\n\n'LazyThreadSafetyMode.PUBLICATION' allows multiple threads to execute the initializer concurrently without blocking locks, but only the first thread that completes writes to the atomic reference; other results are discarded. Use this when the initializer is thread-safe, computationally cheap, and lock contention on a mutex is undesirable.\n\n'LazyThreadSafetyMode.NONE' performs zero thread synchronization and uses no locks. It is unsafe in multi-threaded contexts. In Android, you should explicitly use LazyThreadSafetyMode.NONE for properties accessed solely on the Main Thread (e.g. View binding references, formatters in Composable state holders, or Fragment-scoped UI helpers). This completely bypasses synchronization monitor overhead.",
        "keyPoints": [
          "SYNCHRONIZED uses double-checked locking & volatile barrier",
          "PUBLICATION uses compare-and-set atomic publication",
          "NONE removes all synchronization overhead for UI/MainThread-bound single thread contexts"
        ],
        "pitfalls": [
          "Assuming lazy is always completely free of overhead",
          "Not knowing how to optimize lazy properties on the main thread with mode NONE"
        ]
      }
    ]
  },
  {
    "id": "topic-2",
    "num": "02",
    "title": "Android Component Lifecycles & Process Death",
    "icon": "\ud83d\udcf1",
    "badge": "Lifecycle",
    "desc": "Master Activity & Fragment lifecycles, viewLifecycleOwner, OS process death restoration, SavedStateHandle, PendingIntent security flags, and ContentProviders.",
    "subtopics": [
      {
        "title": "Activity & Fragment Lifecycle Deep-Dive & viewLifecycleOwner",
        "what": "Activity has 7 lifecycle states (onCreate -> onStart -> onResume -> onPause -> onStop -> onDestroy -> onRestart). Fragments have a separate View lifecycle that is destroyed and recreated independently of the Fragment instance itself when navigating backstacks in FragmentManager.",
        "why": "Using Fragment's 'this' as the LifecycleOwner for LiveData or Flow collection leaks views. When a Fragment moves to the backstack, its View is destroyed (onDestroyView), but the Fragment instance lives on. Observers registered with 'this' continue referencing detached views, leaking Bitmaps, ViewBindings, and causing crashes upon re-entry.",
        "how": "Always use 'viewLifecycleOwner' or 'viewLifecycleOwner.lifecycleScope' when observing state in Fragments. Clean up ViewBinding backing properties in onDestroyView() by setting '_binding = null'. In Activity, coordinate heavy resource releases in onStop() (when UI is no longer visible) rather than onPause().",
        "code": "// Correct Leak-Free Fragment Pattern\nclass TransferConfirmationFragment : Fragment(R.layout.fragment_transfer) {\n    private var _binding: FragmentTransferBinding? = null\n    private val binding get() = _binding!! // Safe non-null accessor\n\n    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {\n        super.onViewCreated(view, savedInstanceState)\n        _binding = FragmentTransferBinding.bind(view)\n\n        // CRITICAL: Bind observer to viewLifecycleOwner, NEVER 'this'\n        viewLifecycleOwner.lifecycleScope.launch {\n            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {\n                viewModel.transferState.collect { state ->\n                    renderState(state)\n                }\n            }\n        }\n    }\n\n    override fun onDestroyView() {\n        super.onDestroyView()\n        _binding = null // Essential: Prevents memory leak when Fragment placed in backstack\n    }\n}",
        "realworld": "In large Banking and E-commerce checkout funnels with multi-step Fragment backstacks, neglecting to nullify ViewBinding or observing with 'this' retains heavy View hierarchies and user card data in memory, triggering Low Memory Killer (LMK) events on lower-end devices."
      },
      {
        "title": "Configuration Change vs OS Process Death (The State Survival Matrix)",
        "what": "Configuration changes (screen rotation, fold/unfold, dark mode, locale change) tear down and recreate the Activity instance, but the Application process remains alive. OS Process Death occurs when Android kills a backgrounded app process to reclaim memory for foreground tasks. The user later returns via Recents, and the OS recreates the task stack.",
        "why": "ViewModels survive configuration changes because they are stored in the Activity's ViewModelStore (retained via NonConfigurationInstances). However, ViewModels DO NOT survive process death. Relying solely on ViewModel memory state causes 'NullPointerException' or user form loss upon process recreation.",
        "how": "Use the State Survival Hierarchy: (1) ViewModel in-memory state for runtime data; (2) 'SavedStateHandle' (backed by Bundle) for critical IDs and user inputs that must survive process death (< 1MB limit); (3) Room/DataStore for persistent offline data.",
        "code": "// Process-Death Resilient Banking ViewModel\n@HiltViewModel\nclass SendMoneyViewModel @Inject constructor(\n    private val savedStateHandle: SavedStateHandle, // Automatically restored after process death\n    private val transferRepo: TransferRepository\n) : ViewModel() {\n\n    // Backed by SavedStateHandle Bundle: survives BOTH rotation AND process death\n    val recipientIban: StateFlow<String> = savedStateHandle.getStateFlow(KEY_IBAN, \"\")\n    val transferAmount: StateFlow<Double> = savedStateHandle.getStateFlow(KEY_AMOUNT, 0.0)\n\n    fun onIbanChanged(newIban: String) {\n        savedStateHandle[KEY_IBAN] = newIban\n    }\n\n    fun onAmountChanged(amount: Double) {\n        savedStateHandle[KEY_AMOUNT] = amount\n    }\n\n    companion object {\n        private const val KEY_IBAN = \"saved_recipient_iban\"\n        private const val KEY_AMOUNT = \"saved_transfer_amount\"\n    }\n}",
        "realworld": "In digital banking wire transfers, a user enters account and amount details, switches to an SMS app to check an OTP, and the OS kills the banking app due to low RAM. When returning, SavedStateHandle restores the exact wizard step and transfer fields seamlessly."
      },
      {
        "title": "PendingIntent Security & Android 12+ Mutability Requirements",
        "what": "A PendingIntent is a token handed to another app (like NotificationManager, AlarmManager, or external widgets) granting that external process the permission to execute an Intent with your app's identity and privileges. Starting in Android 12 (API 31), every PendingIntent must explicitly specify FLAG_IMMUTABLE or FLAG_MUTABLE.",
        "why": "Unspecified or mutable PendingIntents are a major security vulnerability (Intent Redirection / Injection). A malicious app can intercept a mutable PendingIntent and overwrite its internal extras, URI, or target component, gaining unauthorized access to privileged exported components.",
        "how": "Always use 'PendingIntent.FLAG_IMMUTABLE' by default. Only use 'FLAG_MUTABLE' when the receiving system genuinely needs to fill in intent arguments (such as Notification Direct Reply or inline action responses).",
        "code": "// Secure Immutable PendingIntent for Push Notification\nval intent = Intent(context, TransactionDetailActivity::class.java).apply {\n    putExtra(EXTRA_TXN_ID, transactionId)\n    flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP\n}\n\nval flags = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {\n    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE\n} else {\n    PendingIntent.FLAG_UPDATE_CURRENT\n}\n\nval pendingIntent = PendingIntent.getActivity(context, REQUEST_CODE, intent, flags)",
        "realworld": "Financial apps handling payment transaction alerts must enforce FLAG_IMMUTABLE on notification actions to ensure third-party malware on rooted or compromised devices cannot tamper with target payment IDs."
      }
    ],
    "quizQuestions": [
      {
        "id": "q2-1",
        "question": "What is the difference between Configuration Change and OS Process Death? How do you test OS Process Death deterministically on a test device?",
        "difficulty": "Senior",
        "thinkPrompt": "Think about ViewModelStore retention vs savedInstanceState Bundle serialization. How do you kill an app via ADB while preserving its backstack state?",
        "principalAnswer": "During a configuration change (e.g. rotation), the Activity is destroyed and recreated, but the OS process remains alive. The Activity's 'ViewModelStore' is saved via 'NonConfigurationInstances' and restored to the new Activity, preserving all in-memory ViewModel StateFlows.\n\nDuring OS Process Death (low memory kill), Android forcibly terminates the entire Linux process hosting the app while it sits in the background. The ViewModel, static singletons, and in-memory caches are completely wiped. Only data written to the 'savedInstanceState' Bundle (or SavedStateHandle) and persistent storage (Room/Disk) survives. When the user taps the app in Recents, Android creates a brand new process and restores the Activity backstack using the saved Bundle.\n\nTo test this deterministically:\n1. Open the target screen and enter data.\n2. Press Home to put the app in the background (forcing onSaveInstanceState).\n3. In terminal execute: 'adb shell am kill <package_name>'.\n4. Tap the app icon or return via Recents. If the app crashes with NullPointerException or loses form inputs, process death handling is broken.",
        "keyPoints": [
          "ViewModelStore survives rotation via NonConfigurationInstances",
          "Process death wipes all memory/ViewModels",
          "SavedStateHandle is backed by savedInstanceState Bundle",
          "Testing via: adb shell am kill <package_name> after backgrounding"
        ],
        "pitfalls": [
          "Thinking ViewModels survive process death",
          "Testing by pressing the Red Stop button in Android Studio (which kills the task without saving state)"
        ]
      },
      {
        "id": "q2-2",
        "question": "Why does observing LiveData or StateFlow with 'viewLifecycleOwner' prevent memory leaks in Fragments compared to passing 'this'?",
        "difficulty": "Senior",
        "thinkPrompt": "Consider Fragment lifecycle vs View lifecycle when transactions are added to the FragmentManager backstack.",
        "principalAnswer": "In Fragments, the View lifecycle and Fragment lifecycle are decoupled. When a Fragment transaction replaces Fragment A with Fragment B and adds A to the backstack, Fragment A's View is destroyed via 'onDestroyView()', but Fragment A's Java/Kotlin instance remains alive in the backstack.\n\nIf you observe LiveData or Flow passing 'this' (the Fragment instance), the observer registration remains tied to the Fragment's lifetime. Each time Fragment A is restored from the backstack, 'onViewCreated()' executes again, registering a duplicate observer. The old observers still reference the destroyed View's widgets, creating substantial memory leaks and causing duplicate emissions. Using 'viewLifecycleOwner' ensures the observer is automatically unregistered as soon as 'onDestroyView()' fires.",
        "keyPoints": [
          "Decoupled View lifecycle vs Fragment instance lifecycle",
          "FragmentManager backstack preserves Fragment instance while destroying View",
          "Passing 'this' creates duplicate observers and holds references to detached Views",
          "viewLifecycleOwner unregisters exactly at onDestroyView"
        ],
        "pitfalls": [
          "Assuming Fragment onDestroy and onDestroyView always fire together",
          "Not nullifying ViewBinding in onDestroyView"
        ]
      }
    ]
  },
  {
    "id": "topic-3",
    "num": "03",
    "title": "Android Services & Background Work",
    "icon": "\u2699\ufe0f",
    "badge": "Services",
    "desc": "Master Started, Bound, and Foreground Services, Android 14 foregroundServiceType requirements, WorkManager chaining and constraints, and Doze mode policies.",
    "subtopics": [
      {
        "title": "Service Types & Android 14 Foreground Service Types",
        "what": "Android Services run on the Main Thread by default unless explicitly offloaded. Three types exist: Started (startService), Bound (bindService via Binder/AIDL), and Foreground Services (show a persistent user notification). Starting in Android 14 (API 34), apps MUST specify an explicit 'android:foregroundServiceType' in the manifest and request corresponding runtime permissions.",
        "why": "Starting background services from the background was restricted in Android 8.0 (Oreo) to eliminate battery-draining background operations. Foreground services guarantee process priority (preventing LMK kills) by informing the user that persistent work (e.g. navigation, media, audio recording, data sync) is ongoing.",
        "how": "Declare 'android:foregroundServiceType' in the AndroidManifest. Call 'startForeground(NOTIFICATION_ID, notification)' within 5 seconds of 'startForegroundService()' to avoid an ANR/ForegroundServiceDidNotStartInTimeException.",
        "code": "// Android 14 Compliant Manifest Declaration\n<!-- AndroidManifest.xml -->\n<service\n    android:name=\".upload.DocumentUploadService\"\n    android:foregroundServiceType=\"dataSync\"\n    android:exported=\"false\" />\n<uses-permission android:name=\"android.permission.FOREGROUND_SERVICE\" />\n<uses-permission android:name=\"android.permission.FOREGROUND_SERVICE_DATA_SYNC\" />\n\n// Service Implementation with Notification\nclass DocumentUploadService : Service() {\n    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {\n        val notification = createPersistentNotification(\"Uploading medical records...\")\n        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {\n            ServiceCompat.startForeground(\n                this,\n                NOTIFICATION_ID,\n                notification,\n                ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC\n            )\n        } else {\n            startForeground(NOTIFICATION_ID, notification)\n        }\n\n        serviceScope.launch(Dispatchers.IO) {\n            performUpload()\n            stopSelf(startId) // Always stop with startId to avoid stopping newer invocations\n        }\n        return START_NOT_STICKY\n    }\n}",
        "realworld": "In Healthcare and Banking apps, uploading large multi-megabyte encrypted documents (diagnostic scans, KYC proof-of-address PDFs) requires a Foreground Service of type 'dataSync' so the transfer completes even if the user switches to other apps."
      },
      {
        "title": "WorkManager: Constraints, Chaining & CoroutineWorker",
        "what": "WorkManager is the Google-recommended solution for persistent, deferrable background work. It guarantees execution even if the app process is killed or the device is rebooted. It uses CoroutineWorker to execute suspend functions safely.",
        "why": "Raw Coroutines die when the app process is killed. JobScheduler is API-level dependent. AlarmManager is designed for exact alarms, not deferrable background work. WorkManager automatically selects the best underlying mechanism (JobScheduler on API 23+, AlarmManager + BroadcastReceiver on legacy) while enforcing hardware constraints (Unmetered Network, Charging, Battery Not Low).",
        "how": "Subclass 'CoroutineWorker' and implement 'doWork()'. Enforce constraints with 'Constraints.Builder()', chain tasks using 'WorkManager.getInstance(context).beginWith().then()', and handle periodic work with 'PeriodicWorkRequestBuilder'.",
        "code": "// Robust Offline Data Sync Chain with Constraints\nclass EncryptedSyncWorker(\n    appContext: Context,\n    workerParams: WorkerParameters\n) : CoroutineWorker(appContext, workerParams) {\n\n    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {\n        return@withContext try {\n            val syncRepository = EntryPointAccessors.fromApplication(\n                applicationContext, WorkerEntryPoint::class.java\n            ).syncRepository()\n\n            syncRepository.uploadPendingTransactions()\n            Result.success()\n        } catch (e: IOException) {\n            // Transient error: retry with exponential backoff\n            Result.retry()\n        } catch (e: Exception) {\n            Result.failure()\n        }\n    }\n}\n\n// WorkManager Chaining Pipeline\nval constraints = Constraints.Builder()\n    .setRequiredNetworkType(NetworkType.UNMETERED)\n    .setRequiresBatteryNotLow(true)\n    .build()\n\nval compressWork = OneTimeWorkRequestBuilder<CompressWorker>().build()\nval encryptWork = OneTimeWorkRequestBuilder<EncryptWorker>().build()\nval uploadWork = OneTimeWorkRequestBuilder<EncryptedSyncWorker>()\n    .setConstraints(constraints)\n    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.SECONDS)\n    .build()\n\nWorkManager.getInstance(context)\n    .beginUniqueWork(\"ledger_sync\", ExistingWorkPolicy.KEEP, compressWork)\n    .then(encryptWork)\n    .then(uploadWork)\n    .enqueue()",
        "realworld": "In E-commerce and FinTech apps with offline shopping carts or pending offline transfers, WorkManager guarantees that the encrypted transaction queue is uploaded as soon as an unmetered Wi-Fi connection is restored."
      }
    ],
    "quizQuestions": [
      {
        "id": "q3-1",
        "question": "WorkManager vs JobScheduler vs AlarmManager vs Foreground Service: Give the exact architectural decision matrix for when to use each.",
        "difficulty": "Senior",
        "thinkPrompt": "Consider exactness of timing (exact alarms), deferrability, user awareness (notifications), and persistence across reboots.",
        "principalAnswer": "1. WorkManager: Use for DEFERRABLE, PERSISTENT work where execution is guaranteed even if the app process is killed or the device reboots. Supports constraints (network, charging, idle) and exponential backoff. Examples: uploading offline analytics, syncing a local Room database with a remote ledger.\n\n2. Foreground Service: Use for NON-DEFERRABLE, IMMEDIATE tasks that require user awareness through an ongoing persistent notification. Use when the user actively initiates work that must continue while backgrounded. Examples: turn-by-turn navigation, media playback, active voice/video call.\n\n3. AlarmManager: Use STRICTLY for EXACT, TIME-SENSITIVE triggers at an exact wall-clock millisecond. Not for general work. Examples: an alarm clock firing at 07:00 AM, calendar event reminders. (Often wakes the device and then schedules work).\n\n4. JobScheduler: Android framework API (API 21+). You should generally NOT use JobScheduler directly anymore; WorkManager wraps JobScheduler on modern devices while adding backward compatibility, SQLite persistence, and coroutine support.",
        "keyPoints": [
          "WorkManager: deferrable + guaranteed persistent",
          "Foreground Service: immediate + user-visible ongoing notification",
          "AlarmManager: exact wall-clock triggers (alarm clocks, calendar)",
          "Avoid using JobScheduler directly; rely on WorkManager"
        ],
        "pitfalls": [
          "Using AlarmManager for background syncing",
          "Using raw Coroutines in ViewModel for background work that must survive process kill"
        ]
      }
    ]
  },
  {
    "id": "topic-4",
    "num": "04",
    "title": "Jetpack Compose Deep-Dive & Internals",
    "icon": "\ud83c\udfa8",
    "badge": "Compose",
    "desc": "Master the Compose compiler & runtime, stability system (@Immutable/@Stable), recomposition optimization, SideEffects, derivedStateOf, and CompositionLocal.",
    "subtopics": [
      {
        "title": "Compose Recomposition Engine & Stability Rules",
        "what": "Recomposition is the process where the Compose runtime re-executes composable functions when their state reads change. The Compose compiler plugin analyzes function parameters at build time and classifies them as Stable or Unstable. A composable function is 'skippable' if all of its parameters are stable.",
        "why": "If an unstable type (such as standard java.util.List, any class with 'var' properties, or an external third-party DTO) is passed into a Composable, the Compose runtime CANNOT guarantee immutability. As a result, it refuses to skip the composable, forcing full recomposition of that subtree even if the data did not change\u2014leading to frame drops.",
        "how": "Mark domain models with '@Immutable' or '@Stable'. Replace standard 'List<T>' with 'ImmutableList<T>' from kotlinx-collections-immutable. Configure Compose compiler metrics/reports via Gradle to audit unstable classes in your build.",
        "code": "// \u274c UNSTABLE: List is an interface, Compose cannot verify immutability\ndata class AccountDashboardState(\n    val accounts: List<Account>, // Causes AccountList to re-evaluate on every recomposition\n    val totalBalance: Double\n)\n\n// \u2705 STABLE: Guarantees skipping optimization\n@Immutable\ndata class AccountDashboardUiState(\n    val accounts: ImmutableList<Account>, // Fully stable!\n    val totalBalance: Double\n)\n\n@Composable\nfun AccountList(\n    accounts: ImmutableList<Account>,\n    onAccountClick: (String) -> Unit, // Stable lambda reference\n    modifier: Modifier = Modifier\n) {\n    LazyColumn(modifier = modifier) {\n        items(\n            items = accounts,\n            key = { account -> account.id }, // Stable identity prevents item rebuild on reorder\n            contentType = { \"account_row\" }  // Enables item slot recycling\n        ) { account ->\n            AccountRow(account = account, onClick = onAccountClick)\n        }\n    }\n}",
        "realworld": "In high-frequency real-time banking tickers or crypto trading screens updating balances multiple times per second, stable state models and key() bindings prevent the entire screen from recomposing, reducing CPU consumption and battery drain by up to 65%."
      },
      {
        "title": "derivedStateOf vs remember(key)",
        "what": "'remember(key) { ... }' recomputes its calculation whenever 'key' changes. 'derivedStateOf { ... }' creates an observable state object that only notifies consumers when its RESULT value actually changes, regardless of how frequently the underlying state dependencies change.",
        "why": "Reading rapid-fire state changes (like LazyListState.firstVisibleItemIndex changing on every pixel scroll) inside a Composable triggers recomposition on EVERY pixel moved. 'derivedStateOf' acts as a high-frequency dampener.",
        "how": "Use 'derivedStateOf' when an input state changes frequently, but your UI only cares about a derived boolean or threshold value. Use 'remember(key)' when you want to cache a calculation based on identity changes.",
        "code": "// High-Frequency Scroll Optimization in Compose\nval listState = rememberLazyListState()\n\n// \u274c BAD: Recomposes on every single scroll pixel!\n// val showScrollToTop = listState.firstVisibleItemIndex > 0\n\n// \u2705 GOOD: Derived state dampener: ONLY emits when boolean flips (true <-> false)\nval showScrollToTop by remember {\n    derivedStateOf { listState.firstVisibleItemIndex > 0 }\n}\n\nAnimatedVisibility(visible = showScrollToTop) {\n    ScrollToTopFloatingActionButton(onClick = { scope.launch { listState.animateScrollToItem(0) } })\n}",
        "realworld": "In large transaction lists or e-commerce feeds, using derivedStateOf for sticky headers, scroll-to-top FABs, or collapsible top app bars ensures the scroll gesture remains smooth at 120Hz."
      },
      {
        "title": "SideEffects Lifecycle Decision Tree",
        "what": "SideEffects are escape hatches used to execute operations that interact with state outside the Composable tree: LaunchedEffect, rememberCoroutineScope, DisposableEffect, SideEffect, and produceState.",
        "why": "Executing side-effects directly inside the body of a Composable is hazardous because Composables can execute on any thread, execute out of order, or be cancelled and discarded mid-frame without warning.",
        "how": "Follow the decision tree: (1) Async work driven by COMPOSITION / key change -> 'LaunchedEffect(key)'; (2) Async work driven by USER EVENT (button click) -> 'rememberCoroutineScope()'; (3) Setup/teardown with cleanup (sensors, broadcast receivers, camera) -> 'DisposableEffect(key)'; (4) Sync Compose state to non-Compose object -> 'SideEffect'; (5) Bridge external callback into State -> 'produceState'.",
        "code": "// Complete SideEffect Architecture Example\n@Composable\nfun BiometricGateScreen(\n    onAuthenticated: () -> Unit,\n    viewModel: AuthViewModel = hiltViewModel()\n) {\n    val context = LocalContext.current\n    val coroutineScope = rememberCoroutineScope() // For user-triggered button click\n\n    // 1. DisposableEffect: Register & Clean up Biometric Callback safely\n    DisposableEffect(context) {\n        val biometricManager = BiometricManager.from(context)\n        val receiver = BiometricStatusReceiver()\n        context.registerReceiver(receiver, IntentFilter(\"ACTION_BIOMETRIC_CHANGED\"))\n\n        onDispose {\n            context.unregisterReceiver(receiver) // Guaranteed cleanup when leaving composition\n        }\n    }\n\n    // 2. LaunchedEffect: Key-driven trigger on error state\n    val errorState by viewModel.errorState.collectAsStateWithLifecycle()\n    LaunchedEffect(errorState) {\n        errorState?.let { err ->\n            showHapticFeedback(context)\n            snackbarHostState.showSnackbar(err.localizedMessage)\n        }\n    }\n\n    Button(onClick = {\n        // User action: Launch via rememberCoroutineScope\n        coroutineScope.launch {\n            viewModel.authenticateBiometrics()\n        }\n    }) {\n        Text(\"Authenticate\")\n    }\n}",
        "realworld": "In biometric verification flows, using DisposableEffect ensures that biometric listeners or camera barcode scanners are instantly released when the user tabs away, preventing hardware resource locks."
      }
    ],
    "quizQuestions": [
      {
        "id": "q4-1",
        "question": "What is the internal mechanism of Compose recomposition skipping? What bytecode does the Compose compiler generate for @Composable functions?",
        "difficulty": "Lead / Staff",
        "thinkPrompt": "Think about Composer, slot tables, groups, and the synthetic $changed bitmask generated at compile time.",
        "principalAnswer": "The Compose compiler plugin transforms every @Composable function by injecting a synthetic 'Composer' parameter and a '$changed' integer bitmask parameter.\n\nAt runtime, the Composer maintains a hierarchical in-memory data structure called the 'Slot Table'. When entering a Composable, the function calls 'composer.startRestartGroup(key)'. The '$changed' bitmask carries flags indicating whether each argument has changed, is static, or needs runtime equality checking.\n\nIf all parameters are verified to be Stable and none of the bits in the bitmask indicate an input mutation (checked via 'composer.changed(param)'), and the Composer's internal invalidation flag is false, the runtime executes an early return ('composer.skipToGroupEnd()'), completely bypassing the execution of the function's body. If any parameter is unstable, skipping is disabled, and the entire function body re-executes.",
        "keyPoints": [
          "Composer injected into every composable",
          "Slot table memory structure",
          "$changed bitmask tracks parameter mutations",
          "Stable types allow early skipToGroupEnd()",
          "Unstable types disable skipping optimization"
        ],
        "pitfalls": [
          "Thinking Compose uses Android View tree invalidation",
          "Not knowing about the Slot Table or Composer"
        ]
      }
    ]
  },
  {
    "id": "topic-5",
    "num": "05",
    "title": "Jetpack Architecture (ViewModel, Room, StateFlow, Paging)",
    "icon": "\ud83c\udfdb\ufe0f",
    "badge": "Architecture",
    "desc": "Master ViewModelStore internals, StateFlow vs SharedFlow vs Channels, Room multi-table migrations, DataStore encryption, and Paging 3 RemoteMediator.",
    "subtopics": [
      {
        "title": "StateFlow vs SharedFlow vs LiveData vs Channels Comparison",
        "what": "StateFlow is a hot state-holder with replay=1 that conflates duplicate values (using equals()). SharedFlow is a hot event-emitter with configurable replay and buffer capacities. LiveData is an older lifecycle-aware observable tightly coupled to Android MainThread. Channels are hot coroutine queues designed for point-to-point single-consumer execution.",
        "why": "Using StateFlow for one-time events (like showing a Snackbar or navigating) leads to the 're-emission on rotation' bug because StateFlow replays the latest value to new collectors. Conversely, using standard SharedFlow without buffering can drop one-time events if the collector is paused in the background.",
        "how": "Use 'StateFlow' for UI State representation ('What the screen IS'). Use 'Channel' (via receiveAsFlow()) or 'SharedFlow' with zero replay for one-time events ('What HAPPENED'). Use 'repeatOnLifecycle(STARTED)' or 'collectAsStateWithLifecycle()' to collect safely.",
        "code": "// Production MVI State & Event Architecture\n@HiltViewModel\nclass PaymentViewModel @Inject constructor(\n    private val processPaymentUseCase: ProcessPaymentUseCase\n) : ViewModel() {\n\n    // 1. STATE: StateFlow for durable UI rendering (replays on rotation)\n    private val _uiState = MutableStateFlow<PaymentUiState>(PaymentUiState.Idle)\n    val uiState: StateFlow<PaymentUiState> = _uiState.asStateFlow()\n\n    // 2. EVENTS: Channel for one-shot side-effects (consumed exactly once)\n    private val _effectChannel = Channel<PaymentEffect>(Channel.BUFFERED)\n    val effects: Flow<PaymentEffect> = _effectChannel.receiveAsFlow()\n\n    fun submitPayment(amount: Double) {\n        viewModelScope.launch {\n            // update{} CAS ensures atomic thread-safe state transition\n            _uiState.update { PaymentUiState.Processing }\n\n            processPaymentUseCase(amount)\n                .onSuccess { receiptId ->\n                    _uiState.update { PaymentUiState.Success(receiptId) }\n                    _effectChannel.send(PaymentEffect.NavigateToReceipt(receiptId))\n                }\n                .onFailure { error ->\n                    _uiState.update { PaymentUiState.Error(error.message) }\n                    _effectChannel.send(PaymentEffect.ShowToast(\"Payment failed: ${error.message}\"))\n                }\n        }\n    }\n}",
        "realworld": "In banking apps, when a user completes a money transfer and rotates the phone, a StateFlow holding an 'ApprovedDialog' state would trigger the dialog again unless reset. Modeling dialogs and navigation events as a Channel guarantees zero duplicate actions."
      },
      {
        "title": "Room Multi-Table Relational Schema & Safe Migrations",
        "what": "Room is an abstraction layer over SQLite. It maps Kotlin data classes to SQL tables (@Entity), models 1-to-1, 1-to-many (@Relation), and many-to-many (@Junction) relationships, and manages database schema upgrades via Migration objects.",
        "why": "Failing to handle database schema migrations properly in production leads to fatal 'IllegalStateException: Room cannot verify data integrity', causing instant crashes on app launch for all updating users. Using fallbackToDestructiveMigration() wipes out user data.",
        "how": "Always export schema ('exportSchema = true'). Write deterministic 'Migration(startVersion, endVersion)' classes with exact SQL statements. Validate every migration in your CI pipeline using 'MigrationTestHelper'.",
        "code": "// Production Room Entity with 1-to-Many Relationship\n@Entity(tableName = \"bank_accounts\")\ndata class AccountEntity(\n    @PrimaryKey val accountId: String,\n    val iban: String,\n    val currency: String,\n    val balance: Double\n)\n\n@Entity(\n    tableName = \"transactions\",\n    foreignKeys = [\n        ForeignKey(\n            entity = AccountEntity::class,\n            parentColumns = [\"accountId\"],\n            childColumns = [\"accountOwnerId\"],\n            onDelete = ForeignKey.CASCADE\n        )\n    ],\n    indices = [Index(value = [\"accountOwnerId\"]), Index(value = [\"timestamp\"])]\n)\ndata class TransactionEntity(\n    @PrimaryKey val txnId: String,\n    val accountOwnerId: String,\n    val amount: Double,\n    val timestamp: Long\n)\n\n// Deterministic Non-Destructive Migration\nval MIGRATION_2_3 = object : Migration(2, 3) {\n    override fun migrate(db: SupportSQLiteDatabase) {\n        // Add encrypted metadata column with default empty string\n        db.execSQL(\"ALTER TABLE transactions ADD COLUMN encrypted_tag TEXT NOT NULL DEFAULT ''\")\n        // Create an index for accelerated timestamp queries\n        db.execSQL(\"CREATE INDEX IF NOT EXISTS index_transactions_timestamp ON transactions(timestamp)\")\n    }\n}",
        "realworld": "In eHealth and Fintech applications, medical history and financial ledgers must persist for years across app upgrades. Automated unit tests with MigrationTestHelper guarantee zero data corruption across 10+ legacy version transitions."
      }
    ],
    "quizQuestions": [
      {
        "id": "q5-1",
        "question": "What happens if a Room database version is incremented from 4 to 5 without providing a Migration object, and fallbackToDestructiveMigration is NOT set?",
        "difficulty": "Senior",
        "thinkPrompt": "Consider Room's identity hash check against the room_master_table on database open.",
        "principalAnswer": "When Room opens the SQLite database, it inspects the internal 'room_master_table' and compares the stored identity hash against the hash generated by the compiled Room schema. If the database file has version 4, the Database annotation specifies version 5, and no matching Migration(4, 5) or transitive path exists, Room throws an 'IllegalStateException: A migration from 4 to 5 was required but not found'.\n\nIf fallbackToDestructiveMigration is not enabled, this exception is unhandled and crashes the app immediately on launch (P0 production incident). If fallbackToDestructiveMigration IS enabled, Room drops all existing tables and rebuilds an empty database, permanently destroying user data. The senior architectural solution is to write a manual Migration object, export the schema JSON, and write an instrumented test using MigrationTestHelper to verify schema parity before release.",
        "keyPoints": [
          "Room identity hash mismatch in room_master_table",
          "IllegalStateException crash on startup",
          "fallbackToDestructiveMigration wipes all tables",
          "MigrationTestHelper verifies schema transitions in CI"
        ],
        "pitfalls": [
          "Suggesting fallbackToDestructiveMigration as a production solution",
          "Not knowing where Room stores its schema identity hash"
        ]
      }
    ]
  },
  {
    "id": "topic-6",
    "num": "06",
    "title": "Networking & Third-Party Libraries (Retrofit, OkHttp, Coil)",
    "icon": "\ud83c\udf10",
    "badge": "Networking",
    "desc": "Master Retrofit 2 API architectures, OkHttp Authenticator mutex locking (preventing 401 refresh storms), offline caching, and Coil image decoding pipelines.",
    "subtopics": [
      {
        "title": "Thread-Safe 401 Token Refresh with OkHttp Authenticator & Mutex",
        "what": "When multiple concurrent network calls receive an HTTP 401 Unauthorized simultaneously, OkHttp's 'Authenticator' triggers. Without synchronization, all concurrent threads initiate duplicate token refresh requests, invalidating one another and logging the user out.",
        "why": "A banking dashboard loading 5 parallel endpoints (Balance, Transactions, Cards, Notifications, Offers) will encounter 5 simultaneous 401s if the token expired. Calling the refresh endpoint 5 times in parallel triggers race conditions and security rate limits.",
        "how": "Implement OkHttp's 'Authenticator'. Use a synchronized lock or Mutex. Check if another thread has ALREADY refreshed the token before making the network call. Update the failed request with the new Authorization header.",
        "code": "// Production-Grade Thread-Safe Token Refresh Authenticator\nclass TokenAuthenticator @Inject constructor(\n    private val tokenStorage: TokenStorage,\n    private val authApiProvider: Provider<AuthApiService> // Provider breaks circular dependency\n) : Authenticator {\n\n    private val lock = Any()\n\n    override fun authenticate(route: Route?, response: Response): Request? {\n        // Prevent infinite retry loop if refresh token itself failed\n        if (responseCount(response) >= 3) return null\n\n        val currentAccessToken = tokenStorage.getAccessToken()\n\n        synchronized(lock) {\n            val updatedAccessToken = tokenStorage.getAccessToken()\n\n            // If another thread already refreshed the token while this thread waited, use it!\n            val tokenToUse = if (updatedAccessToken != currentAccessToken && updatedAccessToken != null) {\n                updatedAccessToken\n            } else {\n                // Actually perform the synchronous refresh call\n                val refreshToken = tokenStorage.getRefreshToken() ?: return null\n                val refreshResponse = authApiProvider.get().refreshTokenDirect(refreshToken).execute()\n\n                if (refreshResponse.isSuccessful && refreshResponse.body() != null) {\n                    val newTokens = refreshResponse.body()!!\n                    tokenStorage.saveTokens(newTokens.accessToken, newTokens.refreshToken)\n                    newTokens.accessToken\n                } else {\n                    tokenStorage.clearTokens()\n                    EventBus.post(SessionExpiredEvent)\n                    return null\n                }\n            }\n\n            // Retry the failed original request with the fresh token\n            return response.request.newBuilder()\n                .header(\"Authorization\", \"Bearer $tokenToUse\")\n                .build()\n        }\n    }\n\n    private fun responseCount(response: Response): Int {\n        var count = 1\n        var prior = response.priorResponse\n        while (prior != null) {\n            count++\n            prior = prior.priorResponse\n        }\n        return count\n    }\n}",
        "realworld": "In all financial banking and payment apps, the synchronized Authenticator pattern is mandatory to prevent token invalidation races and session dropouts when users unlock their device after a token expiry window."
      },
      {
        "title": "Offline-First HTTP Caching with OkHttp Cache & Interceptors",
        "what": "OkHttp includes a disk Cache implementation that obeys HTTP cache-control headers. By combining an Application Interceptor and a Network Interceptor, you can enforce offline caching even if the server does not send proper cache-control headers.",
        "why": "Allows users with flaky subway connections to view previously fetched accounts, product catalogs, or medical summaries with zero network latency.",
        "how": "Set up a 50MB disk Cache in OkHttp.Builder(). In the offline interceptor, check network connectivity; if offline, add 'Cache-Control: public, only-if-cached, max-stale=...'. In the network interceptor, rewrite response cache headers.",
        "code": "// Offline Caching OkHttp Setup\nval cacheSize = 50L * 1024L * 1024L // 50 MB\nval httpCache = Cache(File(context.cacheDir, \"http_cache\"), cacheSize)\n\nval offlineCacheInterceptor = Interceptor { chain ->\n    var request = chain.request()\n    if (!networkMonitor.isOnline()) {\n        val maxStale = 60 * 60 * 24 * 7 // Tolerate 7-day stale cache when offline\n        request = request.newBuilder()\n            .header(\"Cache-Control\", \"public, only-if-cached, max-stale=$maxStale\")\n            .removeHeader(\"Pragma\")\n            .build()\n    }\n    chain.proceed(request)\n}\n\nval okHttpClient = OkHttpClient.Builder()\n    .cache(httpCache)\n    .addInterceptor(offlineCacheInterceptor)\n    .build()",
        "realworld": "In E-Commerce apps during flash sales, aggressive caching of static product catalogs reduces API gateway load by up to 70% while keeping catalog browsing instant for users."
      }
    ],
    "quizQuestions": [
      {
        "id": "q6-1",
        "question": "What is the difference between an Application Interceptor and a Network Interceptor in OkHttp? Where should authentication and caching headers be placed?",
        "difficulty": "Senior",
        "thinkPrompt": "Think about the interceptor execution pipeline relative to redirection, retries, and the HTTP cache layer.",
        "principalAnswer": "1. Application Interceptors (addInterceptor): Execute first and run once per call. They do not have access to intermediate responses (like 302 redirects or retry requests) and execute before OkHttp's internal Cache layer is checked. This is the ideal place for attaching global authentication headers, correlation request IDs, and injecting offline 'only-if-cached' flags.\n\n2. Network Interceptors (addNetworkInterceptor): Execute right before the request is dispatched to the network wire and after the Cache layer. They have full visibility into the raw network traffic (including TLS handshakes, redirects, and retries). If a request is served directly from the OkHttp Cache, the Network Interceptor is NEVER called! This is where you manipulate incoming response cache headers (e.g. rewriting Cache-Control headers from legacy backends) and monitor raw byte throughput.",
        "keyPoints": [
          "Application interceptors run once, outside Cache and redirects",
          "Network interceptors run per-wire-transmission, bypassed on cache hits",
          "Auth headers go in Application Interceptor",
          "Response Cache-Control rewriting goes in Network Interceptor"
        ],
        "pitfalls": [
          "Placing logging or caching rewrite in the wrong interceptor type",
          "Not knowing that Network Interceptors are skipped when served from cache"
        ]
      }
    ]
  },
  {
    "id": "topic-7",
    "num": "07",
    "title": "Dependency Injection (Hilt, Dagger 2, Koin)",
    "icon": "\ud83d\udc89",
    "badge": "DI",
    "desc": "Master Hilt component hierarchies, @Binds vs @Provides bytecode generation, multibindings for plugin architectures, and test isolation with @UninstallModules.",
    "subtopics": [
      {
        "title": "Hilt Component Hierarchy & Scoping Rules",
        "what": "Hilt provides predefined DI components tied to Android lifecycle stages: SingletonComponent (Application), ActivityRetainedComponent (survives rotation), ActivityComponent, ViewModelComponent, FragmentComponent, and ViewComponent.",
        "why": "Prevents memory leaks by strictly disallowing shorter-lived dependencies (e.g. Activity context) from being injected into longer-lived scopes (e.g. Singleton). The compiler validates the graph at build-time.",
        "how": "Inject @ApplicationContext into Singletons. Bind ViewModels to @ViewModelScoped or unscoped. Use @ActivityScoped only for objects that need an Activity Context (e.g. dialog builders or Navigator implementations).",
        "code": "// Hilt Component Binding Architecture\n@Module\n@InstallIn(SingletonComponent::class)\nabstract class RepositoryModule {\n\n    // @Binds is abstract and generates zero bytecode wrapper classes\n    @Binds\n    @Singleton\n    abstract fun bindAccountRepository(impl: AccountRepositoryImpl): AccountRepository\n}\n\n@Module\n@InstallIn(SingletonComponent::class)\nobject NetworkModule {\n\n    // @Provides is used when constructor logic is required\n    @Provides\n    @Singleton\n    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit =\n        Retrofit.Builder()\n            .baseUrl(\"https://api.bank.com\")\n            .client(okHttpClient)\n            .addConverterFactory(MoshiConverterFactory.create())\n            .build()\n}",
        "realworld": "In large modular Android apps, using @Binds instead of @Provides eliminates hundreds of generated Factory classes, shaving 15-25% off build times across multi-module projects."
      },
      {
        "title": "Multibindings (@IntoMap, @IntoSet) for Strategy Patterns",
        "what": "Dagger Multibindings allow you to inject a collection (Set or Map) of implementations without hardcoding them in the consumer. Modules contribute bindings into a central map using a custom @MapKey.",
        "why": "Enforces the Open/Closed Principle (OCP). You can add new payment methods, analytics providers, or FHIR handlers in independent Gradle modules without touching the central processor class.",
        "how": "Define a custom @MapKey annotation. Bind implementations using '@IntoMap' and the key annotation. Inject 'Map<PaymentType, Provider<PaymentStrategy>>' into the consumer.",
        "code": "// Strategy Pattern via Dagger Multibindings\nenum class PaymentType { CREDIT_CARD, UPI, CRYPTO }\n\n@MapKey\nannotation class PaymentTypeKey(val value: PaymentType)\n\n@Module\n@InstallIn(SingletonComponent::class)\nabstract class PaymentStrategiesModule {\n    @Binds\n    @IntoMap\n    @PaymentTypeKey(PaymentType.CREDIT_CARD)\n    abstract fun bindCardStrategy(impl: CardPaymentStrategy): PaymentStrategy\n\n    @Binds\n    @IntoMap\n    @PaymentTypeKey(PaymentType.UPI)\n    abstract fun bindUpiStrategy(impl: UpiPaymentStrategy): PaymentStrategy\n}\n\n// Consuming Processor: Zero when/switch statements needed!\n@Singleton\nclass PaymentProcessor @Inject constructor(\n    private val strategies: Map<PaymentType, @JvmSuppressWildcards Provider<PaymentStrategy>>\n) {\n    fun process(type: PaymentType, amount: Double) {\n        val strategy = strategies[type]?.get()\n            ?: throw UnsupportedOperationException(\"Unsupported payment type\")\n        strategy.pay(amount)\n    }\n}",
        "realworld": "In e-commerce apps with 10+ payment methods across different regional markets, multibindings allow feature teams to register new payment SDKs without touching the core checkout module."
      }
    ],
    "quizQuestions": [
      {
        "id": "q7-1",
        "question": "What is the technical difference between @Binds and @Provides in Dagger/Hilt? Which one should you prefer and why?",
        "difficulty": "Senior",
        "thinkPrompt": "Think about annotation processor code generation and delegate factory creation.",
        "principalAnswer": "1. '@Provides' methods are concrete methods in a Dagger module where you write the instantiation code manually. For every @Provides method, the annotation processor generates a corresponding Factory class (e.g. 'NetworkModule_ProvideRetrofitFactory') that contains the code to call your method. This increases generated class count and compilation time.\n\n2. '@Binds' methods are abstract methods that take a concrete implementation as a parameter and return the interface type. They contain no method body. Dagger does NOT generate a separate factory class for @Binds; instead, it directly references the concrete class's '@Inject constructor' factory and casts it to the interface type in the dependency graph.\n\nYou should ALWAYS prefer '@Binds' whenever you are binding an implementation class with an @Inject constructor to an interface. Only use '@Provides' when instantiating third-party classes (Retrofit, Room, OkHttp) where you cannot add an @Inject constructor, or when construction requires complex builder logic.",
        "keyPoints": [
          "@Provides generates a separate Factory class",
          "@Binds is abstract and generates zero wrapper code",
          "@Binds points directly to the @Inject constructor",
          "Prefer @Binds for compile-time efficiency"
        ],
        "pitfalls": [
          "Using @Provides for simple interface-to-implementation mapping",
          "Not knowing that @Binds modules must be abstract classes or interfaces"
        ]
      }
    ]
  },
  {
    "id": "topic-8",
    "num": "08",
    "title": "Architecture & Design Patterns (Clean Architecture, MVI)",
    "icon": "\ud83d\udcd0",
    "badge": "Clean Arch",
    "desc": "Master Clean Architecture layer boundaries, Domain purity, MVI state machines, the :api/:impl multi-module pattern, and the Strangler Fig migration strategy.",
    "subtopics": [
      {
        "title": "Clean Architecture Layer Boundaries & Inward Dependency Rule",
        "what": "Clean Architecture structures the codebase into concentric layers: Presentation (UI, Composables, ViewModels), Domain (UseCases, Pure Business Entities), and Data (Repositories, Room DAOs, Retrofit API DTOs). Dependencies strictly point inward toward Domain.",
        "why": "Domain contains the core business rules that define your business. It must have ZERO dependencies on Android framework classes (android.content.Context, androidx.lifecycle, Room annotations). This guarantees that business logic can be tested with lightning-fast JVM unit tests without emulators and survives framework deprecations.",
        "how": "Define repository interfaces in Domain; implement them in Data. Data DTOs (Retrofit/Room models) must NEVER leak into Domain or Presentation; map them at the repository boundary into immutable Domain entities.",
        "code": "// Pure Domain Layer (Zero Android Framework Imports)\npackage com.bank.domain.model\n\ndata class Account(\n    val id: String,\n    val balance: Double,\n    val currency: String\n) {\n    // Business rules belong in Domain Entities!\n    fun canWithdraw(amount: Double): Boolean = balance >= amount && amount > 0.0\n}\n\ninterface AccountRepository {\n    suspend fun getAccount(id: String): Result<Account>\n}\n\nclass TransferFundsUseCase @Inject constructor(\n    private val repo: AccountRepository,\n    private val auditLogger: DomainAuditLogger\n) {\n    suspend operator fun invoke(fromId: String, amount: Double): Result<Unit> {\n        val account = repo.getAccount(fromId).getOrElse { return Result.failure(it) }\n        if (!account.canWithdraw(amount)) {\n            return Result.failure(InsufficientFundsException())\n        }\n        return repo.executeTransfer(fromId, amount)\n    }\n}",
        "realworld": "In banking and medical apps with multi-year lifecycles, isolating domain business logic guarantees that migrating from XML to Compose, or from Retrofit to Ktor, requires zero changes to core business use cases."
      },
      {
        "title": "The :api / :impl Multi-Module Scaling Architecture",
        "what": "In large enterprise apps, feature modules are split into two Gradle subprojects: ':feature:X:api' (public interface, navigation contracts, and shared domain models) and ':feature:X:impl' (private ViewModels, Composables, and internal repositories).",
        "why": "Prevents circular dependencies between features and prevents 'Feature Team A breaks Feature Team B'. Other features depend ONLY on ':api'. Changes inside ':impl' trigger incremental compilation for THAT module only, rather than recompiling the entire app.",
        "how": "Feature Y adds 'implementation(project(\":feature:X:api\"))' in build.gradle.kts. Only the ':app' module depends on ':feature:X:impl' to wire Dagger/Hilt bindings together.",
        "code": "// :feature:payments:api (Public Contract)\ninterface PaymentsNavigator {\n    fun openPaymentConfirmation(amount: Double, recipientId: String)\n}\n\n// :feature:payments:impl (Private Implementation)\nclass PaymentsNavigatorImpl @Inject constructor(\n    private val navController: NavController\n) : PaymentsNavigator {\n    override fun openPaymentConfirmation(amount: Double, recipientId: String) {\n        navController.navigate(\"payment_confirm/$amount/$recipientId\")\n    }\n}\n\n// build.gradle.kts of :feature:accounts:impl\ndependencies {\n    implementation(project(\":feature:payments:api\")) // \u2705 ONLY depends on API\n    // implementation(project(\":feature:payments:impl\")) // \u274c STRICTLY FORBIDDEN\n}",
        "realworld": "In apps with 30+ engineers and 15+ modules, the :api/:impl split reduces full rebuild times from 8 minutes down to 45 seconds on feature code iterations."
      }
    ],
    "quizQuestions": [
      {
        "id": "q8-1",
        "question": "How do you navigate between two independent feature modules in a multi-module app without creating circular Gradle dependencies?",
        "difficulty": "Lead / Staff",
        "thinkPrompt": "Think about navigation contracts, interface inversion, and how the :app module wires them.",
        "principalAnswer": "Circular Gradle dependencies (e.g. Feature A depends on Feature B, and Feature B depends on Feature A) cause immediate build failures. To navigate between them cleanly:\n\n1. Use Navigation Contracts in :api modules: Feature B exposes a 'FeatureBNavigator' interface in ':feature:b:api'. Feature A depends only on ':feature:b:api' and calls 'navigator.navigateToFeatureB()'.\n2. Inversion of Control: The concrete implementation of 'FeatureBNavigator' resides in ':feature:b:impl' or ':app'. The ':app' root module, which has visibility into all implementation modules, binds the concrete navigator to the interface via Hilt/Dagger.\n3. Deep Linking: Alternatively, use Uri-based Deep Links (e.g. 'bank://payments/transfer?id=123'). Feature A launches an intent or NavController destination via Uri without having any compile-time dependency on Feature B's code.",
        "keyPoints": [
          ":api contract extraction to decouple compile dependencies",
          "Inversion of control via Hilt in the :app module",
          "Uri-based Deep Linking across module boundaries",
          "Zero direct :impl to :impl dependencies"
        ],
        "pitfalls": [
          "Creating circular dependencies in Gradle",
          "Using reflection to start activities by string name"
        ]
      }
    ]
  },
  {
    "id": "topic-9",
    "num": "09",
    "title": "Concurrency: Coroutines, Flow & Structured Concurrency",
    "icon": "\u26a1",
    "badge": "Coroutines",
    "desc": "Master CoroutineContext, coroutineScope vs supervisorScope, exception propagation, Flow backpressure, repeatOnLifecycle, and Turbine unit testing.",
    "subtopics": [
      {
        "title": "Structured Concurrency: coroutineScope vs supervisorScope",
        "what": "Structured concurrency guarantees that child coroutines are scoped to their parent hierarchy. In 'coroutineScope', if ANY child fails with an unhandled exception, the entire scope immediately cancels all remaining sibling coroutines and propagates the failure upward. In 'supervisorScope', a child failure is isolated; sibling coroutines continue executing undisturbed.",
        "why": "In a dashboard fetching Balance, Transactions, and Promotional Offers in parallel, you don't want the failure of an optional 'Offers' API to crash or cancel the critical 'Balance' or 'Transactions' coroutines. Using supervisorScope protects critical tasks from non-critical failures.",
        "how": "Use 'coroutineScope' when tasks are ATOMIC (all must succeed together or all must be rolled back, like multi-step checkout). Use 'supervisorScope' when tasks are INDEPENDENT (partial success is acceptable).",
        "code": "// Production Resilient Parallel Dashboard Loading\nsuspend fun fetchDashboardData(): DashboardResult = supervisorScope {\n    // 1. Critical Balance Call\n    val balanceDeferred = async { accountApi.getBalance() }\n    // 2. Critical Transactions Call\n    val txnsDeferred = async { accountApi.getTransactions() }\n    // 3. Optional Recommendations Call\n    val offersDeferred = async {\n        try {\n            recommendationsApi.getOffers()\n        } catch (e: Exception) {\n            Timber.w(e, \"Optional offers failed, returning fallback\")\n            emptyList<Offer>()\n        }\n    }\n\n    // Await all independent results safely\n    DashboardResult(\n        balance = balanceDeferred.await(),\n        transactions = txnsDeferred.await(),\n        offers = offersDeferred.await()\n    )\n}",
        "realworld": "In banking and e-commerce apps, using supervisorScope for home screen loading ensures that a 500 error from an advertisement service doesn't crash the user's primary account view."
      },
      {
        "title": "repeatOnLifecycle vs collectAsStateWithLifecycle",
        "what": "Flows collected in Android must respect the Activity/Fragment lifecycle. 'repeatOnLifecycle(Lifecycle.State.STARTED)' cancels the collecting coroutine when the lifecycle drops below STARTED (app backgrounded) and automatically restarts collection when it returns to STARTED. In Compose, 'collectAsStateWithLifecycle()' provides this exact behavior natively.",
        "why": "Collecting cold flows or continuous WebSocket streams while the app is in the background wastes device battery, consumes cellular bandwidth, and risks crashes from attempting to manipulate detached views.",
        "how": "Never use 'lifecycleScope.launch { flow.collect { ... } }' directly for UI collection. In Compose, always use 'flow.collectAsStateWithLifecycle()'. In Fragments, wrap collection inside 'viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED)'.",
        "code": "// Compose Lifecycle-Safe Flow Collection\n@Composable\nfun AccountScreen(viewModel: AccountViewModel = hiltViewModel()) {\n    // Automatically pauses collection when app goes to background!\n    val uiState by viewModel.uiState.collectAsStateWithLifecycle()\n\n    AccountContent(state = uiState)\n}\n\n// Fragment Lifecycle-Safe Flow Collection\noverride fun onViewCreated(view: View, savedInstanceState: Bundle?) {\n    super.onViewCreated(view, savedInstanceState)\n    viewLifecycleOwner.lifecycleScope.launch {\n        viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {\n            viewModel.uiState.collect { state ->\n                renderState(state)\n            }\n        }\n    }\n}",
        "realworld": "In GPS navigation or crypto price streaming apps, collecting with repeatOnLifecycle ensures location listeners and WebSockets suspend the moment the user locks their screen or switches apps."
      }
    ],
    "quizQuestions": [
      {
        "id": "q9-1",
        "question": "What is the difference in exception propagation between launch {} and async {} when called inside a regular CoroutineScope?",
        "difficulty": "Senior",
        "thinkPrompt": "Think about how exceptions are handled immediately vs deferred until await() is invoked.",
        "principalAnswer": "1. 'launch': Designed for fire-and-forget tasks. When an uncaught exception occurs inside launch, it is propagated immediately up the job hierarchy to the parent scope, cancelling siblings and triggering the CoroutineExceptionHandler (or crashing the application if unhandled). Wrapping the launch call itself in a try/catch does NOT catch the exception!\n\n2. 'async': Designed to compute a result and returns a 'Deferred<T>'. An uncaught exception inside async is encapsulated inside the Deferred object and is thrown when '.await()' is invoked on that Deferred. However, there is a major catch: if async is launched as a child of a standard 'coroutineScope' (not supervisorScope), its exception STILL propagates to the parent immediately upon failure, cancelling all siblings even before '.await()' is called!\n\nTo catch exceptions thrown by async without cancelling siblings, you must run it inside a 'supervisorScope' or catch exceptions inside the async block itself.",
        "keyPoints": [
          "launch propagates immediately to parent Job hierarchy",
          "async defers exception throwing until .await()",
          "In standard coroutineScope, async failure cancels siblings immediately",
          "supervisorScope isolates async failures"
        ],
        "pitfalls": [
          "Attempting to wrap launch { ... } in try/catch from the outside",
          "Assuming async never cancels its parent unless await() is called"
        ]
      }
    ]
  },
  {
    "id": "topic-10",
    "num": "10",
    "title": "Security Deep-Dive: Keystore, SSL Pinning, Play Integrity",
    "icon": "\ud83d\udd12",
    "badge": "Security",
    "desc": "Master hardware-backed Android Keystore (TEE/StrongBox), BiometricPrompt CryptoObject, rotation-safe SSL Pinning, Play Integrity API attestation, and ProGuard/R8.",
    "subtopics": [
      {
        "title": "Android Keystore & Biometric Hardware-Backed Cryptography",
        "what": "The Android Keystore stores cryptographic keys in hardware-isolated environments (TEE - Trusted Execution Environment, or StrongBox chips like Titan M). Key material NEVER enters application memory. Keys can be gated with biometric authentication using 'setUserAuthenticationRequired(true)'.",
        "why": "Storing encryption keys in SharedPreferences or hardcoded in APKs allows attackers on rooted devices or via reverse engineering (JADX) to steal keys and decrypt local data offline. Keystore keys resist extraction even with root access.",
        "how": "Generate an AES-256-GCM key with 'KeyGenParameterSpec'. Set 'setInvalidatedByBiometricEnrollment(true)' so keys are permanently destroyed if a new fingerprint is enrolled (preventing unauthorized user attacks). Pass the initialized Cipher into 'BiometricPrompt.CryptoObject'.",
        "code": "// Production Biometric-Gated Keystore Encryption Manager\nclass BiometricKeystoreManager @Inject constructor() {\n    private val keyStore = KeyStore.getInstance(\"AndroidKeyStore\").apply { load(null) }\n\n    fun generateBiometricKey(alias: String) {\n        val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, \"AndroidKeyStore\")\n        val spec = KeyGenParameterSpec.Builder(\n            alias,\n            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT\n        )\n            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)\n            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)\n            .setKeySize(256)\n            .setUserAuthenticationRequired(true) // Requires biometric auth to use!\n            .setUserAuthenticationParameters(0, KeyProperties.AUTH_BIOMETRIC_STRONG)\n            .setInvalidatedByBiometricEnrollment(true) // SECURITY: Invalidate key if new finger added\n            .build()\n\n        keyGenerator.init(spec)\n        keyGenerator.generateKey()\n    }\n\n    fun getEncryptCipher(alias: String): Cipher {\n        val secretKey = keyStore.getKey(alias, null) as SecretKey\n        return Cipher.getInstance(\"AES/GCM/NoPadding\").apply {\n            init(Cipher.ENCRYPT_MODE, secretKey)\n        }\n    }\n}\n\n// Gating Cipher with BiometricPrompt\nval cryptoObject = BiometricPrompt.CryptoObject(keystoreManager.getEncryptCipher(KEY_ALIAS))\nbiometricPrompt.authenticate(promptInfo, cryptoObject)",
        "realworld": "In digital banking apps, biometric authorization creates a hardware-backed signature over the payment payload. Setting setInvalidatedByBiometricEnrollment(true) ensures that if an attacker borrows an unlocked phone and enrolls their own fingerprint in Settings, all encrypted banking tokens are permanently wiped."
      },
      {
        "title": "SSL/TLS Pinning with Zero-Downtime Public Key Rotation",
        "what": "SSL Pinning verifies that the server certificate matches a hardcoded cryptographic hash, bypassing rogue or compromised Certificate Authorities (CAs). Public Key Pinning (pinning the SubjectPublicKeyInfo SHA-256 hash) is superior to certificate pinning because it survives certificate renewals as long as the same private key is used.",
        "why": "Without SSL pinning, Man-in-the-Middle (MITM) proxies like Charles or Burp Suite can install a user CA and intercept all traffic, reading plaintext credentials and banking tokens.",
        "how": "Always pin the public key hash ('sha256/...'). ALWAYS include at least one BACKUP PIN for an upcoming certificate rotation. Never pin a single leaf certificate alone.",
        "code": "// Zero-Downtime SSL Pinning Setup with Backup Pins\nval certificatePinner = CertificatePinner.Builder()\n    // Primary Active Public Key Pin\n    .add(\"api.securebank.com\", \"sha256/YLh1dUR9y6Kja30RrAn7JKnbQG/uEtLMkBgFF2Fuihg=\")\n    // CRITICAL: Backup Public Key Pin for Planned Server Key Rotation\n    .add(\"api.securebank.com\", \"sha256/Vjs8r4z+80wjNcr1YKepWQboSIRi63WsWXhIMN+eWys=\")\n    // Second Disaster Recovery Backup\n    .add(\"api.securebank.com\", \"sha256/k2v657xUM4MpNGnqw5Jh06ev05IjbJJOWIcZgarGDpc=\")\n    .build()\n\nval okHttpClient = OkHttpClient.Builder()\n    .certificatePinner(certificatePinner)\n    .build()",
        "realworld": "In large enterprise fintech deployments, pinning only the live certificate caused million-dollar outages when server certs auto-renewed. Providing a 3-pin strategy (Current, Backup 1, Backup 2) allows seamless server rotations without requiring immediate app updates."
      }
    ],
    "quizQuestions": [
      {
        "id": "q10-1",
        "question": "What is the security implication of setInvalidatedByBiometricEnrollment(true) in Android Keystore, and how does your app recover when a KeyPermanentlyInvalidatedException is thrown?",
        "difficulty": "Lead / Staff",
        "thinkPrompt": "Think about the attack vector where a thief gains device PIN access and enrolls a new biometric fingerprint.",
        "principalAnswer": "1. Security Implication: If an attacker obtains physical access to a user's phone and discovers their device lock screen PIN, they could navigate to Android Settings and enroll their own fingerprint. Without 'setInvalidatedByBiometricEnrollment(true)', the Keystore key would accept this newly enrolled fingerprint, allowing the attacker to decrypt the user's banking tokens. With this flag set to 'true', the Android Keystore automatically and permanently marks the master cryptographic key as invalid the moment any new biometric enrollment occurs on the device.\n\n2. Recovery Strategy: When the app attempts to initialize a Cipher using this key, Keystore throws 'KeyPermanentlyInvalidatedException'. The app must catch this exception, treat it as a critical security event, immediately wipe all local cached credentials and encrypted session tokens, and force the user to perform full re-authentication using their primary credentials (password + SMS/hardware OTP). Once re-authenticated, the app generates a fresh Keystore key pair.",
        "keyPoints": [
          "Prevents unauthorized fingerprint enrollment attacks",
          "Keystore automatically invalidates key when new biometric is registered",
          "Throws KeyPermanentlyInvalidatedException on cipher init",
          "Recovery: wipe local session tokens, force re-login with password + 2FA, generate fresh key"
        ],
        "pitfalls": [
          "Catching the exception and doing nothing (app enters permanent crash loop)",
          "Not knowing how to regenerate the key after invalidation"
        ]
      }
    ]
  },
  {
    "id": "topic-11",
    "num": "11",
    "title": "Performance Optimization, Testing & CI/CD",
    "icon": "\ud83d\ude80",
    "badge": "Performance",
    "desc": "Master Baseline Profiles Ahead-Of-Time (AOT) compilation, Macrobenchmark frame metrics, LeakCanary internals, Turbine Flow testing, and automated Fastlane pipelines.",
    "subtopics": [
      {
        "title": "Baseline Profiles & ART AOT Ahead-Of-Time Compilation",
        "what": "Baseline Profiles are a mechanism that bundles human-readable method signatures in APKs/AABs. Upon app installation, the Android Runtime (ART) pre-compiles these critical paths Ahead-Of-Time (AOT) into machine code using dex2oat.",
        "why": "Without Baseline Profiles, ART runs code using interpreted JIT mode on initial launch. This causes noticeable startup latency (2-4 seconds) and frame drops during first-scroll interactions. Baseline Profiles improve cold start times by 30-40% and eliminate scroll jank.",
        "how": "Create a ':baselineprofile' test module using 'BaselineProfileRule'. Exercise critical user journeys (cold start, dashboard feed scroll). Generate 'baseline-prof.txt' and bundle it in release builds.",
        "code": "// Baseline Profile Generator Test\n@RunWith(AndroidJUnit4::class)\nclass BaselineProfileGenerator {\n    @get:Rule val rule = BaselineProfileRule()\n\n    @Test\n    fun generateProfile() = rule.collect(\n        packageName = \"com.securebank.app\",\n        includeInStartupProfile = true\n    ) {\n        // 1. Cold Startup Path\n        startActivityAndWait()\n\n        // 2. Critical Journey: Scroll Transaction List\n        device.findObject(By.text(\"Transactions\")).click()\n        val list = device.findObject(By.res(\"transaction_list\"))\n        list.scroll(Direction.DOWN, 1.0f)\n        device.waitForIdle()\n    }\n}",
        "realworld": "In large enterprise apps with heavy Jetpack Compose adoption, Baseline Profiles eliminate JIT compilation of Compose internal runtime classes, taking startup from 2.2s to 1.3s on mid-range devices."
      },
      {
        "title": "Coroutines & Flow Unit Testing with Turbine",
        "what": "Turbine is an assertion library for Kotlin Flows. It provides a structured API ('flow.test { ... }') to consume and assert emissions sequentially with virtual clock support.",
        "why": "Manually collecting flows in tests with timeouts or global lists is flaky, prone to race conditions, and fails to verify unconsumed emissions or unexpected errors.",
        "how": "Use 'runTest' with 'StandardTestDispatcher' or 'UnconfinedTestDispatcher'. Call '.test { ... }' on the flow and assert items with 'awaitItem()', 'awaitError()', or 'ensureAllEventsConsumed()'.",
        "code": "// Production ViewModel Flow Unit Test with Turbine\n@Test\nfun `loadTransactions emits Loading then Success`() = runTest {\n    // Arrange\n    val mockTransactions = listOf(Transaction(\"1\", 50.0))\n    coEvery { repository.getTransactions() } returns Result.success(mockTransactions)\n    val viewModel = TransactionsViewModel(repository)\n\n    // Act & Assert via Turbine\n    viewModel.uiState.test {\n        // Initial state\n        assertThat(awaitItem()).isEqualTo(TransactionsUiState.Loading)\n\n        // Trigger action\n        viewModel.loadData()\n\n        // Verify state progression\n        val successState = awaitItem() as TransactionsUiState.Success\n        assertThat(successState.items).hasSize(1)\n\n        // Ensure no unexpected emissions\n        cancelAndConsumeRemainingEvents()\n    }\n}",
        "realworld": "Automating Turbine flow tests across ViewModels prevents UI regressions in continuous integration pipelines, guaranteeing that loading indicators and error banners trigger in the exact intended sequence."
      }
    ],
    "quizQuestions": [
      {
        "id": "q11-1",
        "question": "What is the difference between UnconfinedTestDispatcher and StandardTestDispatcher in kotlinx-coroutines-test? When should each be used?",
        "difficulty": "Senior",
        "thinkPrompt": "Think about eager vs queued execution of coroutine tasks and virtual time advancement.",
        "principalAnswer": "1. 'StandardTestDispatcher' (default in runTest): Coroutines launched on this dispatcher are QUEUED in an internal scheduler rather than executed eagerly. The virtual clock does not advance automatically. You must explicitly control execution using 'advanceUntilIdle()', 'advanceTimeBy(ms)', or 'runCurrent()'. Use this whenever execution ORDER matters, when testing delays, retries with exponential backoff, or debounce logic.\n\n2. 'UnconfinedTestDispatcher': Coroutines launched on this dispatcher execute EAGERLY and immediately on the current thread until the first suspension point. There is no queueing. Use this for simple ViewModel tests where you want state updates to take effect immediately without manually calling advanceUntilIdle(), especially when testing StateFlow emissions.",
        "keyPoints": [
          "StandardTestDispatcher queues work and requires manual time advancement",
          "UnconfinedTestDispatcher executes eagerly until suspension",
          "Use Standard for delays, retries, and execution order",
          "Use Unconfined for simple synchronous-like flow assertions"
        ],
        "pitfalls": [
          "Assuming runTest executes coroutines concurrently on background threads",
          "Mixing up advanceUntilIdle with advanceTimeBy"
        ]
      }
    ]
  },
  {
    "id": "topic-12",
    "num": "12",
    "title": "AOSP System Internals & On-Device AI",
    "icon": "\ud83e\udd16",
    "badge": "AOSP & AI",
    "desc": "Master Binder IPC kernel mechanics, Zygote fork Copy-on-Write, AIDL oneway, on-device Gemini Nano (AICore) vs Cloud routing, and Agentic ReAct safety guardrails.",
    "subtopics": [
      {
        "title": "Binder IPC Kernel Mechanics & AIDL 'oneway'",
        "what": "Binder is Android's kernel-mediated IPC driver (/dev/binder). Unlike traditional Linux IPC that requires 2 data copies (user -> kernel -> user), Binder uses mmap to achieve single-copy data transfer. AIDL 'oneway' marks calls as asynchronous and non-blocking for the caller.",
        "why": "Making synchronous Binder calls from the Main Thread causes ANRs if the remote service is slow. Furthermore, high-frequency IPC callbacks (like 50Hz CAN bus telemetry in automotive) can exhaust the 15-thread Binder thread pool if synchronous.",
        "how": "Use AIDL 'oneway' for high-frequency callbacks. Clear caller identity using 'Binder.clearCallingIdentity()' in system services before accessing internal resources to prevent privilege escalation. Pass large payloads via MemoryFile/Ashmem, not Parcel (1MB limit).",
        "code": "// AIDL Interface for Automotive IVI Telemetry\n// IVehicleTelemetryService.aidl\ninterface IVehicleTelemetryService {\n    // oneway: non-blocking, returns immediately without waiting for server response\n    oneway void registerSpeedCallback(in ISpeedCallback callback);\n    oneway void unregisterSpeedCallback(in ISpeedCallback callback);\n\n    VehicleSnapshot getVehicleSnapshot(); // Synchronous call\n}\n\n// Privileged System Service with Identity Management\nclass VehicleTelemetryService : IVehicleTelemetryService.Stub() {\n    override fun getVehicleSnapshot(): VehicleSnapshot {\n        // Enforce permission\n        mContext.enforceCallingPermission(\"com.oem.permission.VEHICLE_DATA\", \"getSnapshot\")\n\n        // Clear caller identity to run subsequent calls with system privileges\n        val token = Binder.clearCallingIdentity()\n        return try {\n            hardwareHal.readCanBusSnapshot()\n        } finally {\n            Binder.restoreCallingIdentity(token) // MUST restore in finally block!\n        }\n    }\n}",
        "realworld": "In Android Automotive (AAOS), high-frequency speed and sensor telemetry streams from native vehicle HALs to the Android HMI use oneway Binder calls with RemoteCallbackList to ensure zero UI thread stalls."
      },
      {
        "title": "On-Device AI (Gemini Nano) vs Cloud AI: Privacy Routing & Safety",
        "what": "On-device AI executes models (Gemini Nano via Android AICore) directly on the local NPU/GPU without network transit. Cloud AI (Gemini Flash/Pro) executes on remote servers. An AI Router enforces data classification: Protected Health Information (PHI) and PII must strictly route on-device.",
        "why": "Sending sensitive patient data or raw banking credentials to cloud LLMs violates HIPAA, GDPR, and PCI-DSS compliance, incurring legal penalties.",
        "how": "Implement an AIRouter that inspects data classification. If the request contains PHI or PII, enforce on-device execution; if on-device inference is unsupported on the hardware, gracefully disable the feature rather than leaking data to cloud endpoints.",
        "code": "// Privacy-Preserving AI Routing Engine\nclass AIRouter @Inject constructor(\n    private val onDeviceNanoEngine: OnDeviceGeminiNanoEngine,\n    private val cloudGeminiEngine: CloudGeminiEngine\n) {\n    suspend fun processUserRequest(request: AIRequest): Result<String> {\n        return when (request.dataClassification) {\n            DataClassification.CONTAINS_PHI, DataClassification.CONTAINS_PII -> {\n                // STRICT COMPLIANCE RULE: Must run locally on device!\n                if (onDeviceNanoEngine.isHardwareSupported()) {\n                    onDeviceNanoEngine.infer(request.sanitizedPrompt)\n                } else {\n                    Result.failure(SecurityException(\"Hardware does not support on-device AI required for sensitive data.\"))\n                }\n            }\n            DataClassification.PUBLIC_OR_ANONYMIZED -> {\n                // Safe to route to high-capacity Cloud Gemini\n                cloudGeminiEngine.infer(request.sanitizedPrompt)\n            }\n        }\n    }\n}",
        "realworld": "In healthcare telemedicine apps, clinical note summarization containing patient diagnostic codes runs exclusively via on-device Gemini Nano, guaranteeing zero PHI leakage to external cloud APIs."
      }
    ],
    "quizQuestions": [
      {
        "id": "q12-1",
        "question": "What is the purpose of Binder.clearCallingIdentity() and Binder.restoreCallingIdentity()? What security vulnerability occurs if restoreCallingIdentity is omitted?",
        "difficulty": "Lead / Staff",
        "thinkPrompt": "Think about Linux UIDs, privilege escalation, and thread-local Binder state across reused thread pools.",
        "principalAnswer": "When a client app (e.g. UID 10045) makes an IPC call to a system service running in system_server (UID 1000), the Binder driver sets the calling UID on that thread to 10045. If the system service subsequently calls another system service or accesses local databases, those downstream calls would be evaluated against client UID 10045 (which may lack necessary permissions).\n\n'Binder.clearCallingIdentity()' clears the thread's calling identity and returns a token, resetting the effective UID to the system service's own UID (1000), allowing it to complete privileged internal operations.\n\nCRITICAL SECURITY BUG: If 'Binder.restoreCallingIdentity(token)' is omitted (e.g. bypassed by an unhandled exception), the Binder thread remains permanently elevated with UID 1000! When that thread returns to the Binder thread pool and handles a future IPC call from another unprivileged third-party app, that app's request executes with system privileges\u2014a catastrophic privilege escalation vulnerability. Hence, 'restoreCallingIdentity' must ALWAYS be executed in a 'finally' block.",
        "keyPoints": [
          "Binder records caller UID in thread-local storage",
          "clearCallingIdentity elevates execution to service's own UID",
          "restoreCallingIdentity resets identity back to caller",
          "Must be inside a finally block to prevent privilege escalation via thread pool reuse"
        ],
        "pitfalls": [
          "Not placing restoreCallingIdentity in a finally block",
          "Thinking clearCallingIdentity changes the client process's UID"
        ]
      }
    ]
  }
];
