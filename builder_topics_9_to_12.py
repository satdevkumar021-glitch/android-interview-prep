# Module for Topics 9, 10, 11, 12

def get_topics_9_to_12():
    topics = []

    # ==============================================================================
    # TOPIC 9: Concurrency: Coroutines, Flow & Structured Concurrency
    # ==============================================================================
    topics.append({
        "id": "topic-9",
        "num": "09",
        "title": "Concurrency: Coroutines, Flow & Structured Concurrency",
        "icon": "⚡",
        "badge": "Coroutines",
        "desc": "Master CoroutineContext, coroutineScope vs supervisorScope, exception propagation, Flow backpressure, repeatOnLifecycle, and Turbine unit testing.",
        "subtopics": [
            {
                "title": "Structured Concurrency: coroutineScope vs supervisorScope",
                "what": "Structured concurrency guarantees that child coroutines are scoped to their parent hierarchy. In 'coroutineScope', if ANY child fails with an unhandled exception, the entire scope immediately cancels all remaining sibling coroutines and propagates the failure upward. In 'supervisorScope', a child failure is isolated; sibling coroutines continue executing undisturbed.",
                "why": "In a dashboard fetching Balance, Transactions, and Promotional Offers in parallel, you don't want the failure of an optional 'Offers' API to crash or cancel the critical 'Balance' or 'Transactions' coroutines. Using supervisorScope protects critical tasks from non-critical failures.",
                "how": "Use 'coroutineScope' when tasks are ATOMIC (all must succeed together or all must be rolled back, like multi-step checkout). Use 'supervisorScope' when tasks are INDEPENDENT (partial success is acceptable).",
                "code": """// Production Resilient Parallel Dashboard Loading
suspend fun fetchDashboardData(): DashboardResult = supervisorScope {
    // 1. Critical Balance Call
    val balanceDeferred = async { accountApi.getBalance() }
    // 2. Critical Transactions Call
    val txnsDeferred = async { accountApi.getTransactions() }
    // 3. Optional Recommendations Call
    val offersDeferred = async {
        try {
            recommendationsApi.getOffers()
        } catch (e: Exception) {
            Timber.w(e, "Optional offers failed, returning fallback")
            emptyList<Offer>()
        }
    }

    // Await all independent results safely
    DashboardResult(
        balance = balanceDeferred.await(),
        transactions = txnsDeferred.await(),
        offers = offersDeferred.await()
    )
}""",
                "realworld": "In banking and e-commerce apps, using supervisorScope for home screen loading ensures that a 500 error from an advertisement service doesn't crash the user's primary account view."
            },
            {
                "title": "repeatOnLifecycle vs collectAsStateWithLifecycle",
                "what": "Flows collected in Android must respect the Activity/Fragment lifecycle. 'repeatOnLifecycle(Lifecycle.State.STARTED)' cancels the collecting coroutine when the lifecycle drops below STARTED (app backgrounded) and automatically restarts collection when it returns to STARTED. In Compose, 'collectAsStateWithLifecycle()' provides this exact behavior natively.",
                "why": "Collecting cold flows or continuous WebSocket streams while the app is in the background wastes device battery, consumes cellular bandwidth, and risks crashes from attempting to manipulate detached views.",
                "how": "Never use 'lifecycleScope.launch { flow.collect { ... } }' directly for UI collection. In Compose, always use 'flow.collectAsStateWithLifecycle()'. In Fragments, wrap collection inside 'viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED)'.",
                "code": """// Compose Lifecycle-Safe Flow Collection
@Composable
fun AccountScreen(viewModel: AccountViewModel = hiltViewModel()) {
    // Automatically pauses collection when app goes to background!
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    AccountContent(state = uiState)
}

// Fragment Lifecycle-Safe Flow Collection
override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    super.onViewCreated(view, savedInstanceState)
    viewLifecycleOwner.lifecycleScope.launch {
        viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
            viewModel.uiState.collect { state ->
                renderState(state)
            }
        }
    }
}""",
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
                "keyPoints": ["launch propagates immediately to parent Job hierarchy", "async defers exception throwing until .await()", "In standard coroutineScope, async failure cancels siblings immediately", "supervisorScope isolates async failures"],
                "pitfalls": ["Attempting to wrap launch { ... } in try/catch from the outside", "Assuming async never cancels its parent unless await() is called"]
            }
        ]
    })

    # ==============================================================================
    # TOPIC 10: Security Deep-Dive: Keystore, SSL Pinning, Play Integrity
    # ==============================================================================
    topics.append({
        "id": "topic-10",
        "num": "10",
        "title": "Security Deep-Dive: Keystore, SSL Pinning, Play Integrity",
        "icon": "🔒",
        "badge": "Security",
        "desc": "Master hardware-backed Android Keystore (TEE/StrongBox), BiometricPrompt CryptoObject, rotation-safe SSL Pinning, Play Integrity API attestation, and ProGuard/R8.",
        "subtopics": [
            {
                "title": "Android Keystore & Biometric Hardware-Backed Cryptography",
                "what": "The Android Keystore stores cryptographic keys in hardware-isolated environments (TEE - Trusted Execution Environment, or StrongBox chips like Titan M). Key material NEVER enters application memory. Keys can be gated with biometric authentication using 'setUserAuthenticationRequired(true)'.",
                "why": "Storing encryption keys in SharedPreferences or hardcoded in APKs allows attackers on rooted devices or via reverse engineering (JADX) to steal keys and decrypt local data offline. Keystore keys resist extraction even with root access.",
                "how": "Generate an AES-256-GCM key with 'KeyGenParameterSpec'. Set 'setInvalidatedByBiometricEnrollment(true)' so keys are permanently destroyed if a new fingerprint is enrolled (preventing unauthorized user attacks). Pass the initialized Cipher into 'BiometricPrompt.CryptoObject'.",
                "code": """// Production Biometric-Gated Keystore Encryption Manager
class BiometricKeystoreManager @Inject constructor() {
    private val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }

    fun generateBiometricKey(alias: String) {
        val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        val spec = KeyGenParameterSpec.Builder(
            alias,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)
            .setUserAuthenticationRequired(true) // Requires biometric auth to use!
            .setUserAuthenticationParameters(0, KeyProperties.AUTH_BIOMETRIC_STRONG)
            .setInvalidatedByBiometricEnrollment(true) // SECURITY: Invalidate key if new finger added
            .build()

        keyGenerator.init(spec)
        keyGenerator.generateKey()
    }

    fun getEncryptCipher(alias: String): Cipher {
        val secretKey = keyStore.getKey(alias, null) as SecretKey
        return Cipher.getInstance("AES/GCM/NoPadding").apply {
            init(Cipher.ENCRYPT_MODE, secretKey)
        }
    }
}

// Gating Cipher with BiometricPrompt
val cryptoObject = BiometricPrompt.CryptoObject(keystoreManager.getEncryptCipher(KEY_ALIAS))
biometricPrompt.authenticate(promptInfo, cryptoObject)""",
                "realworld": "In digital banking apps, biometric authorization creates a hardware-backed signature over the payment payload. Setting setInvalidatedByBiometricEnrollment(true) ensures that if an attacker borrows an unlocked phone and enrolls their own fingerprint in Settings, all encrypted banking tokens are permanently wiped."
            },
            {
                "title": "SSL/TLS Pinning with Zero-Downtime Public Key Rotation",
                "what": "SSL Pinning verifies that the server certificate matches a hardcoded cryptographic hash, bypassing rogue or compromised Certificate Authorities (CAs). Public Key Pinning (pinning the SubjectPublicKeyInfo SHA-256 hash) is superior to certificate pinning because it survives certificate renewals as long as the same private key is used.",
                "why": "Without SSL pinning, Man-in-the-Middle (MITM) proxies like Charles or Burp Suite can install a user CA and intercept all traffic, reading plaintext credentials and banking tokens.",
                "how": "Always pin the public key hash ('sha256/...'). ALWAYS include at least one BACKUP PIN for an upcoming certificate rotation. Never pin a single leaf certificate alone.",
                "code": """// Zero-Downtime SSL Pinning Setup with Backup Pins
val certificatePinner = CertificatePinner.Builder()
    // Primary Active Public Key Pin
    .add("api.securebank.com", "sha256/YLh1dUR9y6Kja30RrAn7JKnbQG/uEtLMkBgFF2Fuihg=")
    // CRITICAL: Backup Public Key Pin for Planned Server Key Rotation
    .add("api.securebank.com", "sha256/Vjs8r4z+80wjNcr1YKepWQboSIRi63WsWXhIMN+eWys=")
    // Second Disaster Recovery Backup
    .add("api.securebank.com", "sha256/k2v657xUM4MpNGnqw5Jh06ev05IjbJJOWIcZgarGDpc=")
    .build()

val okHttpClient = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build()""",
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
                "keyPoints": ["Prevents unauthorized fingerprint enrollment attacks", "Keystore automatically invalidates key when new biometric is registered", "Throws KeyPermanentlyInvalidatedException on cipher init", "Recovery: wipe local session tokens, force re-login with password + 2FA, generate fresh key"],
                "pitfalls": ["Catching the exception and doing nothing (app enters permanent crash loop)", "Not knowing how to regenerate the key after invalidation"]
            }
        ]
    })

    # ==============================================================================
    # TOPIC 11: Performance Optimization, Testing & CI/CD
    # ==============================================================================
    topics.append({
        "id": "topic-11",
        "num": "11",
        "title": "Performance Optimization, Testing & CI/CD",
        "icon": "🚀",
        "badge": "Performance",
        "desc": "Master Baseline Profiles Ahead-Of-Time (AOT) compilation, Macrobenchmark frame metrics, LeakCanary internals, Turbine Flow testing, and automated Fastlane pipelines.",
        "subtopics": [
            {
                "title": "Baseline Profiles & ART AOT Ahead-Of-Time Compilation",
                "what": "Baseline Profiles are a mechanism that bundles human-readable method signatures in APKs/AABs. Upon app installation, the Android Runtime (ART) pre-compiles these critical paths Ahead-Of-Time (AOT) into machine code using dex2oat.",
                "why": "Without Baseline Profiles, ART runs code using interpreted JIT mode on initial launch. This causes noticeable startup latency (2-4 seconds) and frame drops during first-scroll interactions. Baseline Profiles improve cold start times by 30-40% and eliminate scroll jank.",
                "how": "Create a ':baselineprofile' test module using 'BaselineProfileRule'. Exercise critical user journeys (cold start, dashboard feed scroll). Generate 'baseline-prof.txt' and bundle it in release builds.",
                "code": """// Baseline Profile Generator Test
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {
    @get:Rule val rule = BaselineProfileRule()

    @Test
    fun generateProfile() = rule.collect(
        packageName = "com.securebank.app",
        includeInStartupProfile = true
    ) {
        // 1. Cold Startup Path
        startActivityAndWait()

        // 2. Critical Journey: Scroll Transaction List
        device.findObject(By.text("Transactions")).click()
        val list = device.findObject(By.res("transaction_list"))
        list.scroll(Direction.DOWN, 1.0f)
        device.waitForIdle()
    }
}""",
                "realworld": "In large enterprise apps with heavy Jetpack Compose adoption, Baseline Profiles eliminate JIT compilation of Compose internal runtime classes, taking startup from 2.2s to 1.3s on mid-range devices."
            },
            {
                "title": "Coroutines & Flow Unit Testing with Turbine",
                "what": "Turbine is an assertion library for Kotlin Flows. It provides a structured API ('flow.test { ... }') to consume and assert emissions sequentially with virtual clock support.",
                "why": "Manually collecting flows in tests with timeouts or global lists is flaky, prone to race conditions, and fails to verify unconsumed emissions or unexpected errors.",
                "how": "Use 'runTest' with 'StandardTestDispatcher' or 'UnconfinedTestDispatcher'. Call '.test { ... }' on the flow and assert items with 'awaitItem()', 'awaitError()', or 'ensureAllEventsConsumed()'.",
                "code": """// Production ViewModel Flow Unit Test with Turbine
@Test
fun `loadTransactions emits Loading then Success`() = runTest {
    // Arrange
    val mockTransactions = listOf(Transaction("1", 50.0))
    coEvery { repository.getTransactions() } returns Result.success(mockTransactions)
    val viewModel = TransactionsViewModel(repository)

    // Act & Assert via Turbine
    viewModel.uiState.test {
        // Initial state
        assertThat(awaitItem()).isEqualTo(TransactionsUiState.Loading)

        // Trigger action
        viewModel.loadData()

        // Verify state progression
        val successState = awaitItem() as TransactionsUiState.Success
        assertThat(successState.items).hasSize(1)

        // Ensure no unexpected emissions
        cancelAndConsumeRemainingEvents()
    }
}""",
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
                "keyPoints": ["StandardTestDispatcher queues work and requires manual time advancement", "UnconfinedTestDispatcher executes eagerly until suspension", "Use Standard for delays, retries, and execution order", "Use Unconfined for simple synchronous-like flow assertions"],
                "pitfalls": ["Assuming runTest executes coroutines concurrently on background threads", "Mixing up advanceUntilIdle with advanceTimeBy"]
            }
        ]
    })

    # ==============================================================================
    # TOPIC 12: AOSP System Internals & On-Device AI
    # ==============================================================================
    topics.append({
        "id": "topic-12",
        "num": "12",
        "title": "AOSP System Internals & On-Device AI",
        "icon": "🤖",
        "badge": "AOSP & AI",
        "desc": "Master Binder IPC kernel mechanics, Zygote fork Copy-on-Write, AIDL oneway, on-device Gemini Nano (AICore) vs Cloud routing, and Agentic ReAct safety guardrails.",
        "subtopics": [
            {
                "title": "Binder IPC Kernel Mechanics & AIDL 'oneway'",
                "what": "Binder is Android's kernel-mediated IPC driver (/dev/binder). Unlike traditional Linux IPC that requires 2 data copies (user -> kernel -> user), Binder uses mmap to achieve single-copy data transfer. AIDL 'oneway' marks calls as asynchronous and non-blocking for the caller.",
                "why": "Making synchronous Binder calls from the Main Thread causes ANRs if the remote service is slow. Furthermore, high-frequency IPC callbacks (like 50Hz CAN bus telemetry in automotive) can exhaust the 15-thread Binder thread pool if synchronous.",
                "how": "Use AIDL 'oneway' for high-frequency callbacks. Clear caller identity using 'Binder.clearCallingIdentity()' in system services before accessing internal resources to prevent privilege escalation. Pass large payloads via MemoryFile/Ashmem, not Parcel (1MB limit).",
                "code": """// AIDL Interface for Automotive IVI Telemetry
// IVehicleTelemetryService.aidl
interface IVehicleTelemetryService {
    // oneway: non-blocking, returns immediately without waiting for server response
    oneway void registerSpeedCallback(in ISpeedCallback callback);
    oneway void unregisterSpeedCallback(in ISpeedCallback callback);

    VehicleSnapshot getVehicleSnapshot(); // Synchronous call
}

// Privileged System Service with Identity Management
class VehicleTelemetryService : IVehicleTelemetryService.Stub() {
    override fun getVehicleSnapshot(): VehicleSnapshot {
        // Enforce permission
        mContext.enforceCallingPermission("com.oem.permission.VEHICLE_DATA", "getSnapshot")

        // Clear caller identity to run subsequent calls with system privileges
        val token = Binder.clearCallingIdentity()
        return try {
            hardwareHal.readCanBusSnapshot()
        } finally {
            Binder.restoreCallingIdentity(token) // MUST restore in finally block!
        }
    }
}""",
                "realworld": "In Android Automotive (AAOS), high-frequency speed and sensor telemetry streams from native vehicle HALs to the Android HMI use oneway Binder calls with RemoteCallbackList to ensure zero UI thread stalls."
            },
            {
                "title": "On-Device AI (Gemini Nano) vs Cloud AI: Privacy Routing & Safety",
                "what": "On-device AI executes models (Gemini Nano via Android AICore) directly on the local NPU/GPU without network transit. Cloud AI (Gemini Flash/Pro) executes on remote servers. An AI Router enforces data classification: Protected Health Information (PHI) and PII must strictly route on-device.",
                "why": "Sending sensitive patient data or raw banking credentials to cloud LLMs violates HIPAA, GDPR, and PCI-DSS compliance, incurring legal penalties.",
                "how": "Implement an AIRouter that inspects data classification. If the request contains PHI or PII, enforce on-device execution; if on-device inference is unsupported on the hardware, gracefully disable the feature rather than leaking data to cloud endpoints.",
                "code": """// Privacy-Preserving AI Routing Engine
class AIRouter @Inject constructor(
    private val onDeviceNanoEngine: OnDeviceGeminiNanoEngine,
    private val cloudGeminiEngine: CloudGeminiEngine
) {
    suspend fun processUserRequest(request: AIRequest): Result<String> {
        return when (request.dataClassification) {
            DataClassification.CONTAINS_PHI, DataClassification.CONTAINS_PII -> {
                // STRICT COMPLIANCE RULE: Must run locally on device!
                if (onDeviceNanoEngine.isHardwareSupported()) {
                    onDeviceNanoEngine.infer(request.sanitizedPrompt)
                } else {
                    Result.failure(SecurityException("Hardware does not support on-device AI required for sensitive data."))
                }
            }
            DataClassification.PUBLIC_OR_ANONYMIZED -> {
                // Safe to route to high-capacity Cloud Gemini
                cloudGeminiEngine.infer(request.sanitizedPrompt)
            }
        }
    }
}""",
                "realworld": "In healthcare telemedicine apps, clinical note summarization containing patient diagnostic codes runs exclusively via on-device Gemini Nano, guaranteeing zero PHI leakage to external cloud APIs."
            }
        ],
        "quizQuestions": [
            {
                "id": "q12-1",
                "question": "What is the purpose of Binder.clearCallingIdentity() and Binder.restoreCallingIdentity()? What security vulnerability occurs if restoreCallingIdentity is omitted?",
                "difficulty": "Lead / Staff",
                "thinkPrompt": "Think about Linux UIDs, privilege escalation, and thread-local Binder state across reused thread pools.",
                "principalAnswer": "When a client app (e.g. UID 10045) makes an IPC call to a system service running in system_server (UID 1000), the Binder driver sets the calling UID on that thread to 10045. If the system service subsequently calls another system service or accesses local databases, those downstream calls would be evaluated against client UID 10045 (which may lack necessary permissions).\n\n'Binder.clearCallingIdentity()' clears the thread's calling identity and returns a token, resetting the effective UID to the system service's own UID (1000), allowing it to complete privileged internal operations.\n\nCRITICAL SECURITY BUG: If 'Binder.restoreCallingIdentity(token)' is omitted (e.g. bypassed by an unhandled exception), the Binder thread remains permanently elevated with UID 1000! When that thread returns to the Binder thread pool and handles a future IPC call from another unprivileged third-party app, that app's request executes with system privileges—a catastrophic privilege escalation vulnerability. Hence, 'restoreCallingIdentity' must ALWAYS be executed in a 'finally' block.",
                "keyPoints": ["Binder records caller UID in thread-local storage", "clearCallingIdentity elevates execution to service's own UID", "restoreCallingIdentity resets identity back to caller", "Must be inside a finally block to prevent privilege escalation via thread pool reuse"],
                "pitfalls": ["Not placing restoreCallingIdentity in a finally block", "Thinking clearCallingIdentity changes the client process's UID"]
            }
        ]
    })

    return topics

if __name__ == '__main__':
    print(f"Builder 9-12 loaded with {len(get_topics_9_to_12())} topics.")
