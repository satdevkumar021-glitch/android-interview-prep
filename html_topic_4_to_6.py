# Generator for Topics 4, 5, 6

def get_topics_4_to_6_html():
    return """
    <!-- ============================================= -->
    <!-- TOPIC 4: JETPACK COMPOSE RUNTIME & INTERNALS   -->
    <!-- ============================================= -->
    <section class="topic-section" id="topic-4">
      <div class="topic-header">
        <span class="topic-number">04</span>
        <h1>Jetpack Compose Runtime & Internals</h1>
        <p class="topic-desc">Slot Tables, compiler $changed bitmask, stability system (@Immutable/@Stable), recomposition storm diagnosis, derivedStateOf, and SideEffects.</p>
        <div class="topic-tags">
          <span class="tag tag-compose">Compose</span>
          <span class="tag tag-performance">Recomposition</span>
          <span class="tag tag-architecture">Senior / Staff</span>
        </div>
      </div>

      <!-- Subtopic 4.1 -->
      <div class="subtopic" id="subtopic-4-1">
        <h2>4.1 The Compose Recomposition Engine & Stability Rules</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p>Compose replaces Android's legacy View tree with an in-memory <strong>Slot Table</strong>. When state changes, the Compose runtime determines which Composables read that state and executes <strong>Recomposition</strong>. The Compose compiler plugin analyzes function parameters at build-time and tags them as <strong>Stable</strong> or <strong>Unstable</strong>. If all parameters of a Composable are stable, the function is marked <strong>skippable</strong>.</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> If an unstable type (such as <code>java.util.List</code>, any class with <code>var</code> properties, or a third-party DTO) is passed into a Composable, the runtime cannot guarantee immutability. As a result, it refuses to skip the composable, forcing full recomposition of that subtree on every single state change—causing massive frame drops and UI jank.</p>
          <ul>
            <li><strong>Recomposition Skipping:</strong> Allows unchanged UI subtrees to bypass execution entirely in a single CPU cycle.</li>
            <li><strong>Compiler Reports:</strong> Enables auditing stability metrics via Gradle flags (<code>reportsDestination</code> and <code>metricsDestination</code>).</li>
            <li><strong>Stable Collections:</strong> Using <code>ImmutableList&lt;T&gt;</code> guarantees Compose will skip list items during scroll.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>// ❌ UNSTABLE: List is an interface, Compose treats it as unstable by default
data class AccountListState(
    val accounts: List<Account>, // Causes AccountList to re-evaluate on every parent frame!
    val totalBalance: Double
)

// ✅ STABLE: Guarantees skipping optimization
@Immutable
data class AccountListUiState(
    val accounts: ImmutableList<Account>, // Fully stable!
    val totalBalance: Double
)

@Composable
fun AccountList(
    state: AccountListUiState,
    onAccountClick: (String) -> Unit, // Stable lambda reference
    modifier: Modifier = Modifier
) {
    LazyColumn(modifier = modifier) {
        items(
            items = state.accounts,
            key = { account -> account.id }, // Stable identity: prevents row rebuilding on list updates
            contentType = { "account_row" }  // Enables item slot reuse in the slot table
        ) { account ->
            AccountRow(account = account, onClick = onAccountClick)
        }
    }
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>FinTech Ticker & Banking Feeds:</strong> In a high-frequency banking dashboard displaying 10+ accounts with live balance updates arriving via WebSockets, unstable UI models caused the entire screen to recompose 60 times a second (a recomposition storm). Refactoring lists to <code>ImmutableList</code> and adding <code>@Immutable</code> annotations dropped recompositions by 92%, restoring a smooth 120Hz refresh rate.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "When explaining Compose performance, I dive straight into the compiler plugin. The compiler injects a synthetic <code>Composer</code> and a <code>$changed</code> bitmask into every composable. If arguments are stable and equality checks pass, the Composer executes <code>skipToGroupEnd()</code>, skipping the body entirely. I explain that standard <code>List&lt;T&gt;</code> is an interface that can be backed by a mutable <code>ArrayList</code>, so Compose treats it as unstable. To fix this in enterprise code, I enforce <code>ImmutableList</code> from kotlinx-collections-immutable and generate compiler metric reports in our CI pipeline."
          </div>
        </div>
      </div>

      <!-- Subtopic 4.2 -->
      <div class="subtopic" id="subtopic-4-2">
        <h2>4.2 derivedStateOf vs remember(key) High-Frequency Dampening</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p><code>remember(key) { ... }</code> recalculates its block whenever the <code>key</code> reference changes. <code>derivedStateOf { ... }</code> creates an observable state object that only notifies observers when its <strong>computed result</strong> actually changes, regardless of how frequently the underlying state dependencies mutate.</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> Reading rapidly changing state (like <code>listState.firstVisibleItemIndex</code> or raw scroll pixel offsets) inside a Composable triggers recomposition on <strong>every single pixel of scroll</strong>. <code>derivedStateOf</code> acts as a high-frequency dampener.</p>
          <ul>
            <li><strong>Dampens High-Frequency Inputs:</strong> Input state changes 1,000 times (pixels scrolled), but output state only changes twice (e.g. <code>showButton = true / false</code>).</li>
            <li><strong>Eliminates Scroll Jank:</strong> Prevents main thread frame overruns on 90Hz/120Hz displays.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>val listState = rememberLazyListState()

// ❌ ANTI-PATTERN: Recomposes the parent composable on every single scroll pixel!
// val showScrollToTop = listState.firstVisibleItemIndex > 0

// ✅ SENIOR PATTERN: derivedStateOf dampens 1000s of scroll emissions down to boolean changes
val showScrollToTop by remember {
    derivedStateOf { listState.firstVisibleItemIndex > 0 }
}

AnimatedVisibility(visible = showScrollToTop) {
    ScrollToTopFAB(onClick = { coroutineScope.launch { listState.animateScrollToItem(0) } })
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>E-Commerce Infinite Catalog:</strong> In an e-commerce product feed with 5,000 items, calculating dynamic sticky category headers and collapsing search bars using raw scroll listeners caused dropped frames on mid-range Android devices. Wrapping threshold calculations in <code>derivedStateOf</code> reduced recompositions during scrolling from 850 down to just 4.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "I use a simple rule of thumb for interviewers: use <code>derivedStateOf</code> when your inputs change MORE frequently than your output. For example, scrolling a list triggers hundreds of index updates per second, but a 'Scroll-to-Top' button only cares when <code>firstVisibleItemIndex > 0</code> flips between true and false. <code>derivedStateOf</code> acts as an observable dampener, notifying the snapshot system only when the calculated boolean transitions."
          </div>
        </div>
      </div>

      <!-- Subtopic 4.3 -->
      <div class="subtopic" id="subtopic-4-3">
        <h2>4.3 SideEffects Lifecycle Decision Tree</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p>SideEffects are lifecycle-safe escape hatches for executing non-composable operations outside the Composable tree: <code>LaunchedEffect</code> (coroutine linked to keys), <code>rememberCoroutineScope</code> (user event coroutine), <code>DisposableEffect</code> (cleanup/teardown), <code>SideEffect</code> (sync Compose state to external objects), and <code>produceState</code> (bridge callbacks into Compose State).</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> Running asynchronous work, registering sensor listeners, or triggering network calls directly inside the body of a Composable causes severe bugs: Composables can execute on any thread, execute out of order, or be discarded and recomposed multiple times in a single frame.</p>
          <ul>
            <li><strong>Deterministic Lifecycle Binding:</strong> SideEffects ensure code executes at predictable points in the composition lifecycle.</li>
            <li><strong>Guaranteed Cleanup:</strong> <code>DisposableEffect.onDispose</code> prevents hardware sensor, broadcast receiver, and camera resource leaks.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>@Composable
fun BiometricAuthScreen(
    onSuccess: () -> Unit,
    viewModel: AuthViewModel = hiltViewModel()
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope() // 1. For user click events

    // 2. DisposableEffect: Register & guaranteed teardown of broadcast listeners
    DisposableEffect(context) {
        val receiver = BiometricEnrollmentReceiver()
        context.registerReceiver(receiver, IntentFilter("ACTION_BIOMETRICS_CHANGED"))

        onDispose {
            context.unregisterReceiver(receiver) // Guaranteed cleanup on leaving composition
        }
    }

    // 3. LaunchedEffect: Key-driven trigger on state transition
    val authError by viewModel.authError.collectAsStateWithLifecycle()
    LaunchedEffect(authError) {
        authError?.let { err ->
            showHapticError(context)
            snackbarHostState.showSnackbar(err.localizedMessage)
        }
    }

    Button(onClick = {
        // User action: Launch coroutine via rememberCoroutineScope
        coroutineScope.launch {
            viewModel.authenticate()
        }
    }) {
        Text("Authenticate Biometrics")
    }
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>Healthcare QR Code Patient Scanner:</strong> CameraX barcode scanners require strict camera lifecycle binding. Initializing the camera in a <code>DisposableEffect</code> ensures that when the physician navigates away from the scanning tab, the camera hardware is immediately released in <code>onDispose</code>, preventing camera daemon battery locks.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "I articulate the SideEffect decision tree: (1) Is the task triggered by a Composable entering the composition or a key changing? Use <code>LaunchedEffect</code>. (2) Is it triggered by a user action like a button tap? Use <code>rememberCoroutineScope</code>. (3) Does it need cleanup (like unregistering a sensor or callback)? Use <code>DisposableEffect</code> with <code>onDispose</code>. (4) Do you need to push Compose state into an external non-Compose object on every successful composition? Use <code>SideEffect</code>."
          </div>
        </div>
      </div>

      <!-- Q&A Section -->
      <div class="qa-section">
        <h2>🎯 Senior/Lead Interview Q&A (Jetpack Compose Internals)</h2>

        <div class="qa-item" data-difficulty="basic">
          <div class="qa-question">
            <span class="qa-number">Q1</span>
            <span class="badge badge-basic">Basic</span>
            <p>What is the difference between remember and rememberSaveable?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> <code>remember</code> caches an object in the Slot Table across recompositions, but the value is destroyed during Activity configuration changes (rotation) and OS Process Death. <code>rememberSaveable</code> survives configuration changes and OS process death by serializing the value into the Activity's <code>savedInstanceState</code> Bundle. For custom types, <code>rememberSaveable</code> requires a custom <code>Saver</code> or <code>@Parcelize</code>.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="advanced">
          <div class="qa-question">
            <span class="qa-number">Q2</span>
            <span class="badge badge-advanced">Advanced</span>
            <p>How does the Compose Compiler determine if a function is skippable? What is the $changed bitmask?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> The compiler generates a synthetic <code>$changed</code> integer parameter for every <code>@Composable</code> function. Each parameter occupies 3 bits in the bitmask (indicating static, same, or changed). At runtime, if all parameters are classified as <code>@Stable</code> or <code>@Immutable</code>, and the bitmask indicates none have changed since the last invocation, the <code>Composer</code> executes <code>skipToGroupEnd()</code>, jumping past the function body and saving execution time.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="advanced">
          <div class="qa-question">
            <span class="qa-number">Q3</span>
            <span class="badge badge-advanced">Advanced</span>
            <p>What causes a 'Recomposition Storm' in Compose and how do you diagnose it?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> A recomposition storm occurs when an unstable parameter (like <code>List&lt;T&gt;</code>) or an unstable lambda capture causes high-frequency re-evaluation of parent composables on every frame. Diagnose by: (1) Enabling Compose Layout Inspector with 'Show Recomposition Counts', (2) Running Gradle with compiler metrics (<code>-Pplugin:androidx.compose.compiler.plugins.kotlin:metricsDestination</code>) to inspect <code>unstable_classes.txt</code>, and (3) Auditing for state reads occurring too high in the Composable tree.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="scenario">
          <div class="qa-number">Q4</div>
          <div class="qa-question">
            <span class="badge badge-scenario">Scenario</span>
            <p>Why is passing a raw lambda like 'onClick = { viewModel.doSomething() }' potentially unstable, and how do you fix it?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> When you write <code>onClick = { viewModel.doAction() }</code>, Compose creates a new lambda instance on every recomposition. If the lambda captures unstable local variables, the compiler cannot verify its equality, disabling skipping on the child Composable. Fix by: (1) Method reference: <code>onClick = viewModel::doAction</code>, (2) Caching with <code>remember(viewModel) { { viewModel.doAction() } }</code>, or (3) Passing stable hoisted action intents.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="scenario">
          <div class="qa-number">Q5</div>
          <div class="qa-question">
            <span class="badge badge-scenario">Scenario</span>
            <p>Compare staticCompositionLocalOf and compositionLocalOf. When does staticCompositionLocalOf hurt performance?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> <code>compositionLocalOf</code> tracks reads: when its provided value changes, only composables that actually read that CompositionLocal are recomposed. <code>staticCompositionLocalOf</code> does NOT track reads: when its value changes, the <strong>ENTIRE SUBTREE</strong> below the provider is forcibly recomposed! Use <code>staticCompositionLocalOf</code> only for values that rarely change (like Theme palettes, Typography). Using it for frequently changing state (like user balance or current timestamp) causes massive full-tree recomposition storms.</p>
          </div>
        </div>
      </div>

      <!-- Checklist -->
      <div class="topic-progress-tracker">
        <h3>✅ Topic 4 Mastery Checklist</h3>
        <label class="progress-check"><input type="checkbox" data-topic="4" data-item="0"> Slot Table & Compose Compiler $changed bitmask</label>
        <label class="progress-check"><input type="checkbox" data-topic="4" data-item="1"> Stability System (@Immutable, @Stable, ImmutableList)</label>
        <label class="progress-check"><input type="checkbox" data-topic="4" data-item="2"> derivedStateOf vs remember(key) dampening</label>
        <label class="progress-check"><input type="checkbox" data-topic="4" data-item="3"> SideEffects Decision Tree (LaunchedEffect vs DisposableEffect)</label>
        <label class="progress-check"><input type="checkbox" data-topic="4" data-item="4"> Answered & Mastered all 5 Topic 4 Q&As</label>
      </div>
    </section>

    <!-- ============================================= -->
    <!-- TOPIC 5: JETPACK ARCHITECTURE & ROOM          -->
    <!-- ============================================= -->
    <section class="topic-section" id="topic-5">
      <div class="topic-header">
        <span class="topic-number">05</span>
        <h1>Jetpack Architecture: ViewModel, Room, StateFlow & Paging</h1>
        <p class="topic-desc">ViewModelStore retain mechanics, StateFlow vs SharedFlow vs Channels, Room relational schemas, safe migrations, DataStore encryption, and Paging 3.</p>
        <div class="topic-tags">
          <span class="tag tag-architecture">Room</span>
          <span class="tag tag-compose">StateFlow</span>
          <span class="tag tag-performance">Senior / Staff</span>
        </div>
      </div>

      <!-- Subtopic 5.1 -->
      <div class="subtopic" id="subtopic-5-1">
        <h2>5.1 StateFlow vs SharedFlow vs Channels vs LiveData (The Definitive Matrix)</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p>Four primary state and event propagation primitives exist in modern Android:
          <strong>StateFlow</strong> (hot state-holder with replay=1, conflation by equality), 
          <strong>SharedFlow</strong> (hot event bus with configurable replay and buffer capacities), 
          <strong>Channel</strong> (hot point-to-point unicast queue for single-consumer execution), and 
          <strong>LiveData</strong> (legacy lifecycle-aware observable tied to the Main Thread).</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> Emitting one-time navigation commands, payment toasts, or biometric prompts through StateFlow triggers the notorious <strong>'duplicate event on rotation' bug</strong> because StateFlow immediately replays its current value to any new collector upon activity recreation.</p>
          <ul>
            <li><strong>State vs Event Duality:</strong> State represents <em>What the screen IS</em> (Balance, Form Inputs). Events represent <em>What HAPPENED</em> (Navigate to Receipt, Show Toast).</li>
            <li><strong>Atomic State Updates:</strong> <code>StateFlow.update { ... }</code> uses an atomic Compare-And-Swap (CAS) loop, preventing race conditions when multiple background threads update state concurrently.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>// Production MVI ViewModel: Clean State & Event Separation
@HiltViewModel
class TransferViewModel @Inject constructor(
    private val executeTransferUseCase: ExecuteTransferUseCase
) : ViewModel() {

    // 1. STATE: StateFlow for durable UI rendering (replays on rotation)
    private val _uiState = MutableStateFlow<TransferUiState>(TransferUiState.Idle)
    val uiState: StateFlow<TransferUiState> = _uiState.asStateFlow()

    // 2. EVENTS: Channel for one-time side-effects (consumed exactly once)
    private val _effectChannel = Channel<TransferEffect>(Channel.BUFFERED)
    val effects: Flow<TransferEffect> = _effectChannel.receiveAsFlow()

    fun confirmTransfer(amount: Double, iban: String) {
        viewModelScope.launch {
            // update{} CAS ensures atomic thread-safe transition
            _uiState.update { TransferUiState.Processing }

            executeTransferUseCase(amount, iban)
                .onSuccess { receiptId ->
                    _uiState.update { TransferUiState.Success(receiptId) }
                    // Dispatched once: will never re-fire upon screen rotation!
                    _effectChannel.send(TransferEffect.NavigateToReceipt(receiptId))
                }
                .onFailure { error ->
                    _uiState.update { TransferUiState.Error(error.localizedMessage) }
                    _effectChannel.send(TransferEffect.ShowSnackbar("Transfer failed: ${error.message}"))
                }
        }
    }
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>FinTech Money Transfer:</strong> After completing a $5,000 transfer, the user rotates their device while reviewing the confirmation screen. If the navigation trigger was modeled in StateFlow, the Activity recreation would immediately re-collect the 'NavigateToReceipt' state, causing a duplicate navigation push or re-initiating the transfer. Modeling side-effects as a buffered Channel eliminates duplicate execution.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "I frame the distinction as <strong>State vs Event</strong>. State represents a durable snapshot of the UI—it must be retained and replayed upon configuration change, so StateFlow with <code>collectAsStateWithLifecycle</code> is the right tool. Events represent transient actions like showing a snackbar or navigating—they must be consumed once and never re-emitted on rotation. For events, I use a <code>Channel(Channel.BUFFERED)</code> exposed via <code>receiveAsFlow()</code>. I also explain that <code>_state.update { }</code> uses an atomic CAS loop, whereas <code>_state.value = ...</code> is subject to lost updates during concurrent writes."
          </div>
        </div>
      </div>

      <!-- Subtopic 5.2 -->
      <div class="subtopic" id="subtopic-5-2">
        <h2>5.2 Room Multi-Table Relational Schema & Safe Migrations</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p>Room is an SQLite object mapping layer that verifies SQL queries at compile-time. It models relationships via <code>@Embedded</code>, <code>@Relation</code> (1-to-many), and <code>@Junction</code> (many-to-many). Schema migrations are executed via explicit <code>Migration(startVersion, endVersion)</code> objects or declarative <code>AutoMigration</code> (Room 2.4+).</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> If an app updates its Room version without providing a valid migration path, Room throws a fatal <code>IllegalStateException: Room cannot verify data integrity</code>, causing the app to crash on launch for every updating user. Using <code>fallbackToDestructiveMigration()</code> drops all tables, wiping user data permanently.</p>
          <ul>
            <li><strong>Compile-Time SQL Verification:</strong> Typos in SQL queries or mismatched column types fail the build, preventing runtime SQLiteExceptions.</li>
            <li><strong>Reactive Query Streams:</strong> Returning <code>Flow&lt;List&lt;T&gt;&gt;</code> from DAOs automatically re-emits fresh data whenever the underlying SQLite tables change.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>// 1. Relational Entities with Foreign Keys and Indices
@Entity(tableName = "bank_accounts")
data class AccountEntity(
    @PrimaryKey val accountId: String,
    val iban: String,
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
    val timestamp: Long,
    val encryptedTag: String = ""
)

// 2. Safe Deterministic Migration 2 -> 3
val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("ALTER TABLE transactions ADD COLUMN encryptedTag TEXT NOT NULL DEFAULT ''")
        db.execSQL("CREATE INDEX IF NOT EXISTS index_transactions_timestamp ON transactions(timestamp)")
    }
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>Healthcare Offline Medical Records:</strong> In electronic medical record (EMR) apps used in remote hospitals, patient data, diagnosis logs, and medication histories are cached locally in Room. Automated CI tests using <code>MigrationTestHelper</code> test every migration step (1&rarr;2, 2&rarr;3, ..., 1&rarr;10) against historical exported schema JSONs to guarantee zero patient data loss across updates.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "I explain to interviewers that Room validates its schema on open by comparing the identity hash in <code>room_master_table</code> against the compiled schema hash. If the hashes mismatch and no migration is provided, Room crashes the app. In enterprise architectures, I enforce three non-negotiable rules: (1) Always enable <code>exportSchema = true</code> and commit the JSON files to git, (2) Never use <code>fallbackToDestructiveMigration()</code> in production releases, and (3) Validate every migration in CI using <code>MigrationTestHelper</code>."
          </div>
        </div>
      </div>

      <!-- Q&A Section -->
      <div class="qa-section">
        <h2>🎯 Senior/Lead Interview Q&A (Jetpack Architecture & Room)</h2>

        <div class="qa-item" data-difficulty="basic">
          <div class="qa-question">
            <span class="qa-number">Q1</span>
            <span class="badge badge-basic">Basic</span>
            <p>What is the difference between StateFlow.value = ... and StateFlow.update { ... }?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> <code>StateFlow.value = ...</code> performs a direct write. If multiple coroutines attempt read-modify-write operations concurrently (e.g. <code>_state.value = _state.value.copy(counter = _state.value.counter + 1)</code>), it is susceptible to race conditions and lost updates. <code>StateFlow.update { ... }</code> executes an atomic Compare-And-Swap (CAS) loop: it repeatedly attempts to update the value until it succeeds without thread interference, guaranteeing thread safety during concurrent state mutations.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="advanced">
          <div class="qa-question">
            <span class="qa-number">Q2</span>
            <span class="badge badge-advanced">Advanced</span>
            <p>How does Room handle reactive queries with Flow? How does it detect database table changes?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> When a DAO method returns a <code>Flow&lt;T&gt;</code>, Room registers an <code>InvalidationTracker.Observer</code> on the queried SQLite tables. When any insert, update, or delete transaction commits against those observed tables, SQLite triggers notify the InvalidationTracker on a background thread. Room then re-executes the DAO query and emits the newly fetched list as a fresh emission on the Flow.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="advanced">
          <div class="qa-question">
            <span class="qa-number">Q3</span>
            <span class="badge badge-advanced">Advanced</span>
            <p>What is Paging 3 RemoteMediator and how does it implement offline-first infinite scrolling?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> <code>RemoteMediator</code> acts as an intermediary between the network API and the local Room database. The UI observes PagingData strictly from Room (Single Source of Truth). When the local cache runs out of data (e.g. user reaches the end of the list), <code>RemoteMediator.load()</code> is triggered to fetch the next page from the network, write it into the Room database, and Room automatically updates the UI.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="scenario">
          <div class="qa-number">Q4</div>
          <div class="qa-question">
            <span class="badge badge-scenario">Scenario</span>
            <p>A Room migration fails on 5% of devices in production with an SQLiteConstraintException. How do you triage and fix it without data loss?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> <strong>Root Cause:</strong> An <code>ALTER TABLE ADD COLUMN ... NOT NULL</code> was executed without providing a default value, or existing rows contained nulls for a newly constrained unique column.\n\n<strong>Fix:</strong> Ship an emergency hotfix migration that checks PRAGMA table_info, creates a temporary staging table, copies valid data over, drops the old table, and renames the staging table. In CI, configure <code>MigrationTestHelper</code> to seed real dirty production SQLite dumps before running migrations.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="scenario">
          <div class="qa-number">Q5</div>
          <div class="qa-question">
            <span class="badge badge-scenario">Scenario</span>
            <p>Compare SharedPreferences vs Preferences DataStore vs Proto DataStore for enterprise apps.</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> SharedPreferences parses XML synchronously on the Main Thread (causing ANRs on <code>apply()</code>/<code>commit()</code>), provides no type safety, and throws runtime ClassCastExceptions. <code>Preferences DataStore</code> runs asynchronously on Dispatchers.IO using Kotlin Coroutines and Flow, preventing UI thread blocking. <code>Proto DataStore</code> is the gold standard for enterprise apps: it uses Protocol Buffers to define structured, strongly typed schemas with compile-time verification and native encryption support.</p>
          </div>
        </div>
      </div>

      <!-- Checklist -->
      <div class="topic-progress-tracker">
        <h3>✅ Topic 5 Mastery Checklist</h3>
        <label class="progress-check"><input type="checkbox" data-topic="5" data-item="0"> StateFlow vs SharedFlow vs Channels decision matrix</label>
        <label class="progress-check"><input type="checkbox" data-topic="5" data-item="1"> StateFlow.update atomic CAS loop</label>
        <label class="progress-check"><input type="checkbox" data-topic="5" data-item="2"> Room foreign keys, indices, and InvalidationTracker</label>
        <label class="progress-check"><input type="checkbox" data-topic="5" data-item="3"> Non-destructive migrations with MigrationTestHelper</label>
        <label class="progress-check"><input type="checkbox" data-topic="5" data-item="4"> Answered & Mastered all 5 Topic 5 Q&As</label>
      </div>
    </section>

    <!-- ============================================= -->
    <!-- TOPIC 6: NETWORKING & THIRD-PARTY LIBRARIES   -->
    <!-- ============================================= -->
    <section class="topic-section" id="topic-6">
      <div class="topic-header">
        <span class="topic-number">06</span>
        <h1>Networking & Third-Party Libraries (Retrofit, OkHttp, Coil)</h1>
        <p class="topic-desc">Thread-safe 401 token refresh with Mutex in Authenticator, offline HTTP caching with CacheControl, Coil vs Glide, and Moshi vs Kotlinx Serialization.</p>
        <div class="topic-tags">
          <span class="tag tag-architecture">Retrofit</span>
          <span class="tag tag-performance">OkHttp</span>
          <span class="tag tag-security">Senior / Staff</span>
        </div>
      </div>

      <!-- Subtopic 6.1 -->
      <div class="subtopic" id="subtopic-6-1">
        <h2>6.1 Thread-Safe 401 Token Refresh with OkHttp Authenticator & Mutex</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p>OkHttp's <code>Authenticator</code> interface handles HTTP 401 Unauthorized challenges by fetching a fresh access token and retrying the failed request. When multiple parallel requests (e.g. balance, transactions, notifications) fail with 401 simultaneously, a thread synchronization lock or Mutex is mandatory to prevent duplicate refresh calls.</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> Without synchronization, 5 parallel network calls trigger 5 concurrent token refresh requests. In OAuth 2.0 with Refresh Token Rotation, the first refresh succeeds and invalidates the refresh token; the remaining 4 calls fail with invalid grant errors, logging the user out abruptly.</p>
          <ul>
            <li><strong>Eliminates 401 Refresh Storms:</strong> Ensures exactly ONE network request refreshes the token, while other concurrent requests wait and reuse the fresh token.</li>
            <li><strong>Handles Refresh Token Expiry:</strong> Safely clears local credentials and navigates the user to the Login screen if the refresh token itself is expired.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>// Production Thread-Safe Token Refresh Authenticator
class TokenAuthenticator @Inject constructor(
    private val tokenStorage: TokenStorage,
    private val authApiProvider: Provider<AuthApiService> // Provider breaks circular Dagger dependency
) : Authenticator {

    private val refreshLock = Any()

    override fun authenticate(route: Route?, response: Response): Request? {
        // Prevent infinite loops if authentication fails repeatedly
        if (responseCount(response) >= 3) return null

        val currentAccessToken = tokenStorage.getAccessToken()

        synchronized(refreshLock) {
            val updatedAccessToken = tokenStorage.getAccessToken()

            // If another thread already refreshed the token while we waited, reuse it!
            val tokenToUse = if (updatedAccessToken != currentAccessToken && updatedAccessToken != null) {
                updatedAccessToken
            } else {
                val refreshToken = tokenStorage.getRefreshToken() ?: return null
                // Execute synchronous direct refresh call
                val refreshCall = authApiProvider.get().refreshTokenDirect(refreshToken).execute()

                if (refreshCall.isSuccessful && refreshCall.body() != null) {
                    val tokens = refreshCall.body()!!
                    tokenStorage.saveTokens(tokens.accessToken, tokens.refreshToken)
                    tokens.accessToken
                } else {
                    // Refresh token invalid or expired: force session termination
                    tokenStorage.clearTokens()
                    SessionBus.post(SessionExpiredEvent)
                    return null
                }
            }

            // Retry the original failed request with the new token
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
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>FinTech Mobile Banking:</strong> When a user resumes the app after their 15-minute access token expires, the dashboard immediately triggers 4 simultaneous calls (Balance, Transactions, Credit Score, Alerts). The synchronized Authenticator blocks 3 requests while the first refreshes the token, then replays all 4 seamlessly with zero user interruption.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "I walk through the 401 token refresh problem as a classic concurrency challenge. In modern OAuth systems with refresh token rotation, parallel 401 responses will invalidate each other if not serialized. In OkHttp, I use <code>Authenticator</code> with a synchronized block. Crucially, before executing the network refresh, I check if <code>tokenStorage.getAccessToken()</code> has ALREADY changed—meaning another thread finished refreshing while this thread was waiting on the lock. If so, I bypass the network call and immediately retry with the new token. I also check <code>response.priorResponse</code> count to prevent infinite retry loops."
          </div>
        </div>
      </div>

      <!-- Subtopic 6.2 -->
      <div class="subtopic" id="subtopic-6-2">
        <h2>6.2 Image Loading: Coil vs Glide & Custom Decoders</h2>

        <div class="card card-what">
          <h3>🔷 What is it?</h3>
          <p>Coil is an image loading library built specifically for Kotlin and Jetpack Compose. It uses Kotlin Coroutines, OkHttp, and Android's hardware Bitmaps. Glide is a mature, feature-rich Java library based on custom memory pools and annotation processing.</p>
        </div>

        <div class="card card-why">
          <h3>❓ Why do we use it & What problem does it solve?</h3>
          <p><strong>The Core Problem:</strong> Loading raw Bitmaps directly into ImageViews or Composables on the UI thread causes instant OutOfMemory (OOM) crashes and scroll jank due to high heap allocation and lack of bitmap downsampling.</p>
          <ul>
            <li><strong>Coil Advantages:</strong> Fast, lightweight (~2,000 methods vs Glide's ~8,000), 100% Kotlin-native, uses existing OkHttpClient, and provides native Compose integration via <code>AsyncImage</code>.</li>
            <li><strong>Memory Caching:</strong> Automatically calculates target view bounds and downsamples Bitmaps to exact pixel dimensions.</li>
          </ul>
        </div>

        <div class="card card-how">
          <h3>🛠️ How do we use it? (Step-by-Step Code)</h3>
          <div class="code-block" data-language="kotlin">
            <pre><code>// 1. Compose AsyncImage with Crossfade & Cache Policies
@Composable
fun MerchantAvatar(imageUrl: String?, modifier: Modifier = Modifier) {
    AsyncImage(
        model = ImageRequest.Builder(LocalContext.current)
            .data(imageUrl)
            .crossfade(300)
            .memoryCachePolicy(CachePolicy.ENABLED)
            .diskCachePolicy(CachePolicy.ENABLED)
            .error(R.drawable.ic_merchant_placeholder)
            .build(),
        contentDescription = "Merchant Logo",
        contentScale = ContentScale.Crop,
        modifier = modifier.size(48.dp).clip(CircleShape)
    )
}

// 2. Custom Decrypting Decoder for Encrypted Medical Records (Healthcare)
class EncryptedImageDecoder(
    private val source: ImageSource,
    private val options: Options
) : Decoder {
    override suspend fun decode(): DecodeResult {
        val encryptedBytes = source.source().readByteArray()
        val decryptedBytes = AesGcmCipher.decrypt(encryptedBytes)
        val bitmap = BitmapFactory.decodeByteArray(decryptedBytes, 0, decryptedBytes.size)
        return DecodeResult(drawable = bitmap.toDrawable(options.context.resources), isSampled = false)
    }
}</code></pre>
          </div>
        </div>

        <div class="card card-realworld">
          <h3>🏭 Real-World Production Architecture</h3>
          <p><strong>Healthcare Patient EMR:</strong> Patient wound photographs and diagnostic X-rays must be stored encrypted on disk to comply with HIPAA. A custom Coil <code>Decoder</code> transparently decrypts the byte stream in memory using Android Keystore keys before rendering into Composables, guaranteeing that unencrypted patient photos are never written to disk.</p>
        </div>

        <div class="card card-presenter">
          <h3>🎤 How to Present in an Interview (The Senior Pitch)</h3>
          <div class="pitch-quote">
            "I compare Coil and Glide from an architectural perspective: Coil is my default choice for modern Compose apps because it shares our existing OkHttp client and coroutine dispatchers, adding minimal method count and APK size. Glide remains the tool of choice for complex GIF/video frame decoding or legacy XML apps. In regulated apps, I leverage Coil's extensible pipeline (Interceptors, Fetchers, Decoders) to inject transparent decryption layers for secure local asset caching."
          </div>
        </div>
      </div>

      <!-- Q&A Section -->
      <div class="qa-section">
        <h2>🎯 Senior/Lead Interview Q&A (Networking & Third-Party)</h2>

        <div class="qa-item" data-difficulty="basic">
          <div class="qa-question">
            <span class="qa-number">Q1</span>
            <span class="badge badge-basic">Basic</span>
            <p>What is the difference between an Application Interceptor and a Network Interceptor in OkHttp?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> <strong>Application Interceptors</strong> (<code>addInterceptor</code>) run first and execute once per call, before the HTTP cache is checked and outside redirects/retries. This is where you attach global headers (Auth tokens, correlation IDs) and rewrite offline cache queries. <strong>Network Interceptors</strong> (<code>addNetworkInterceptor</code>) execute directly before the request hits the network wire and after the cache. They have visibility into TLS handshakes and redirects, but are NEVER called if the request is served directly from the OkHttp Cache.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="advanced">
          <div class="qa-question">
            <span class="qa-number">Q2</span>
            <span class="badge badge-advanced">Advanced</span>
            <p>How do you implement offline-first caching in OkHttp when the backend does not send cache headers?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> Configure a disk <code>Cache</code> (e.g. 50MB) on <code>OkHttpClient.Builder</code>. Install a Network Interceptor that intercepts incoming responses and overwrites the server's <code>Cache-Control</code> header with <code>public, max-age=60</code>. Add an Application Interceptor that checks network connectivity; if offline, it rewrites the request header to <code>Cache-Control: public, only-if-cached, max-stale=86400</code>, forcing OkHttp to return cached responses without hitting the network.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="advanced">
          <div class="qa-question">
            <span class="qa-number">Q3</span>
            <span class="badge badge-advanced">Advanced</span>
            <p>Compare Moshi vs Kotlinx Serialization vs Gson. Why is Gson discouraged in modern Kotlin?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> <strong>Gson</strong> relies on Java reflection and unsafe object allocation (<code>sun.misc.Unsafe</code>), bypassing Kotlin's constructor checks. This means if an API returns <code>null</code> for a non-nullable property (e.g. <code>val id: String</code>), Gson sets it to null anyway, causing NullPointerExceptions later! <strong>Moshi</strong> and <strong>Kotlinx Serialization</strong> respect Kotlin nullability, support sealed class polymorphism, and Kotlinx Serialization generates compiler code without reflection, making it significantly faster and R8-friendly.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="scenario">
          <div class="qa-number">Q4</div>
          <div class="qa-question">
            <span class="badge badge-scenario">Scenario</span>
            <p>How do you upload a 200MB video file with progress tracking in Retrofit without running Out of Memory?</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <p><strong>Senior Answer:</strong> Create a custom <code>RequestBody</code> that wraps an Okio <code>Source</code> or <code>FileInputStream</code>. In its <code>writeTo(sink: BufferedSink)</code> method, read the file in 8KB chunks and write directly to the socket sink, emitting progress percentages to a Flow or callback. Use Retrofit's <code>@Multipart</code> with <code>@Part</code>. Never read the file into a <code>ByteArray</code> in memory, which would trigger an immediate OOM crash.</p>
          </div>
        </div>

        <div class="qa-item" data-difficulty="scenario">
          <div class="qa-number">Q5</div>
          <div class="qa-question">
            <span class="badge badge-scenario">Scenario</span>
            <p>Design a dynamic CallAdapterFactory in Retrofit that wraps API responses into a sealed Result&lt;T&gt; type.</p>
            <span class="expand-icon">▼</span>
          </div>
          <div class="qa-answer">
            <div class="code-block" data-language="kotlin">
              <pre><code>// Custom CallAdapter wrapping Retrofit Calls into Result<T>
class ResultCallAdapter<R>(private val responseType: Type) : CallAdapter<R, Call<Result<R>>> {
    override fun responseType(): Type = responseType
    override fun adapt(call: Call<R>): Call<Result<R>> = ResultCall(call)
}

class ResultCall<T>(private val delegate: Call<T>) : Call<Result<T>> {
    override fun enqueue(callback: Callback<Result<T>>) {
        delegate.enqueue(object : Callback<T> {
            override fun onResponse(call: Call<T>, response: Response<T>) {
                val result = if (response.isSuccessful) {
                    Result.success(response.body()!!)
                } else {
                    Result.failure(HttpException(response))
                }
                callback.onResponse(this@ResultCall, Response.success(result))
            }
            override fun onFailure(call: Call<T>, t: Throwable) {
                callback.onResponse(this@ResultCall, Response.success(Result.failure(t)))
            }
        })
    }
    // delegate remaining Call interface methods...
}</code></pre>
            </div>
          </div>
        </div>
      </div>

      <!-- Checklist -->
      <div class="topic-progress-tracker">
        <h3>✅ Topic 6 Mastery Checklist</h3>
        <label class="progress-check"><input type="checkbox" data-topic="6" data-item="0"> Application vs Network Interceptors</label>
        <label class="progress-check"><input type="checkbox" data-topic="6" data-item="1"> Thread-safe 401 token refresh in OkHttp Authenticator</label>
        <label class="progress-check"><input type="checkbox" data-topic="6" data-item="2"> Offline HTTP caching with CacheControl</label>
        <label class="progress-check"><input type="checkbox" data-topic="6" data-item="3"> Coil vs Glide image decoding pipelines</label>
        <label class="progress-check"><input type="checkbox" data-topic="6" data-item="4"> Answered & Mastered all 5 Topic 6 Q&As</label>
      </div>
    </section>
    """

if __name__ == '__main__':
    print("html_topic_4_to_6 loaded successfully.")
