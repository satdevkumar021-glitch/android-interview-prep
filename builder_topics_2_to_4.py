# Module for Topics 2, 3, 4

def get_topics_2_to_4():
    topics = []

    # ==============================================================================
    # TOPIC 2: Android Component Lifecycles & Process Death
    # ==============================================================================
    topics.append({
        "id": "topic-2",
        "num": "02",
        "title": "Android Component Lifecycles & Process Death",
        "icon": "📱",
        "badge": "Lifecycle",
        "desc": "Master Activity & Fragment lifecycles, viewLifecycleOwner, OS process death restoration, SavedStateHandle, PendingIntent security flags, and ContentProviders.",
        "subtopics": [
            {
                "title": "Activity & Fragment Lifecycle Deep-Dive & viewLifecycleOwner",
                "what": "Activity has 7 lifecycle states (onCreate -> onStart -> onResume -> onPause -> onStop -> onDestroy -> onRestart). Fragments have a separate View lifecycle that is destroyed and recreated independently of the Fragment instance itself when navigating backstacks in FragmentManager.",
                "why": "Using Fragment's 'this' as the LifecycleOwner for LiveData or Flow collection leaks views. When a Fragment moves to the backstack, its View is destroyed (onDestroyView), but the Fragment instance lives on. Observers registered with 'this' continue referencing detached views, leaking Bitmaps, ViewBindings, and causing crashes upon re-entry.",
                "how": "Always use 'viewLifecycleOwner' or 'viewLifecycleOwner.lifecycleScope' when observing state in Fragments. Clean up ViewBinding backing properties in onDestroyView() by setting '_binding = null'. In Activity, coordinate heavy resource releases in onStop() (when UI is no longer visible) rather than onPause().",
                "code": """// Correct Leak-Free Fragment Pattern
class TransferConfirmationFragment : Fragment(R.layout.fragment_transfer) {
    private var _binding: FragmentTransferBinding? = null
    private val binding get() = _binding!! // Safe non-null accessor

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentTransferBinding.bind(view)

        // CRITICAL: Bind observer to viewLifecycleOwner, NEVER 'this'
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.transferState.collect { state ->
                    renderState(state)
                }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // Essential: Prevents memory leak when Fragment placed in backstack
    }
}""",
                "realworld": "In large Banking and E-commerce checkout funnels with multi-step Fragment backstacks, neglecting to nullify ViewBinding or observing with 'this' retains heavy View hierarchies and user card data in memory, triggering Low Memory Killer (LMK) events on lower-end devices."
            },
            {
                "title": "Configuration Change vs OS Process Death (The State Survival Matrix)",
                "what": "Configuration changes (screen rotation, fold/unfold, dark mode, locale change) tear down and recreate the Activity instance, but the Application process remains alive. OS Process Death occurs when Android kills a backgrounded app process to reclaim memory for foreground tasks. The user later returns via Recents, and the OS recreates the task stack.",
                "why": "ViewModels survive configuration changes because they are stored in the Activity's ViewModelStore (retained via NonConfigurationInstances). However, ViewModels DO NOT survive process death. Relying solely on ViewModel memory state causes 'NullPointerException' or user form loss upon process recreation.",
                "how": "Use the State Survival Hierarchy: (1) ViewModel in-memory state for runtime data; (2) 'SavedStateHandle' (backed by Bundle) for critical IDs and user inputs that must survive process death (< 1MB limit); (3) Room/DataStore for persistent offline data.",
                "code": """// Process-Death Resilient Banking ViewModel
@HiltViewModel
class SendMoneyViewModel @Inject constructor(
    private val savedStateHandle: SavedStateHandle, // Automatically restored after process death
    private val transferRepo: TransferRepository
) : ViewModel() {

    // Backed by SavedStateHandle Bundle: survives BOTH rotation AND process death
    val recipientIban: StateFlow<String> = savedStateHandle.getStateFlow(KEY_IBAN, "")
    val transferAmount: StateFlow<Double> = savedStateHandle.getStateFlow(KEY_AMOUNT, 0.0)

    fun onIbanChanged(newIban: String) {
        savedStateHandle[KEY_IBAN] = newIban
    }

    fun onAmountChanged(amount: Double) {
        savedStateHandle[KEY_AMOUNT] = amount
    }

    companion object {
        private const val KEY_IBAN = "saved_recipient_iban"
        private const val KEY_AMOUNT = "saved_transfer_amount"
    }
}""",
                "realworld": "In digital banking wire transfers, a user enters account and amount details, switches to an SMS app to check an OTP, and the OS kills the banking app due to low RAM. When returning, SavedStateHandle restores the exact wizard step and transfer fields seamlessly."
            },
            {
                "title": "PendingIntent Security & Android 12+ Mutability Requirements",
                "what": "A PendingIntent is a token handed to another app (like NotificationManager, AlarmManager, or external widgets) granting that external process the permission to execute an Intent with your app's identity and privileges. Starting in Android 12 (API 31), every PendingIntent must explicitly specify FLAG_IMMUTABLE or FLAG_MUTABLE.",
                "why": "Unspecified or mutable PendingIntents are a major security vulnerability (Intent Redirection / Injection). A malicious app can intercept a mutable PendingIntent and overwrite its internal extras, URI, or target component, gaining unauthorized access to privileged exported components.",
                "how": "Always use 'PendingIntent.FLAG_IMMUTABLE' by default. Only use 'FLAG_MUTABLE' when the receiving system genuinely needs to fill in intent arguments (such as Notification Direct Reply or inline action responses).",
                "code": """// Secure Immutable PendingIntent for Push Notification
val intent = Intent(context, TransactionDetailActivity::class.java).apply {
    putExtra(EXTRA_TXN_ID, transactionId)
    flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
}

val flags = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
} else {
    PendingIntent.FLAG_UPDATE_CURRENT
}

val pendingIntent = PendingIntent.getActivity(context, REQUEST_CODE, intent, flags)""",
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
                "keyPoints": ["ViewModelStore survives rotation via NonConfigurationInstances", "Process death wipes all memory/ViewModels", "SavedStateHandle is backed by savedInstanceState Bundle", "Testing via: adb shell am kill <package_name> after backgrounding"],
                "pitfalls": ["Thinking ViewModels survive process death", "Testing by pressing the Red Stop button in Android Studio (which kills the task without saving state)"]
            },
            {
                "id": "q2-2",
                "question": "Why does observing LiveData or StateFlow with 'viewLifecycleOwner' prevent memory leaks in Fragments compared to passing 'this'?",
                "difficulty": "Senior",
                "thinkPrompt": "Consider Fragment lifecycle vs View lifecycle when transactions are added to the FragmentManager backstack.",
                "principalAnswer": "In Fragments, the View lifecycle and Fragment lifecycle are decoupled. When a Fragment transaction replaces Fragment A with Fragment B and adds A to the backstack, Fragment A's View is destroyed via 'onDestroyView()', but Fragment A's Java/Kotlin instance remains alive in the backstack.\n\nIf you observe LiveData or Flow passing 'this' (the Fragment instance), the observer registration remains tied to the Fragment's lifetime. Each time Fragment A is restored from the backstack, 'onViewCreated()' executes again, registering a duplicate observer. The old observers still reference the destroyed View's widgets, creating substantial memory leaks and causing duplicate emissions. Using 'viewLifecycleOwner' ensures the observer is automatically unregistered as soon as 'onDestroyView()' fires.",
                "keyPoints": ["Decoupled View lifecycle vs Fragment instance lifecycle", "FragmentManager backstack preserves Fragment instance while destroying View", "Passing 'this' creates duplicate observers and holds references to detached Views", "viewLifecycleOwner unregisters exactly at onDestroyView"],
                "pitfalls": ["Assuming Fragment onDestroy and onDestroyView always fire together", "Not nullifying ViewBinding in onDestroyView"]
            }
        ]
    })

    # ==============================================================================
    # TOPIC 3: Android Services & Background Work
    # ==============================================================================
    topics.append({
        "id": "topic-3",
        "num": "03",
        "title": "Android Services & Background Work",
        "icon": "⚙️",
        "badge": "Services",
        "desc": "Master Started, Bound, and Foreground Services, Android 14 foregroundServiceType requirements, WorkManager chaining and constraints, and Doze mode policies.",
        "subtopics": [
            {
                "title": "Service Types & Android 14 Foreground Service Types",
                "what": "Android Services run on the Main Thread by default unless explicitly offloaded. Three types exist: Started (startService), Bound (bindService via Binder/AIDL), and Foreground Services (show a persistent user notification). Starting in Android 14 (API 34), apps MUST specify an explicit 'android:foregroundServiceType' in the manifest and request corresponding runtime permissions.",
                "why": "Starting background services from the background was restricted in Android 8.0 (Oreo) to eliminate battery-draining background operations. Foreground services guarantee process priority (preventing LMK kills) by informing the user that persistent work (e.g. navigation, media, audio recording, data sync) is ongoing.",
                "how": "Declare 'android:foregroundServiceType' in the AndroidManifest. Call 'startForeground(NOTIFICATION_ID, notification)' within 5 seconds of 'startForegroundService()' to avoid an ANR/ForegroundServiceDidNotStartInTimeException.",
                "code": """// Android 14 Compliant Manifest Declaration
<!-- AndroidManifest.xml -->
<service
    android:name=".upload.DocumentUploadService"
    android:foregroundServiceType="dataSync"
    android:exported="false" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />

// Service Implementation with Notification
class DocumentUploadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createPersistentNotification("Uploading medical records...")
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
            stopSelf(startId) // Always stop with startId to avoid stopping newer invocations
        }
        return START_NOT_STICKY
    }
}""",
                "realworld": "In Healthcare and Banking apps, uploading large multi-megabyte encrypted documents (diagnostic scans, KYC proof-of-address PDFs) requires a Foreground Service of type 'dataSync' so the transfer completes even if the user switches to other apps."
            },
            {
                "title": "WorkManager: Constraints, Chaining & CoroutineWorker",
                "what": "WorkManager is the Google-recommended solution for persistent, deferrable background work. It guarantees execution even if the app process is killed or the device is rebooted. It uses CoroutineWorker to execute suspend functions safely.",
                "why": "Raw Coroutines die when the app process is killed. JobScheduler is API-level dependent. AlarmManager is designed for exact alarms, not deferrable background work. WorkManager automatically selects the best underlying mechanism (JobScheduler on API 23+, AlarmManager + BroadcastReceiver on legacy) while enforcing hardware constraints (Unmetered Network, Charging, Battery Not Low).",
                "how": "Subclass 'CoroutineWorker' and implement 'doWork()'. Enforce constraints with 'Constraints.Builder()', chain tasks using 'WorkManager.getInstance(context).beginWith().then()', and handle periodic work with 'PeriodicWorkRequestBuilder'.",
                "code": """// Robust Offline Data Sync Chain with Constraints
class EncryptedSyncWorker(
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
            // Transient error: retry with exponential backoff
            Result.retry()
        } catch (e: Exception) {
            Result.failure()
        }
    }
}

// WorkManager Chaining Pipeline
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED)
    .setRequiresBatteryNotLow(true)
    .build()

val compressWork = OneTimeWorkRequestBuilder<CompressWorker>().build()
val encryptWork = OneTimeWorkRequestBuilder<EncryptWorker>().build()
val uploadWork = OneTimeWorkRequestBuilder<EncryptedSyncWorker>()
    .setConstraints(constraints)
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.SECONDS)
    .build()

WorkManager.getInstance(context)
    .beginUniqueWork("ledger_sync", ExistingWorkPolicy.KEEP, compressWork)
    .then(encryptWork)
    .then(uploadWork)
    .enqueue()""",
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
                "keyPoints": ["WorkManager: deferrable + guaranteed persistent", "Foreground Service: immediate + user-visible ongoing notification", "AlarmManager: exact wall-clock triggers (alarm clocks, calendar)", "Avoid using JobScheduler directly; rely on WorkManager"],
                "pitfalls": ["Using AlarmManager for background syncing", "Using raw Coroutines in ViewModel for background work that must survive process kill"]
            }
        ]
    })

    # ==============================================================================
    # TOPIC 4: Jetpack Compose Deep-Dive & Internals
    # ==============================================================================
    topics.append({
        "id": "topic-4",
        "num": "04",
        "title": "Jetpack Compose Deep-Dive & Internals",
        "icon": "🎨",
        "badge": "Compose",
        "desc": "Master the Compose compiler & runtime, stability system (@Immutable/@Stable), recomposition optimization, SideEffects, derivedStateOf, and CompositionLocal.",
        "subtopics": [
            {
                "title": "Compose Recomposition Engine & Stability Rules",
                "what": "Recomposition is the process where the Compose runtime re-executes composable functions when their state reads change. The Compose compiler plugin analyzes function parameters at build time and classifies them as Stable or Unstable. A composable function is 'skippable' if all of its parameters are stable.",
                "why": "If an unstable type (such as standard java.util.List, any class with 'var' properties, or an external third-party DTO) is passed into a Composable, the Compose runtime CANNOT guarantee immutability. As a result, it refuses to skip the composable, forcing full recomposition of that subtree even if the data did not change—leading to frame drops.",
                "how": "Mark domain models with '@Immutable' or '@Stable'. Replace standard 'List<T>' with 'ImmutableList<T>' from kotlinx-collections-immutable. Configure Compose compiler metrics/reports via Gradle to audit unstable classes in your build.",
                "code": """// ❌ UNSTABLE: List is an interface, Compose cannot verify immutability
data class AccountDashboardState(
    val accounts: List<Account>, // Causes AccountList to re-evaluate on every recomposition
    val totalBalance: Double
)

// ✅ STABLE: Guarantees skipping optimization
@Immutable
data class AccountDashboardUiState(
    val accounts: ImmutableList<Account>, // Fully stable!
    val totalBalance: Double
)

@Composable
fun AccountList(
    accounts: ImmutableList<Account>,
    onAccountClick: (String) -> Unit, // Stable lambda reference
    modifier: Modifier = Modifier
) {
    LazyColumn(modifier = modifier) {
        items(
            items = accounts,
            key = { account -> account.id }, // Stable identity prevents item rebuild on reorder
            contentType = { "account_row" }  // Enables item slot recycling
        ) { account ->
            AccountRow(account = account, onClick = onAccountClick)
        }
    }
}""",
                "realworld": "In high-frequency real-time banking tickers or crypto trading screens updating balances multiple times per second, stable state models and key() bindings prevent the entire screen from recomposing, reducing CPU consumption and battery drain by up to 65%."
            },
            {
                "title": "derivedStateOf vs remember(key)",
                "what": "'remember(key) { ... }' recomputes its calculation whenever 'key' changes. 'derivedStateOf { ... }' creates an observable state object that only notifies consumers when its RESULT value actually changes, regardless of how frequently the underlying state dependencies change.",
                "why": "Reading rapid-fire state changes (like LazyListState.firstVisibleItemIndex changing on every pixel scroll) inside a Composable triggers recomposition on EVERY pixel moved. 'derivedStateOf' acts as a high-frequency dampener.",
                "how": "Use 'derivedStateOf' when an input state changes frequently, but your UI only cares about a derived boolean or threshold value. Use 'remember(key)' when you want to cache a calculation based on identity changes.",
                "code": """// High-Frequency Scroll Optimization in Compose
val listState = rememberLazyListState()

// ❌ BAD: Recomposes on every single scroll pixel!
// val showScrollToTop = listState.firstVisibleItemIndex > 0

// ✅ GOOD: Derived state dampener: ONLY emits when boolean flips (true <-> false)
val showScrollToTop by remember {
    derivedStateOf { listState.firstVisibleItemIndex > 0 }
}

AnimatedVisibility(visible = showScrollToTop) {
    ScrollToTopFloatingActionButton(onClick = { scope.launch { listState.animateScrollToItem(0) } })
}""",
                "realworld": "In large transaction lists or e-commerce feeds, using derivedStateOf for sticky headers, scroll-to-top FABs, or collapsible top app bars ensures the scroll gesture remains smooth at 120Hz."
            },
            {
                "title": "SideEffects Lifecycle Decision Tree",
                "what": "SideEffects are escape hatches used to execute operations that interact with state outside the Composable tree: LaunchedEffect, rememberCoroutineScope, DisposableEffect, SideEffect, and produceState.",
                "why": "Executing side-effects directly inside the body of a Composable is hazardous because Composables can execute on any thread, execute out of order, or be cancelled and discarded mid-frame without warning.",
                "how": "Follow the decision tree: (1) Async work driven by COMPOSITION / key change -> 'LaunchedEffect(key)'; (2) Async work driven by USER EVENT (button click) -> 'rememberCoroutineScope()'; (3) Setup/teardown with cleanup (sensors, broadcast receivers, camera) -> 'DisposableEffect(key)'; (4) Sync Compose state to non-Compose object -> 'SideEffect'; (5) Bridge external callback into State -> 'produceState'.",
                "code": """// Complete SideEffect Architecture Example
@Composable
fun BiometricGateScreen(
    onAuthenticated: () -> Unit,
    viewModel: AuthViewModel = hiltViewModel()
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope() // For user-triggered button click

    // 1. DisposableEffect: Register & Clean up Biometric Callback safely
    DisposableEffect(context) {
        val biometricManager = BiometricManager.from(context)
        val receiver = BiometricStatusReceiver()
        context.registerReceiver(receiver, IntentFilter("ACTION_BIOMETRIC_CHANGED"))

        onDispose {
            context.unregisterReceiver(receiver) // Guaranteed cleanup when leaving composition
        }
    }

    // 2. LaunchedEffect: Key-driven trigger on error state
    val errorState by viewModel.errorState.collectAsStateWithLifecycle()
    LaunchedEffect(errorState) {
        errorState?.let { err ->
            showHapticFeedback(context)
            snackbarHostState.showSnackbar(err.localizedMessage)
        }
    }

    Button(onClick = {
        // User action: Launch via rememberCoroutineScope
        coroutineScope.launch {
            viewModel.authenticateBiometrics()
        }
    }) {
        Text("Authenticate")
    }
}""",
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
                "keyPoints": ["Composer injected into every composable", "Slot table memory structure", "$changed bitmask tracks parameter mutations", "Stable types allow early skipToGroupEnd()", "Unstable types disable skipping optimization"],
                "pitfalls": ["Thinking Compose uses Android View tree invalidation", "Not knowing about the Slot Table or Composer"]
            }
        ]
    })

    return topics

if __name__ == '__main__':
    print(f"Builder 2-4 loaded with {len(get_topics_2_to_4())} topics.")
