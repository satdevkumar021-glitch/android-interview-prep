
def get_topics_13_to_17_html():
    return '''
<!-- ============================================================ -->
<!--  TOPIC 13: Android Fundamentals                              -->
<!-- ============================================================ -->
<section class="topic-section" id="topic-13">
  <div class="topic-header">
    <div class="topic-header-icon">📱</div>
    <div class="topic-header-text">
      <h1>Android Fundamentals</h1>
      <p class="topic-tagline">Activity &amp; Fragment lifecycle, Intents, Back Stack — the bedrock every senior Android engineer must own</p>
      <div class="category-badge-group">
        <span class="cat-pill">Activity</span>
        <span class="cat-pill">Fragment</span>
        <span class="cat-pill">Intent</span>
        <span class="cat-pill">Back Stack</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 13-1: Activity Lifecycle -->
  <div class="subtopic" id="subtopic-13-1">
    <h2>Activity Lifecycle &amp; Back Stack</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Android runs on resource-constrained devices. The OS can kill your app process at any moment — a phone call comes in, the user rotates the screen, or RAM runs low. Without a well-defined lifecycle, your app would leak memory (holding a reference to a destroyed Activity), crash on rotation (trying to update a view that no longer exists), or lose user data silently. The Activity lifecycle is Android's contract between your code and the OS: it tells you exactly when to save state, release resources, and resume work.</p>
      <p>Concretely: if you start a video stream in <code>onStart()</code> but never stop it in <code>onStop()</code>, you drain the battery even when the user navigates away. If you register a BroadcastReceiver in <code>onCreate()</code> but forget to unregister in <code>onDestroy()</code>, you get a memory leak that accumulates across every rotation.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p>The <strong>Activity Lifecycle</strong> is a state machine managed by the Android framework (ActivityManagerService, running in system_server). Each Activity instance transitions through a fixed set of states:</p>
      <ul>
        <li><strong>onCreate</strong> — Activity created; do one-time initialization (inflate layout, bind ViewModel).</li>
        <li><strong>onStart</strong> — Activity becoming visible; register lightweight observers.</li>
        <li><strong>onResume</strong> — Activity in foreground; start animations, open camera, begin real-time updates.</li>
        <li><strong>onPause</strong> — Another Activity partially covers this one; commit unsaved changes, stop heavy work. Must be FAST (&lt;500ms) or the new Activity is delayed.</li>
        <li><strong>onStop</strong> — Activity fully hidden; release expensive resources (video, sensors).</li>
        <li><strong>onDestroy</strong> — Activity being destroyed (finish() called or OS killing for memory).</li>
        <li><strong>onSaveInstanceState / onRestoreInstanceState</strong> — Framework-managed state preservation across process death.</li>
      </ul>
      <p>The <strong>Back Stack</strong> is a LIFO stack maintained per Task. Each call to <code>startActivity()</code> pushes a new Activity on top; pressing Back pops it. Tasks are isolated — the Instagram camera task has its own back stack separate from the email task.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <p>When you call <code>startActivity(intent)</code>, ActivityManagerService in system_server resolves the target Activity, creates a new ActivityRecord, pushes it onto the appropriate TaskRecord back stack, then sends an IPC (Binder) transaction to your app process telling it to launch. Your app's ActivityThread receives this via its Handler, instantiates the Activity, and calls the lifecycle methods in order.</p>
      <p>On rotation, the OS calls <code>onSaveInstanceState(bundle)</code> before destroying the Activity — you store lightweight state (selected tab, scroll position) in the Bundle. The new Activity instance receives this Bundle in <code>onCreate(savedInstanceState)</code>. Heavy state (network data, large bitmaps) should be held in a <code>ViewModel</code>, which survives configuration changes because it is stored in the ViewModelStore attached to the non-UI fragment retained across rotations.</p>
      <pre class="code-block"><code class="language-kotlin">class PaymentActivity : AppCompatActivity() {

    private lateinit var viewModel: PaymentViewModel
    private lateinit var binding: ActivityPaymentBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPaymentBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // ViewModel survives rotation — no need to re-fetch data
        viewModel = ViewModelProvider(this)[PaymentViewModel::class.java]

        // Restore lightweight UI state (e.g., selected payment method index)
        val selectedIndex = savedInstanceState?.getInt(KEY_SELECTED_METHOD) ?: 0
        binding.paymentMethodGroup.check(binding.paymentMethodGroup.getChildAt(selectedIndex).id)

        viewModel.paymentState.observe(this) { state ->
            when (state) {
                is PaymentState.Loading -> binding.progressBar.isVisible = true
                is PaymentState.Success -> navigateToReceipt(state.transactionId)
                is PaymentState.Error   -> showError(state.message)
            }
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Only lightweight UI state here — ViewModel holds the real data
        outState.putInt(KEY_SELECTED_METHOD, getSelectedMethodIndex())
    }

    override fun onStop() {
        super.onStop()
        // Release camera / heavy resources here, not onPause
        releaseNfcReader()
    }

    override fun onDestroy() {
        super.onDestroy()
        // ViewModel.onCleared() called automatically — no manual cleanup needed
    }

    companion object {
        private const val KEY_SELECTED_METHOD = "selected_payment_method"
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// Launch modes — set in AndroidManifest or via Intent flags
// standard     : new instance every time (default)
// singleTop    : reuse if already on top of stack (deep links)
// singleTask   : one instance per task; clears top on relaunch (main activity)
// singleInstance: own task, no other activities (custom launcher)

// Programmatic equivalent using Intent flags:
val intent = Intent(this, DashboardActivity::class.java).apply {
    flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
}
startActivity(intent)

// Result API (replaces deprecated startActivityForResult):
val pickMedia = registerForActivityResult(ActivityResultContracts.PickVisualMedia()) { uri ->
    uri?.let { binding.avatarImage.setImageURI(it) }
}
pickMedia.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly))

// Process death simulation (test this in production!):
// adb shell am kill <package-name>
// Then navigate back — onSaveInstanceState bundle is restored

// Task affinity — group activities into the same task:
// android:taskAffinity=".FinancialTask" in manifest
// Combine with FLAG_ACTIVITY_NEW_TASK to force new task</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example</h3>
      <p><strong>FinTech — OTP Verification Flow:</strong> When a payment OTP screen is shown, the user must not be able to go back to the payment amount entry screen (security requirement). We use <code>FLAG_ACTIVITY_NO_HISTORY</code> on the amount screen and ensure the OTP screen is <code>singleTop</code> so hardware back kills the flow entirely rather than leaking sensitive data.</p>
      <pre class="code-block"><code class="language-kotlin">// PaymentAmountActivity.kt
fun proceedToOtp(amount: BigDecimal) {
    val intent = Intent(this, OtpVerificationActivity::class.java).apply {
        putExtra(EXTRA_AMOUNT, amount.toPlainString())
        // This activity won't appear in back stack — security requirement
        addFlags(Intent.FLAG_ACTIVITY_NO_HISTORY)
    }
    startActivity(intent)
}

// OtpVerificationActivity.kt — declared singleTop in manifest
// android:launchMode="singleTop"
override fun onNewIntent(intent: Intent) {
    super.onNewIntent(intent)
    // Handle deep-link retry from push notification without creating new instance
    handleOtpDeepLink(intent)
}

// After successful OTP, clear back stack so user cannot press Back to OTP screen
fun onOtpVerified(transactionId: String) {
    val intent = Intent(this, ReceiptActivity::class.java).apply {
        putExtra(EXTRA_TRANSACTION_ID, transactionId)
        flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
    }
    startActivity(intent)
    finish()
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Heavy work in onPause:</strong> Writing to database, making network calls in onPause blocks the incoming Activity from appearing — ✅ Fix: Use onStop for cleanup, or dispatch background coroutines with lifecycleScope.</li>
        <li>❌ <strong>Storing large objects in Bundle:</strong> Bitmaps, lists of 1000 items in onSaveInstanceState causes TransactionTooLargeException — ✅ Fix: Store in ViewModel; only store primitive keys (IDs) in Bundle.</li>
        <li>❌ <strong>Calling finish() then startActivity():</strong> Wrong order — the new Activity may appear before the current one is fully cleaned up — ✅ Fix: startActivity() first, then finish().</li>
        <li>❌ <strong>Ignoring process death:</strong> Testing only rotation, not actual process kill — ✅ Fix: Always test with <code>adb shell am kill</code> + navigating back. Use the "Don't keep activities" developer option.</li>
        <li>❌ <strong>FLAG_ACTIVITY_CLEAR_TOP without SINGLE_TOP:</strong> Creates a new instance even if one exists on the stack — ✅ Fix: Always combine these two flags when you want to navigate up to an existing instance.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"The Activity lifecycle is essentially a state machine that lets Android reclaim resources from background apps while preserving user experience. In production, I treat lifecycle methods with clear responsibilities: onCreate for one-time DI and ViewModel binding, onStart/onStop for visibility-tied resources like location or camera, and onPause only for absolute minimums — saving a draft at most. For state, I follow the rule: ViewModels hold business/UI state across rotations, Bundles hold lightweight navigation keys for process-death restoration, and the repository holds the source of truth. On the back stack side, I leverage launch modes carefully — singleTask for the main activity to prevent multiple instances when the user taps the app icon, singleTop for notification deep links to avoid stacking identical screens, and FLAG_ACTIVITY_CLEAR_TASK after login/logout to reset the entire flow. I always test process death by enabling 'Don't keep activities' in developer settings before shipping."</p>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 13-2: Fragment Lifecycle & Intents -->
  <div class="subtopic" id="subtopic-13-2">
    <h2>Fragment Lifecycle &amp; Intent Types</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Fragments solve the reusability and modularity problem that Activities cannot. A single Activity can host multiple Fragments simultaneously (split-screen on tablets), swap them without full screen transitions, and share a single ViewModel between them. Without Fragments, you'd need dozens of Activities for every screen variant, making deep-linking, animation, and state sharing far more complex.</p>
      <p>Intents are the message-passing protocol of Android — they decouple callers from callees at the OS level. Without Intents, you'd have tight coupling between app components, making it impossible to open a PDF with the system viewer, share a photo to Instagram, or receive a payment deep link from another app.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p>A <strong>Fragment</strong> has its own lifecycle that is nested within and controlled by its host Activity. Key states unique to Fragment: <code>onAttach</code> (bound to Activity context), <code>onCreateView</code> (inflate layout), <code>onViewCreated</code> (safe to reference views), <code>onDestroyView</code> (clear view references to avoid leaks in back-stack fragments), <code>onDetach</code> (unbound from Activity). Critically: a Fragment on the back stack is <em>stopped</em> but not <em>destroyed</em> — its view IS destroyed, but the Fragment instance lives on.</p>
      <p><strong>Intent Types:</strong></p>
      <ul>
        <li><strong>Explicit Intent:</strong> Specifies exact component class — used for internal navigation within your app.</li>
        <li><strong>Implicit Intent:</strong> Specifies action + data + category — the OS finds the best-matching component across all apps. Enables inter-app communication.</li>
        <li><strong>Pending Intent:</strong> A future Intent wrapped with your app's permissions — given to the OS or another app to fire on your behalf (notifications, alarms, widgets).</li>
        <li><strong>Broadcast Intent:</strong> Sent system-wide (or within your app via LocalBroadcastManager / sendBroadcast) — used for system events like connectivity changes.</li>
      </ul>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <p>The Fragment back stack is managed by <code>FragmentManager</code>. Each <code>beginTransaction()</code> creates a <code>FragmentTransaction</code> that atomically changes the set of active fragments. When you call <code>addToBackStack(name)</code>, the transaction is recorded and pressing Back reverses it. The Fragment's view is destroyed on back-stack entry (to free memory) but the Fragment instance remains, preserving its member variables and ViewModel association.</p>
      <pre class="code-block"><code class="language-kotlin">// Fragment — always clear view references in onDestroyView
class TransactionListFragment : Fragment(R.layout.fragment_transaction_list) {

    // Use backing property pattern to avoid leaking binding
    private var _binding: FragmentTransactionListBinding? = null
    private val binding get() = _binding!!

    // Shared ViewModel scoped to the parent Activity — survives fragment replacement
    private val sharedViewModel: AccountViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentTransactionListBinding.bind(view)

        // Use viewLifecycleOwner, NOT this — fragment outlives its view on backstack
        sharedViewModel.transactions.observe(viewLifecycleOwner) { transactions ->
            adapter.submitList(transactions)
        }

        // Fragment Result API — type-safe communication between fragments
        setFragmentResultListener(FilterFragment.REQUEST_KEY) { _, bundle ->
            val filter = bundle.getParcelable<TransactionFilter>(FilterFragment.KEY_FILTER)
            filter?.let { sharedViewModel.applyFilter(it) }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null  // CRITICAL: prevents memory leak when fragment is on backstack
    }
}

// Implicit Intent — open PDF, let OS pick handler
fun openReport(uri: Uri) {
    val intent = Intent(Intent.ACTION_VIEW).apply {
        setDataAndType(uri, "application/pdf")
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }
    // Check if any app can handle this before launching!
    if (intent.resolveActivity(packageManager) != null) {
        startActivity(intent)
    } else {
        showError("No PDF viewer installed")
    }
}

// PendingIntent for notification action (immutable flag required on API 23+)
fun buildPaymentNotification(transactionId: String): Notification {
    val deepLinkIntent = Intent(context, MainActivity::class.java).apply {
        action = ACTION_VIEW_TRANSACTION
        putExtra(EXTRA_TRANSACTION_ID, transactionId)
        flags = Intent.FLAG_ACTIVITY_SINGLE_TOP
    }
    val pendingIntent = PendingIntent.getActivity(
        context, transactionId.hashCode(), deepLinkIntent,
        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
    )
    return NotificationCompat.Builder(context, CHANNEL_PAYMENTS)
        .setContentTitle("Payment Received")
        .setContentIntent(pendingIntent)
        .build()
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// FragmentManager transactions
supportFragmentManager.commit {
    setCustomAnimations(R.anim.slide_in, R.anim.slide_out, R.anim.pop_enter, R.anim.pop_exit)
    replace(R.id.fragment_container, DetailFragment.newInstance(id))
    addToBackStack("detail")
}

// Fragment Result API (modern, type-safe, replaces interface callbacks)
// Sender Fragment:
setFragmentResult("requestKey", bundleOf("amount" to 100.0))

// Receiver Fragment (or Activity):
supportFragmentManager.setFragmentResultListener("requestKey", this) { _, bundle ->
    val amount = bundle.getDouble("amount")
}

// Share data between fragments via shared ViewModel
class SharedViewModel : ViewModel() {
    private val _selected = MutableLiveData<Transaction>()
    val selected: LiveData<Transaction> = _selected
    fun select(t: Transaction) { _selected.value = t }
}
// In both fragments:
val model: SharedViewModel by activityViewModels()

// Intent chooser (let user pick from multiple handlers)
val shareIntent = Intent.createChooser(
    Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"
        putExtra(Intent.EXTRA_TEXT, "Check out my transaction!")
    }, "Share via"
)
startActivity(shareIntent)</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example</h3>
      <p><strong>Healthcare — Patient Record Navigation:</strong> A tablet shows a master-detail layout where the left pane lists patients (ListFragment) and the right pane shows details (DetailFragment). Both share a ViewModel. A bottom sheet Fragment for adding notes uses the Fragment Result API to send results back to DetailFragment without tight coupling.</p>
      <pre class="code-block"><code class="language-kotlin">class PatientDetailFragment : Fragment(R.layout.fragment_patient_detail) {
    private var _binding: FragmentPatientDetailBinding? = null
    private val binding get() = _binding!!
    private val viewModel: PatientViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentPatientDetailBinding.bind(view)

        // Receive new clinical note from AddNoteBottomSheet
        setFragmentResultListener(AddNoteBottomSheet.RESULT_KEY) { _, bundle ->
            val note = bundle.getParcelable<ClinicalNote>(AddNoteBottomSheet.KEY_NOTE)
            note?.let { viewModel.addNote(it) }
        }

        binding.addNoteFab.setOnClickListener {
            AddNoteBottomSheet().show(childFragmentManager, AddNoteBottomSheet.TAG)
        }

        viewModel.patientDetail.observe(viewLifecycleOwner) { detail ->
            binding.patientName.text = detail.fullName
            binding.vitalSigns.text = detail.latestVitals.summary()
            notesAdapter.submitList(detail.clinicalNotes)
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Observing LiveData with <code>this</code> instead of <code>viewLifecycleOwner</code>:</strong> When the fragment is on the back stack, its view is destroyed but the fragment lives on — <code>this</code> lifecycle is STARTED, so updates arrive to a null view — ✅ Fix: Always use <code>viewLifecycleOwner</code> for view-related observations.</li>
        <li>❌ <strong>Not nulling binding in onDestroyView:</strong> Fragment instance stays on the back stack holding binding reference which holds views → memory leak — ✅ Fix: <code>_binding = null</code> in onDestroyView.</li>
        <li>❌ <strong>Implicit Intent without resolveActivity check:</strong> On Android 11+ with package visibility restrictions, unhandled intents throw ActivityNotFoundException — ✅ Fix: Always check <code>intent.resolveActivity(packageManager) != null</code> or catch the exception.</li>
        <li>❌ <strong>Mutable PendingIntent without FLAG_IMMUTABLE:</strong> Required from Android 12 (API 31) — ✅ Fix: Always add FLAG_IMMUTABLE (or FLAG_MUTABLE if you must mutate).</li>
        <li>❌ <strong>Using interface callbacks between fragments:</strong> Creates coupling, easy to NPE — ✅ Fix: Use Fragment Result API or shared ViewModel.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Fragment lifecycle has a subtle but critical distinction: the fragment instance outlives its view when placed on the back stack. In production, I always use the backing-property pattern for ViewBinding (<code>_binding = null</code> in onDestroyView) and observe LiveData with <code>viewLifecycleOwner</code> — not <code>this</code> — to avoid delivering updates to a null view. For fragment-to-fragment communication, I've migrated all interface-callback patterns to the Fragment Result API, which is type-safe and lifecycle-aware by design. For Intents, I treat implicit intents as contracts with the OS ecosystem — always verifying resolution before launch and using FLAG_GRANT_READ_URI_PERMISSION for content URIs. For PendingIntents, particularly in notifications and alarms, I always add FLAG_IMMUTABLE on API 23+ and use unique request codes derived from content IDs to prevent collisions."</p>
      </div>
    </div>
  </div>

  <!-- Q&A Section for Topic 13 -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the correct order of Activity lifecycle callbacks when a user opens an Activity, then another Activity covers it partially (dialog-theme), then the user dismisses the dialog?</div>
      <div class="qa-answer">
        <p>Opening: <strong>onCreate → onStart → onResume</strong></p>
        <p>Dialog-theme Activity covers partially: <strong>onPause</strong> (NOT onStop — the original Activity is still visible behind the dialog)</p>
        <p>Dialog dismissed: <strong>onResume</strong></p>
        <p>Key insight: <code>onStop</code> is only called when the Activity is <em>completely</em> hidden. A dialog-themed Activity only partially covers the screen, so the original Activity remains visible and only pauses.</p>
        <pre class="code-block"><code class="language-kotlin">// Verify this by adding logs to each callback:
override fun onPause()  { super.onPause();  Log.d("LC", "onPause")  }
override fun onStop()   { super.onStop();   Log.d("LC", "onStop")   }
override fun onResume() { super.onResume(); Log.d("LC", "onResume") }
// Result: only onPause/onResume fires, never onStop</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q2</span>How does ViewModel survive configuration changes? What exactly happens at the framework level?</div>
      <div class="qa-answer">
        <p>When a configuration change occurs (rotation), the Activity is destroyed and recreated. But before destroying, <code>ActivityThread</code> calls <code>onRetainNonConfigurationInstance()</code> which returns the <code>ViewModelStore</code> wrapped in a <code>NonConfigurationInstances</code> object. This object is stored in the <code>ActivityClientRecord</code> inside the app process — it is NOT serialized, NOT sent to system_server. When the new Activity instance is created, the framework calls <code>getLastNonConfigurationInstance()</code> to retrieve it. The ViewModel's <code>onCleared()</code> is only called when the Activity is truly finishing (not rotating), detected by <code>isFinishing()</code> being true.</p>
        <pre class="code-block"><code class="language-kotlin">// ViewModelStore survives rotation because it's held in memory, not serialized
// Sequence on rotation:
// 1. Activity.onRetainNonConfigurationInstance() called internally
// 2. Returns ActivityThread.NonConfigurationInstances containing ViewModelStore
// 3. Activity destroyed (but NOT ViewModelStore.clear())
// 4. New Activity created
// 5. Activity.getLastNonConfigurationInstance() retrieves the same store
// 6. ViewModelProvider finds existing ViewModel in the store
// 7. onCleared() is called only when isFinishing() == true</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q3</span>Your app has a 3-screen flow: A → B → C. From C, the user taps "Go to Home" which should go back to A and clear B and C from the stack. How do you implement this?</div>
      <div class="qa-answer">
        <p>Use <code>FLAG_ACTIVITY_CLEAR_TOP</code> combined with <code>FLAG_ACTIVITY_SINGLE_TOP</code>:</p>
        <pre class="code-block"><code class="language-kotlin">// From Activity C:
fun navigateToHome() {
    val intent = Intent(this, HomeActivity::class.java).apply {
        // CLEAR_TOP: removes B and C from stack, brings A to top
        // SINGLE_TOP: reuses existing A instance (calls onNewIntent) instead of creating new one
        flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
    }
    startActivity(intent)
    finish() // Also finish C explicitly since CLEAR_TOP handles B
}

// In HomeActivity — handle the re-navigation
override fun onNewIntent(intent: Intent) {
    super.onNewIntent(intent)
    setIntent(intent) // Update intent if needed
    // Reset to home tab if needed
    binding.bottomNav.selectedItemId = R.id.nav_home
}</code></pre>
        <p><strong>Alternative with Navigation Component:</strong></p>
        <pre class="code-block"><code class="language-kotlin">// In nav_graph.xml, define action with popUpTo
// Or programmatically:
findNavController().navigate(
    R.id.homeFragment,
    null,
    NavOptions.Builder()
        .setPopUpTo(R.id.homeFragment, inclusive = false)
        .build()
)</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q4</span>What is the difference between <code>viewLifecycleOwner</code> and <code>this</code> when observing LiveData in a Fragment? Why does it matter?</div>
      <div class="qa-answer">
        <p><strong>Fragment's <code>this</code> lifecycle:</strong> Created when Fragment is created, destroyed when Fragment is truly destroyed (popped from back stack entirely). When Fragment is on the back stack, <code>this</code> lifecycle is STOPPED but not destroyed.</p>
        <p><strong><code>viewLifecycleOwner</code>:</strong> A separate LifecycleOwner tied to the Fragment's <em>view</em>. Created in <code>onCreateView</code>, destroyed in <code>onDestroyView</code>. When Fragment goes on back stack, its view IS destroyed, so <code>viewLifecycleOwner</code> is destroyed too — stopping observers.</p>
        <p><strong>Why it matters:</strong> If you use <code>this</code> to observe LiveData and the fragment is on the back stack (view destroyed), a LiveData update arrives → observer runs → tries to update <code>binding.someView</code> → NullPointerException (binding was nulled in onDestroyView) or memory leak (binding still holds view reference).</p>
        <pre class="code-block"><code class="language-kotlin">// WRONG — can crash or leak:
viewModel.data.observe(this) { binding.textView.text = it }

// CORRECT — observer dies with the view:
viewModel.data.observe(viewLifecycleOwner) { binding.textView.text = it }</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q5</span>In a banking app, after the user logs out, pressing Back should NOT return to any authenticated screen. How do you implement this?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">// Option 1: Clear task on logout
fun logout() {
    authRepository.clearSession()
    val intent = Intent(this, LoginActivity::class.java).apply {
        // FLAG_ACTIVITY_NEW_TASK: Start fresh task
        // FLAG_ACTIVITY_CLEAR_TASK: Clears ALL activities in the current task
        flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
    }
    startActivity(intent)
    // No need to call finish() — CLEAR_TASK destroys everything
}

// Option 2: With Navigation Component — pop everything
fun logout() {
    authRepository.clearSession()
    findNavController().navigate(
        R.id.loginFragment,
        null,
        NavOptions.Builder()
            .setPopUpTo(R.id.nav_graph, inclusive = true) // Pops the root
            .build()
    )
}

// Option 3: Override onBackPressed in all auth activities
class DashboardActivity : AppCompatActivity() {
    override fun onBackPressed() {
        if (!authRepository.isLoggedIn()) {
            // Already logged out — finish completely
            finishAffinity()
        } else {
            super.onBackPressed()
        }
    }
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q6</span>What is the difference between an Explicit and Implicit Intent? When do you use each?</div>
      <div class="qa-answer">
        <p><strong>Explicit Intent:</strong> You specify the exact component (class) to start. Used for internal app navigation — you know exactly which Activity/Service to start.</p>
        <p><strong>Implicit Intent:</strong> You specify an action, data URI, and/or category. The OS matches this against all registered IntentFilters across all apps and presents options (or auto-launches if only one match). Used for inter-app communication.</p>
        <pre class="code-block"><code class="language-kotlin">// Explicit — internal navigation
val explicit = Intent(this, PaymentActivity::class.java)
startActivity(explicit)

// Implicit — let any app handle "view PDF"
val implicit = Intent(Intent.ACTION_VIEW).apply {
    setDataAndType(pdfUri, "application/pdf")
    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
}
// Safety check required before starting!
if (packageManager.resolveActivity(implicit, 0) != null) {
    startActivity(implicit)
}

// Never use implicit intents for starting your own Services (security)
// Android 5.0+ throws IllegalArgumentException for implicit Service intents</code></pre>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge</h3>
    <p><strong>Problem:</strong> Implement a Fragment back stack that handles the following scenario: MainActivity hosts a NavHostFragment. The user navigates A → B → C → D. From D, they want to "Go to B" (popping C and D), then from B they can still go back to A. Additionally, implement proper lifecycle-safe observation in each fragment.</p>
    <pre class="code-block"><code class="language-kotlin">// Solution using Navigation Component + Safe Observation

// nav_graph.xml (conceptual)
// A --[action_a_to_b]--> B --[action_b_to_c]--> C --[action_c_to_d]--> D
// D has [action_d_to_b] with popUpTo="B" inclusive=false

// FragmentD.kt
class FragmentD : Fragment(R.layout.fragment_d) {
    private var _binding: FragmentDBinding? = null
    private val binding get() = _binding!!
    private val viewModel: SharedViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentDBinding.bind(view)

        // Lifecycle-safe observation
        viewModel.importantState.observe(viewLifecycleOwner) { state ->
            binding.statusText.text = state.message
        }

        // Navigate to B, removing C and D from stack
        binding.goToBButton.setOnClickListener {
            // Option 1: Nav Component (declarative, preferred)
            findNavController().navigate(
                R.id.action_d_to_b,
                null,
                NavOptions.Builder()
                    .setPopUpTo(R.id.fragmentB, inclusive = false) // Keep B, pop C & D
                    .build()
            )

            // Option 2: Programmatic FragmentManager
            // parentFragmentManager.popBackStack("B_tag", 0)
            // (0 = pop everything above the named entry, inclusive=0 means keep B)
        }

        // Send result back to B before navigating
        binding.goToBWithDataButton.setOnClickListener {
            // Fragment Result API — type-safe, no coupling
            setFragmentResult(
                "D_to_B_result",
                bundleOf("processedData" to "Result from D")
            )
            findNavController().navigate(
                R.id.action_d_to_b,
                null,
                NavOptions.Builder().setPopUpTo(R.id.fragmentB, false).build()
            )
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // Prevent memory leak
    }
}

// FragmentB.kt — receives result from D
class FragmentB : Fragment(R.layout.fragment_b) {
    private var _binding: FragmentBBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentBBinding.bind(view)

        // Listen for result from D
        setFragmentResultListener("D_to_B_result") { _, bundle ->
            val data = bundle.getString("processedData")
            binding.resultText.text = data
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

// Time Complexity: O(n) where n = depth of back stack for popBackStack
// Space Complexity: O(n) for back stack entries
// Key Points:
// 1. viewLifecycleOwner prevents NPE on back-stack fragments
// 2. Fragment Result API replaces interface callbacks (decoupled)
// 3. NavOptions.popUpTo is declarative and testable
// 4. _binding = null in onDestroyView is mandatory for back-stack fragments</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="13" data-item="0"> ✅ Understood Why &amp; What</label>
    <label class="progress-check"><input type="checkbox" data-topic="13" data-item="1"> ✅ Can explain How it works internally</label>
    <label class="progress-check"><input type="checkbox" data-topic="13" data-item="2"> ✅ Reviewed Common Mistakes</label>
    <label class="progress-check"><input type="checkbox" data-topic="13" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="13" data-item="4"> ✅ Solved Coding Challenge</label>
  </div>
</section>

<!-- ============================================================ -->
<!--  TOPIC 14: Kotlin Coroutines                                 -->
<!-- ============================================================ -->
<section class="topic-section" id="topic-14">
  <div class="topic-header">
    <div class="topic-header-icon">⚡</div>
    <div class="topic-header-text">
      <h1>Kotlin Coroutines</h1>
      <p class="topic-tagline">Structured concurrency, Dispatchers, cancellation, and exception handling — the async backbone of modern Android</p>
      <div class="category-badge-group">
        <span class="cat-pill">Coroutines</span>
        <span class="cat-pill">Dispatchers</span>
        <span class="cat-pill">Structured Concurrency</span>
        <span class="cat-pill">Exception Handling</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 14-1: Coroutine Builders & Dispatchers -->
  <div class="subtopic" id="subtopic-14-1">
    <h2>Coroutine Builders, Dispatchers &amp; CoroutineScope</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Android's main thread drives UI rendering at 60-120fps — any blocking operation (network, database, file I/O) over ~16ms causes a dropped frame or ANR. Traditional solutions — Java threads, RxJava, callbacks — all have severe drawbacks: threads are expensive (1MB stack each), callbacks produce "callback hell" making error propagation impossible, and RxJava has a steep learning curve with complex operator chains.</p>
      <p>Coroutines let you write async code that <em>reads like synchronous code</em>, uses a tiny amount of memory (no OS thread required — just a continuation object on the heap), and integrates natively with Android's lifecycle via <code>lifecycleScope</code> and <code>viewModelScope</code>. The key innovation is <strong>structured concurrency</strong>: coroutines are organized in a hierarchy — when a parent scope is cancelled, all children are cancelled automatically, preventing orphaned coroutines from leaking.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p>A <strong>coroutine</strong> is a suspendable computation — a unit of work that can be paused (suspended) at <code>suspend</code> function call points and resumed later, without blocking the underlying thread. Internally, the Kotlin compiler transforms <code>suspend</code> functions into state machines using a <code>Continuation</code> parameter (Continuation Passing Style). Each suspension point becomes a state in the machine.</p>
      <p><strong>Dispatchers</strong> determine which thread(s) a coroutine runs on:</p>
      <ul>
        <li><code>Dispatchers.Main</code> — Android's main thread. For UI updates only.</li>
        <li><code>Dispatchers.IO</code> — Elastic thread pool (up to 64 threads or CPU cores × 2, whichever is larger). For network, database, file I/O.</li>
        <li><code>Dispatchers.Default</code> — CPU-bounded pool (CPU core count threads). For parsing, sorting, heavy computation.</li>
        <li><code>Dispatchers.Unconfined</code> — Runs in the caller's thread until first suspension, then resumes in whatever thread the suspending function completes on. Rarely used in production.</li>
      </ul>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <p>Under the hood, <code>suspend fun fetchUser(): User</code> is compiled to <code>fun fetchUser(continuation: Continuation&lt;User&gt;): Any?</code>. When the coroutine suspends (e.g., at a network call), it stores its local state in the Continuation object and returns <code>COROUTINE_SUSPENDED</code>. The dispatcher's thread is now free to do other work. When the network response arrives, the continuation is resumed on the appropriate dispatcher's thread.</p>
      <pre class="code-block"><code class="language-kotlin">class TransactionViewModel : ViewModel() {

    // viewModelScope is tied to ViewModel lifecycle — auto-cancelled in onCleared()
    fun loadDashboard(userId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            // withContext switches dispatcher for this block only
            // then returns to the calling dispatcher (Main)
            val result = runCatching {
                withContext(Dispatchers.IO) {
                    // These run concurrently within the IO dispatcher
                    val userDeferred = async { userRepository.fetchUser(userId) }
                    val balanceDeferred = async { accountRepository.fetchBalance(userId) }
                    val transactionsDeferred = async { transactionRepository.fetchRecent(userId) }

                    // await() suspends until each completes; if any throws, all are cancelled
                    DashboardData(
                        user = userDeferred.await(),
                        balance = balanceDeferred.await(),
                        transactions = transactionsDeferred.await()
                    )
                }
            }

            _uiState.value = result.fold(
                onSuccess = { UiState.Success(it) },
                onFailure = { UiState.Error(it.message ?: "Unknown error") }
            )
        }
    }

    // withContext vs launch: withContext returns a result, launch is fire-and-forget
    suspend fun getAccountSummary(id: String): AccountSummary = withContext(Dispatchers.IO) {
        accountRepository.getSummary(id) // Suspends here, frees calling thread
    }
}

// In Activity/Fragment — use lifecycleScope for view-related coroutines
class DashboardFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Scoped to Fragment's view lifecycle — auto-cancelled in onDestroyView
        viewLifecycleOwner.lifecycleScope.launch {
            // repeatOnLifecycle suspends when below STARTED, resumes when STARTED
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    updateUi(state)
                }
            }
        }
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// Coroutine Builders:
// launch — fire-and-forget, returns Job
val job: Job = scope.launch { /* ... */ }
job.cancel()  // Cancels coroutine (cooperative — checks cancellation at suspension points)
job.join()    // Suspends until job completes

// async — concurrent computation, returns Deferred<T>
val deferred: Deferred<User> = scope.async { fetchUser() }
val user: User = deferred.await()  // Suspends until result available

// runBlocking — BLOCKS current thread until completion (ONLY in tests/main())
val result = runBlocking { fetchUser() }  // NEVER use in production Android code!

// withContext — switch dispatcher, returns result
val parsed = withContext(Dispatchers.Default) { parseJson(rawJson) }

// CoroutineScope creation:
val customScope = CoroutineScope(SupervisorJob() + Dispatchers.IO + CoroutineName("MyScope"))

// Key Job functions:
job.isActive      // true if running
job.isCancelled   // true if cancelled
job.isCompleted   // true if done (success or failure)
job.cancelAndJoin()  // cancel + wait for cleanup

// Dispatcher switching pattern:
suspend fun processData(data: RawData): ProcessedData {
    val parsed = withContext(Dispatchers.Default) { heavyParsing(data) }
    val saved  = withContext(Dispatchers.IO)      { database.insert(parsed) }
    return saved
    // Back on calling dispatcher after return
}</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example</h3>
      <p><strong>FinTech — Parallel Account Aggregation:</strong> A financial dashboard must load data from 3 independent services concurrently (not sequentially) to minimize latency. If one fails, the others should still display. Uses supervisorScope + async.</p>
      <pre class="code-block"><code class="language-kotlin">class AccountAggregationViewModel : ViewModel() {
    private val _state = MutableStateFlow<AggregationState>(AggregationState.Loading)
    val state: StateFlow<AggregationState> = _state.asStateFlow()

    fun loadAggregatedData(userId: String) {
        viewModelScope.launch {
            _state.value = AggregationState.Loading

            // supervisorScope: child failures don't cancel siblings
            val result = withContext(Dispatchers.IO) {
                supervisorScope {
                    // All 3 start concurrently
                    val checkingDeferred = async {
                        runCatching { bankApi.getCheckingAccount(userId) }
                    }
                    val savingsDeferred = async {
                        runCatching { bankApi.getSavingsAccount(userId) }
                    }
                    val investmentsDeferred = async {
                        runCatching { brokerApi.getPortfolio(userId) }
                    }

                    AggregatedAccountData(
                        checking    = checkingDeferred.await().getOrNull(),
                        savings     = savingsDeferred.await().getOrNull(),
                        investments = investmentsDeferred.await().getOrNull(),
                        errors      = listOfNotNull(
                            checkingDeferred.await().exceptionOrNull(),
                            savingsDeferred.await().exceptionOrNull(),
                            investmentsDeferred.await().exceptionOrNull()
                        )
                    )
                }
            }

            _state.value = AggregationState.Success(result)

            // Show degraded state banner if some sources failed
            if (result.errors.isNotEmpty()) {
                _state.value = AggregationState.PartialSuccess(result)
            }
        }
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Using GlobalScope:</strong> Coroutines outlive Activity/ViewModel, cause leaks and orphaned network calls — ✅ Fix: Always use viewModelScope, lifecycleScope, or a custom scope with a well-defined lifetime.</li>
        <li>❌ <strong>launch inside launch for sequential work:</strong> Nested launches are independent and don't propagate cancellation or results — ✅ Fix: Use withContext for sequential work within the same coroutine.</li>
        <li>❌ <strong>Calling blocking functions in coroutines without withContext:</strong> <code>Thread.sleep()</code>, <code>File.readText()</code> on Dispatchers.Main blocks UI — ✅ Fix: Always wrap blocking calls in withContext(Dispatchers.IO).</li>
        <li>❌ <strong>Not handling cancellation in CPU-intensive loops:</strong> A cancelled coroutine at a pure computation loop never suspends → never checks cancellation → hangs — ✅ Fix: Periodically call <code>ensureActive()</code> or <code>yield()</code> in long loops.</li>
        <li>❌ <strong>Using async/await sequentially:</strong> <code>val a = async { }; a.await(); val b = async { }; b.await()</code> has zero parallelism benefit — ✅ Fix: Start all async blocks first, then await all results.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Coroutines solve Android's threading problem through structured concurrency — the principle that coroutines have a defined lifetime tied to a scope. In production, I use viewModelScope for data-loading operations and viewLifecycleOwner.lifecycleScope with repeatOnLifecycle for UI collection. I choose Dispatchers.IO for all I/O (network, DB, files) and Dispatchers.Default for CPU-heavy transformations, never blocking Main. For concurrent operations where failures should be independent — like loading data from multiple APIs — I use supervisorScope with async/await so one failure doesn't kill the others. I'm meticulous about ensuring coroutines are cancellable: I never use Thread.sleep in coroutines, and in CPU-bound loops I call ensureActive() to cooperate with cancellation. The key mental model is: a Job is a node in a tree; cancelling a parent cancels all children; exceptions propagate up unless isolated by supervisorScope or async."</p>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 14-2: Exception Handling & Cancellation -->
  <div class="subtopic" id="subtopic-14-2">
    <h2>Exception Handling &amp; Cancellation</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>In concurrent systems, unhandled exceptions can silently swallow errors, corrupt state, or crash the entire app. Kotlin Coroutines have a non-obvious exception propagation model: exceptions from <code>launch</code> propagate up to the parent scope and can crash the app if unhandled, while exceptions from <code>async</code> are stored in the Deferred and only thrown when you call <code>await()</code>. Without understanding this, you write try-catch blocks in the wrong places and ship apps that crash in production on slow networks.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p><strong>Exception Handling in Coroutines:</strong> Exceptions from <code>launch</code> are immediately propagated to the parent Job and then to the CoroutineExceptionHandler (or crash if none). Exceptions from <code>async</code> are <em>deferred</em> — stored until <code>await()</code> is called. <code>supervisorScope</code> / <code>SupervisorJob</code> changes this: child failures do NOT propagate to the parent, allowing sibling coroutines to continue.</p>
      <p><strong>Cancellation:</strong> Cancellation is cooperative. When you call <code>job.cancel()</code>, the coroutine's Job moves to a Cancelling state. The cancellation only takes effect at the next suspension point (any <code>suspend</code> function call) — the runtime throws <code>CancellationException</code> there. CancellationException is special: it is never propagated to CoroutineExceptionHandler (it's a normal part of structured concurrency) and should not be caught and swallowed.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// Exception Handling Patterns

// 1. try-catch inside coroutine (recommended for specific operations)
viewModelScope.launch {
    try {
        val data = repository.fetchSensitiveData() // Can throw IOException, HttpException
        _state.value = UiState.Success(data)
    } catch (e: IOException) {
        _state.value = UiState.Error("Network error: ${e.message}")
    } catch (e: HttpException) {
        _state.value = UiState.Error("Server error: ${e.code()}")
    }
    // CancellationException propagates up automatically — don't catch it!
}

// 2. runCatching — functional style
viewModelScope.launch {
    val result = runCatching { repository.fetchData() }
    result.fold(
        onSuccess = { _state.value = UiState.Success(it) },
        onFailure = { e ->
            if (e is CancellationException) throw e // Re-throw cancellation!
            _state.value = UiState.Error(e.message ?: "Unknown error")
        }
    )
}

// 3. CoroutineExceptionHandler — last resort for launch (not async!)
val handler = CoroutineExceptionHandler { _, exception ->
    // Runs on the dispatcher of the failed coroutine
    // Use for logging/crash reporting only — NOT for UI updates from here
    Timber.e(exception, "Unhandled coroutine exception")
    crashlytics.recordException(exception)
}
val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main + handler)

// 4. supervisorScope — siblings are independent
viewModelScope.launch {
    supervisorScope {
        launch {
            try {
                repository.syncTransactions() // If this fails...
            } catch (e: Exception) {
                Timber.e(e) // Handle locally — doesn't kill sibling
            }
        }
        launch {
            repository.syncProfile() // ...this still runs
        }
    }
}

// 5. Cancellation — cooperative pattern
suspend fun processLargeDataset(items: List<Item>): List<Result> {
    return items.mapIndexed { index, item ->
        ensureActive() // Throws CancellationException if cancelled — cooperative!
        processItem(item)
    }
}

// withTimeout / withTimeoutOrNull
val result = withTimeoutOrNull(5_000L) { // 5 second timeout
    repository.fetchWithRetry()
} ?: handleTimeout() // Returns null on timeout instead of throwing</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// Key Exception Handling APIs:
try { } catch (e: CancellationException) { throw e } // ALWAYS re-throw CancellationException
runCatching { suspendFun() }.onFailure { if (it is CancellationException) throw it }

// SupervisorJob vs Job:
// Job: child failure → parent cancelled → all siblings cancelled
// SupervisorJob: child failure → only that child fails, siblings continue

// CoroutineExceptionHandler:
val handler = CoroutineExceptionHandler { coroutineContext, throwable ->
    // Called for UNCAUGHT exceptions in launch coroutines
    // NOT called for async (you catch via await())
    // NOT called if you use supervisorScope without a handler
}

// Cancellation checking:
ensureActive()          // Throws CancellationException if Job is cancelled
isActive                // Boolean check (use in loops)
yield()                 // Checks cancellation AND yields execution to other coroutines

// Timeout:
withTimeout(2_000L) { networkCall() }          // Throws TimeoutCancellationException
val r = withTimeoutOrNull(2_000L) { networkCall() }  // Returns null on timeout

// Non-cancellable cleanup:
withContext(NonCancellable) {
    database.savePartialProgress() // Runs even if parent is being cancelled
}</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example</h3>
      <p><strong>Healthcare — Patient Data Sync with Timeout &amp; Retry:</strong> Critical patient data must sync with a 10-second timeout and 3 retry attempts. If cancelled (user navigates away), partial progress must be saved atomically.</p>
      <pre class="code-block"><code class="language-kotlin">class PatientSyncRepository @Inject constructor(
    private val api: EhrApi,
    private val database: PatientDatabase
) {
    suspend fun syncPatientRecord(patientId: String): SyncResult {
        var lastException: Exception? = null
        repeat(3) { attempt ->
            try {
                val record = withTimeout(10_000L) {
                    api.fetchPatientRecord(patientId)
                }
                withContext(Dispatchers.IO) {
                    database.upsertPatientRecord(record)
                }
                return SyncResult.Success(record)
            } catch (e: TimeoutCancellationException) {
                lastException = e
                Timber.w("Sync attempt ${attempt + 1} timed out for patient $patientId")
                if (attempt < 2) delay(1_000L * (attempt + 1)) // Exponential backoff
            } catch (e: CancellationException) {
                // Scope was cancelled (user navigated away) — save partial state
                withContext(NonCancellable + Dispatchers.IO) {
                    database.markSyncInterrupted(patientId)
                }
                throw e // Re-throw — structured concurrency must propagate this
            } catch (e: HttpException) {
                if (e.code() == 429) { // Rate limited
                    delay(e.retryAfterMillis())
                } else throw e // Don't retry on client errors
            }
        }
        return SyncResult.Failure(lastException ?: Exception("Max retries exceeded"))
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Catching CancellationException and not re-throwing:</strong> Swallowing CancellationException breaks structured concurrency — the parent thinks the coroutine completed successfully — ✅ Fix: Always re-throw CancellationException or use runCatching carefully with explicit re-throw.</li>
        <li>❌ <strong>Putting try-catch around async{} instead of await():</strong> Exceptions from async don't throw until await() — catch around async{} block catches nothing — ✅ Fix: Wrap await() in try-catch.</li>
        <li>❌ <strong>Using launch + CoroutineExceptionHandler with supervisorScope:</strong> CoroutineExceptionHandler is only invoked on the root of the coroutine hierarchy — inside supervisorScope, it works; but the handler must be on the scope, not the child — ✅ Fix: Understand handler scoping rules.</li>
        <li>❌ <strong>Blocking thread inside catch block:</strong> Doing Thread.sleep() in a catch block inside a coroutine still blocks the thread — ✅ Fix: Use delay() in coroutines for waiting.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Coroutine exception handling has two mental models depending on the builder. With launch, exceptions propagate immediately up to the parent scope and cause it to fail — unless you use SupervisorJob or supervisorScope to isolate them. With async, exceptions are stored in the Deferred and only surface at await() — which means you must wrap await() calls in try-catch. The critical rule I follow in production: never swallow CancellationException. When runCatching is used, I always check for CancellationException and re-throw it, because it's the mechanism structured concurrency uses to cleanly terminate coroutine trees. For cleanup that must happen even during cancellation — like saving a user's partial form data — I use withContext(NonCancellable) for the critical section. For timeouts, I prefer withTimeoutOrNull over withTimeout in UI code to avoid exception-based flow control."</p>
      </div>
    </div>
  </div>

  <!-- Q&A for Topic 14 -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the difference between <code>launch</code> and <code>async</code>? When do you use each?</div>
      <div class="qa-answer">
        <p><strong>launch:</strong> Fire-and-forget. Returns a <code>Job</code> (no result value). Exceptions propagate immediately to the parent scope. Use when you don't need a return value.</p>
        <p><strong>async:</strong> Returns a <code>Deferred&lt;T&gt;</code> — a future value. Exceptions are deferred until <code>await()</code> is called. Use when you need a result, especially for parallel decomposition.</p>
        <pre class="code-block"><code class="language-kotlin">// launch — no result needed
viewModelScope.launch {
    analyticsService.logEvent("screen_viewed")
}

// async — parallel work with results
viewModelScope.launch {
    // Both start concurrently:
    val userDeferred = async { userRepo.fetchUser(id) }
    val ordersDeferred = async { orderRepo.fetchOrders(id) }

    // Suspend until both complete:
    val user = userDeferred.await()
    val orders = ordersDeferred.await()
    _state.value = ProfileState(user, orders)
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q2</span>What is structured concurrency and why does it matter?</div>
      <div class="qa-answer">
        <p>Structured concurrency is the principle that coroutines must complete before the scope that launched them completes. Every coroutine belongs to a scope, and scopes form a tree. This guarantees:</p>
        <ul>
          <li><strong>No leaks:</strong> When a scope is cancelled (e.g., ViewModel cleared), all child coroutines are automatically cancelled.</li>
          <li><strong>Error propagation:</strong> Exceptions from children bubble up to parents.</li>
          <li><strong>Completion ordering:</strong> A parent scope doesn't complete until all its children do.</li>
        </ul>
        <pre class="code-block"><code class="language-kotlin">// Without structured concurrency (GlobalScope — WRONG):
fun loadData() {
    GlobalScope.launch { // Outlives ViewModel! Even after onCleared()
        repository.fetchExpensiveData()
    }
}

// With structured concurrency (viewModelScope — CORRECT):
fun loadData() {
    viewModelScope.launch { // Auto-cancelled when ViewModel.onCleared() called
        repository.fetchExpensiveData()
        // If this throws, scope handles it; when scope cancelled, this is cancelled
    }
}

// coroutineScope {} — creates a child scope; suspends parent until all children complete
suspend fun doWork() {
    coroutineScope {
        launch { task1() }
        launch { task2() }
    } // Suspends here until task1 AND task2 complete
    // If task1 or task2 throws, both are cancelled, exception propagates
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>What is the difference between <code>coroutineScope</code> and <code>supervisorScope</code>?</div>
      <div class="qa-answer">
        <p><strong>coroutineScope:</strong> If any child coroutine fails, all siblings are cancelled and the exception propagates to the parent. All-or-nothing semantics. Use when all tasks must succeed for the result to be meaningful.</p>
        <p><strong>supervisorScope:</strong> Child failures are independent — one failing child does NOT cancel siblings. The exception must be handled locally (within the child) or it's ignored at the supervisor level. Use when tasks are independent.</p>
        <pre class="code-block"><code class="language-kotlin">// coroutineScope: if user fetch fails, orders fetch is also cancelled
suspend fun loadProfileData(): ProfileData {
    return coroutineScope {
        val user = async { userRepo.fetchUser() }
        val orders = async { orderRepo.fetchOrders() }
        ProfileData(user.await(), orders.await()) // If either throws, both cancelled
    }
}

// supervisorScope: analytics failure doesn't cancel the main data load
suspend fun loadDashboard() {
    supervisorScope {
        launch {
            try { analyticsRepo.logView() }
            catch (e: Exception) { /* Non-critical — ignore */ }
        }
        launch {
            // This runs even if analytics fails
            val data = mainRepo.fetchDashboardData()
            _state.value = UiState.Success(data)
        }
    }
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q4</span>You have a coroutine doing a long CPU-intensive calculation in a loop. The user navigates away and the scope is cancelled. Why might the coroutine NOT stop immediately, and how do you fix it?</div>
      <div class="qa-answer">
        <p>Cancellation in Kotlin Coroutines is <strong>cooperative</strong>. When you call <code>job.cancel()</code>, the cancellation flag is set, but the actual <code>CancellationException</code> is only thrown at the next <em>suspension point</em>. A pure CPU-bound loop with no <code>suspend</code> calls has NO suspension points — the coroutine will run to completion regardless of cancellation.</p>
        <pre class="code-block"><code class="language-kotlin">// PROBLEM: Non-cooperative cancellation
suspend fun processItems(items: List<Item>) = withContext(Dispatchers.Default) {
    for (item in items) {
        heavyComputation(item) // No suspension points — ignores cancellation!
    }
}

// FIX 1: ensureActive() — throws CancellationException if cancelled
suspend fun processItems(items: List<Item>) = withContext(Dispatchers.Default) {
    for (item in items) {
        ensureActive() // Cooperative cancellation check
        heavyComputation(item)
    }
}

// FIX 2: yield() — also checks cancellation AND gives other coroutines a chance to run
suspend fun processItems(items: List<Item>) = withContext(Dispatchers.Default) {
    for (item in items) {
        yield() // Cancellation-aware + fair scheduling
        heavyComputation(item)
    }
}

// FIX 3: isActive check (for conditional logic)
suspend fun processItems(items: List<Item>) = withContext(Dispatchers.Default) {
    for (item in items) {
        if (!isActive) break // Graceful exit instead of exception
        heavyComputation(item)
    }
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q5</span>What happens if you use <code>Dispatchers.IO</code> for CPU-intensive work? What is the correct dispatcher?</div>
      <div class="qa-answer">
        <p><strong>Dispatchers.IO</strong> is designed for I/O-bound work: it has a large thread pool (up to 64 threads or CPU cores × 2) because I/O threads spend most of their time <em>waiting</em> (for network packets, disk reads) — having many threads ensures they don't idle.</p>
        <p><strong>Dispatchers.Default</strong> is for CPU-bound work: it has exactly <code>Runtime.getRuntime().availableProcessors()</code> threads (minimum 2) because CPU work actively uses processor time — having more threads than CPUs just causes context-switching overhead.</p>
        <p>If you use Dispatchers.IO for CPU work: you create unnecessary thread contention with legitimate I/O work, and you may saturate the shared thread pool causing I/O operations to wait for threads. If you use Dispatchers.Default for I/O: threads block waiting for I/O, starving the small pool and causing all coroutines to queue up.</p>
        <pre class="code-block"><code class="language-kotlin">// Correct pattern:
suspend fun processData(rawData: ByteArray): Report {
    // CPU-intensive: JSON parsing, sorting, filtering
    val parsed = withContext(Dispatchers.Default) {
        heavyJsonParsing(rawData)
    }
    // I/O: save to database, upload to server
    val saved = withContext(Dispatchers.IO) {
        database.insert(parsed)
        api.uploadReport(parsed)
    }
    return saved
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>Why should you never catch <code>CancellationException</code> without re-throwing it?</div>
      <div class="qa-answer">
        <p>CancellationException is the mechanism Kotlin Coroutines uses to propagate cancellation through the coroutine hierarchy. When a scope is cancelled, the framework throws CancellationException at each active coroutine's suspension point. If you catch and swallow this exception, the coroutine continues running as if nothing happened — breaking structured concurrency guarantees.</p>
        <pre class="code-block"><code class="language-kotlin">// WRONG — breaks structured concurrency:
viewModelScope.launch {
    try {
        repository.fetchData()
    } catch (e: Exception) { // Catches CancellationException too!
        Timber.e(e) // Logs it and continues — coroutine doesn't stop!
    }
}

// CORRECT — re-throw CancellationException:
viewModelScope.launch {
    try {
        repository.fetchData()
    } catch (e: CancellationException) {
        throw e // Must propagate — this is how cancellation works
    } catch (e: IOException) {
        _state.value = UiState.Error(e.message)
    }
}

// CORRECT with runCatching:
val result = runCatching { repository.fetchData() }
result.onFailure { e ->
    if (e is CancellationException) throw e // Re-throw!
    _state.value = UiState.Error(e.message)
}</code></pre>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge</h3>
    <p><strong>Problem:</strong> Implement a retry mechanism with exponential backoff for a network call, with a maximum of 3 attempts, a 10-second overall timeout, and proper cancellation handling. The function should return null if all retries fail or timeout occurs.</p>
    <pre class="code-block"><code class="language-kotlin">// Solution: Retry with Exponential Backoff + Timeout + Cancellation

suspend fun <T> retryWithBackoff(
    maxAttempts: Int = 3,
    initialDelayMs: Long = 500L,
    maxDelayMs: Long = 5_000L,
    timeoutMs: Long = 10_000L,
    block: suspend () -> T
): T? {
    return withTimeoutOrNull(timeoutMs) {
        var currentDelay = initialDelayMs
        var lastException: Exception? = null

        repeat(maxAttempts) { attempt ->
            try {
                return@withTimeoutOrNull block() // Success — return immediately
            } catch (e: CancellationException) {
                throw e // CRITICAL: never swallow CancellationException!
            } catch (e: Exception) {
                lastException = e
                Timber.w("Attempt ${attempt + 1}/$maxAttempts failed: ${e.message}")

                if (attempt < maxAttempts - 1) {
                    delay(currentDelay) // Suspend (cancellable!) — not Thread.sleep
                    currentDelay = minOf(currentDelay * 2, maxDelayMs) // Exponential backoff
                }
            }
        }
        Timber.e("All $maxAttempts attempts failed. Last error: ${lastException?.message}")
        null // withTimeoutOrNull returns null on failure
    }
}

// Usage in ViewModel:
fun loadUserData(userId: String) {
    viewModelScope.launch {
        _state.value = UiState.Loading

        val user = retryWithBackoff(
            maxAttempts = 3,
            initialDelayMs = 500L,
            timeoutMs = 10_000L
        ) {
            userRepository.fetchUser(userId) // Your suspend function
        }

        _state.value = if (user != null) {
            UiState.Success(user)
        } else {
            UiState.Error("Failed to load user after retries")
        }
    }
}

// Advanced version with specific retryable exceptions:
suspend fun <T> retryOnNetworkError(
    maxAttempts: Int = 3,
    block: suspend () -> T
): T? {
    var attempt = 0
    var delay = 1_000L
    while (attempt < maxAttempts) {
        try {
            return block()
        } catch (e: CancellationException) { throw e }
        catch (e: IOException) { /* Network error — retry */ }
        catch (e: HttpException) {
            if (e.code() in 500..599) { /* Server error — retry */ }
            else throw e // Client error (4xx) — don't retry
        }
        attempt++
        if (attempt < maxAttempts) {
            delay(delay)
            delay = minOf(delay * 2, 30_000L)
        }
    }
    return null
}

// Time Complexity: O(maxAttempts) network calls, O(1) memory
// Key Decisions:
// 1. withTimeoutOrNull gives overall time budget without exception-based flow
// 2. delay() is coroutine-friendly (suspends, not blocks; cancellable)
// 3. CancellationException always re-thrown — structured concurrency requirement
// 4. Exponential backoff with cap prevents thundering herd on server recovery</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="14" data-item="0"> ✅ Understood Why &amp; What</label>
    <label class="progress-check"><input type="checkbox" data-topic="14" data-item="1"> ✅ Can explain How it works internally</label>
    <label class="progress-check"><input type="checkbox" data-topic="14" data-item="2"> ✅ Reviewed Common Mistakes</label>
    <label class="progress-check"><input type="checkbox" data-topic="14" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="14" data-item="4"> ✅ Solved Coding Challenge</label>
  </div>
</section>

<!-- ============================================================ -->
<!--  TOPIC 15: Kotlin Flow                                       -->
<!-- ============================================================ -->
<section class="topic-section" id="topic-15">
  <div class="topic-header">
    <div class="topic-header-icon">🌊</div>
    <div class="topic-header-text">
      <h1>Kotlin Flow</h1>
      <p class="topic-tagline">Reactive streams done right — StateFlow, SharedFlow, operators, backpressure, and lifecycle-safe collection</p>
      <div class="category-badge-group">
        <span class="cat-pill">Flow</span>
        <span class="cat-pill">StateFlow</span>
        <span class="cat-pill">SharedFlow</span>
        <span class="cat-pill">Operators</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 15-1: Cold vs Hot Flows -->
  <div class="subtopic" id="subtopic-15-1">
    <h2>Cold Flows vs Hot Flows (StateFlow &amp; SharedFlow)</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Modern Android apps are fundamentally reactive: the UI should automatically update when data changes in the database, network, or user input. LiveData was Android's first answer, but it's lifecycle-aware only in the View layer and has limited operators. RxJava provides rich operators but has enormous API surface and painful threading model.</p>
      <p>Kotlin Flow builds on coroutines to give you a type-safe, backpressure-aware, suspendable reactive stream with the full power of Kotlin operators. You need to understand Cold vs Hot because choosing wrong means either executing database queries on every rotation (cold when you want hot) or missing events from one-shot actions like navigation (hot when you want cold).</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p><strong>Cold Flow (<code>Flow&lt;T&gt;</code>):</strong> The flow's code block runs fresh for each collector. Like a YouTube video — each viewer starts from the beginning. Nothing runs until someone collects. All operators are lazy. Used for database queries, network calls, computed values where each collector gets its own independent execution.</p>
      <p><strong>Hot Flow:</strong> Produces values independently of collectors. Like a live TV broadcast — you see what's airing now, not from the beginning.</p>
      <ul>
        <li><strong>StateFlow:</strong> Always has a value (current state), replays the latest value to new collectors, conflates rapid updates (only delivers the latest to slow collectors). Equivalent to LiveData. Use for UI state.</li>
        <li><strong>SharedFlow:</strong> More general. Configurable replay cache, configurable buffer, can emit to multiple collectors simultaneously. Use for events (navigation, one-time actions) where you want guaranteed delivery.</li>
      </ul>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <p>A cold <code>Flow</code> is defined with the <code>flow { }</code> builder. The lambda is the producer block — it only runs when a terminal operator (like <code>collect</code>) is called. Each collector creates a new instance of the producer block. The Kotlin Flow runtime implements backpressure by using coroutines: the producer suspends at <code>emit()</code> if the collector hasn't processed the previous value yet.</p>
      <p><code>StateFlow</code> is backed by a <code>MutableStateFlow</code> which internally uses a lock-free compare-and-set to update its value. New values are conflated — if you call <code>.value = x</code> multiple times before collectors can process, they only see the latest value. <code>SharedFlow</code> has a configurable <code>replay</code> cache and buffer — it can buffer up to <code>extraBufferCapacity</code> items before suspending the producer.</p>
      <pre class="code-block"><code class="language-kotlin">// Cold Flow — new execution per collector
fun getTransactionUpdates(accountId: String): Flow<List<Transaction>> = flow {
    // This block runs fresh for EACH collector
    while (true) {
        val transactions = database.getTransactions(accountId) // Suspends
        emit(transactions) // Suspends if collector is slow
        delay(30_000L) // Poll every 30 seconds
    }
}

// StateFlow — hot, always has value, conflated
class AccountViewModel : ViewModel() {
    // MutableStateFlow is the writable version; expose immutable StateFlow
    private val _balance = MutableStateFlow<BalanceState>(BalanceState.Loading)
    val balance: StateFlow<BalanceState> = _balance.asStateFlow()

    // SharedFlow — for one-shot events (no replay by default)
    private val _events = MutableSharedFlow<AccountEvent>(
        replay = 0,                              // No replay for new collectors
        extraBufferCapacity = 1,                  // Buffer 1 event if collector slow
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val events: SharedFlow<AccountEvent> = _events.asSharedFlow()

    fun refreshBalance(accountId: String) {
        viewModelScope.launch {
            _balance.value = BalanceState.Loading
            runCatching { api.fetchBalance(accountId) }
                .onSuccess { _balance.value = BalanceState.Success(it) }
                .onFailure { e ->
                    if (e is CancellationException) throw e
                    _balance.value = BalanceState.Error(e.message ?: "Error")
                }
        }
    }

    fun onTransactionTapped(id: String) {
        viewModelScope.launch {
            _events.emit(AccountEvent.NavigateToDetail(id))
        }
    }
}

// In Fragment — lifecycle-safe collection
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        launch { viewModel.balance.collect { renderBalance(it) } }
        launch { viewModel.events.collect { handleEvent(it) } }
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// Cold Flow creation:
val coldFlow: Flow<Int> = flow { emit(1); emit(2) }
val flowOfValues = flowOf(1, 2, 3)          // Fixed values
val rangeFlow = (1..10).asFlow()             // From range

// StateFlow:
val stateFlow = MutableStateFlow(initialValue)
stateFlow.value = newValue                   // Synchronous update (safe from any thread)
stateFlow.update { it.copy(field = value) }  // Atomic update
stateFlow.value                              // Always non-null current value

// SharedFlow:
val sharedFlow = MutableSharedFlow<Event>(replay = 1, extraBufferCapacity = 10)
sharedFlow.emit(event)                       // Suspends if buffer full
sharedFlow.tryEmit(event)                    // Returns false if buffer full (non-suspend)

// Terminal operators (trigger collection):
flow.collect { value -> }                    // Basic collect
flow.first()                                 // Collect first, then cancel
flow.toList()                                // Collect all into list
flow.launchIn(scope)                         // Collect in given scope (returns Job)

// Transformations (intermediate, lazy):
flow.map { it * 2 }
flow.filter { it > 0 }
flow.flatMapLatest { query -> searchFlow(query) }  // Cancel previous inner flow
flow.debounce(300)                           // Only emit after 300ms of silence
flow.distinctUntilChanged()                  // Skip duplicate consecutive values
flow.take(5)                                 // Take first 5 emissions

// Combining flows:
combine(flow1, flow2) { a, b -> Pair(a, b) } // Emit on EITHER update (latest values)
zip(flow1, flow2) { a, b -> Pair(a, b) }     // Pair by position (waits for both)
merge(flow1, flow2)                           // Interleave emissions from both</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example</h3>
      <p><strong>E-Commerce — Search with debounce, flatMapLatest, and combine:</strong> A product search that debounces user input (avoids API call per keystroke), cancels in-flight searches on new input, and combines results with saved favorites from Room database.</p>
      <pre class="code-block"><code class="language-kotlin">class SearchViewModel @Inject constructor(
    private val productRepository: ProductRepository,
    private val favoritesRepository: FavoritesRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    // Core search pipeline:
    val searchResults: StateFlow<SearchUiState> = _searchQuery
        .debounce(300L)                   // Wait 300ms after user stops typing
        .distinctUntilChanged()            // Skip if query hasn't changed
        .filter { it.length >= 2 }         // Don't search for 1-char queries
        .flatMapLatest { query ->          // Cancel previous search on new query!
            productRepository.searchProducts(query) // Returns Flow<List<Product>>
                .map<List<Product>, SearchUiState> { SearchUiState.Success(it) }
                .catch { e -> emit(SearchUiState.Error(e.message ?: "Search failed")) }
                .onStart { emit(SearchUiState.Loading) }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000L), // Keep alive 5s after last subscriber
            initialValue = SearchUiState.Idle
        )

    // Combine search results with favorites for enriched display
    val enrichedResults: StateFlow<List<ProductDisplayItem>> = combine(
        searchResults,
        favoritesRepository.getFavoriteIds() // Flow<Set<String>> from Room
    ) { searchState, favoriteIds ->
        when (searchState) {
            is SearchUiState.Success -> searchState.products.map { product ->
                ProductDisplayItem(product, isFavorite = product.id in favoriteIds)
            }
            else -> emptyList()
        }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000L), emptyList())

    fun onQueryChanged(query: String) {
        _searchQuery.value = query
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Using <code>lifecycleScope.launch { flow.collect {} }</code> without repeatOnLifecycle:</strong> The collection continues even when the app is in background, processing updates to invisible UI and wasting resources — ✅ Fix: Always use <code>repeatOnLifecycle(Lifecycle.State.STARTED)</code> to auto-pause collection in background.</li>
        <li>❌ <strong>Using StateFlow for one-shot events (navigation):</strong> New collectors replay the last value — navigating back then re-collecting triggers navigation again — ✅ Fix: Use SharedFlow(replay=0) for events.</li>
        <li>❌ <strong>Using <code>collect</code> where <code>collectLatest</code> is needed:</strong> In search, if collect is processing a previous result when a new emission arrives, it queues up — flatMapLatest + collect is the correct pattern for cancelling outdated work — ✅ Fix: Use flatMapLatest for cancellable inner flows.</li>
        <li>❌ <strong>Not using stateIn / shareIn for upstream cold flows:</strong> Each subscriber to a cold flow triggers a new database query or network call — ✅ Fix: Use stateIn() or shareIn() to multicast a single upstream to multiple subscribers.</li>
        <li>❌ <strong>Calling <code>flow.first()</code> where the flow never emits:</strong> Suspends forever — ✅ Fix: Use <code>flow.firstOrNull()</code> or add a timeout with <code>withTimeoutOrNull</code>.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"I think of Flow in terms of three categories: cold flows for data sources (Room DAO queries, network calls wrapped in flow{}), StateFlow for UI state that always needs a current value, and SharedFlow for events that must be delivered exactly once. The key architectural decision is the ViewModel boundary: ViewModels expose StateFlow (not MutableStateFlow) so the View layer can only observe. For lifecycle-safe collection in fragments, I always use repeatOnLifecycle(STARTED) — never a bare lifecycleScope launch — so background processing stops when the app is backgrounded. For complex pipelines, I leverage stateIn() with SharingStarted.WhileSubscribed(5000) which keeps the upstream alive for 5 seconds after the last subscriber leaves — perfect for surviving configuration changes without restarting network calls. The combine operator is my go-to for merging multiple independent data streams, and flatMapLatest is the key to implementing search correctly."</p>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 15-2: Flow Operators & collect vs collectLatest -->
  <div class="subtopic" id="subtopic-15-2">
    <h2>Flow Operators &amp; collect vs collectLatest</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Raw <code>collect</code> processes every emission sequentially — if your UI takes 500ms to render an item, and new items arrive every 100ms, your UI is always 400ms behind reality and may crash trying to render stale data. Flow operators let you transform, filter, flatten, and rate-limit streams declaratively without writing complex threading logic. Understanding the difference between <code>collect</code>, <code>collectLatest</code>, and <code>flatMapLatest</code> is a senior-level signal — it shows you understand backpressure and cancellation as first-class concerns.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p><strong>collect:</strong> Suspends the caller for each emission, processes it sequentially. If the collector is slow, the producer suspends (backpressure). Every emission is processed.</p>
      <p><strong>collectLatest:</strong> When a new emission arrives, the current collector block is <em>cancelled</em> and restarted with the new value. The previous collector block's work is discarded. Use when only the latest value matters and processing old values is wasted work.</p>
      <p><strong>Key Operators:</strong> map, filter, transform, flatMapConcat (sequential), flatMapMerge (concurrent), flatMapLatest (cancel-on-new), debounce, sample, buffer, conflate, zip, combine, merge, onStart, catch, onCompletion.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// collect vs collectLatest demonstration:
val tickerFlow = flow {
    var i = 0
    while (true) {
        emit(i++)
        delay(100) // Emits every 100ms
    }
}

// collect — processes every item (producer suspends if collector is slow)
scope.launch {
    tickerFlow.collect { value ->
        delay(200) // Collector takes 200ms — backpressure applied, misses nothing
        Timber.d("Collected: $value") // Sees: 0, 1, 2, 3... but delayed
    }
}

// collectLatest — cancels previous collector on new emission
scope.launch {
    tickerFlow.collectLatest { value ->
        delay(200) // But new value arrives after 100ms — this gets cancelled!
        Timber.d("Latest: $value") // Only sees values that "survive" 200ms quiet period
    }
}

// buffer — decouple producer and consumer speeds
tickerFlow
    .buffer(capacity = 10) // Producer runs ahead by up to 10 items
    .collect { value ->
        delay(200) // Consumer slow but buffer absorbs bursts
        process(value)
    }

// conflate — keep only the latest, drop intermediate values
tickerFlow
    .conflate() // Like StateFlow — only latest value, no buffer buildup
    .collect { process(it) }

// flatMapLatest — for search: cancel previous result fetch on new query
val queryFlow: Flow<String> = searchField.textChanges().map { it.toString() }
val results = queryFlow
    .debounce(300)
    .flatMapLatest { query ->
        // Previous inner flow is cancelled when new query arrives
        productApi.search(query)
            .catch { emit(emptyList()) }
    }

// combine vs zip:
val pricesFlow: Flow<Map<String, Double>> = stockApi.getPrices()
val holdingsFlow: Flow<Map<String, Int>> = portfolioDb.getHoldings()

// combine — emits whenever EITHER upstream updates (uses latest of each)
combine(pricesFlow, holdingsFlow) { prices, holdings ->
    holdings.mapValues { (ticker, qty) -> (prices[ticker] ?: 0.0) * qty }
}.collect { portfolioValues -> updatePortfolioDisplay(portfolioValues) }

// zip — pairs emissions by index, waits for both, shorter stream wins
val stream1 = flowOf("A", "B", "C")
val stream2 = flowOf(1, 2)
stream1.zip(stream2) { letter, number -> "$letter$number" }
    .collect { println(it) } // Prints: A1, B2 (C is dropped — stream2 ends)</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// Flattening operators (for flows-of-flows):
// flatMapConcat: inner flows collected sequentially (one at a time)
// flatMapMerge:  inner flows collected concurrently (limited by concurrency param)
// flatMapLatest: new emission cancels previous inner flow

flow.flatMapConcat { id -> fetchDetails(id) }   // Order preserved
flow.flatMapMerge(concurrency = 4) { id -> fetchDetails(id) } // 4 concurrent fetches
flow.flatMapLatest { query -> searchApi(query) } // Cancel stale searches

// Error handling in flows:
flow
    .catch { e -> emit(fallbackValue) }         // Handle error, continue
    .onCompletion { cause -> cleanup() }         // Always runs (like finally)
    .retry(3) { e -> e is IOException }          // Retry on specific exceptions
    .retryWhen { cause, attempt ->               // Retry with backoff
        if (cause is IOException && attempt < 3) {
            delay(1_000L * (attempt + 1))
            true  // Retry
        } else false // Don't retry
    }

// Converting to hot flows:
val coldFlow: Flow<Data> = repository.getData()

// stateIn: converts cold flow to StateFlow
val stateFlow: StateFlow<Data> = coldFlow.stateIn(
    scope = viewModelScope,
    started = SharingStarted.WhileSubscribed(5_000L),
    initialValue = Data.Loading
)

// shareIn: converts cold flow to SharedFlow
val sharedFlow: SharedFlow<Data> = coldFlow.shareIn(
    scope = viewModelScope,
    started = SharingStarted.WhileSubscribed(5_000L),
    replay = 1
)

// SharingStarted strategies:
// Eagerly: starts immediately, never stops
// Lazily: starts on first subscriber, never stops
// WhileSubscribed(stopTimeout): starts on first subscriber, stops 5s after last leaves</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example</h3>
      <p><strong>Automotive — Real-time Vehicle Telemetry:</strong> A vehicle dashboard app receives telemetry data (speed, RPM, fuel) at 10Hz from a BLE sensor. The UI renders at 60fps. We need to conflate telemetry bursts, combine with trip data from Room, and detect anomalies.</p>
      <pre class="code-block"><code class="language-kotlin">class VehicleDashboardViewModel @Inject constructor(
    private val bleService: VehicleBleService,
    private val tripRepository: TripRepository
) : ViewModel() {

    // Raw telemetry at 10Hz — conflate so UI only gets latest
    private val telemetryFlow: Flow<VehicleTelemetry> = bleService
        .telemetryStream()        // Emits 10 times per second
        .conflate()               // Drop intermediate values if UI is busy
        .flowOn(Dispatchers.IO)   // Decode BLE packets on IO thread

    // Trip data from Room
    private val activeTripFlow: Flow<TripData?> = tripRepository
        .getActiveTrip()
        .distinctUntilChanged()

    // Combined display state
    val dashboardState: StateFlow<DashboardState> = combine(
        telemetryFlow,
        activeTripFlow
    ) { telemetry, trip ->
        DashboardState(
            speedKmh      = telemetry.speedKmh,
            rpm           = telemetry.rpm,
            fuelLevel     = telemetry.fuelPercent,
            tripDistance  = trip?.distanceKm ?: 0.0,
            isAnomaly     = telemetry.rpm > 7000 || telemetry.oilTemp > 130
        )
    }
    .onEach { state ->
        if (state.isAnomaly) {
            notificationManager.sendAnomalyAlert(state)
        }
    }
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000L),
        initialValue = DashboardState.initial()
    )
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Using flatMapMerge without concurrency limit:</strong> If the upstream emits rapidly, you spawn thousands of concurrent coroutines — ✅ Fix: Always specify <code>concurrency</code> parameter: <code>flatMapMerge(concurrency = 4)</code>.</li>
        <li>❌ <strong>Using zip when you need combine:</strong> zip waits for both streams to emit a new value before producing — if one stream is slow, zip stalls — ✅ Fix: Use combine when you want the latest from each stream on every update.</li>
        <li>❌ <strong>Applying flowOn in the wrong place:</strong> flowOn only affects operators UPSTREAM of it, not downstream — ✅ Fix: Place flowOn immediately after the operators you want to run on that thread.</li>
        <li>❌ <strong>Not using catch before stateIn:</strong> An exception in the upstream flow will cancel the StateFlow entirely — ✅ Fix: Add .catch { emit(errorState) } before .stateIn().</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"The collect vs collectLatest distinction is about backpressure strategy. collect gives you every emission — the producer suspends if the collector is slow, implementing natural backpressure. collectLatest cancels previous processing when new data arrives — ideal for search results where old results are immediately outdated. For flows-of-flows (a query that produces a results flow), I use flatMapLatest almost exclusively because it correctly cancels in-flight requests when the input changes. For rate-limiting, I reach for conflate when I only need the latest value (telemetry, UI updates) and buffer when I need burst absorption. The combine operator is how I implement the unidirectional data flow pattern — multiple upstream sources (database, network, user input) get combined into a single StateFlow that the UI observes. Using SharingStarted.WhileSubscribed(5000) on stateIn is a key optimization: the 5-second timeout means configuration changes don't restart the upstream, but a genuine background + resume restart does."</p>
      </div>
    </div>
  </div>

  <!-- Q&A for Topic 15 -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the difference between a cold Flow and a hot Flow? Give examples of each.</div>
      <div class="qa-answer">
        <p><strong>Cold Flow:</strong> The producer code runs fresh for each new collector. Nothing happens until someone collects. Two collectors get two independent executions.</p>
        <p><strong>Hot Flow:</strong> Produces values regardless of collectors. Multiple collectors share the same stream. Collectors joining late miss past values (unless replay is configured).</p>
        <pre class="code-block"><code class="language-kotlin">// Cold — each collect triggers a new network call!
val coldFlow: Flow<Weather> = flow {
    val weather = api.fetchWeather() // Runs per collector
    emit(weather)
}
coldFlow.collect { /* network call 1 */ }
coldFlow.collect { /* network call 2 — separate! */ }

// Hot — StateFlow: one value, shared by all collectors
val weatherState = MutableStateFlow<Weather?>(null)
viewModelScope.launch { weatherState.value = api.fetchWeather() } // Fetched once
weatherState.collect { /* same data */ }
weatherState.collect { /* same data — no extra network call */ }

// Converting cold to hot:
val hotWeather: StateFlow<Weather?> = flow { emit(api.fetchWeather()) }
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null)</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q2</span>When should you use <code>SharedFlow</code> vs <code>StateFlow</code> for events in a ViewModel?</div>
      <div class="qa-answer">
        <p><strong>StateFlow:</strong> Replays the latest value to new collectors. Suitable for <em>state</em> — data that represents the current condition. If you use StateFlow for navigation events, rotating the screen will re-trigger the navigation because the new collector gets the last value.</p>
        <p><strong>SharedFlow(replay=0):</strong> No replay. Events are only delivered to currently active collectors. Use for one-shot events: navigation, Snackbar messages, dialogs.</p>
        <pre class="code-block"><code class="language-kotlin">// StateFlow for UI state (correct):
private val _uiState = MutableStateFlow<LoginState>(LoginState.Idle)
val uiState: StateFlow<LoginState> = _uiState.asStateFlow()

// SharedFlow for events (correct — no replay):
private val _events = MutableSharedFlow<LoginEvent>(replay = 0, extraBufferCapacity = 1)
val events: SharedFlow<LoginEvent> = _events.asSharedFlow()

fun onLoginSuccess(token: String) {
    _uiState.value = LoginState.Success(token)      // Persists for new collectors
    viewModelScope.launch {
        _events.emit(LoginEvent.NavigateToDashboard) // Delivered once, not replayed
    }
}

// WRONG — StateFlow for navigation event causes re-navigation on rotation:
private val _navigateEvent = MutableStateFlow<String?>(null)
// New collector after rotation gets "navigate" again! Use SharedFlow instead.</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>What does <code>SharingStarted.WhileSubscribed(5000)</code> do and why is it preferred?</div>
      <div class="qa-answer">
        <p><code>SharingStarted.WhileSubscribed(stopTimeoutMillis)</code> controls when the upstream flow starts and stops:</p>
        <ul>
          <li><strong>Starts</strong> when the first subscriber collects.</li>
          <li><strong>Stops</strong> N milliseconds after the <em>last</em> subscriber leaves.</li>
        </ul>
        <p><strong>Why 5000ms?</strong> Configuration changes (rotation) destroy and recreate the Fragment/Activity. The View unsubscribes during destruction (~100ms), then re-subscribes after creation. With a 5-second window, the upstream is kept alive across this brief gap — so no redundant network/database calls happen on rotation. But if the user genuinely backgrounds the app and comes back after 6+ seconds, the upstream restarts and fetches fresh data.</p>
        <pre class="code-block"><code class="language-kotlin">val data: StateFlow<Data> = repository.getData()
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000L), // Keep alive 5s
        initialValue = Data.Loading
    )

// Comparison:
// SharingStarted.Eagerly:    starts immediately, never stops (use for critical data)
// SharingStarted.Lazily:     starts on first subscriber, never stops (memory concern)
// SharingStarted.WhileSubscribed(5000): lifecycle-aware, no waste (recommended)</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q4</span>Explain the difference between <code>combine</code>, <code>zip</code>, and <code>merge</code> with a use case for each.</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">// combine: emits when EITHER upstream updates, using latest value of each
// Use case: stock portfolio (price updates constantly, holdings change rarely)
combine(priceFlow, holdingsFlow) { prices, holdings ->
    holdings.mapValues { (ticker, qty) -> prices[ticker]!! * qty }
}.collect { renderPortfolio(it) }
// If price updates 100x/sec, emits 100x/sec with same holdings value

// zip: pairs emissions positionally, waits for both to have a new value
// Use case: compare two paginated lists item by item
zip(expectedResultsFlow, actualResultsFlow) { expected, actual ->
    TestResult(expected, actual, passed = expected == actual)
}.collect { showTestResult(it) }
// Only emits when BOTH have a new value; slower stream controls pace

// merge: interleave emissions from multiple flows, no pairing
// Use case: aggregate events from multiple sources into one stream
merge(bleEventsFlow, wifiEventsFlow, gpsEventsFlow)
    .collect { event -> processAnyEvent(event) }
// Emits from whichever source fires, in arrival order</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q5</span>How does backpressure work in Kotlin Flow? How does it compare to RxJava?</div>
      <div class="qa-answer">
        <p>Kotlin Flow handles backpressure natively through coroutine suspension. When the producer calls <code>emit(value)</code>, if the consumer hasn't processed the previous value, the <code>emit</code> call <em>suspends</em> the producer coroutine — the producer thread is freed (no thread blocking) until the consumer is ready. This is built into the language with zero boilerplate.</p>
        <p><strong>Control strategies:</strong></p>
        <ul>
          <li><strong>Default (suspension):</strong> Producer suspends until consumer ready — lossless, natural backpressure.</li>
          <li><strong>buffer():</strong> Add a buffer between producer and consumer — producer can run ahead by buffer size before suspending.</li>
          <li><strong>conflate():</strong> Producer never suspends; consumer only gets the latest value (intermediate values dropped).</li>
          <li><strong>collectLatest:</strong> Consumer cancels its current work when new value arrives.</li>
        </ul>
        <p>In RxJava, backpressure requires explicit <code>Flowable</code> type and explicit <code>BackpressureStrategy</code> (BUFFER, DROP, LATEST, ERROR). Getting it wrong causes <code>MissingBackpressureException</code> — a runtime exception. Flow makes the correct behavior the default.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>Why is <code>lifecycleScope.launch { flow.collect {} }</code> considered wrong for Fragment UI collection, and what is the correct approach?</div>
      <div class="qa-answer">
        <p>The problem: <code>lifecycleScope</code> is scoped to the Fragment's lifecycle — it's cancelled only when the Fragment is <em>destroyed</em>. When the app is backgrounded, the Fragment is STOPPED but not destroyed. The coroutine is still running and collecting! This means:</p>
        <ul>
          <li>UI updates are delivered to a stopped Fragment (views may be null in some patterns).</li>
          <li>Heavy processing (network, DB) continues in the background unnecessarily.</li>
          <li>Battery drain and potential crashes.</li>
        </ul>
        <pre class="code-block"><code class="language-kotlin">// WRONG — collects even in background:
viewLifecycleOwner.lifecycleScope.launch {
    viewModel.data.collect { updateUi(it) } // Runs when app backgrounded!
}

// CORRECT — repeatOnLifecycle suspends when below STARTED:
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.data.collect { updateUi(it) }
        // Automatically paused when Fragment STOPs (backgrounded)
        // Automatically resumed when Fragment STARTs (foregrounded)
    }
}

// Multiple flows — use separate launches inside repeatOnLifecycle:
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        launch { viewModel.state.collect { renderState(it) } }
        launch { viewModel.events.collect { handleEvent(it) } }
    }
}</code></pre>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge</h3>
    <p><strong>Problem:</strong> Implement a type-ahead search feature with the following requirements: debounce 300ms, minimum 2 characters, cancel previous search on new input, handle errors gracefully without crashing the flow, combine results with a locally cached favorites list, and expose as a single StateFlow. Write the complete ViewModel.</p>
    <pre class="code-block"><code class="language-kotlin">// Complete Type-Ahead Search ViewModel

data class SearchUiState(
    val isLoading: Boolean = false,
    val results: List<ProductItem> = emptyList(),
    val error: String? = null,
    val query: String = ""
)

data class ProductItem(
    val id: String,
    val name: String,
    val price: Double,
    val isFavorite: Boolean = false
)

class TypeAheadSearchViewModel @Inject constructor(
    private val productRepository: ProductRepository,
    private val favoritesRepository: FavoritesRepository
) : ViewModel() {

    // Mutable query state — driven by user input
    private val _query = MutableStateFlow("")

    // Expose for UI to bind text changes
    val query: StateFlow<String> = _query.asStateFlow()

    // Favorites from local Room DB — cold Flow, will be shared below
    private val favoritesFlow: Flow<Set<String>> = favoritesRepository
        .getFavoriteProductIds()        // Returns Flow<Set<String>>
        .distinctUntilChanged()
        .catch { emit(emptySet()) }     // Favorites failure shouldn't break search

    // Search results pipeline
    private val searchResultsFlow: Flow<Pair<Boolean, List<ProductItem>>> =
        _query
            .debounce(300L)             // Wait 300ms after user stops typing
            .map { it.trim() }
            .distinctUntilChanged()     // Don't re-search same trimmed query
            .flatMapLatest { query ->   // Cancel previous search on new query
                if (query.length < 2) {
                    flowOf(Pair(false, emptyList())) // Below minimum — return empty
                } else {
                    productRepository.searchProducts(query)
                        .map { products -> Pair(false, products) }
                        .onStart { emit(Pair(true, emptyList())) } // Loading state
                        .catch { e ->
                            // Errors caught here don't cancel the outer flow
                            emit(Pair(false, emptyList())) // Graceful fallback
                        }
                }
            }

    // Combine search results with favorites — single source of truth for UI
    val uiState: StateFlow<SearchUiState> = combine(
        _query,
        searchResultsFlow,
        favoritesFlow
    ) { currentQuery, (isLoading, products), favorites ->
        SearchUiState(
            isLoading = isLoading,
            results   = products.map { it.copy(isFavorite = it.id in favorites) },
            error     = null,
            query     = currentQuery
        )
    }
    .catch { e ->
        // Top-level catch — prevents StateFlow from being cancelled on error
        emit(SearchUiState(error = e.message ?: "Search failed"))
    }
    .stateIn(
        scope   = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000L),
        initialValue = SearchUiState()
    )

    fun onQueryChanged(newQuery: String) {
        _query.value = newQuery
    }

    fun onFavoriteToggled(productId: String) {
        viewModelScope.launch {
            favoritesRepository.toggleFavorite(productId)
            // Room DB update automatically emits new value through favoritesFlow
            // combine operator picks it up and updates uiState automatically
        }
    }
}

// In Fragment:
class SearchFragment : Fragment(R.layout.fragment_search) {
    private val viewModel: TypeAheadSearchViewModel by viewModels()
    private var _binding: FragmentSearchBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentSearchBinding.bind(view)

        // Bind user input to ViewModel
        binding.searchField.addTextChangedListener { editable ->
            viewModel.onQueryChanged(editable.toString())
        }

        // Lifecycle-safe collection with repeatOnLifecycle
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    binding.progressBar.isVisible = state.isLoading
                    binding.errorText.isVisible   = state.error != null
                    binding.errorText.text         = state.error
                    searchAdapter.submitList(state.results)
                }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

// Key Design Decisions:
// 1. flatMapLatest: cancels in-flight search when query changes (no stale results)
// 2. debounce(300): avoids API call on every keystroke
// 3. combine: declarative merge of query + search + favorites = single UI state
// 4. catch at each level: favorites failure doesn't break search; search error is graceful
// 5. stateIn with WhileSubscribed(5000): no duplicate fetches on rotation
// 6. repeatOnLifecycle(STARTED): no background processing</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="15" data-item="0"> ✅ Understood Why &amp; What</label>
    <label class="progress-check"><input type="checkbox" data-topic="15" data-item="1"> ✅ Can explain How it works internally</label>
    <label class="progress-check"><input type="checkbox" data-topic="15" data-item="2"> ✅ Reviewed Common Mistakes</label>
    <label class="progress-check"><input type="checkbox" data-topic="15" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="15" data-item="4"> ✅ Solved Coding Challenge</label>
  </div>
</section>

<!-- ============================================================ -->
<!--  TOPIC 16: Android Architecture                              -->
<!-- ============================================================ -->
<section class="topic-section" id="topic-16">
  <div class="topic-header">
    <div class="topic-header-icon">🏛️</div>
    <div class="topic-header-text">
      <h1>Android Architecture</h1>
      <p class="topic-tagline">MVC → MVP → MVVM → MVI → Clean Architecture — understanding WHY each evolved and HOW to apply them</p>
      <div class="category-badge-group">
        <span class="cat-pill">MVVM</span>
        <span class="cat-pill">MVI</span>
        <span class="cat-pill">Clean Architecture</span>
        <span class="cat-pill">UDF</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 16-1: Architecture Evolution -->
  <div class="subtopic" id="subtopic-16-1">
    <h2>Architecture Evolution: MVC → MVP → MVVM → MVI</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Without a clear architecture, Android apps become "God Activity" codebases: a single Activity class with 2000+ lines that handles UI events, makes network calls, writes to database, formats data, and manages navigation. This is untestable (can't unit test without starting a full Activity), unmaintainable (changing one feature breaks three others), and unscalable (every developer commits to the same giant class).</p>
      <p>Each architecture pattern exists because the previous one had a specific failure mode at scale. Understanding the evolution — not just memorizing pattern names — is the signal that separates senior engineers from junior ones in interviews.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <ul>
        <li><strong>MVC (Model-View-Controller):</strong> In Android, the Activity IS both View and Controller — they can't be separated. The Model is the data layer. Problem: tight coupling, untestable, View and Controller share the same class.</li>
        <li><strong>MVP (Model-View-Presenter):</strong> Presenter is a plain Kotlin class (testable!) that drives the View through an interface. Problem: boilerplate interface explosion, Presenter holds View reference (memory leak if not carefully managed), manual lifecycle management.</li>
        <li><strong>MVVM (Model-View-ViewModel):</strong> ViewModel exposes observable state (LiveData/StateFlow); View observes and renders. ViewModel has no View reference. Survives rotation. Google's recommended pattern with Jetpack. Problem: ViewModel can become "God ViewModel" with too many concerns; state management for complex UIs gets messy.</li>
        <li><strong>MVI (Model-View-Intent):</strong> Strict Unidirectional Data Flow. User generates Intents (events), Reducer processes Intents + current State → new State, View renders State. Single source of truth. Predictable, debuggable (state is a value you can log and replay). Problem: more boilerplate for simple screens; requires discipline.</li>
      </ul>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// MVP Pattern — interface-driven
interface LoginContract {
    interface View {
        fun showLoading()
        fun hideLoading()
        fun showError(message: String)
        fun navigateToDashboard()
    }
    interface Presenter {
        fun onLoginClicked(email: String, password: String)
        fun onViewDestroyed()
    }
}

class LoginPresenter(
    private var view: LoginContract.View?,
    private val authRepository: AuthRepository
) : LoginContract.Presenter {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    override fun onLoginClicked(email: String, password: String) {
        view?.showLoading()
        scope.launch {
            val result = runCatching { authRepository.login(email, password) }
            view?.hideLoading()
            result.fold(
                onSuccess = { view?.navigateToDashboard() },
                onFailure = { view?.showError(it.message ?: "Login failed") }
            )
        }
    }
    override fun onViewDestroyed() { view = null; scope.cancel() }
}

// ------------------------------------------------------------------
// MVVM Pattern — ViewModel with StateFlow (recommended)
sealed class LoginUiState {
    object Idle    : LoginUiState()
    object Loading : LoginUiState()
    data class Error(val message: String) : LoginUiState()
    object Success : LoginUiState()
}

class LoginViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<LoginUiState>(LoginUiState.Idle)
    val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()

    fun login(email: String, password: String) {
        viewModelScope.launch {
            _uiState.value = LoginUiState.Loading
            runCatching { authRepository.login(email, password) }
                .onSuccess { _uiState.value = LoginUiState.Success }
                .onFailure { e ->
                    if (e is CancellationException) throw e
                    _uiState.value = LoginUiState.Error(e.message ?: "Login failed")
                }
        }
    }
}

// ------------------------------------------------------------------
// MVI Pattern — Intent, State, Reducer
sealed class LoginIntent {
    data class Login(val email: String, val password: String) : LoginIntent()
    object ResetError : LoginIntent()
}

data class LoginState(
    val email: String = "",
    val password: String = "",
    val isLoading: Boolean = false,
    val error: String? = null,
    val isSuccess: Boolean = false
)

class LoginMviViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {
    private val _state = MutableStateFlow(LoginState())
    val state: StateFlow<LoginState> = _state.asStateFlow()

    fun processIntent(intent: LoginIntent) {
        when (intent) {
            is LoginIntent.Login      -> handleLogin(intent.email, intent.password)
            is LoginIntent.ResetError -> _state.update { it.copy(error = null) }
        }
    }

    private fun handleLogin(email: String, password: String) {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, error = null) }
            runCatching { authRepository.login(email, password) }
                .onSuccess { _state.update { it.copy(isLoading = false, isSuccess = true) } }
                .onFailure { e ->
                    if (e is CancellationException) throw e
                    _state.update { it.copy(isLoading = false, error = e.message) }
                }
        }
    }
}

// MVI View — single entry point for all interactions
class LoginFragment : Fragment() {
    private val viewModel: LoginMviViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // All user actions go through processIntent
        binding.loginButton.setOnClickListener {
            viewModel.processIntent(LoginIntent.Login(
                email    = binding.emailField.text.toString(),
                password = binding.passwordField.text.toString()
            ))
        }
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.state.collect { state -> render(state) }
            }
        }
    }

    private fun render(state: LoginState) {
        binding.progressBar.isVisible = state.isLoading
        binding.errorText.isVisible   = state.error != null
        binding.errorText.text         = state.error
        if (state.isSuccess) navigateToDashboard()
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// MVI State update patterns:
_state.update { currentState ->
    currentState.copy(isLoading = true) // Atomic, thread-safe update
}

// Sealed classes for Intent/Action modeling:
sealed class UiIntent {
    object LoadData                          : UiIntent()
    data class Search(val query: String)     : UiIntent()
    data class SelectItem(val id: String)    : UiIntent()
    object Refresh                           : UiIntent()
}

// Sealed class for State:
sealed class UiState {
    object Loading                           : UiState()
    data class Success(val data: DashData)   : UiState()
    data class Error(val msg: String)        : UiState()
}

// Or data class state (preferred for complex screens):
data class DashboardState(
    val isLoading: Boolean = false,
    val transactions: List<Transaction> = emptyList(),
    val balance: Double = 0.0,
    val selectedTab: Tab = Tab.ALL,
    val error: String? = null
)

// Reducer function (pure, testable):
fun reduce(state: DashboardState, intent: DashboardIntent): DashboardState {
    return when (intent) {
        is DashboardIntent.TabSelected   -> state.copy(selectedTab = intent.tab)
        is DashboardIntent.DataLoaded    -> state.copy(isLoading = false, transactions = intent.data)
        is DashboardIntent.LoadingStarted -> state.copy(isLoading = true)
        is DashboardIntent.Error         -> state.copy(isLoading = false, error = intent.message)
    }
}</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example</h3>
      <p><strong>FinTech — Transaction Dashboard with MVI:</strong> A banking dashboard with multiple concurrent data sources (balance, transactions, spending insights), filtering, sorting, and real-time updates. MVI's predictable state makes debugging production issues possible by replaying the sequence of intents.</p>
      <pre class="code-block"><code class="language-kotlin">class TransactionDashboardViewModel @Inject constructor(
    private val transactionRepo: TransactionRepository,
    private val accountRepo: AccountRepository
) : ViewModel() {

    private val _state = MutableStateFlow(TransactionDashboardState())
    val state: StateFlow<TransactionDashboardState> = _state.asStateFlow()

    init { processIntent(DashboardIntent.Initialize) }

    fun processIntent(intent: DashboardIntent) {
        when (intent) {
            is DashboardIntent.Initialize   -> loadInitialData()
            is DashboardIntent.FilterChanged -> applyFilter(intent.filter)
            is DashboardIntent.SortChanged  -> applySort(intent.sortBy)
            is DashboardIntent.Refresh      -> refreshData()
            is DashboardIntent.SearchQueryChanged -> updateSearch(intent.query)
        }
    }

    private fun loadInitialData() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            combine(
                transactionRepo.getTransactions(),
                accountRepo.getBalance()
            ) { transactions, balance ->
                _state.update { currentState ->
                    currentState.copy(
                        isLoading    = false,
                        transactions = transactions,
                        balance      = balance,
                        error        = null
                    )
                }
            }
            .catch { e -> _state.update { it.copy(isLoading = false, error = e.message) } }
            .launchIn(viewModelScope)
        }
    }

    private fun applyFilter(filter: TransactionFilter) {
        _state.update { currentState ->
            val filtered = currentState.allTransactions.filter { transaction ->
                when (filter) {
                    TransactionFilter.ALL      -> true
                    TransactionFilter.INCOME   -> transaction.amount > 0
                    TransactionFilter.EXPENSE  -> transaction.amount < 0
                    is TransactionFilter.DATE_RANGE ->
                        transaction.date in filter.start..filter.end
                }
            }
            currentState.copy(activeFilter = filter, transactions = filtered)
        }
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>God ViewModel in MVVM:</strong> ViewModel grows to 500+ lines with unrelated logic (formatting, navigation logic, business rules) — ✅ Fix: Extract UseCase classes for business logic; ViewModel only coordinates data flow between Use Cases and UI.</li>
        <li>❌ <strong>Exposing MutableStateFlow from ViewModel:</strong> View can mutate state directly, breaking UDF — ✅ Fix: Expose only <code>asStateFlow()</code> (immutable StateFlow).</li>
        <li>❌ <strong>Using navigation events as State (isSuccess: Boolean) in MVI:</strong> Once success=true, every new collector (rotation) re-triggers navigation — ✅ Fix: Use SharedFlow for one-shot events, or consume-and-reset the flag.</li>
        <li>❌ <strong>Reducer functions with side effects:</strong> In pure MVI, the reducer should be a pure function (same input → same output, no I/O) — ✅ Fix: Handle async side effects in the ViewModel's intent handlers; reducer only does in-memory state transformation.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"I evaluate architecture patterns based on testability, predictability, and scalability. MVC failed on Android because Activity is both View and Controller — untestable without a device. MVP solved testability via interfaces but introduced lifecycle management burden and interface boilerplate. MVVM with ViewModel solved lifecycle survival and reduced boilerplate, but without discipline, ViewModels accumulate mixed concerns. MVI takes MVVM further by enforcing strict Unidirectional Data Flow: every user action is an Intent, every state change is explicit, and the UI is a pure function of State. In production FinTech, I've used MVI because the state history is auditable — I can log every Intent and State transition to Crashlytics, reproduce bugs exactly by replaying the Intent sequence. For simpler screens, MVVM is pragmatic. The key principle regardless of pattern: ViewModel never has a View reference, state is exposed as immutable Flow, and each layer has one reason to change."</p>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 16-2: Clean Architecture -->
  <div class="subtopic" id="subtopic-16-2">
    <h2>Clean Architecture &amp; Module Boundaries</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>At scale (10+ developers, 100+ features), without module boundaries, everything depends on everything. Changing the database schema breaks the ViewModel. Changing the API response model changes the UI. Build times grow to 10+ minutes because every change triggers full recompilation. Clean Architecture imposes strict dependency rules — inner layers know nothing of outer layers — making modules independently compilable, testable in isolation, and replaceable without touching other layers.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p>Clean Architecture (Robert C. Martin) organizes code into concentric layers where <strong>dependencies only point inward</strong>:</p>
      <ul>
        <li><strong>Domain Layer (innermost):</strong> Pure Kotlin/Java. Entities (core business objects), Use Cases (business logic), Repository interfaces. Zero Android dependencies. 100% unit testable with plain JUnit.</li>
        <li><strong>Data Layer:</strong> Repository implementations, data sources (Retrofit, Room), DTOs, mappers. Depends on Domain (implements interfaces). Isolated from UI framework.</li>
        <li><strong>Presentation Layer (outermost):</strong> ViewModel, Fragments/Activities, Compose. Depends on Domain (via Use Cases). Never depends directly on Data.</li>
      </ul>
      <p>Android modularization maps to this: <code>:domain</code>, <code>:data</code>, <code>:feature-X</code> modules with enforced Gradle dependencies.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// ============ DOMAIN LAYER (:domain module) ============
// No Android imports, pure Kotlin

// Entity — core business object
data class Transaction(
    val id: String,
    val amount: BigDecimal,
    val currency: String,
    val timestamp: Long,
    val merchantName: String,
    val category: TransactionCategory
) {
    fun isDebit(): Boolean = amount < BigDecimal.ZERO
    fun formattedAmount(): String = "${if (isDebit()) "-" else "+"}${amount.abs()} $currency"
}

// Repository interface — defined in Domain, implemented in Data
interface TransactionRepository {
    fun getTransactions(accountId: String): Flow<List<Transaction>>
    suspend fun getTransactionById(id: String): Transaction?
    suspend fun categorizeTransaction(id: String, category: TransactionCategory): Result<Unit>
}

// Use Case — single responsibility, orchestrates domain logic
class GetFilteredTransactionsUseCase @Inject constructor(
    private val transactionRepository: TransactionRepository
) {
    operator fun invoke(accountId: String, filter: TransactionFilter): Flow<List<Transaction>> {
        return transactionRepository.getTransactions(accountId)
            .map { transactions ->
                transactions
                    .filter { filter.matches(it) }
                    .sortedByDescending { it.timestamp }
            }
    }
}

// ============ DATA LAYER (:data module) ============
// Implements domain interfaces, knows about Room/Retrofit

// DTO — matches API response shape (different from Domain entity)
@Serializable
data class TransactionDto(
    @SerialName("transaction_id") val transactionId: String,
    @SerialName("amount_cents") val amountCents: Long,
    @SerialName("currency_code") val currencyCode: String,
    @SerialName("unix_timestamp") val unixTimestamp: Long,
    @SerialName("merchant") val merchant: MerchantDto
)

// Mapper — convert Data model to Domain model
fun TransactionDto.toDomain(): Transaction = Transaction(
    id           = transactionId,
    amount       = BigDecimal(amountCents).movePointLeft(2),
    currency     = currencyCode,
    timestamp    = unixTimestamp,
    merchantName = merchant.displayName,
    category     = TransactionCategory.fromMcc(merchant.mcc)
)

// Repository implementation
class TransactionRepositoryImpl @Inject constructor(
    private val remoteDataSource: TransactionRemoteDataSource,
    private val localDataSource: TransactionLocalDataSource
) : TransactionRepository {
    override fun getTransactions(accountId: String): Flow<List<Transaction>> {
        return localDataSource.observeTransactions(accountId)
            .map { entities -> entities.map { it.toDomain() } }
            .onStart {
                // Trigger remote refresh without blocking
                remoteDataSource.fetchAndCacheTransactions(accountId)
            }
    }
}

// ============ PRESENTATION LAYER (:feature-transactions module) ============
class TransactionViewModel @Inject constructor(
    private val getFilteredTransactions: GetFilteredTransactionsUseCase,
    private val categorizeTransaction: CategorizeTransactionUseCase
) : ViewModel() {
    // Only depends on Domain Use Cases — never on Repository or DTO
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// Gradle module dependency rules (build.gradle.kts):
// :feature-transactions depends on :domain (NOT :data)
// :data depends on :domain
// :domain depends on nothing (pure Kotlin)

// settings.gradle.kts
include(":app", ":domain", ":data", ":feature-transactions", ":feature-accounts")

// :feature-transactions/build.gradle.kts
dependencies {
    implementation(project(":domain"))
    // NO implementation(project(":data")) — enforced by Gradle!
}

// :data/build.gradle.kts
dependencies {
    implementation(project(":domain"))
    implementation(libs.retrofit)
    implementation(libs.room)
}

// Dependency Inversion (the 'D' in SOLID + Clean Arch):
// Domain defines:
interface PaymentGateway {
    suspend fun processPayment(request: PaymentRequest): PaymentResult
}

// Data implements:
class StripePaymentGateway @Inject constructor(
    private val stripeApi: StripeApi
) : PaymentGateway {
    override suspend fun processPayment(request: PaymentRequest): PaymentResult {
        return stripeApi.charge(request.toStripeDto()).toDomain()
    }
}

// Domain Use Case uses interface — never knows about Stripe:
class ProcessPaymentUseCase @Inject constructor(
    private val gateway: PaymentGateway // Injected by Hilt from Data module
) {
    suspend operator fun invoke(request: PaymentRequest): PaymentResult {
        validateRequest(request) // Domain business rule
        return gateway.processPayment(request)
    }
}</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example</h3>
      <p><strong>Healthcare — Multi-module EHR App:</strong> An Electronic Health Record app with strict PHI (Protected Health Information) data isolation. The domain module contains zero Android or network code — it can run on server-side Kotlin. The data module handles FHIR API integration and local encryption. Feature modules (patient-list, clinical-notes, vitals) only talk to the domain.</p>
      <pre class="code-block"><code class="language-kotlin">// :domain/src/main/kotlin/com/ehr/domain/

// Core entity — PHI, must be encrypted at rest
data class PatientRecord(
    val id: PatientId,
    val demographics: Demographics,
    val clinicalNotes: List<ClinicalNote>,
    val vitalSigns: List<VitalSign>
) {
    fun isHighRisk(): Boolean = vitalSigns.any { it.isAbnormal() }
}

// Business rule encapsulated in domain
class AssessRiskUseCase @Inject constructor(
    private val patientRepository: PatientRepository,
    private val riskCalculator: RiskCalculator // Interface, implemented in data
) {
    suspend operator fun invoke(patientId: PatientId): RiskAssessment {
        val record = patientRepository.getPatient(patientId)
            ?: throw PatientNotFoundException(patientId)

        return riskCalculator.calculate(record).also {
            // Business rule: flag patients above threshold
            if (it.score > RiskThreshold.HIGH) {
                patientRepository.flagForReview(patientId)
            }
        }
    }
}

// :feature-vitals/src/main/kotlin/com/ehr/vitals/

class VitalsViewModel @Inject constructor(
    private val getVitalSigns: GetVitalSignsUseCase,   // From :domain
    private val assessRisk: AssessRiskUseCase            // From :domain
) : ViewModel() {
    // Zero knowledge of FHIR API, encryption, or Room schema
    val vitals = getVitalSigns(currentPatientId)
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Domain entities with Android imports:</strong> Importing Parcelable, Context, or any android.* in the domain module breaks the core promise (portable, JVM-only) — ✅ Fix: Domain entities are pure Kotlin data classes; use mappers in presentation to convert to Parcelable DTOs for navigation.</li>
        <li>❌ <strong>Use Cases doing too much:</strong> A single Use Case that fetches data, formats it, logs analytics, and sends a notification has multiple reasons to change — ✅ Fix: One Use Case = one business operation. Compose them in ViewModel if needed.</li>
        <li>❌ <strong>Skipping Use Cases for "simple" features:</strong> ViewModel talks directly to Repository → Domain rules scattered — ✅ Fix: Even simple operations deserve a Use Case — it's the testable boundary for business logic.</li>
        <li>❌ <strong>Leaking Data layer types into Domain:</strong> Using <code>Response&lt;T&gt;</code> (Retrofit) or <code>Cursor</code> (Room) in domain interfaces defeats the abstraction — ✅ Fix: Domain interfaces only use domain types; mappers in data layer convert framework types.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Clean Architecture's core value proposition is The Dependency Rule: source code dependencies must point inward — toward domain, never toward infrastructure. In practice this means my domain module has zero Android or third-party library imports — it compiles as pure Kotlin, runs on a JVM without a device, and my Use Cases are 100% unit testable with JUnit and no Mockito mocking of Android classes. The payoff compounds over time: when we migrated from Retrofit to Ktor, we changed only the data module; when we moved from Room to SQLDelight, the domain and feature modules compiled without a single change. The key signal I look for in code reviews is dependencies flowing in the wrong direction — a domain entity importing android.os.Parcelable, or a Use Case importing Retrofit's Response type. Those are architectural debt that compounds."</p>
      </div>
    </div>
  </div>

  <!-- Q&A for Topic 16 -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>Why did MVP replace MVC in Android, and why was MVVM then preferred over MVP?</div>
      <div class="qa-answer">
        <p><strong>MVC → MVP:</strong> In Android MVC, the Activity/Fragment serves as both View and Controller — they cannot be separated. This makes unit testing impossible without a running device (you can't test an Activity in a JUnit test). MVP extracted the Controller logic into a Presenter — a plain Kotlin class with no Android dependencies. Now you can unit test the Presenter with JUnit by passing a mock View interface.</p>
        <p><strong>MVP → MVVM:</strong> MVP's Presenter holds a direct reference to the View interface. This creates lifecycle management burden — you must null the view reference in onDestroy to prevent leaks, and you must manage scope cancellation manually. MVVM (with ViewModel + LiveData/StateFlow) solves this: the ViewModel has NO reference to the View. The View observes the ViewModel's state. ViewModel survives configuration changes natively. LiveData/StateFlow are lifecycle-aware observers — automatic cleanup. Far less boilerplate, built-in lifecycle safety.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q2</span>What is Unidirectional Data Flow (UDF) and why is it important?</div>
      <div class="qa-answer">
        <p>UDF means data flows in a single direction through the app:</p>
        <ol>
          <li><strong>User Action</strong> (click, input) → ViewModel (via function call or Intent)</li>
          <li><strong>ViewModel</strong> updates State</li>
          <li><strong>UI observes State</strong> and re-renders</li>
        </ol>
        <p>In a bidirectional model, the View both reads AND writes state — you can update the UI from the ViewModel AND from within the View itself. This creates race conditions, inconsistent state, and bugs that are hard to reproduce.</p>
        <p>UDF makes state predictable: at any point in time, there is exactly ONE source of truth (the StateFlow in the ViewModel). You can reproduce any UI state by knowing the StateFlow's value. Event sourcing and state logging become straightforward.</p>
        <pre class="code-block"><code class="language-kotlin">// Bidirectional (WRONG) — View modifies state directly:
class BadFragment : Fragment() {
    fun onSubmit() {
        viewModel.data.value = viewModel.data.value.copy(submitted = true) // View writes!
        binding.button.isEnabled = false // View independently tracks state
    }
}

// UDF (CORRECT) — View only sends intents:
class GoodFragment : Fragment() {
    fun onSubmit() {
        viewModel.processIntent(FormIntent.Submit) // View delegates
        // UI state (button disabled) comes from viewModel.state, not from local state
    }
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>In Clean Architecture, what is a Use Case and why is it important to have it as a separate class?</div>
      <div class="qa-answer">
        <p>A <strong>Use Case</strong> (also called Interactor) represents a single, specific business operation — a user story at the code level. It:</p>
        <ul>
          <li>Contains ONLY business rules (not data fetching logic, not UI logic)</li>
          <li>Depends only on domain interfaces (repositories, services)</li>
          <li>Is a plain Kotlin class — fully unit testable without Android or mocks of Android classes</li>
        </ul>
        <p><strong>Why not put business logic in ViewModel?</strong></p>
        <ul>
          <li>ViewModel is presentation layer — it survives rotation but it's tied to a screen. Business rules should be reusable across screens and even platforms.</li>
          <li>ViewModel tests require more setup. Use Case tests are dead simple — just pass mock repositories.</li>
          <li>Multiple ViewModels (phone + tablet) can share the same Use Case.</li>
        </ul>
        <pre class="code-block"><code class="language-kotlin">// Use Case — pure domain logic, easily testable
class TransferFundsUseCase @Inject constructor(
    private val accountRepository: AccountRepository,
    private val notificationService: NotificationService
) {
    suspend operator fun invoke(
        fromAccountId: String,
        toAccountId: String,
        amount: BigDecimal
    ): TransferResult {
        // Business rules — these belong here, not in ViewModel:
        require(amount > BigDecimal.ZERO) { "Transfer amount must be positive" }
        val fromAccount = accountRepository.getAccount(fromAccountId)
            ?: return TransferResult.Failure("Source account not found")
        if (fromAccount.balance < amount) return TransferResult.Failure("Insufficient funds")

        return accountRepository.transfer(fromAccountId, toAccountId, amount)
            .also { if (it is TransferResult.Success) notificationService.notifyTransfer(it) }
    }
}

// Test — zero Android mocking needed:
class TransferFundsUseCaseTest {
    @Test fun `should fail when balance insufficient`() = runTest {
        val repo = FakeAccountRepository(balance = BigDecimal("50.00"))
        val useCase = TransferFundsUseCase(repo, FakeNotificationService())
        val result = useCase("acc1", "acc2", BigDecimal("100.00"))
        assertIs<TransferResult.Failure>(result)
        assertEquals("Insufficient funds", result.message)
    }
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q4</span>How do you handle navigation in MVVM without putting navigation logic in ViewModel (which shouldn't know about Context)?</div>
      <div class="qa-answer">
        <p>The ViewModel exposes navigation events via SharedFlow (not StateFlow — no replay). The View (Fragment/Activity) collects the events and performs the actual navigation.</p>
        <pre class="code-block"><code class="language-kotlin">// ViewModel — emits navigation events as sealed class
sealed class NavigationEvent {
    data class ToDetail(val id: String) : NavigationEvent()
    object ToLogin : NavigationEvent()
    object Back : NavigationEvent()
}

class DashboardViewModel : ViewModel() {
    private val _navigation = MutableSharedFlow<NavigationEvent>(
        replay = 0,           // No replay — one-shot
        extraBufferCapacity = 1
    )
    val navigation: SharedFlow<NavigationEvent> = _navigation.asSharedFlow()

    fun onTransactionClicked(id: String) {
        viewModelScope.launch {
            _navigation.emit(NavigationEvent.ToDetail(id))
        }
    }
}

// Fragment — handles navigation (has access to NavController)
class DashboardFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.navigation.collect { event ->
                    when (event) {
                        is NavigationEvent.ToDetail ->
                            findNavController().navigate(
                                DashboardFragmentDirections.actionToDetail(event.id)
                            )
                        NavigationEvent.ToLogin ->
                            findNavController().navigate(R.id.loginFragment)
                        NavigationEvent.Back ->
                            findNavController().popBackStack()
                    }
                }
            }
        }
    }
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q5</span>Explain the Repository pattern and why it's a key part of Android architecture.</div>
      <div class="qa-answer">
        <p>The Repository pattern provides a clean API for data access that abstracts the data sources (remote API, local database, in-memory cache). The ViewModel/Use Case has no idea whether data comes from network or cache — it just calls repository methods.</p>
        <p><strong>Key Responsibilities:</strong></p>
        <ul>
          <li>Single source of truth: coordinates between remote and local data sources</li>
          <li>Cache strategy: return cached data immediately, fetch fresh data, update cache, re-emit</li>
          <li>Error handling: translate network/DB exceptions to domain exceptions</li>
          <li>Data mapping: convert DTOs to domain entities</li>
        </ul>
        <pre class="code-block"><code class="language-kotlin">class TransactionRepositoryImpl @Inject constructor(
    private val api: BankApi,
    private val dao: TransactionDao,
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) : TransactionRepository {

    // Single source of truth pattern: emit DB immediately, fetch network, update DB
    override fun getTransactions(accountId: String): Flow<List<Transaction>> = flow {
        // 1. Emit cached data immediately (fast, no network wait)
        val cached = withContext(dispatcher) { dao.getTransactions(accountId) }
        emit(cached.map { it.toDomain() })

        // 2. Fetch fresh data from network
        val fresh = withContext(dispatcher) { api.getTransactions(accountId) }

        // 3. Update cache
        withContext(dispatcher) { dao.upsertAll(fresh.map { it.toEntity() }) }

        // 4. Emit fresh data (UI automatically updates)
        emit(fresh.map { it.toDomain() })
    }
    .catch { e -> throw mapException(e) } // Translate to domain exceptions
    .flowOn(dispatcher)
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>Your team is debating whether to use MVVM or MVI. What are the tradeoffs and when would you recommend each?</div>
      <div class="qa-answer">
        <p><strong>MVVM — Choose when:</strong></p>
        <ul>
          <li>Team is newer to Android — lower learning curve, more Jetpack examples</li>
          <li>Simpler screens with few state variables</li>
          <li>You want minimal boilerplate (no Intent sealed class, no reducer)</li>
          <li>Mixing Compose and View system (Compose's state management aligns naturally)</li>
        </ul>
        <p><strong>MVI — Choose when:</strong></p>
        <ul>
          <li>Complex screens with many interacting state variables (trading dashboard, multi-step forms)</li>
          <li>Team needs reproducible bug reports — log Intent sequence and replay state</li>
          <li>Time-travel debugging / state snapshots needed</li>
          <li>Multiple async events that must be processed atomically</li>
          <li>The screen has complex state transitions that are hard to reason about in MVVM</li>
        </ul>
        <p><strong>Practical recommendation:</strong> Use MVVM as the default; adopt MVI for individual screens where state complexity warrants it. You can mix patterns within one app — each ViewModel is independent. The critical invariant for both: single source of truth, UDF, no mutable state leaking from ViewModel.</p>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge</h3>
    <p><strong>Problem:</strong> Implement a Clean Architecture UseCase and Repository for a "Transfer Funds" feature. Include: domain entities, repository interface, repository implementation with network + local data sources, a TransferFundsUseCase with business validation, and a ViewModel that uses it. Demonstrate the full stack.</p>
    <pre class="code-block"><code class="language-kotlin">// ======= :domain module =======

data class BankAccount(
    val id: String,
    val ownerId: String,
    val balance: BigDecimal,
    val currency: String,
    val isActive: Boolean
)

sealed class TransferResult {
    data class Success(val transactionId: String, val newBalance: BigDecimal) : TransferResult()
    data class Failure(val reason: String, val errorCode: TransferErrorCode) : TransferResult()
}

enum class TransferErrorCode { INSUFFICIENT_FUNDS, ACCOUNT_NOT_FOUND, ACCOUNT_INACTIVE, NETWORK_ERROR }

interface BankAccountRepository {
    suspend fun getAccount(accountId: String): BankAccount?
    suspend fun transfer(from: String, to: String, amount: BigDecimal): TransferResult
    fun observeAccount(accountId: String): Flow<BankAccount>
}

class TransferFundsUseCase @Inject constructor(
    private val repository: BankAccountRepository
) {
    data class Params(val fromId: String, val toId: String, val amount: BigDecimal)

    suspend operator fun invoke(params: Params): TransferResult {
        val (fromId, toId, amount) = params

        // Business validations (these are domain rules, not UI rules):
        if (amount <= BigDecimal.ZERO) {
            return TransferResult.Failure("Amount must be positive", TransferErrorCode.INSUFFICIENT_FUNDS)
        }
        if (fromId == toId) {
            return TransferResult.Failure("Cannot transfer to same account", TransferErrorCode.ACCOUNT_NOT_FOUND)
        }

        val fromAccount = repository.getAccount(fromId)
            ?: return TransferResult.Failure("Source account not found", TransferErrorCode.ACCOUNT_NOT_FOUND)

        if (!fromAccount.isActive) {
            return TransferResult.Failure("Source account is inactive", TransferErrorCode.ACCOUNT_INACTIVE)
        }
        if (fromAccount.balance < amount) {
            return TransferResult.Failure(
                "Insufficient funds: balance ${fromAccount.balance}, requested $amount",
                TransferErrorCode.INSUFFICIENT_FUNDS
            )
        }

        return repository.transfer(fromId, toId, amount)
    }
}

// ======= :data module =======

@Serializable
data class AccountDto(
    @SerialName("account_id") val accountId: String,
    @SerialName("balance_cents") val balanceCents: Long,
    @SerialName("currency") val currency: String,
    @SerialName("owner_id") val ownerId: String,
    @SerialName("is_active") val isActive: Boolean
)

fun AccountDto.toDomain() = BankAccount(
    id = accountId,
    ownerId = ownerId,
    balance = BigDecimal(balanceCents).movePointLeft(2),
    currency = currency,
    isActive = isActive
)

class BankAccountRepositoryImpl @Inject constructor(
    private val api: BankApi,
    private val dao: AccountDao
) : BankAccountRepository {

    override suspend fun getAccount(accountId: String): BankAccount? {
        return withContext(Dispatchers.IO) {
            try {
                val dto = api.getAccount(accountId)
                dao.insert(dto.toEntity()) // Cache locally
                dto.toDomain()
            } catch (e: HttpException) {
                if (e.code() == 404) null
                else dao.getAccount(accountId)?.toDomain() // Fallback to cache
            } catch (e: IOException) {
                dao.getAccount(accountId)?.toDomain() // Offline fallback
            }
        }
    }

    override suspend fun transfer(from: String, to: String, amount: BigDecimal): TransferResult {
        return withContext(Dispatchers.IO) {
            try {
                val response = api.transfer(
                    TransferRequest(
                        fromAccountId = from,
                        toAccountId = to,
                        amountCents = amount.movePointRight(2).toLong()
                    )
                )
                dao.updateBalance(from, response.newBalanceCents)
                TransferResult.Success(response.transactionId, response.newBalance)
            } catch (e: HttpException) {
                TransferResult.Failure("Transfer failed: ${e.code()}", TransferErrorCode.NETWORK_ERROR)
            } catch (e: IOException) {
                TransferResult.Failure("Network unavailable", TransferErrorCode.NETWORK_ERROR)
            }
        }
    }

    override fun observeAccount(accountId: String): Flow<BankAccount> =
        dao.observeAccount(accountId).map { it.toDomain() }
}

// ======= :feature-transfer module =======

data class TransferUiState(
    val fromAccount: BankAccount? = null,
    val isLoading: Boolean = false,
    val amountError: String? = null,
    val transferResult: TransferResult? = null,
    val error: String? = null
)

class TransferViewModel @Inject constructor(
    private val transferFunds: TransferFundsUseCase,
    private val getAccount: GetAccountUseCase,
    savedStateHandle: SavedStateHandle
) : ViewModel() {
    private val accountId = savedStateHandle.get<String>("accountId")!!

    private val _state = MutableStateFlow(TransferUiState())
    val state: StateFlow<TransferUiState> = _state.asStateFlow()

    init {
        viewModelScope.launch {
            val account = getAccount(accountId)
            _state.update { it.copy(fromAccount = account) }
        }
    }

    fun transfer(toAccountId: String, amountText: String) {
        val amount = amountText.toBigDecimalOrNull()
        if (amount == null || amount <= BigDecimal.ZERO) {
            _state.update { it.copy(amountError = "Enter a valid amount") }
            return
        }

        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, amountError = null, error = null) }

            val result = transferFunds(
                TransferFundsUseCase.Params(
                    fromId = accountId,
                    toId = toAccountId,
                    amount = amount
                )
            )

            _state.update { it.copy(isLoading = false, transferResult = result) }
        }
    }
}

// Architecture summary:
// domain: BankAccount, TransferResult, BankAccountRepository (interface), TransferFundsUseCase
// data:   AccountDto, BankAccountRepositoryImpl, AccountDao, BankApi
// feature: TransferViewModel (only imports domain classes!), TransferFragment
// Dependency flow: feature -> domain <- data (data and feature never import each other)</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="16" data-item="0"> ✅ Understood Why &amp; What</label>
    <label class="progress-check"><input type="checkbox" data-topic="16" data-item="1"> ✅ Can explain How it works internally</label>
    <label class="progress-check"><input type="checkbox" data-topic="16" data-item="2"> ✅ Reviewed Common Mistakes</label>
    <label class="progress-check"><input type="checkbox" data-topic="16" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="16" data-item="4"> ✅ Solved Coding Challenge</label>
  </div>
</section>

<!-- ============================================================ -->
<!--  TOPIC 17: SOLID Principles                                  -->
<!-- ============================================================ -->
<section class="topic-section" id="topic-17">
  <div class="topic-header">
    <div class="topic-header-icon">🧱</div>
    <div class="topic-header-text">
      <h1>SOLID Principles</h1>
      <p class="topic-tagline">The five design principles every senior Android engineer applies daily — with real Kotlin and Android examples</p>
      <div class="category-badge-group">
        <span class="cat-pill">SOLID</span>
        <span class="cat-pill">Design Principles</span>
        <span class="cat-pill">OOP</span>
        <span class="cat-pill">Clean Code</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 17-1: S, O, L Principles -->
  <div class="subtopic" id="subtopic-17-1">
    <h2>S — Single Responsibility, O — Open/Closed, L — Liskov Substitution</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>SOLID principles exist because software grows. A class that starts at 50 lines becomes 500. A class with multiple responsibilities becomes the bottleneck — every developer must touch it for every feature. SOLID provides concrete heuristics for splitting responsibilities and defining stable interfaces that make code extensible without modification. In Android specifically, violations manifest as: untestable classes (SRP violation — too many dependencies to mock), feature additions that break existing functionality (OCP violation), crashes when substituting implementations (LSP violation), bloated interfaces (ISP violation), and high-level modules fragile to low-level changes (DIP violation).</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p><strong>S — Single Responsibility Principle:</strong> A class should have only one reason to change. One class = one cohesive responsibility = one actor (stakeholder) who might require changes.</p>
      <p><strong>O — Open/Closed Principle:</strong> Software entities should be open for extension but closed for modification. Add new behavior by adding new code (new classes), not by editing existing code.</p>
      <p><strong>L — Liskov Substitution Principle:</strong> Objects of a subclass should be substitutable for objects of the superclass without altering program correctness. Subtypes must honor the behavioral contract of their supertype.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// ============ S — Single Responsibility ============

// VIOLATION: LoginViewModel does too many things
class ViolationLoginViewModel : ViewModel() {
    fun login(email: String, password: String) {
        // 1. Validates input (presentation concern)
        if (!email.contains("@")) { /* show error */ return }
        // 2. Makes API call (data concern)
        val response = retrofit.create(AuthApi::class.java).login(email, password)
        // 3. Saves token (data concern)
        sharedPrefs.edit().putString("token", response.token).apply()
        // 4. Logs analytics (cross-cutting concern)
        FirebaseAnalytics.getInstance(context).logEvent("login_success", null)
        // 5. Navigates (presentation concern)
        startActivity(Intent(context, DashboardActivity::class.java))
    }
}

// CORRECT: Each class has ONE reason to change
class InputValidator {
    fun validateEmail(email: String): ValidationResult =
        if (email.contains("@") && email.contains(".")) ValidationResult.Valid
        else ValidationResult.Invalid("Invalid email format")
}

class AuthRepository @Inject constructor(
    private val authApi: AuthApi,
    private val tokenStorage: TokenStorage
) {
    suspend fun login(email: String, password: String): AuthResult {
        val response = authApi.login(LoginRequest(email, password))
        tokenStorage.saveToken(response.token)
        return AuthResult.Success(response.userId)
    }
}

class LoginAnalyticsTracker @Inject constructor(private val analytics: FirebaseAnalytics) {
    fun trackLoginSuccess(userId: String) = analytics.logEvent("login_success", bundleOf("uid" to userId))
    fun trackLoginFailure(reason: String) = analytics.logEvent("login_fail", bundleOf("reason" to reason))
}

class LoginViewModel @Inject constructor(
    private val validator: InputValidator,
    private val authRepository: AuthRepository,
    private val analytics: LoginAnalyticsTracker
) : ViewModel() {
    private val _state = MutableStateFlow<LoginState>(LoginState.Idle)
    val state: StateFlow<LoginState> = _state.asStateFlow()

    fun login(email: String, password: String) {
        val validation = validator.validateEmail(email)
        if (validation is ValidationResult.Invalid) {
            _state.value = LoginState.ValidationError(validation.message)
            return
        }
        viewModelScope.launch {
            _state.value = LoginState.Loading
            runCatching { authRepository.login(email, password) }
                .onSuccess { result ->
                    analytics.trackLoginSuccess(result.userId)
                    _state.value = LoginState.Success
                }
                .onFailure { e ->
                    if (e is CancellationException) throw e
                    analytics.trackLoginFailure(e.message ?: "unknown")
                    _state.value = LoginState.Error(e.message ?: "Login failed")
                }
        }
    }
}

// ============ O — Open/Closed ============

// VIOLATION: Switch statement that grows with every new payment method
fun processPayment(method: String, amount: BigDecimal) {
    when (method) {
        "credit_card" -> { /* Stripe processing */ }
        "paypal"      -> { /* PayPal processing */ }
        "apple_pay"   -> { /* Apple Pay processing */ }
        // Adding new method requires MODIFYING this function!
    }
}

// CORRECT: Add new payment methods without touching existing code
interface PaymentProcessor {
    val supportedMethod: PaymentMethod
    suspend fun process(request: PaymentRequest): PaymentResult
    fun isAvailable(): Boolean = true // Open for override
}

class StripePaymentProcessor @Inject constructor(
    private val stripeApi: StripeApi
) : PaymentProcessor {
    override val supportedMethod = PaymentMethod.CREDIT_CARD
    override suspend fun process(request: PaymentRequest): PaymentResult {
        return stripeApi.charge(request.toStripeCharge()).toDomain()
    }
}

class GooglePayProcessor @Inject constructor(
    private val googlePayClient: PaymentsClient
) : PaymentProcessor {
    override val supportedMethod = PaymentMethod.GOOGLE_PAY
    override fun isAvailable(): Boolean = GoogleApiAvailability.getInstance().isGooglePlayServicesAvailable(context) == ConnectionResult.SUCCESS
    override suspend fun process(request: PaymentRequest): PaymentResult { /* ... */ return PaymentResult.Success("") }
}

// Registry — closed for modification, open for extension via DI
class PaymentProcessorRegistry @Inject constructor(
    processors: Set<@JvmSuppressWildcards PaymentProcessor>
) {
    private val processorMap = processors.associateBy { it.supportedMethod }

    fun getProcessor(method: PaymentMethod): PaymentProcessor =
        processorMap[method] ?: throw UnsupportedPaymentMethodException(method)
}
// Adding CryptoPaymentProcessor? Just create the class + add to Hilt set binding. NOTHING else changes.

// ============ L — Liskov Substitution ============

// VIOLATION: Subtype breaks supertype contract
abstract class DataSource {
    abstract fun getData(): List<String> // Contract: always returns a list
}

class CachingDataSource : DataSource() {
    override fun getData(): List<String> {
        // VIOLATION: Contract promises List<String>, but we throw sometimes!
        if (!cacheLoaded) throw CacheNotInitializedException()
        return cachedData
    }
}

// CORRECT: Subtype fully honors contract
interface DataRepository<T> {
    suspend fun get(id: String): T?  // Contract: returns T or null (never throws for "not found")
    suspend fun getAll(): List<T>     // Contract: returns list, may be empty
}

class RemoteUserRepository @Inject constructor(private val api: UserApi) : DataRepository<User> {
    override suspend fun get(id: String): User? = runCatching { api.getUser(id) }.getOrNull()
    override suspend fun getAll(): List<User> = runCatching { api.getAllUsers() }.getOrElse { emptyList() }
}

class LocalUserRepository @Inject constructor(private val dao: UserDao) : DataRepository<User> {
    override suspend fun get(id: String): User? = dao.findById(id)?.toDomain()
    override suspend fun getAll(): List<User> = dao.getAll().map { it.toDomain() }
}

// Both implementations are fully interchangeable — no surprises for the caller
class UserViewModel @Inject constructor(
    private val userRepository: DataRepository<User> // Works with Remote OR Local
) : ViewModel() { }</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// SRP — Identify by "and": if class name has "and", it violates SRP
// LoginAndAnalyticsManager → split into LoginManager + AnalyticsManager

// OCP — Identify by "switch/when on type": replace with polymorphism
// Hilt Set Multibindings enable OCP registration:
@Module @InstallIn(SingletonComponent::class)
abstract class PaymentProcessorsModule {
    @Binds @IntoSet abstract fun bindStripe(p: StripePaymentProcessor): PaymentProcessor
    @Binds @IntoSet abstract fun bindGoogle(p: GooglePayProcessor): PaymentProcessor
}

// LSP — Rule of thumb: preconditions cannot be strengthened in subtype
//        postconditions cannot be weakened in subtype
// Check: "Does my subtype throw where supertype would return null?"
// Check: "Does my subtype accept less input than supertype?"

// Kotlin sealed classes help enforce LSP — exhaustive when() means all subtypes handled:
sealed class PaymentResult {
    data class Success(val transactionId: String) : PaymentResult()
    data class Failure(val reason: String)         : PaymentResult()
}
// Any processor returning PaymentResult must return only Success or Failure — no surprises</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example</h3>
      <p><strong>OCP in Analytics:</strong> A large e-commerce app has analytics events sent to Firebase, Amplitude, and a custom backend. OCP means adding Mixpanel later requires zero changes to existing analytics code.</p>
      <pre class="code-block"><code class="language-kotlin">interface AnalyticsProvider {
    fun track(event: AnalyticsEvent)
    fun setUserId(userId: String)
}

class FirebaseAnalyticsProvider @Inject constructor(
    private val firebaseAnalytics: FirebaseAnalytics
) : AnalyticsProvider {
    override fun track(event: AnalyticsEvent) {
        firebaseAnalytics.logEvent(event.name, event.toBundle())
    }
    override fun setUserId(userId: String) { firebaseAnalytics.setUserId(userId) }
}

class AmplitudeAnalyticsProvider @Inject constructor(
    private val amplitude: Amplitude
) : AnalyticsProvider {
    override fun track(event: AnalyticsEvent) { amplitude.track(event.name, event.toJsonObject()) }
    override fun setUserId(userId: String) { amplitude.setUserId(userId) }
}

// Composite — fans out to all providers — CLOSED for modification:
class CompositeAnalyticsProvider @Inject constructor(
    private val providers: Set<@JvmSuppressWildcards AnalyticsProvider>
) : AnalyticsProvider {
    override fun track(event: AnalyticsEvent) { providers.forEach { it.track(event) } }
    override fun setUserId(userId: String) { providers.forEach { it.setUserId(userId) } }
}
// To add Mixpanel: create MixpanelAnalyticsProvider, add @IntoSet binding. DONE.</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Confusing SRP with "one method per class":</strong> SRP means one reason to change (one stakeholder), not one method — ✅ Fix: Ask "who asks me to change this class?" If the answer is multiple stakeholders (product, design, backend), split.</li>
        <li>❌ <strong>Over-engineering OCP:</strong> Adding abstraction layers for behavior that never changes — ✅ Fix: Apply OCP where you anticipate extension (payment providers, analytics, validators). Don't abstract prematurely.</li>
        <li>❌ <strong>Throwing exceptions where supertype returns null (LSP):</strong> The caller can't safely substitute the subtype — ✅ Fix: Match the error behavior contract of the supertype exactly; use Kotlin's type system (nullable return types, Result types) to express it.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"SRP for me is about change isolation — a class should change for one reason. In Android, the most common violation is the God Activity or God ViewModel that handles validation, business logic, and analytics. I extract these into dedicated UseCase, Validator, and Tracker classes. OCP is about choosing the right extension point — I apply it wherever I expect variation, like payment methods or analytics providers, using Hilt's set multibindings to allow new implementations without touching existing code. LSP is subtler — the key test is: can I substitute any implementation without the caller needing to know which one it got? In Kotlin, sealed classes and Result types help enforce LSP because the compiler enforces exhaustive handling of all subtypes."</p>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 17-2: I and D Principles -->
  <div class="subtopic" id="subtopic-17-2">
    <h2>I — Interface Segregation, D — Dependency Inversion</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Interface Segregation solves the problem of "fat interfaces" — when a class must implement methods it doesn't use, its test doubles (fakes, mocks) must stub irrelevant methods, and changes to unrelated methods force recompilation. Dependency Inversion (combined with dependency injection) is what makes Android code testable at all — instead of <code>new Retrofit()</code> inside your ViewModel (untestable), you inject an interface that your test can swap for a fake.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p><strong>I — Interface Segregation Principle:</strong> Clients should not be forced to depend on interfaces they don't use. Many specific interfaces are better than one general-purpose fat interface. Classes should only implement methods they actually need.</p>
      <p><strong>D — Dependency Inversion Principle:</strong> High-level modules should not depend on low-level modules; both should depend on abstractions. Abstractions should not depend on details; details should depend on abstractions. In practice: inject your dependencies as interfaces, not concrete classes. The implementation is chosen at app startup by the DI container (Hilt).</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// ============ I — Interface Segregation ============

// VIOLATION: Fat interface — most implementors only need a subset
interface UserRepository {
    suspend fun getUser(id: String): User
    suspend fun createUser(user: User): User
    suspend fun updateUser(user: User): User
    suspend fun deleteUser(id: String)
    suspend fun searchUsers(query: String): List<User>
    suspend fun exportUsers(): File
    suspend fun importUsers(file: File): Int
    suspend fun sendPasswordReset(email: String)
    suspend fun verifyEmail(token: String): Boolean
    // Test doubles must stub ALL of these even for a simple "get user" test!
}

// CORRECT: Segregated interfaces — each is a focused contract
interface UserReadRepository {
    suspend fun getUser(id: String): User?
    suspend fun searchUsers(query: String): List<User>
}

interface UserWriteRepository {
    suspend fun createUser(user: User): User
    suspend fun updateUser(user: User): User
    suspend fun deleteUser(id: String)
}

interface UserAuthRepository {
    suspend fun sendPasswordReset(email: String)
    suspend fun verifyEmail(token: String): Boolean
}

interface UserExportRepository {
    suspend fun exportUsers(): File
    suspend fun importUsers(file: File): Int
}

// Each class only implements what it needs:
class ProfileViewModel @Inject constructor(
    private val userReader: UserReadRepository  // Only needs read operations
) : ViewModel() { }

class AdminPanelViewModel @Inject constructor(
    private val userWriter: UserWriteRepository,    // Needs write
    private val exporter: UserExportRepository      // And export
) : ViewModel() { }

// Implementation can implement multiple interfaces if needed:
class UserRepositoryImpl @Inject constructor(
    private val api: UserApi,
    private val dao: UserDao
) : UserReadRepository, UserWriteRepository, UserAuthRepository, UserExportRepository {
    override suspend fun getUser(id: String): User? = runCatching { api.getUser(id) }.getOrNull()
    override suspend fun createUser(user: User): User = api.createUser(user.toDto()).toDomain()
    // ... other implementations
}

// ============ D — Dependency Inversion ============

// VIOLATION: High-level module depends on low-level concrete class
class PaymentViewModel : ViewModel() {
    // Directly depends on CONCRETE implementation — impossible to test without network!
    private val stripeApi = Retrofit.Builder()
        .baseUrl("https://api.stripe.com")
        .build()
        .create(StripeApi::class.java)

    fun processPayment(amount: BigDecimal) {
        // Can't test this without hitting Stripe's API
        stripeApi.charge(amount)
    }
}

// CORRECT: Both high-level and low-level depend on abstraction
interface PaymentGateway {
    suspend fun processPayment(request: PaymentRequest): PaymentResult
    suspend fun refund(transactionId: String, amount: BigDecimal): RefundResult
}

// High-level (ViewModel) depends on interface:
class PaymentViewModel @Inject constructor(
    private val paymentGateway: PaymentGateway, // Interface! Injected by Hilt
    private val processPayment: ProcessPaymentUseCase
) : ViewModel() {
    fun onPayClicked(amount: BigDecimal) {
        viewModelScope.launch {
            val result = processPayment(PaymentRequest(amount))
            _state.value = when (result) {
                is PaymentResult.Success -> PaymentState.Success(result.transactionId)
                is PaymentResult.Failure -> PaymentState.Error(result.reason)
            }
        }
    }
}

// Low-level (Stripe) depends on interface — not the other way around:
class StripePaymentGateway @Inject constructor(
    private val stripeApi: StripeApi
) : PaymentGateway {
    override suspend fun processPayment(request: PaymentRequest): PaymentResult {
        return try {
            val response = stripeApi.createPaymentIntent(request.toStripeDto())
            PaymentResult.Success(response.paymentIntentId)
        } catch (e: StripeException) {
            PaymentResult.Failure(e.localizedMessage ?: "Payment failed")
        }
    }
    override suspend fun refund(transactionId: String, amount: BigDecimal): RefundResult {
        val response = stripeApi.createRefund(transactionId, amount.toLong())
        return RefundResult.Success(response.refundId)
    }
}

// Hilt DI module — wires interface to implementation:
@Module @InstallIn(SingletonComponent::class)
abstract class PaymentModule {
    @Binds abstract fun bindPaymentGateway(impl: StripePaymentGateway): PaymentGateway
}

// Test — swap implementation without touching ViewModel:
class PaymentViewModelTest {
    private val fakeGateway = FakePaymentGateway(shouldSucceed = true)
    private val viewModel = PaymentViewModel(
        paymentGateway = fakeGateway,
        processPayment = ProcessPaymentUseCase(fakeGateway)
    )

    @Test fun `should show success state after successful payment`() = runTest {
        viewModel.onPayClicked(BigDecimal("99.99"))
        assertEquals(PaymentState.Success::class, viewModel.state.value::class)
    }
}

class FakePaymentGateway(private val shouldSucceed: Boolean) : PaymentGateway {
    override suspend fun processPayment(request: PaymentRequest): PaymentResult =
        if (shouldSucceed) PaymentResult.Success("fake-tx-id")
        else PaymentResult.Failure("Payment declined")
    override suspend fun refund(transactionId: String, amount: BigDecimal): RefundResult =
        RefundResult.Success("fake-refund-id")
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// ISP — Kotlin delegation lets a class implement multiple interfaces cleanly:
class UserRepositoryImpl(
    private val remoteSource: UserRemoteDataSource,
    private val localSource: UserLocalDataSource
) : UserReadRepository by UserReadRepositoryDelegate(remoteSource, localSource),
    UserWriteRepository by UserWriteRepositoryDelegate(remoteSource, localSource)

// DIP — Hilt injection patterns:
// Constructor injection (preferred):
class MyViewModel @Inject constructor(private val repo: MyRepository) : ViewModel()

// Field injection (only for Android classes that framework instantiates):
@AndroidEntryPoint
class MyFragment : Fragment() {
    @Inject lateinit var analyticsTracker: AnalyticsTracker
}

// Hilt abstract module for interface bindings:
@Module @InstallIn(ViewModelComponent::class)
abstract class RepositoryModule {
    @Binds abstract fun bindUserRepo(impl: UserRepositoryImpl): UserRepository
}

// Qualifiers for multiple implementations of same interface:
@Qualifier @Retention(AnnotationRetention.BINARY)
annotation class Remote

@Qualifier @Retention(AnnotationRetention.BINARY)
annotation class Local

@Module @InstallIn(SingletonComponent::class)
abstract class DataSourceModule {
    @Binds @Remote abstract fun bindRemote(impl: RemoteUserDataSource): UserDataSource
    @Binds @Local  abstract fun bindLocal(impl: LocalUserDataSource): UserDataSource
}</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example</h3>
      <p><strong>DIP in Testing — Offline-first Banking App:</strong> The production app uses Retrofit for network calls. Integration tests use a fake in-memory implementation. The ViewModel is tested with neither touching the network nor database.</p>
      <pre class="code-block"><code class="language-kotlin">// Domain interface (dependency inversion point)
interface AccountDataSource {
    suspend fun fetchBalance(accountId: String): AccountBalance
    suspend fun fetchTransactions(accountId: String, page: Int): PagedTransactions
}

// Production implementation (low-level detail, implements abstraction)
class RetrofitAccountDataSource @Inject constructor(
    private val bankApi: BankApi
) : AccountDataSource {
    override suspend fun fetchBalance(accountId: String): AccountBalance {
        return bankApi.getBalance(accountId).toDomain()
    }
    override suspend fun fetchTransactions(accountId: String, page: Int): PagedTransactions {
        return bankApi.getTransactions(accountId, page).toDomain()
    }
}

// Test fake (replaces Retrofit in tests — no network needed)
class FakeAccountDataSource : AccountDataSource {
    val balances = mutableMapOf<String, AccountBalance>()
    val transactions = mutableMapOf<String, List<Transaction>>()
    var shouldThrow: Exception? = null

    override suspend fun fetchBalance(accountId: String): AccountBalance {
        shouldThrow?.let { throw it }
        return balances[accountId] ?: throw AccountNotFoundException(accountId)
    }
    override suspend fun fetchTransactions(accountId: String, page: Int): PagedTransactions {
        val items = transactions[accountId] ?: emptyList()
        return PagedTransactions(items, hasMore = false)
    }
}

// ViewModel test — complete, fast, no Robolectric, no network:
class AccountViewModelTest {
    private val fakeDataSource = FakeAccountDataSource().apply {
        balances["acc-123"] = AccountBalance(BigDecimal("1500.00"), "USD")
    }
    private val viewModel = AccountViewModel(
        accountRepository = AccountRepositoryImpl(fakeDataSource)
    )

    @Test fun `should display balance after loading`() = runTest {
        viewModel.loadAccount("acc-123")
        val state = viewModel.state.value
        assertIs<AccountState.Success>(state)
        assertEquals(BigDecimal("1500.00"), state.balance.amount)
    }

    @Test fun `should show error when account not found`() = runTest {
        fakeDataSource.shouldThrow = AccountNotFoundException("acc-999")
        viewModel.loadAccount("acc-999")
        assertIs<AccountState.Error>(viewModel.state.value)
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>One interface per class (too granular ISP):</strong> Creating <code>UserFetcher</code>, <code>UserSaver</code>, <code>UserDeleter</code> each with one method — excessive fragmentation — ✅ Fix: Group by cohesive use case (read operations together, write operations together).</li>
        <li>❌ <strong>Injecting Retrofit/OkHttpClient directly into ViewModel:</strong> ViewModel depends on framework details, impossible to test — ✅ Fix: Create repository/data source interface; inject that instead.</li>
        <li>❌ <strong>Using concrete classes in function parameters:</strong> <code>fun save(db: RoomDatabase)</code> — couples caller to Room — ✅ Fix: Define a <code>LocalStorage</code> interface; pass that.</li>
        <li>❌ <strong>Creating dependencies inside constructors (new keyword):</strong> <code>private val repo = UserRepository()</code> inside ViewModel — impossible to swap in tests — ✅ Fix: Always receive dependencies via constructor injection.</li>
        <li>❌ <strong>Depending on DI framework classes (Hilt/Dagger) in domain:</strong> Using <code>@Inject</code> in domain entities — ✅ Fix: @Inject belongs in data/presentation; domain classes are plain Kotlin with constructor parameters.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"ISP and DIP work together to make Android code testable. ISP says: define the smallest interfaces your clients actually need — my ViewModel that displays a profile only gets a UserReadRepository, not the full UserRepository with export and admin methods. This keeps test doubles trivial — I only stub what the class uses. DIP says: both my ViewModel and my Retrofit implementation depend on an interface — the ViewModel doesn't care if the data comes from Stripe, PayPal, or a local SQLite cache. In practice, this is where Hilt delivers value — it's the mechanism that wires the interface to the correct implementation at runtime, while tests wire it to a fake. The rule I enforce in code reviews: if a ViewModel constructor takes a concrete class (Retrofit, Room, SharedPreferences), it's a DIP violation. We always inject interfaces, and we always have a fake implementation for tests."</p>
      </div>
    </div>
  </div>

  <!-- Q&A for Topic 17 -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What does the Single Responsibility Principle mean in practice for an Android ViewModel?</div>
      <div class="qa-answer">
        <p>SRP means a ViewModel should have one reason to change — it should coordinate UI state for a single screen/feature. It should NOT contain input validation logic (separate Validator class), business rules (separate UseCase), analytics tracking (separate Tracker), or data access (separate Repository).</p>
        <p>A ViewModel that violates SRP changes when: the product team changes business rules, when the analytics team adds new events, when the design team changes validation rules, and when the backend team changes the API. That's four stakeholders → four reasons to change → SRP violation.</p>
        <pre class="code-block"><code class="language-kotlin">// Clean ViewModel — single responsibility: coordinate UI state
class ProfileViewModel @Inject constructor(
    private val getUserProfile: GetUserProfileUseCase,    // Business logic
    private val updateProfile: UpdateUserProfileUseCase,  // Business logic
    private val validator: ProfileInputValidator,          // Validation
    private val tracker: ProfileAnalyticsTracker          // Analytics
) : ViewModel() {
    // ViewModel's ONLY job: react to intents, update state, coordinate use cases
    fun onSaveClicked(name: String, bio: String) {
        val result = validator.validate(name, bio)
        if (result is ValidationResult.Invalid) {
            _state.update { it.copy(nameError = result.nameError, bioError = result.bioError) }
            return
        }
        viewModelScope.launch {
            updateProfile(UpdateProfileParams(name, bio))
                .onSuccess { tracker.trackProfileUpdated() }
        }
    }
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q2</span>How does Dependency Inversion (DIP) relate to testability? Give a concrete Android example.</div>
      <div class="qa-answer">
        <p>DIP is the foundational principle for testability. If a ViewModel depends on <code>Retrofit</code> directly (concrete class), testing it requires either a real network connection or a Robolectric setup — slow, fragile, not unit tests. If the ViewModel depends on a <code>UserRepository</code> interface, tests can inject a <code>FakeUserRepository</code> that returns controlled data instantly in memory.</p>
        <pre class="code-block"><code class="language-kotlin">// Without DIP — untestable:
class BadViewModel : ViewModel() {
    private val api = Retrofit.Builder().baseUrl("https://api.example.com").build()
        .create(UserApi::class.java) // Hardcoded concrete — impossible to swap!
}

// With DIP — fully testable:
class GoodViewModel @Inject constructor(
    private val userRepository: UserRepository // Interface
) : ViewModel()

// Production: Hilt binds UserRepositoryImpl
// Test: FakeUserRepository injected directly
class GoodViewModelTest {
    @Test fun `test without network`() = runTest {
        val fake = FakeUserRepository(users = listOf(testUser))
        val vm = GoodViewModel(fake) // Pure unit test — zero Android framework
        vm.loadUser("123")
        assertEquals(testUser.name, (vm.state.value as UserState.Success).user.name)
    }
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q3</span>Your app has an analytics interface. How do you use OCP to add a new analytics provider (Mixpanel) without changing existing code?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">// 1. Define the interface (already done — no changes):
interface AnalyticsProvider {
    fun track(event: AnalyticsEvent)
    fun identify(userId: String)
}

// 2. Create new implementation — NEW FILE, zero changes elsewhere:
class MixpanelAnalyticsProvider @Inject constructor(
    private val mixpanel: MixpanelAPI
) : AnalyticsProvider {
    override fun track(event: AnalyticsEvent) {
        val props = JSONObject(event.properties)
        mixpanel.track(event.name, props)
    }
    override fun identify(userId: String) {
        mixpanel.identify(userId)
    }
}

// 3. Register in Hilt module — add ONE line, no other changes:
@Module @InstallIn(SingletonComponent::class)
abstract class AnalyticsModule {
    @Binds @IntoSet abstract fun bindFirebase(p: FirebaseAnalyticsProvider): AnalyticsProvider
    @Binds @IntoSet abstract fun bindAmplitude(p: AmplitudeAnalyticsProvider): AnalyticsProvider
    @Binds @IntoSet abstract fun bindMixpanel(p: MixpanelAnalyticsProvider): AnalyticsProvider // ADDED
}

// Composite automatically picks up the new provider — no changes:
class CompositeAnalyticsProvider @Inject constructor(
    private val providers: Set<@JvmSuppressWildcards AnalyticsProvider>
) : AnalyticsProvider {
    override fun track(event: AnalyticsEvent) { providers.forEach { it.track(event) } }
    override fun identify(userId: String) { providers.forEach { it.identify(userId) } }
}
// Result: Mixpanel events flow automatically. Zero existing code modified.</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q4</span>What is the Liskov Substitution Principle violation risk with RecyclerView.Adapter subclasses?</div>
      <div class="qa-answer">
        <p>LSP requires that subtypes honor the behavioral contract of their supertype. With RecyclerView adapters, violations occur when:</p>
        <ul>
          <li>A subclass overrides <code>getItemCount()</code> to throw an exception in certain states instead of returning 0.</li>
          <li>A subclass's <code>onBindViewHolder</code> ignores the <code>position</code> parameter and uses internal state instead, causing incorrect binding if the RecyclerView manager calls it with an unexpected position.</li>
        </ul>
        <pre class="code-block"><code class="language-kotlin">// LSP VIOLATION in ListAdapter:
class BadProductAdapter : ListAdapter<Product, ProductViewHolder>(ProductDiffCallback()) {
    override fun getItemCount(): Int {
        // VIOLATION: contract says return count; we throw if not loaded
        if (!isDataLoaded) throw IllegalStateException("Data not loaded yet!")
        return currentList.size
    }
}
// RecyclerView calls getItemCount() to decide layout — now crashes!

// LSP CORRECT:
class GoodProductAdapter : ListAdapter<Product, ProductViewHolder>(ProductDiffCallback()) {
    override fun getItemCount(): Int = currentList.size // Always returns a valid count (0 when empty)
    // Use submitList(emptyList()) when no data, submitList(products) when loaded
    // The caller (RecyclerView) can safely substitute any ListAdapter subclass
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q5</span>Your repository interface has 15 methods. Most ViewModels only use 2-3. What principle is violated and how do you fix it?</div>
      <div class="qa-answer">
        <p>This violates the <strong>Interface Segregation Principle</strong>. The fat interface forces all ViewModels to depend on 15 methods even if they only use 2-3. Consequences: test doubles must stub 12 irrelevant methods; any change to any of the 15 methods forces recompilation of all consumers; it's harder to understand what any given ViewModel actually needs.</p>
        <pre class="code-block"><code class="language-kotlin">// BEFORE: Fat interface — 15 methods, ViewModels only use a subset
interface ProductRepository {
    suspend fun getProduct(id: String): Product
    suspend fun getAllProducts(): List<Product>
    suspend fun searchProducts(query: String): List<Product>
    suspend fun createProduct(product: Product): Product
    suspend fun updateProduct(product: Product): Product
    suspend fun deleteProduct(id: String)
    suspend fun bulkImport(file: File): Int
    suspend fun exportCatalog(): File
    suspend fun getInventory(productId: String): Inventory
    suspend fun updateInventory(productId: String, delta: Int)
    suspend fun getReviews(productId: String): List<Review>
    // ... 4 more
}

// AFTER: Segregated into role-based interfaces
interface ProductReadRepository {
    suspend fun getProduct(id: String): Product?
    fun searchProducts(query: String): Flow<List<Product>>
}

interface ProductWriteRepository {
    suspend fun createProduct(product: Product): Product
    suspend fun updateProduct(product: Product): Product
    suspend fun deleteProduct(id: String)
}

interface ProductInventoryRepository {
    suspend fun getInventory(productId: String): Inventory
    suspend fun updateInventory(productId: String, delta: Int)
}

interface ProductAdminRepository : ProductWriteRepository {
    suspend fun bulkImport(file: File): Int
    suspend fun exportCatalog(): File
}

// Each ViewModel gets exactly what it needs:
class ProductDetailViewModel @Inject constructor(
    private val products: ProductReadRepository // Only reads — tiny interface to fake
) : ViewModel()

class AdminPanelViewModel @Inject constructor(
    private val adminProducts: ProductAdminRepository,
    private val inventory: ProductInventoryRepository
) : ViewModel()</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q6</span>Explain the difference between Dependency Injection and Dependency Inversion. Are they the same thing?</div>
      <div class="qa-answer">
        <p>They are related but different concepts:</p>
        <p><strong>Dependency Inversion (DIP)</strong> is a <em>design principle</em>: high-level modules should not depend on low-level modules; both should depend on abstractions. It's about the DIRECTION of dependencies. You satisfy DIP by programming to interfaces, not concrete implementations.</p>
        <p><strong>Dependency Injection (DI)</strong> is a <em>technique/pattern</em>: provide (inject) an object's dependencies from the outside rather than having it create them internally. DI is a WAY to satisfy DIP, but not the only way (service locator is another way, though less recommended).</p>
        <pre class="code-block"><code class="language-kotlin">// DIP without DI (Service Locator — satisfies DIP but problematic):
class MyViewModel : ViewModel() {
    private val repo: UserRepository = ServiceLocator.get(UserRepository::class) // Depends on interface (DIP)
    // But hides dependencies — hard to test, global state
}

// DIP WITH DI (Constructor injection — best practice):
class MyViewModel @Inject constructor(
    private val repo: UserRepository // Interface (DIP) + injected from outside (DI)
) : ViewModel()
// Hilt provides the concrete implementation at runtime
// Tests provide a fake implementation directly

// Summary:
// DIP = principle: depend on abstractions (interfaces), not concretions (classes)
// DI = mechanism: dependencies provided externally (constructor, field, method)
// In Android: DIP defines WHAT you inject (interfaces); Hilt is the DI framework that does the injecting</code></pre>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge</h3>
    <p><strong>Problem:</strong> Refactor the following code that violates all 5 SOLID principles. Identify each violation and provide the refactored version:</p>
    <pre class="code-block"><code class="language-kotlin">// Original code — VIOLATES ALL 5 SOLID PRINCIPLES:
class UserManager(private val context: Context) {
    private val db = Room.databaseBuilder(context, AppDatabase::class.java, "app.db").build()
    private val api = Retrofit.Builder().baseUrl("https://api.example.com/").build().create(ApiService::class.java)

    fun getUserAndSendEmail(userId: String, emailType: String) {
        val user = db.userDao().getUser(userId)
        if (emailType == "welcome") {
            sendEmail(user.email, "Welcome!", "Welcome to our app, ${user.name}")
        } else if (emailType == "reset") {
            sendEmail(user.email, "Reset Password", "Click here to reset...")
        } else if (emailType == "promo") {
            sendEmail(user.email, "Special Offer", "20% off today!")
        }
    }

    fun sendEmail(to: String, subject: String, body: String) {
        // SMTP email sending logic
    }

    fun saveUser(user: User) {
        db.userDao().insert(user)
        api.createUser(user)
    }

    fun deleteUser(userId: String) {
        db.userDao().delete(userId)
        // Also needs to delete from S3, cache, analytics... keeps growing
    }
}

// SOLUTION — Refactored with all SOLID principles applied:

// ============ DOMAIN LAYER ============

// SRP: User is a pure data entity (no behavior mixing concerns)
data class User(val id: String, val name: String, val email: String)

// DIP: Define abstractions that high-level modules depend on
interface UserRepository {
    suspend fun getUser(id: String): User?
    suspend fun saveUser(user: User)
    suspend fun deleteUser(id: String)
}

// ISP: Email sending is a separate, focused interface
interface EmailService {
    suspend fun sendEmail(to: String, subject: String, body: String)
}

// OCP: Email template is extensible without modifying existing code
interface EmailTemplate {
    val type: String
    fun buildEmail(user: User): EmailContent
}

data class EmailContent(val subject: String, val body: String)

// OCP: Each email type is a separate class — add new types without changing anything
class WelcomeEmailTemplate : EmailTemplate {
    override val type = "welcome"
    override fun buildEmail(user: User) = EmailContent(
        subject = "Welcome to the app!",
        body    = "Welcome, ${user.name}! We're glad you're here."
    )
}

class PasswordResetEmailTemplate : EmailTemplate {
    override val type = "reset"
    override fun buildEmail(user: User) = EmailContent(
        subject = "Reset your password",
        body    = "Hi ${user.name}, click here to reset your password..."
    )
}

class PromoEmailTemplate : EmailTemplate {
    override val type = "promo"
    override fun buildEmail(user: User) = EmailContent(
        subject = "Special offer for you!",
        body    = "Hi ${user.name}, enjoy 20% off today!"
    )
}

// SRP: Only sends emails — doesn't know about users or templates
// DIP: High-level SendEmailUseCase depends on EmailService interface
class SendUserEmailUseCase @Inject constructor(
    private val userRepository: UserRepository,
    private val emailService: EmailService,
    templates: Set<@JvmSuppressWildcards EmailTemplate>  // DIP + OCP: inject all templates
) {
    private val templateMap = templates.associateBy { it.type }

    suspend operator fun invoke(userId: String, emailType: String): Result<Unit> = runCatching {
        val user = userRepository.getUser(userId) ?: error("User not found: $userId")
        val template = templateMap[emailType] ?: error("Unknown email type: $emailType")
        val content = template.buildEmail(user)
        emailService.sendEmail(user.email, content.subject, content.body)
    }
}

// SRP: Only manages user lifecycle
class DeleteUserUseCase @Inject constructor(
    private val userRepository: UserRepository,
    private val cacheService: CacheService,         // ISP: focused interface
    private val storageService: CloudStorageService // ISP: focused interface
) {
    suspend operator fun invoke(userId: String): Result<Unit> = runCatching {
        userRepository.deleteUser(userId)  // Coordinates, but delegates each concern
        cacheService.invalidateUser(userId)
        storageService.deleteUserFiles(userId)
    }
}

// ============ DATA LAYER ============
// LSP: Implementation fully honors UserRepository contract (never throws where contract says return null)
class UserRepositoryImpl @Inject constructor(
    private val localDb: UserLocalDataSource,
    private val remoteApi: UserRemoteDataSource
) : UserRepository {
    override suspend fun getUser(id: String): User? =
        runCatching { remoteApi.getUser(id) }.getOrElse { localDb.getUser(id) }

    override suspend fun saveUser(user: User) {
        localDb.saveUser(user)
        runCatching { remoteApi.createUser(user) } // Don't fail save if network fails
    }

    override suspend fun deleteUser(id: String) {
        localDb.deleteUser(id)
        runCatching { remoteApi.deleteUser(id) }
    }
}

// ============ DI MODULE ============
@Module @InstallIn(SingletonComponent::class)
abstract class AppModule {
    // DIP: bind abstractions
    @Binds abstract fun bindUserRepo(impl: UserRepositoryImpl): UserRepository
    @Binds abstract fun bindEmail(impl: SmtpEmailService): EmailService

    // OCP: add new email types by adding @IntoSet bindings
    @Binds @IntoSet abstract fun bindWelcome(t: WelcomeEmailTemplate): EmailTemplate
    @Binds @IntoSet abstract fun bindReset(t: PasswordResetEmailTemplate): EmailTemplate
    @Binds @IntoSet abstract fun bindPromo(t: PromoEmailTemplate): EmailTemplate
}

// SOLID Principles Applied:
// S: UserManager split into SendUserEmailUseCase, DeleteUserUseCase, UserRepositoryImpl
// O: New email types added by creating new EmailTemplate class + @IntoSet binding
// L: UserRepositoryImpl honors UserRepository contract (null on not-found, not exception)
// I: EmailService, CacheService, CloudStorageService are focused single-purpose interfaces
// D: All use cases depend on interfaces; Hilt wires concrete implementations at runtime

// Testability result:
// SendUserEmailUseCase test only needs FakeUserRepository + FakeEmailService
// Adding CryptoEmailTemplate: zero changes to existing code — just new class + binding</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="17" data-item="0"> ✅ Understood Why &amp; What</label>
    <label class="progress-check"><input type="checkbox" data-topic="17" data-item="1"> ✅ Can explain How it works internally</label>
    <label class="progress-check"><input type="checkbox" data-topic="17" data-item="2"> ✅ Reviewed Common Mistakes</label>
    <label class="progress-check"><input type="checkbox" data-topic="17" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="17" data-item="4"> ✅ Solved Coding Challenge</label>
  </div>
</section>
'''
