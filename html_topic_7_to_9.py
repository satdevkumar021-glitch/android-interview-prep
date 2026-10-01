# Generator for Topics 7, 8, 9

def get_topics_7_to_9_html():
    return """
    <!-- ============================================= -->
    <!-- TOPIC 7: DEPENDENCY INJECTION (HILT & DAGGER) -->
    <!-- ============================================= -->
    <section class="topic-section" id="topic-7">
      <div class="topic-header">
        <span class="topic-number">07</span>
        <h1>Dependency Injection (Hilt, Dagger 2, Koin)</h1>
        <p class="topic-desc">Hilt component scoping hierarchy, @Binds vs @Provides bytecode generation, Dagger multibindings for Strategy patterns, and test isolation.</p>
        <div class="topic-tags">
          <span class="tag tag-architecture">Hilt</span>
          <span class="tag tag-kotlin">Dagger 2</span>
          <span class="tag tag-performance">Senior / Staff</span>
        </div>
      </div>

      <!-- Subtopic 7.1 -->
      <div class="subtopic" id="subtopic-7-1">
        <h2>7.1 @Binds vs @Provides Bytecode Generation & Compile Times</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p>In Dagger and Hilt, <code>@Provides</code> is a concrete method containing manual instantiation code. For every <code>@Provides</code> method, the Dagger annotation processor generates a separate synthetic Factory class (e.g. <code>NetworkModule_ProvideRetrofitFactory</code>). <code>@Binds</code> is an abstract method that binds an existing implementation class with an <code>@Inject</code> constructor to an interface, generating ZERO wrapper classes.</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> Using <code>@Provides</code> for simple interface-to-implementation mappings generates hundreds of redundant Java/Kotlin classes during compilation, drastically increasing build times, APK DEX method counts, and classloader memory overhead.</p>
          <ul>
            <li><strong>Accelerates Incremental Compilation:</strong> Eliminates factory class generation, speeding up clean and incremental builds by up to 25%.</li>
            <li><strong>Enforces Inversion of Control:</strong> Cleanly decouples interface consumers from concrete implementations.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>// 1. @Binds in an abstract module (Zero bytecode wrapper overhead!)
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindAccountRepository(
        impl: AccountRepositoryImpl // Implementation MUST have @Inject constructor
    ): AccountRepository
}

// 2. @Provides in an object module (Used ONLY when custom construction is required)
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.bank.com")
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create())
            .build()
    }
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>Enterprise Multi-Module App:</strong> In an app with 40+ Gradle feature modules and 300+ repositories, converting all legacy <code>@Provides</code> repository bindings to <code>@Binds</code> eliminated over 450 generated factory classes, cutting CI pipeline build times by 3.5 minutes per pull request.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "I always recommend <code>@Binds</code> over <code>@Provides</code> whenever possible. <code>@Provides</code> is a concrete method where Dagger must generate a corresponding <code>Factory</code> class to call your method at runtime. <code>@Binds</code> is abstract—it contains no bytecode. Dagger simply points the dependency graph directly to the implementation class's <code>@Inject</code> constructor. I only use <code>@Provides</code> when instantiating third-party classes like Room, Retrofit, or OkHttpClient where I cannot modify the constructor."
          </div>
        </div>
      </div>

      <!-- Subtopic 7.2 -->
      <div class="subtopic" id="subtopic-7-2">
        <h2>7.2 Dagger Multibindings (@IntoMap, @IntoSet) for Strategy Patterns</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p>Dagger Multibindings allow independent modules to contribute entries into a central collection (<code>Set&lt;T&gt;</code> or <code>Map&lt;K, V&gt;</code>) without the consumer knowing about the concrete implementations at compile-time.</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> Violates the Open/Closed Principle (OCP). Without multibindings, a central payment processor needs a giant <code>when(type)</code> block that imports every payment implementation, creating tight coupling across modules.</p>
          <ul>
            <li><strong>True Feature Pluggability:</strong> New features can register themselves into core payment, analytics, or routing maps without modifying core modules.</li>
            <li><strong>Lazy Initialization:</strong> Injecting <code>Map&lt;K, Provider&lt;V&gt;&gt;</code> delays instantiation of heavyweight SDKs until they are actually invoked by the user.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>// 1. Define custom MapKey
enum class PaymentType { CREDIT_CARD, UPI, CRYPTO }

@MapKey
annotation class PaymentTypeKey(val value: PaymentType)

// 2. Feature modules contribute bindings into the central map
@Module
@InstallIn(SingletonComponent::class)
abstract class PaymentStrategiesModule {
    @Binds
    @IntoMap
    @PaymentTypeKey(PaymentType.CREDIT_CARD)
    abstract fun bindCard(impl: CardPaymentStrategy): PaymentStrategy

    @Binds
    @IntoMap
    @PaymentTypeKey(PaymentType.UPI)
    abstract fun bindUpi(impl: UpiPaymentStrategy): PaymentStrategy
}

// 3. Central Processor consumes the Map with ZERO when-statements!
@Singleton
class PaymentProcessor @Inject constructor(
    private val strategies: Map<PaymentType, @JvmSuppressWildcards Provider<PaymentStrategy>>
) {
    fun process(type: PaymentType, amount: Double) {
        val strategy = strategies[type]?.get()
            ?: throw UnsupportedOperationException("Unsupported payment type: $type")
        strategy.pay(amount)
    }
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>FinTech SuperApp:</strong> A global banking application supports 12 regional payment gateways (Apple Pay, Google Pay, UPI, Pix, Klarna). Feature teams build their gateways in isolated Gradle modules. Multibindings allow each module to plug into the checkout pipeline without modifying the core checkout repository.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "I use Dagger Multibindings to enforce the Open/Closed Principle. Instead of writing a fragile <code>when</code> statement in my payment or analytics orchestrator, I declare a custom <code>@MapKey</code>. Feature modules use <code>@IntoMap</code> to contribute their implementation into the graph. The processor injects <code>Map&lt;PaymentType, Provider&lt;PaymentStrategy&gt;&gt;</code>. Notice the <code>Provider</code>: this ensures heavyweight payment SDKs are not initialized at app startup—they are lazily instantiated only when the user selects that specific payment method."
          </div>
        </div>
      </div>

      <!-- Q&A Section -->
      <div class="qa-section">
        <h2>🎯 Senior/Lead Interview Q&A (Dependency Injection)</h2>

        <div class="qa-item" data-difficulty="basic">
          <div class="qa-question">
            <span class="qa-number">Q1</span>
            <span class="badge badge-basic">Basic</span>
            <p>Compare Hilt vs Dagger 2 vs Koin. What are the key architectural trade-offs?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> <strong>Dagger 2</strong> is a pure compile-time annotation processor that generates strict static code, providing compile-time verification and zero runtime reflection overhead, but with high boilerplate. <strong>Hilt</strong> is built on top of Dagger: it standardizes Android component lifecycles (<code>SingletonComponent</code>, <code>ViewModelComponent</code>) and eliminates boilerplate while preserving compile-time safety. <strong>Koin</strong> is a runtime service locator using Kotlin DSL: it has zero code generation and fast build times, but dependency resolution crashes happen at RUNTIME rather than compile-time.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="advanced">
          <div class="qa-question">
            <span class="qa-number">Q2</span>
            <span class="badge badge-advanced">Advanced</span>
            <p>What happens if you inject an @ActivityScoped dependency into a @Singleton component?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> Dagger/Hilt detects this at <strong>compile-time</strong> and fails the build with a scoping error: <code>[Dagger/IncompatiblyScopedBindings]</code>! An Activity has a shorter lifespan than the Singleton (Application) scope. If a Singleton held a reference to an ActivityScoped dependency, the Activity instance would be permanently retained across screen closures, creating a massive memory leak of the Activity, its View hierarchy, and Bitmaps.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="advanced">
          <div class="qa-question">
            <span class="qa-number">Q3</span>
            <span class="badge badge-advanced">Advanced</span>
            <p>How does Hilt generate code under the hood? What is the role of @HiltAndroidApp?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> <code>@HiltAndroidApp</code> triggers Hilt's code generator to create a base Application class (e.g. <code>Hilt_MyApplication</code>) that implements <code>GeneratedComponentManager</code>. This class instantiates and retains the root Dagger component (<code>SingletonComponent</code>). Hilt uses bytecode transformation (via the Gradle plugin) to rewrite your application, activities, and fragments to extend their generated Hilt base classes, automatically injecting dependencies in <code>onCreate()</code> or <code>onAttach()</code>.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="scenario">
          <div class="qa-number">Q4</div>
          <div class="qa-question">
            <span class="badge badge-scenario">Scenario</span>
            <p>How do you inject dynamic runtime arguments (like an account ID passed from a bundle) into a ViewModel with Hilt?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> Use <strong>SavedStateHandle</strong> or <strong>Assisted Injection</strong>. Hilt automatically injects <code>SavedStateHandle</code> into <code>@HiltViewModel</code> constructors, which contains all navigation arguments passed to the destination. For non-ViewModel classes requiring dynamic runtime arguments alongside injected singletons, use <code>@AssistedInject</code> on the constructor and define an <code>@AssistedFactory</code> interface.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="scenario">
          <div class="qa-number">Q5</div>
          <div class="qa-question">
            <span class="badge badge-scenario">Scenario</span>
            <p>How do you mock dependencies in Hilt instrumented tests without polluting production code?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> Annotate the test class with <code>@HiltAndroidTest</code> and <code>@UninstallModules(ProductionNetworkModule::class)</code>. In the test class or test source set, define a replacement test module: <code>@Module @TestInstallIn(components = [SingletonComponent::class], replaces = [ProductionNetworkModule::class])</code> that provides mock or fake implementations of the repository/network service.</p>
          </div>
        </div>
      </div>

      <!-- Checklist -->
      <div class="topic-progress-tracker">
        <h3>✅ Topic 7 Mastery Checklist</h3>
        <label class="progress-check"><input type="checkbox" data-topic="7" data-item="0"> @Binds vs @Provides bytecode & factory differences</label>
        <label class="progress-check"><input type="checkbox" data-topic="7" data-item="1"> Dagger Multibindings (@IntoMap, @MapKey) for Strategy patterns</label>
        <label class="progress-check"><input type="checkbox" data-topic="7" data-item="2"> Component scoping hierarchy and memory leak prevention</label>
        <label class="progress-check"><input type="checkbox" data-topic="7" data-item="3"> Assisted Injection (@AssistedInject, @AssistedFactory)</label>
        <label class="progress-check"><input type="checkbox" data-topic="7" data-item="4"> Answered & Mastered all 5 Topic 7 Q&As</label>
      </div>
    </section>

    <!-- ============================================= -->
    <!-- TOPIC 8: ARCHITECTURE PATTERNS (MVP, MVVM, MVI)-->
    <!-- ============================================= -->
    <section class="topic-section" id="topic-8">
      <div class="topic-header">
        <span class="topic-number">08</span>
        <h1>Architecture Patterns: MVP vs MVVM vs MVI & Clean Architecture</h1>
        <p class="topic-desc">Evolution from legacy MVP to modern MVVM and MVI, Clean Architecture layer boundaries, Domain purity, and the :api/:impl multi-module pattern.</p>
        <div class="topic-tags">
          <span class="tag tag-architecture">Clean Architecture</span>
          <span class="tag tag-compose">MVI</span>
          <span class="tag tag-performance">Senior / Staff</span>
        </div>
      </div>

      <!-- Subtopic 8.1 -->
      <div class="subtopic" id="subtopic-8-1">
        <h2>8.1 Evolution of Android UI Patterns: MVP vs MVVM vs MVI</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p>Android UI architecture has evolved through three major paradigms:
          <strong>MVP (Model-View-Presenter)</strong>: 1-to-1 tight coupling via interface callbacks; Presenter explicitly commands the View (<code>view.showLoading()</code>, <code>view.hideLoading()</code>).
          <strong>MVVM (Model-View-ViewModel)</strong>: Decoupled via observables (LiveData/StateFlow); View observes state changes from ViewModel.
          <strong>MVI (Model-View-Intent)</strong>: Unidirectional Data Flow (UDF) with a single, immutable state model (<code>UiState</code>) driven by user intentions (<code>UiIntent</code>).</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem with MVP:</strong> In MVP, the Presenter holds a direct reference to the View interface. If an asynchronous network call finishes after the Activity is destroyed or rotated, calling <code>view.displayData()</code> triggers a NullPointerException or leaks the Activity. Furthermore, state is scattered across multiple mutable variables, making state reproduction impossible.</p>
          <ul>
            <li><strong>Why Industry Moved to MVVM:</strong> ViewModels have zero references to Views and survive configuration changes, eliminating lifecycle leaks.</li>
            <li><strong>Why Modern Apps Choose MVI:</strong> Single Source of Truth! In complex screens (like payment checkout), having 6 different LiveDatas updating asynchronously leads to race conditions and invalid intermediate UI states. MVI guarantees deterministic, predictable UI transitions.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>// 1. MVI Contract Definition (Single Source of Truth)
sealed interface PaymentIntent {
    data class EnterAmount(val amount: Double) : PaymentIntent
    object SubmitPayment : PaymentIntent
    object DismissError : PaymentIntent
}

@Immutable
data class PaymentUiState(
    val amount: Double = 0.0,
    val isLoading: Boolean = false,
    val transactionId: String? = null,
    val errorMessage: String? = null
)

// 2. MVI ViewModel (Unidirectional Data Flow)
@HiltViewModel
class PaymentMviViewModel @Inject constructor(
    private val transferUseCase: ExecuteTransferUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(PaymentUiState())
    val uiState: StateFlow<PaymentUiState> = _uiState.asStateFlow()

    // Single entry point for all user interactions
    fun processIntent(intent: PaymentIntent) {
        when (intent) {
            is PaymentIntent.EnterAmount -> {
                _uiState.update { it.copy(amount = intent.amount) }
            }
            is PaymentIntent.SubmitPayment -> executePayment()
            is PaymentIntent.DismissError -> {
                _uiState.update { it.copy(errorMessage = null) }
            }
        }
    }

    private fun executePayment() {
        val currentAmount = _uiState.value.amount
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            transferUseCase(currentAmount)
                .onSuccess { txnId ->
                    _uiState.update { it.copy(isLoading = false, transactionId = txnId) }
                }
                .onFailure { error ->
                    _uiState.update { it.copy(isLoading = false, errorMessage = error.message) }
                }
        }
    }
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>FinTech Trading Platform:</strong> In crypto and stock trading apps where market prices, user balances, limit orders, and order book depths update asynchronously 10 times per second, MVI's single immutable <code>UiState</code> ensures the UI never displays a desynchronized state (e.g. showing a successful trade banner with an outdated balance).</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "I walk interviewers through the architectural progression: In <strong>MVP</strong>, the Presenter explicitly told the View what to do via callbacks (<code>view.showProgress()</code>), which tightly coupled them and required defensive <code>isViewAttached()</code> checks to prevent lifecycle leaks. <strong>MVVM</strong> decoupled the View via observables, allowing Views to observe independent streams. However, as screens grew complex, having 10 distinct LiveDatas created inconsistent intermediate states. <strong>MVI</strong> solves this by introducing Unidirectional Data Flow: a single immutable <code>UiState</code>, sealed <code>UiIntent</code> commands, and one-shot <code>UiEffect</code> events. I choose MVI for mission-critical screens like checkout or trading where state determinism is paramount."
          </div>
        </div>
      </div>

      <!-- Subtopic 8.2 -->
      <div class="subtopic" id="subtopic-8-2">
        <h2>8.2 Clean Architecture Boundaries & Domain Purity</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p>Clean Architecture structures the codebase into three concentric layers: <strong>Presentation</strong> (UI, Composables, ViewModels), <strong>Domain</strong> (UseCases, Pure Business Entities), and <strong>Data</strong> (Repositories, Room DAOs, Retrofit API DTOs). Dependencies strictly point inward toward Domain.</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> If Android framework classes (<code>Context</code>, <code>Room</code> annotations, <code>Retrofit</code> DTOs) leak into business logic, you cannot run fast local JVM unit tests, and changing a database column or network field breaks your business use cases.</p>
          <ul>
            <li><strong>Domain Layer Purity:</strong> Pure Kotlin with ZERO Android framework imports.</li>
            <li><strong>Inversion of Control:</strong> The Domain layer defines the repository interface; the Data layer implements it.</li>
            <li><strong>Mappers at Boundaries:</strong> DTOs and database entities are mapped into immutable Domain models at repository boundaries.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>// 1. Pure Domain Model (Zero Framework Imports)
package com.bank.domain.model

data class BankAccount(
    val id: String,
    val balance: Double,
    val currency: String
) {
    // Pure business rule
    fun canWithdraw(amount: Double): Boolean = balance >= amount && amount > 0.0
}

// 2. Domain Repository Interface
interface BankAccountRepository {
    suspend fun getAccount(id: String): Result<BankAccount>
}

// 3. Domain UseCase
class WithdrawFundsUseCase @Inject constructor(
    private val repo: BankAccountRepository,
    private val auditLogger: DomainAuditLogger
) {
    suspend operator fun invoke(accountId: String, amount: Double): Result<Unit> {
        val account = repo.getAccount(accountId).getOrElse { return Result.failure(it) }
        if (!account.canWithdraw(amount)) {
            return Result.failure(InsufficientFundsException("Balance too low"))
        }
        return repo.executeWithdrawal(accountId, amount)
    }
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>Healthcare Clinical Decision Engine:</strong> In an app calculating insulin dosages based on blood glucose readings, keeping the dosage calculation use cases in a pure Kotlin Domain module allowed running 1,500 JUnit tests in 2.3 seconds on CI, completely isolated from SQLite and Android OS updates.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "The heart of Clean Architecture is the <strong>Inward Dependency Rule</strong>. The Domain layer is the core of our business and must remain pure Kotlin: no <code>android.content.Context</code>, no Room, no Retrofit. The Domain layer defines the repository interface; the Data layer implements it. If backend engineers change a JSON key from <code>user_id</code> to <code>uuid</code>, that change is absorbed by a mapper in the Data layer—our Domain models, UseCases, and ViewModels remain completely untouched."
          </div>
        </div>
      </div>

      <!-- Q&A Section -->
      <div class="qa-section">
        <h2>🎯 Senior/Lead Interview Q&A (Architecture Patterns & Clean Arch)</h2>

        <div class="qa-item" data-difficulty="basic">
          <div class="qa-question">
            <span class="qa-number">Q1</span>
            <span class="badge badge-basic">Basic</span>
            <p>What is the Dependency Inversion Principle and how is it applied in Clean Architecture?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> High-level business logic modules must not depend on low-level implementation modules; both must depend on abstractions. In Clean Architecture, the high-level <code>TransferUseCase</code> in the Domain layer does not depend on the concrete <code>AccountRepositoryImpl</code> in the Data layer. Instead, Domain declares an abstract <code>AccountRepository</code> interface. The Data layer implements this interface, inverting the dependency arrow so that all dependencies point inward toward the business core.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="advanced">
          <div class="qa-question">
            <span class="qa-number">Q2</span>
            <span class="badge badge-advanced">Advanced</span>
            <p>Why should the Domain layer have ZERO Android SDK dependencies?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> (1) <strong>Testing Velocity:</strong> Pure Kotlin code can be tested with standard JVM unit tests in milliseconds without Robolectric or Android emulators. (2) <strong>Portability:</strong> Pure Kotlin domain logic can be shared across Android and iOS via Kotlin Multiplatform (KMP). (3) <strong>Framework Independence:</strong> Prevents business rules from becoming entangled with deprecated Android APIs (like migrating from AsyncTask to Coroutines, or XML to Compose).</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="advanced">
          <div class="qa-question">
            <span class="qa-number">Q3</span>
            <span class="badge badge-advanced">Advanced</span>
            <p>What is the :api / :impl multi-module architectural pattern and what problem does it solve?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> Every feature module is split into two Gradle subprojects: <code>:feature:X:api</code> (public interface, navigation contracts, domain models) and <code>:feature:X:impl</code> (private implementation, ViewModels, UI). Other features depend ONLY on <code>:api</code>. This solves circular dependencies between features, prevents feature teams from accessing internal implementation details, and drastically speeds up Gradle incremental compilation by avoiding cascading rebuilds when internal implementation code changes.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="scenario">
          <div class="qa-number">Q4</div>
          <div class="qa-question">
            <span class="badge badge-scenario">Scenario</span>
            <p>How do you navigate between two independent feature modules in a multi-module app without creating circular Gradle dependencies?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> (1) <strong>Navigation Contract in :api:</strong> Feature B exposes an interface <code>FeatureBNavigator</code> in <code>:feature:b:api</code>. Feature A depends on <code>:feature:b:api</code> and invokes the interface. The root <code>:app</code> module, which knows all modules, binds the concrete implementation. (2) <strong>URI-Based Deep Linking:</strong> Feature A navigates via deep link (<code>app://payments/transfer?id=123</code>), completely decoupling compile-time dependencies.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="scenario">
          <div class="qa-number">Q5</div>
          <div class="qa-question">
            <span class="badge badge-scenario">Scenario</span>
            <p>Explain the Strangler Fig pattern for migrating a 5-year-old monolithic Android app to Clean Architecture multi-module.</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> Avoid big-bang rewrites! The Strangler Fig pattern incrementally replaces legacy features: (1) Create a new <code>:core</code> and <code>:feature:new_feature</code> module with Clean Architecture. (2) Build new features entirely inside the new modules. (3) When modifying legacy screens, strangle them: extract their data layer to a repository, wrap legacy activities behind a navigator interface, and port one screen at a time. The legacy monolith gradually shrinks until it is entirely strangled and deleted.</p>
          </div>
        </div>
      </div>

      <!-- Checklist -->
      <div class="topic-progress-tracker">
        <h3>✅ Topic 8 Mastery Checklist</h3>
        <label class="progress-check"><input type="checkbox" data-topic="8" data-item="0"> MVP vs MVVM vs MVI architectural trade-offs</label>
        <label class="progress-check"><input type="checkbox" data-topic="8" data-item="1"> Clean Architecture Inward Dependency Rule</label>
        <label class="progress-check"><input type="checkbox" data-topic="8" data-item="2"> Domain layer purity (zero Android SDK dependencies)</label>
        <label class="progress-check"><input type="checkbox" data-topic="8" data-item="3"> :api / :impl multi-module scaling pattern</label>
        <label class="progress-check"><input type="checkbox" data-topic="8" data-item="4"> Answered & Mastered all 5 Topic 8 Q&As</label>
      </div>
    </section>

    <!-- ============================================= -->
    <!-- TOPIC 9: CONCURRENCY & COROUTINES             -->
    <!-- ============================================= -->
    <section class="topic-section" id="topic-9">
      <div class="topic-header">
        <span class="topic-number">09</span>
        <h1>Concurrency: Coroutines, Flow & Structured Concurrency</h1>
        <p class="topic-desc">CoroutineContext, coroutineScope vs supervisorScope, Flow backpressure, repeatOnLifecycle, and unit testing asynchronous streams with Turbine.</p>
        <div class="topic-tags">
          <span class="tag tag-kotlin">Coroutines</span>
          <span class="tag tag-compose">Flow</span>
          <span class="tag tag-performance">Senior / Staff</span>
        </div>
      </div>

      <!-- Subtopic 9.1 -->
      <div class="subtopic" id="subtopic-9-1">
        <h2>9.1 Structured Concurrency: coroutineScope vs supervisorScope</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p>Structured Concurrency guarantees that coroutine lifecycles are strictly bound to a hierarchical tree: parent coroutines cannot complete until all children finish, and cancellation cascades downward. In <code>coroutineScope</code>, if ANY child fails with an unhandled exception, the entire scope immediately cancels all siblings and propagates the failure. In <code>supervisorScope</code>, children failures are isolated; a child failure does not cancel sibling coroutines.</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> In a dashboard loading Account Balance, Recent Transactions, and Promotional Banners in parallel, a 500 error from the non-critical Banners service should NOT crash the screen or cancel the critical Account Balance coroutine!</p>
          <ul>
            <li><strong>Failure Isolation:</strong> <code>supervisorScope</code> ensures partial failures in optional services do not compromise core transactional user journeys.</li>
            <li><strong>Structured Teardown:</strong> When the parent scope is cancelled (e.g. user leaves screen), all child coroutines are cleanly cancelled, preventing background resource leaks.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>// Resilient Parallel Dashboard Loading with supervisorScope
suspend fun fetchDashboardData(): DashboardResult = supervisorScope {
    // 1. Critical Balance Call
    val balanceDeferred = async { accountApi.getBalance() }
    
    // 2. Critical Transactions Call
    val txnsDeferred = async { accountApi.getTransactions() }
    
    // 3. Optional Promotional Offers Call (Failure MUST NOT cancel siblings!)
    val offersDeferred = async {
        try {
            offersApi.getOffers()
        } catch (e: Exception) {
            Timber.w(e, "Optional offers failed; returning fallback")
            emptyList<Offer>()
        }
    }

    DashboardResult(
        balance = balanceDeferred.await(),
        transactions = txnsDeferred.await(),
        offers = offersDeferred.await()
    )
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>FinTech SuperApp:</strong> A home screen launches 6 parallel requests. Using <code>supervisorScope</code> guarantees that if the localized marketing promotion or stock market widget fails, the user's core checking account balance and credit card summary still render smoothly.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "I explain structured concurrency as parent-child responsibility. In <code>coroutineScope</code>, all tasks are atomic: if one fails, all fail together (ideal for a multi-step checkout where payment + inventory reservation must succeed together). In <code>supervisorScope</code>, tasks are independent: failures are isolated to the specific child (ideal for dashboards where optional services shouldn't break critical data). I also highlight that <code>launch</code> propagates exceptions immediately up the Job hierarchy, whereas <code>async</code> defers throwing until <code>.await()</code> is invoked."
          </div>
        </div>
      </div>

      <!-- Subtopic 9.2 -->
      <div class="subtopic" id="subtopic-9-2">
        <h2>9.2 Lifecycle-Safe Flow Collection with repeatOnLifecycle</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p><code>repeatOnLifecycle(Lifecycle.State.STARTED)</code> is an Android lifecycle extension that automatically suspends/cancels coroutine collection when the lifecycle drops below the target state (e.g. app sent to background) and restarts collection when the lifecycle returns to that state.</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> Collecting Flows using raw <code>lifecycleScope.launch</code> keeps collecting in the background even when the app is minimized. The deprecated <code>launchWhenStarted</code> suspended execution, but kept upstream flow producers (like GPS updates, camera frames, and WebSockets) actively producing data, draining device battery.</p>
          <ul>
            <li><strong>True Cancellation:</strong> Automatically halts cold flow producers when the app is backgrounded.</li>
            <li><strong>Compose Equivalent:</strong> In Jetpack Compose, <code>flow.collectAsStateWithLifecycle()</code> provides this exact safety natively.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>// 1. Compose: Native Lifecycle-Safe Flow Collection
@Composable
fun AccountScreen(viewModel: AccountViewModel = hiltViewModel()) {
    // Automatically pauses collection when app goes to background!
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    AccountContent(state = uiState)
}

// 2. Fragment: repeatOnLifecycle in onViewCreated
override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    super.onViewCreated(view, savedInstanceState)
    viewLifecycleOwner.lifecycleScope.launch {
        viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
            viewModel.uiState.collect { state ->
                renderState(state)
            }
        }
    }
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>Automotive Navigation & Fleet Tracking:</strong> GPS location flow producers emit 1Hz coordinate streams. Collecting with <code>repeatOnLifecycle(STARTED)</code> ensures that when the driver switches to the radio or media app, GPS hardware and cellular telemetry suspend immediately, conserving vehicle battery and cellular data.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "I point out why Google deprecated <code>launchWhenStarted</code> in favor of <code>repeatOnLifecycle</code>: <code>launchWhenStarted</code> merely pauses the consumer coroutine, but the upstream flow producer continues running in the background. If you are collecting a continuous location stream or WebSocket feed, it wastes battery and network bandwidth. <code>repeatOnLifecycle</code> cancels the block completely when the lifecycle drops below <code>STARTED</code> and re-launches it from scratch upon returning. In Compose, I always use <code>collectAsStateWithLifecycle</code>."
          </div>
        </div>
      </div>

      <!-- Q&A Section -->
      <div class="qa-section">
        <h2>🎯 Senior/Lead Interview Q&A (Concurrency & Coroutines)</h2>

        <div class="qa-item" data-difficulty="basic">
          <div class="qa-question">
            <span class="qa-number">Q1</span>
            <span class="badge badge-basic">Basic</span>
            <p>What is the difference between launch and async in Kotlin Coroutines?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> <code>launch</code> is fire-and-forget: it returns a <code>Job</code> and does not carry a return value. Uncaught exceptions inside <code>launch</code> propagate immediately up the Job hierarchy to the parent scope. <code>async</code> is designed to compute a result: it returns a <code>Deferred&lt;T&gt;</code>, and exceptions are encapsulated within the Deferred object, thrown only when <code>.await()</code> is invoked on that Deferred.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="advanced">
          <div class="qa-question">
            <span class="qa-number">Q2</span>
            <span class="badge badge-advanced">Advanced</span>
            <p>How does cooperative cancellation work in Kotlin Coroutines? What happens if you catch CancellationException?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> Coroutine cancellation is cooperative: calling <code>job.cancel()</code> merely marks the coroutine as inactive. Suspending functions (like <code>delay</code>, <code>yield</code>, <code>withContext</code>) periodically check <code>isActive</code>; if cancelled, they throw a <code>CancellationException</code> to unwind the stack. If your code catches <code>Exception</code> without rethrowing <code>CancellationException</code>, you swallow the cancellation signal, creating orphaned background coroutines that continue executing indefinitely!</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="advanced">
          <div class="qa-question">
            <span class="qa-number">Q3</span>
            <span class="badge badge-advanced">Advanced</span>
            <p>What is Flow backpressure and how do you handle high-frequency streams in Kotlin Flow?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> Backpressure occurs when a Flow producer emits items faster than the collector can consume them. By default, cold flows are sequential and suspend the producer until the consumer finishes. For hot flows, backpressure is handled via: (1) <code>conflate()</code>: skips intermediate values, emitting only the latest, (2) <code>buffer(capacity, onBufferOverflow)</code> with <code>DROP_OLDEST</code>, or (3) <code>collectLatest { }</code>: cancels the previous collector block when a new emission arrives.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="scenario">
          <div class="qa-number">Q4</div>
          <div class="qa-question">
            <span class="badge badge-scenario">Scenario</span>
            <p>Compare StandardTestDispatcher vs UnconfinedTestDispatcher in kotlinx-coroutines-test.</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> <code>StandardTestDispatcher</code> queues coroutine tasks on an internal scheduler; virtual time does not advance automatically, requiring manual calls to <code>advanceUntilIdle()</code> or <code>advanceTimeBy(ms)</code>. Use this when testing execution order, retries, or delays. <code>UnconfinedTestDispatcher</code> executes coroutines eagerly on the current thread until the first suspension point, with zero queueing. Use this for simple ViewModel state testing where you want emissions to apply immediately without manually advancing time.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="scenario">
          <div class="qa-number">Q5</div>
          <div class="qa-question">
            <span class="badge badge-scenario">Scenario</span>
            <p>How do you convert a legacy callback-based third-party SDK (like Firebase or LocationManager) into a cold Flow?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <div class="code-block" data-language="kotlin">
              <pre><code>fun observeLocationUpdates(): Flow<Location> = callbackFlow {
    val listener = LocationListener { location ->
        trySend(location).isSuccess // Non-blocking send into channel
    }
    locationClient.registerListener(listener)

    // MANDATORY: awaitClose suspends until the flow collector is cancelled
    awaitClose {
        locationClient.unregisterListener(listener) // Guaranteed cleanup!
    }
}.flowOn(Dispatchers.IO)</code></pre>
            </div>
          </div>
        </div>
      </div>

      <!-- Checklist -->
      <div class="topic-progress-tracker">
        <h3>✅ Topic 9 Mastery Checklist</h3>
        <label class="progress-check"><input type="checkbox" data-topic="9" data-item="0"> coroutineScope vs supervisorScope failure propagation</label>
        <label class="progress-check"><input type="checkbox" data-topic="9" data-item="1"> Cooperative cancellation & CancellationException</label>
        <label class="progress-check"><input type="checkbox" data-topic="9" data-item="2"> repeatOnLifecycle vs launchWhenStarted</label>
        <label class="progress-check"><input type="checkbox" data-topic="9" data-item="3"> callbackFlow with awaitClose cleanup</label>
        <label class="progress-check"><input type="checkbox" data-topic="9" data-item="4"> Answered & Mastered all 5 Topic 9 Q&As</label>
      </div>
    </section>
    """

if __name__ == '__main__':
    print("html_topic_7_to_9 loaded successfully.")
