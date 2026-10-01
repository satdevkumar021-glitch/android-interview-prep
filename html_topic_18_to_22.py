def get_topics_18_to_22_html():
    return '''
<!-- ==================== TOPIC 18: DESIGN PATTERNS IN ANDROID ==================== -->
<section class="topic-section" id="topic-18">
  <div class="topic-header">
    <div class="topic-header-icon">🏗️</div>
    <div class="topic-header-text">
      <h1>Design Patterns in Android</h1>
      <p class="topic-tagline">Creational, Structural &amp; Behavioral patterns with real Android production code</p>
      <div class="category-badge-group">
        <span class="cat-pill">Architecture</span>
        <span class="cat-pill">OOP</span>
        <span class="cat-pill">Kotlin</span>
        <span class="cat-pill">Senior-Level</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 18-1: Creational Patterns -->
  <div class="subtopic" id="subtopic-18-1">
    <h2>Creational Patterns: Factory, Builder, Singleton</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need Creational Patterns?</h3>
      <p>In Android, object creation is often complex and context-dependent. Without creational patterns you get: tight coupling between callers and concrete classes, duplicated construction logic scattered across the codebase, untestable code (can\'t swap real vs. fake objects), and thread-safety bugs from naive Singleton implementations. A real problem: without a Factory, every screen that needs a ViewModel must know its exact constructor dependencies — break encapsulation, impossible to swap for tests. Without Builder, constructing a <code>Notification</code> or <code>AlertDialog</code> requires 20 setter calls in a fragile order.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Are Creational Patterns?</h3>
      <p><strong>Singleton:</strong> Guarantees a single instance of a class for the lifetime of the app/scope. Android pitfall: naive Singletons that hold a <code>Context</code> cause memory leaks. Fix: use ApplicationContext or use Hilt\'s <code>@Singleton</code> scope instead.<br><br>
      <strong>Factory / Abstract Factory:</strong> Decouples creation logic from the caller. A Factory Method lets subclasses decide which class to instantiate. In Android: <code>ViewModelProvider.Factory</code>, <code>WorkerFactory</code>.<br><br>
      <strong>Builder:</strong> Constructs complex objects step-by-step. Android examples: <code>AlertDialog.Builder</code>, <code>NotificationCompat.Builder</code>, <code>OkHttpClient.Builder</code>, <code>Retrofit.Builder</code>. Kotlin data classes with named parameters are often used as a lightweight alternative.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Do They Work? — Production Examples</h3>
      <p>Thread-safe Singleton (Double-Checked Locking), a typed Factory for analytics events, and a Builder for a network request config.</p>
      <pre class="code-block"><code class="language-kotlin">// ===== SINGLETON — Thread-safe with Double-Checked Locking =====
class SessionManager private constructor(context: Context) {
    private val prefs = context.applicationContext
        .getSharedPreferences("session", Context.MODE_PRIVATE)

    fun getToken(): String? = prefs.getString("token", null)
    fun setToken(token: String) = prefs.edit().putString("token", token).apply()
    fun clearSession() = prefs.edit().clear().apply()

    companion object {
        @Volatile private var INSTANCE: SessionManager? = null

        fun getInstance(context: Context): SessionManager =
            INSTANCE ?: synchronized(this) {
                INSTANCE ?: SessionManager(context).also { INSTANCE = it }
            }
    }
}
// Usage: SessionManager.getInstance(appContext).getToken()

// ===== FACTORY METHOD — ViewModel Factory =====
sealed class AnalyticsEvent {
    data class Purchase(val orderId: String, val amount: Double) : AnalyticsEvent()
    data class PageView(val screenName: String) : AnalyticsEvent()
    data class Error(val code: Int, val message: String) : AnalyticsEvent()
}

interface EventTracker { fun track(event: AnalyticsEvent) }

class FirebaseTracker : EventTracker {
    override fun track(event: AnalyticsEvent) {
        // Firebase implementation
    }
}
class MixpanelTracker : EventTracker {
    override fun track(event: AnalyticsEvent) { /* Mixpanel impl */ }
}

object AnalyticsTrackerFactory {
    fun create(flavor: String): EventTracker = when (flavor) {
        "firebase"  -> FirebaseTracker()
        "mixpanel"  -> MixpanelTracker()
        else        -> throw IllegalArgumentException("Unknown tracker: $flavor")
    }
}

// ===== BUILDER — Network Request Config =====
data class ApiConfig private constructor(
    val baseUrl: String,
    val timeoutSeconds: Long,
    val retryCount: Int,
    val enableLogging: Boolean,
    val headers: Map&lt;String, String&gt;
) {
    class Builder(private val baseUrl: String) {
        private var timeoutSeconds: Long = 30L
        private var retryCount: Int = 3
        private var enableLogging: Boolean = false
        private val headers: MutableMap&lt;String, String&gt; = mutableMapOf()

        fun timeout(seconds: Long) = apply { timeoutSeconds = seconds }
        fun retry(count: Int) = apply { retryCount = count }
        fun logging(enable: Boolean) = apply { enableLogging = enable }
        fun header(key: String, value: String) = apply { headers[key] = value }
        fun build() = ApiConfig(baseUrl, timeoutSeconds, retryCount, enableLogging, headers)
    }
}

val config = ApiConfig.Builder("https://api.mybank.com/v2")
    .timeout(15L)
    .retry(2)
    .logging(BuildConfig.DEBUG)
    .header("X-App-Version", BuildConfig.VERSION_NAME)
    .build()</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// Kotlin object keyword = thread-safe Singleton by default
object AppDatabase { /* ... */ }  // Kotlin Singleton

// Companion object factory method (idiomatic Kotlin)
class MyViewModel(repo: UserRepository) : ViewModel() {
    companion object {
        fun provideFactory(repo: UserRepository): ViewModelProvider.Factory =
            object : ViewModelProvider.Factory {
                override fun &lt;T : ViewModel&gt; create(modelClass: Class&lt;T&gt;): T {
                    @Suppress("UNCHECKED_CAST")
                    return MyViewModel(repo) as T
                }
            }
    }
}

// Kotlin DSL-style Builder using lambdas
fun buildApiConfig(baseUrl: String, init: ApiConfig.Builder.() -> Unit): ApiConfig =
    ApiConfig.Builder(baseUrl).apply(init).build()

val config = buildApiConfig("https://api.example.com") {
    timeout(20L)
    retry(3)
    logging(true)
}</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example — FinTech Payment SDK</h3>
      <p>In a payment processing SDK, we use all three creational patterns together: Singleton for the SDK session, Factory for payment method handlers, Builder for payment requests.</p>
      <pre class="code-block"><code class="language-kotlin">// PaymentSDK.kt — FinTech production pattern
class PaymentSDK private constructor(private val config: SDKConfig) {

    companion object {
        @Volatile private var instance: PaymentSDK? = null

        fun initialize(config: SDKConfig): PaymentSDK =
            instance ?: synchronized(this) {
                instance ?: PaymentSDK(config).also { instance = it }
            }

        fun getInstance(): PaymentSDK =
            checkNotNull(instance) { "PaymentSDK not initialized. Call initialize() first." }
    }

    fun processPayment(request: PaymentRequest): Flow&lt;PaymentResult&gt; {
        val handler = PaymentHandlerFactory.create(request.method)
        return handler.process(request)
    }
}

sealed class PaymentMethod { object Card : PaymentMethod(); object UPI : PaymentMethod(); object NetBanking : PaymentMethod() }

object PaymentHandlerFactory {
    fun create(method: PaymentMethod): PaymentHandler = when (method) {
        is PaymentMethod.Card       -> CardPaymentHandler()
        is PaymentMethod.UPI        -> UpiPaymentHandler()
        is PaymentMethod.NetBanking -> NetBankingHandler()
    }
}

data class PaymentRequest private constructor(
    val amount: Long,          // in paise
    val currency: String,
    val method: PaymentMethod,
    val description: String,
    val metadata: Map&lt;String, String&gt;
) {
    class Builder(private val amount: Long, private val method: PaymentMethod) {
        private var currency = "INR"
        private var description = ""
        private val metadata = mutableMapOf&lt;String, String&gt;()

        fun currency(c: String) = apply { currency = c }
        fun description(d: String) = apply { description = d }
        fun metadata(key: String, value: String) = apply { metadata[key] = value }
        fun build() = PaymentRequest(amount, currency, method, description, metadata)
    }
}

// Usage at call site — clean and readable
val request = PaymentRequest.Builder(50000L, PaymentMethod.Card)
    .currency("INR")
    .description("Netflix Subscription")
    .metadata("orderId", "ORD-12345")
    .build()

PaymentSDK.getInstance().processPayment(request).collect { result ->
    when (result) {
        is PaymentResult.Success -> handleSuccess(result.transactionId)
        is PaymentResult.Failure -> handleError(result.errorCode)
        is PaymentResult.Pending -> showPendingState()
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Context-leaking Singleton:</strong> Storing <code>Activity</code> context in a Singleton field — the Activity is never GC\'d. ✅ Fix: Always store <code>context.applicationContext</code>.</li>
        <li>❌ <strong>Non-thread-safe Singleton:</strong> Using <code>if (INSTANCE == null) INSTANCE = ...</code> without synchronization — race condition on first call. ✅ Fix: Use <code>@Volatile</code> + <code>synchronized</code> or Kotlin <code>object</code>.</li>
        <li>❌ <strong>Overusing Singleton:</strong> Making everything a Singleton causes hidden global state, hard-to-test code. ✅ Fix: Use DI scopes (Hilt <code>@Singleton</code>) instead of manual Singletons.</li>
        <li>❌ <strong>Builder not validating:</strong> Calling <code>build()</code> with missing required fields throws NPE at runtime. ✅ Fix: Validate in <code>build()</code> using <code>require()</code> / <code>check()</code>.</li>
        <li>❌ <strong>Factory ignoring exhaustive when:</strong> Using <code>if-else</code> chains in Factory — adding new types silently skips. ✅ Fix: Use Kotlin <code>when</code> on sealed classes (compiler enforces exhaustiveness).</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"In production Android, I use creational patterns to solve object lifecycle and construction complexity. For Singleton I avoid manual implementation — I either use Kotlin <code>object</code> for compile-time safety, or Hilt\'s <code>@Singleton</code> scope which gives me testable injection points. The problem with manual Singletons is they\'re impossible to fake in tests without extra effort like dependency injection. For Factory, I lean heavily on sealed classes with exhaustive <code>when</code> so the compiler tells me when I forget to handle a new type. For Builder, I prefer Kotlin DSL style with <code>apply</code> lambdas — it reads like configuration, which is exactly what it is. In our payment SDK, these three patterns work together: Singleton for the SDK lifecycle, Factory for payment handler dispatch, Builder for constructing immutable payment requests."</p>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 18-2: Structural Patterns -->
  <div class="subtopic" id="subtopic-18-2">
    <h2>Structural Patterns: Adapter, Decorator, Facade</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need Structural Patterns?</h3>
      <p>Structural patterns solve the problem of composing classes and objects to form larger structures. In Android: <strong>Adapter</strong> — RecyclerView needs a bridge between your data model and ViewHolder views, or you need to integrate a legacy API that has an incompatible interface. <strong>Decorator</strong> — you want to add logging, caching, or retry logic to a repository without changing the repository class itself. <strong>Facade</strong> — your ViewModel shouldn\'t need to know about 5 different data sources; it should call one clean facade method.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Are Structural Patterns?</h3>
      <p><strong>Adapter:</strong> Converts the interface of a class into another interface that clients expect. RecyclerView.Adapter is the canonical Android example. Also used when wrapping third-party SDKs.<br><br>
      <strong>Decorator:</strong> Attaches additional responsibilities to an object dynamically. In Kotlin, delegation (<code>by</code> keyword) makes this elegant — you implement an interface and delegate to the wrapped instance, overriding only what you need to decorate.<br><br>
      <strong>Facade:</strong> Provides a simplified interface to a complex subsystem. A Repository in MVVM is a Facade over network, database, and cache layers. The ViewModel calls one method; the Facade handles orchestration.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Do They Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// ===== ADAPTER — Wrapping legacy payment gateway =====
// Legacy interface we cannot change
class LegacyPaymentGateway {
    fun makePayment(cardNum: String, expiry: String, cvv: String, amountCents: Int): Boolean = true
}

// Our modern interface
interface PaymentGateway {
    suspend fun pay(request: PaymentRequest): Result&lt;String&gt;
}

// Adapter bridges the gap
class LegacyPaymentAdapter(
    private val legacy: LegacyPaymentGateway
) : PaymentGateway {
    override suspend fun pay(request: PaymentRequest): Result&lt;String&gt; = withContext(Dispatchers.IO) {
        val success = legacy.makePayment(
            request.cardNumber, request.expiry, request.cvv,
            (request.amountInRupees * 100).toInt()
        )
        if (success) Result.success("TXN-${System.currentTimeMillis()}")
        else Result.failure(Exception("Payment failed"))
    }
}

// ===== DECORATOR — Caching + Logging Repository =====
interface UserRepository {
    suspend fun getUser(id: String): User
    suspend fun updateUser(user: User): Boolean
}

class RemoteUserRepository(private val api: ApiService) : UserRepository {
    override suspend fun getUser(id: String): User = api.getUser(id)
    override suspend fun updateUser(user: User): Boolean = api.updateUser(user)
}

// Decorator: adds in-memory caching without changing RemoteUserRepository
class CachingUserRepository(
    private val delegate: UserRepository,
    private val cache: LruCache&lt;String, User&gt; = LruCache(50)
) : UserRepository by delegate {  // Kotlin delegation — delegate all by default
    override suspend fun getUser(id: String): User {
        return cache.get(id) ?: delegate.getUser(id).also { cache.put(id, it) }
    }
}

// Another Decorator: adds logging
class LoggingUserRepository(
    private val delegate: UserRepository,
    private val logger: Logger
) : UserRepository by delegate {
    override suspend fun getUser(id: String): User {
        logger.d("Fetching user: $id")
        return delegate.getUser(id).also { logger.d("Got user: ${it.name}") }
    }
}

// Compose decorators: cache on top of logging on top of remote
val repository: UserRepository =
    CachingUserRepository(
        LoggingUserRepository(
            RemoteUserRepository(apiService), logger
        )
    )

// ===== FACADE — DataFacade hides complexity =====
class UserDataFacade(
    private val api: UserApiService,
    private val db: UserDao,
    private val prefs: UserPreferences,
    private val analytics: AnalyticsTracker
) {
    suspend fun getUserProfile(userId: String): UserProfile {
        val cached = db.getUserById(userId)
        if (cached != null && !cached.isStale()) return cached.toProfile()

        return api.fetchUser(userId).also { dto ->
            db.insertUser(dto.toEntity())
            analytics.track(AnalyticsEvent.PageView("profile_$userId"))
        }.toProfile()
    }

    suspend fun updateDisplayName(userId: String, name: String): Result&lt;Unit&gt; = runCatching {
        api.updateUser(userId, UpdateRequest(displayName = name))
        db.updateDisplayName(userId, name)
        prefs.setLastUpdated(System.currentTimeMillis())
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// Kotlin interface delegation — cornerstone of Decorator pattern
class LoggingRepo(private val delegate: UserRepository) : UserRepository by delegate {
    // Only override what you want to decorate; rest is auto-delegated
    override suspend fun getUser(id: String): User {
        println("GETTING $id")
        return delegate.getUser(id)
    }
}

// RecyclerView Adapter — classic Adapter pattern
class UserAdapter(private val onClick: (User) -> Unit) :
    ListAdapter&lt;User, UserAdapter.ViewHolder&gt;(DIFF_CALLBACK) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
        ViewHolder(ItemUserBinding.inflate(LayoutInflater.from(parent.context), parent, false))

    override fun onBindViewHolder(holder: ViewHolder, position: Int) =
        holder.bind(getItem(position))

    inner class ViewHolder(private val binding: ItemUserBinding) :
        RecyclerView.ViewHolder(binding.root) {
        fun bind(user: User) {
            binding.name.text = user.name
            binding.root.setOnClickListener { onClick(user) }
        }
    }

    companion object {
        val DIFF_CALLBACK = object : DiffUtil.ItemCallback&lt;User&gt;() {
            override fun areItemsTheSame(old: User, new: User) = old.id == new.id
            override fun areContentsTheSame(old: User, new: User) = old == new
        }
    }
}</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example — E-Commerce App</h3>
      <p>In an e-commerce app, we combine all three structural patterns in the product listing feature:</p>
      <pre class="code-block"><code class="language-kotlin">// FACADE — ProductFacade orchestrates catalog, inventory, and pricing
class ProductFacade(
    private val catalogApi: CatalogApiService,
    private val inventoryApi: InventoryApiService,
    private val pricingEngine: PricingEngine,
    private val productDao: ProductDao
) {
    suspend fun getProductDetail(sku: String): ProductDetailUiModel {
        val product = catalogApi.getProduct(sku)
        val inventory = inventoryApi.getStock(sku)
        val price = pricingEngine.calculatePrice(sku, product.basePrice)
        productDao.upsert(product.toEntity())
        return ProductDetailUiModel(
            title = product.title,
            imageUrl = product.imageUrl,
            displayPrice = "₹${price.finalPrice}",
            originalPrice = "₹${product.basePrice}",
            discount = price.discountPercent,
            inStock = inventory.available > 0,
            stockCount = inventory.available
        )
    }
}

// ADAPTER — adapting legacy catalog SDK to our ProductRepository interface
interface ProductRepository {
    suspend fun searchProducts(query: String): List&lt;Product&gt;
}

class LegacyCatalogAdapter(private val sdk: LegacyCatalogSdk) : ProductRepository {
    override suspend fun searchProducts(query: String): List&lt;Product&gt; =
        withContext(Dispatchers.IO) {
            sdk.search(query, 0, 20)  // Legacy API with pagination params
                .results
                .map { it.toProduct() }
        }
}

// DECORATOR — adds offline support
class OfflineFirstProductRepository(
    private val remote: ProductRepository,
    private val dao: ProductDao
) : ProductRepository by remote {
    override suspend fun searchProducts(query: String): List&lt;Product&gt; = try {
        remote.searchProducts(query).also { dao.insertAll(it.map { p -> p.toEntity() }) }
    } catch (e: IOException) {
        dao.searchProducts(query).map { it.toProduct() }
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Facade becoming God class:</strong> The Facade grows to 500 lines handling everything. ✅ Fix: Split into multiple focused facades (ProductFacade, CartFacade, OrderFacade).</li>
        <li>❌ <strong>Adapter doing business logic:</strong> Adapters should only translate interfaces, not transform data. ✅ Fix: Keep adapters thin; move transformation to mappers.</li>
        <li>❌ <strong>Decorator breaking Liskov:</strong> Decorator changes behavior in a way that breaks contracts. ✅ Fix: Decorator should extend, not replace — callers shouldn\'t need to know about decoration.</li>
        <li>❌ <strong>RecyclerView Adapter updating from wrong thread:</strong> Calling <code>notifyDataSetChanged()</code> from background thread crashes. ✅ Fix: Use <code>ListAdapter.submitList()</code> — it handles DiffUtil on background thread automatically.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Structural patterns are about composition. In Android, the most impactful one for me is Decorator combined with Kotlin\'s <code>by</code> delegation syntax — it\'s incredibly clean. When I need to add caching or logging to a repository, I wrap it in a decorator that implements the same interface via delegation, and only override the methods I want to augment. This is far better than inheritance because I can compose multiple decorators and easily swap them in tests. Facade is equally important — my ViewModels should never know about multiple data sources. A facade with one method <code>getUserProfile()</code> hides all the orchestration behind a clean API. This also makes testing trivial — I mock the facade, not 5 separate data sources."</p>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 18-3: Behavioral Patterns -->
  <div class="subtopic" id="subtopic-18-3">
    <h2>Behavioral Patterns: Observer, Strategy, Command</h2>

    <div class="card card-how">
      <h3>🛠️ Observer, Strategy &amp; Command — Production Code</h3>
      <pre class="code-block"><code class="language-kotlin">// ===== OBSERVER — StateFlow / SharedFlow (modern Android Observer) =====
// The classic Observer pattern is built into Kotlin coroutines via Flow
class OrderViewModel(private val repo: OrderRepository) : ViewModel() {
    private val _orderState = MutableStateFlow&lt;OrderState&gt;(OrderState.Idle)
    val orderState: StateFlow&lt;OrderState&gt; = _orderState.asStateFlow()

    fun placeOrder(cart: Cart) {
        viewModelScope.launch {
            _orderState.value = OrderState.Loading
            repo.placeOrder(cart)
                .onSuccess { order -> _orderState.value = OrderState.Success(order) }
                .onFailure { e -> _orderState.value = OrderState.Error(e.message ?: "Unknown") }
        }
    }
}

sealed class OrderState {
    object Idle : OrderState()
    object Loading : OrderState()
    data class Success(val order: Order) : OrderState()
    data class Error(val message: String) : OrderState()
}

// Collecting in Fragment (observer subscribing to observable)
viewLifecycleOwner.lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.orderState.collect { state ->
            when (state) {
                is OrderState.Loading -> showLoading()
                is OrderState.Success -> showOrderConfirmation(state.order)
                is OrderState.Error   -> showError(state.message)
                is OrderState.Idle    -> Unit
            }
        }
    }
}

// ===== STRATEGY — Sorting strategy for product lists =====
fun interface SortStrategy {
    fun sort(products: List&lt;Product&gt;): List&lt;Product&gt;
}

object PriceAscStrategy : SortStrategy {
    override fun sort(products: List&lt;Product&gt;) = products.sortedBy { it.price }
}
object RatingDescStrategy : SortStrategy {
    override fun sort(products: List&lt;Product&gt;) = products.sortedByDescending { it.rating }
}
object PopularityStrategy : SortStrategy {
    override fun sort(products: List&lt;Product&gt;) = products.sortedByDescending { it.salesCount }
}

class ProductListViewModel(private val repo: ProductRepository) : ViewModel() {
    private var sortStrategy: SortStrategy = PopularityStrategy

    fun setSortStrategy(strategy: SortStrategy) { sortStrategy = strategy; refreshList() }
    private fun refreshList() { /* re-sort and emit */ }
}

// ===== COMMAND — Undo/Redo for a drawing canvas app =====
interface DrawCommand {
    fun execute()
    fun undo()
}

class DrawLineCommand(
    private val canvas: DrawingCanvas,
    private val from: PointF,
    private val to: PointF,
    private val paint: Paint
) : DrawCommand {
    override fun execute() = canvas.drawLine(from, to, paint)
    override fun undo() = canvas.eraseLine(from, to)
}

class CommandManager {
    private val history = ArrayDeque&lt;DrawCommand&gt;()
    private val redoStack = ArrayDeque&lt;DrawCommand&gt;()

    fun execute(cmd: DrawCommand) {
        cmd.execute()
        history.addLast(cmd)
        redoStack.clear()
    }

    fun undo() {
        if (history.isEmpty()) return
        val cmd = history.removeLast()
        cmd.undo()
        redoStack.addLast(cmd)
    }

    fun redo() {
        if (redoStack.isEmpty()) return
        val cmd = redoStack.removeLast()
        cmd.execute()
        history.addLast(cmd)
    }
}</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example — Healthcare App</h3>
      <p>In a healthcare monitoring app, Strategy pattern drives different alert rules for different patient conditions:</p>
      <pre class="code-block"><code class="language-kotlin">// Strategy for vital sign alert thresholds — differs per patient condition
interface AlertStrategy {
    fun shouldAlert(reading: VitalReading): Boolean
    val alertMessage: String
}

class DiabetesAlertStrategy : AlertStrategy {
    override fun shouldAlert(reading: VitalReading): Boolean =
        reading.bloodSugar > 180 || reading.bloodSugar < 70
    override val alertMessage = "Blood sugar out of diabetic safe range"
}

class HypertensionAlertStrategy : AlertStrategy {
    override fun shouldAlert(reading: VitalReading): Boolean =
        reading.systolicBP > 140 || reading.diastolicBP > 90
    override val alertMessage = "Blood pressure critically high"
}

class PostSurgeryAlertStrategy : AlertStrategy {
    override fun shouldAlert(reading: VitalReading): Boolean =
        reading.heartRate > 100 || reading.oxygenSaturation < 95
    override val alertMessage = "Post-surgery vital sign alert"
}

class PatientMonitor(private val alertStrategy: AlertStrategy) {
    fun checkVitals(reading: VitalReading) {
        if (alertStrategy.shouldAlert(reading)) {
            notifyNursingStation(alertStrategy.alertMessage, reading)
        }
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Using LiveData without lifecycle awareness:</strong> Observing LiveData with <code>Observer</code> but forgetting lifecycle owner causes leaks. ✅ Fix: Always use <code>viewLifecycleOwner</code> as the lifecycle owner in Fragments.</li>
        <li>❌ <strong>Strategy with if-else inside strategy:</strong> If your strategy implementations are full of conditionals, you haven\'t truly separated concerns. ✅ Fix: Each strategy class should have a single, focused algorithm.</li>
        <li>❌ <strong>Command pattern without error handling:</strong> If <code>execute()</code> fails halfway, <code>undo()</code> may be in an inconsistent state. ✅ Fix: Use transactions or compensating commands.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"In modern Android, the Observer pattern is baked into the architecture via StateFlow and SharedFlow — it\'s not something you implement from scratch anymore. I use StateFlow for UI state (single source of truth) and SharedFlow for one-shot events like navigation or snackbar triggers. Strategy is my go-to when I see multiple <code>if-else</code> branches switching on a type — I extract each branch into a Strategy class. This makes adding new variants as simple as adding a new class, not modifying existing ones — Open/Closed Principle. Command is underused in Android but invaluable for apps that need undo/redo, or for queuing operations that might need to be retried."</p>
      </div>
    </div>
  </div>

  <!-- Q&A Section -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the difference between a Singleton and a static class? When would you prefer each in Android?</div>
      <div class="qa-answer">
        <p><strong>Static class:</strong> All members are static — no instance, no state sharing via instance reference, can\'t implement interfaces, can\'t be injected. <strong>Singleton:</strong> A single instance of a class — can implement interfaces, can be mocked/injected, holds state via instance fields. In Android: prefer Singleton (especially via Hilt <code>@Singleton</code>) over static classes because Singletons are testable (you can inject a fake via DI), support interfaces, and integrate with DI frameworks. Static utility methods (pure functions with no state) are fine as top-level Kotlin functions or companion object methods.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q2</span>How does Kotlin\'s <code>by</code> delegation keyword implement the Decorator pattern, and what are its limitations?</div>
      <div class="qa-answer">
        <p>Kotlin generates code that calls every interface method on the delegate instance. When you write <code>class A(d: MyInterface) : MyInterface by d</code>, the compiler generates forwarding methods for every method in <code>MyInterface</code> that you don\'t override. You only override the methods you want to decorate. <strong>Limitations:</strong> (1) Delegation is resolved at compile time — you can\'t change the delegate dynamically (it must be set in the constructor). (2) If the delegate calls a method on itself (<code>this</code>) that you\'ve overridden, it calls the original, not your decorated version — so it doesn\'t solve the "self-delegation" problem. (3) Only works with interfaces, not abstract classes.</p>
        <pre class="code-block"><code class="language-kotlin">interface Greeter { fun greet(): String; fun loudGreet(): String }
class DefaultGreeter : Greeter {
    override fun greet() = "Hello"
    // This calls greet() on itself, not on any decorator!
    override fun loudGreet() = greet().uppercase()
}
class LoggingGreeter(d: Greeter) : Greeter by d {
    override fun greet() = "Logged: ${d.greet()}"
    // loudGreet() will call DefaultGreeter.loudGreet() -> DefaultGreeter.greet(), NOT LoggingGreeter.greet()
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>How do StateFlow and SharedFlow differ, and when do you use each as the Observer pattern in Android?</div>
      <div class="qa-answer">
        <p><strong>StateFlow:</strong> Has an initial value, always holds current state, replays last value to new collectors, backed by <code>value</code> property. Use for <em>UI state</em> — screen data that should be visible immediately when user navigates to screen.<br><br>
        <strong>SharedFlow:</strong> No initial value by default, configurable replay cache (0 to N), configurable buffer, doesn\'t lose emissions if no collector. Use for <em>events</em> — one-shot actions like navigation, snackbar, dialogs that should only happen once and not replay on screen rotation.</p>
        <pre class="code-block"><code class="language-kotlin">class MyViewModel : ViewModel() {
    // StateFlow — UI state (replays on rotation, shows current data)
    private val _uiState = MutableStateFlow&lt;UiState&gt;(UiState.Loading)
    val uiState = _uiState.asStateFlow()

    // SharedFlow — events (no replay, fire-and-forget)
    private val _events = MutableSharedFlow&lt;UiEvent&gt;()
    val events = _events.asSharedFlow()

    fun navigateToDetail(id: String) {
        viewModelScope.launch { _events.emit(UiEvent.Navigate("detail/$id")) }
    }
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q4</span>You have a feature where users can apply different discount strategies at checkout (10% off, buy-2-get-1, flat ₹100 off). How do you implement this with the Strategy pattern?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">fun interface DiscountStrategy {
    fun apply(cartTotal: Double, items: List&lt;CartItem&gt;): Double  // returns discounted total
}

object TenPercentOff : DiscountStrategy {
    override fun apply(total: Double, items: List&lt;CartItem&gt;) = total * 0.90
}

object FlatHundredOff : DiscountStrategy {
    override fun apply(total: Double, items: List&lt;CartItem&gt;) = maxOf(0.0, total - 100.0)
}

class BuyTwoGetOneFree : DiscountStrategy {
    override fun apply(total: Double, items: List&lt;CartItem&gt;): Double {
        val sortedItems = items.sortedBy { it.price }
        val freeItems = sortedItems.take(sortedItems.size / 3)
        val discount = freeItems.sumOf { it.price }
        return total - discount
    }
}

class CheckoutEngine(private var discountStrategy: DiscountStrategy = TenPercentOff) {
    fun setStrategy(strategy: DiscountStrategy) { discountStrategy = strategy }
    fun calculateTotal(items: List&lt;CartItem&gt;): Double {
        val raw = items.sumOf { it.price }
        return discountStrategy.apply(raw, items)
    }
}
// Runtime switching:
val engine = CheckoutEngine()
engine.setStrategy(BuyTwoGetOneFree())
val total = engine.calculateTotal(cart.items)</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q5</span>What is the difference between the Adapter pattern and the Facade pattern?</div>
      <div class="qa-answer">
        <p><strong>Adapter:</strong> Converts one interface to another — it\'s about compatibility. You use it when you have an existing class with an incompatible interface and you want to make it work with new code without changing the original. Example: wrapping a legacy payment SDK to implement your modern <code>PaymentGateway</code> interface.<br><br>
        <strong>Facade:</strong> Provides a simpler interface to a complex subsystem — it\'s about simplicity. You use it when you want to hide complexity and provide one clean entry point. Example: <code>UserDataFacade.getUserProfile()</code> hides calls to API, DB, and analytics behind one method. The subsystem doesn\'t change; you just create a simpler view of it.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>Your team is adding a new analytics provider alongside the existing one. How would you use the Observer or Decorator pattern to send events to multiple providers without changing the event-firing code?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">// Composite pattern (variant of Decorator) — fan out to multiple trackers
class CompositeAnalyticsTracker(
    private val trackers: List&lt;AnalyticsTracker&gt;
) : AnalyticsTracker {
    override fun track(event: AnalyticsEvent) {
        trackers.forEach { it.track(event) }
    }
    override fun setUserId(id: String) {
        trackers.forEach { it.setUserId(id) }
    }
}

// Setup in DI module
val tracker: AnalyticsTracker = CompositeAnalyticsTracker(
    listOf(
        FirebaseAnalyticsTracker(firebaseAnalytics),
        MixpanelTracker(mixpanel),
        BrazeTracker(braze)   // new provider added here — zero changes to callers
    )
)
// All existing code calls tracker.track(event) — no changes needed anywhere</code></pre>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge — Implement an Undo/Redo System</h3>
    <p><strong>Problem:</strong> Implement a text editor with undo/redo using the Command pattern. Support: type text, delete text, clear all. Each operation must be undoable.</p>
    <pre class="code-block"><code class="language-kotlin">// Command interface
interface TextCommand {
    fun execute(buffer: StringBuilder)
    fun undo(buffer: StringBuilder)
}

class TypeCommand(private val text: String) : TextCommand {
    override fun execute(buffer: StringBuilder) { buffer.append(text) }
    override fun undo(buffer: StringBuilder) { buffer.delete(buffer.length - text.length, buffer.length) }
}

class DeleteCommand(private val count: Int) : TextCommand {
    private var deletedText: String = ""
    override fun execute(buffer: StringBuilder) {
        val from = maxOf(0, buffer.length - count)
        deletedText = buffer.substring(from)
        buffer.delete(from, buffer.length)
    }
    override fun undo(buffer: StringBuilder) { buffer.append(deletedText) }
}

class ClearCommand : TextCommand {
    private var savedContent: String = ""
    override fun execute(buffer: StringBuilder) {
        savedContent = buffer.toString()
        buffer.clear()
    }
    override fun undo(buffer: StringBuilder) {
        buffer.clear()
        buffer.append(savedContent)
    }
}

class TextEditor {
    private val buffer = StringBuilder()
    private val history = ArrayDeque&lt;TextCommand&gt;()
    private val redoStack = ArrayDeque&lt;TextCommand&gt;()

    fun execute(cmd: TextCommand) {
        cmd.execute(buffer)
        history.addLast(cmd)
        redoStack.clear()
    }

    fun undo(): Boolean {
        if (history.isEmpty()) return false
        val cmd = history.removeLast()
        cmd.undo(buffer)
        redoStack.addLast(cmd)
        return true
    }

    fun redo(): Boolean {
        if (redoStack.isEmpty()) return false
        val cmd = redoStack.removeLast()
        cmd.execute(buffer)
        history.addLast(cmd)
        return true
    }

    fun getText(): String = buffer.toString()
}

// Test:
val editor = TextEditor()
editor.execute(TypeCommand("Hello"))      // "Hello"
editor.execute(TypeCommand(" World"))    // "Hello World"
editor.execute(DeleteCommand(5))         // "Hello "
editor.undo()                            // "Hello World"
editor.undo()                            // "Hello"
editor.redo()                            // "Hello World"
// Time: O(1) per operation. Space: O(n) for history stack</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="18" data-item="0"> ✅ Understood Creational Patterns</label>
    <label class="progress-check"><input type="checkbox" data-topic="18" data-item="1"> ✅ Understood Structural Patterns</label>
    <label class="progress-check"><input type="checkbox" data-topic="18" data-item="2"> ✅ Understood Behavioral Patterns</label>
    <label class="progress-check"><input type="checkbox" data-topic="18" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="18" data-item="4"> ✅ Solved Undo/Redo Coding Challenge</label>
  </div>
</section>

<!-- ==================== TOPIC 19: DEPENDENCY INJECTION WITH HILT & DAGGER ==================== -->
<section class="topic-section" id="topic-19">
  <div class="topic-header">
    <div class="topic-header-icon">💉</div>
    <div class="topic-header-text">
      <h1>Dependency Injection with Hilt &amp; Dagger</h1>
      <p class="topic-tagline">Component hierarchy, scopes, bindings, multibindings, and Hilt testing</p>
      <div class="category-badge-group">
        <span class="cat-pill">Hilt</span>
        <span class="cat-pill">Dagger</span>
        <span class="cat-pill">DI</span>
        <span class="cat-pill">Testing</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 19-1: Why DI + Hilt Basics -->
  <div class="subtopic" id="subtopic-19-1">
    <h2>Why DI, Hilt Setup &amp; Component Hierarchy</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need Dependency Injection?</h3>
      <p>Without DI, classes construct their own dependencies — tight coupling that makes code impossible to test. Example: if <code>OrderViewModel</code> creates <code>new OrderRepository(new ApiService(new OkHttpClient()))</code> inside itself, you can\'t swap in a fake repository for unit tests, you can\'t change the API base URL without modifying ViewModel, and every class becomes responsible for the full dependency graph. This violates Single Responsibility and Dependency Inversion principles. DI frameworks solve this by inverting control: classes declare what they need, the framework provides it. Hilt is Google\'s opinionated DI framework built on Dagger, specifically designed for Android with standard component hierarchy pre-defined.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is Hilt?</h3>
      <p>Hilt is a DI framework that generates code at compile time (via annotation processing / KSP). It wraps Dagger\'s powerful but verbose component setup into pre-defined Android components: <code>SingletonComponent</code> (app lifetime), <code>ActivityRetainedComponent</code> (ViewModel lifetime), <code>ActivityComponent</code>, <code>FragmentComponent</code>, <code>ViewComponent</code>, <code>ServiceComponent</code>. Hilt reads your <code>@Module</code> and <code>@Provides</code>/<code>@Binds</code> annotations and generates the boilerplate Dagger code (Components, Subcomponents, Builders). KSP (Kotlin Symbol Processing) is the modern annotation processor that replaces KAPT for Hilt.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does Hilt Work? — Full Setup</h3>
      <pre class="code-block"><code class="language-kotlin">// 1. Application — must be annotated
@HiltAndroidApp
class MyApp : Application()

// 2. Entry points — Activities, Fragments, Services
@AndroidEntryPoint
class MainActivity : AppCompatActivity() { /* Hilt injects here */ }

@AndroidEntryPoint
class HomeFragment : Fragment() {
    @Inject lateinit var tracker: AnalyticsTracker  // Field injection (use sparingly)
    private val viewModel: HomeViewModel by viewModels()  // Hilt + ViewModel integration
}

// 3. ViewModel injection
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val productRepo: ProductRepository,
    private val analyticsTracker: AnalyticsTracker
) : ViewModel() { /* ... */ }

// 4. Module providing dependencies
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient =
        OkHttpClient.Builder()
            .addInterceptor(AuthInterceptor())
            .connectTimeout(30, TimeUnit.SECONDS)
            .build()

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit =
        Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create())
            .build()

    @Provides
    @Singleton
    fun provideProductApi(retrofit: Retrofit): ProductApiService =
        retrofit.create(ProductApiService::class.java)
}

// 5. Binding interface to implementation
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    @Singleton
    abstract fun bindProductRepository(impl: ProductRepositoryImpl): ProductRepository

    @Binds
    @Singleton
    abstract fun bindAnalyticsTracker(impl: FirebaseAnalyticsTracker): AnalyticsTracker
}

// 6. The implementation — just declares what it needs
class ProductRepositoryImpl @Inject constructor(
    private val api: ProductApiService,
    private val dao: ProductDao,
    private val dispatchers: CoroutineDispatchers
) : ProductRepository { /* ... */ }</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs — Scopes</h3>
      <pre class="code-block"><code class="language-kotlin">// SCOPE ANNOTATIONS — control instance lifetime
@Singleton          // Lives for app lifetime (SingletonComponent)
@ActivityRetainedScoped  // Lives across config changes (ActivityRetainedComponent — ViewModel scope)
@ActivityScoped     // Lives for activity lifetime
@FragmentScoped     // Lives for fragment lifetime
@ViewScoped         // Lives for view lifetime

// Without a scope annotation — new instance every time it\'s requested (unscoped)

// @Provides vs @Binds
// @Provides — use for third-party types or complex construction
@Provides
@Singleton
fun provideMoshi(): Moshi = Moshi.Builder().add(KotlinJsonAdapterFactory()).build()

// @Binds — use when you want to bind an interface to its implementation (more efficient, no instantiation overhead)
@Binds
@Singleton
abstract fun bindRepo(impl: MyRepoImpl): MyRepository

// QUALIFIERS — when you need multiple instances of the same type
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class AuthOkHttp

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class PublicOkHttp

@Module
@InstallIn(SingletonComponent::class)
object OkHttpModule {
    @Provides @Singleton @AuthOkHttp
    fun provideAuthOkHttp(): OkHttpClient = OkHttpClient.Builder()
        .addInterceptor(AuthInterceptor()).build()

    @Provides @Singleton @PublicOkHttp
    fun providePublicOkHttp(): OkHttpClient = OkHttpClient.Builder().build()
}

// Injection using qualifier
class ApiRepository @Inject constructor(
    @AuthOkHttp private val authClient: OkHttpClient,
    @PublicOkHttp private val publicClient: OkHttpClient
)</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example — Multibindings &amp; CoroutineDispatchers</h3>
      <pre class="code-block"><code class="language-kotlin">// CoroutineDispatchers abstraction — makes tests use TestCoroutineDispatcher
interface CoroutineDispatchers {
    val main: CoroutineDispatcher
    val io: CoroutineDispatcher
    val default: CoroutineDispatcher
}

class DefaultCoroutineDispatchers @Inject constructor() : CoroutineDispatchers {
    override val main = Dispatchers.Main
    override val io = Dispatchers.IO
    override val default = Dispatchers.Default
}

@Module
@InstallIn(SingletonComponent::class)
abstract class DispatcherModule {
    @Binds @Singleton
    abstract fun bindDispatchers(impl: DefaultCoroutineDispatchers): CoroutineDispatchers
}

// MULTIBINDINGS — inject a Set or Map of implementations
// Useful for plugin architectures, multiple analytics trackers, feature flags
@Module
@InstallIn(SingletonComponent::class)
abstract class AnalyticsModule {
    @Binds @IntoSet
    abstract fun bindFirebaseTracker(impl: FirebaseAnalyticsTracker): AnalyticsTracker

    @Binds @IntoSet
    abstract fun bindMixpanelTracker(impl: MixpanelTracker): AnalyticsTracker
}

// Injected as a Set — composite tracking
class CompositeAnalytics @Inject constructor(
    private val trackers: Set&lt;@JvmSuppressWildcards AnalyticsTracker&gt;
) : AnalyticsTracker {
    override fun track(event: AnalyticsEvent) = trackers.forEach { it.track(event) }
}

// HILT ENTRY POINT — for non-Hilt-aware classes (e.g., ContentProvider, custom View)
@EntryPoint
@InstallIn(SingletonComponent::class)
interface AnalyticsEntryPoint {
    fun analyticsTracker(): AnalyticsTracker
}

// Usage in ContentProvider
class MyContentProvider : ContentProvider() {
    private val tracker: AnalyticsTracker by lazy {
        EntryPointAccessors.fromApplication(
            context!!.applicationContext,
            AnalyticsEntryPoint::class.java
        ).analyticsTracker()
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Missing scope annotation:</strong> Not annotating with <code>@Singleton</code> means a new instance is created every time — database, network client created multiple times. ✅ Fix: Annotate expensive objects with the appropriate scope.</li>
        <li>❌ <strong>@Provides in abstract module:</strong> Using <code>@Provides</code> in an <code>abstract class</code> module — compiler error. ✅ Fix: <code>@Provides</code> must be in concrete class or companion object; <code>@Binds</code> must be in abstract class.</li>
        <li>❌ <strong>Field injection in non-Android classes:</strong> Using <code>@Inject lateinit var</code> in a plain Kotlin class — Hilt can\'t inject it. ✅ Fix: Use constructor injection (<code>@Inject constructor</code>) for all non-Android-framework classes.</li>
        <li>❌ <strong>Scope mismatch:</strong> A <code>@Singleton</code>-scoped class cannot depend on an <code>@ActivityScoped</code> class — wider scope depending on narrower scope. ✅ Fix: Dependencies must have equal or wider scope than the dependent class.</li>
        <li>❌ <strong>Not using TestCoroutineDispatcher:</strong> Tests that use real <code>Dispatchers.IO</code> are slow and flaky. ✅ Fix: Inject <code>CoroutineDispatchers</code> interface; provide <code>TestDispatchers</code> in test module.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"I use Hilt as the DI framework on all Android projects because it provides the right abstraction level — it wraps Dagger\'s compile-time safety without requiring you to hand-write the component hierarchy. The key decisions I make are around scoping. I default everything to unscoped (new instance per injection) and only scope up when there\'s a clear reason — <code>@Singleton</code> for network clients and databases, <code>@ActivityRetainedScoped</code> for things ViewModels share. I use <code>@Binds</code> over <code>@Provides</code> whenever possible because it\'s more efficient — Dagger doesn\'t need to instantiate a module object to call the method. For testing, the key pattern is injecting <code>CoroutineDispatchers</code> as an interface so tests can swap in <code>UnconfinedTestDispatcher</code>. I also use <code>@TestInstallIn</code> to replace production modules with test fakes in Hilt-based instrumentation tests."</p>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 19-2: Testing with Hilt -->
  <div class="subtopic" id="subtopic-19-2">
    <h2>Testing with Hilt</h2>
    <div class="card card-how">
      <h3>🛠️ Hilt Testing — Unit Tests &amp; Instrumentation Tests</h3>
      <pre class="code-block"><code class="language-kotlin">// ===== UNIT TEST — No Hilt needed, pure constructor injection =====
class HomeViewModelTest {
    private val fakeRepo = FakeProductRepository()
    private val fakeTracker = FakeAnalyticsTracker()
    private val testDispatchers = TestCoroutineDispatchers()

    private val viewModel = HomeViewModel(fakeRepo, fakeTracker, testDispatchers)

    @Test
    fun `loadProducts emits success state on valid response`() = runTest {
        fakeRepo.productsToReturn = listOf(Product("1", "Phone", 50000.0))

        viewModel.loadProducts()

        val state = viewModel.uiState.value
        assertTrue(state is HomeUiState.Success)
        assertEquals(1, (state as HomeUiState.Success).products.size)
    }
}

// Fake implementations for testing
class FakeProductRepository : ProductRepository {
    var productsToReturn: List&lt;Product&gt; = emptyList()
    var shouldThrow: Boolean = false
    override suspend fun getProducts(): List&lt;Product&gt; {
        if (shouldThrow) throw IOException("Network error")
        return productsToReturn
    }
}

class TestCoroutineDispatchers : CoroutineDispatchers {
    override val main = UnconfinedTestDispatcher()
    override val io = UnconfinedTestDispatcher()
    override val default = UnconfinedTestDispatcher()
}

// ===== INSTRUMENTATION TEST — using @HiltAndroidTest =====
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class ProductRepositoryImplTest {

    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var repository: ProductRepository  // Will be the test double

    @Before
    fun setUp() { hiltRule.inject() }

    @Test
    fun testRepositoryReturnsProducts() = runBlocking {
        val products = repository.getProducts()
        assertFalse(products.isEmpty())
    }
}

// Replace production module with test module
@TestInstallIn(
    components = [SingletonComponent::class],
    replaces = [RepositoryModule::class]
)
@Module
abstract class FakeRepositoryModule {
    @Binds @Singleton
    abstract fun bindFakeRepo(impl: FakeProductRepository): ProductRepository
}

// @EntryPoint for getting dependencies in tests without injection
@EntryPoint
@InstallIn(SingletonComponent::class)
interface TestEntryPoint {
    fun getProductDao(): ProductDao
}</code></pre>
    </div>
  </div>

  <!-- Q&A Section -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the difference between <code>@Provides</code> and <code>@Binds</code> in Hilt/Dagger?</div>
      <div class="qa-answer">
        <p><strong>@Provides:</strong> Used in a concrete class (or companion object). The method body instantiates and returns the dependency. Can do complex construction. Dagger calls this method every time the dependency is needed (unless scoped). Generates a module instance and calls the method.<br><br>
        <strong>@Binds:</strong> Used in an abstract class. The method has no body — it just tells Dagger "when someone asks for the interface, give them this concrete implementation." More efficient because Dagger generates direct code without a module instance. Can only be used when the binding is a simple interface-to-implementation mapping with no extra logic. Rule of thumb: use <code>@Binds</code> whenever you can, <code>@Provides</code> only when you must (third-party classes, complex construction).</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q2</span>Explain Hilt\'s component hierarchy and what "scope" means in this context.</div>
      <div class="qa-answer">
        <p>Hilt has a pre-defined component hierarchy: <code>SingletonComponent</code> → <code>ActivityRetainedComponent</code> → <code>ActivityComponent</code> → <code>FragmentComponent</code> → <code>ViewComponent</code>. Also: <code>ServiceComponent</code> and <code>ViewWithFragmentComponent</code>. A "scope" annotation ties an instance\'s lifetime to a component\'s lifetime. <code>@Singleton</code> = lives as long as <code>SingletonComponent</code> (app process). <code>@ActivityScoped</code> = one instance per Activity. Without a scope, a new instance is created every injection request. A component can only inject types from its own scope or parent scopes — never from child scopes (prevents the scope mismatch bug). <code>@ActivityRetainedScoped</code> is special — it survives configuration changes, making it the correct scope for ViewModels.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>How do you inject two different instances of the same type in Hilt (e.g., two different OkHttpClient instances)?</div>
      <div class="qa-answer">
        <p>Use <strong>Qualifier annotations</strong>. Create custom annotations with <code>@Qualifier</code> and <code>@Retention(BINARY)</code>, then annotate both the <code>@Provides</code> methods and the injection sites with the qualifier.</p>
        <pre class="code-block"><code class="language-kotlin">@Qualifier @Retention(AnnotationRetention.BINARY) annotation class Authenticated
@Qualifier @Retention(AnnotationRetention.BINARY) annotation class Anonymous

@Module @InstallIn(SingletonComponent::class)
object HttpModule {
    @Provides @Singleton @Authenticated
    fun provideAuthClient(interceptor: AuthInterceptor): OkHttpClient =
        OkHttpClient.Builder().addInterceptor(interceptor).build()

    @Provides @Singleton @Anonymous
    fun provideAnonClient(): OkHttpClient = OkHttpClient.Builder().build()
}

class ApiRepository @Inject constructor(
    @Authenticated private val authClient: OkHttpClient,
    @Anonymous private val anonClient: OkHttpClient
)</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q4</span>How do you unit test a ViewModel that uses Hilt for DI, without actually running Hilt?</div>
      <div class="qa-answer">
        <p>The key insight: <strong>don\'t use Hilt in unit tests</strong>. Unit tests should be pure JVM tests with no Android framework. Since Hilt uses constructor injection, you can instantiate the ViewModel directly by passing fake/mock dependencies to the constructor. This is the primary reason to always prefer constructor injection over field injection.</p>
        <pre class="code-block"><code class="language-kotlin">// No @HiltAndroidTest, no hiltRule — pure JUnit test
class OrderViewModelTest {
    @get:Rule val mainDispatcherRule = MainDispatcherRule()  // Sets Main dispatcher for tests

    private val fakeRepo = mockk&lt;OrderRepository&gt;()
    private val viewModel = OrderViewModel(fakeRepo)  // Direct constructor call

    @Test
    fun `place order success updates state to Success`() = runTest {
        coEvery { fakeRepo.placeOrder(any()) } returns Result.success(Order("123"))
        viewModel.placeOrder(mockCart)
        assertEquals(OrderState.Success::class, viewModel.orderState.value::class)
    }
}

class MainDispatcherRule(val dispatcher: TestCoroutineDispatcher = TestCoroutineDispatcher()) : TestWatcher() {
    override fun starting(description: Description) { Dispatchers.setMain(dispatcher) }
    override fun finished(description: Description) { Dispatchers.resetMain() }
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q5</span>What are Hilt Multibindings and when would you use them?</div>
      <div class="qa-answer">
        <p>Multibindings allow you to inject a <code>Set&lt;T&gt;</code> or <code>Map&lt;K, V&gt;</code> that contains multiple bound implementations. Use <code>@IntoSet</code> or <code>@IntoMap</code> on each <code>@Provides</code>/<code>@Binds</code> method. <strong>When to use:</strong> Plugin architectures, multiple analytics trackers (all fire on one event), feature flag evaluators, middleware pipelines, WorkerFactory that can create multiple Worker types. The key advantage: adding a new implementation is as simple as adding one new <code>@Binds @IntoSet</code> binding — zero changes to the consumer code.</p>
        <pre class="code-block"><code class="language-kotlin">// Map multibinding for WorkerFactory
@MapKey annotation class WorkerKey(val value: KClass&lt;out ListenableWorker&gt;)

@Module @InstallIn(SingletonComponent::class)
abstract class WorkerModule {
    @Binds @IntoMap @WorkerKey(SyncWorker::class)
    abstract fun bindSyncWorker(factory: SyncWorker.Factory): ChildWorkerFactory

    @Binds @IntoMap @WorkerKey(UploadWorker::class)
    abstract fun bindUploadWorker(factory: UploadWorker.Factory): ChildWorkerFactory
}

class HiltWorkerFactory @Inject constructor(
    private val creators: Map&lt;Class&lt;out ListenableWorker&gt;, @JvmSuppressWildcards ChildWorkerFactory&gt;
) : WorkerFactory() {
    override fun createWorker(ctx: Context, workerClass: String, params: WorkerParameters): ListenableWorker? {
        val factory = creators.entries.find { Class.forName(workerClass).isAssignableFrom(it.key) }?.value
        return factory?.create(ctx, params)
    }
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q6</span>Why is constructor injection preferred over field injection in Android?</div>
      <div class="qa-answer">
        <p><strong>Field injection</strong> (<code>@Inject lateinit var</code>) requires the object to be created before Hilt injects the fields — so the constructor can\'t use the fields, and they\'re nullable until injection happens (risk of NPE). Also: field injection only works with classes that Hilt knows about (annotated with <code>@AndroidEntryPoint</code> or <code>@HiltViewModel</code>), not plain Kotlin classes. <strong>Constructor injection</strong> provides dependencies at the moment of construction — the object is always in a valid state, fields can be <code>val</code> (immutable), and you can instantiate the class directly in tests without Hilt. Rule: use constructor injection for all non-Android-framework classes; use field injection only where it\'s unavoidable (Activity, Fragment, BroadcastReceiver — because Android creates these without calling your constructor).</p>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge — Design a Hilt Module for a Multi-Environment App</h3>
    <p><strong>Problem:</strong> Design Hilt modules for an app with DEBUG and RELEASE builds where DEBUG uses a mock API server and an in-memory database, RELEASE uses the real API and Room database. Demonstrate how to swap implementations without changing ViewModel code.</p>
    <pre class="code-block"><code class="language-kotlin">// Shared interface
interface AppDatabase {
    fun userDao(): UserDao
    fun productDao(): ProductDao
}

// Production implementation
class RoomAppDatabase @Inject constructor(
    @ApplicationContext context: Context
) : AppDatabase {
    private val db = Room.databaseBuilder(context, RoomDatabaseImpl::class.java, "app_db").build()
    override fun userDao() = db.userDao()
    override fun productDao() = db.productDao()
}

// Debug/Test implementation
class InMemoryAppDatabase @Inject constructor(
    @ApplicationContext context: Context
) : AppDatabase {
    private val db = Room.inMemoryDatabaseBuilder(context, RoomDatabaseImpl::class.java).build()
    override fun userDao() = db.userDao()
    override fun productDao() = db.productDao()
}

// Production module (in main source set)
@Module
@InstallIn(SingletonComponent::class)
abstract class DatabaseModule {
    @Binds @Singleton
    abstract fun bindDatabase(impl: RoomAppDatabase): AppDatabase
}

// Debug module (in debug source set — app/src/debug/)
@TestInstallIn(components = [SingletonComponent::class], replaces = [DatabaseModule::class])
@Module
abstract class DebugDatabaseModule {
    @Binds @Singleton
    abstract fun bindDatabase(impl: InMemoryAppDatabase): AppDatabase
}

// API base URL qualifier
@Qualifier @Retention(AnnotationRetention.BINARY)
annotation class BaseUrl

@Module @InstallIn(SingletonComponent::class)
object ApiConfigModule {
    @Provides @BaseUrl
    fun provideBaseUrl(): String = if (BuildConfig.DEBUG) "http://localhost:8080" else "https://api.prod.com"
}

// ViewModel doesn\'t change at all
@HiltViewModel
class ProductViewModel @Inject constructor(
    private val db: AppDatabase,   // Gets InMemory in debug, Room in release
    private val api: ProductApiService
) : ViewModel() { /* ... */ }</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="19" data-item="0"> ✅ Understood Hilt Component Hierarchy &amp; Scopes</label>
    <label class="progress-check"><input type="checkbox" data-topic="19" data-item="1"> ✅ Understood @Binds vs @Provides &amp; Qualifiers</label>
    <label class="progress-check"><input type="checkbox" data-topic="19" data-item="2"> ✅ Understood Multibindings</label>
    <label class="progress-check"><input type="checkbox" data-topic="19" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="19" data-item="4"> ✅ Solved Multi-Environment Module Challenge</label>
  </div>
</section>

<!-- ==================== TOPIC 20: NETWORKING — RETROFIT, OKHTTP, INTERCEPTORS ==================== -->
<section class="topic-section" id="topic-20">
  <div class="topic-header">
    <div class="topic-header-icon">🌐</div>
    <div class="topic-header-text">
      <h1>Networking — Retrofit, OkHttp &amp; Interceptors</h1>
      <p class="topic-tagline">Retrofit setup, OkHttp interceptors, token refresh, SSL pinning &amp; production patterns</p>
      <div class="category-badge-group">
        <span class="cat-pill">Retrofit</span>
        <span class="cat-pill">OkHttp</span>
        <span class="cat-pill">Interceptors</span>
        <span class="cat-pill">Security</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 20-1: Retrofit Setup -->
  <div class="subtopic" id="subtopic-20-1">
    <h2>Retrofit Setup &amp; Coroutines Integration</h2>

    <div class="card card-why">
      <h3>❓ Why Retrofit + OkHttp?</h3>
      <p>Making raw HTTP calls with <code>HttpURLConnection</code> requires enormous boilerplate: manually building URLs, serializing request bodies, reading response streams, handling redirects, managing connection pools, adding headers, and dealing with thread switching. OkHttp solves the low-level HTTP mechanics (connection pooling, GZIP, caching, HTTPS). Retrofit sits on top and adds the declarative API annotation layer — you define your HTTP endpoints as Kotlin interface methods, and Retrofit generates the implementation. Together they handle 95% of networking needs with production-level quality.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is Retrofit?</h3>
      <p>Retrofit is a type-safe HTTP client for Android/JVM. It uses annotation processing to convert your API interface methods into OkHttp calls. Key internals: each annotated method in your <code>interface</code> is proxied by a <code>ServiceMethod</code> that parses annotations at build time (not per-call), builds the HTTP request, executes it via OkHttp, and converts the response using a <code>Converter</code> (Moshi/Gson/etc.). With Kotlin coroutines support (via <code>suspend</code> functions), Retrofit automatically switches to the OkHttp thread pool for I/O and handles cancellation via coroutine cancellation.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work? — Full Production Setup</h3>
      <pre class="code-block"><code class="language-kotlin">// 1. API Interface — declarative HTTP endpoints
interface ProductApiService {
    @GET("v1/products")
    suspend fun getProducts(
        @Query("category") category: String?,
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20,
        @Header("Accept-Language") locale: String = "en"
    ): ApiResponse&lt;List&lt;ProductDto&gt;&gt;

    @GET("v1/products/{id}")
    suspend fun getProduct(@Path("id") id: String): ApiResponse&lt;ProductDto&gt;

    @POST("v1/cart/items")
    suspend fun addToCart(@Body request: AddToCartRequest): ApiResponse&lt;CartDto&gt;

    @PUT("v1/profile")
    suspend fun updateProfile(
        @Header("Authorization") token: String,
        @Body request: UpdateProfileRequest
    ): Response&lt;UserDto&gt;  // Raw Response for status code access

    @Multipart
    @POST("v1/profile/avatar")
    suspend fun uploadAvatar(
        @Part image: MultipartBody.Part
    ): ApiResponse&lt;AvatarResponse&gt;
}

// 2. Wrapper for API responses
data class ApiResponse&lt;T&gt;(
    val data: T?,
    val message: String?,
    val success: Boolean,
    val errorCode: String?
)

// 3. Retrofit + OkHttp builder (full production config)
@Singleton
class NetworkModule {
    @Provides @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor,
        loggingInterceptor: HttpLoggingInterceptor
    ): OkHttpClient = OkHttpClient.Builder()
        .addInterceptor(authInterceptor)         // Add auth header to every request
        .addInterceptor(loggingInterceptor)      // Log requests/responses in DEBUG
        .addNetworkInterceptor(ResponseCacheInterceptor())  // Cache-control headers
        .authenticator(TokenRefreshAuthenticator())  // Auto-refresh on 401
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .retryOnConnectionFailure(true)
        .cache(Cache(File(cacheDir, "http_cache"), 10 * 1024 * 1024L))  // 10MB cache
        .build()

    @Provides @Singleton
    fun provideMoshi(): Moshi = Moshi.Builder()
        .add(KotlinJsonAdapterFactory())
        .add(OffsetDateTimeAdapter())  // Custom date adapter
        .build()

    @Provides @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient, moshi: Moshi): Retrofit =
        Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()
}

// 4. Safe API call wrapper — converts Retrofit exceptions to domain errors
sealed class NetworkResult&lt;out T&gt; {
    data class Success&lt;T&gt;(val data: T) : NetworkResult&lt;T&gt;()
    data class Error(val code: Int, val message: String) : NetworkResult&lt;Nothing&gt;()
    object NetworkError : NetworkResult&lt;Nothing&gt;()
}

suspend fun &lt;T&gt; safeApiCall(block: suspend () -> T): NetworkResult&lt;T&gt; = try {
    NetworkResult.Success(block())
} catch (e: HttpException) {
    NetworkResult.Error(e.code(), e.message())
} catch (e: IOException) {
    NetworkResult.NetworkError
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// Retrofit annotations cheat sheet
@GET("endpoint")        // HTTP GET
@POST("endpoint")       // HTTP POST
@PUT("endpoint")        // HTTP PUT
@PATCH("endpoint")      // HTTP PATCH
@DELETE("endpoint")     // HTTP DELETE
@HEAD("endpoint")       // HTTP HEAD

@Path("id")             // URL path parameter: /users/{id}
@Query("page")          // URL query param: ?page=1
@QueryMap               // Multiple query params from Map
@Body                   // Request body (serialized by converter)
@Field("key")           // Form-encoded field (use with @FormUrlEncoded)
@Part                   // Multipart field (use with @Multipart)
@Header("key")          // Single header
@Headers("Key: Value")  // Static headers
@HeaderMap              // Multiple headers from Map

// Return types
suspend fun getItem(): ItemDto                  // Auto-unwrapped body
suspend fun getItem(): Response&lt;ItemDto&gt;        // Full HTTP response
suspend fun getItem(): ResponseBody             // Raw bytes
fun getItem(): Call&lt;ItemDto&gt;                    // Non-suspend, manual execution

// Moshi custom adapter example
class OffsetDateTimeAdapter {
    @ToJson fun toJson(value: OffsetDateTime): String = value.toString()
    @FromJson fun fromJson(value: String): OffsetDateTime = OffsetDateTime.parse(value)
}</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example — OkHttp Interceptors &amp; Token Refresh</h3>
      <pre class="code-block"><code class="language-kotlin">// AUTH INTERCEPTOR — adds Bearer token to every request
class AuthInterceptor @Inject constructor(
    private val tokenStore: TokenStore
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val token = tokenStore.getAccessToken()
        val request = if (token != null) {
            chain.request().newBuilder()
                .header("Authorization", "Bearer $token")
                .header("X-App-Version", BuildConfig.VERSION_NAME)
                .build()
        } else chain.request()
        return chain.proceed(request)
    }
}

// TOKEN REFRESH AUTHENTICATOR — called automatically on 401
class TokenRefreshAuthenticator @Inject constructor(
    private val tokenStore: TokenStore,
    private val authApi: AuthApiService  // Must use separate OkHttpClient without this authenticator!
) : Authenticator {
    @Volatile private var isRefreshing = false
    private val lock = Any()

    override fun authenticate(route: Route?, response: Response): Request? {
        // Prevent multiple simultaneous refresh attempts
        val newToken = synchronized(lock) {
            if (isRefreshing) {
                tokenStore.getAccessToken()  // Another thread already refreshed
            } else {
                isRefreshing = true
                try {
                    val refreshResponse = runBlocking {
                        authApi.refreshToken(RefreshRequest(tokenStore.getRefreshToken() ?: return@runBlocking null))
                    }
                    refreshResponse?.let {
                        tokenStore.saveTokens(it.accessToken, it.refreshToken)
                        it.accessToken
                    }
                } finally {
                    isRefreshing = false
                }
            }
        }
        return newToken?.let {
            response.request.newBuilder()
                .header("Authorization", "Bearer $it")
                .build()
        }
    }
}

// SSL PINNING — CertificatePinner
val certificatePinner = CertificatePinner.Builder()
    .add("api.mybank.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .add("api.mybank.com", "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=")  // Backup pin
    .build()

val pinnedClient = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build()

// LOGGING INTERCEPTOR — only in DEBUG
val loggingInterceptor = HttpLoggingInterceptor().apply {
    level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY
            else HttpLoggingInterceptor.Level.NONE
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Using same OkHttpClient for token refresh:</strong> The TokenRefreshAuthenticator calls the auth API using the same OkHttpClient that has the authenticator — infinite refresh loop. ✅ Fix: Create a separate "auth" OkHttpClient without the Authenticator for the refresh call.</li>
        <li>❌ <strong>Not handling concurrent 401s:</strong> Multiple requests fail simultaneously, each tries to refresh — gets multiple refresh tokens, invalidating each other. ✅ Fix: Use <code>synchronized</code> block with an <code>isRefreshing</code> flag.</li>
        <li>❌ <strong>Calling network on main thread:</strong> OkHttp itself is blocking — but <code>suspend</code> Retrofit functions use OkHttp\'s thread pool automatically. ✅ Fix: Always call Retrofit <code>suspend</code> functions from a coroutine (the thread switching is automatic).</li>
        <li>❌ <strong>Not pinning backup certificates:</strong> SSL pinning with only one pin causes app to fail if the certificate is renewed. ✅ Fix: Always pin at least 2 certificates (current + backup).</li>
        <li>❌ <strong>Logging sensitive data in production:</strong> <code>HttpLoggingInterceptor.Level.BODY</code> logs tokens, passwords, PII. ✅ Fix: Only enable BODY level in debug builds; use NONE in release.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"My standard network stack is Retrofit with Moshi (not Gson — Moshi is null-safe and works better with Kotlin data classes), on top of OkHttp. I separate concerns clearly: AuthInterceptor adds the Bearer token to every request, a separate Authenticator handles the 401 token refresh flow. The critical detail about token refresh is concurrency — you must synchronize the refresh so parallel failing requests don\'t each attempt a refresh and invalidate each other\'s tokens. I also wrap all API calls in a <code>safeApiCall</code> extension that converts HTTP exceptions and IOExceptions into a sealed <code>NetworkResult</code> class, so my repository layer returns clean domain types, not Retrofit-specific exceptions. For security in FinTech or health apps, I add certificate pinning with at minimum two pins — one current, one backup — and I never log request bodies in production builds."</p>
      </div>
    </div>
  </div>

  <!-- Q&A Section -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the difference between an OkHttp Interceptor and an Authenticator?</div>
      <div class="qa-answer">
        <p><strong>Interceptor:</strong> Intercepts every request/response, regardless of status code. Used to add headers, log, cache, modify requests/responses. Has two types: Application Interceptor (added via <code>addInterceptor</code> — runs before network, sees original request) and Network Interceptor (added via <code>addNetworkInterceptor</code> — runs after redirect/retry, sees exactly what goes over the wire).<br><br>
        <strong>Authenticator:</strong> Only called when a response returns HTTP 401 Unauthorized. OkHttp calls it to get a new authenticated request. If you return <code>null</code>, OkHttp gives up and returns the 401 response. It\'s specifically designed for token refresh scenarios — retry the request with fresh credentials. Returning the same request without changes will cause OkHttp to loop 3 times then give up.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q2</span>How would you implement a network request retry with exponential backoff using OkHttp?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">class RetryInterceptor(private val maxRetries: Int = 3) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        var attempt = 0
        var lastException: IOException? = null
        while (attempt <= maxRetries) {
            try {
                val response = chain.proceed(chain.request())
                if (response.isSuccessful || attempt == maxRetries) return response
                // Retry on server errors (5xx)
                if (response.code in 500..599) {
                    response.close()
                    Thread.sleep(exponentialBackoff(attempt))
                    attempt++
                    continue
                }
                return response
            } catch (e: IOException) {
                lastException = e
                if (attempt == maxRetries) throw e
                Thread.sleep(exponentialBackoff(attempt))
                attempt++
            }
        }
        throw lastException ?: IOException("Max retries reached")
    }
    private fun exponentialBackoff(attempt: Int): Long = (2.0.pow(attempt) * 1000).toLong()  // 1s, 2s, 4s
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>Explain how Moshi differs from Gson and why it\'s preferred for Kotlin.</div>
      <div class="qa-answer">
        <p><strong>Gson issues with Kotlin:</strong> (1) Gson bypasses Kotlin\'s constructor entirely — it uses reflection to set fields, ignoring <code>null</code> safety. A <code>data class User(val name: String)</code> can have <code>name</code> set to <code>null</code> if the JSON has <code>"name": null</code>. (2) Gson ignores default parameter values. (3) Gson doesn\'t understand Kotlin sealed classes or value classes natively.<br><br>
        <strong>Moshi advantages:</strong> (1) <code>KotlinJsonAdapterFactory</code> uses Kotlin reflection to respect nullability and default values. (2) Fails fast on null violations at the adapter level, not later when you access the field. (3) Codegen with <code>@JsonClass(generateAdapter = true)</code> generates adapters at compile time — faster and no reflection at runtime. (4) Supports sealed classes with custom adapters. (5) Better error messages.</p>
        <pre class="code-block"><code class="language-kotlin">@JsonClass(generateAdapter = true)  // Generates adapter at compile time — no reflection!
data class UserDto(
    val id: String,
    val name: String,
    @Json(name = "email_address") val email: String,  // Custom JSON key
    val age: Int = 0  // Default value respected by Moshi
)</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q4</span>Your app needs to upload a profile picture along with user metadata. How do you implement multipart upload with Retrofit?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">// API interface
@Multipart
@POST("v1/profile/avatar")
suspend fun uploadAvatar(
    @Part image: MultipartBody.Part,
    @Part("user_id") userId: RequestBody,
    @Part("description") description: RequestBody
): ApiResponse&lt;AvatarResponse&gt;

// Usage in repository
suspend fun uploadAvatar(userId: String, imageUri: Uri): Result&lt;String&gt; = runCatching {
    val imageFile = imageUri.toFile()  // Convert URI to File
    val requestBody = imageFile.asRequestBody("image/jpeg".toMediaType())
    val imagePart = MultipartBody.Part.createFormData("avatar", imageFile.name, requestBody)
    val userIdBody = userId.toRequestBody("text/plain".toMediaType())
    val descBody = "Profile photo".toRequestBody("text/plain".toMediaType())

    val response = api.uploadAvatar(imagePart, userIdBody, descBody)
    response.data?.avatarUrl ?: throw Exception("No URL returned")
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q5</span>How do you implement offline-first networking with OkHttp cache?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">// Network interceptor — sets cache headers based on connectivity
class OfflineCacheInterceptor(private val context: Context) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = if (!context.isNetworkAvailable()) {
            chain.request().newBuilder()
                .cacheControl(CacheControl.Builder()
                    .onlyIfCached()
                    .maxStale(7, TimeUnit.DAYS)  // Accept stale cache up to 7 days offline
                    .build())
                .build()
        } else {
            chain.request().newBuilder()
                .cacheControl(CacheControl.Builder()
                    .maxAge(5, TimeUnit.MINUTES)  // Fresh for 5 minutes
                    .build())
                .build()
        }
        return chain.proceed(request)
    }
}

val client = OkHttpClient.Builder()
    .cache(Cache(File(context.cacheDir, "http"), 20 * 1024 * 1024L))
    .addInterceptor(OfflineCacheInterceptor(context))
    .build()</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q6</span>What is SSL Pinning and what are its risks?</div>
      <div class="qa-answer">
        <p><strong>SSL Pinning:</strong> Instead of trusting any certificate signed by a trusted CA, you "pin" specific certificates or public keys that your app trusts. Even if an attacker gets a certificate signed by a trusted CA, they can\'t MITM your app because their certificate doesn\'t match the pins. <strong>Implementation:</strong> OkHttp\'s <code>CertificatePinner</code> with SHA-256 fingerprints of the server\'s certificate or public key.<br><br>
        <strong>Risks:</strong> (1) If you pin the leaf certificate and the server rotates it, your app breaks until users update. (2) During development, Charles/Fiddler proxies can\'t intercept traffic (by design — can disable in debug builds). (3) Forgetting to pin a backup certificate before certificate rotation causes production outage. <strong>Best practice:</strong> Pin the intermediate CA public key (more stable than leaf cert), always include at least one backup pin, and have a remote config kill switch to disable pinning in emergencies.</p>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge — Implement a Rate-Limiting Interceptor</h3>
    <p><strong>Problem:</strong> Implement an OkHttp interceptor that limits API calls to a maximum of 10 requests per second across all endpoints. Queue requests that exceed the limit.</p>
    <pre class="code-block"><code class="language-kotlin">class RateLimitingInterceptor(
    private val maxRequests: Int = 10,
    private val windowMillis: Long = 1000L
) : Interceptor {
    private val semaphore = Semaphore(maxRequests)
    private val requestTimestamps = ArrayDeque&lt;Long&gt;()
    private val lock = ReentrantLock()

    override fun intercept(chain: Interceptor.Chain): Response {
        waitForSlot()
        return try {
            chain.proceed(chain.request())
        } finally {
            // Slot is released by time, not explicitly
        }
    }

    private fun waitForSlot() {
        while (true) {
            lock.lock()
            try {
                val now = System.currentTimeMillis()
                // Remove timestamps outside the window
                while (requestTimestamps.isNotEmpty() && requestTimestamps.first() < now - windowMillis) {
                    requestTimestamps.removeFirst()
                }
                if (requestTimestamps.size < maxRequests) {
                    requestTimestamps.addLast(now)
                    return  // Slot available
                }
                // Calculate how long to wait until oldest request falls out of window
                val waitMs = windowMillis - (now - requestTimestamps.first()) + 1
                lock.unlock()
                Thread.sleep(waitMs)
                continue
            } finally {
                if (lock.isHeldByCurrentThread) lock.unlock()
            }
        }
    }
}

// Token bucket alternative (production preferred)
class TokenBucketInterceptor(
    private val capacity: Int = 10,
    private val refillRatePerSecond: Int = 10
) : Interceptor {
    private var tokens = capacity.toDouble()
    private var lastRefillTime = System.nanoTime()
    private val lock = Object()

    override fun intercept(chain: Interceptor.Chain): Response {
        synchronized(lock) {
            refill()
            while (tokens < 1) {
                val waitMs = ((1 - tokens) / refillRatePerSecond * 1000).toLong() + 1
                (lock as Object).wait(waitMs)
                refill()
            }
            tokens--
        }
        return chain.proceed(chain.request())
    }

    private fun refill() {
        val now = System.nanoTime()
        val elapsed = (now - lastRefillTime) / 1_000_000_000.0
        tokens = minOf(capacity.toDouble(), tokens + elapsed * refillRatePerSecond)
        lastRefillTime = now
    }
}
// Token Bucket is preferred: O(1) memory, smooth rate limiting vs bursty sliding window</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="20" data-item="0"> ✅ Understood Retrofit Setup &amp; Annotations</label>
    <label class="progress-check"><input type="checkbox" data-topic="20" data-item="1"> ✅ Understood OkHttp Interceptors &amp; Authenticator</label>
    <label class="progress-check"><input type="checkbox" data-topic="20" data-item="2"> ✅ Understood SSL Pinning &amp; Token Refresh</label>
    <label class="progress-check"><input type="checkbox" data-topic="20" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="20" data-item="4"> ✅ Solved Rate Limiting Challenge</label>
  </div>
</section>

<!-- ==================== TOPIC 21: ROOM DATABASE & LOCAL STORAGE ==================== -->
<section class="topic-section" id="topic-21">
  <div class="topic-header">
    <div class="topic-header-icon">🗄️</div>
    <div class="topic-header-text">
      <h1>Room Database &amp; Local Storage</h1>
      <p class="topic-tagline">Entity/DAO/Database, relationships, migrations, DataStore &amp; storage strategy</p>
      <div class="category-badge-group">
        <span class="cat-pill">Room</span>
        <span class="cat-pill">DataStore</span>
        <span class="cat-pill">SQLite</span>
        <span class="cat-pill">Local Storage</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 21-1: Room Setup -->
  <div class="subtopic" id="subtopic-21-1">
    <h2>Room: Entity, DAO, Database &amp; Relationships</h2>

    <div class="card card-why">
      <h3>❓ Why Room Instead of Raw SQLite?</h3>
      <p>Raw SQLite requires: writing SQL strings by hand (compile-time no verification), manually mapping <code>Cursor</code> to objects (tedious, error-prone), managing database versions and migrations yourself, handling threading manually (database operations must not run on the main thread). Room solves all of this: SQL is verified at compile time (annotation processor checks your queries against your schema), Room auto-generates the mapping code via generated DAO implementations, provides first-class <code>Flow</code> support for reactive queries, and handles threading correctly. It also integrates with Hilt for DI.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is Room?</h3>
      <p>Room is Android\'s official ORM (Object-Relational Mapping) library built on SQLite. It has three main components: <strong>Entity</strong> — a data class annotated with <code>@Entity</code> that maps to a database table. <strong>DAO</strong> (Data Access Object) — an interface annotated with <code>@Dao</code> that defines database operations; Room generates the implementation. <strong>Database</strong> — an abstract class annotated with <code>@Database</code> that is the main access point; Room generates a concrete implementation using the Singleton pattern internally.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work? — Full Production Setup with Relationships</h3>
      <pre class="code-block"><code class="language-kotlin">// ===== ENTITIES =====
@Entity(tableName = "users",
    indices = [Index(value = ["email"], unique = true)])
data class UserEntity(
    @PrimaryKey val id: String,
    val name: String,
    val email: String,
    @ColumnInfo(name = "created_at") val createdAt: Long = System.currentTimeMillis(),
    @ColumnInfo(name = "is_active") val isActive: Boolean = true
)

@Entity(tableName = "orders",
    foreignKeys = [ForeignKey(
        entity = UserEntity::class,
        parentColumns = ["id"],
        childColumns = ["user_id"],
        onDelete = ForeignKey.CASCADE  // Delete orders when user is deleted
    )],
    indices = [Index("user_id")]
)
data class OrderEntity(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "user_id") val userId: String,
    val total: Double,
    val status: String,
    @ColumnInfo(name = "placed_at") val placedAt: Long = System.currentTimeMillis()
)

@Entity(tableName = "order_items",
    primaryKeys = ["order_id", "product_id"],  // Composite primary key
    foreignKeys = [ForeignKey(entity = OrderEntity::class,
        parentColumns = ["id"], childColumns = ["order_id"], onDelete = ForeignKey.CASCADE)]
)
data class OrderItemEntity(
    @ColumnInfo(name = "order_id") val orderId: String,
    @ColumnInfo(name = "product_id") val productId: String,
    val quantity: Int,
    val price: Double
)

// ===== RELATIONSHIPS =====
data class UserWithOrders(
    @Embedded val user: UserEntity,
    @Relation(parentColumn = "id", entityColumn = "user_id")
    val orders: List&lt;OrderEntity&gt;
)

data class OrderWithItems(
    @Embedded val order: OrderEntity,
    @Relation(parentColumn = "id", entityColumn = "order_id")
    val items: List&lt;OrderItemEntity&gt;
)

// ===== DAO =====
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    fun getUserById(id: String): Flow&lt;UserEntity?&gt;  // Reactive — emits on every DB change

    @Query("SELECT * FROM users WHERE is_active = 1 ORDER BY created_at DESC")
    fun getAllActiveUsers(): Flow&lt;List&lt;UserEntity&gt;&gt;

    @Transaction
    @Query("SELECT * FROM users WHERE id = :userId")
    fun getUserWithOrders(userId: String): Flow&lt;UserWithOrders?&gt;

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: UserEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUsers(users: List&lt;UserEntity&gt;)

    @Update
    suspend fun updateUser(user: UserEntity)

    @Delete
    suspend fun deleteUser(user: UserEntity)

    @Query("DELETE FROM users WHERE id = :id")
    suspend fun deleteUserById(id: String)

    @Query("UPDATE users SET is_active = :isActive WHERE id = :id")
    suspend fun setUserActive(id: String, isActive: Boolean)

    // Paging support
    @Query("SELECT * FROM users ORDER BY name ASC")
    fun getUsersPaginated(): PagingSource&lt;Int, UserEntity&gt;
}

@Dao
interface OrderDao {
    @Transaction
    @Query("SELECT * FROM orders WHERE user_id = :userId ORDER BY placed_at DESC")
    fun getOrdersWithItems(userId: String): Flow&lt;List&lt;OrderWithItems&gt;&gt;

    @Transaction
    suspend fun insertOrderWithItems(order: OrderEntity, items: List&lt;OrderItemEntity&gt;) {
        insertOrder(order)
        insertItems(items)
    }

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertOrder(order: OrderEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertItems(items: List&lt;OrderItemEntity&gt;)

    // Raw query for complex dynamic queries
    @RawQuery(observedEntities = [OrderEntity::class])
    fun getOrdersRaw(query: SupportSQLiteQuery): Flow&lt;List&lt;OrderEntity&gt;&gt;
}

// ===== DATABASE =====
@Database(
    entities = [UserEntity::class, OrderEntity::class, OrderItemEntity::class],
    version = 3,
    exportSchema = true  // Export to JSON for migration testing
)
@TypeConverters(DateConverters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun orderDao(): OrderDao

    companion object {
        @Volatile private var INSTANCE: AppDatabase? = null
        fun getInstance(context: Context): AppDatabase =
            INSTANCE ?: synchronized(this) {
                INSTANCE ?: Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "app_database"
                )
                .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
                .fallbackToDestructiveMigration()  // Last resort — data loss
                .build().also { INSTANCE = it }
            }
    }
}

// TypeConverter example
class DateConverters {
    @TypeConverter fun fromTimestamp(value: Long?): Date? = value?.let { Date(it) }
    @TypeConverter fun dateToTimestamp(date: Date?): Long? = date?.time
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Migrations &amp; TypeConverters</h3>
      <pre class="code-block"><code class="language-kotlin">// ===== MIGRATIONS — never use fallbackToDestructiveMigration in production =====
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        // Add new column with default value
        database.execSQL("ALTER TABLE users ADD COLUMN phone_number TEXT")
        // Create new table
        database.execSQL("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT NOT NULL PRIMARY KEY,
                theme TEXT NOT NULL DEFAULT 'system',
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """.trimIndent())
    }
}

val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(database: SupportSQLiteDatabase) {
        // Rename column (SQLite doesn\'t support ALTER COLUMN — need recreate)
        database.execSQL("ALTER TABLE orders ADD COLUMN currency TEXT NOT NULL DEFAULT 'INR'")
        // Create index
        database.execSQL("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
    }
}

// ===== ROOM with custom type =====
enum class OrderStatus { PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED }

class OrderStatusConverter {
    @TypeConverter fun toStatus(value: String): OrderStatus = enumValueOf(value)
    @TypeConverter fun fromStatus(status: OrderStatus): String = status.name
}

// ===== RAW QUERY for dynamic filtering =====
fun buildOrderQuery(userId: String, status: OrderStatus?, fromDate: Long?): SupportSQLiteQuery {
    val sb = StringBuilder("SELECT * FROM orders WHERE user_id = ?")
    val args = mutableListOf&lt;Any&gt;(userId)
    if (status != null) { sb.append(" AND status = ?"); args.add(status.name) }
    if (fromDate != null) { sb.append(" AND placed_at &gt;= ?"); args.add(fromDate) }
    sb.append(" ORDER BY placed_at DESC")
    return SimpleSQLiteQuery(sb.toString(), args.toTypedArray())
}</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example — SharedPreferences vs DataStore vs Room</h3>
      <pre class="code-block"><code class="language-kotlin">// RULE OF THUMB:
// SharedPreferences — simple key-value, synchronous, small data. AVOID in new code.
// DataStore (Proto/Preferences) — key-value or proto-based, async/coroutine-native, safe. PREFER over SharedPreferences.
// Room — structured, relational, queryable data. PREFER for lists, complex data.

// ===== DATASTORE — modern replacement for SharedPreferences =====
// Proto DataStore (type-safe, requires .proto file)
// OR Preferences DataStore (like SharedPreferences but coroutine-based)

val Context.dataStore: DataStore&lt;Preferences&gt; by preferencesDataStore(name = "settings")

object PreferencesKeys {
    val AUTH_TOKEN = stringPreferencesKey("auth_token")
    val USER_ID = stringPreferencesKey("user_id")
    val DARK_MODE = booleanPreferencesKey("dark_mode")
    val NOTIFICATION_ENABLED = booleanPreferencesKey("notifications")
}

class UserPreferencesRepository(private val dataStore: DataStore&lt;Preferences&gt;) {
    // Read — returns Flow, updates reactively when preferences change
    val authToken: Flow&lt;String?&gt; = dataStore.data
        .catch { if (it is IOException) emit(emptyPreferences()) else throw it }
        .map { prefs -> prefs[PreferencesKeys.AUTH_TOKEN] }

    val isDarkMode: Flow&lt;Boolean&gt; = dataStore.data
        .map { it[PreferencesKeys.DARK_MODE] ?: false }

    // Write — suspend function, runs on DataStore\'s background dispatcher
    suspend fun saveAuthToken(token: String) {
        dataStore.edit { prefs -> prefs[PreferencesKeys.AUTH_TOKEN] = token }
    }

    suspend fun clearSession() {
        dataStore.edit { prefs ->
            prefs.remove(PreferencesKeys.AUTH_TOKEN)
            prefs.remove(PreferencesKeys.USER_ID)
        }
    }

    // Atomic read-modify-write
    suspend fun toggleDarkMode() {
        dataStore.edit { prefs ->
            prefs[PreferencesKeys.DARK_MODE] = !(prefs[PreferencesKeys.DARK_MODE] ?: false)
        }
    }
}

// When to use what:
// Auth token, user settings -> DataStore (small, key-value, reactive)
// User profile data cached from API -> Room (structured, queryable)
// Product catalog, orders, cart -> Room (relational, needs queries)
// Temp file, downloaded content -> File storage (Internal/External storage)</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Missing @Transaction on relationship queries:</strong> Querying relations without <code>@Transaction</code> can return inconsistent data if the DB changes between queries. ✅ Fix: Always annotate relationship queries with <code>@Transaction</code>.</li>
        <li>❌ <strong>Using allowMainThreadQueries():</strong> This allows blocking DB calls on the main thread — causes ANRs. ✅ Fix: Never use this in production; always use <code>suspend</code> functions and collect <code>Flow</code> from coroutines.</li>
        <li>❌ <strong>Not exporting schema:</strong> Without <code>exportSchema = true</code>, you lose migration test capability. ✅ Fix: Set <code>exportSchema = true</code> and add the schema directory to version control.</li>
        <li>❌ <strong>Using fallbackToDestructiveMigration in production:</strong> This deletes all data on schema mismatch. ✅ Fix: Write proper migrations; use destructive migration only for debug builds.</li>
        <li>❌ <strong>SharedPreferences for sensitive data:</strong> SharedPreferences is plain XML on disk, readable on rooted devices. ✅ Fix: Use EncryptedSharedPreferences or DataStore with encryption for tokens/passwords.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"My local storage strategy is: Room for any structured data that needs querying, DataStore for user preferences and settings, and EncryptedSharedPreferences for sensitive items like auth tokens (though DataStore with EncryptedFile is even better). For Room, the most important production practice is treating migrations as first-class citizens — I export the schema to JSON, store it in version control, and have automated tests that verify each migration path. I never use <code>fallbackToDestructiveMigration</code> in production builds. For reactive UI, Room\'s <code>Flow</code> return type is excellent — the UI automatically updates when data changes, and it cancels cleanly with lifecycle. For complex filtering UI where query parameters are dynamic, I use <code>@RawQuery</code> with <code>SimpleSQLiteQuery</code> — it\'s less type-safe but necessary for dynamic SQL."</p>
      </div>
    </div>
  </div>

  <!-- Q&A Section -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What are the three main components of Room and what does each do?</div>
      <div class="qa-answer">
        <p><strong>@Entity:</strong> Maps to a database table. Annotate a data class with <code>@Entity</code> and its fields become columns. Use <code>@PrimaryKey</code>, <code>@ColumnInfo</code>, <code>@ForeignKey</code>, <code>@Index</code> for fine-grained control.<br><br>
        <strong>@Dao:</strong> Data Access Object — an interface where you declare SQL operations as methods. Annotated with <code>@Query</code>, <code>@Insert</code>, <code>@Update</code>, <code>@Delete</code>. Room\'s annotation processor generates the concrete implementation at compile time, verifying all SQL queries against your schema.<br><br>
        <strong>@Database:</strong> The database holder — an abstract class extending <code>RoomDatabase</code>. Declares the list of entities, version number, and abstract methods returning DAO instances. Room generates the implementation using SQLite. Should be a Singleton.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q2</span>How do you handle database migrations in Room without losing user data?</div>
      <div class="qa-answer">
        <p>Create a <code>Migration</code> object for each version increment, implementing <code>migrate(SupportSQLiteDatabase)</code> with the SQL DDL changes. Register all migrations in the database builder. Key migration operations: <code>ALTER TABLE ADD COLUMN</code> (safest), recreating a table (for column rename/delete since SQLite doesn\'t support those), creating/dropping indexes, creating new tables. For testing: use <code>MigrationTestHelper</code> from Room\'s test artifact to verify each migration preserves data correctly. Never skip migration versions — if a user has version 1 and current is version 5, Room applies 1→2, 2→3, 3→4, 4→5 in sequence.</p>
        <pre class="code-block"><code class="language-kotlin">// Testing migrations
@RunWith(AndroidJUnit4::class)
class MigrationTest {
    private val TEST_DB = "migration-test"
    @get:Rule val helper = MigrationTestHelper(InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java)

    @Test
    fun migrate1to2() {
        helper.createDatabase(TEST_DB, 1).apply {
            execSQL("INSERT INTO users VALUES ('user1', 'John', 'john@test.com', 1234567890, 1)")
            close()
        }
        val db = helper.runMigrationsAndValidate(TEST_DB, 2, true, MIGRATION_1_2)
        val cursor = db.query("SELECT phone_number FROM users WHERE id = 'user1'")
        cursor.moveToFirst()
        assertNull(cursor.getString(0))  // New column should be null
    }
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>What is the difference between DataStore and SharedPreferences? Why should you migrate?</div>
      <div class="qa-answer">
        <p><strong>SharedPreferences issues:</strong> (1) Synchronous <code>commit()</code> blocks the calling thread; <code>apply()</code> is async but provides no error signal. (2) Not safe to call from multiple threads or processes. (3) <code>getSharedPreferences()</code> can throw <code>ClassCastException</code> at runtime if types are mixed up. (4) No type safety. (5) No atomic batch edits with proper error handling.<br><br>
        <strong>DataStore advantages:</strong> (1) Built on Kotlin coroutines + Flow — fully async, never blocks. (2) Handles IOException gracefully. (3) Type-safe with Kotlin generics. (4) Atomic read-modify-write operations. (5) Proto DataStore gives full type safety with protocol buffers. (6) Consistent state — either all changes in an <code>edit { }</code> block are committed, or none. Migration is simple: DataStore has a <code>SharedPreferencesMigration</code> that reads existing SharedPreferences data on first launch.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q4</span>How do you implement an offline-first architecture with Room and Retrofit?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">// Offline-first repository — single source of truth is the database
class ProductRepository @Inject constructor(
    private val api: ProductApiService,
    private val dao: ProductDao,
    private val networkMonitor: NetworkMonitor
) {
    fun getProducts(category: String): Flow&lt;Resource&lt;List&lt;Product&gt;&gt;&gt; = flow {
        emit(Resource.Loading())

        // 1. Emit cached data immediately
        val cached = dao.getProductsByCategory(category).first()
        if (cached.isNotEmpty()) emit(Resource.Success(cached.map { it.toProduct() }))

        // 2. If online, fetch fresh data
        if (networkMonitor.isConnected()) {
            try {
                val fresh = api.getProducts(category)
                dao.deleteByCategory(category)      // Invalidate cache
                dao.insertAll(fresh.map { it.toEntity() })
                // 3. Room\'s Flow automatically re-emits with new data
            } catch (e: IOException) {
                if (cached.isEmpty()) emit(Resource.Error("No cached data and network unavailable"))
            }
        }
    }
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q5</span>What is @Transaction in Room and why is it important for relationship queries?</div>
      <div class="qa-answer">
        <p><code>@Transaction</code> wraps the function body in a SQLite transaction. For queries that return related objects (one-to-many, many-to-many via <code>@Relation</code>), Room issues multiple SQL queries internally — one for the parent entity and one for each related entity type. Without <code>@Transaction</code>, another thread could modify the database between these queries, resulting in inconsistent data (e.g., you get a User with orders that no longer belong to them). <code>@Transaction</code> also helps with batch inserts/updates — if one fails, all are rolled back. Performance benefit: batch operations inside a transaction are much faster (one <code>fsync</code> instead of N).</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q6</span>How would you handle a many-to-many relationship in Room (e.g., Students and Courses)?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">@Entity data class Student(@PrimaryKey val studentId: String, val name: String)
@Entity data class Course(@PrimaryKey val courseId: String, val title: String)

// Junction / Cross-reference table
@Entity(tableName = "student_course_cross_ref",
    primaryKeys = ["studentId", "courseId"])
data class StudentCourseCrossRef(val studentId: String, val courseId: String)

// Relationship class
data class StudentWithCourses(
    @Embedded val student: Student,
    @Relation(
        parentColumn = "studentId",
        entityColumn = "courseId",
        associateBy = Junction(StudentCourseCrossRef::class)
    )
    val courses: List&lt;Course&gt;
)

data class CourseWithStudents(
    @Embedded val course: Course,
    @Relation(
        parentColumn = "courseId",
        entityColumn = "studentId",
        associateBy = Junction(StudentCourseCrossRef::class)
    )
    val students: List&lt;Student&gt;
)

@Dao interface CourseDao {
    @Transaction @Query("SELECT * FROM Student")
    fun getStudentsWithCourses(): Flow&lt;List&lt;StudentWithCourses&gt;&gt;

    @Insert suspend fun enrollStudent(crossRef: StudentCourseCrossRef)
    @Delete suspend fun unenrollStudent(crossRef: StudentCourseCrossRef)
}</code></pre>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge — Implement a Search with Room FTS</h3>
    <p><strong>Problem:</strong> Implement full-text search on product titles and descriptions using Room\'s FTS4 support. Results should be ranked by relevance.</p>
    <pre class="code-block"><code class="language-kotlin">// FTS (Full-Text Search) entity — creates a virtual table with FTS4 index
@Fts4(contentEntity = ProductEntity::class)
@Entity(tableName = "products_fts")
data class ProductFtsEntity(
    val title: String,
    val description: String
)

// Regular entity
@Entity(tableName = "products")
data class ProductEntity(
    @PrimaryKey val rowid: Long = 0,  // Must be Long rowid for FTS content entity
    val id: String,
    val title: String,
    val description: String,
    val price: Double,
    val category: String
)

@Dao
interface ProductSearchDao {
    // FTS MATCH query — much faster than LIKE for text search
    @Transaction
    @Query("""
        SELECT products.* FROM products
        INNER JOIN products_fts ON products.rowid = products_fts.rowid
        WHERE products_fts MATCH :query
        ORDER BY bm25(products_fts) ASC
    """)
    fun searchProducts(query: String): Flow&lt;List&lt;ProductEntity&gt;&gt;

    // Escape and format query for FTS (handle special characters)
    companion object {
        fun formatFtsQuery(input: String): String {
            // Escape special FTS characters, add wildcard for prefix matching
            val escaped = input.trim()
                .replace("\"", "\"\"")
                .replace("\'", "\'\'")
            return if (escaped.isBlank()) "" else "\"$escaped\"*"
        }
    }
}

// Repository usage with debounce for search
class ProductSearchRepository @Inject constructor(private val dao: ProductSearchDao) {
    fun search(query: StateFlow&lt;String&gt;): Flow&lt;List&lt;Product&gt;&gt; =
        query
            .debounce(300)  // Wait 300ms after user stops typing
            .filter { it.length &gt;= 2 }  // Minimum 2 characters
            .flatMapLatest { input ->
                val ftsQuery = ProductSearchDao.formatFtsQuery(input)
                if (ftsQuery.isBlank()) flowOf(emptyList())
                else dao.searchProducts(ftsQuery).map { list -> list.map { it.toProduct() } }
            }
}
// FTS4 MATCH is orders of magnitude faster than LIKE \'%query%\' for large datasets
// bm25() is a relevance ranking function — lower values = better match</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="21" data-item="0"> ✅ Understood Room Entity/DAO/Database</label>
    <label class="progress-check"><input type="checkbox" data-topic="21" data-item="1"> ✅ Understood Relationships &amp; Migrations</label>
    <label class="progress-check"><input type="checkbox" data-topic="21" data-item="2"> ✅ Understood DataStore vs SharedPreferences</label>
    <label class="progress-check"><input type="checkbox" data-topic="21" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="21" data-item="4"> ✅ Solved FTS Search Challenge</label>
  </div>
</section>

<!-- ==================== TOPIC 22: WORKMANAGER & BACKGROUND PROCESSING ==================== -->
<section class="topic-section" id="topic-22">
  <div class="topic-header">
    <div class="topic-header-icon">⚙️</div>
    <div class="topic-header-text">
      <h1>WorkManager &amp; Background Processing</h1>
      <p class="topic-tagline">WorkManager vs Service vs AlarmManager, constraints, chaining, Doze mode &amp; expedited work</p>
      <div class="category-badge-group">
        <span class="cat-pill">WorkManager</span>
        <span class="cat-pill">Background</span>
        <span class="cat-pill">Coroutines</span>
        <span class="cat-pill">Battery</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 22-1: WorkManager Fundamentals -->
  <div class="subtopic" id="subtopic-22-1">
    <h2>WorkManager Fundamentals &amp; When to Use It</h2>

    <div class="card card-why">
      <h3>❓ Why WorkManager? The Background Problem</h3>
      <p>Android aggressively kills background processes to conserve battery (since Android 6.0 Doze mode, 8.0 background execution limits, 12.0 exact alarms restrictions). The challenge: you need to sync data, upload logs, send analytics, process images — but Android might kill your process at any time. <strong>Without WorkManager:</strong> <code>Service</code> can be killed; <code>AlarmManager</code> doesn\'t handle network constraints or retries; manual threading doesn\'t survive process death; <code>JobScheduler</code> is API 21+ and verbose; Firebase JobDispatcher is deprecated. <strong>WorkManager</strong> is the unified, battery-aware, backwards-compatible API for deferrable, guaranteed background work.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is WorkManager?</h3>
      <p>WorkManager is part of Android Jetpack. It guarantees work execution even if the app exits or the device restarts. Internally, it chooses the best underlying implementation: <code>JobScheduler</code> (API 23+), <code>AlarmManager</code> (API 14-22 — not used for new code). WorkManager persists work requests in an internal Room database, so pending work survives process death and device reboots. It supports: constraints (network, battery, storage), chaining workers into sequential or parallel pipelines, observing work status via <code>Flow</code>/<code>LiveData</code>, and exponential backoff on failure.<br><br>
      <strong>Key distinction:</strong> WorkManager is for <em>deferrable</em> work. If you need immediate, long-running foreground work (like a music player), use a foreground Service. If you need precise timing, use <code>AlarmManager</code> with <code>setExactAndAllowWhileIdle</code>.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work? — CoroutineWorker &amp; Constraints</h3>
      <pre class="code-block"><code class="language-kotlin">// ===== BASIC COROUTINEWORKER =====
class SyncDataWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted workerParams: WorkerParameters,
    private val syncRepository: SyncRepository,
    private val notificationManager: NotificationManagerCompat
) : CoroutineWorker(context, workerParams) {

    override suspend fun doWork(): Result {
        // This runs on Dispatchers.Default by default for CoroutineWorker
        // Override getCoroutineContext() to use a specific dispatcher
        val userId = inputData.getString(KEY_USER_ID)
            ?: return Result.failure(workDataOf(KEY_ERROR to "Missing user ID"))

        return try {
            setProgress(workDataOf(KEY_PROGRESS to 10))
            val data = syncRepository.fetchRemoteData(userId)
            setProgress(workDataOf(KEY_PROGRESS to 60))
            syncRepository.saveLocally(data)
            setProgress(workDataOf(KEY_PROGRESS to 100))
            Result.success(workDataOf(KEY_SYNCED_COUNT to data.size))
        } catch (e: IOException) {
            if (runAttemptCount < MAX_RETRIES) Result.retry()  // Retry with backoff
            else Result.failure(workDataOf(KEY_ERROR to e.message))
        } catch (e: Exception) {
            Result.failure(workDataOf(KEY_ERROR to e.message))  // Non-retryable failure
        }
    }

    // Foreground service info for long-running work (Android 12+)
    override suspend fun getForegroundInfo(): ForegroundInfo {
        val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setContentTitle("Syncing data...")
            .setSmallIcon(R.drawable.ic_sync)
            .setProgress(0, 0, true)
            .setOngoing(true)
            .build()
        return ForegroundInfo(NOTIFICATION_ID, notification)
    }

    companion object {
        const val KEY_USER_ID = "user_id"
        const val KEY_PROGRESS = "progress"
        const val KEY_SYNCED_COUNT = "synced_count"
        const val KEY_ERROR = "error"
        const val MAX_RETRIES = 3
        const val NOTIFICATION_ID = 101
        const val CHANNEL_ID = "sync_channel"
    }

    @AssistedFactory
    interface Factory : ChildWorkerFactory
}

// ===== SCHEDULING WORK =====
class WorkScheduler @Inject constructor(
    @ApplicationContext private val context: Context
) {
    // ONE-TIME WORK
    fun scheduleSyncNow(userId: String) {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()

        val syncRequest = OneTimeWorkRequestBuilder&lt;SyncDataWorker&gt;()
            .setConstraints(constraints)
            .setInputData(workDataOf(SyncDataWorker.KEY_USER_ID to userId))
            .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
            .addTag(TAG_SYNC)
            .build()

        WorkManager.getInstance(context)
            .enqueueUniqueWork(UNIQUE_SYNC_WORK, ExistingWorkPolicy.KEEP, syncRequest)
    }

    // PERIODIC WORK — minimum 15 minutes interval (system-enforced)
    fun schedulePeriodicSync(userId: String) {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.UNMETERED)  // Only on WiFi
            .setRequiresCharging(false)
            .build()

        val periodicRequest = PeriodicWorkRequestBuilder&lt;SyncDataWorker&gt;(1, TimeUnit.HOURS)
            .setConstraints(constraints)
            .setInputData(workDataOf(SyncDataWorker.KEY_USER_ID to userId))
            .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 15, TimeUnit.MINUTES)
            .addTag(TAG_PERIODIC_SYNC)
            .build()

        WorkManager.getInstance(context)
            .enqueueUniquePeriodicWork(
                UNIQUE_PERIODIC_SYNC,
                ExistingPeriodicWorkPolicy.UPDATE,  // Update if already scheduled
                periodicRequest
            )
    }

    companion object {
        const val TAG_SYNC = "sync"
        const val TAG_PERIODIC_SYNC = "periodic_sync"
        const val UNIQUE_SYNC_WORK = "unique_sync_work"
        const val UNIQUE_PERIODIC_SYNC = "unique_periodic_sync"
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Chaining Workers &amp; Observing Status</h3>
      <pre class="code-block"><code class="language-kotlin">// ===== WORKER CHAINING — sequential and parallel =====
// Sequential: download -> process -> upload
val downloadWork = OneTimeWorkRequestBuilder&lt;DownloadWorker&gt;()
    .setInputData(workDataOf("url" to imageUrl))
    .build()
val processWork = OneTimeWorkRequestBuilder&lt;ProcessImageWorker&gt;().build()
val uploadWork = OneTimeWorkRequestBuilder&lt;UploadWorker&gt;().build()
val notifyWork = OneTimeWorkRequestBuilder&lt;NotificationWorker&gt;().build()

// Data flows from one worker to the next via Result.success(workDataOf(...))
WorkManager.getInstance(context)
    .beginUniqueWork("image_pipeline", ExistingWorkPolicy.REPLACE, downloadWork)
    .then(processWork)
    .then(uploadWork)
    .then(notifyWork)
    .enqueue()

// Parallel merge: multiple downloads, then a single combine step
val download1 = OneTimeWorkRequestBuilder&lt;DownloadWorker&gt;().build()
val download2 = OneTimeWorkRequestBuilder&lt;DownloadWorker&gt;().build()
val combineWork = OneTimeWorkRequestBuilder&lt;CombineWorker&gt;().build()

WorkManager.getInstance(context)
    .beginWith(listOf(download1, download2))  // Parallel
    .then(combineWork)                         // Runs when ALL parallel complete
    .enqueue()

// ===== OBSERVING WORK STATUS =====
// From ViewModel — observe as Flow
class SyncViewModel @Inject constructor(
    @ApplicationContext private val context: Context
) : ViewModel() {
    val syncStatus: Flow&lt;WorkInfo?&gt; = WorkManager.getInstance(context)
        .getWorkInfosByTagFlow(WorkScheduler.TAG_SYNC)
        .map { infos -> infos.firstOrNull() }

    val syncProgress: Flow&lt;Int&gt; = syncStatus
        .filterNotNull()
        .map { info -> info.progress.getInt(SyncDataWorker.KEY_PROGRESS, 0) }
}

// In Fragment
viewLifecycleOwner.lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.syncStatus.collect { workInfo ->
            when (workInfo?.state) {
                WorkInfo.State.ENQUEUED  -> showStatus("Queued...")
                WorkInfo.State.RUNNING   -> showProgress(workInfo.progress.getInt("progress", 0))
                WorkInfo.State.SUCCEEDED -> showSuccess(workInfo.outputData.getInt("synced_count", 0))
                WorkInfo.State.FAILED    -> showError(workInfo.outputData.getString("error"))
                WorkInfo.State.CANCELLED -> showStatus("Cancelled")
                else -> Unit
            }
        }
    }
}

// ===== EXPEDITED WORK (Android 12+) — runs immediately, exempt from Doze =====
val expeditedRequest = OneTimeWorkRequestBuilder&lt;CriticalSyncWorker&gt;()
    .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
    .build()
// Worker must override getForegroundInfo() to support pre-API-31 fallback</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example — Healthcare App: Medical Record Sync</h3>
      <pre class="code-block"><code class="language-kotlin">// Healthcare app: sync patient vitals from wearable to cloud
// Must work offline, handle network failures, preserve data integrity

class VitalsSyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val vitalsDao: VitalsDao,
    private val healthApi: HealthApiService,
    private val encryptionService: EncryptionService
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        val patientId = inputData.getString("patient_id") ?: return@withContext Result.failure()

        // 1. Get unsynced vitals from local DB
        val unsynced = vitalsDao.getUnsyncedVitals(patientId)
        if (unsynced.isEmpty()) return@withContext Result.success()

        setForeground(buildForegroundInfo(unsynced.size))

        // 2. Encrypt before transmission (HIPAA compliance)
        val encryptedBatch = unsynced.map { vital ->
            encryptionService.encrypt(vital.toJson())
        }

        // 3. Upload in batches of 50
        val batches = encryptedBatch.chunked(50)
        var successCount = 0
        for ((index, batch) in batches.withIndex()) {
            try {
                val response = healthApi.uploadVitalsBatch(
                    patientId = patientId,
                    vitals = batch,
                    batchIndex = index,
                    totalBatches = batches.size
                )
                // 4. Mark as synced only after server confirms
                val syncedIds = response.confirmedIds
                vitalsDao.markAsSynced(syncedIds)
                successCount += syncedIds.size
                setProgress(workDataOf("progress" to ((index + 1f / batches.size) * 100).toInt()))
            } catch (e: HttpException) {
                if (e.code() == 429) return@withContext Result.retry()  // Rate limited
                if (e.code() in 500..599) return@withContext Result.retry()  // Server error
                return@withContext Result.failure(workDataOf("error" to "HTTP ${e.code()}"))
            }
        }
        Result.success(workDataOf("synced_count" to successCount))
    }

    private suspend fun buildForegroundInfo(count: Int): ForegroundInfo {
        val notification = NotificationCompat.Builder(applicationContext, "health_sync")
            .setContentTitle("Syncing $count vital readings")
            .setSmallIcon(R.drawable.ic_health)
            .setOngoing(true)
            .build()
        return ForegroundInfo(1001, notification)
    }

    @AssistedFactory interface Factory : ChildWorkerFactory
}

// Schedule: sync every hour on any network, retry with exponential backoff
fun scheduleVitalsSync(patientId: String) {
    val request = PeriodicWorkRequestBuilder&lt;VitalsSyncWorker&gt;(1, TimeUnit.HOURS)
        .setConstraints(Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build())
        .setInputData(workDataOf("patient_id" to patientId))
        .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 10, TimeUnit.MINUTES)
        .build()

    WorkManager.getInstance(context)
        .enqueueUniquePeriodicWork("vitals_sync_$patientId",
            ExistingPeriodicWorkPolicy.UPDATE, request)
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Using Service for deferrable work:</strong> Services are killed by the OS; work is lost. ✅ Fix: Use WorkManager for any work that must complete eventually, even if deferred.</li>
        <li>❌ <strong>Ignoring Doze mode:</strong> On API 23+, normal network access is blocked during Doze. ✅ Fix: WorkManager handles Doze correctly by default — it queues work and executes during maintenance windows.</li>
        <li>❌ <strong>Periodic work below 15-minute interval:</strong> Setting interval less than 15 minutes is silently increased to 15 minutes by the system. ✅ Fix: Design your sync strategy around the 15-minute minimum.</li>
        <li>❌ <strong>Long-running work without setForeground:</strong> On Android 12+, workers running for more than 10 minutes without calling <code>setForeground()</code> are stopped. ✅ Fix: Call <code>setForeground()</code> early in <code>doWork()</code> for long-running tasks.</li>
        <li>❌ <strong>Passing large data through WorkManager input/output:</strong> WorkData is limited to 10KB. ✅ Fix: Pass only IDs via WorkData; read actual data from Room/DataStore inside the worker.</li>
        <li>❌ <strong>Not using unique work for critical operations:</strong> Enqueuing the same work multiple times causes parallel execution and potential conflicts. ✅ Fix: Always use <code>enqueueUniqueWork</code> or <code>enqueueUniquePeriodicWork</code> for operations that should not run in parallel.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"My go-to decision tree for background work: if it\'s user-facing and immediate, use a foreground Service. If it\'s guaranteed deferred work (sync, upload, cleanup), use WorkManager. If it needs precise timing for things like calendar alarms, use AlarmManager with <code>setExactAndAllowWhileIdle</code>. WorkManager is the right choice for maybe 80% of background work cases. The key production patterns I use: CoroutineWorker over ListenableWorker for cleaner coroutine integration, unique work to prevent duplicate execution, chains for multi-step pipelines where data flows between steps via output/input data, and proper backoff strategies. The two most common mistakes I see are: passing large objects through WorkData (use IDs, read from DB in the worker), and not calling <code>setForeground()</code> on long-running workers (causes silent termination on Android 12+)."</p>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 22-2: WorkManager vs Alternatives -->
  <div class="subtopic" id="subtopic-22-2">
    <h2>WorkManager vs Service vs AlarmManager vs Foreground Service</h2>

    <div class="card card-how">
      <h3>🛠️ Comparison &amp; Decision Guide</h3>
      <pre class="code-block"><code class="language-kotlin">// WHEN TO USE EACH:

// 1. WorkManager — deferrable, guaranteed background work
// Use: data sync, log upload, image processing, cache cleanup
// NOT for: precise timing, user-facing immediate work
val syncWork = OneTimeWorkRequestBuilder&lt;SyncWorker&gt;().build()
WorkManager.getInstance(context).enqueue(syncWork)

// 2. Foreground Service — immediate, user-visible long-running work
// Use: music playback, navigation, file download shown to user, fitness tracking
// Must show a persistent notification
class MusicPlaybackService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIF_ID, buildNotification())
        return START_STICKY  // Re-create if killed
    }
}

// 3. JobService (API 21+) — low-level JobScheduler (prefer WorkManager instead)
// WorkManager uses this under the hood; prefer WorkManager directly

// 4. AlarmManager — precise timing for user-facing events
// Use: calendar reminders, recurring exact-time alarms
// NOT for: deferrable work (use WorkManager), background sync
val alarmManager = context.getSystemService(AlarmManager::class.java)
val intent = PendingIntent.getBroadcast(context, 0, Intent(context, AlarmReceiver::class.java),
    PendingIntent.FLAG_IMMUTABLE)
alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,
    triggerAtMillis, intent)  // Fires even in Doze

// 5. BroadcastReceiver — short-lived, reactive to system events
// Use: boot complete (reschedule WorkManager), connectivity change
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            // WorkManager auto-reschedules pending work on boot
            // But re-initialize any custom state here
            WorkScheduler(context).schedulePeriodicSync(getUserId(context))
        }
    }
}

// DOZE MODE IMPACT:
// Standard network requests: BLOCKED during deep Doze
// AlarmManager setExact: DEFERRED to next maintenance window (unless setExactAndAllowWhileIdle)
// WorkManager: AUTOMATICALLY deferred to maintenance windows — handles Doze correctly
// Expedited WorkManager: EXEMPT from Doze, runs immediately (limited quota)</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Example — E-Commerce: Order Status Push + Background Sync</h3>
      <pre class="code-block"><code class="language-kotlin">// E-commerce app: FCM push triggers immediate sync, plus periodic background sync

class MessagingService : FirebaseMessagingService() {
    override fun onMessageReceived(message: RemoteMessage) {
        when (message.data["type"]) {
            "order_status_update" -> {
                // Trigger expedited WorkManager sync — runs immediately
                val orderId = message.data["order_id"] ?: return
                val request = OneTimeWorkRequestBuilder&lt;OrderSyncWorker&gt;()
                    .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
                    .setInputData(workDataOf("order_id" to orderId))
                    .build()
                WorkManager.getInstance(applicationContext)
                    .enqueueUniqueWork("sync_order_$orderId",
                        ExistingWorkPolicy.KEEP, request)
            }
            "flash_sale" -> showHighPriorityNotification(message)
        }
    }
}

class OrderSyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val orderRepo: OrderRepository
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        val orderId = inputData.getString("order_id") ?: return Result.failure()
        return try {
            val order = orderRepo.fetchOrderFromApi(orderId)
            orderRepo.updateLocalOrder(order)
            // Notify UI via Room Flow (the Flow will re-emit automatically)
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount &lt; 3) Result.retry() else Result.failure()
        }
    }
    override suspend fun getForegroundInfo(): ForegroundInfo =
        ForegroundInfo(1002, buildSilentNotification())

    @AssistedFactory interface Factory : ChildWorkerFactory
}</code></pre>
    </div>
  </div>

  <!-- Q&A Section -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the difference between WorkManager, Service, and AlarmManager? When do you use each?</div>
      <div class="qa-answer">
        <p><strong>WorkManager:</strong> For deferrable, guaranteed background work that must complete eventually. Battery-aware, handles Doze, survives process death and reboots. Not for precise timing or immediate user-facing work. Examples: data sync, log upload, image compression.<br><br>
        <strong>Foreground Service:</strong> For immediate, long-running, user-visible work. Must show a notification. Examples: music playback, file download, fitness tracking, navigation.<br><br>
        <strong>AlarmManager:</strong> For precise timing, fires at exact times even during Doze (with <code>setExactAndAllowWhileIdle</code>). Examples: calendar reminders, recurring exact-time notifications. NOT for background sync or data tasks.<br><br>
        <strong>Background Service (non-foreground):</strong> Mostly deprecated for new use cases. Android 8.0+ kills background services within minutes. Use WorkManager instead.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q2</span>How does Doze mode affect background processing, and how does WorkManager handle it?</div>
      <div class="qa-answer">
        <p>Doze mode (Android 6.0+) activates when the device is still, unplugged, and screen is off for a period. During Doze, the system: defers standard network access, defers <code>AlarmManager</code> alarms (except <code>setExactAndAllowWhileIdle</code>), defers <code>JobScheduler</code> jobs, stops Wi-Fi scans, prevents sync. The system provides periodic "maintenance windows" where all deferred work runs. <strong>WorkManager handles Doze automatically</strong> — it uses the JobScheduler under the hood, which respects maintenance windows. Your workers run when the system schedules them (in maintenance windows). For truly Doze-exempt work, use <code>setExpedited</code> — expedited work has a system-granted quota and is exempt from Doze restrictions, but you can\'t set a large quota manually.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>How do you chain workers so that output of one is passed as input to the next?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">// Worker A produces output
class DownloadWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        val url = inputData.getString("url") ?: return Result.failure()
        val localPath = downloadFile(url)
        return Result.success(workDataOf("local_path" to localPath))  // Output passed to next
    }
}

// Worker B receives output of A as input
class ProcessWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        val path = inputData.getString("local_path") ?: return Result.failure()  // Gets A\'s output
        val processedPath = processFile(path)
        return Result.success(workDataOf("processed_path" to processedPath))
    }
}

// Chaining
val download = OneTimeWorkRequestBuilder&lt;DownloadWorker&gt;()
    .setInputData(workDataOf("url" to "https://...")).build()
val process = OneTimeWorkRequestBuilder&lt;ProcessWorker&gt;().build()

// Data merging for parallel-to-sequential: use InputMerger
val parallel1 = OneTimeWorkRequestBuilder&lt;WorkerA&gt;().build()
val parallel2 = OneTimeWorkRequestBuilder&lt;WorkerB&gt;().build()
val merge = OneTimeWorkRequestBuilder&lt;MergeWorker&gt;()
    .setInputMerger(ArrayCreatingInputMerger::class)  // Merges arrays from multiple parents
    .build()

WorkManager.getInstance(context)
    .beginWith(listOf(parallel1, parallel2))
    .then(merge)
    .enqueue()</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q4</span>Your app needs to sync data every 15 minutes ONLY when on WiFi and battery is not low. How do you implement this?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED)  // WiFi only
    .setRequiresBatteryNotLow(true)
    .build()

val periodicRequest = PeriodicWorkRequestBuilder&lt;SyncWorker&gt;(
    15, TimeUnit.MINUTES,       // Repeat interval
    5, TimeUnit.MINUTES         // Flex interval — can run anywhere in last 5 min of window
)
    .setConstraints(constraints)
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
    .addTag("sync_tag")
    .build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork(
        "periodic_wifi_sync",
        ExistingPeriodicWorkPolicy.UPDATE,  // Update constraints if already scheduled
        periodicRequest
    )

// Cancellation — when user logs out
WorkManager.getInstance(context).cancelUniqueWork("periodic_wifi_sync")
// or by tag
WorkManager.getInstance(context).cancelAllWorkByTag("sync_tag")</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q5</span>What is expedited work in WorkManager and when should you use it?</div>
      <div class="qa-answer">
        <p>Expedited work (API 31+ / WorkManager 2.7+) is designed for work that is important and should start immediately — like sending a message, processing a payment, or syncing critical data triggered by user action. The system grants expedited work a quota: initially it can run even while Doze is active. If the quota is exceeded, you can choose fallback behavior via <code>OutOfQuotaPolicy</code>: <code>RUN_AS_NON_EXPEDITED_WORK_REQUEST</code> (run eventually, possibly deferred) or <code>DROP_WORK_REQUEST</code> (abandon if no quota). Workers using expedited work MUST override <code>getForegroundInfo()</code> to provide a notification — this allows the system to run it as a foreground service on older APIs (below API 31). Use for: payment confirmation sync, critical message sending, important user-triggered uploads.</p>
        <pre class="code-block"><code class="language-kotlin">class PaymentConfirmationWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork(): Result { /* ... */ }
    override suspend fun getForegroundInfo(): ForegroundInfo =
        ForegroundInfo(999, NotificationCompat.Builder(applicationContext, "payments")
            .setContentTitle("Processing payment...")
            .setSmallIcon(R.drawable.ic_payment)
            .build())
}

val expedited = OneTimeWorkRequestBuilder&lt;PaymentConfirmationWorker&gt;()
    .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
    .build()</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>How do you inject dependencies into a Worker class with Hilt?</div>
      <div class="qa-answer">
        <p>Workers can\'t use constructor injection directly because WorkManager creates them. The solution is Hilt\'s <code>@HiltWorker</code> annotation combined with <code>@AssistedInject</code>. You also need to provide a custom <code>WorkerFactory</code> using Hilt\'s <code>HiltWorkerFactory</code> and configure WorkManager to use it via <code>WorkerFactory</code> configuration.</p>
        <pre class="code-block"><code class="language-kotlin">// 1. Worker with @HiltWorker
@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val repo: SyncRepository  // Hilt-injected
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result { /* ... */ }
}

// 2. Disable auto-init and provide HiltWorkerFactory
@Suppress("unused")
class MyApp : Application(), Configuration.Provider {
    @Inject lateinit var workerFactory: HiltWorkerFactory

    override fun getWorkManagerConfiguration(): Configuration =
        Configuration.Builder()
            .setWorkerFactory(workerFactory)
            .build()
}

// In AndroidManifest.xml — remove default WorkManager initializer
// &lt;provider android:name="androidx.startup.InitializationProvider"&gt;
//   &lt;meta-data android:name="androidx.work.WorkManagerInitializer" android:value="androidx.startup.Disabled" /&gt;
// &lt;/provider&gt;</code></pre>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge — Implement a File Upload Pipeline with Retry &amp; Progress</h3>
    <p><strong>Problem:</strong> Implement a WorkManager-based file upload that: compresses the file first, then uploads in chunks, reports progress, retries on failure with exponential backoff, and notifies the user when complete.</p>
    <pre class="code-block"><code class="language-kotlin">// Step 1: Compress Worker
@HiltWorker
class CompressFileWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val fileCompressor: FileCompressor
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val filePath = inputData.getString("file_path") ?: return Result.failure()
        return try {
            setProgress(workDataOf("stage" to "compressing", "progress" to 0))
            val compressed = fileCompressor.compress(filePath) { progress ->
                // Report compression progress
                setProgress(workDataOf("stage" to "compressing", "progress" to progress))
            }
            Result.success(workDataOf("compressed_path" to compressed, "file_size" to compressed.length()))
        } catch (e: IOException) {
            Result.failure(workDataOf("error" to "Compression failed: ${e.message}"))
        }
    }

    @AssistedFactory interface Factory : ChildWorkerFactory
}

// Step 2: Upload Worker
@HiltWorker
class UploadFileWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val uploadApi: UploadApiService,
    private val notificationHelper: NotificationHelper
) : CoroutineWorker(context, params) {
    private val CHUNK_SIZE = 512 * 1024  // 512KB chunks

    override suspend fun doWork(): Result {
        val filePath = inputData.getString("compressed_path") ?: return Result.failure()
        val file = File(filePath)
        if (!file.exists()) return Result.failure(workDataOf("error" to "File not found"))

        setForeground(buildForegroundInfo("Uploading..."))

        return try {
            val uploadId = uploadApi.initiateUpload(file.name, file.length())
            val totalChunks = (file.length() / CHUNK_SIZE + 1).toInt()

            file.inputStream().use { stream ->
                val buffer = ByteArray(CHUNK_SIZE)
                var bytesRead: Int
                var chunkIndex = 0
                while (stream.read(buffer).also { bytesRead = it } != -1) {
                    val chunk = buffer.copyOf(bytesRead)
                    uploadApi.uploadChunk(uploadId, chunkIndex, chunk)
                    chunkIndex++
                    val progress = ((chunkIndex.toFloat() / totalChunks) * 100).toInt()
                    setProgress(workDataOf("stage" to "uploading", "progress" to progress))
                    setForeground(buildForegroundInfo("Uploading... $progress%"))
                }
            }

            val finalUrl = uploadApi.finalizeUpload(uploadId)
            notificationHelper.showUploadComplete(file.name, finalUrl)
            // Clean up compressed file
            file.delete()
            Result.success(workDataOf("download_url" to finalUrl))
        } catch (e: HttpException) {
            if (e.code() in 500..599 && runAttemptCount &lt; 3) Result.retry()
            else Result.failure(workDataOf("error" to "Upload failed: HTTP ${e.code()}"))
        } catch (e: IOException) {
            if (runAttemptCount &lt; 3) Result.retry()
            else Result.failure(workDataOf("error" to "Network error: ${e.message}"))
        }
    }

    private fun buildForegroundInfo(title: String): ForegroundInfo {
        val notification = NotificationCompat.Builder(applicationContext, "uploads")
            .setContentTitle(title)
            .setSmallIcon(R.drawable.ic_upload)
            .setOngoing(true)
            .build()
        return ForegroundInfo(2001, notification)
    }

    @AssistedFactory interface Factory : ChildWorkerFactory
}

// Orchestrate: compress THEN upload
fun enqueueFileUpload(context: Context, filePath: String) {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .build()

    val compressWork = OneTimeWorkRequestBuilder&lt;CompressFileWorker&gt;()
        .setInputData(workDataOf("file_path" to filePath))
        .addTag("file_upload")
        .build()

    val uploadWork = OneTimeWorkRequestBuilder&lt;UploadFileWorker&gt;()
        .setConstraints(constraints)
        .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
        .addTag("file_upload")
        .build()

    WorkManager.getInstance(context)
        .beginUniqueWork("upload_$filePath", ExistingWorkPolicy.REPLACE, compressWork)
        .then(uploadWork)
        .enqueue()
}
// compressed_path output from CompressFileWorker is automatically available as input to UploadFileWorker
// Progress tracked separately per stage via setProgress()</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="22" data-item="0"> ✅ Understood WorkManager vs Service vs AlarmManager</label>
    <label class="progress-check"><input type="checkbox" data-topic="22" data-item="1"> ✅ Understood Constraints, Chaining &amp; Unique Work</label>
    <label class="progress-check"><input type="checkbox" data-topic="22" data-item="2"> ✅ Understood Doze Mode &amp; Expedited Work</label>
    <label class="progress-check"><input type="checkbox" data-topic="22" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="22" data-item="4"> ✅ Solved File Upload Pipeline Challenge</label>
  </div>
</section>
'''
