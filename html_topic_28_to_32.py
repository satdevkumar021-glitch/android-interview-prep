# html_topic_28_to_32.py
# Topics: Testing, Performance, Memory Management, Gradle & Build System, App Modularization

def get_topics_28_to_32_html():
    return '''
<!-- ==================== TOPIC 28: TESTING IN ANDROID ==================== -->
<section class="topic-section" id="topic-28">
  <div class="topic-header">
    <div class="topic-header-icon">🧪</div>
    <div class="topic-header-text">
      <h1>Testing in Android</h1>
      <p class="topic-tagline">JUnit4/5, MockK, Turbine, Espresso, Compose UI Testing — build confidence in your code</p>
      <div class="category-badge-group">
        <span class="cat-pill">Testing</span>
        <span class="cat-pill">JUnit</span>
        <span class="cat-pill">MockK</span>
        <span class="cat-pill">Espresso</span>
        <span class="cat-pill">Compose</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 28-1: Unit Testing with JUnit & MockK -->
  <div class="subtopic" id="subtopic-28-1">
    <h2>Unit Testing: JUnit4/5, MockK vs Mockito, TestCoroutineDispatcher</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Without automated tests, every code change risks introducing regressions that only surface in production. In a 50-engineer Android team at a FinTech company, a single untested ViewModel bug can crash payments for millions of users. Unit tests catch logic errors in milliseconds — before PRs merge — giving the team confidence to refactor, ship fast, and maintain code quality. Tests also act as executable documentation: they define the contract each function must satisfy.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p><strong>JUnit4</strong> is the standard JVM test runner used in most Android projects; annotations like <code>@Test</code>, <code>@Before</code>, <code>@After</code>, and <code>@Rule</code> drive test lifecycle. <strong>JUnit5 (Jupiter)</strong> introduces extensions, parameterized tests, nested tests, and better display names — but requires the <code>junit-vintage-engine</code> bridge for AndroidX Test compatibility. <strong>MockK</strong> is a Kotlin-native mocking library that supports coroutines, extension functions, objects, and top-level functions natively, unlike <strong>Mockito</strong> which was designed for Java and struggles with Kotlin final classes without the <code>mockito-inline</code> artifact. <strong>TestCoroutineDispatcher</strong> (now <code>UnconfinedTestDispatcher</code> / <code>StandardTestDispatcher</code> from <code>kotlinx-coroutines-test</code>) replaces real dispatchers in tests so coroutines run synchronously and deterministically.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <p>A typical unit test lifecycle with coroutines:</p>
      <ol>
        <li>Replace <code>Dispatchers.Main</code> via <code>Dispatchers.setMain(testDispatcher)</code> in <code>@Before</code></li>
        <li>Create mocks with MockK's <code>mockk()</code> or <code>spyk()</code></li>
        <li>Stub responses with <code>every { } returns</code> / <code>coEvery { } returns</code></li>
        <li>Run the SUT (System Under Test)</li>
        <li>Assert with <code>verify { }</code> / <code>coVerify { }</code> and assertJ / Truth assertions</li>
        <li>Tear down with <code>Dispatchers.resetMain()</code> in <code>@After</code></li>
      </ol>
      <pre class="code-block"><code class="language-kotlin">// build.gradle.kts (module level)
testImplementation("junit:junit:4.13.2")
testImplementation("io.mockk:mockk:1.13.10")
testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.8.0")
testImplementation("app.cash.turbine:turbine:1.1.0")
testImplementation("com.google.truth:truth:1.4.2")

// PaymentViewModel.kt — the SUT
class PaymentViewModel(
    private val repository: PaymentRepository,
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) : ViewModel() {

    private val _state = MutableStateFlow<PaymentState>(PaymentState.Idle)
    val state: StateFlow<PaymentState> = _state.asStateFlow()

    fun submitPayment(amount: Double, cardToken: String) {
        viewModelScope.launch(dispatcher) {
            _state.value = PaymentState.Loading
            val result = repository.processPayment(amount, cardToken)
            _state.value = when {
                result.isSuccess -> PaymentState.Success(result.getOrThrow())
                else -> PaymentState.Error(result.exceptionOrNull()?.message ?: "Unknown error")
            }
        }
    }
}

// PaymentViewModelTest.kt
@OptIn(ExperimentalCoroutinesApi::class)
class PaymentViewModelTest {

    private val testDispatcher = UnconfinedTestDispatcher()
    private val repository: PaymentRepository = mockk()
    private lateinit var viewModel: PaymentViewModel

    @Before
    fun setUp() {
        Dispatchers.setMain(testDispatcher)
        viewModel = PaymentViewModel(repository, testDispatcher)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
        unmockkAll()
    }

    @Test
    fun `submitPayment emits Loading then Success when repository succeeds`() = runTest {
        // Given
        val receipt = Receipt(id = "TXN-001", amount = 100.0)
        coEvery { repository.processPayment(100.0, "tok_visa") } returns Result.success(receipt)

        // When + Then (using Turbine)
        viewModel.state.test {
            assertThat(awaitItem()).isInstanceOf(PaymentState.Idle::class.java)
            viewModel.submitPayment(100.0, "tok_visa")
            assertThat(awaitItem()).isInstanceOf(PaymentState.Loading::class.java)
            val success = awaitItem() as PaymentState.Success
            assertThat(success.receipt.id).isEqualTo("TXN-001")
            cancelAndIgnoreRemainingEvents()
        }

        coVerify(exactly = 1) { repository.processPayment(100.0, "tok_visa") }
    }

    @Test
    fun `submitPayment emits Error when repository throws`() = runTest {
        coEvery { repository.processPayment(any(), any()) } returns
            Result.failure(IOException("Network error"))

        viewModel.state.test {
            awaitItem() // Idle
            viewModel.submitPayment(50.0, "tok_bad")
            awaitItem() // Loading
            val error = awaitItem() as PaymentState.Error
            assertThat(error.message).isEqualTo("Network error")
            cancelAndIgnoreRemainingEvents()
        }
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// MockK Essentials
val mock = mockk&lt;MyClass&gt;()               // strict mock
val relaxed = mockk&lt;MyClass&gt;(relaxed = true) // returns defaults
val spy = spyk(MyClass())                   // real impl + override

every { mock.getValue() } returns 42
every { mock.getValue() } throws RuntimeException("boom")
coEvery { mock.suspendFun() } returns "result"   // coroutine stubs
every { mock.getValue() } answers { callOriginal() }

verify(exactly = 1) { mock.getValue() }
verify(atLeast = 2) { mock.doSomething() }
coVerify { mock.suspendFun() }
confirmVerified(mock)                       // no unexpected calls

// Mocking objects / companions
mockkObject(MyObject)
every { MyObject.singleton() } returns "mocked"
unmockkObject(MyObject)

// Mocking top-level / extension functions
mockkStatic("com.example.ExtensionsKt")
every { anyString().myExtension() } returns "extended"

// JUnit5 with @ExtendWith
@ExtendWith(MockKExtension::class)
class MyTest {
    @MockK lateinit var dep: Dependency
    @InjectMockKs lateinit var sut: MyService
}

// Parameterized JUnit5
@ParameterizedTest
@ValueSource(doubles = [0.0, -1.0, Double.MAX_VALUE])
fun `rejects invalid amounts`(amount: Double) {
    assertThat(viewModel.validateAmount(amount)).isFalse()
}

// Coroutine test utilities
runTest { /* automatically advances virtual time */ }
advanceUntilIdle()
advanceTimeBy(1000L)
runCurrent()
</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example — FinTech: Transaction Repository</h3>
      <p>A banking app's transaction service must retry on transient failures with exponential backoff. Testing the retry logic requires controlling time without sleeping real milliseconds.</p>
      <pre class="code-block"><code class="language-kotlin">// TransactionRepository.kt
class TransactionRepository(
    private val api: BankingApi,
    private val cache: TransactionCache,
    private val retryPolicy: RetryPolicy = ExponentialBackoff(maxRetries = 3)
) {
    suspend fun fetchTransactions(accountId: String): List<Transaction> {
        return retryPolicy.execute {
            api.getTransactions(accountId)
        }.also { cache.store(accountId, it) }
    }
}

// TransactionRepositoryTest.kt
@OptIn(ExperimentalCoroutinesApi::class)
class TransactionRepositoryTest {

    private val api: BankingApi = mockk()
    private val cache: TransactionCache = mockk(relaxed = true)
    private val testDispatcher = StandardTestDispatcher()

    private val repo = TransactionRepository(
        api = api,
        cache = cache,
        retryPolicy = ExponentialBackoff(maxRetries = 3)
    )

    @Test
    fun `fetchTransactions retries twice then succeeds`() = runTest(testDispatcher) {
        val transactions = listOf(Transaction("1", 100.0), Transaction("2", 200.0))
        coEvery { api.getTransactions("ACC-001") } throwsMany listOf(
            IOException("timeout"),
            IOException("timeout")
        ) andThen transactions

        val result = repo.fetchTransactions("ACC-001")

        assertThat(result).hasSize(2)
        coVerify(exactly = 3) { api.getTransactions("ACC-001") }
        coVerify { cache.store("ACC-001", transactions) }
    }

    @Test
    fun `fetchTransactions throws after max retries exhausted`() = runTest(testDispatcher) {
        coEvery { api.getTransactions(any()) } throws IOException("server down")

        assertThrows&lt;IOException&gt; {
            repo.fetchTransactions("ACC-002")
        }
        coVerify(exactly = 3) { api.getTransactions("ACC-002") }
        coVerify(exactly = 0) { cache.store(any(), any()) }
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Forgetting Dispatchers.setMain():</strong> Tests calling <code>viewModelScope.launch</code> crash with "Module with Main dispatcher not found". — ✅ Fix: Always call <code>Dispatchers.setMain(testDispatcher)</code> in <code>@Before</code> and <code>resetMain()</code> in <code>@After</code>.</li>
        <li>❌ <strong>Using <code>runBlocking</code> instead of <code>runTest</code>:</strong> runBlocking doesn't control virtual time so <code>delay()</code> waits real milliseconds. — ✅ Fix: Use <code>runTest { }</code> from <code>kotlinx-coroutines-test</code>; it auto-advances virtual clock.</li>
        <li>❌ <strong>MockK strict mocks with missing stubs:</strong> Accessing an unstubbed method throws <code>MockKException</code>. — ✅ Fix: Use <code>mockk(relaxed = true)</code> for dependencies you don't care about, strict for ones you need to verify.</li>
        <li>❌ <strong>Not calling <code>unmockkAll()</code> after mockkStatic/mockkObject:</strong> Static mocks leak between tests, causing flaky failures. — ✅ Fix: Always call <code>unmockkAll()</code> in <code>@After</code>.</li>
        <li>❌ <strong>Testing implementation details instead of behavior:</strong> Verifying internal method calls makes tests brittle. — ✅ Fix: Test observable state/output (StateFlow values, returned values), not internal calls.</li>
        <li>❌ <strong>UnconfinedTestDispatcher vs StandardTestDispatcher confusion:</strong> Unconfined runs coroutines eagerly (no need to advance time); Standard requires explicit <code>advanceUntilIdle()</code>. — ✅ Fix: Use Unconfined for simple tests; use Standard + advance calls for testing timing-dependent logic.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <p>When asked about testing strategy, don't just list tools — describe your philosophy and trade-offs.</p>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Our testing pyramid has fast unit tests at the base — ViewModels, UseCases, Repositories — all tested with JUnit4, MockK, and Turbine for Flow assertions. We chose MockK over Mockito because Kotlin classes are final by default and MockK handles coroutines, objects, and extension functions natively. For coroutine tests, we inject CoroutineDispatcher and swap it with UnconfinedTestDispatcher in tests, combined with runTest to control virtual time. Turbine lets us assert on StateFlow emissions exactly — we can check Idle → Loading → Success without any timing hacks. For instrumented tests on device, we use Espresso for legacy screens and Compose's ComposeTestRule for new UI — both in our CI pipeline via Firebase Test Lab. Our integration tests cover the Repository layer against a mock HTTP server using OkHttp MockWebServer. We track test coverage with Jacoco and gate PRs at 80% coverage on business logic classes."</p>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 28-2: Integration, E2E, Espresso, Compose UI Testing -->
  <div class="subtopic" id="subtopic-28-2">
    <h2>Integration, E2E, Espresso &amp; Compose UI Testing</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Unit tests verify isolated logic, but they can't catch wiring bugs: a ViewModel connected to the wrong Repository, a navigation graph routing to the wrong destination, or a Compose composable that doesn't show the right text when state changes. Integration and UI tests validate the full slice from ViewModel to screen — and E2E tests validate real user journeys through the entire app, catching contract bugs between frontend and backend that unit tests completely miss.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p><strong>Integration tests</strong> test multiple components together (e.g., ViewModel + Room database) using AndroidX Test with a real or in-memory database. <strong>Espresso</strong> is Google's UI testing framework for View-based UI — it synchronizes with the main thread automatically using IdlingResources. <strong>Compose UI Testing</strong> uses <code>createComposeRule()</code> / <code>createAndroidComposeRule()</code> with semantics-based finders (<code>onNodeWithText</code>, <code>onNodeWithContentDescription</code>) for reliable Compose assertions. <strong>E2E tests</strong> run full app flows (login → purchase → receipt) on a real device or emulator via Firebase Test Lab. <strong>Test doubles</strong> include: Fake (working implementation), Stub (returns hardcoded values), Mock (verifies interactions), Spy (partial mock), Dummy (placeholder).</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// Compose UI Test — ProductDetailScreen
@HiltAndroidTest
class ProductDetailScreenTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeRule = createAndroidComposeRule&lt;MainActivity&gt;()

    @BindValue
    @JvmField
    val fakeRepository: ProductRepository = FakeProductRepository()

    @Before
    fun setUp() {
        hiltRule.inject()
    }

    @Test
    fun productDetailScreen_displaysProductName_andAddToCartButton() {
        // Navigate to product detail
        composeRule.onNodeWithText("Electronics").performClick()
        composeRule.onNodeWithContentDescription("Product: Pixel 9 Pro").assertIsDisplayed()
        composeRule.onNodeWithText("Add to Cart").assertIsEnabled()
    }

    @Test
    fun addToCart_updatesCartBadge() {
        composeRule.onNodeWithText("Add to Cart").performClick()
        composeRule.onNodeWithContentDescription("Cart badge: 1").assertIsDisplayed()
    }
}

// FakeProductRepository.kt — a Fake test double
class FakeProductRepository : ProductRepository {
    private val products = mutableListOf(
        Product("1", "Pixel 9 Pro", 999.0, "Electronics")
    )

    override suspend fun getProducts(): List<Product> = products
    override suspend fun getProduct(id: String): Product =
        products.first { it.id == id }
    override suspend fun addToCart(productId: String) {
        // no-op in fake, but trackable
    }
}

// Espresso Test — LoginActivity (legacy View UI)
@RunWith(AndroidJUnit4::class)
class LoginActivityTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(LoginActivity::class.java)

    @Test
    fun validCredentials_navigatesToHomeScreen() {
        onView(withId(R.id.emailField))
            .perform(typeText("user@bank.com"), closeSoftKeyboard())
        onView(withId(R.id.passwordField))
            .perform(typeText("SecurePass123"), closeSoftKeyboard())
        onView(withId(R.id.loginButton))
            .perform(click())
        onView(withId(R.id.homeTitle))
            .check(matches(isDisplayed()))
    }

    @Test
    fun emptyEmail_showsValidationError() {
        onView(withId(R.id.loginButton)).perform(click())
        onView(withText("Email is required"))
            .check(matches(isDisplayed()))
    }
}

// Room Integration Test
@RunWith(AndroidJUnit4::class)
class TransactionDaoTest {

    private lateinit var db: AppDatabase
    private lateinit var dao: TransactionDao

    @Before
    fun createDb() {
        val context = ApplicationProvider.getApplicationContext&lt;Context&gt;()
        db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java)
            .allowMainThreadQueries()
            .build()
        dao = db.transactionDao()
    }

    @After
    fun closeDb() = db.close()

    @Test
    fun insertAndReadTransaction() = runTest {
        val txn = TransactionEntity(id = "T1", amount = 500.0, date = System.currentTimeMillis())
        dao.insert(txn)
        val results = dao.getAll().first()
        assertThat(results).hasSize(1)
        assertThat(results[0].amount).isEqualTo(500.0)
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// Compose Testing APIs
composeRule.onNodeWithText("Submit").performClick()
composeRule.onNodeWithTag("loading_indicator").assertIsDisplayed()
composeRule.onNodeWithContentDescription("Back").assertExists()
composeRule.onAllNodesWithText("Item").assertCountEquals(5)
composeRule.waitUntil(3000L) {
    composeRule.onNodeWithText("Success").fetchSemanticsNode() != null
}
composeRule.onNode(hasText("Price") and hasClickAction()).performClick()
composeRule.onNodeWithText("Input").performTextInput("test@email.com")

// Turbine (Flow testing)
myFlow.test {
    assertThat(awaitItem()).isEqualTo(initialState)
    // trigger action
    assertThat(awaitItem()).isEqualTo(expectedState)
    awaitComplete()           // or cancelAndIgnoreRemainingEvents()
    ensureAllEventsConsumed() // fail if any unconsumed events
}

// Espresso cheat sheet
onView(withId(R.id.myButton)).perform(click())
onView(withText("Submit")).check(matches(isEnabled()))
onView(withId(R.id.list)).check(RecyclerViewItemCountAssertion(5))
onData(hasEntry("key", "value")).inAdapterView(withId(R.id.spinner)).perform(click())

// Custom IdlingResource for Espresso + OkHttp
val idlingResource = OkHttp3IdlingResource.create("okhttp", okHttpClient)
IdlingRegistry.getInstance().register(idlingResource)
</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example — E-Commerce: Checkout Flow Test</h3>
      <pre class="code-block"><code class="language-kotlin">// End-to-end checkout flow using Compose + Hilt
@HiltAndroidTest
@LargeTest
class CheckoutFlowE2ETest {

    @get:Rule(order = 0) val hiltRule = HiltAndroidRule(this)
    @get:Rule(order = 1) val composeRule = createAndroidComposeRule&lt;MainActivity&gt;()

    @BindValue @JvmField
    val fakePaymentGateway: PaymentGateway = FakePaymentGateway(
        simulateSuccess = true, delayMs = 100
    )

    @Test
    fun fullCheckoutFlow_fromCartToOrderConfirmation() = runTest {
        // Step 1: Navigate to cart
        composeRule.onNodeWithContentDescription("Cart").performClick()
        composeRule.onNodeWithText("Proceed to Checkout").assertIsEnabled().performClick()

        // Step 2: Fill shipping
        composeRule.onNodeWithTag("name_field").performTextInput("John Doe")
        composeRule.onNodeWithTag("address_field").performTextInput("123 Main St")
        composeRule.onNodeWithText("Continue").performClick()

        // Step 3: Payment
        composeRule.onNodeWithTag("card_number").performTextInput("4111111111111111")
        composeRule.onNodeWithTag("expiry").performTextInput("12/26")
        composeRule.onNodeWithTag("cvv").performTextInput("123")
        composeRule.onNodeWithText("Place Order").performClick()

        // Step 4: Verify confirmation screen
        composeRule.waitUntil(10_000L) {
            composeRule.onAllNodesWithText("Order Confirmed").fetchSemanticsNodes().isNotEmpty()
        }
        composeRule.onNodeWithText("Order Confirmed").assertIsDisplayed()
        composeRule.onNodeWithContentDescription("Order confirmation number").assertExists()
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Using Thread.sleep() in UI tests:</strong> Makes tests slow and flaky. — ✅ Fix: Use <code>composeRule.waitUntil { }</code> or Espresso IdlingResources to wait for async operations.</li>
        <li>❌ <strong>Not using testTags in Compose:</strong> Relying on text strings breaks when designers change copy. — ✅ Fix: Add <code>Modifier.testTag("submit_button")</code> and find with <code>onNodeWithTag()</code>.</li>
        <li>❌ <strong>Heavy E2E tests in every PR:</strong> 20-minute test suites block developers. — ✅ Fix: Run unit tests on every PR, integration tests on merge to main, E2E tests nightly on Firebase Test Lab.</li>
        <li>❌ <strong>Shared mutable state between tests:</strong> One test's side effects pollute the next. — ✅ Fix: Use <code>@Before</code> to reset state, use in-memory databases, and clear SharedPreferences/DataStore between runs.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"For UI testing in Compose, we use semantics-based finders rather than hardcoded resource IDs — we add testTags to composables during development so tests are resilient to text changes. We inject Hilt test doubles using @BindValue to replace real network clients with Fakes that return deterministic data. For async UI states, we use waitUntil{} with a reasonable timeout instead of sleep(). Our test pyramid: 70% unit tests (fast, JVM, no device), 20% integration (Room, navigation), 10% E2E on Firebase Test Lab. This gives us maximum confidence at minimum CI cost."</p>
      </div>
    </div>
  </div>

  <!-- Q&A Section -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the difference between MockK and Mockito for Kotlin projects?</div>
      <div class="qa-answer">
        <p><strong>Mockito</strong> was built for Java. It relies on subclassing/proxy generation, which fails for Kotlin's <code>final</code> classes (all classes are final by default in Kotlin). You need <code>mockito-inline</code> or the <code>@MockitoSettings(strictness = LENIENT)</code> workaround. It also doesn't natively support Kotlin's suspend functions, extension functions, or companion objects.</p>
        <p><strong>MockK</strong> is Kotlin-native. It uses instrumentation to mock final classes by default, supports <code>coEvery</code>/<code>coVerify</code> for coroutines, <code>mockkStatic</code> for extension/top-level functions, and <code>mockkObject</code> for Kotlin objects. In modern Kotlin/Android projects, MockK is almost always the better choice.</p>
        <pre class="code-block"><code class="language-kotlin">// MockK for coroutines — natural syntax
coEvery { repo.getData() } returns listOf("a", "b")
coVerify { repo.getData() }

// Mockito equivalent is verbose and error-prone
`when`(runBlocking { repo.getData() }).thenReturn(listOf("a", "b"))
</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q2</span>What is Turbine and why use it for testing Flows?</div>
      <div class="qa-answer">
        <p><strong>Turbine</strong> (by Cash App) is a testing library that provides a structured way to collect and assert on Flow emissions. Without Turbine, testing a Flow requires collecting into a list with a separate coroutine and complex synchronization. Turbine gives you an intuitive API: <code>awaitItem()</code>, <code>awaitComplete()</code>, <code>awaitError()</code>.</p>
        <pre class="code-block"><code class="language-kotlin">// Without Turbine — cumbersome
val emissions = mutableListOf&lt;UiState&gt;()
val job = launch { viewModel.state.collect { emissions.add(it) } }
viewModel.loadData()
advanceUntilIdle()
assertThat(emissions[0]).isInstanceOf(Loading::class.java)
job.cancel()

// With Turbine — clean and readable
viewModel.state.test {
    viewModel.loadData()
    assertThat(awaitItem()).isInstanceOf(Loading::class.java)
    assertThat(awaitItem()).isInstanceOf(Success::class.java)
    cancelAndIgnoreRemainingEvents()
}
</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>Explain UnconfinedTestDispatcher vs StandardTestDispatcher. When would you use each?</div>
      <div class="qa-answer">
        <p><strong>UnconfinedTestDispatcher</strong>: Runs coroutines eagerly — they execute immediately when launched, without needing to explicitly advance the virtual clock. Great for simple tests where you just want coroutines to run to completion automatically.</p>
        <p><strong>StandardTestDispatcher</strong>: Coroutines are queued but NOT run automatically. You control execution by calling <code>advanceUntilIdle()</code>, <code>advanceTimeBy(ms)</code>, or <code>runCurrent()</code>. Use this when you need to assert intermediate states (e.g., assert Loading state before advancing to Success) or test timing-sensitive logic like debounce/retry with delays.</p>
        <pre class="code-block"><code class="language-kotlin">// StandardTestDispatcher — control intermediate states
val dispatcher = StandardTestDispatcher()
runTest(dispatcher) {
    viewModel.search("query")
    // Coroutine launched but not yet run
    assertThat(viewModel.state.value).isEqualTo(UiState.Idle)
    advanceTimeBy(300) // advance past debounce
    assertThat(viewModel.state.value).isEqualTo(UiState.Loading)
    advanceUntilIdle()
    assertThat(viewModel.state.value).isInstanceOf(UiState.Success::class.java)
}
</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q4</span>What are test doubles and what is the difference between a Mock and a Fake?</div>
      <div class="qa-answer">
        <p><strong>Test Doubles</strong> (Gerard Meszaros terminology):</p>
        <ul>
          <li><strong>Dummy:</strong> Passed but never used. E.g., a null logger passed to a constructor.</li>
          <li><strong>Stub:</strong> Returns hardcoded responses. No behavior verification.</li>
          <li><strong>Fake:</strong> Working lightweight implementation. E.g., in-memory database instead of SQLite. Has business logic but is simpler than production.</li>
          <li><strong>Mock:</strong> Pre-programmed with expectations. Verifies that specific interactions happened. Created by frameworks like MockK.</li>
          <li><strong>Spy:</strong> Wraps a real object, delegates by default but can stub specific methods.</li>
        </ul>
        <p><strong>Key distinction:</strong> Mocks focus on interaction verification (did method X get called?). Fakes focus on state verification (is the output correct?). Fakes are more stable under refactoring — they don't break when you rename internal methods. Use Fakes for repositories in integration tests; use Mocks in unit tests where you need to assert specific calls were made.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q5</span>How would you test a ViewModel that uses both a StateFlow for UI state and a SharedFlow for one-time events (navigation, snackbars)?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">class CheckoutViewModel(private val repo: CheckoutRepository) : ViewModel() {
    private val _state = MutableStateFlow&lt;CheckoutState&gt;(CheckoutState.Idle)
    val state = _state.asStateFlow()

    private val _events = MutableSharedFlow&lt;CheckoutEvent&gt;()
    val events = _events.asSharedFlow()

    fun placeOrder() {
        viewModelScope.launch {
            _state.value = CheckoutState.Loading
            val result = repo.placeOrder()
            if (result.isSuccess) {
                _state.value = CheckoutState.Success
                _events.emit(CheckoutEvent.NavigateToConfirmation(result.getOrThrow().orderId))
            } else {
                _state.value = CheckoutState.Error
                _events.emit(CheckoutEvent.ShowSnackbar("Order failed"))
            }
        }
    }
}

// Test — use Turbine for BOTH flows simultaneously
@Test
fun placeOrder_onSuccess_emitsSuccessStateAndNavigationEvent() = runTest {
    coEvery { repo.placeOrder() } returns Result.success(Order("ORD-999"))

    // Collect both flows concurrently
    viewModel.state.test {
        viewModel.events.test {
            assertThat(awaitItem()).isEqualTo(CheckoutState.Idle)
            viewModel.placeOrder()
            assertThat(awaitItem()).isEqualTo(CheckoutState.Loading)
            assertThat(awaitItem()).isEqualTo(CheckoutState.Success)
            cancelAndIgnoreRemainingEvents()

            // Check event
            val event = awaitItem() as CheckoutEvent.NavigateToConfirmation
            assertThat(event.orderId).isEqualTo("ORD-999")
            cancelAndIgnoreRemainingEvents()
        }
    }
}
</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>How do you structure your test pyramid for a large Android app with 50+ engineers?</div>
      <div class="qa-answer">
        <p><strong>The ideal pyramid (70/20/10 ratio):</strong></p>
        <ul>
          <li><strong>70% Unit Tests (JVM, &lt;1ms each):</strong> ViewModels, UseCases, Repositories, Mappers, Utils. Run on every commit in &lt;2 minutes. Technology: JUnit4 + MockK + Turbine + Truth.</li>
          <li><strong>20% Integration Tests (device/emulator, &lt;5s each):</strong> Room DAOs, Navigation, ViewModel + Repository with in-memory DB, Hilt dependency graph validation. Run on merge to main. Technology: AndroidX Test + Hilt testing.</li>
          <li><strong>10% E2E Tests (&lt;2min each):</strong> Critical user journeys: login, checkout, payment. Run nightly on Firebase Test Lab across real device matrix. Technology: Compose Test + Espresso.</li>
        </ul>
        <p><strong>Team practices:</strong> Gate PRs at 80% coverage on business logic. Track flaky tests in a dashboard and quarantine/fix within 24h. Use test sharding in CI to parallelize the suite. Module-level test targets so feature teams only run tests for changed modules.</p>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge</h3>
    <p><strong>Problem:</strong> Write a complete test class for a <code>SearchViewModel</code> that debounces search queries by 300ms, cancels in-flight requests when a new query arrives, and exposes results via <code>StateFlow&lt;SearchState&gt;</code>. Include tests for: debounce behavior, cancellation of previous search, empty query returning empty state, and error handling.</p>
    <pre class="code-block"><code class="language-kotlin">// SearchViewModel.kt (SUT)
class SearchViewModel(
    private val repository: SearchRepository,
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) : ViewModel() {

    private val _query = MutableStateFlow("")
    private val _state = MutableStateFlow&lt;SearchState&gt;(SearchState.Empty)
    val state: StateFlow&lt;SearchState&gt; = _state.asStateFlow()

    init {
        viewModelScope.launch {
            _query
                .debounce(300L)
                .distinctUntilChanged()
                .collectLatest { query ->
                    if (query.isBlank()) {
                        _state.value = SearchState.Empty
                        return@collectLatest
                    }
                    _state.value = SearchState.Loading
                    try {
                        val results = repository.search(query)
                        _state.value = SearchState.Success(results)
                    } catch (e: Exception) {
                        _state.value = SearchState.Error(e.message ?: "Search failed")
                    }
                }
        }
    }

    fun onQueryChanged(query: String) { _query.value = query }
}

// SearchViewModelTest.kt — full solution
@OptIn(ExperimentalCoroutinesApi::class)
class SearchViewModelTest {

    private val testDispatcher = StandardTestDispatcher()
    private val repository: SearchRepository = mockk()
    private lateinit var viewModel: SearchViewModel

    @Before
    fun setUp() {
        Dispatchers.setMain(testDispatcher)
        viewModel = SearchViewModel(repository, testDispatcher)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
        unmockkAll()
    }

    @Test
    fun `empty query returns Empty state without calling repository`() = runTest(testDispatcher) {
        viewModel.state.test {
            assertThat(awaitItem()).isEqualTo(SearchState.Empty)
            viewModel.onQueryChanged("")
            advanceTimeBy(400)
            // Should still be Empty, no Loading emitted
            expectNoEvents()
            cancelAndIgnoreRemainingEvents()
        }
        coVerify(exactly = 0) { repository.search(any()) }
    }

    @Test
    fun `query debounces by 300ms before searching`() = runTest(testDispatcher) {
        val results = listOf(SearchResult("Pixel 9"))
        coEvery { repository.search("pixel") } returns results

        viewModel.state.test {
            assertThat(awaitItem()).isEqualTo(SearchState.Empty)
            viewModel.onQueryChanged("p")
            viewModel.onQueryChanged("pi")
            viewModel.onQueryChanged("pix")
            viewModel.onQueryChanged("pixe")
            viewModel.onQueryChanged("pixel")

            advanceTimeBy(200)
            expectNoEvents() // Debounce hasn't fired yet

            advanceTimeBy(200) // Now 400ms past last keystroke
            assertThat(awaitItem()).isEqualTo(SearchState.Loading)
            advanceUntilIdle()
            assertThat(awaitItem()).isEqualTo(SearchState.Success(results))
            cancelAndIgnoreRemainingEvents()
        }
        // Repository called only once despite 5 query changes
        coVerify(exactly = 1) { repository.search("pixel") }
    }

    @Test
    fun `new query cancels in-flight search via collectLatest`() = runTest(testDispatcher) {
        val slowResults = listOf(SearchResult("Android"))
        val fastResults = listOf(SearchResult("Kotlin"))
        coEvery { repository.search("android") } coAnswers {
            delay(500); slowResults
        }
        coEvery { repository.search("kotlin") } returns fastResults

        viewModel.state.test {
            assertThat(awaitItem()).isEqualTo(SearchState.Empty)
            viewModel.onQueryChanged("android")
            advanceTimeBy(400) // debounce fires, search starts
            assertThat(awaitItem()).isEqualTo(SearchState.Loading)

            viewModel.onQueryChanged("kotlin")
            advanceTimeBy(400) // debounce fires, "android" search cancelled
            // Loading again for "kotlin"
            assertThat(awaitItem()).isEqualTo(SearchState.Loading)
            advanceUntilIdle()
            val success = awaitItem() as SearchState.Success
            assertThat(success.results).isEqualTo(fastResults)
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `repository error emits Error state`() = runTest(testDispatcher) {
        coEvery { repository.search("crash") } throws IOException("Network error")

        viewModel.state.test {
            assertThat(awaitItem()).isEqualTo(SearchState.Empty)
            viewModel.onQueryChanged("crash")
            advanceTimeBy(400)
            assertThat(awaitItem()).isEqualTo(SearchState.Loading)
            advanceUntilIdle()
            val error = awaitItem() as SearchState.Error
            assertThat(error.message).isEqualTo("Network error")
            cancelAndIgnoreRemainingEvents()
        }
    }
}
</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="28" data-item="0"> ✅ Understood Why &amp; What</label>
    <label class="progress-check"><input type="checkbox" data-topic="28" data-item="1"> ✅ Can explain How it works internally</label>
    <label class="progress-check"><input type="checkbox" data-topic="28" data-item="2"> ✅ Reviewed Common Mistakes</label>
    <label class="progress-check"><input type="checkbox" data-topic="28" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="28" data-item="4"> ✅ Solved Coding Challenge</label>
  </div>
</section>

<!-- ==================== TOPIC 29: ANDROID PERFORMANCE ==================== -->
<section class="topic-section" id="topic-29">
  <div class="topic-header">
    <div class="topic-header-icon">⚡</div>
    <div class="topic-header-text">
      <h1>Android Performance</h1>
      <p class="topic-tagline">ANR diagnosis, 16ms frame budget, Perfetto, Baseline Profiles, Macrobenchmark — ship smooth apps</p>
      <div class="category-badge-group">
        <span class="cat-pill">Performance</span>
        <span class="cat-pill">ANR</span>
        <span class="cat-pill">Perfetto</span>
        <span class="cat-pill">Baseline Profiles</span>
        <span class="cat-pill">Macrobenchmark</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 29-1: ANR, Frame Budget, Rendering -->
  <div class="subtopic" id="subtopic-29-1">
    <h2>ANR Diagnosis, 16ms Frame Budget &amp; Rendering Pipeline</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Google Play store ratings and user retention are directly correlated with app smoothness. A single ANR (Application Not Responding) dialog causes 50%+ of affected users to uninstall. Dropped frames make apps feel cheap. The Google Play Vitals dashboard tracks ANR rate, crash rate, and slow rendering — apps exceeding thresholds get demoted in search rankings. On lower-end devices (which are 70%+ of the global Android market), performance bugs surface that developers with flagship phones never notice. Systematic performance engineering is not optional — it's a competitive differentiator.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p><strong>ANR (Application Not Responding)</strong> occurs when the main thread is blocked for &gt;5 seconds (user input) or a BroadcastReceiver doesn't complete in 10 seconds. Android shows the ANR dialog. <strong>The 16ms frame budget</strong>: at 60fps, each frame has 16.67ms to complete measure, layout, draw, and RenderThread work. At 90fps (Pixel 7+): 11ms. At 120fps: 8.33ms. Exceeding the budget drops frames (jank). The <strong>rendering pipeline</strong>: CPU (measure/layout/draw) → RenderThread (display list recording) → GPU (rasterization) → SurfaceFlinger (compositing) → display.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <p>ANR root causes and fixes:</p>
      <pre class="code-block"><code class="language-kotlin">// ❌ ANR-causing patterns
class MainActivity : AppCompatActivity() {

    // NEVER do this — blocks main thread
    fun loadDataBad() {
        val data = URLConnection.openConnection(URL("https://api.example.com/data"))
            .getInputStream().readBytes() // BLOCKS MAIN THREAD → ANR

        val prefs = getSharedPreferences("app", MODE_PRIVATE)
        prefs.edit().putString("key", "value").commit() // commit() is synchronous!

        val db = Room.databaseBuilder(this, AppDatabase::class.java, "db").build()
        val items = db.itemDao().getAll() // Direct Room query on main thread → crash
    }
}

// ✅ Correct — all I/O on background thread
class MainActivity : AppCompatActivity() {

    private val viewModel: MainViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch {
            viewModel.data.collect { state ->
                updateUi(state) // Only UI work on main thread
            }
        }
    }
}

class MainViewModel(private val repo: DataRepository) : ViewModel() {
    val data = flow {
        emit(UiState.Loading)
        try {
            val result = repo.fetchData() // suspends on IO dispatcher
            emit(UiState.Success(result))
        } catch (e: Exception) {
            emit(UiState.Error(e.message))
        }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), UiState.Loading)
}

// Detecting jank — use Choreographer
class FrameRateMonitor(private val onJank: (Double) -> Unit) {
    private var lastFrameTime = 0L

    private val frameCallback = object : Choreographer.FrameCallback {
        override fun doFrame(frameTimeNanos: Long) {
            if (lastFrameTime != 0L) {
                val frameDurationMs = (frameTimeNanos - lastFrameTime) / 1_000_000.0
                if (frameDurationMs > 16.67) {
                    onJank(frameDurationMs) // Jank detected
                }
            }
            lastFrameTime = frameTimeNanos
            Choreographer.getInstance().postFrameCallback(this)
        }
    }

    fun start() = Choreographer.getInstance().postFrameCallback(frameCallback)
    fun stop() = Choreographer.getInstance().removeFrameCallback(frameCallback)
}

// StrictMode for catching main thread violations during development
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(
                StrictMode.ThreadPolicy.Builder()
                    .detectAll()
                    .penaltyLog()
                    .penaltyDeath() // Crash on violation in debug
                    .build()
            )
            StrictMode.setVmPolicy(
                StrictMode.VmPolicy.Builder()
                    .detectLeakedSqlLiteObjects()
                    .detectLeakedClosableObjects()
                    .penaltyLog()
                    .build()
            )
        }
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// Macrobenchmark — startup and scroll benchmarks
@RunWith(AndroidJUnit4::class)
class StartupBenchmark {

    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun startupCold() = benchmarkRule.measureRepeated(
        packageName = "com.example.myapp",
        metrics = listOf(StartupTimingMetric()),
        iterations = 5,
        startupMode = StartupMode.COLD
    ) {
        pressHome()
        startActivityAndWait()
    }

    @Test
    fun scrollBenchmark() = benchmarkRule.measureRepeated(
        packageName = "com.example.myapp",
        metrics = listOf(FrameTimingMetric()),
        iterations = 5,
        startupMode = StartupMode.WARM
    ) {
        startActivityAndWait()
        val device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation())
        device.findObject(By.res("product_list")).also { list ->
            repeat(5) { list.fling(Direction.DOWN) }
        }
    }
}

// Baseline Profiles — generate with Macrobenchmark
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {

    @get:Rule
    val rule = BaselineProfileRule()

    @Test
    fun generate() = rule.collect(
        packageName = "com.example.myapp"
    ) {
        pressHome()
        startActivityAndWait()
        // Navigate critical paths
        device.findObject(By.text("Products")).click()
        device.findObject(By.text("Pixel 9 Pro")).click()
    }
}

// Apply baseline profile in app module
// src/main/baseline-prof.txt (generated automatically)
// build.gradle.kts
dependencies {
    implementation("androidx.profileinstaller:profileinstaller:1.3.1")
}

// Trace sections for Perfetto analysis
fun heavyOperation() {
    android.os.Trace.beginSection("HeavyOperation")
    try {
        // your work
    } finally {
        android.os.Trace.endSection()
    }
}
</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example — Automotive: Maps Rendering Performance</h3>
      <p>An automotive navigation app must render maps at 60fps even during complex route calculations. Any frame drop causes jarring map movement visible to drivers.</p>
      <pre class="code-block"><code class="language-kotlin">// OffscreenMapRenderer — pre-renders map tiles off the main thread
class OffscreenMapRenderer(
    private val tileCache: TileCache,
    private val renderScope: CoroutineScope = CoroutineScope(Dispatchers.Default)
) {
    // Pre-render tiles for predicted panning direction
    fun prefetchTiles(center: LatLng, zoomLevel: Int, predictedDirection: Direction) {
        renderScope.launch {
            val tilesToFetch = calculatePredictedTiles(center, zoomLevel, predictedDirection)
            tilesToFetch.map { tile ->
                async { tileCache.fetchAndCacheTile(tile) }
            }.awaitAll()
        }
    }

    // Use hardware layers for frequently animated views
    fun setupMapView(mapView: View) {
        mapView.setLayerType(View.LAYER_TYPE_HARDWARE, null)
    }

    // Batch canvas draw calls to reduce GPU state changes
    fun drawRouteOverlay(canvas: Canvas, route: List&lt;LatLng&gt;, paint: Paint) {
        val path = Path()
        route.forEachIndexed { index, point ->
            val (x, y) = projectToScreen(point)
            if (index == 0) path.moveTo(x, y) else path.lineTo(x, y)
        }
        canvas.drawPath(path, paint) // Single draw call for entire route
    }
}

// Compose performance — remember expensive calculations
@Composable
fun RouteMap(route: List&lt;LatLng&gt;, modifier: Modifier = Modifier) {
    // Expensive projection only recalculated when route changes
    val projectedPoints = remember(route) {
        route.map { latLng -> projectToScreenCoordinates(latLng) }
    }

    // Use derivedStateOf for computed state to avoid unnecessary recompositions
    val routeLength by remember {
        derivedStateOf { projectedPoints.size }
    }

    Canvas(modifier = modifier) {
        // Draw only visible portion of route
        val visiblePoints = projectedPoints.filter { (x, y) ->
            x in 0f..size.width && y in 0f..size.height
        }
        drawRoute(visiblePoints)
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Doing disk I/O in RecyclerView.onBindViewHolder():</strong> Binding 100 items × 10ms disk read = 1 second of main thread blocking. — ✅ Fix: Pre-load data in ViewModel; bind only in-memory data in onBindViewHolder().</li>
        <li>❌ <strong>Deeply nested layouts:</strong> Each extra nesting level adds measure passes (RelativeLayout does 2 passes). — ✅ Fix: Use ConstraintLayout for flat hierarchies; use merge tags to eliminate redundant ViewGroups.</li>
        <li>❌ <strong>Creating objects in onDraw():</strong> Allocating Paint, Path, or Rect objects during every frame triggers GC, causing frame drops. — ✅ Fix: Pre-allocate all objects as class fields, reuse them in onDraw().</li>
        <li>❌ <strong>Not using Baseline Profiles:</strong> Without them, the JIT compiler interprets bytecode cold — app startup can be 30-40% slower. — ✅ Fix: Generate Baseline Profiles with Macrobenchmark and ship <code>baseline-prof.txt</code> in the release APK.</li>
        <li>❌ <strong>Overdraw:</strong> Drawing the same pixel multiple times (background + card + text). — ✅ Fix: Enable GPU Overdraw visualization in Developer Options; use <code>windowBackground</code> wisely and avoid opaque backgrounds on invisible views.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Performance engineering at scale starts with measurement. We integrate Macrobenchmark into CI for startup time regression detection — any PR that increases cold startup by &gt;50ms is automatically flagged. We generate Baseline Profiles during our release process, which AOT-compiles our critical paths and improves startup by 30-40%. For ANR diagnosis, we analyze ANR traces from Play Console — the key is the main thread stack trace at the time of ANR. Most ANRs fall into three categories: network on main thread (fix: move to coroutine), SharedPreferences.commit() (fix: use apply() or DataStore), or holding a lock (fix: restructure concurrency). For render performance, we use Perfetto to identify janky frames and trace custom sections with android.os.Trace to pinpoint which operation exceeds the 16ms budget."</p>
      </div>
    </div>
  </div>

  <!-- Q&A Section -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is an ANR and what are the most common causes?</div>
      <div class="qa-answer">
        <p><strong>ANR (Application Not Responding)</strong> is triggered when the main/UI thread is blocked and cannot process user input or draw for &gt;5 seconds. Android shows a system dialog offering the user to "Wait" or "Close App".</p>
        <p><strong>Most common causes:</strong></p>
        <ul>
          <li>Network calls on the main thread (<code>HttpURLConnection.connect()</code>, Retrofit without coroutines)</li>
          <li>Disk I/O on main thread (SharedPreferences.commit(), reading files directly)</li>
          <li>Heavy computation (image processing, JSON parsing of large payloads)</li>
          <li>Database queries without background thread</li>
          <li>Deadlocks between threads</li>
          <li>BroadcastReceiver.onReceive() taking &gt;10 seconds</li>
        </ul>
        <p><strong>Diagnosis:</strong> Play Console ANR traces show the main thread stack at ANR time. Use StrictMode in debug builds to catch violations before they reach production.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q2</span>Why is the frame budget 16ms at 60fps? What happens when you miss it?</div>
      <div class="qa-answer">
        <p>At 60fps, the display refreshes every 1000ms ÷ 60 = <strong>16.67ms</strong>. Within this window, the system must complete: measure → layout → draw (CPU), RenderThread recording, GPU rasterization, and SurfaceFlinger compositing.</p>
        <p>If the frame isn't ready in 16.67ms, the display shows the <em>previous</em> frame again — a "dropped frame" (also called jank). Users perceive this as stuttering. Multiple consecutive dropped frames make scrolling feel laggy.</p>
        <p><strong>Higher refresh rate devices</strong>: Pixel 7 (90fps → 11.1ms), Pixel 8 Pro (120fps → 8.33ms). Apps targeting these devices have even tighter budgets.</p>
        <p><strong>Detection</strong>: <code>adb shell dumpsys gfxinfo com.example.app</code> shows janky frames percentage. Perfetto shows per-frame timing. FrameTimingMetric in Macrobenchmark reports P50/P90/P99 frame durations.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>What are Baseline Profiles and how do they improve startup time?</div>
      <div class="qa-answer">
        <p>By default, Android uses Just-In-Time (JIT) compilation — code is interpreted the first time it runs, then gradually compiled to native code in the background. This means <strong>cold startup</strong> is slow because all code starts interpreted.</p>
        <p><strong>Baseline Profiles</strong> (introduced in Android 9, fully supported from API 24+) provide a list of classes and methods that should be <strong>Ahead-Of-Time (AOT) compiled</strong> when the APK is installed. This avoids JIT interpretation on the critical startup path.</p>
        <p><strong>How to create:</strong></p>
        <ol>
          <li>Add Macrobenchmark module to your project</li>
          <li>Write a <code>BaselineProfileRule</code> test that exercises startup + critical user journeys</li>
          <li>Run with <code>./gradlew :macrobenchmark:generateBaselineProfile</code></li>
          <li>The generated <code>baseline-prof.txt</code> is placed in <code>src/main/</code></li>
          <li>AGP bundles it into the release APK; Play installs it via <code>profileinstaller</code> library</li>
        </ol>
        <p><strong>Results:</strong> Google reports 30-40% faster startup, 15-20% smoother initial scrolling. Works on Android 7+ (older versions gracefully ignore the profile).</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q4</span>How does Perfetto differ from Systrace, and what can you find in a Perfetto trace?</div>
      <div class="qa-answer">
        <p><strong>Systrace</strong> (legacy) was the original Android tracing tool — HTML-based output, limited to system events. Deprecated in favor of Perfetto.</p>
        <p><strong>Perfetto</strong> is the modern, low-overhead tracing system built into Android 9+. It captures system-wide data including:</p>
        <ul>
          <li>CPU scheduler events (which thread is running on which core)</li>
          <li>GPU activity and render frames (per-frame timing visible as "Choreographer#doFrame")</li>
          <li>Custom app trace sections (via <code>android.os.Trace.beginSection()</code>)</li>
          <li>Memory allocations and GC events</li>
          <li>I/O and disk access patterns</li>
          <li>Binder IPC calls between processes</li>
        </ul>
        <p><strong>In Android Studio</strong>, use CPU Profiler → System Trace to get an integrated Perfetto view. Look for: main thread frames taking &gt;16ms, GC pauses interrupting frame rendering, Binder calls blocking the main thread, and your custom <code>Trace.beginSection()</code> annotations pinpointing slow functions.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q5</span>A user reports that scrolling a RecyclerView with images is janky on mid-range devices. How do you diagnose and fix it?</div>
      <div class="qa-answer">
        <p><strong>Diagnosis steps:</strong></p>
        <ol>
          <li>Run Macrobenchmark <code>FrameTimingMetric</code> on the affected device to quantify P99 frame time</li>
          <li>Capture Perfetto trace during scroll — look for: onBindViewHolder duration, Bitmap decode operations on main thread, GC pauses</li>
          <li>Enable GPU Overdraw in Developer Options to check overdraw severity</li>
          <li>Check <code>adb shell dumpsys gfxinfo</code> for janky frames count</li>
        </ol>
        <p><strong>Common fixes:</strong></p>
        <ul>
          <li>Image loading: Use Coil/Glide with proper caching and <code>crossfade(true)</code>. Decode Bitmaps on background thread (they do this by default)</li>
          <li>Fixed item sizes: Set <code>setHasFixedSize(true)</code> on RecyclerView and use fixed height items to avoid re-measure</li>
          <li>RecycledViewPool: Share across multiple RecyclerViews if nested</li>
          <li>Prefetch: <code>LinearLayoutManager.setInitialPrefetchItemCount(4)</code> pre-binds items during idle time</li>
          <li>Avoid allocations in onBindViewHolder: Pre-create formatters, drawables, and click listeners</li>
          <li>DiffUtil for partial updates instead of <code>notifyDataSetChanged()</code></li>
        </ul>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>How would you set up a CI performance regression detection system for app startup time?</div>
      <div class="qa-answer">
        <p><strong>Architecture:</strong></p>
        <ol>
          <li><strong>Macrobenchmark test</strong>: Write a <code>StartupBenchmark</code> with <code>StartupTimingMetric</code>, COLD/WARM/HOT startup modes, 10+ iterations for statistical confidence</li>
          <li><strong>Benchmarking device</strong>: Use a fixed physical device (not emulator — too variable) locked to a specific CPU frequency with <code>lockClocks.sh</code> script from AOSP for reproducibility</li>
          <li><strong>CI step</strong>: Run benchmark on every merge to main via Firebase Test Lab or a dedicated benchmark device farm. Output JSON results artifact</li>
          <li><strong>Threshold detection</strong>: Parse JSON results in a CI script; fail the build if P50 cold startup exceeds baseline + 10% or absolute threshold (e.g., &gt;600ms)</li>
          <li><strong>Historical tracking</strong>: Store benchmark results in a time-series database (InfluxDB/BigQuery) and display in a Grafana dashboard</li>
          <li><strong>Bisect on regression</strong>: When a regression is detected, use <code>git bisect</code> with automated benchmark runs to find the offending commit</li>
        </ol>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge</h3>
    <p><strong>Problem:</strong> Write a Macrobenchmark test that measures cold startup time AND scroll performance for a product list screen. Include proper setup, metrics collection, and explain how to interpret the results.</p>
    <pre class="code-block"><code class="language-kotlin">// :macrobenchmark module
// build.gradle.kts
plugins { id("com.android.test"); id("org.jetbrains.kotlin.android") }
android {
    targetProjectPath = ":app"
    experimentalProperties["android.experimental.self-instrumenting"] = true
}
dependencies {
    implementation("androidx.test.ext:junit:1.1.5")
    implementation("androidx.test.uiautomator:uiautomator:2.2.0")
    implementation("androidx.benchmark:benchmark-macro-junit4:1.2.4")
}

// ShopAppBenchmark.kt
@RunWith(AndroidJUnit4::class)
class ShopAppBenchmark {

    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    // COLD startup — process killed, no memory cached
    @Test
    fun coldStartup() = benchmarkRule.measureRepeated(
        packageName = "com.example.shopapp",
        metrics = listOf(
            StartupTimingMetric(),       // timeToInitialDisplay, timeToFullDisplay
            FrameTimingMetric()          // P50/P90/P99 frame durations
        ),
        compilationMode = CompilationMode.Full(), // Simulates release (AOT compiled)
        startupMode = StartupMode.COLD,
        iterations = 10,
        setupBlock = {
            // Ensure we start from home screen
            pressHome()
        }
    ) {
        startActivityAndWait()
        // Wait for product list to fully load
        device.wait(
            Until.hasObject(By.res("com.example.shopapp:id/product_list")),
            5_000L
        )
    }

    // Scroll performance benchmark
    @Test
    fun productListScroll() = benchmarkRule.measureRepeated(
        packageName = "com.example.shopapp",
        metrics = listOf(FrameTimingMetric()),
        compilationMode = CompilationMode.Full(),
        startupMode = StartupMode.WARM, // App already started
        iterations = 5,
        setupBlock = {
            pressHome()
            startActivityAndWait()
        }
    ) {
        val productList = device.findObject(
            By.res("com.example.shopapp:id/product_list")
        )
        // Fling down 5 times to stress-test scroll performance
        repeat(5) {
            productList.fling(Direction.DOWN, 5000) // high velocity fling
            SystemClock.sleep(500) // brief pause between flings
        }
        repeat(3) {
            productList.fling(Direction.UP, 5000)
            SystemClock.sleep(500)
        }
    }
}

/*
 * How to run:
 * ./gradlew :macrobenchmark:connectedReleaseAndroidTest -P android.testInstrumentationRunnerArguments.androidx.benchmark.suppressErrors=EMULATOR
 *
 * Interpreting results (printed to logcat + JSON artifact):
 * StartupTimingMetric:
 *   timeToInitialDisplay (TTID): Time until first frame drawn. Target: < 500ms
 *   timeToFullDisplay (TTFD): Time until Activity.reportFullyDrawn() called. Target: < 1500ms
 *
 * FrameTimingMetric:
 *   frameDurationCpuMs[P50]=10.2ms  — 50% of frames under 10.2ms (good, within 16ms budget)
 *   frameDurationCpuMs[P90]=18.7ms  — 10% of frames exceed 16ms (some jank)
 *   frameDurationCpuMs[P99]=45.3ms  — 1% of frames very slow (investigate with Perfetto)
 *   frameOverrunMs[P99]=28.6ms      — worst frames overrun their deadline by 28ms
 *
 * A P99 frameDuration > 2x the frame budget (32ms at 60fps) indicates a significant jank
 * problem that needs Perfetto investigation to pinpoint the root cause.
 */
</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="29" data-item="0"> ✅ Understood Why &amp; What</label>
    <label class="progress-check"><input type="checkbox" data-topic="29" data-item="1"> ✅ Can explain How it works internally</label>
    <label class="progress-check"><input type="checkbox" data-topic="29" data-item="2"> ✅ Reviewed Common Mistakes</label>
    <label class="progress-check"><input type="checkbox" data-topic="29" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="29" data-item="4"> ✅ Solved Coding Challenge</label>
  </div>
</section>

<!-- ==================== TOPIC 30: MEMORY MANAGEMENT ==================== -->
<section class="topic-section" id="topic-30">
  <div class="topic-header">
    <div class="topic-header-icon">🧠</div>
    <div class="topic-header-text">
      <h1>Memory Management</h1>
      <p class="topic-tagline">GC types, Reference types, LeakCanary, common leak patterns, Bitmap handling, onTrimMemory</p>
      <div class="category-badge-group">
        <span class="cat-pill">Memory</span>
        <span class="cat-pill">GC</span>
        <span class="cat-pill">LeakCanary</span>
        <span class="cat-pill">Bitmaps</span>
        <span class="cat-pill">References</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 30-1: GC and Reference Types -->
  <div class="subtopic" id="subtopic-30-1">
    <h2>GC Types, Reference Hierarchy &amp; Memory Leak Patterns</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Android devices have limited RAM — even flagship devices have 12GB shared across all apps. The system aggressively kills background apps to reclaim memory. If your app leaks memory, it grows continuously until either the system kills it (bad user experience) or triggers an OOM crash. Memory leaks in Activities are particularly catastrophic: a single retained Activity prevents GC from collecting its entire view hierarchy (potentially 50MB+). At scale, understanding memory management means the difference between an app that's kept in memory by the system (better resume time, better UX) and one that's constantly killed.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p>Android's runtime (ART) uses a <strong>generational garbage collector</strong>:</p>
      <ul>
        <li><strong>Young generation (Minor GC):</strong> Short-lived objects. Collected frequently, quickly. Pause: ~1-5ms.</li>
        <li><strong>Old generation (Major GC):</strong> Long-lived objects promoted from young gen. Collected less frequently. Pause: ~10-50ms — can cause frame drops.</li>
        <li><strong>Large Object Space:</strong> Bitmaps and other large allocations go here directly.</li>
      </ul>
      <p><strong>Java Reference Types (by GC strength):</strong></p>
      <ul>
        <li><strong>Strong Reference:</strong> Default. Object never collected while strongly reachable.</li>
        <li><strong>SoftReference:</strong> Collected only when JVM is running low on memory. Use for memory-sensitive caches.</li>
        <li><strong>WeakReference:</strong> Collected at next GC cycle. Use to hold references to objects without preventing collection (event listeners, caches).</li>
        <li><strong>PhantomReference:</strong> Object already finalized; used for cleanup actions via ReferenceQueue. Rarely used directly in Android apps.</li>
      </ul>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// ❌ Memory leak — static reference to Activity
object AppManager {
    var currentActivity: Activity? = null // Static ref → Activity never GC'd!
}

// ❌ Anonymous inner class captures outer class reference
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Handler holds reference to MyActivity via implicit outer class reference
        val handler = Handler(Looper.getMainLooper())
        handler.postDelayed({
            updateUI() // If delayed 5 seconds, Activity might be destroyed but not GC'd
        }, 5000)
    }
}

// ✅ Fix — use WeakReference to avoid retaining Activity
class MyActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())
    private val updateRunnable = Runnable { updateUI() }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacks(updateRunnable) // Always remove callbacks!
    }
}

// ❌ ViewModel holding Context
class BadViewModel(private val context: Context) : ViewModel() {
    // context is an Activity → Activity can't be GC'd even after rotation!
}

// ✅ Fix — use Application context if context needed at all
class GoodViewModel(application: Application) : AndroidViewModel(application) {
    private val appContext = application.applicationContext // Safe — outlives all activities
}

// ❌ Singleton holding Listener (Activity)
object EventBus {
    private val listeners = mutableListOf&lt;EventListener&gt;()
    fun register(listener: EventListener) = listeners.add(listener)
    // No unregister called → Activity listener held forever
}

// ✅ Fix — use WeakReference in listener list
object EventBus {
    private val listeners = mutableListOf&lt;WeakReference&lt;EventListener&gt;&gt;()

    fun register(listener: EventListener) {
        listeners.add(WeakReference(listener))
    }

    fun emit(event: Event) {
        val iterator = listeners.iterator()
        while (iterator.hasNext()) {
            val ref = iterator.next().get()
            if (ref == null) {
                iterator.remove() // Clean up GC'd references
            } else {
                ref.onEvent(event)
            }
        }
    }
}

// Correct Bitmap handling
fun loadBitmapEfficiently(resources: Resources, resId: Int, reqWidth: Int, reqHeight: Int): Bitmap {
    val options = BitmapFactory.Options().apply {
        inJustDecodeBounds = true // Read dimensions without allocating
    }
    BitmapFactory.decodeResource(resources, resId, options)

    options.apply {
        inSampleSize = calculateInSampleSize(this, reqWidth, reqHeight)
        inJustDecodeBounds = false
        inPreferredConfig = Bitmap.Config.RGB_565 // 2 bytes/pixel vs 4 for ARGB_8888
    }
    return BitmapFactory.decodeResource(resources, resId, options)
}

fun calculateInSampleSize(options: BitmapFactory.Options, reqWidth: Int, reqHeight: Int): Int {
    val (height, width) = options.run { outHeight to outWidth }
    var inSampleSize = 1
    if (height > reqHeight || width > reqWidth) {
        val halfHeight = height / 2
        val halfWidth = width / 2
        while ((halfHeight / inSampleSize) >= reqHeight && (halfWidth / inSampleSize) >= reqWidth) {
            inSampleSize *= 2
        }
    }
    return inSampleSize
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// Reference types
val strongRef: MyObject = MyObject()        // default — prevents GC
val softRef = SoftReference(MyObject())     // GC when memory low
val weakRef = WeakReference(myActivity)     // GC at any cycle
val phantomRef = PhantomReference(obj, queue)

// Accessing weak/soft references
val obj = weakRef.get() // Returns null if GC'd
obj?.doWork() ?: run { /* handle GC'd case */ }

// onTrimMemory — respond to system memory pressure
class MyActivity : AppCompatActivity() {
    override fun onTrimMemory(level: Int) {
        super.onTrimMemory(level)
        when (level) {
            ComponentCallbacks2.TRIM_MEMORY_UI_HIDDEN -> {
                // App goes background — clear UI caches
                imageCache.evictAll()
            }
            ComponentCallbacks2.TRIM_MEMORY_RUNNING_CRITICAL,
            ComponentCallbacks2.TRIM_MEMORY_COMPLETE -> {
                // Critically low memory — release everything
                imageCache.evictAll()
                dataCache.clear()
            }
        }
    }
}

// LeakCanary setup (automatic in debug builds)
// build.gradle.kts
debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")

// Custom leak detection for non-Android objects
AppWatcher.objectWatcher.expectWeaklyReachable(
    myObject,
    "MyObject should be GC'd after session end"
)

// Memory profiling — dump heap from code
val debugPath = File(cacheDir, "heap-dump.hprof")
Debug.dumpHprofData(debugPath.absolutePath)
// Then analyze with Android Studio Memory Profiler or leakcanary-object-watcher
</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example — Healthcare: Medical Image Viewer</h3>
      <p>A healthcare app displays high-resolution DICOM medical images (each up to 50MB). Holding all images in memory causes OOM crashes on mid-range devices.</p>
      <pre class="code-block"><code class="language-kotlin">// LruCache-based image cache with memory-aware sizing
class MedicalImageCache {
    private val maxMemory = Runtime.getRuntime().maxMemory()
    private val cacheSize = (maxMemory / 8).toInt() // Use 1/8th of available memory

    private val memoryCache = object : LruCache&lt;String, Bitmap&gt;(cacheSize) {
        override fun sizeOf(key: String, bitmap: Bitmap): Int {
            // Return size in bytes rather than count
            return bitmap.byteCount
        }

        override fun entryRemoved(evicted: Boolean, key: String, old: Bitmap, new: Bitmap?) {
            // Bitmap was evicted from LRU — make it available for GC
            if (!old.isRecycled) {
                // In modern Android (API 26+), Bitmaps are in native memory — just remove reference
                // old.recycle() // Only needed on very old devices
            }
        }
    }

    // Disk cache as second level using DiskLruCache
    private val diskCache: DiskLruCache = DiskLruCache.open(
        File(cacheDir, "dicom_cache"),
        1,  // app version
        1,  // value count per key
        50L * 1024 * 1024 // 50MB disk cache
    )

    suspend fun getImage(studyId: String, sliceIndex: Int): Bitmap? = withContext(Dispatchers.IO) {
        val key = "$studyId-$sliceIndex"

        // 1. Check memory cache (main thread safe)
        memoryCache.get(key)?.let { return@withContext it }

        // 2. Check disk cache
        diskCache.get(key)?.let { snapshot ->
            val bitmap = BitmapFactory.decodeStream(snapshot.getInputStream(0))
            memoryCache.put(key, bitmap) // Promote to memory cache
            snapshot.close()
            return@withContext bitmap
        }

        // 3. Fetch from server with sampling to fit device screen
        val rawBitmap = fetchDicomFromServer(studyId, sliceIndex)
        val sampledBitmap = downscaleToFitMemory(rawBitmap, maxDimension = 2048)

        // Store in both caches
        memoryCache.put(key, sampledBitmap)
        saveToDiskCache(key, sampledBitmap)

        sampledBitmap
    }

    private fun downscaleToFitMemory(original: Bitmap, maxDimension: Int): Bitmap {
        val scale = minOf(
            maxDimension.toFloat() / original.width,
            maxDimension.toFloat() / original.height,
            1.0f
        )
        if (scale >= 1.0f) return original
        val scaled = Bitmap.createScaledBitmap(
            original,
            (original.width * scale).toInt(),
            (original.height * scale).toInt(),
            true
        )
        original.recycle() // Free original immediately
        return scaled
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Registering BroadcastReceiver without unregistering:</strong> The receiver holds a reference to the Activity forever. — ✅ Fix: Unregister in <code>onStop()</code> or <code>onDestroy()</code>; use <code>LifecycleOwner</code>-aware alternatives.</li>
        <li>❌ <strong>Coroutine launched in GlobalScope referencing Activity:</strong> GlobalScope survives the Activity lifecycle. — ✅ Fix: Use <code>lifecycleScope</code> or <code>viewModelScope</code> which auto-cancel on destroy.</li>
        <li>❌ <strong>Non-static inner classes in ViewModel:</strong> Inner class holds implicit reference to outer class. — ✅ Fix: Use static nested classes or top-level classes; pass data explicitly.</li>
        <li>❌ <strong>Bitmap.Config.ARGB_8888 for all images:</strong> A 1920×1080 ARGB_8888 bitmap = 8MB. — ✅ Fix: Use <code>RGB_565</code> (4MB) for images without alpha; use Coil/Glide which downscale to view bounds automatically.</li>
        <li>❌ <strong>Calling bitmap.recycle() prematurely:</strong> If another view still references the bitmap, <code>recycle()</code> causes "Canvas: trying to use a recycled bitmap" crashes. — ✅ Fix: Let GC handle Bitmaps on API 26+ (native memory). Only recycle explicitly in memory-critical situations after confirming no other references.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Memory management in Android is about understanding the GC lifecycle and avoiding common reference traps. The three most common leaks I've encountered in production are: Activities retained by static references (fix: never store Activity in static fields), listeners registered with singletons not unregistered (fix: WeakReference listener lists + explicit unregister), and coroutines launched in GlobalScope capturing Activity context (fix: always use lifecycleScope or viewModelScope). We run LeakCanary in debug builds — it watches every Activity and Fragment for retention after destruction using a WeakReference + ReferenceQueue pattern. When a leak is detected, it dumps the heap and builds a shortest-leak-path report. We also implement onTrimMemory to release image caches when the system is under pressure, which dramatically reduces the chance of our app being killed while backgrounded."</p>
      </div>
    </div>
  </div>

  <!-- Q&A Section -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the difference between WeakReference and SoftReference?</div>
      <div class="qa-answer">
        <p><strong>WeakReference</strong>: The referenced object can be collected by GC at <em>any time</em> — even if there is plenty of free memory. GC ignores weak references when determining reachability. The reference becomes null after GC. Use for: observer patterns, caches where you don't need guaranteed availability, breaking reference cycles.</p>
        <p><strong>SoftReference</strong>: The referenced object is only collected when the JVM is <em>running low on memory</em>. The JVM guarantees all soft references will be cleared before throwing <code>OutOfMemoryError</code>. More expensive than WeakReference. Use for: memory-sensitive caches (LRU bitmap caches) where you want to keep objects if memory allows but don't need them if memory is tight.</p>
        <p>In practice on Android: <code>LruCache</code> with proper <code>sizeOf()</code> is preferred over SoftReference caches — it gives you more predictable memory behavior with explicit size limits.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q2</span>How does LeakCanary detect memory leaks?</div>
      <div class="qa-answer">
        <p><strong>LeakCanary's detection mechanism:</strong></p>
        <ol>
          <li>When an Activity is destroyed, LeakCanary wraps it in a <code>WeakReference</code> and stores the reference with a unique key in a <code>ReferenceQueue</code></li>
          <li>After 5 seconds (configurable), LeakCanary checks if the <code>ReferenceQueue</code> contains the key — if yes, the object was GC'd (no leak)</li>
          <li>If the key is NOT in the queue after 5 seconds, it forces GC (<code>Runtime.getRuntime().gc()</code>) and checks again</li>
          <li>If still not GC'd, LeakCanary triggers a heap dump via <code>Debug.dumpHprofData()</code></li>
          <li>It analyzes the heap dump using Shark (its own heap parser) to find the shortest path from GC roots to the leaked object</li>
          <li>It reports the leak with a human-readable path: "GC ROOT → static field → Activity"</li>
        </ol>
        <p>LeakCanary works for any object, not just Activities — use <code>AppWatcher.objectWatcher.expectWeaklyReachable(obj, "reason")</code> for custom objects.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>Explain the Android GC generations and how to minimize GC pressure in a high-throughput app.</div>
      <div class="qa-answer">
        <p>ART uses a <strong>concurrent, generational GC</strong>:</p>
        <ul>
          <li><strong>Young/nursery generation</strong>: New objects allocated here (bump pointer allocator — very fast). Minor GC is concurrent and usually &lt;2ms pause.</li>
          <li><strong>Old generation</strong>: Long-lived objects promoted from young gen. Major GC is more expensive: concurrent mark, stop-the-world compaction. Pause can be 10-50ms — enough to cause frame drops at 60fps.</li>
        </ul>
        <p><strong>Minimizing GC pressure:</strong></p>
        <ul>
          <li><strong>Object pooling:</strong> Reuse objects instead of creating new ones. Android provides <code>Pools.SimplePool&lt;T&gt;</code> for this pattern. Critical in audio/video processing callbacks called 60fps.</li>
          <li><strong>Avoid allocations in hot paths:</strong> <code>RecyclerView.onBindViewHolder()</code>, <code>View.onDraw()</code>, audio callbacks — pre-allocate all needed objects.</li>
          <li><strong>Use primitives over boxed types:</strong> <code>IntArray</code> vs <code>Array&lt;Int&gt;</code>. Each boxed Integer is a separate heap object.</li>
          <li><strong>SparseArray over HashMap:</strong> Avoids Integer boxing for int keys.</li>
          <li><strong>StringBuilder reuse:</strong> Pre-allocate and clear instead of creating new strings.</li>
        </ul>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q4</span>Why is storing a Context in a ViewModel dangerous and what are the safe alternatives?</div>
      <div class="qa-answer">
        <p>A <code>ViewModel</code> outlives the <code>Activity</code> across configuration changes (screen rotation). If you store an <code>Activity</code> context in the ViewModel, the Activity can't be GC'd even after rotation — the ViewModel holds a strong reference to the old Activity while a new Activity is created. After N rotations, N old Activities leak.</p>
        <p><strong>Even worse</strong>: Each Activity holds references to its entire View hierarchy (potentially 50-100MB on modern phones). Leaking one Activity can easily OOM the app.</p>
        <p><strong>Safe alternatives:</strong></p>
        <ul>
          <li><strong>AndroidViewModel</strong>: Holds Application context (safe — it's a singleton that outlives all Activities)</li>
          <li><strong>Hilt injection</strong>: Inject <code>@ApplicationContext context: Context</code> into ViewModel via constructor, scoped to Application component</li>
          <li><strong>Don't store context at all</strong>: Move context-dependent operations (string formatting, resource access) to the View layer</li>
          <li><strong>Repository pattern</strong>: Repositories can hold Application context if truly needed for database path resolution, etc.</li>
        </ul>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q5</span>Your app's memory usage grows by ~5MB per navigation to a detail screen. How do you diagnose and fix this?</div>
      <div class="qa-answer">
        <p><strong>Diagnosis steps:</strong></p>
        <ol>
          <li>Enable LeakCanary — it will immediately flag if an Activity/Fragment is being retained</li>
          <li>Use Android Studio Memory Profiler: take heap dumps before and after navigation, compare retained objects</li>
          <li>In Memory Profiler, filter by "Activity" class — any Activity with count &gt; 1 after the original is destroyed is a leak</li>
          <li>Use "Record native allocations" to catch Bitmap leaks in native memory (API 26+)</li>
          <li>Check the leak path in LeakCanary: it shows exactly which reference is preventing GC</li>
        </ol>
        <p><strong>Common culprits for ~5MB growth:</strong></p>
        <ul>
          <li>A RecyclerView Adapter or listener registered in a singleton not cleared</li>
          <li>Coroutines in GlobalScope referencing the Fragment/Activity</li>
          <li>Bitmap loaded into an ImageView that's held by a statically referenced cache</li>
          <li>A custom View registered as SensorEventListener / LocationListener without unregistering</li>
        </ul>
        <p><strong>Fix pattern:</strong> Move listener registration to <code>onStart()</code>/<code>onStop()</code> pairs. Use <code>lifecycleScope</code> instead of GlobalScope. Clear Adapters in <code>onDestroyView()</code> (especially important for Fragments — set <code>binding = null</code>).</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>How do you handle Bitmaps efficiently in a feed app that displays hundreds of images?</div>
      <div class="qa-answer">
        <p><strong>Best practices for a high-volume image feed:</strong></p>
        <ul>
          <li><strong>Use Coil or Glide</strong>: They handle all complexity — memory LRU cache, disk cache, downsampling to view bounds, Bitmap recycling/reuse pool, animated GIF, and coroutine integration.</li>
          <li><strong>Specify exact target size</strong>: <code>imageView.load(url) { size(200, 200) }</code> — prevents loading a 4K image to display in a 200px thumbnail</li>
          <li><strong>Bitmap reuse (inBitmap)</strong>: For custom loading, use <code>BitmapFactory.Options.inBitmap</code> to reuse an existing Bitmap's allocation, avoiding new heap allocation</li>
          <li><strong>RGB_565 for opaque images</strong>: Halves memory per pixel (2 bytes vs 4 bytes ARGB_8888)</li>
          <li><strong>Preloading</strong>: Use Coil's <code>PreloadingCoilImagePainter</code> or Glide's preload() to fetch images before they scroll into view</li>
          <li><strong>Cancel requests on scroll</strong>: Coil/Glide automatically cancel in-flight requests when view is recycled via RecyclerView</li>
          <li><strong>Memory pressure response</strong>: Implement <code>onTrimMemory()</code> and call <code>Coil.imageLoader(context).memoryCache?.clear()</code> on TRIM_MEMORY_UI_HIDDEN</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge</h3>
    <p><strong>Problem:</strong> Implement a memory-safe image cache using LruCache that: (1) sizes itself based on available memory, (2) properly evicts bitmaps, (3) responds to onTrimMemory signals, and (4) prevents loading same image multiple times concurrently (deduplication).</p>
    <pre class="code-block"><code class="language-kotlin">class SmartImageCache(context: Context) : ComponentCallbacks2 {

    init {
        // Register for memory callbacks
        context.applicationContext.registerComponentCallbacks(this)
    }

    private val maxMemory = Runtime.getRuntime().maxMemory()
    private val cacheSize = (maxMemory / 8).toInt() // 1/8 of max heap

    private val lruCache = object : LruCache&lt;String, Bitmap&gt;(cacheSize) {
        override fun sizeOf(key: String, value: Bitmap): Int = value.byteCount
    }

    // Deduplication — track in-flight requests
    private val inFlight = ConcurrentHashMap&lt;String, Deferred&lt;Bitmap?&gt;&gt;()
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    suspend fun getBitmap(url: String, targetWidth: Int, targetHeight: Int): Bitmap? {
        val key = "$url-${targetWidth}x$targetHeight"

        // 1. Check memory cache
        lruCache.get(key)?.let { return it }

        // 2. Deduplicate concurrent requests for same key
        return coroutineScope {
            val deferred = inFlight.getOrPut(key) {
                scope.async {
                    try {
                        loadAndSampleBitmap(url, targetWidth, targetHeight)?.also { bitmap ->
                            lruCache.put(key, bitmap)
                        }
                    } finally {
                        inFlight.remove(key)
                    }
                }
            }
            deferred.await()
        }
    }

    private suspend fun loadAndSampleBitmap(
        url: String, reqWidth: Int, reqHeight: Int
    ): Bitmap? = withContext(Dispatchers.IO) {
        try {
            val connection = URL(url).openConnection().apply {
                connectTimeout = 5000; readTimeout = 10000
            }
            val stream = connection.getInputStream()

            // Two-pass decode: first get dimensions, then decode at correct sample size
            val bytes = stream.readBytes()
            val options = BitmapFactory.Options().apply { inJustDecodeBounds = true }
            BitmapFactory.decodeByteArray(bytes, 0, bytes.size, options)

            options.apply {
                inSampleSize = calculateInSampleSize(this, reqWidth, reqHeight)
                inJustDecodeBounds = false
                inPreferredConfig = Bitmap.Config.RGB_565 // Save 50% memory for opaque images
                inMutable = true // Allow reuse as inBitmap in future
            }
            BitmapFactory.decodeByteArray(bytes, 0, bytes.size, options)
        } catch (e: Exception) {
            null
        }
    }

    override fun onTrimMemory(level: Int) {
        when (level) {
            ComponentCallbacks2.TRIM_MEMORY_UI_HIDDEN -> lruCache.trimToSize(cacheSize / 2)
            ComponentCallbacks2.TRIM_MEMORY_RUNNING_CRITICAL,
            ComponentCallbacks2.TRIM_MEMORY_COMPLETE -> lruCache.evictAll()
        }
    }

    override fun onConfigurationChanged(newConfig: Configuration) {}
    override fun onLowMemory() = lruCache.evictAll()

    fun destroy() {
        scope.cancel()
        lruCache.evictAll()
    }

    private fun calculateInSampleSize(opts: BitmapFactory.Options, reqW: Int, reqH: Int): Int {
        var size = 1
        if (opts.outHeight > reqH || opts.outWidth > reqW) {
            val halfH = opts.outHeight / 2; val halfW = opts.outWidth / 2
            while ((halfH / size) >= reqH && (halfW / size) >= reqW) size *= 2
        }
        return size
    }
}
</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="30" data-item="0"> ✅ Understood Why &amp; What</label>
    <label class="progress-check"><input type="checkbox" data-topic="30" data-item="1"> ✅ Can explain How it works internally</label>
    <label class="progress-check"><input type="checkbox" data-topic="30" data-item="2"> ✅ Reviewed Common Mistakes</label>
    <label class="progress-check"><input type="checkbox" data-topic="30" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="30" data-item="4"> ✅ Solved Coding Challenge</label>
  </div>
</section>

<!-- ==================== TOPIC 31: GRADLE & BUILD SYSTEM ==================== -->
<section class="topic-section" id="topic-31">
  <div class="topic-header">
    <div class="topic-header-icon">🔧</div>
    <div class="topic-header-text">
      <h1>Gradle &amp; Build System</h1>
      <p class="topic-tagline">Gradle lifecycle, AGP, build variants, Kotlin DSL, build caching — master the build</p>
      <div class="category-badge-group">
        <span class="cat-pill">Gradle</span>
        <span class="cat-pill">AGP</span>
        <span class="cat-pill">Build Variants</span>
        <span class="cat-pill">Kotlin DSL</span>
        <span class="cat-pill">Caching</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 31-1: Gradle Lifecycle and AGP -->
  <div class="subtopic" id="subtopic-31-1">
    <h2>Gradle Lifecycle, AGP &amp; Build Variants</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Build system knowledge separates senior engineers from mid-level ones. A slow build system kills developer productivity — a 10-minute build for a 50-engineer team costs 500+ engineer-minutes per build cycle. Understanding Gradle's internals lets you: diagnose slow builds with profiling, implement build caching to reduce CI time by 60%+, configure variant-specific code for different environments (dev/staging/prod), and structure multi-module projects for parallel compilation. When you're leading a team, build system expertise is critical for scaling the team without scaling build times.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p><strong>Gradle</strong> is a build automation tool based on a DAG (Directed Acyclic Graph) of tasks. It operates in three lifecycle phases:</p>
      <ol>
        <li><strong>Initialization:</strong> Gradle evaluates <code>settings.gradle.kts</code> to determine which projects/modules are included in the build</li>
        <li><strong>Configuration:</strong> Gradle evaluates <em>all</em> <code>build.gradle.kts</code> files, configures all tasks, and builds the task DAG — even for tasks that won't run</li>
        <li><strong>Execution:</strong> Gradle executes only the tasks required for the requested task, in DAG order, respecting dependencies</li>
      </ol>
      <p><strong>Android Gradle Plugin (AGP)</strong> is the plugin (<code>com.android.application</code> / <code>com.android.library</code>) that integrates Android-specific build logic into Gradle: resource compilation (AAPT2), DEX compilation, manifest merging, signing, and APK/AAB packaging. <strong>Build variants</strong> = product flavor × build type combinations (e.g., <code>freeDebug</code>, <code>paidRelease</code>).</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// settings.gradle.kts — Initialization phase
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
    // Version catalog
    versionCatalogs {
        create("libs") { from(files("gradle/libs.versions.toml")) }
    }
}

rootProject.name = "ShopApp"
include(":app", ":core:network", ":core:database", ":feature:cart", ":feature:catalog")

// app/build.gradle.kts — Configuration phase
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.hilt)
    alias(libs.plugins.ksp)
}

android {
    namespace = "com.example.shopapp"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.example.shopapp"
        minSdk = 26
        targetSdk = 35
        versionCode = libs.versions.versionCode.get().toInt()
        versionName = libs.versions.versionName.get()

        buildConfigField("String", "API_BASE_URL", "\"https://api.example.com\"")
        buildConfigField("Boolean", "FEATURE_DARK_MODE", "true")
        resValue("string", "app_name", "ShopApp")
    }

    buildTypes {
        debug {
            isDebuggable = true
            isMinifyEnabled = false
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
            buildConfigField("String", "API_BASE_URL", "\"https://dev-api.example.com\"")
        }
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }
        create("staging") {
            initWith(getByName("release"))
            applicationIdSuffix = ".staging"
            buildConfigField("String", "API_BASE_URL", "\"https://staging-api.example.com\"")
        }
    }

    // Product flavors for free/paid tiers
    flavorDimensions += "tier"
    productFlavors {
        create("free") {
            dimension = "tier"
            buildConfigField("Boolean", "IS_PREMIUM", "false")
        }
        create("paid") {
            dimension = "tier"
            applicationIdSuffix = ".premium"
            buildConfigField("Boolean", "IS_PREMIUM", "true")
        }
    }

    buildFeatures {
        buildConfig = true
        compose = true
        viewBinding = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = libs.versions.composeCompiler.get()
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// gradle/libs.versions.toml — Version Catalog (modern approach)
[versions]
agp = "8.4.0"
kotlin = "2.0.0"
hilt = "2.51.1"
compose-bom = "2024.05.00"
versionCode = "10"
versionName = "2.1.0"

[libraries]
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
compose-ui = { group = "androidx.compose.ui", name = "ui" }  # Version from BOM
hilt-android = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }
hilt-compiler = { group = "com.google.dagger", name = "hilt-compiler", version.ref = "hilt" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }

// Dependency configurations
dependencies {
    implementation(libs.hilt.android)      // Runtime + test classpath
    ksp(libs.hilt.compiler)                // Annotation processing
    api(libs.core.network)                 // Exposed to consumers (avoid overuse!)
    compileOnly(libs.annotation)           // Compile-time only, not in output
    runtimeOnly(libs.logger)               // Runtime only, not compile classpath
    testImplementation(libs.junit)         // Unit test only
    androidTestImplementation(libs.espresso) // Instrumented test only
    debugImplementation(libs.leakcanary)   // Debug build type only

    // Compose BOM — single version for all compose artifacts
    implementation(platform(libs.compose.bom))
    implementation(libs.compose.ui)        // No version needed — managed by BOM
}

// Build caching config — gradle.properties
org.gradle.caching=true
org.gradle.parallel=true
org.gradle.configureondemand=true
org.gradle.jvmargs=-Xmx4g -XX:MaxMetaspaceSize=512m -XX:+UseParallelGC
kotlin.incremental=true
android.enableR8.fullMode=true

// Custom Gradle task
tasks.register("printBuildVariants") {
    doLast {
        android.applicationVariants.all { variant ->
            println("Variant: ${variant.name} — buildType: ${variant.buildType.name}")
        }
    }
}
</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example — E-Commerce: Multi-Environment Build Configuration</h3>
      <pre class="code-block"><code class="language-kotlin">// buildSrc/src/main/kotlin/AppConfig.kt — convention plugins
object AppConfig {
    const val compileSdk = 35
    const val minSdk = 26
    const val targetSdk = 35
    const val versionCode = 42
    const val versionName = "3.5.1"
}

// build-logic/convention/src/main/kotlin/AndroidLibraryConventionPlugin.kt
class AndroidLibraryConventionPlugin : Plugin&lt;Project&gt; {
    override fun apply(target: Project) {
        with(target) {
            with(pluginManager) {
                apply("com.android.library")
                apply("org.jetbrains.kotlin.android")
            }
            extensions.configure&lt;LibraryExtension&gt; {
                compileSdk = AppConfig.compileSdk
                defaultConfig {
                    minSdk = AppConfig.minSdk
                    testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
                }
                compileOptions {
                    sourceCompatibility = JavaVersion.VERSION_17
                    targetCompatibility = JavaVersion.VERSION_17
                }
            }
        }
    }
}

// feature/cart/build.gradle.kts — uses convention plugin
plugins {
    id("shopapp.android.library")  // Convention plugin — all config in one place!
    id("shopapp.android.hilt")
    id("shopapp.android.compose")
}

dependencies {
    implementation(project(":core:network"))
    implementation(project(":core:database"))
    implementation(libs.compose.material3)
    testImplementation(libs.junit)
    testImplementation(libs.mockk)
}

// Signing config from environment variables (CI/CD safe)
// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_PATH") ?: "debug.keystore")
            storePassword = System.getenv("KEYSTORE_PASSWORD") ?: "android"
            keyAlias = System.getenv("KEY_ALIAS") ?: "androiddebugkey"
            keyPassword = System.getenv("KEY_PASSWORD") ?: "android"
        }
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Using <code>api()</code> everywhere instead of <code>implementation()</code>:</strong> <code>api</code> exposes the dependency to all consumers, causing unnecessary recompilation cascades. — ✅ Fix: Use <code>implementation</code> by default; only use <code>api</code> when consumers genuinely need the type in their public API.</li>
        <li>❌ <strong>Hardcoded version strings across modules:</strong> Updating a library version requires editing 20 files. — ✅ Fix: Use Version Catalogs (<code>libs.versions.toml</code>) as a single source of truth for all versions.</li>
        <li>❌ <strong>Not enabling Gradle build caching:</strong> Every CI run rebuilds everything from scratch. — ✅ Fix: Set <code>org.gradle.caching=true</code> and configure a remote build cache server for multi-machine cache sharing.</li>
        <li>❌ <strong>Tasks that always run (non-incremental):</strong> Custom tasks that don't declare inputs/outputs invalidate build cache. — ✅ Fix: Annotate task inputs with <code>@Input</code>, <code>@InputFile</code> and outputs with <code>@OutputFile</code> for Gradle incremental build support.</li>
        <li>❌ <strong>Duplicating build config across modules:</strong> Each module has its own <code>compileSdk</code>, <code>compileOptions</code>, etc. — ✅ Fix: Use Convention Plugins (build-logic module) to centralize shared build configuration.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Gradle mastery is about reducing build time at scale. In our last project, we reduced CI build time from 18 minutes to 7 minutes by: (1) migrating to Convention Plugins for shared config, (2) enabling remote build cache on a GCS bucket — cache hits skip all compilation for unchanged modules, (3) enabling parallel execution with <code>org.gradle.parallel=true</code>, and (4) migrating to Version Catalogs so dependency updates are a one-line change. For multi-environment configuration, we use build types (debug/staging/release) and inject environment-specific API URLs via <code>buildConfigField</code> so the same code targets different backends without runtime config files. In Kotlin DSL, we get compile-time safety and IDE autocomplete — catching typos in build scripts before they break CI."</p>
      </div>
    </div>
  </div>

  <!-- Q&A Section -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What are the three phases of the Gradle build lifecycle?</div>
      <div class="qa-answer">
        <p><strong>1. Initialization:</strong> Gradle reads <code>settings.gradle.kts</code> to determine the project structure — which modules are included. Creates <code>Project</code> instances for each module. For multi-module projects, this determines what's "in scope" for the build.</p>
        <p><strong>2. Configuration:</strong> Gradle evaluates ALL <code>build.gradle.kts</code> files in ALL modules, even if you're only building one module. It configures every task and builds the complete task dependency graph (DAG). This is why bad code in <code>build.gradle.kts</code> (e.g., slow network calls) slows every build — it runs at configuration time.</p>
        <p><strong>3. Execution:</strong> Gradle determines which tasks need to run (based on what you requested, e.g., <code>assembleDebug</code>) and executes them in the correct order per the DAG. Only tasks that are out-of-date or not in cache are actually executed.</p>
        <p>Key insight: <strong>Configuration on demand</strong> (<code>org.gradle.configureondemand=true</code>) skips configuring modules not relevant to the requested task, speeding up configuration phase for large multi-module projects.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q2</span>What is the difference between implementation, api, and compileOnly dependency configurations?</div>
      <div class="qa-answer">
        <p><strong>implementation:</strong> Dependency is available during compilation AND at runtime, but is <em>NOT</em> exposed to modules that depend on yours. If module A uses <code>implementation(libraryX)</code>, and module B depends on A, then B cannot use libraryX's types directly. This enables better build parallelism — changing libraryX only requires recompiling A, not B.</p>
        <p><strong>api:</strong> Like <code>implementation</code>, but the dependency IS exposed to consumers. B can use libraryX's types. Use when libraryX types appear in A's public API (return types, parameter types of public functions). Overuse of <code>api</code> creates compilation cascades — any change to libraryX forces recompilation of A and all modules depending on A.</p>
        <p><strong>compileOnly:</strong> Available during compilation only — NOT included in the runtime output or APK. Used for annotation processors, compile-time-only APIs (like annotations that are processed by KSP), or Java EE APIs provided by the container.</p>
        <p><strong>runtimeOnly:</strong> Available at runtime but NOT on the compile classpath. Used for JDBC drivers, logging implementations (SLF4J implementations).</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>How does Gradle's build cache work? What is the difference between local and remote cache?</div>
      <div class="qa-answer">
        <p>Gradle's <strong>build cache</strong> stores task outputs keyed by a hash of all task inputs (source files, classpath, environment variables, task parameters). Before executing a task, Gradle checks if an output for that input hash exists in the cache. If yes, it restores the outputs without re-executing the task.</p>
        <p><strong>Task inputs that affect the cache key:</strong> source files content, compiler classpath, JVM version, task configuration, OS-specific settings.</p>
        <p><strong>Local cache</strong> (<code>~/.gradle/caches/build-cache</code>): Stores outputs on your local machine. Helps when you switch branches — builds for old branches can be restored from local cache. Default when <code>org.gradle.caching=true</code>.</p>
        <p><strong>Remote cache</strong> (e.g., GCS, S3, Gradle Enterprise): Shared across all developers and CI machines. Developer A builds feature X → CI and Developer B can reuse the cache. Dramatically reduces CI build times for unchanged modules.</p>
        <p><strong>Cache misses are caused by:</strong> Non-reproducible builds (timestamps in outputs), non-cacheable tasks (not declaring inputs/outputs), absolute paths in outputs (use project-relative paths).</p>
        <pre class="code-block"><code class="language-kotlin">// settings.gradle.kts — configure remote build cache
buildCache {
    local { isEnabled = true }
    remote&lt;HttpBuildCache&gt; {
        url = uri("https://cache.mycompany.com/cache/")
        isPush = System.getenv("CI") != null // Only CI pushes to cache
        isEnabled = true
        credentials {
            username = System.getenv("CACHE_USER")
            password = System.getenv("CACHE_PASSWORD")
        }
    }
}
</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q4</span>What is the difference between Kotlin DSL and Groovy DSL for Gradle? Why is Kotlin DSL preferred for large teams?</div>
      <div class="qa-answer">
        <p><strong>Groovy DSL</strong> (<code>.gradle</code> files): Dynamic language. No type checking. Limited IDE support (autocomplete is guesswork). Can call any method dynamically — great flexibility, terrible discoverability. Very compact syntax but easy to make typos that only fail at build time.</p>
        <p><strong>Kotlin DSL</strong> (<code>.gradle.kts</code> files): Statically typed. Full IDE autocomplete and navigation. Type-safe configuration. Compile-time error detection for build scripts. Refactoring support. All the Kotlin language features (lambdas, extension functions, when expressions) available.</p>
        <p><strong>Why Kotlin DSL for large teams:</strong></p>
        <ul>
          <li><strong>Discoverability:</strong> Press Ctrl+Space in build.gradle.kts to see all available methods — no need to guess or google</li>
          <li><strong>Compile-time safety:</strong> Typos in method names fail at configuration phase, not silently at runtime</li>
          <li><strong>IDE integration:</strong> IntelliJ/Android Studio fully understands Kotlin DSL — navigate to source, find usages, rename refactoring all work</li>
          <li><strong>Consistency:</strong> Same language as production code — no mental context switch</li>
          <li><strong>Drawback:</strong> Slightly slower first-time script compilation (subsequent runs are cached)</li>
        </ul>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q5</span>Your Android project build takes 15 minutes locally. How do you investigate and reduce build time?</div>
      <div class="qa-answer">
        <p><strong>Step 1 — Profile the build:</strong></p>
        <pre class="code-block"><code class="language-bash">./gradlew assembleDebug --profile --scan
# Opens build scan at gradle.com with flamegraph of task timing</code></pre>
        <p><strong>Step 2 — Identify bottlenecks:</strong> Look for tasks that take the most wall-clock time. Common culprits: kapt annotation processing, R8/ProGuard in debug builds, lint, large source sets.</p>
        <p><strong>Step 3 — Apply fixes:</strong></p>
        <ul>
          <li><strong>Enable build caching:</strong> <code>org.gradle.caching=true</code> — unchanged modules served from cache</li>
          <li><strong>Migrate from kapt to KSP:</strong> KSP is 2x faster for annotation processing (Hilt, Room, Moshi)</li>
          <li><strong>Disable R8/ProGuard in debug:</strong> <code>isMinifyEnabled = false</code> for debug (should already be default)</li>
          <li><strong>Enable parallel execution:</strong> <code>org.gradle.parallel=true</code></li>
          <li><strong>Increase Gradle heap:</strong> <code>org.gradle.jvmargs=-Xmx4g</code></li>
          <li><strong>Modularize the project:</strong> Smaller modules compile in parallel, and unchanged modules are cached</li>
          <li><strong>Configuration on demand:</strong> <code>org.gradle.configureondemand=true</code></li>
          <li><strong>Move lint to CI only:</strong> Don't run lint on every local build</li>
          <li><strong>Use latest AGP/Kotlin versions:</strong> Each version brings build performance improvements</li>
        </ul>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>How do you manage different API keys and configuration for debug, staging, and release builds safely?</div>
      <div class="qa-answer">
        <p><strong>Approach 1 — BuildConfig fields (most common):</strong></p>
        <pre class="code-block"><code class="language-kotlin">buildTypes {
    debug {
        buildConfigField("String", "API_KEY", "\"debug_key_abc123\"")
        buildConfigField("String", "BASE_URL", "\"https://dev-api.example.com\"")
    }
    release {
        // For production secrets — inject from CI environment, not hardcoded!
        buildConfigField("String", "API_KEY", "\"${System.getenv("PROD_API_KEY") ?: ""}\"")
        buildConfigField("String", "BASE_URL", "\"https://api.example.com\"")
    }
}
// Access: BuildConfig.API_KEY, BuildConfig.BASE_URL</code></pre>
        <p><strong>Approach 2 — local.properties (NOT committed to git):</strong></p>
        <pre class="code-block"><code class="language-kotlin">// local.properties (gitignored)
// PROD_API_KEY=real_secret_key

// build.gradle.kts — read from local.properties
val localProperties = Properties().apply {
    val file = rootProject.file("local.properties")
    if (file.exists()) load(file.inputStream())
}
buildConfigField("String", "API_KEY", "\"${localProperties["PROD_API_KEY"]}\"")
</code></pre>
        <p><strong>Security rule</strong>: Never commit API keys to git. Use <code>local.properties</code> for local dev and CI environment variables for builds. For extra security, store secrets in Android Keystore or fetch from a secure config service at runtime rather than embedding in the APK (which can be decompiled).</p>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge</h3>
    <p><strong>Problem:</strong> Write a Convention Plugin that enforces company-wide Android library standards: compileSdk=35, minSdk=26, Java 17 compatibility, Kotlin strict mode, and automatically applies Hilt and KSP. Show the plugin, its registration, and how a feature module uses it.</p>
    <pre class="code-block"><code class="language-kotlin">// build-logic/convention/build.gradle.kts
plugins {
    `kotlin-dsl`
}
dependencies {
    compileOnly(libs.android.gradlePlugin)
    compileOnly(libs.kotlin.gradlePlugin)
    compileOnly(libs.ksp.gradlePlugin)
    compileOnly(libs.hilt.gradlePlugin)
}

// build-logic/convention/src/main/kotlin/AndroidLibraryConventionPlugin.kt
import com.android.build.gradle.LibraryExtension
import org.gradle.api.Plugin
import org.gradle.api.Project
import org.gradle.kotlin.dsl.configure

class AndroidLibraryConventionPlugin : Plugin&lt;Project&gt; {
    override fun apply(target: Project): Unit = with(target) {
        with(pluginManager) {
            apply("com.android.library")
            apply("org.jetbrains.kotlin.android")
        }

        extensions.configure&lt;LibraryExtension&gt; {
            compileSdk = 35
            defaultConfig { minSdk = 26 }
            compileOptions {
                sourceCompatibility = JavaVersion.VERSION_17
                targetCompatibility = JavaVersion.VERSION_17
            }
        }

        // Enforce Kotlin strict mode
        tasks.withType(org.jetbrains.kotlin.gradle.tasks.KotlinCompile::class.java) {
            kotlinOptions {
                jvmTarget = "17"
                allWarningsAsErrors = true
                freeCompilerArgs = freeCompilerArgs + listOf(
                    "-opt-in=kotlinx.coroutines.ExperimentalCoroutinesApi",
                    "-Xexplicit-api=strict" // All public APIs must have explicit types
                )
            }
        }
    }
}

// AndroidHiltConventionPlugin.kt
class AndroidHiltConventionPlugin : Plugin&lt;Project&gt; {
    override fun apply(target: Project): Unit = with(target) {
        with(pluginManager) {
            apply("com.google.devtools.ksp")
            apply("dagger.hilt.android.plugin")
        }
        dependencies.apply {
            add("implementation", "com.google.dagger:hilt-android:2.51.1")
            add("ksp", "com.google.dagger:hilt-compiler:2.51.1")
        }
    }
}

// build-logic/convention/src/main/kotlin/build.gradle.kts registration
gradlePlugin {
    plugins {
        register("androidLibrary") {
            id = "shopapp.android.library"
            implementationClass = "AndroidLibraryConventionPlugin"
        }
        register("androidHilt") {
            id = "shopapp.android.hilt"
            implementationClass = "AndroidHiltConventionPlugin"
        }
    }
}

// settings.gradle.kts — include build-logic
pluginManagement {
    includeBuild("build-logic")
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}

// feature/cart/build.gradle.kts — clean, minimal, standards enforced automatically
plugins {
    id("shopapp.android.library")  // compileSdk, minSdk, Java 17, Kotlin strict
    id("shopapp.android.hilt")     // Hilt + KSP auto-configured
}

dependencies {
    implementation(project(":core:network"))
    implementation(libs.compose.material3)
    testImplementation(libs.junit)
    testImplementation(libs.mockk)
}
// That's it! All 40+ lines of standard config are in the convention plugin.
</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="31" data-item="0"> ✅ Understood Why &amp; What</label>
    <label class="progress-check"><input type="checkbox" data-topic="31" data-item="1"> ✅ Can explain How it works internally</label>
    <label class="progress-check"><input type="checkbox" data-topic="31" data-item="2"> ✅ Reviewed Common Mistakes</label>
    <label class="progress-check"><input type="checkbox" data-topic="31" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="31" data-item="4"> ✅ Solved Coding Challenge</label>
  </div>
</section>

<!-- ==================== TOPIC 32: APP MODULARIZATION ==================== -->
<section class="topic-section" id="topic-32">
  <div class="topic-header">
    <div class="topic-header-icon">🏗️</div>
    <div class="topic-header-text">
      <h1>App Modularization</h1>
      <p class="topic-tagline">:core vs :feature vs :app modules, api/impl pattern, dynamic delivery, team scaling</p>
      <div class="category-badge-group">
        <span class="cat-pill">Modularization</span>
        <span class="cat-pill">Dynamic Features</span>
        <span class="cat-pill">Build Speed</span>
        <span class="cat-pill">Team Scaling</span>
        <span class="cat-pill">Gradle</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 32-1: Module Architecture -->
  <div class="subtopic" id="subtopic-32-1">
    <h2>Module Architecture: :core, :feature, :app &amp; the api/impl Pattern</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>A monolithic Android app with all code in a single module has a fatal scaling problem: <strong>every code change recompiles the entire codebase</strong>. Gradle can only parallelize across module boundaries — within a single module, compilation is sequential. For a 50-engineer team with 200K+ lines of code, a full clean build takes 20+ minutes. Modularization splits the codebase into independent modules that compile in parallel, cache independently, and are only rebuilt when changed. Beyond build speed, modularization enforces architectural boundaries (a :feature:cart module literally cannot import from :feature:catalog — enforced by Gradle), enables different teams to own different modules, and unlocks Play's Dynamic Delivery for on-demand feature downloads.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p>Multi-module architecture organizes code into Gradle modules with explicit dependency boundaries:</p>
      <ul>
        <li><strong>:app</strong>: The application module. Depends on all :feature modules. Contains Application class, main activity, navigation graph. Minimal logic.</li>
        <li><strong>:feature:X</strong>: Self-contained feature modules (cart, catalog, checkout, profile). Depend on :core modules but NOT on each other. Contain UI (Composables), ViewModels, and feature-specific logic.</li>
        <li><strong>:core:network</strong>: Retrofit setup, interceptors, auth, base API interfaces. Shared across all features.</li>
        <li><strong>:core:database</strong>: Room database definition, shared DAOs, entity mappers.</li>
        <li><strong>:core:ui</strong>: Shared Design System — common Composables, themes, typography, colors.</li>
        <li><strong>:core:domain</strong>: Pure Kotlin use cases and domain models. NO Android dependencies — fully unit testable on JVM.</li>
        <li><strong>:core:testing</strong>: Shared test utilities, fakes, test fixtures used across modules.</li>
      </ul>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// settings.gradle.kts — module declarations
include(
    ":app",
    ":core:network",
    ":core:database",
    ":core:domain",
    ":core:ui",
    ":core:testing",
    ":feature:catalog",
    ":feature:cart",
    ":feature:checkout",
    ":feature:profile",
    ":feature:auth"
)

// :core:domain/build.gradle.kts — pure Kotlin, no Android
plugins {
    id("shopapp.kotlin.library") // Custom plugin for pure-kotlin modules
}
dependencies {
    implementation(libs.kotlinx.coroutines.core)
    // NO android dependencies!
}

// :core:domain/src/main/kotlin/domain/usecase/GetProductsUseCase.kt
class GetProductsUseCase(private val productRepository: ProductRepository) {
    suspend operator fun invoke(categoryId: String): Result&lt;List&lt;Product&gt;&gt; = runCatching {
        productRepository.getProducts(categoryId)
            .filter { it.isAvailable }
            .sortedByDescending { it.rating }
    }
}

// :feature:catalog/build.gradle.kts — Android feature module
plugins {
    id("shopapp.android.feature") // Convention plugin: library + hilt + compose
}
dependencies {
    implementation(project(":core:network"))
    implementation(project(":core:database"))
    implementation(project(":core:domain"))
    implementation(project(":core:ui"))
    // Cannot depend on :feature:cart or :feature:checkout — enforced by module boundary!
}

// :app/build.gradle.kts — orchestrator
plugins { id("shopapp.android.application") }
dependencies {
    implementation(project(":feature:catalog"))
    implementation(project(":feature:cart"))
    implementation(project(":feature:checkout"))
    implementation(project(":feature:profile"))
    implementation(project(":feature:auth"))
    implementation(project(":core:ui")) // for Application-level theme
}

// Navigation between features uses ONLY string routes or sealed class — no direct imports
// :app/src/main/kotlin/navigation/AppNavHost.kt
@Composable
fun AppNavHost(navController: NavHostController) {
    NavHost(navController, startDestination = "catalog") {
        catalogNavGraph(navController)   // Extension function defined IN :feature:catalog
        cartNavGraph(navController)      // Extension function defined IN :feature:cart
        checkoutNavGraph(navController)
        profileNavGraph(navController)
        authNavGraph(navController)
    }
}
</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// The api/impl pattern — hiding implementation details
// :core:network-api/build.gradle.kts — interfaces only
plugins { id("shopapp.kotlin.library") }
// Only interfaces and data classes — no implementation

// :core:network-api/src/main/kotlin/network/api/ProductApi.kt
interface ProductApi {
    suspend fun getProducts(categoryId: String): List&lt;ProductDto&gt;
}

// :core:network-impl/build.gradle.kts — concrete implementation
plugins { id("shopapp.android.library"); id("shopapp.android.hilt") }
dependencies {
    api(project(":core:network-api"))   // Expose the interface
    implementation(libs.retrofit)
    implementation(libs.okhttp)
    // Retrofit, OkHttp are NOT leaked to consumers — they use implementation()
}

// :core:network-impl/src/main/kotlin/network/impl/RetrofitProductApi.kt
@Singleton
class RetrofitProductApi @Inject constructor(
    private val retrofit: Retrofit
) : ProductApi {
    private val service = retrofit.create(ProductApiService::class.java)
    override suspend fun getProducts(categoryId: String) =
        service.getProducts(categoryId)
}

// Dependency inversion via Hilt — features depend only on :network-api interface
// :feature:catalog uses ProductApi (interface), never RetrofitProductApi (impl)
@Module @InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides @Singleton
    fun provideProductApi(retrofit: Retrofit): ProductApi = RetrofitProductApi(retrofit)
}

// Dynamic Feature Module — Play Dynamic Delivery
// :feature:ar-try-on/build.gradle.kts (on-demand 50MB AR feature)
plugins { id("com.android.dynamic-feature") }
android {
    // Declared in AndroidManifest: dist:onDemand=true
}
dependencies {
    implementation(project(":app")) // Dynamic features depend on :app, not the other way!
}

// Requesting dynamic feature installation at runtime
val splitInstallManager = SplitInstallManagerFactory.create(context)
val request = SplitInstallRequest.newBuilder()
    .addModule("feature_ar_try_on")
    .build()
splitInstallManager.startInstall(request)
    .addOnSuccessListener { sessionId -> /* feature installed */ }
    .addOnFailureListener { exception -> /* handle error */ }
</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example — E-Commerce: Now In Android Style Module Graph</h3>
      <pre class="code-block"><code class="language-kotlin">/*
 Module dependency graph (arrows = depends on):

 :app
  ├── :feature:catalog   ─────┐
  ├── :feature:cart      ─────┤──▶ :core:domain
  ├── :feature:checkout  ─────┤──▶ :core:network (impl)
  ├── :feature:profile   ─────┤──▶ :core:database
  └── :feature:auth      ─────┤──▶ :core:ui
                               └──▶ :core:testing (testImplementation only)

  :core:network (impl) ──▶ :core:network-api (interfaces)
  :core:domain ─────────▶ :core:network-api (interfaces)

  Features NEVER depend on each other.
  :app is the ONLY module that knows all features exist.
*/

// :feature:checkout implements a cross-feature flow using events/callbacks
// Rather than importing :feature:cart directly, it uses a shared domain model

// :core:domain/src/main/kotlin/domain/model/CartItem.kt
data class CartItem(
    val productId: String,
    val quantity: Int,
    val price: Double
)

// Shared cart repository interface in :core:domain
interface CartRepository {
    fun getCartItems(): Flow&lt;List&lt;CartItem&gt;&gt;
    suspend fun addItem(productId: String, quantity: Int)
    suspend fun removeItem(productId: String)
    suspend fun clearCart()
}

// Both :feature:cart and :feature:checkout depend on CartRepository from :core:domain
// They never import from each other — communication via shared domain types only

// Build graph validation with a custom Gradle task
tasks.register("validateModuleGraph") {
    doLast {
        val forbiddenDeps = mapOf(
            ":feature:catalog" to listOf(":feature:cart", ":feature:checkout"),
            ":feature:cart" to listOf(":feature:catalog", ":feature:checkout"),
            ":core:domain" to listOf(":core:network", ":core:database")
        )
        forbiddenDeps.forEach { (module, forbidden) ->
            val project = project(module)
            project.configurations.getByName("implementation").dependencies
                .filterIsInstance&lt;ProjectDependency&gt;()
                .forEach { dep ->
                    check(dep.dependencyProject.path !in forbidden) {
                        "FORBIDDEN: $module depends on ${dep.dependencyProject.path}!"
                    }
                }
        }
        println("Module graph validation passed!")
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Feature modules depending on other feature modules:</strong> Creates tight coupling and defeats the purpose of modularization. — ✅ Fix: Communicate between features via :core:domain interfaces, shared events, or navigation-only (string routes).</li>
        <li>❌ <strong>Putting everything in :core:</strong> One giant :core module is as bad as a monolith. — ✅ Fix: Split :core into focused sub-modules (:core:network, :core:database, :core:ui, :core:domain) with clear responsibilities.</li>
        <li>❌ <strong>Using <code>api()</code> instead of <code>implementation()</code> in modules:</strong> Leaks internal dependencies to all consumers, bloating compile classpaths and causing cascading recompilation. — ✅ Fix: Use api/impl module split — only expose interfaces via <code>api()</code>, keep implementations hidden with <code>implementation()</code>.</li>
        <li>❌ <strong>Circular module dependencies:</strong> A → B → A causes Gradle configuration failure. — ✅ Fix: Extract the shared interface to a third module (:core) that both A and B depend on.</li>
        <li>❌ <strong>Modularizing too early:</strong> With &lt;5 engineers and &lt;50K lines, modularization overhead outweighs benefits. — ✅ Fix: Start modularizing when build times exceed 3 minutes or team grows beyond 5 engineers working on the same codebase.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Modularization is fundamentally about two things: <strong>build speed</strong> and <strong>architectural enforcement</strong>. On build speed: Gradle parallelizes across module boundaries, and with a good remote build cache, engineers only rebuild modules they've touched. On a 15-module app, my last team went from 18-minute full builds to 4-minute incremental builds. On architecture: Gradle module dependencies are the strongest possible architectural boundary — a feature module literally cannot compile if it tries to import from another feature. We follow the :app / :feature / :core layering from Google's Now In Android sample. Features communicate only through :core:domain interfaces — there are no direct feature-to-feature imports. This lets team A own :feature:catalog and team B own :feature:cart completely independently. For the largest features we don't need at startup, we use Play Dynamic Delivery — users download the AR try-on module on demand, keeping the base APK small and improving store conversion rates."</p>
      </div>
    </div>
  </div>

  <!-- Q&A Section -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What are the main benefits of app modularization?</div>
      <div class="qa-answer">
        <p><strong>1. Build speed:</strong> Gradle compiles modules in parallel. Only changed modules + their dependents are recompiled. With remote build cache, CI/CD skips building unchanged modules entirely. Real numbers: 10-module app can reduce incremental build time from 8 minutes to 1-2 minutes.</p>
        <p><strong>2. Architectural enforcement:</strong> Module boundaries are Gradle dependency constraints. A :feature:cart module that tries to <code>import com.example.catalog.CatalogViewModel</code> fails compilation unless cart explicitly depends on catalog — which you can prevent in your module graph rules.</p>
        <p><strong>3. Team scalability:</strong> Different teams own different modules. Team A merges to :feature:cart without touching :feature:catalog code. Reduces merge conflicts, enables parallel feature development.</p>
        <p><strong>4. Dynamic Delivery:</strong> Feature modules can be delivered on-demand via Play — base APK is smaller (better conversion), users download features only when needed.</p>
        <p><strong>5. Testability:</strong> Pure :core:domain modules with no Android dependencies can be unit tested on JVM in milliseconds — no emulator needed.</p>
        <p><strong>6. Code reuse:</strong> :core:ui design system, :core:network client shared across all features with a single implementation point.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q2</span>How do feature modules communicate with each other in a properly modularized app?</div>
      <div class="qa-answer">
        <p>Feature modules must NOT depend on each other. Communication happens through:</p>
        <p><strong>1. Shared domain models in :core:domain:</strong> Both :feature:cart and :feature:checkout use <code>CartItem</code>, <code>Product</code>, <code>Order</code> data classes defined in :core:domain. They share data through these common types, not through each other's classes.</p>
        <p><strong>2. Shared repository interfaces in :core:domain:</strong> <code>CartRepository</code> interface lives in :core:domain. Both features can use it. The implementation lives in :core:database (or another impl module). Dependency injection wires the implementation to the interface.</p>
        <p><strong>3. Navigation events with string routes:</strong> Features navigate to each other using string route constants. :feature:catalog triggers navigation to "cart" route without importing CartActivity or CartComposable. The :app NavHost handles routing.</p>
        <p><strong>4. Shared event bus in :core:domain:</strong> For cross-feature events (e.g., "item added to cart" notification to update badge), use a shared SharedFlow/EventBus defined in :core:domain.</p>
        <p>The key principle: only <em>abstractions</em> (interfaces, data classes, event types) live in :core. Implementations stay in :feature or :core:impl modules.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>Explain the api/impl module pattern. When would you use it and what problem does it solve?</div>
      <div class="qa-answer">
        <p>The <strong>api/impl module split</strong> solves the problem of exposing stable interfaces while hiding implementation details and their transitive dependencies.</p>
        <p><strong>Without the pattern:</strong> :core:network module depends on Retrofit, OkHttp, Gson. Using <code>api()</code> on these leaks them to all consumers. All feature modules accidentally get Retrofit on their compile classpath — even if they never use it. Any Retrofit version change forces recompilation of ALL modules.</p>
        <p><strong>With the pattern:</strong></p>
        <ul>
          <li><strong>:core:network-api</strong>: Contains ONLY interfaces (<code>ProductApi</code>, <code>UserApi</code>) and DTOs. Zero heavy dependencies. Compiles instantly.</li>
          <li><strong>:core:network-impl</strong>: Contains Retrofit/OkHttp implementation. Depends on :core:network-api with <code>api()</code> (exposes interface) and Retrofit with <code>implementation()</code> (hides Retrofit). Only :app depends on :core:network-impl.</li>
          <li><strong>Feature modules</strong>: Depend only on :core:network-api — tiny compile classpath, instant compilation. Never see Retrofit classes.</li>
        </ul>
        <p><strong>Result:</strong> Changing Retrofit version in :core:network-impl only forces recompilation of :core:network-impl and :app. All feature modules are unaffected because they only see the interface, not the implementation.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q4</span>What is Play Dynamic Delivery and how do dynamic feature modules work?</div>
      <div class="qa-answer">
        <p><strong>Play Dynamic Delivery</strong> lets you publish one <code>.aab</code> (Android App Bundle) that Google Play splits into multiple APKs. Users only download what their device needs:</p>
        <ul>
          <li><strong>Configuration splits:</strong> Automatic — Play delivers only the correct ABI, screen density, and language resources</li>
          <li><strong>Dynamic feature modules:</strong> Large optional features (AR, premium features, ML models) delivered on-demand</li>
        </ul>
        <p><strong>Dynamic feature module characteristics:</strong></p>
        <ul>
          <li>Declared as <code>com.android.dynamic-feature</code> plugin</li>
          <li>The module depends on <code>:app</code> (reverse of normal — app doesn't list it in dependencies)</li>
          <li>AndroidManifest declares <code>dist:onDemand="true"</code> or <code>dist:installTime="true"</code></li>
          <li>Code inside is NOT available to :app at compile time — must use reflection or service locator to access</li>
          <li>Delivered via <code>SplitInstallManager</code> API at runtime</li>
        </ul>
        <p><strong>Use cases:</strong></p>
        <ul>
          <li>AR try-on feature (50MB model): Download only when user clicks "Try On"</li>
          <li>Premium features: Download when user upgrades subscription</li>
          <li>Seldom-used tools: Download on first use</li>
        </ul>
        <p>Result: Base APK stays small (&lt;10MB), improving Play Store conversion. Users get features when they need them.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q5</span>How would you migrate an existing monolithic Android app to a multi-module architecture without breaking production?</div>
      <div class="qa-answer">
        <p><strong>Strangler Fig migration strategy — incremental, never a "big bang":</strong></p>
        <p><strong>Phase 1 — Extract :core modules (Week 1-2):</strong></p>
        <ol>
          <li>Create :core:domain with all data models and repository interfaces (pure Kotlin)</li>
          <li>Move network layer to :core:network — Retrofit setup, interceptors, API interfaces</li>
          <li>Move database to :core:database — Room DB, DAOs, entities</li>
          <li>Move UI design system to :core:ui — colors, typography, shared composables</li>
          <li>App still works — all feature code remains in :app, just using :core modules</li>
        </ol>
        <p><strong>Phase 2 — Extract feature modules one at a time (Week 3-8):</strong></p>
        <ol>
          <li>Start with the most self-contained feature (e.g., :feature:profile)</li>
          <li>Move UI, ViewModel, and any feature-local code to the new module</li>
          <li>Wire navigation in :app NavHost</li>
          <li>Run full test suite — verify nothing broke</li>
          <li>Repeat for each feature, prioritizing high-churn features for maximum build speed benefit</li>
        </ol>
        <p><strong>Phase 3 — Enable parallelism and caching:</strong> Once modules are extracted, enable <code>org.gradle.parallel=true</code>, set up remote build cache. Measure build time improvement.</p>
        <p><strong>Key guardrails:</strong> Never merge a migration PR that breaks tests. Use feature flags to keep half-migrated features from reaching users. Keep migration PRs small and reviewable.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>How does modularization help with team scaling at 50+ engineers?</div>
      <div class="qa-answer">
        <p><strong>Code ownership:</strong> Assign each feature module to a team. Team A owns :feature:catalog and :feature:search. Team B owns :feature:cart and :feature:checkout. They can develop, test, and release their features independently without stepping on each other's code. Module boundaries reduce merge conflicts by 70%+ in practice.</p>
        <p><strong>Parallel CI pipelines:</strong> When a PR only touches :feature:catalog, CI only needs to build and test :feature:catalog and its dependents — not the entire app. With a 15-module app, this can reduce CI from 15 minutes (full build) to 3 minutes (affected modules only). Use Gradle's <code>--configuration-cache</code> for further speedup.</p>
        <p><strong>Independent versioning:</strong> Core libraries (:core:network, :core:ui) can be versioned and published to a Maven repository. Feature teams consume specific stable versions — no surprise breakages from other teams' changes.</p>
        <p><strong>Hiring and onboarding:</strong> New engineers can focus on understanding their team's 2-3 modules without needing to understand the full 200K-line codebase. Module README files document the public API and responsibilities of each module.</p>
        <p><strong>Contract testing:</strong> Interfaces in :core:domain are contracts between teams. Changes to interfaces require cross-team coordination (interface change = breaking change for consumers). This creates healthy friction that prevents hasty API changes.</p>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge</h3>
    <p><strong>Problem:</strong> Design the complete module structure for a FinTech app with these features: authentication, account dashboard, fund transfer, investment portfolio, and settings. Show the dependency graph, a sample build.gradle.kts for each module type, and explain how the Transfer feature can access Account data without directly importing the Account feature module.</p>
    <pre class="code-block"><code class="language-kotlin">/*
 FinTech App Module Structure:

 :app
  ├── :feature:auth
  ├── :feature:dashboard
  ├── :feature:transfer
  ├── :feature:investments
  └── :feature:settings
        All features ──▶ :core:domain
                   ──▶ :core:ui
                   ──▶ :core:network-api

 :core:domain (pure Kotlin — no Android)
 :core:network-api (interfaces only)
 :core:network-impl ──▶ :core:network-api
 :core:database ──▶ :core:domain
 :core:ui (Compose design system)
 :core:testing (shared test fakes)

 :app ──▶ :core:network-impl  (wires the implementation)
      ──▶ :core:database       (wires the Room DB)
*/

// :core:domain — Account and Transfer contracts
// AccountRepository.kt
interface AccountRepository {
    fun getAccounts(): Flow&lt;List&lt;BankAccount&gt;&gt;
    suspend fun getAccount(accountId: String): BankAccount
    suspend fun getBalance(accountId: String): Money
}

// TransferRepository.kt
interface TransferRepository {
    suspend fun initiateTransfer(request: TransferRequest): Result&lt;TransactionReceipt&gt;
    fun getTransferHistory(accountId: String): Flow&lt;List&lt;TransactionReceipt&gt;&gt;
}

// Shared domain models
data class BankAccount(val id: String, val iban: String, val alias: String, val balance: Money)
data class Money(val amount: BigDecimal, val currency: Currency)
data class TransferRequest(
    val sourceAccountId: String,
    val destinationIban: String,
    val amount: Money,
    val reference: String
)

// :feature:transfer — can access account data via domain interface!
// No import of :feature:dashboard needed!
@HiltViewModel
class TransferViewModel @Inject constructor(
    private val accountRepository: AccountRepository,  // From :core:domain
    private val transferRepository: TransferRepository, // From :core:domain
    private val getExchangeRateUseCase: GetExchangeRateUseCase // From :core:domain
) : ViewModel() {

    val sourceAccounts: StateFlow&lt;List&lt;BankAccount&gt;&gt; = accountRepository.getAccounts()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    private val _transferState = MutableStateFlow&lt;TransferState&gt;(TransferState.Idle)
    val transferState = _transferState.asStateFlow()

    fun submitTransfer(sourceId: String, destIban: String, amount: Money, ref: String) {
        viewModelScope.launch {
            _transferState.value = TransferState.Loading
            val request = TransferRequest(sourceId, destIban, amount, ref)
            val result = transferRepository.initiateTransfer(request)
            _transferState.value = result.fold(
                onSuccess = { receipt -> TransferState.Success(receipt) },
                onFailure = { error -> TransferState.Error(error.message ?: "Transfer failed") }
            )
        }
    }
}

// :core:database — implements both repositories
@Singleton
class RoomAccountRepository @Inject constructor(
    private val accountDao: AccountDao,
    private val api: BankingApi
) : AccountRepository {
    override fun getAccounts(): Flow&lt;List&lt;BankAccount&gt;&gt; =
        accountDao.getAllAccounts().map { entities -> entities.map { it.toDomain() } }

    override suspend fun getAccount(accountId: String): BankAccount =
        accountDao.getAccount(accountId).toDomain()

    override suspend fun getBalance(accountId: String): Money =
        api.getBalance(accountId).toDomain()
}

// :app/src/main/kotlin/di/RepositoryModule.kt — wire impl to interfaces
@Module @InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds @Singleton
    abstract fun bindAccountRepository(impl: RoomAccountRepository): AccountRepository

    @Binds @Singleton
    abstract fun bindTransferRepository(impl: ApiTransferRepository): TransferRepository
}

// :feature:transfer/build.gradle.kts — minimal, clean
plugins {
    id("fintech.android.feature")  // Convention plugin
    id("fintech.android.hilt")
}
dependencies {
    implementation(project(":core:domain"))   // AccountRepository + TransferRepository interfaces
    implementation(project(":core:ui"))       // Shared design system
    // NOT :feature:dashboard — never!
    // NOT :core:database — implementation detail hidden behind interface
}
</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="32" data-item="0"> ✅ Understood Why &amp; What</label>
    <label class="progress-check"><input type="checkbox" data-topic="32" data-item="1"> ✅ Can explain How it works internally</label>
    <label class="progress-check"><input type="checkbox" data-topic="32" data-item="2"> ✅ Reviewed Common Mistakes</label>
    <label class="progress-check"><input type="checkbox" data-topic="32" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="32" data-item="4"> ✅ Solved Coding Challenge</label>
  </div>
</section>
'''
