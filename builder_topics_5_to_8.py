# Module for Topics 5, 6, 7, 8

def get_topics_5_to_8():
    topics = []

    # ==============================================================================
    # TOPIC 5: Jetpack Architecture (ViewModel, Room, StateFlow, Paging)
    # ==============================================================================
    topics.append({
        "id": "topic-5",
        "num": "05",
        "title": "Jetpack Architecture (ViewModel, Room, StateFlow, Paging)",
        "icon": "🏛️",
        "badge": "Architecture",
        "desc": "Master ViewModelStore internals, StateFlow vs SharedFlow vs Channels, Room multi-table migrations, DataStore encryption, and Paging 3 RemoteMediator.",
        "subtopics": [
            {
                "title": "StateFlow vs SharedFlow vs LiveData vs Channels Comparison",
                "what": "StateFlow is a hot state-holder with replay=1 that conflates duplicate values (using equals()). SharedFlow is a hot event-emitter with configurable replay and buffer capacities. LiveData is an older lifecycle-aware observable tightly coupled to Android MainThread. Channels are hot coroutine queues designed for point-to-point single-consumer execution.",
                "why": "Using StateFlow for one-time events (like showing a Snackbar or navigating) leads to the 're-emission on rotation' bug because StateFlow replays the latest value to new collectors. Conversely, using standard SharedFlow without buffering can drop one-time events if the collector is paused in the background.",
                "how": "Use 'StateFlow' for UI State representation ('What the screen IS'). Use 'Channel' (via receiveAsFlow()) or 'SharedFlow' with zero replay for one-time events ('What HAPPENED'). Use 'repeatOnLifecycle(STARTED)' or 'collectAsStateWithLifecycle()' to collect safely.",
                "code": """// Production MVI State & Event Architecture
@HiltViewModel
class PaymentViewModel @Inject constructor(
    private val processPaymentUseCase: ProcessPaymentUseCase
) : ViewModel() {

    // 1. STATE: StateFlow for durable UI rendering (replays on rotation)
    private val _uiState = MutableStateFlow<PaymentUiState>(PaymentUiState.Idle)
    val uiState: StateFlow<PaymentUiState> = _uiState.asStateFlow()

    // 2. EVENTS: Channel for one-shot side-effects (consumed exactly once)
    private val _effectChannel = Channel<PaymentEffect>(Channel.BUFFERED)
    val effects: Flow<PaymentEffect> = _effectChannel.receiveAsFlow()

    fun submitPayment(amount: Double) {
        viewModelScope.launch {
            // update{} CAS ensures atomic thread-safe state transition
            _uiState.update { PaymentUiState.Processing }

            processPaymentUseCase(amount)
                .onSuccess { receiptId ->
                    _uiState.update { PaymentUiState.Success(receiptId) }
                    _effectChannel.send(PaymentEffect.NavigateToReceipt(receiptId))
                }
                .onFailure { error ->
                    _uiState.update { PaymentUiState.Error(error.message) }
                    _effectChannel.send(PaymentEffect.ShowToast("Payment failed: ${error.message}"))
                }
        }
    }
}""",
                "realworld": "In banking apps, when a user completes a money transfer and rotates the phone, a StateFlow holding an 'ApprovedDialog' state would trigger the dialog again unless reset. Modeling dialogs and navigation events as a Channel guarantees zero duplicate actions."
            },
            {
                "title": "Room Multi-Table Relational Schema & Safe Migrations",
                "what": "Room is an abstraction layer over SQLite. It maps Kotlin data classes to SQL tables (@Entity), models 1-to-1, 1-to-many (@Relation), and many-to-many (@Junction) relationships, and manages database schema upgrades via Migration objects.",
                "why": "Failing to handle database schema migrations properly in production leads to fatal 'IllegalStateException: Room cannot verify data integrity', causing instant crashes on app launch for all updating users. Using fallbackToDestructiveMigration() wipes out user data.",
                "how": "Always export schema ('exportSchema = true'). Write deterministic 'Migration(startVersion, endVersion)' classes with exact SQL statements. Validate every migration in your CI pipeline using 'MigrationTestHelper'.",
                "code": """// Production Room Entity with 1-to-Many Relationship
@Entity(tableName = "bank_accounts")
data class AccountEntity(
    @PrimaryKey val accountId: String,
    val iban: String,
    val currency: String,
    val balance: Double
)

@Entity(
    tableName = "transactions",
    foreignKeys = [
        ForeignKey(
            entity = AccountEntity::class,
            parentColumns = ["accountId"],
            childColumns = ["accountOwnerId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index(value = ["accountOwnerId"]), Index(value = ["timestamp"])]
)
data class TransactionEntity(
    @PrimaryKey val txnId: String,
    val accountOwnerId: String,
    val amount: Double,
    val timestamp: Long
)

// Deterministic Non-Destructive Migration
val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(db: SupportSQLiteDatabase) {
        // Add encrypted metadata column with default empty string
        db.execSQL("ALTER TABLE transactions ADD COLUMN encrypted_tag TEXT NOT NULL DEFAULT ''")
        // Create an index for accelerated timestamp queries
        db.execSQL("CREATE INDEX IF NOT EXISTS index_transactions_timestamp ON transactions(timestamp)")
    }
}""",
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
                "keyPoints": ["Room identity hash mismatch in room_master_table", "IllegalStateException crash on startup", "fallbackToDestructiveMigration wipes all tables", "MigrationTestHelper verifies schema transitions in CI"],
                "pitfalls": ["Suggesting fallbackToDestructiveMigration as a production solution", "Not knowing where Room stores its schema identity hash"]
            }
        ]
    })

    # ==============================================================================
    # TOPIC 6: Networking & Third-Party Libraries (Retrofit, OkHttp, Coil)
    # ==============================================================================
    topics.append({
        "id": "topic-6",
        "num": "06",
        "title": "Networking & Third-Party Libraries (Retrofit, OkHttp, Coil)",
        "icon": "🌐",
        "badge": "Networking",
        "desc": "Master Retrofit 2 API architectures, OkHttp Authenticator mutex locking (preventing 401 refresh storms), offline caching, and Coil image decoding pipelines.",
        "subtopics": [
            {
                "title": "Thread-Safe 401 Token Refresh with OkHttp Authenticator & Mutex",
                "what": "When multiple concurrent network calls receive an HTTP 401 Unauthorized simultaneously, OkHttp's 'Authenticator' triggers. Without synchronization, all concurrent threads initiate duplicate token refresh requests, invalidating one another and logging the user out.",
                "why": "A banking dashboard loading 5 parallel endpoints (Balance, Transactions, Cards, Notifications, Offers) will encounter 5 simultaneous 401s if the token expired. Calling the refresh endpoint 5 times in parallel triggers race conditions and security rate limits.",
                "how": "Implement OkHttp's 'Authenticator'. Use a synchronized lock or Mutex. Check if another thread has ALREADY refreshed the token before making the network call. Update the failed request with the new Authorization header.",
                "code": """// Production-Grade Thread-Safe Token Refresh Authenticator
class TokenAuthenticator @Inject constructor(
    private val tokenStorage: TokenStorage,
    private val authApiProvider: Provider<AuthApiService> // Provider breaks circular dependency
) : Authenticator {

    private val lock = Any()

    override fun authenticate(route: Route?, response: Response): Request? {
        // Prevent infinite retry loop if refresh token itself failed
        if (responseCount(response) >= 3) return null

        val currentAccessToken = tokenStorage.getAccessToken()

        synchronized(lock) {
            val updatedAccessToken = tokenStorage.getAccessToken()

            // If another thread already refreshed the token while this thread waited, use it!
            val tokenToUse = if (updatedAccessToken != currentAccessToken && updatedAccessToken != null) {
                updatedAccessToken
            } else {
                // Actually perform the synchronous refresh call
                val refreshToken = tokenStorage.getRefreshToken() ?: return null
                val refreshResponse = authApiProvider.get().refreshTokenDirect(refreshToken).execute()

                if (refreshResponse.isSuccessful && refreshResponse.body() != null) {
                    val newTokens = refreshResponse.body()!!
                    tokenStorage.saveTokens(newTokens.accessToken, newTokens.refreshToken)
                    newTokens.accessToken
                } else {
                    tokenStorage.clearTokens()
                    EventBus.post(SessionExpiredEvent)
                    return null
                }
            }

            // Retry the failed original request with the fresh token
            return response.request.newBuilder()
                .header("Authorization", "Bearer $tokenToUse")
                .build()
        }
    }

    private fun responseCount(response: Response): Int {
        var count = 1
        var prior = response.priorResponse
        while (prior != null) {
            count++
            prior = prior.priorResponse
        }
        return count
    }
}""",
                "realworld": "In all financial banking and payment apps, the synchronized Authenticator pattern is mandatory to prevent token invalidation races and session dropouts when users unlock their device after a token expiry window."
            },
            {
                "title": "Offline-First HTTP Caching with OkHttp Cache & Interceptors",
                "what": "OkHttp includes a disk Cache implementation that obeys HTTP cache-control headers. By combining an Application Interceptor and a Network Interceptor, you can enforce offline caching even if the server does not send proper cache-control headers.",
                "why": "Allows users with flaky subway connections to view previously fetched accounts, product catalogs, or medical summaries with zero network latency.",
                "how": "Set up a 50MB disk Cache in OkHttp.Builder(). In the offline interceptor, check network connectivity; if offline, add 'Cache-Control: public, only-if-cached, max-stale=...'. In the network interceptor, rewrite response cache headers.",
                "code": """// Offline Caching OkHttp Setup
val cacheSize = 50L * 1024L * 1024L // 50 MB
val httpCache = Cache(File(context.cacheDir, "http_cache"), cacheSize)

val offlineCacheInterceptor = Interceptor { chain ->
    var request = chain.request()
    if (!networkMonitor.isOnline()) {
        val maxStale = 60 * 60 * 24 * 7 // Tolerate 7-day stale cache when offline
        request = request.newBuilder()
            .header("Cache-Control", "public, only-if-cached, max-stale=$maxStale")
            .removeHeader("Pragma")
            .build()
    }
    chain.proceed(request)
}

val okHttpClient = OkHttpClient.Builder()
    .cache(httpCache)
    .addInterceptor(offlineCacheInterceptor)
    .build()""",
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
                "keyPoints": ["Application interceptors run once, outside Cache and redirects", "Network interceptors run per-wire-transmission, bypassed on cache hits", "Auth headers go in Application Interceptor", "Response Cache-Control rewriting goes in Network Interceptor"],
                "pitfalls": ["Placing logging or caching rewrite in the wrong interceptor type", "Not knowing that Network Interceptors are skipped when served from cache"]
            }
        ]
    })

    # ==============================================================================
    # TOPIC 7: Dependency Injection (Hilt, Dagger 2, Koin)
    # ==============================================================================
    topics.append({
        "id": "topic-7",
        "num": "07",
        "title": "Dependency Injection (Hilt, Dagger 2, Koin)",
        "icon": "💉",
        "badge": "DI",
        "desc": "Master Hilt component hierarchies, @Binds vs @Provides bytecode generation, multibindings for plugin architectures, and test isolation with @UninstallModules.",
        "subtopics": [
            {
                "title": "Hilt Component Hierarchy & Scoping Rules",
                "what": "Hilt provides predefined DI components tied to Android lifecycle stages: SingletonComponent (Application), ActivityRetainedComponent (survives rotation), ActivityComponent, ViewModelComponent, FragmentComponent, and ViewComponent.",
                "why": "Prevents memory leaks by strictly disallowing shorter-lived dependencies (e.g. Activity context) from being injected into longer-lived scopes (e.g. Singleton). The compiler validates the graph at build-time.",
                "how": "Inject @ApplicationContext into Singletons. Bind ViewModels to @ViewModelScoped or unscoped. Use @ActivityScoped only for objects that need an Activity Context (e.g. dialog builders or Navigator implementations).",
                "code": """// Hilt Component Binding Architecture
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    // @Binds is abstract and generates zero bytecode wrapper classes
    @Binds
    @Singleton
    abstract fun bindAccountRepository(impl: AccountRepositoryImpl): AccountRepository
}

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    // @Provides is used when constructor logic is required
    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit =
        Retrofit.Builder()
            .baseUrl("https://api.bank.com")
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create())
            .build()
}""",
                "realworld": "In large modular Android apps, using @Binds instead of @Provides eliminates hundreds of generated Factory classes, shaving 15-25% off build times across multi-module projects."
            },
            {
                "title": "Multibindings (@IntoMap, @IntoSet) for Strategy Patterns",
                "what": "Dagger Multibindings allow you to inject a collection (Set or Map) of implementations without hardcoding them in the consumer. Modules contribute bindings into a central map using a custom @MapKey.",
                "why": "Enforces the Open/Closed Principle (OCP). You can add new payment methods, analytics providers, or FHIR handlers in independent Gradle modules without touching the central processor class.",
                "how": "Define a custom @MapKey annotation. Bind implementations using '@IntoMap' and the key annotation. Inject 'Map<PaymentType, Provider<PaymentStrategy>>' into the consumer.",
                "code": """// Strategy Pattern via Dagger Multibindings
enum class PaymentType { CREDIT_CARD, UPI, CRYPTO }

@MapKey
annotation class PaymentTypeKey(val value: PaymentType)

@Module
@InstallIn(SingletonComponent::class)
abstract class PaymentStrategiesModule {
    @Binds
    @IntoMap
    @PaymentTypeKey(PaymentType.CREDIT_CARD)
    abstract fun bindCardStrategy(impl: CardPaymentStrategy): PaymentStrategy

    @Binds
    @IntoMap
    @PaymentTypeKey(PaymentType.UPI)
    abstract fun bindUpiStrategy(impl: UpiPaymentStrategy): PaymentStrategy
}

// Consuming Processor: Zero when/switch statements needed!
@Singleton
class PaymentProcessor @Inject constructor(
    private val strategies: Map<PaymentType, @JvmSuppressWildcards Provider<PaymentStrategy>>
) {
    fun process(type: PaymentType, amount: Double) {
        val strategy = strategies[type]?.get()
            ?: throw UnsupportedOperationException("Unsupported payment type")
        strategy.pay(amount)
    }
}""",
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
                "keyPoints": ["@Provides generates a separate Factory class", "@Binds is abstract and generates zero wrapper code", "@Binds points directly to the @Inject constructor", "Prefer @Binds for compile-time efficiency"],
                "pitfalls": ["Using @Provides for simple interface-to-implementation mapping", "Not knowing that @Binds modules must be abstract classes or interfaces"]
            }
        ]
    })

    # ==============================================================================
    # TOPIC 8: Architecture & Design Patterns (Clean Architecture, MVI)
    # ==============================================================================
    topics.append({
        "id": "topic-8",
        "num": "08",
        "title": "Architecture & Design Patterns (Clean Architecture, MVI)",
        "icon": "📐",
        "badge": "Clean Arch",
        "desc": "Master Clean Architecture layer boundaries, Domain purity, MVI state machines, the :api/:impl multi-module pattern, and the Strangler Fig migration strategy.",
        "subtopics": [
            {
                "title": "Clean Architecture Layer Boundaries & Inward Dependency Rule",
                "what": "Clean Architecture structures the codebase into concentric layers: Presentation (UI, Composables, ViewModels), Domain (UseCases, Pure Business Entities), and Data (Repositories, Room DAOs, Retrofit API DTOs). Dependencies strictly point inward toward Domain.",
                "why": "Domain contains the core business rules that define your business. It must have ZERO dependencies on Android framework classes (android.content.Context, androidx.lifecycle, Room annotations). This guarantees that business logic can be tested with lightning-fast JVM unit tests without emulators and survives framework deprecations.",
                "how": "Define repository interfaces in Domain; implement them in Data. Data DTOs (Retrofit/Room models) must NEVER leak into Domain or Presentation; map them at the repository boundary into immutable Domain entities.",
                "code": """// Pure Domain Layer (Zero Android Framework Imports)
package com.bank.domain.model

data class Account(
    val id: String,
    val balance: Double,
    val currency: String
) {
    // Business rules belong in Domain Entities!
    fun canWithdraw(amount: Double): Boolean = balance >= amount && amount > 0.0
}

interface AccountRepository {
    suspend fun getAccount(id: String): Result<Account>
}

class TransferFundsUseCase @Inject constructor(
    private val repo: AccountRepository,
    private val auditLogger: DomainAuditLogger
) {
    suspend operator fun invoke(fromId: String, amount: Double): Result<Unit> {
        val account = repo.getAccount(fromId).getOrElse { return Result.failure(it) }
        if (!account.canWithdraw(amount)) {
            return Result.failure(InsufficientFundsException())
        }
        return repo.executeTransfer(fromId, amount)
    }
}""",
                "realworld": "In banking and medical apps with multi-year lifecycles, isolating domain business logic guarantees that migrating from XML to Compose, or from Retrofit to Ktor, requires zero changes to core business use cases."
            },
            {
                "title": "The :api / :impl Multi-Module Scaling Architecture",
                "what": "In large enterprise apps, feature modules are split into two Gradle subprojects: ':feature:X:api' (public interface, navigation contracts, and shared domain models) and ':feature:X:impl' (private ViewModels, Composables, and internal repositories).",
                "why": "Prevents circular dependencies between features and prevents 'Feature Team A breaks Feature Team B'. Other features depend ONLY on ':api'. Changes inside ':impl' trigger incremental compilation for THAT module only, rather than recompiling the entire app.",
                "how": "Feature Y adds 'implementation(project(\":feature:X:api\"))' in build.gradle.kts. Only the ':app' module depends on ':feature:X:impl' to wire Dagger/Hilt bindings together.",
                "code": """// :feature:payments:api (Public Contract)
interface PaymentsNavigator {
    fun openPaymentConfirmation(amount: Double, recipientId: String)
}

// :feature:payments:impl (Private Implementation)
class PaymentsNavigatorImpl @Inject constructor(
    private val navController: NavController
) : PaymentsNavigator {
    override fun openPaymentConfirmation(amount: Double, recipientId: String) {
        navController.navigate("payment_confirm/$amount/$recipientId")
    }
}

// build.gradle.kts of :feature:accounts:impl
dependencies {
    implementation(project(":feature:payments:api")) // ✅ ONLY depends on API
    // implementation(project(":feature:payments:impl")) // ❌ STRICTLY FORBIDDEN
}""",
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
                "keyPoints": [":api contract extraction to decouple compile dependencies", "Inversion of control via Hilt in the :app module", "Uri-based Deep Linking across module boundaries", "Zero direct :impl to :impl dependencies"],
                "pitfalls": ["Creating circular dependencies in Gradle", "Using reflection to start activities by string name"]
            }
        ]
    })

    return topics

if __name__ == '__main__':
    print(f"Builder 5-8 loaded with {len(get_topics_5_to_8())} topics.")
