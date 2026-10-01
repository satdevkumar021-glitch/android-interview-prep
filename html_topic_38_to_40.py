
def get_topics_38_to_40_html():
    return '''
<!-- ============================================================ -->
<!-- TOPIC 38: Android System Design                              -->
<!-- ============================================================ -->
<section class="topic-section" id="topic-38">
  <div class="topic-header">
    <div class="topic-header-icon">🏗️</div>
    <div class="topic-header-text">
      <h1>Android System Design</h1>
      <p class="topic-tagline">Design scalable, maintainable Android architectures for real-world production apps</p>
      <div class="category-badge-group">
        <span class="cat-pill">System Design</span>
        <span class="cat-pill">Architecture</span>
        <span class="cat-pill">Senior Level</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 38-1: News Feed App Design -->
  <div class="subtopic" id="subtopic-38-1">
    <h2>Design a News Feed App</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>System design questions reveal how you think at scale. A News Feed app is a classic because it combines <strong>pagination, caching, offline support, real-time updates, and media loading</strong> — all the real challenges senior Android engineers face daily. Interviewers want to see that you can decompose complexity, choose the right trade-offs, and justify every architectural decision.</p>
      <p>Problems without proper design: unbounded memory, stale data, jank from network calls on main thread, no offline support, no way to paginate efficiently.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p>Designing a News Feed app on Android involves architecting a system that can: fetch paginated articles from a REST/GraphQL API, cache them locally in Room, display them in a RecyclerView with smooth scrolling, support offline-first reading, handle background refresh with WorkManager, and load images efficiently with Coil/Glide. The design spans <strong>network layer, persistence layer, UI layer, and background task layer</strong>.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <p><strong>Architecture: MVVM + Repository + Clean Architecture layers</strong></p>
      <ol>
        <li>UI (Compose/View) observes StateFlow from ViewModel</li>
        <li>ViewModel delegates to UseCase / Repository</li>
        <li>Repository checks Room cache first (offline-first), then fetches from Retrofit</li>
        <li>Paging 3 handles pagination transparently</li>
        <li>WorkManager schedules periodic background sync</li>
        <li>Coil loads images with disk + memory cache</li>
      </ol>
      <pre class="code-block"><code class="language-kotlin">// --- Domain Layer ---
data class Article(
    val id: String,
    val title: String,
    val summary: String,
    val imageUrl: String,
    val publishedAt: Long,
    val isBookmarked: Boolean = false
)

// --- Data Layer: Room Entity ---
@Entity(tableName = "articles")
data class ArticleEntity(
    @PrimaryKey val id: String,
    val title: String,
    val summary: String,
    val imageUrl: String,
    val publishedAt: Long,
    val isBookmarked: Boolean,
    val cachedAt: Long = System.currentTimeMillis()
)

// --- DAO with Paging 3 support ---
@Dao
interface ArticleDao {
    @Query("SELECT * FROM articles ORDER BY publishedAt DESC")
    fun pagingSource(): PagingSource<Int, ArticleEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(articles: List<ArticleEntity>)

    @Query("UPDATE articles SET isBookmarked = :bookmarked WHERE id = :id")
    suspend fun updateBookmark(id: String, bookmarked: Boolean)

    @Query("DELETE FROM articles WHERE cachedAt < :threshold AND isBookmarked = 0")
    suspend fun evictStale(threshold: Long)
}

// --- RemoteMediator: the heart of offline-first Paging 3 ---
@OptIn(ExperimentalPagingApi::class)
class ArticleRemoteMediator(
    private val api: NewsApi,
    private val db: AppDatabase,
    private val category: String
) : RemoteMediator<Int, ArticleEntity>() {

    override suspend fun load(
        loadType: LoadType,
        state: PagingState<Int, ArticleEntity>
    ): MediatorResult {
        return try {
            val page = when (loadType) {
                LoadType.REFRESH -> 1
                LoadType.PREPEND -> return MediatorResult.Success(endOfPaginationReached = true)
                LoadType.APPEND -> {
                    val lastItem = state.lastItemOrNull()
                        ?: return MediatorResult.Success(endOfPaginationReached = true)
                    // Use cursor-based pagination for stability
                    db.remoteKeyDao().getNextCursor(lastItem.id) ?: return MediatorResult.Success(true)
                }
            }

            val response = api.getArticles(category = category, page = page, pageSize = state.config.pageSize)

            db.withTransaction {
                if (loadType == LoadType.REFRESH) {
                    db.articleDao().evictStale(System.currentTimeMillis() - 24 * 60 * 60 * 1000)
                }
                db.articleDao().insertAll(response.articles.map { it.toEntity() })
                db.remoteKeyDao().insertAll(response.articles.map {
                    RemoteKey(articleId = it.id, nextCursor = response.nextCursor)
                })
            }

            MediatorResult.Success(endOfPaginationReached = response.nextCursor == null)
        } catch (e: IOException) {
            MediatorResult.Error(e)
        } catch (e: HttpException) {
            MediatorResult.Error(e)
        }
    }
}

// --- ViewModel ---
@HiltViewModel
class NewsFeedViewModel @Inject constructor(
    private val repository: ArticleRepository
) : ViewModel() {

    private val _category = MutableStateFlow("technology")
    val category: StateFlow<String> = _category.asStateFlow()

    val articles: Flow<PagingData<ArticleUiModel>> = _category
        .flatMapLatest { cat -> repository.getArticlesPaged(cat) }
        .map { pagingData -> pagingData.map { it.toUiModel() } }
        .cachedIn(viewModelScope)

    fun onBookmarkToggled(articleId: String, bookmarked: Boolean) {
        viewModelScope.launch {
            repository.toggleBookmark(articleId, bookmarked)
        }
    }
}

// --- WorkManager background sync ---
class NewsSyncWorker(
    context: Context,
    params: WorkerParameters,
    private val repository: ArticleRepository
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            repository.syncLatestArticles()
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }

    companion object {
        fun schedule(workManager: WorkManager) {
            val request = PeriodicWorkRequestBuilder<NewsSyncWorker>(15, TimeUnit.MINUTES)
                .setConstraints(
                    Constraints.Builder()
                        .setRequiredNetworkType(NetworkType.CONNECTED)
                        .build()
                )
                .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
                .build()
            workManager.enqueueUniquePeriodicWork(
                "news_sync",
                ExistingPeriodicWorkPolicy.KEEP,
                request
            )
        }
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Key Design Decisions &amp; Trade-offs</h3>
      <pre class="code-block"><code class="language-kotlin">// Trade-off 1: REST vs GraphQL
// REST: simple, cacheable, wide tooling support
// GraphQL: fetch exactly what UI needs, reduces over-fetching
// Decision: REST + field selection query params for mobile

// Trade-off 2: Cursor vs Offset Pagination
// Offset: simple but breaks on inserts (articles shift)
// Cursor: stable even with real-time inserts, recommended for feeds
// Decision: Cursor-based with server-generated opaque tokens

// Trade-off 3: Room vs DataStore for small prefs
// Room: relational, queryable, good for lists
// DataStore: better for settings/flags (no SQL overhead)
// Decision: Room for articles, DataStore for user preferences

// Trade-off 4: Image loading — Coil vs Glide
// Coil: Kotlin-first, coroutine-native, smaller APK
// Glide: mature, battle-tested, more customization
// Decision: Coil in new projects, Glide if existing codebase

// Trade-off 5: Single Activity vs Multi Activity
// Single Activity: deep link handling, shared ViewModel scope
// Multi Activity: process isolation, clearer back stack
// Decision: Single Activity with Navigation Component</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example</h3>
      <p><strong>FinTech News Feed (Bloomberg-style):</strong> Articles with market data require &lt;100ms Time-To-First-Byte feel. We combine skeleton loaders, stale-while-revalidate caching (serve Room data immediately, refresh in background), and priority loading (above-fold articles get HIGH OkHttp priority).</p>
      <pre class="code-block"><code class="language-kotlin">// Stale-while-revalidate pattern
class ArticleRepository @Inject constructor(
    private val api: NewsApi,
    private val dao: ArticleDao,
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    fun getArticleStream(id: String): Flow<Result<Article>> = flow {
        // 1. Emit cached data immediately (fast, offline support)
        val cached = dao.getById(id)
        if (cached != null) {
            emit(Result.success(cached.toDomain()))
        }
        // 2. Fetch fresh in background
        try {
            val fresh = withContext(dispatcher) { api.getArticle(id) }
            dao.insert(fresh.toEntity())
            emit(Result.success(fresh.toDomain()))
        } catch (e: Exception) {
            if (cached == null) emit(Result.failure(e))
            // If cached exists, don't emit error — user has usable data
        }
    }.flowOn(dispatcher)
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Loading images synchronously:</strong> Blocking RecyclerView bind calls — ✅ Fix: Use Coil/Glide async loading in onBindViewHolder or Compose AsyncImage</li>
        <li>❌ <strong>No cache eviction:</strong> Room grows unbounded — ✅ Fix: Evict articles older than 24h that aren't bookmarked using WorkManager cleanup task</li>
        <li>❌ <strong>Fetching ALL articles on refresh:</strong> Wastes bandwidth — ✅ Fix: Send If-Modified-Since or ETag header; server returns 304 Not Modified if unchanged</li>
        <li>❌ <strong>Observing LiveData in Fragment incorrectly:</strong> Memory leaks with wrong lifecycleOwner — ✅ Fix: Use viewLifecycleOwner, never 'this' in Fragment</li>
        <li>❌ <strong>Not handling LoadState in Paging 3:</strong> Blank screen on error — ✅ Fix: Observe loadStateFlow, show retry UI on LoadState.Error</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"For a News Feed, I start with the constraints: DAU, article volume, read/write ratio (reads dominate 100:1), latency SLO. On Android I use <strong>Paging 3 with RemoteMediator</strong> for offline-first pagination — Room as the single source of truth, network as the sync layer. Images go through Coil with aggressive disk caching. Background sync via <strong>PeriodicWorkManager</strong> every 15 min. The key trade-off I always highlight: cursor vs offset pagination — cursors are non-negotiable for live feeds because offset breaks when new articles are inserted. For bandwidth, I add If-Modified-Since headers to skip unnecessary re-fetches. Memory is managed by setting Paging 3's maxSize and Coil's memory cache size based on available heap."</p>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 38-2: Offline-First Architecture -->
  <div class="subtopic" id="subtopic-38-2">
    <h2>Design Offline-First Architecture</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Mobile networks are unreliable — tunnels, elevators, rural areas, airplane mode. An app that breaks without internet is a terrible UX. Offline-first means the app <strong>works fully without a network connection</strong> and syncs changes when connectivity returns. This is the difference between a consumer-grade app and a production-grade one. Think Google Maps offline, Gmail drafts, Notion offline edits.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p>Offline-first architecture treats the <strong>local database as the primary source of truth</strong>. All reads come from local storage. All writes go to local storage first, then sync to the server. Conflict resolution strategies (last-write-wins, CRDTs, server-wins) must be explicitly designed. Key components: Room (local store), WorkManager (sync engine), ConnectivityManager (network awareness), and a robust conflict resolution layer.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// Operation Queue for offline writes
@Entity(tableName = "pending_operations")
data class PendingOperation(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val type: String,          // CREATE, UPDATE, DELETE
    val entityType: String,    // "article", "bookmark", "comment"
    val entityId: String,
    val payload: String,       // JSON serialized payload
    val createdAt: Long = System.currentTimeMillis(),
    val retryCount: Int = 0,
    val status: String = "PENDING" // PENDING, SYNCING, FAILED
)

// Sync Manager
class SyncManager @Inject constructor(
    private val operationDao: PendingOperationDao,
    private val api: SyncApi,
    private val db: AppDatabase
) {
    suspend fun syncPendingOperations(): SyncResult {
        val pending = operationDao.getPendingOperations()
        var successCount = 0
        var failCount = 0

        pending.forEach { op ->
            try {
                operationDao.updateStatus(op.id, "SYNCING")
                when (op.type) {
                    "CREATE" -> api.createEntity(op.entityType, op.payload)
                    "UPDATE" -> api.updateEntity(op.entityType, op.entityId, op.payload)
                    "DELETE" -> api.deleteEntity(op.entityType, op.entityId)
                }
                operationDao.delete(op.id)
                successCount++
            } catch (e: HttpException) {
                if (e.code() in 400..499) {
                    // Client error — don't retry, mark failed
                    operationDao.updateStatus(op.id, "FAILED")
                } else {
                    // Server error — retry later
                    operationDao.incrementRetry(op.id)
                }
                failCount++
            }
        }
        return SyncResult(successCount, failCount)
    }
}

// Conflict resolution: Vector Clocks approach
data class VersionedEntity<T>(
    val data: T,
    val vectorClock: Map<String, Long>,  // deviceId -> timestamp
    val lastModifiedBy: String
)

fun resolveConflict(local: VersionedEntity<Article>, remote: VersionedEntity<Article>): VersionedEntity<Article> {
    // Compare vector clocks
    val localDominates = local.vectorClock.all { (k, v) -> (remote.vectorClock[k] ?: 0) <= v }
    val remoteDominates = remote.vectorClock.all { (k, v) -> (local.vectorClock[k] ?: 0) <= v }

    return when {
        localDominates -> local   // local is strictly newer
        remoteDominates -> remote // remote is strictly newer
        else -> {
            // True conflict — merge or apply policy (last-writer-wins by timestamp)
            if (local.data.updatedAt > remote.data.updatedAt) local else remote
        }
    }
}

// ConnectivityObserver
class NetworkConnectivityObserver(context: Context) : ConnectivityObserver {
    private val connectivityManager = context.getSystemService(ConnectivityManager::class.java)

    override fun observe(): Flow<Status> = callbackFlow {
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) { trySend(Status.Available) }
            override fun onLost(network: Network) { trySend(Status.Lost) }
            override fun onUnavailable() { trySend(Status.Unavailable) }
        }
        connectivityManager.registerDefaultNetworkCallback(callback)
        awaitClose { connectivityManager.unregisterNetworkCallback(callback) }
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// Key offline-first patterns

// 1. Optimistic UI update
fun toggleBookmark(articleId: String) {
    viewModelScope.launch {
        // Immediately update local DB (optimistic)
        dao.updateBookmark(articleId, true)
        // Queue for sync
        pendingOpDao.insert(PendingOperation(
            type = "UPDATE", entityType = "bookmark", entityId = articleId,
            payload = """{"bookmarked": true}"""
        ))
        // Trigger sync if online
        if (networkObserver.isOnline()) syncManager.syncPendingOperations()
    }
}

// 2. WorkManager sync on connectivity restore
class SyncOnConnectWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork(): Result {
        syncManager.syncPendingOperations()
        return Result.success()
    }
}

// Register for connectivity change
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .build()
val syncRequest = OneTimeWorkRequestBuilder<SyncOnConnectWorker>()
    .setConstraints(constraints)
    .build()
WorkManager.getInstance(context).enqueueUniqueWork(
    "connectivity_sync", ExistingWorkPolicy.REPLACE, syncRequest
)</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example</h3>
      <p><strong>Healthcare App (EMR on Android tablets):</strong> Nurses record patient vitals while walking through the hospital. Network is spotty. Every reading must be captured and synced reliably. We use a <strong>Write-Ahead Log (WAL)</strong> pattern — all writes go to an operations queue in Room, a WorkManager job syncs them with exponential backoff. We use optimistic UI for instant feedback and roll back if sync fails with a visible snackbar.</p>
      <pre class="code-block"><code class="language-kotlin">// Healthcare vitals recording with offline queue
class VitalsRepository @Inject constructor(
    private val vitalsDao: VitalsDao,
    private val pendingOpDao: PendingOperationDao,
    private val workManager: WorkManager
) {
    suspend fun recordVital(vital: PatientVital): Result<Unit> {
        return try {
            // 1. Write to local DB immediately
            vitalsDao.insert(vital.toEntity().copy(syncStatus = SyncStatus.PENDING))
            // 2. Queue sync operation
            pendingOpDao.insert(vital.toPendingOp())
            // 3. Schedule immediate sync attempt (runs when network available)
            val syncWork = OneTimeWorkRequestBuilder<VitalsSyncWorker>()
                .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
                .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
                .build()
            workManager.enqueue(syncWork)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Checking network before writing:</strong> Race condition — connectivity can drop mid-write — ✅ Fix: Always write locally first, sync after</li>
        <li>❌ <strong>No idempotency keys:</strong> Duplicate operations on retry — ✅ Fix: Use UUID as operation ID, server checks if already applied</li>
        <li>❌ <strong>Assuming last-write-wins is always safe:</strong> Dangerous for collaborative data — ✅ Fix: Use entity-appropriate conflict resolution (CRDT for counters, user-prompt for important fields)</li>
        <li>❌ <strong>Infinite retry on client 4xx errors:</strong> Drains battery — ✅ Fix: Distinguish 4xx (logic error, stop) from 5xx (transient, retry)</li>
        <li>❌ <strong>No sync status feedback:</strong> User doesn't know if data is saved — ✅ Fix: Show sync status badge (✓ synced, ⏳ pending, ⚠️ failed)</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Offline-first means local DB is the source of truth — reads always hit Room, writes go to Room first then sync. I implement a <strong>pending operations queue</strong> — each mutation gets serialized as a PendingOperation entity with UUID for idempotency. WorkManager syncs them with CONNECTED constraint + exponential backoff. The hard problem is conflicts — I design around three strategies: server-wins (simple, safe for most cases), last-modified-wins (for user-specific data), and field-level merging for collaborative features. I always expose sync status to the UI so users know their data is queued. The key insight: treat the network as an eventually-consistent sync layer, not a required dependency."</p>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 38-3: Chat App with WebSocket -->
  <div class="subtopic" id="subtopic-38-3">
    <h2>Design Chat App with WebSocket</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Chat apps require <strong>real-time bidirectional communication</strong>. HTTP polling wastes bandwidth and creates latency. WebSockets maintain a persistent TCP connection, enabling server-push of messages instantly. The design challenge: managing WebSocket lifecycle with Android's Activity/Fragment lifecycle, reconnection on network changes, message ordering, delivery receipts, and offline queuing.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p>A WebSocket-based chat system on Android uses OkHttp's WebSocket API (or Socket.IO for rooms/namespaces) running in a <strong>foreground Service</strong> (to survive screen-off), with messages persisted in Room, displayed in a RecyclerView/Compose LazyColumn, and delivery status tracked per-message. The lifecycle: Connect on app foreground → Disconnect gracefully on app background → Reconnect on network restore.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// Chat Message entity
@Entity(tableName = "messages")
data class MessageEntity(
    @PrimaryKey val id: String,
    val conversationId: String,
    val senderId: String,
    val content: String,
    val timestamp: Long,
    val status: String,  // SENDING, SENT, DELIVERED, READ, FAILED
    val isLocal: Boolean // true = optimistic insert, not yet confirmed
)

// WebSocket Manager — runs in a bound Service
class ChatWebSocketManager @Inject constructor(
    private val okHttpClient: OkHttpClient,
    private val messageDao: MessageDao,
    private val scope: CoroutineScope
) {
    private var webSocket: WebSocket? = null
    private val _connectionState = MutableStateFlow<ConnectionState>(ConnectionState.Disconnected)
    val connectionState = _connectionState.asStateFlow()

    private val _incomingMessages = MutableSharedFlow<ChatMessage>()
    val incomingMessages = _incomingMessages.asSharedFlow()

    fun connect(token: String) {
        val request = Request.Builder()
            .url("wss://api.chatapp.com/ws")
            .addHeader("Authorization", "Bearer $token")
            .build()

        webSocket = okHttpClient.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                _connectionState.value = ConnectionState.Connected
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                scope.launch {
                    val message = Json.decodeFromString<ChatMessage>(text)
                    // Persist immediately
                    messageDao.insert(message.toEntity())
                    // Emit for UI
                    _incomingMessages.emit(message)
                    // Send delivery receipt
                    sendAck(message.id)
                }
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                _connectionState.value = ConnectionState.Error(t)
                scheduleReconnect()
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                _connectionState.value = ConnectionState.Disconnected
            }
        })
    }

    fun sendMessage(message: ChatMessage) {
        scope.launch {
            // Optimistic insert
            messageDao.insert(message.toEntity().copy(status = "SENDING"))
            val json = Json.encodeToString(message)
            val sent = webSocket?.send(json) ?: false
            if (!sent) {
                // Queue for later if WebSocket is not connected
                messageDao.updateStatus(message.id, "FAILED")
                offlineQueue.enqueue(message)
            }
        }
    }

    private var reconnectJob: Job? = null
    private fun scheduleReconnect() {
        reconnectJob?.cancel()
        reconnectJob = scope.launch {
            var delay = 1000L
            repeat(5) {
                delay(delay)
                if (connectionState.value !is ConnectionState.Connected) {
                    connect(tokenProvider.getToken())
                }
                delay = minOf(delay * 2, 30_000L) // exponential backoff cap at 30s
            }
        }
    }

    fun disconnect() {
        webSocket?.close(1000, "User disconnected")
        reconnectJob?.cancel()
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// OkHttp WebSocket setup
val okHttpClient = OkHttpClient.Builder()
    .pingInterval(30, TimeUnit.SECONDS) // Keep-alive ping
    .connectTimeout(10, TimeUnit.SECONDS)
    .readTimeout(0, TimeUnit.MILLISECONDS) // No timeout for persistent connection
    .build()

// Message ordering with sequence numbers
data class ChatMessage(
    val id: String,
    val seq: Long,          // Server-assigned sequence number
    val conversationId: String,
    val content: String,
    val senderId: String,
    val timestamp: Long
)

// Handle out-of-order messages
class MessageOrderBuffer {
    private val buffer = TreeMap<Long, ChatMessage>()
    private var expectedSeq = 1L

    fun receive(msg: ChatMessage): List<ChatMessage> {
        buffer[msg.seq] = msg
        val ready = mutableListOf<ChatMessage>()
        while (buffer.containsKey(expectedSeq)) {
            ready.add(buffer.remove(expectedSeq)!!)
            expectedSeq++
        }
        return ready
    }
}</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example</h3>
      <p><strong>Automotive Fleet Chat (Driver &lt;-&gt; Dispatcher):</strong> Drivers must receive dispatch instructions even in poor network. We run WebSocket in a ForegroundService with a permanent notification. When network drops, we fall back to FCM push for urgent messages. All messages are queued locally and bulk-synced on reconnect.</p>
      <pre class="code-block"><code class="language-kotlin">// Foreground Service for persistent WebSocket
class ChatService : Service() {
    @Inject lateinit var webSocketManager: ChatWebSocketManager
    private val serviceScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIFICATION_ID, buildNotification())
        serviceScope.launch { webSocketManager.connect(getToken()) }
        return START_STICKY  // Restart if killed by system
    }

    override fun onDestroy() {
        webSocketManager.disconnect()
        serviceScope.cancel()
    }

    private fun buildNotification() = NotificationCompat.Builder(this, CHANNEL_ID)
        .setContentTitle("Chat Active")
        .setSmallIcon(R.drawable.ic_chat)
        .setPriority(NotificationCompat.PRIORITY_LOW)
        .build()
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Opening WebSocket in Activity:</strong> Connection lost on rotation or background — ✅ Fix: Run in a bound ForegroundService or process-level singleton</li>
        <li>❌ <strong>No ping/pong keep-alive:</strong> Connection silently drops — ✅ Fix: Set pingInterval(30, SECONDS) on OkHttpClient</li>
        <li>❌ <strong>Displaying messages without ordering guarantee:</strong> Out-of-order messages corrupt conversation — ✅ Fix: Use server-assigned sequence numbers and a reorder buffer</li>
        <li>❌ <strong>Reconnecting aggressively:</strong> Thundering herd on server restart — ✅ Fix: Exponential backoff with jitter, cap at 30s</li>
        <li>❌ <strong>Not handling duplicate messages:</strong> On reconnect, server may replay recent messages — ✅ Fix: Use message ID as PrimaryKey with REPLACE strategy in Room</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"For a chat app, I run WebSocket in a ForegroundService for lifecycle independence. OkHttp handles the WebSocket with 30-second ping intervals to keep NATs happy. All incoming messages are immediately persisted to Room before emitting to UI — never lose a message. Delivery receipts flow back through the same WebSocket. The two hard problems: reconnection (exponential backoff with jitter, max 30s) and message ordering (server sequence numbers + client reorder buffer for network reordering). For offline: FCM as a fallback transport for urgent messages when WebSocket is down. I always separate the transport layer from the message store so we can swap WebSocket for MQTT without changing the UI."</p>
      </div>
    </div>
  </div>

  <!-- Q&A Section -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the difference between offline-first and cache-first architecture?</div>
      <div class="qa-answer">
        <p><strong>Cache-first:</strong> Try cache, fall back to network if cache is empty or expired. Network is still required for first load. User experience degrades without internet.</p>
        <p><strong>Offline-first:</strong> Local DB is the <em>always</em> source of truth. Writes go to local DB first. Network is a sync layer, not a requirement. App works fully without internet. Sync happens opportunistically when network is available.</p>
        <p>Key difference: in offline-first, you design for network absence as the default, not the exception.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q2</span>How do you handle conflicts in an offline-first app when the same data is modified on two devices?</div>
      <div class="qa-answer">
        <p>There are three main strategies:</p>
        <ol>
          <li><strong>Server wins:</strong> Remote version always overwrites local. Simple, safe for read-heavy data. User loses local edits.</li>
          <li><strong>Last-write-wins (LWW):</strong> Compare timestamps, newer wins. Works for user-specific data. Requires synchronized clocks (use server timestamps, not device).</li>
          <li><strong>CRDT (Conflict-free Replicated Data Types):</strong> Data structures designed to merge without conflicts. Counter increments, set unions. Complex to implement but truly conflict-free.</li>
          <li><strong>Three-way merge:</strong> Compare local, remote, and common ancestor. Show user a diff UI for manual resolution (Google Docs approach).</li>
        </ol>
        <p>For most mobile apps: server-wins for shared data, LWW for personal data, prompt user for collaborative documents.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>How does Paging 3's RemoteMediator enable offline-first pagination?</div>
      <div class="qa-answer">
        <p>RemoteMediator acts as a bridge between the network source and Room. It is called by Paging when the local data is exhausted (APPEND) or on REFRESH. It fetches from network, writes to Room, and Room's PagingSource (which is the UI's data source) automatically emits new pages.</p>
        <p>This means: <strong>the UI always reads from Room</strong> (works offline), <strong>RemoteMediator populates Room from network</strong> (syncs when online). Set <code>initialLoadSize</code> and cache the Pager in ViewModel with <code>.cachedIn(viewModelScope)</code> to survive rotation.</p>
        <pre class="code-block"><code class="language-kotlin">val pager = Pager(
    config = PagingConfig(pageSize = 20, enablePlaceholders = false),
    remoteMediator = ArticleRemoteMediator(api, db),
    pagingSourceFactory = { db.articleDao().pagingSource() }
).flow.cachedIn(viewModelScope)</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q4</span>Your WebSocket chat app loses messages during network switches (WiFi to LTE). How do you fix it?</div>
      <div class="qa-answer">
        <p>This is a classic reconnection + message replay problem. Solution:</p>
        <ol>
          <li><strong>Track last received sequence number</strong> per conversation in Room.</li>
          <li>On reconnect, send a <code>SYNC</code> frame: <code>{"type":"sync","lastSeq":1234,"conversationId":"abc"}</code></li>
          <li>Server replays all messages with seq &gt; lastSeq.</li>
          <li>Client deduplicates using Room's <code>OnConflictStrategy.IGNORE</code>.</li>
          <li>Implement <strong>ConnectivityManager.NetworkCallback</strong> to detect network switches and trigger reconnect immediately (don't wait for socket error).</li>
        </ol>
        <pre class="code-block"><code class="language-kotlin">// On reconnect
val lastSeq = messageDao.getLastSeq(conversationId)
webSocket.send("""{"type":"sync","lastSeq":$lastSeq}""")</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q5</span>How would you design a Payment SDK for Android that other apps can integrate?</div>
      <div class="qa-answer">
        <p>A Payment SDK must be: secure, easy to integrate, tamper-resistant, and PCI-DSS compliant.</p>
        <ol>
          <li><strong>Minimal surface area:</strong> Expose only a single entry point — <code>PaymentClient.present(activity, request, callback)</code>. Internals are hidden.</li>
          <li><strong>Isolated Activity:</strong> Launch your own Activity with <code>startActivityForResult</code> or <code>ActivityResultLauncher</code>. Card data never touches host app's memory.</li>
          <li><strong>Certificate pinning:</strong> Pin your payment server's public key in OkHttp. Prevents MITM even on rooted devices.</li>
          <li><strong>Obfuscation:</strong> R8 with aggressive rules. No card number in logs ever.</li>
          <li><strong>Keystore for tokens:</strong> Store payment tokens in Android Keystore, never SharedPreferences.</li>
          <li><strong>Root/emulator detection:</strong> Refuse to process payments on compromised devices (configurable by SDK consumer).</li>
          <li><strong>Versioned API:</strong> PaymentRequest v1, v2 — backwards compatible with deprecation warnings.</li>
        </ol>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q6</span>What are the trade-offs between REST, GraphQL, and gRPC for Android apps?</div>
      <div class="qa-answer">
        <p><strong>REST:</strong> Simple, universally supported, HTTP caching (ETags, Cache-Control), easy to debug. Over-fetching (too many fields), under-fetching (N+1 requests). Best for: CRUD-heavy apps with simple relationships.</p>
        <p><strong>GraphQL:</strong> Fetch exactly the fields the UI needs, no over/under-fetching, single endpoint, introspection. Complex caching (Apollo handles it), higher server complexity. Best for: complex UIs with many related entities (social feeds, dashboards).</p>
        <p><strong>gRPC:</strong> Protocol Buffers (smaller payload, faster parse than JSON), strong typing, bidirectional streaming. Harder to debug (binary format), less browser support, requires code generation. Best for: microservice-to-microservice, real-time streaming (telemetry, live prices).</p>
        <p>My default: REST for new projects. GraphQL when UI has complex data requirements. gRPC for real-time streaming or internal service calls.</p>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge: Design an LRU Image Cache</h3>
    <p><strong>Problem:</strong> Design a thread-safe in-memory LRU image cache for an Android news feed. It should evict the least recently used bitmap when the cache exceeds a maximum byte size. Implement get(key), put(key, bitmap), and automatic eviction.</p>
    <pre class="code-block"><code class="language-kotlin">import java.util.LinkedHashMap

class BitmapLruCache(private val maxBytes: Long) {
    // LinkedHashMap with accessOrder=true maintains LRU order
    private val cache = object : LinkedHashMap<String, ByteArray>(16, 0.75f, true) {
        override fun removeEldestEntry(eldest: Map.Entry<String, ByteArray>): Boolean {
            return currentBytes > maxBytes
        }
    }
    private var currentBytes = 0L
    private val lock = Any()

    fun get(key: String): ByteArray? = synchronized(lock) {
        cache[key]  // access updates LRU order
    }

    fun put(key: String, data: ByteArray) = synchronized(lock) {
        // Remove old entry if exists
        cache.remove(key)?.also { currentBytes -= it.size }
        cache[key] = data
        currentBytes += data.size
        // LinkedHashMap.removeEldestEntry handles eviction automatically
    }

    fun evict(key: String) = synchronized(lock) {
        cache.remove(key)?.also { currentBytes -= it.size }
    }

    fun clear() = synchronized(lock) {
        cache.clear()
        currentBytes = 0
    }

    fun size() = synchronized(lock) { currentBytes }

    // Production addition: hit rate tracking
    private var hits = 0L
    private var misses = 0L
    fun hitRate() = synchronized(lock) { if (hits + misses == 0L) 0.0 else hits.toDouble() / (hits + misses) }
}

// Usage
val cache = BitmapLruCache(maxBytes = 20 * 1024 * 1024L) // 20 MB

// Time: O(1) for get/put (HashMap + LinkedList pointer update)
// Space: O(n) where n is number of cached items up to maxBytes</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="38" data-item="0"> ✅ Understood Why &amp; What</label>
    <label class="progress-check"><input type="checkbox" data-topic="38" data-item="1"> ✅ Can explain How it works internally</label>
    <label class="progress-check"><input type="checkbox" data-topic="38" data-item="2"> ✅ Reviewed Common Mistakes</label>
    <label class="progress-check"><input type="checkbox" data-topic="38" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="38" data-item="4"> ✅ Solved Coding Challenge</label>
  </div>
</section>

<!-- ============================================================ -->
<!-- TOPIC 39: App Release & Distribution                         -->
<!-- ============================================================ -->
<section class="topic-section" id="topic-39">
  <div class="topic-header">
    <div class="topic-header-icon">🚀</div>
    <div class="topic-header-text">
      <h1>App Release &amp; Distribution</h1>
      <p class="topic-tagline">APK vs AAB, ProGuard/R8, keystore, versioning, staged rollouts, and in-app updates</p>
      <div class="category-badge-group">
        <span class="cat-pill">Release Engineering</span>
        <span class="cat-pill">Play Store</span>
        <span class="cat-pill">Distribution</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 39-1: APK vs AAB and Build Variants -->
  <div class="subtopic" id="subtopic-39-1">
    <h2>APK vs AAB &amp; Build Configuration</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>A poorly configured release costs you: larger APK means fewer installs (every 10MB increase in APK size = ~1% fewer installs per Google's research), missing ProGuard rules expose business logic and crash production builds, a compromised keystore means you can never update your app, and a bad rollout strategy means a crashing release hits 100% of users before you can react. Understanding the release pipeline is what separates junior devs from senior engineers.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p><strong>APK (Android Package Kit):</strong> A single archive containing compiled code, resources, and assets for ALL device configurations. Historically the only distribution format.</p>
      <p><strong>AAB (Android App Bundle):</strong> A publishing format (not installable directly) that contains all code and resources separated by configuration. Google Play uses it to generate optimized APKs for each device — called <strong>Dynamic Delivery</strong>. Users download only the ABI, density, and language splits they need.</p>
      <p><strong>Savings:</strong> AAB typically reduces download size by 15-40% vs universal APK. At scale (millions of users) this is enormous.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// build.gradle.kts — Production-grade release config

android {
    compileSdk = 34
    defaultConfig {
        applicationId = "com.company.app"
        minSdk = 24
        targetSdk = 34
        versionCode = computeVersionCode()     // auto from CI
        versionName = "4.2.1"

        // Inject build metadata into BuildConfig
        buildConfigField("String", "API_BASE_URL", "\"${getProperty("PROD_API_URL")}\"")
        buildConfigField("String", "BUILD_TIME", "\"${System.currentTimeMillis()}\"")
    }

    signingConfigs {
        create("release") {
            // NEVER hardcode keystore in build file
            // Read from environment variables (CI) or local.properties (dev)
            storeFile = file(System.getenv("KEYSTORE_PATH") ?: localProperties["keystore.path"]!!)
            storePassword = System.getenv("KEYSTORE_PASSWORD") ?: localProperties["keystore.password"]!!
            keyAlias = System.getenv("KEY_ALIAS") ?: localProperties["key.alias"]!!
            keyPassword = System.getenv("KEY_PASSWORD") ?: localProperties["key.password"]!!
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")

            // Ensure release builds have no debug overhead
            isDebuggable = false
            isPseudoLocalesEnabled = false
        }
        debug {
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-DEBUG"
            isDebuggable = true
        }
        create("staging") {
            initWith(getByName("release"))
            applicationIdSuffix = ".staging"
            versionNameSuffix = "-STAGING"
            // Staging: minified like release but with debug signing for side-loading
            signingConfig = signingConfigs.getByName("debug")
        }
    }

    // Bundle config for AAB
    bundle {
        language { enableSplit = true }       // Download only user's language
        density { enableSplit = true }         // Download only screen density resources
        abi { enableSplit = true }             // Download only device ABI (arm64, x86, etc.)
    }

    // Dynamic Feature Modules (on-demand features)
    dynamicFeatures += setOf(":feature_premium", ":feature_ar")
}

// Compute versionCode from git commit count (CI-friendly)
fun computeVersionCode(): Int {
    return try {
        val process = ProcessBuilder("git", "rev-list", "--count", "HEAD")
            .start()
        process.inputStream.bufferedReader().readText().trim().toInt()
    } catch (e: Exception) {
        1 // fallback for environments without git
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 ProGuard / R8 Rules</h3>
      <pre class="code-block"><code class="language-kotlin">// proguard-rules.pro — Production rules

# Keep data classes used in Gson/Moshi deserialization
-keep class com.company.app.data.model.** { *; }

# Keep Retrofit interfaces
-keep interface com.company.app.data.network.** { *; }

# Keep Room entities
-keep @androidx.room.Entity class * { *; }

# Keep Parcelable implementations
-keep class * implements android.os.Parcelable {
    public static final android.os.Parcelable$Creator *;
}

# Keep Kotlin Serialization
-keepattributes *Annotation*
-keep @kotlinx.serialization.Serializable class * { *; }

# Keep enum names (Gson uses them by default)
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# Don't warn about missing classes from optional dependencies
-dontwarn org.bouncycastle.**
-dontwarn okio.**

# R8 full mode optimizations (very aggressive — test thoroughly)
# Enable in gradle.properties:
# android.enableR8.fullMode=true

# Keep crash reporter classes
-keep class com.google.firebase.crashlytics.** { *; }

# For debugging R8 issues, generate a mapping file
# -printmapping build/outputs/mapping/release/mapping.txt
# Upload this to Play Console for deobfuscated stack traces</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example</h3>
      <p><strong>E-Commerce app release pipeline:</strong> We reduced download size from 48MB to 29MB by switching to AAB with language/density splits, enabling R8 full mode, and removing unused resources via strict lint rules. Versioning is automated — versionCode = git commit count, versionName = semantic version from git tags. Keystore lives in AWS Secrets Manager, injected into CI (GitHub Actions) at build time. The keystore is backed up encrypted in two separate AWS regions — losing it means you can never update the app.</p>
      <pre class="code-block"><code class="language-kotlin">// GitHub Actions release workflow snippet (as reference)
// jobs:
//   release:
//     steps:
//       - name: Decode keystore
//         run: echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > keystore.jks
//       - name: Build release bundle
//         run: ./gradlew bundleRelease
//         env:
//           KEYSTORE_PATH: keystore.jks
//           KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
//           KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
//           KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
//       - name: Upload to Play Store
//         uses: r0adkll/upload-google-play@v1

// Versioning strategy: Major.Minor.Patch + Build
// 4.2.1 = Major breaking change.Feature.Bug fix
// versionCode auto-increments from git history</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Hardcoding keystore passwords in build.gradle:</strong> Committed to git, security breach — ✅ Fix: Read from environment variables or local.properties (gitignored)</li>
        <li>❌ <strong>Not uploading mapping.txt to Play Console:</strong> Crashes in Firebase/Play Console are obfuscated gibberish — ✅ Fix: Automate mapping.txt upload in CI pipeline</li>
        <li>❌ <strong>Using APK for Play Store in 2024:</strong> Google mandates AAB since August 2021 for new apps — ✅ Fix: Use bundleRelease, test with bundletool locally</li>
        <li>❌ <strong>Not testing release build before rollout:</strong> ProGuard breaks at runtime what debug builds worked fine — ✅ Fix: Always install the release APK (or use bundletool) and smoke test before uploading</li>
        <li>❌ <strong>Using same versionCode for re-uploads:</strong> Play Store rejects it — ✅ Fix: Auto-increment from CI, never hardcode</li>
        <li>❌ <strong>Forgetting to keep Serializable/Parcelable classes:</strong> Silent crashes in release build — ✅ Fix: Have ProGuard rules for all serialization libraries in your project</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"For release configuration, I enforce strict separation of concerns: secrets live in CI environment variables, never in source control. We use AAB over APK — language/density/ABI splits typically cut download size by 30%. Our versioning is fully automated: versionCode from git commit count (monotonically increasing, CI-safe), versionName from git tags following semver. R8 with full mode gives us 20-30% APK size reduction on top of AAB. The most dangerous thing in a release pipeline is the keystore — we store it in AWS Secrets Manager, backed up encrypted in two regions, with a strict rotation policy. Losing the keystore means the app ID is dead — you'd have to publish a new app."</p>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 39-2: Play Store Staged Rollout & In-App Updates -->
  <div class="subtopic" id="subtopic-39-2">
    <h2>Staged Rollout &amp; In-App Updates</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Releasing to 100% of users immediately is a high-risk strategy. A critical bug (crash, data loss, security issue) hits your entire user base before you can react. Staged rollout limits blast radius — release to 1% first, monitor crash rates and ANRs, then gradually increase. In-app updates force users on old versions to update when you have a critical security patch or breaking API change.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p><strong>Staged Rollout:</strong> Play Console feature that distributes a new release to a percentage of users (1% → 5% → 20% → 50% → 100%) with monitoring at each stage. You can halt a rollout instantly if metrics deteriorate.</p>
      <p><strong>In-App Updates API:</strong> Android Play Core API that allows your app to prompt users to update from within the app itself, without requiring them to visit the Play Store. Two modes: <strong>Flexible</strong> (download in background, user installs at their convenience) and <strong>Immediate</strong> (full-screen blocking update required before using app — for critical security patches).</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// In-App Updates implementation

class UpdateManager @Inject constructor(
    private val appUpdateManager: AppUpdateManager
) {
    // Check if update is available
    fun checkForUpdate(activity: Activity) {
        appUpdateManager.appUpdateInfo
            .addOnSuccessListener { appUpdateInfo ->
                when {
                    appUpdateInfo.updateAvailability() == UpdateAvailability.UPDATE_AVAILABLE
                    && appUpdateInfo.isUpdateTypeAllowed(AppUpdateType.FLEXIBLE) -> {
                        startFlexibleUpdate(activity, appUpdateInfo)
                    }
                    appUpdateInfo.updateAvailability() == UpdateAvailability.UPDATE_AVAILABLE
                    && appUpdateInfo.clientVersionStalenessDays() ?: -1 >= DAYS_FOR_IMMEDIATE_UPDATE
                    && appUpdateInfo.isUpdateTypeAllowed(AppUpdateType.IMMEDIATE) -> {
                        startImmediateUpdate(activity, appUpdateInfo)
                    }
                }
            }
    }

    private fun startFlexibleUpdate(activity: Activity, appUpdateInfo: AppUpdateInfo) {
        appUpdateManager.startUpdateFlowForResult(
            appUpdateInfo,
            AppUpdateType.FLEXIBLE,
            activity,
            REQUEST_CODE_UPDATE
        )
        // Monitor download progress
        appUpdateManager.registerListener(installStateUpdatedListener)
    }

    private val installStateUpdatedListener = InstallStateUpdatedListener { state ->
        when (state.installStatus()) {
            InstallStatus.DOWNLOADED -> {
                // Show snackbar to user: "Update ready — tap to install"
                showInstallSnackbar()
            }
            InstallStatus.FAILED -> {
                // Log to analytics, allow user to retry
            }
            InstallStatus.CANCELED -> { /* user dismissed */ }
        }
    }

    fun completeUpdate() {
        // Call when user taps "Install Now" in snackbar
        appUpdateManager.completeUpdate()
    }

    private fun startImmediateUpdate(activity: Activity, appUpdateInfo: AppUpdateInfo) {
        // Blocks app usage until update is complete
        // Use only for critical security patches
        appUpdateManager.startUpdateFlowForResult(
            appUpdateInfo,
            AppUpdateType.IMMEDIATE,
            activity,
            REQUEST_CODE_UPDATE
        )
    }

    // IMPORTANT: Resume interrupted immediate updates on app restart
    fun resumeImmediateUpdateIfNeeded(activity: Activity) {
        appUpdateManager.appUpdateInfo.addOnSuccessListener { info ->
            if (info.updateAvailability() == UpdateAvailability.DEVELOPER_TRIGGERED_UPDATE_IN_PROGRESS) {
                appUpdateManager.startUpdateFlowForResult(
                    info, AppUpdateType.IMMEDIATE, activity, REQUEST_CODE_UPDATE
                )
            }
        }
    }

    companion object {
        const val REQUEST_CODE_UPDATE = 500
        const val DAYS_FOR_IMMEDIATE_UPDATE = 14
    }
}

// In Activity / ViewModel
class MainActivity : AppCompatActivity() {
    @Inject lateinit var updateManager: UpdateManager

    override fun onResume() {
        super.onResume()
        // Always check for pending immediate update on resume
        updateManager.resumeImmediateUpdateIfNeeded(this)
    }

    override fun onStart() {
        super.onStart()
        updateManager.checkForUpdate(this)
    }
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 App Bundle Delivery &amp; Feature Modules</h3>
      <pre class="code-block"><code class="language-kotlin">// Dynamic Feature Module — on-demand download
// In feature module's AndroidManifest.xml:
// <dist:module dist:onDemand="true" dist:title="@string/title_premium">
//   <dist:fusing dist:include="true"/>
// </dist:module>

// Download a dynamic feature on demand
class PremiumFeatureManager @Inject constructor(
    private val splitInstallManager: SplitInstallManager
) {
    fun installPremiumFeature(onSuccess: () -> Unit, onError: (Int) -> Unit) {
        val request = SplitInstallRequest.newBuilder()
            .addModule("feature_premium")
            .build()

        splitInstallManager.startInstall(request)
            .addOnSuccessListener { sessionId ->
                // Monitor download
                splitInstallManager.registerListener { state ->
                    when (state.status()) {
                        SplitInstallSessionStatus.INSTALLED -> onSuccess()
                        SplitInstallSessionStatus.FAILED -> onError(state.errorCode())
                        SplitInstallSessionStatus.DOWNLOADING -> {
                            val progress = (state.bytesDownloaded() * 100 / state.totalBytesToDownload()).toInt()
                            // Update progress UI
                        }
                    }
                }
            }
    }

    fun isInstalled(moduleName: String): Boolean =
        splitInstallManager.installedModules.contains(moduleName)
}

// App Bundle Delivery Config in build.gradle.kts
android {
    bundle {
        language { enableSplit = true }
        density { enableSplit = true }
        abi { enableSplit = true }
    }
}

// Test locally with bundletool
// bundletool build-apks --bundle=app-release.aab --output=app.apks --ks=keystore.jks --ks-key-alias=key
// bundletool install-apks --apks=app.apks</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example</h3>
      <p><strong>FinTech App Critical Security Patch:</strong> A vulnerability was discovered in our token storage. We needed all users on the patched version ASAP. We used IMMEDIATE in-app update for users on vulnerable versions (detected via /version-check API), bypassed staged rollout (released to 100% immediately with expedited review), and monitored crash rate in real-time. The immediate update dialog cannot be dismissed — users must update. Within 6 hours, 89% of active users were on the patched version.</p>
      <pre class="code-block"><code class="language-kotlin">// Server-side version enforcement
class VersionCheckInterceptor @Inject constructor(
    private val versionConfig: VersionConfig
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val response = chain.proceed(chain.request())
        if (response.code == 426) { // 426 Upgrade Required
            // Trigger immediate update UI
            versionConfig.setForceUpdateRequired(true)
        }
        return response
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Not calling resumeImmediateUpdateIfNeeded on resume:</strong> User kills app mid-download, update never completes — ✅ Fix: Always call in onResume to resume interrupted downloads</li>
        <li>❌ <strong>Using IMMEDIATE update for non-critical updates:</strong> Very user-hostile, high abandonment — ✅ Fix: IMMEDIATE only for security patches or breaking API changes; FLEXIBLE for feature updates</li>
        <li>❌ <strong>Not monitoring staged rollout metrics:</strong> Problems go undetected — ✅ Fix: Set up alerts for crash rate &gt; baseline in Firebase/Play Console before each percentage increase</li>
        <li>❌ <strong>Forgetting to unregister InstallStateUpdatedListener:</strong> Memory leak — ✅ Fix: Unregister in onStop/onDestroy or use a ViewModel-scoped listener</li>
        <li>❌ <strong>Staged rollout with incompatible API change:</strong> Old version users get API errors — ✅ Fix: API must be backwards compatible for the rollout duration; use versioned endpoints</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Our release process: build AAB in CI, automated smoke tests on Firebase Test Lab, upload to Play Console internal track. From internal we promote to alpha (internal testers), then beta (open testing), then production at 1% rollout. At each stage we monitor crash-free rate, ANR rate, and rating delta. We have an automated halt trigger — if crash-free sessions drop more than 0.5 percentage points above baseline, the rollout auto-halts via Play Developer API. For forced updates, we use the In-App Update API: FLEXIBLE for normal releases, IMMEDIATE only for security critical patches. We also have server-side enforcement — our API returns 426 Upgrade Required for versions below the minimum supported version, triggering in-app update flow."</p>
      </div>
    </div>
  </div>

  <!-- Q&A Section -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the difference between APK and AAB? Why did Google mandate AAB?</div>
      <div class="qa-answer">
        <p><strong>APK:</strong> A complete, installable package containing all resources for all device configurations (all screen densities, all languages, all ABIs). Large download size — users download resources they'll never use.</p>
        <p><strong>AAB:</strong> A publishing format that includes all configurations separated. Google Play generates device-optimized APKs server-side (Dynamic Delivery). Users download only what their device needs — typically 15-40% smaller.</p>
        <p><strong>Why mandated:</strong> Google mandated AAB for new apps from August 2021 because smaller APKs = higher install rates = better user experience = more revenue for developers and Google. The savings at millions of installs are significant in bandwidth and storage.</p>
        <p>You cannot install an AAB directly — use bundletool locally for testing: <code>bundletool build-apks --bundle=release.aab --output=app.apks</code></p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q2</span>Explain how R8 differs from ProGuard and what "full mode" means.</div>
      <div class="qa-answer">
        <p><strong>ProGuard:</strong> The original bytecode optimizer/obfuscator/shrinker. Works on JVM bytecode. Slower, less aggressive optimization.</p>
        <p><strong>R8:</strong> Google's replacement for ProGuard (default since Android Gradle Plugin 3.4). R8 compiles directly from bytecode to optimized DEX in a single pass — faster build times. R8 applies more aggressive dead code elimination and inlining.</p>
        <p><strong>R8 Full Mode:</strong> Enabled with <code>android.enableR8.fullMode=true</code> in gradle.properties. Makes additional assumptions: if a class/method is not directly referenced in code, it can be removed even if it could theoretically be accessed via reflection. Gives 5-15% additional size reduction but requires more thorough keep rules. Always run full integration tests with full mode enabled.</p>
        <p>Key difference in practice: R8 full mode will aggressively remove classes that ProGuard would keep "just in case." You MUST have explicit keep rules for: Gson/Moshi models, Retrofit interfaces, Room entities, and anything accessed via reflection.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>Your app has a critical bug. How do you respond using Play Store tools?</div>
      <div class="qa-answer">
        <ol>
          <li><strong>Immediately halt the staged rollout</strong> in Play Console (if not at 100%)</li>
          <li>If at 100%: use <strong>Emergency Halt</strong> — this stops distribution of the current version but users who installed it are unaffected</li>
          <li><strong>Roll back:</strong> Promote the previous stable version back to production (Play Console supports this)</li>
          <li>Fix the bug, build new version with incremented versionCode</li>
          <li>Use <strong>IMMEDIATE in-app update</strong> to force affected users to update</li>
          <li>If data corruption possible: use server-side API to reject requests from affected versionCodes (return 426) to force update</li>
          <li><strong>Post-mortem:</strong> Add the crash scenario to integration test suite, add monitoring alert for similar crash signatures</li>
        </ol>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q4</span>Your company lost the keystore file. What happens and how do you prevent this?</div>
      <div class="qa-answer">
        <p><strong>What happens:</strong> You can never update the app under the same package name. Google Play requires all updates to be signed with the same key as the original upload. The existing app on the Play Store becomes permanently stranded — you must publish a new app with a new package ID and ask users to reinstall.</p>
        <p><strong>Prevention strategies:</strong></p>
        <ol>
          <li><strong>Play App Signing:</strong> Enroll in Google's Play App Signing program. Google holds your app signing key (in their HSM). You upload with an upload key (which you control). If you lose the upload key, Google can reset it. The actual signing key is safe with Google.</li>
          <li><strong>Backup:</strong> Store encrypted keystore in multiple locations — AWS Secrets Manager, separate AWS region backup, offline encrypted USB in a physical safe.</li>
          <li><strong>Access control:</strong> Limit who has keystore access. Use CI environment variables, never commit to git.</li>
          <li><strong>Document recovery procedure:</strong> Written SOP for key rotation/recovery, tested annually.</li>
        </ol>
        <p>Play App Signing is the only truly safe option — highly recommend enrolling.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q5</span>What versioning strategy do you use for versionCode and versionName?</div>
      <div class="qa-answer">
        <p><strong>versionName:</strong> Semantic versioning — MAJOR.MINOR.PATCH (e.g., 4.2.1). MAJOR = breaking changes or significant redesign. MINOR = new features, backwards compatible. PATCH = bug fixes only.</p>
        <p><strong>versionCode:</strong> Must be a monotonically increasing integer. Two common strategies:</p>
        <ol>
          <li><strong>Git commit count:</strong> <code>git rev-list --count HEAD</code> — automatically increments with every commit, CI-friendly, deterministic.</li>
          <li><strong>Timestamp-based:</strong> <code>YYYYMMDDBB</code> where BB is build number of the day — human readable, but requires CI coordination.</li>
        </ol>
        <p>Never hardcode versionCode — it will inevitably be forgotten to increment. Automate it. The CI system should be the only thing that generates release builds, ensuring versionCode is always correct.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>How do you use Dynamic Feature Modules to reduce initial download size?</div>
      <div class="qa-answer">
        <p>Dynamic Feature Modules (DFM) allow you to split optional features out of the base APK into separate modules that are downloaded on-demand.</p>
        <p><strong>Good candidates for DFMs:</strong> AR features, premium/paid features, rarely-used admin tools, large ML models, country-specific compliance features.</p>
        <p><strong>Implementation:</strong> Create a new module with <code>com.android.dynamic-feature</code> plugin. Add <code>dist:onDemand="true"</code> in its manifest. In the base app, use SplitInstallManager to download when needed.</p>
        <p><strong>Delivery modes:</strong></p>
        <ul>
          <li><strong>On-demand:</strong> Downloaded when user requests the feature (explicit SplitInstallRequest)</li>
          <li><strong>Install-time:</strong> Downloaded with initial install (large but critical features)</li>
          <li><strong>Conditional:</strong> Downloaded based on device characteristics (API level, screen size, country)</li>
          <li><strong>Fast-follow:</strong> Downloaded in background shortly after install completes</li>
        </ul>
        <p>Typical savings: a 60MB app with an AR feature can reduce initial install to 35MB by making AR a DFM.</p>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge: Automated Version Code Generator</h3>
    <p><strong>Problem:</strong> Write a Gradle buildSrc utility function that computes a versionCode from git history, and falls back to a default on machines without git. Also write a function that parses semantic versionName and validates it.</p>
    <pre class="code-block"><code class="language-kotlin">// buildSrc/src/main/kotlin/Versioning.kt

object Versioning {
    fun computeVersionCode(): Int {
        return try {
            val process = ProcessBuilder("git", "rev-list", "--count", "HEAD")
                .redirectErrorStream(true)
                .start()
            process.waitFor(10, java.util.concurrent.TimeUnit.SECONDS)
            val output = process.inputStream.bufferedReader().readText().trim()
            output.toIntOrNull() ?: 1
        } catch (e: Exception) {
            println("WARNING: git not available, using versionCode=1")
            1
        }
    }

    fun computeVersionName(): String {
        return try {
            // Use latest git tag if available
            val tagProcess = ProcessBuilder("git", "describe", "--tags", "--abbrev=0")
                .start()
            tagProcess.waitFor(10, java.util.concurrent.TimeUnit.SECONDS)
            val tag = tagProcess.inputStream.bufferedReader().readText().trim()
            if (tag.isNotEmpty() && tag.matches(Regex("v?\\d+\\.\\d+\\.\\d+"))) {
                tag.removePrefix("v")
            } else {
                "1.0.0"
            }
        } catch (e: Exception) {
            "1.0.0"
        }
    }

    fun validateSemanticVersion(version: String): Boolean {
        val semverRegex = Regex("""^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$""")
        return semverRegex.matches(version)
    }
}

// Usage in app/build.gradle.kts:
// defaultConfig {
//     versionCode = Versioning.computeVersionCode()
//     versionName = Versioning.computeVersionName()
// }

// Tests for the validator:
// validateSemanticVersion("4.2.1") == true
// validateSemanticVersion("4.2.1-beta.1") == true
// validateSemanticVersion("4.2") == false (missing patch)
// validateSemanticVersion("v4.2.1") == false (has prefix)</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="39" data-item="0"> ✅ Understood Why &amp; What</label>
    <label class="progress-check"><input type="checkbox" data-topic="39" data-item="1"> ✅ Can explain How it works internally</label>
    <label class="progress-check"><input type="checkbox" data-topic="39" data-item="2"> ✅ Reviewed Common Mistakes</label>
    <label class="progress-check"><input type="checkbox" data-topic="39" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="39" data-item="4"> ✅ Solved Coding Challenge</label>
  </div>
</section>

<!-- ============================================================ -->
<!-- TOPIC 40: DSA Coding Questions in Kotlin                     -->
<!-- ============================================================ -->
<section class="topic-section" id="topic-40">
  <div class="topic-header">
    <div class="topic-header-icon">⚡</div>
    <div class="topic-header-text">
      <h1>DSA Coding Questions in Kotlin</h1>
      <p class="topic-tagline">Master common interview data structures and algorithms in idiomatic Kotlin</p>
      <div class="category-badge-group">
        <span class="cat-pill">DSA</span>
        <span class="cat-pill">Kotlin</span>
        <span class="cat-pill">Algorithms</span>
        <span class="cat-pill">Coding Interview</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 40-1: Arrays & Hashing -->
  <div class="subtopic" id="subtopic-40-1">
    <h2>Arrays, Hashing &amp; Two Pointers</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Android interviews at FAANG and top-tier companies include 1-2 LeetCode-style coding rounds. You must be fluent in Kotlin idioms — using idiomatic constructs (groupBy, partition, fold, scan, windowed) shows you know the language deeply. Arrays and hash maps underpin nearly every real-world algorithm: caching, deduplication, frequency counting, and lookup optimization.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p>Fundamental data structures: Arrays (O(1) random access, O(n) insert), HashMaps (O(1) average get/put, O(n) worst case), HashSets (O(1) membership test). Two-pointer technique reduces O(n²) brute-force to O(n) by maintaining invariants with left/right pointers.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ Classic Problems</h3>
      <pre class="code-block"><code class="language-kotlin">// ============================================
// 1. TWO SUM — find indices of two numbers that add to target
// Time: O(n), Space: O(n)
// ============================================
fun twoSum(nums: IntArray, target: Int): IntArray {
    val seen = HashMap<Int, Int>()  // value -> index
    for ((i, num) in nums.withIndex()) {
        val complement = target - num
        if (complement in seen) return intArrayOf(seen[complement]!!, i)
        seen[num] = i
    }
    return intArrayOf()  // guaranteed solution exists per problem
}

// Kotlin idiomatic version using fold:
fun twoSumIdiomatic(nums: IntArray, target: Int): IntArray {
    val seen = mutableMapOf<Int, Int>()
    nums.forEachIndexed { i, num ->
        val complement = target - num
        if (complement in seen) return intArrayOf(seen[complement]!!, i)
        seen[num] = i
    }
    return intArrayOf()
}

// ============================================
// 2. CONTAINS DUPLICATE — Kotlin one-liner
// Time: O(n), Space: O(n)
// ============================================
fun containsDuplicate(nums: IntArray): Boolean = nums.size != nums.toHashSet().size

// ============================================
// 3. GROUP ANAGRAMS — group strings by sorted character signature
// Time: O(n * k log k) where k = max string length
// ============================================
fun groupAnagrams(strs: Array<String>): List<List<String>> {
    return strs.groupBy { it.toCharArray().sorted().joinToString("") }.values.toList()
}

// ============================================
// 4. VALID PALINDROME — Two pointer
// Time: O(n), Space: O(1)
// ============================================
fun isPalindrome(s: String): Boolean {
    val cleaned = s.lowercase().filter { it.isLetterOrDigit() }
    var left = 0; var right = cleaned.length - 1
    while (left < right) {
        if (cleaned[left] != cleaned[right]) return false
        left++; right--
    }
    return true
}

// ============================================
// 5. CONTAINER WITH MOST WATER — Two pointer
// Time: O(n), Space: O(1)
// ============================================
fun maxArea(height: IntArray): Int {
    var left = 0; var right = height.lastIndex; var maxWater = 0
    while (left < right) {
        val water = minOf(height[left], height[right]) * (right - left)
        maxWater = maxOf(maxWater, water)
        // Move the shorter side inward — moving taller side can only decrease area
        if (height[left] < height[right]) left++ else right--
    }
    return maxWater
}

// ============================================
// 6. PRODUCT OF ARRAY EXCEPT SELF — No division
// Time: O(n), Space: O(1) output array
// ============================================
fun productExceptSelf(nums: IntArray): IntArray {
    val n = nums.size
    val result = IntArray(n) { 1 }
    // Left pass: result[i] = product of all elements left of i
    var leftProduct = 1
    for (i in nums.indices) { result[i] = leftProduct; leftProduct *= nums[i] }
    // Right pass: multiply by product of all elements right of i
    var rightProduct = 1
    for (i in nums.indices.reversed()) { result[i] *= rightProduct; rightProduct *= nums[i] }
    return result
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Sliding Window Problems</h3>
      <pre class="code-block"><code class="language-kotlin">// ============================================
// LONGEST SUBSTRING WITHOUT REPEATING CHARACTERS
// Time: O(n), Space: O(min(n, 26))
// ============================================
fun lengthOfLongestSubstring(s: String): Int {
    val charIndex = HashMap<Char, Int>()
    var maxLen = 0; var left = 0
    for ((right, c) in s.withIndex()) {
        // If character already in window, shrink window from left
        left = maxOf(left, (charIndex[c] ?: -1) + 1)
        charIndex[c] = right
        maxLen = maxOf(maxLen, right - left + 1)
    }
    return maxLen
}

// ============================================
// MINIMUM WINDOW SUBSTRING
// Time: O(n + m), Space: O(m)
// ============================================
fun minWindow(s: String, t: String): String {
    if (t.isEmpty()) return ""
    val need = t.groupingBy { it }.eachCount().toMutableMap()
    var have = 0; val required = need.size
    var left = 0; var minLen = Int.MAX_VALUE; var result = ""
    val window = HashMap<Char, Int>()

    for ((right, c) in s.withIndex()) {
        window[c] = (window[c] ?: 0) + 1
        if (c in need && window[c] == need[c]) have++

        while (have == required) {
            // Update result if smaller window found
            if (right - left + 1 < minLen) {
                minLen = right - left + 1
                result = s.substring(left, right + 1)
            }
            // Shrink window from left
            val leftChar = s[left]
            window[leftChar] = window[leftChar]!! - 1
            if (leftChar in need && window[leftChar]!! < need[leftChar]!!) have--
            left++
        }
    }
    return result
}

// ============================================
// SLIDING WINDOW MAXIMUM (Deque/Monotonic Queue)
// Time: O(n), Space: O(k)
// ============================================
fun maxSlidingWindow(nums: IntArray, k: Int): IntArray {
    val deque = ArrayDeque<Int>()  // stores indices, maintains decreasing order of values
    val result = IntArray(nums.size - k + 1)

    for (i in nums.indices) {
        // Remove indices outside window
        while (deque.isNotEmpty() && deque.first() < i - k + 1) deque.removeFirst()
        // Remove smaller elements from back (they can never be max)
        while (deque.isNotEmpty() && nums[deque.last()] < nums[i]) deque.removeLast()
        deque.addLast(i)
        if (i >= k - 1) result[i - k + 1] = nums[deque.first()]
    }
    return result
}</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example</h3>
      <p><strong>Android Rate Limiter using Sliding Window:</strong> Prevent users from spamming a "Report" button — allow max 3 reports per 60 seconds.</p>
      <pre class="code-block"><code class="language-kotlin">class SlidingWindowRateLimiter(
    private val maxRequests: Int,
    private val windowMs: Long
) {
    private val timestamps = ArrayDeque<Long>()

    @Synchronized
    fun tryAcquire(): Boolean {
        val now = System.currentTimeMillis()
        val windowStart = now - windowMs
        // Evict timestamps outside window
        while (timestamps.isNotEmpty() && timestamps.first() < windowStart) {
            timestamps.removeFirst()
        }
        return if (timestamps.size < maxRequests) {
            timestamps.addLast(now)
            true  // allowed
        } else {
            false // rate limited
        }
    }
}

// Usage
val reportRateLimiter = SlidingWindowRateLimiter(maxRequests = 3, windowMs = 60_000)
if (reportRateLimiter.tryAcquire()) {
    submitReport()
} else {
    showError("Too many reports. Please wait.")
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Using == for Integer comparison in Java/Kotlin boxed types:</strong> Integer cache only works for -128 to 127 — ✅ Fix: In Kotlin, use == (structural equality) which is always safe; avoid Java Integer boxing issues</li>
        <li>❌ <strong>Modifying a list while iterating it:</strong> ConcurrentModificationException — ✅ Fix: Collect indices to modify first, then apply changes, or use iterator.remove()</li>
        <li>❌ <strong>Off-by-one in sliding window:</strong> Missing last element or going out of bounds — ✅ Fix: Carefully trace through with a 3-element example before coding</li>
        <li>❌ <strong>Using Array instead of IntArray in Kotlin for primitives:</strong> Boxing overhead — ✅ Fix: Use IntArray, LongArray, etc. for primitive performance</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Before coding, I always state my approach: 'The brute-force is O(n²) but I can reduce to O(n) using a HashMap to trade space for time — complementary lookup in O(1).' I write clean, idiomatic Kotlin — using withIndex() instead of a manual counter, data class destructuring, and extension functions. I call out time and space complexity as I write each step, not just at the end. I also mention edge cases: empty input, all duplicates, integer overflow. The interviewer is looking for problem decomposition clarity, not just a correct solution."</p>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 40-2: Trees, Graphs, DP -->
  <div class="subtopic" id="subtopic-40-2">
    <h2>Trees, Graphs &amp; Dynamic Programming</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Tree and graph problems appear in senior Android interviews because they test recursive thinking and BFS/DFS — skills needed for navigating Android's View hierarchy, dependency graphs in DI frameworks, and navigation graph traversal. Dynamic programming shows you can identify overlapping subproblems and optimize exponential brute-force to polynomial time.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p><strong>Trees:</strong> Hierarchical structures with O(log n) operations when balanced. BST for sorted data, Tries for prefix matching (autocomplete), Binary Trees for expression evaluation.</p>
      <p><strong>Graphs:</strong> Nodes + edges. BFS for shortest path (unweighted), DFS for cycle detection/topological sort, Dijkstra for weighted shortest path.</p>
      <p><strong>Dynamic Programming:</strong> Break problem into overlapping subproblems, cache results (memoization = top-down, tabulation = bottom-up). Identify: optimal substructure + overlapping subproblems.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ Classic Tree &amp; Graph Problems</h3>
      <pre class="code-block"><code class="language-kotlin">// Binary Tree Node
data class TreeNode(val `val`: Int, var left: TreeNode? = null, var right: TreeNode? = null)

// ============================================
// INORDER TRAVERSAL (Iterative — preferred in interview)
// Time: O(n), Space: O(h) where h = height
// ============================================
fun inorderTraversal(root: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()
    val stack = ArrayDeque<TreeNode>()
    var current = root
    while (current != null || stack.isNotEmpty()) {
        while (current != null) { stack.addLast(current); current = current.left }
        current = stack.removeLast()
        result.add(current.`val`)
        current = current.right
    }
    return result
}

// ============================================
// MAXIMUM DEPTH OF BINARY TREE
// Time: O(n), Space: O(h)
// ============================================
fun maxDepth(root: TreeNode?): Int {
    if (root == null) return 0
    return 1 + maxOf(maxDepth(root.left), maxDepth(root.right))
}

// ============================================
// LOWEST COMMON ANCESTOR OF BST
// Time: O(log n) for balanced BST
// ============================================
fun lowestCommonAncestor(root: TreeNode, p: TreeNode, q: TreeNode): TreeNode {
    return when {
        p.`val` < root.`val` && q.`val` < root.`val` -> lowestCommonAncestor(root.left!!, p, q)
        p.`val` > root.`val` && q.`val` > root.`val` -> lowestCommonAncestor(root.right!!, p, q)
        else -> root  // split point — this is the LCA
    }
}

// ============================================
// LEVEL ORDER TRAVERSAL (BFS)
// Time: O(n), Space: O(w) where w = max width
// ============================================
fun levelOrder(root: TreeNode?): List<List<Int>> {
    if (root == null) return emptyList()
    val result = mutableListOf<List<Int>>()
    val queue = ArrayDeque<TreeNode>().also { it.add(root) }
    while (queue.isNotEmpty()) {
        val level = mutableListOf<Int>()
        repeat(queue.size) {  // process exactly this level's nodes
            val node = queue.removeFirst()
            level.add(node.`val`)
            node.left?.let { queue.add(it) }
            node.right?.let { queue.add(it) }
        }
        result.add(level)
    }
    return result
}

// ============================================
// NUMBER OF ISLANDS (DFS on grid)
// Time: O(m * n), Space: O(m * n) recursion stack
// ============================================
fun numIslands(grid: Array<CharArray>): Int {
    var count = 0
    for (r in grid.indices) {
        for (c in grid[0].indices) {
            if (grid[r][c] == '1') {
                dfsFlood(grid, r, c)
                count++
            }
        }
    }
    return count
}

private fun dfsFlood(grid: Array<CharArray>, r: Int, c: Int) {
    if (r < 0 || r >= grid.size || c < 0 || c >= grid[0].size || grid[r][c] != '1') return
    grid[r][c] = '0'  // mark visited
    dfsFlood(grid, r + 1, c); dfsFlood(grid, r - 1, c)
    dfsFlood(grid, r, c + 1); dfsFlood(grid, r, c - 1)
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Dynamic Programming Patterns</h3>
      <pre class="code-block"><code class="language-kotlin">// ============================================
// FIBONACCI — Three approaches
// ============================================
// Naive recursive: O(2^n) — NEVER in interview
// Memoization (top-down): O(n) time, O(n) space
fun fibMemo(n: Int, memo: MutableMap<Int, Long> = mutableMapOf()): Long {
    if (n <= 1) return n.toLong()
    return memo.getOrPut(n) { fibMemo(n - 1, memo) + fibMemo(n - 2, memo) }
}
// Tabulation (bottom-up): O(n) time, O(1) space
fun fib(n: Int): Long {
    if (n <= 1) return n.toLong()
    var a = 0L; var b = 1L
    repeat(n - 1) { val tmp = a + b; a = b; b = tmp }
    return b
}

// ============================================
// COIN CHANGE — Classic DP
// Time: O(amount * coins), Space: O(amount)
// ============================================
fun coinChange(coins: IntArray, amount: Int): Int {
    val dp = IntArray(amount + 1) { Int.MAX_VALUE }
    dp[0] = 0
    for (a in 1..amount) {
        for (coin in coins) {
            if (coin <= a && dp[a - coin] != Int.MAX_VALUE) {
                dp[a] = minOf(dp[a], dp[a - coin] + 1)
            }
        }
    }
    return if (dp[amount] == Int.MAX_VALUE) -1 else dp[amount]
}

// ============================================
// LONGEST COMMON SUBSEQUENCE
// Time: O(m * n), Space: O(m * n)
// ============================================
fun longestCommonSubsequence(text1: String, text2: String): Int {
    val m = text1.length; val n = text2.length
    val dp = Array(m + 1) { IntArray(n + 1) }
    for (i in 1..m) {
        for (j in 1..n) {
            dp[i][j] = if (text1[i - 1] == text2[j - 1]) {
                dp[i - 1][j - 1] + 1
            } else {
                maxOf(dp[i - 1][j], dp[i][j - 1])
            }
        }
    }
    return dp[m][n]
}

// ============================================
// 0/1 KNAPSACK — Classic DP
// Time: O(n * W), Space: O(W)
// ============================================
fun knapsack(weights: IntArray, values: IntArray, capacity: Int): Int {
    val dp = IntArray(capacity + 1)
    for (i in weights.indices) {
        for (w in capacity downTo weights[i]) {  // traverse backwards to avoid using item twice
            dp[w] = maxOf(dp[w], dp[w - weights[i]] + values[i])
        }
    }
    return dp[capacity]
}</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example</h3>
      <p><strong>Android Dependency Graph Cycle Detection:</strong> In a custom DI framework, use DFS topological sort to detect circular dependencies at compile time.</p>
      <pre class="code-block"><code class="language-kotlin">// Detect cycles in dependency injection graph
class DependencyGraph {
    private val edges = mutableMapOf<String, MutableList<String>>()

    fun addDependency(from: String, to: String) {
        edges.getOrPut(from) { mutableListOf() }.add(to)
    }

    fun hasCycle(): Boolean {
        val visited = mutableSetOf<String>()
        val inStack = mutableSetOf<String>()

        fun dfs(node: String): Boolean {
            visited.add(node)
            inStack.add(node)
            for (neighbor in edges[node] ?: emptyList()) {
                if (neighbor !in visited && dfs(neighbor)) return true
                if (neighbor in inStack) return true  // back edge = cycle
            }
            inStack.remove(node)
            return false
        }

        return edges.keys.any { it !in visited && dfs(it) }
    }

    fun topologicalSort(): List<String>? {
        val inDegree = mutableMapOf<String, Int>()
        val allNodes = edges.keys + edges.values.flatten()
        allNodes.forEach { inDegree.getOrPut(it) { 0 } }
        edges.forEach { (_, deps) -> deps.forEach { inDegree[it] = (inDegree[it] ?: 0) + 1 } }

        val queue = ArrayDeque(inDegree.filter { it.value == 0 }.keys)
        val result = mutableListOf<String>()
        while (queue.isNotEmpty()) {
            val node = queue.removeFirst()
            result.add(node)
            edges[node]?.forEach { dep ->
                inDegree[dep] = inDegree[dep]!! - 1
                if (inDegree[dep] == 0) queue.add(dep)
            }
        }
        return if (result.size == inDegree.size) result else null  // null = cycle exists
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Not handling null root in tree problems:</strong> NullPointerException — ✅ Fix: Always check if (root == null) return base case at function start</li>
        <li>❌ <strong>Using recursion for very deep trees:</strong> Stack overflow (10,000+ depth) — ✅ Fix: Convert to iterative with explicit stack for production use</li>
        <li>❌ <strong>Forgetting to mark visited in graph BFS/DFS:</strong> Infinite loop on cycles — ✅ Fix: Use a visited HashSet, add node BEFORE enqueuing (not after dequeuing) to prevent re-enqueue</li>
        <li>❌ <strong>DP table initialized incorrectly:</strong> Wrong base cases corrupt all results — ✅ Fix: Trace through a small example by hand before coding, verify dp[0] and dp[1]</li>
        <li>❌ <strong>Integer overflow in DP:</strong> Summing large values exceeds Int range — ✅ Fix: Use Long for DP tables when values can be large; check constraints first</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"For DP problems, I always start by identifying whether I need top-down (memoization) or bottom-up (tabulation). Top-down is easier to reason about — write the naive recursive solution, add a memo map. Bottom-up is more efficient (no recursion overhead, better cache locality). The key is defining the state correctly: dp[i] means 'the answer for the first i elements.' I always draw the recurrence relation before touching the keyboard. For tree problems, I ask whether iterative or recursive is better — recursive is cleaner but iterative avoids stack overflow on degenerate inputs. I mention this trade-off explicitly to show depth."</p>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 40-3: Linked Lists & Stack -->
  <div class="subtopic" id="subtopic-40-3">
    <h2>Linked Lists, Stacks &amp; LRU Cache</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Linked list problems test pointer manipulation precision. LRU Cache is one of the most common Android interview problems because it directly maps to real-world image cache, API response cache, and ViewModel state management. Stacks underpin Android's back stack, expression evaluation, and undo/redo features.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is It?</h3>
      <p>Linked lists: sequential nodes with O(1) insert/delete when you have a pointer to the node, O(n) random access. LRU Cache combines a doubly-linked list (O(1) front/back operations) with a HashMap (O(1) lookup) to achieve O(1) get and put. This is the classic data structure design problem.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ LRU Cache &amp; Linked List Problems</h3>
      <pre class="code-block"><code class="language-kotlin">// ============================================
// LRU CACHE — The classic O(1) get/put implementation
// ============================================
class LRUCache(private val capacity: Int) {
    private data class Node(val key: Int, var value: Int, var prev: Node? = null, var next: Node? = null)

    // Sentinel nodes — eliminate null checks
    private val head = Node(-1, -1)
    private val tail = Node(-1, -1)
    private val map = HashMap<Int, Node>()

    init { head.next = tail; tail.prev = head }

    fun get(key: Int): Int {
        val node = map[key] ?: return -1
        moveToFront(node)
        return node.value
    }

    fun put(key: Int, value: Int) {
        if (key in map) {
            map[key]!!.value = value
            moveToFront(map[key]!!)
        } else {
            if (map.size == capacity) evictLRU()
            val node = Node(key, value)
            map[key] = node
            insertAtFront(node)
        }
    }

    private fun insertAtFront(node: Node) {
        node.next = head.next; node.prev = head
        head.next?.prev = node; head.next = node
    }

    private fun removeNode(node: Node) {
        node.prev?.next = node.next; node.next?.prev = node.prev
    }

    private fun moveToFront(node: Node) { removeNode(node); insertAtFront(node) }

    private fun evictLRU() {
        val lru = tail.prev!!
        removeNode(lru)
        map.remove(lru.key)
    }
}

// ============================================
// REVERSE LINKED LIST
// Time: O(n), Space: O(1)
// ============================================
data class ListNode(val `val`: Int, var next: ListNode? = null)

fun reverseList(head: ListNode?): ListNode? {
    var prev: ListNode? = null; var curr = head
    while (curr != null) {
        val next = curr.next
        curr.next = prev
        prev = curr; curr = next
    }
    return prev
}

// Recursive (elegant but O(n) stack space)
fun reverseListRecursive(head: ListNode?): ListNode? {
    if (head?.next == null) return head
    val newHead = reverseListRecursive(head.next)
    head.next?.next = head; head.next = null
    return newHead
}

// ============================================
// DETECT CYCLE — Floyd's Algorithm (Tortoise &amp; Hare)
// Time: O(n), Space: O(1)
// ============================================
fun hasCycle(head: ListNode?): Boolean {
    var slow = head; var fast = head
    while (fast?.next != null) {
        slow = slow?.next
        fast = fast.next?.next
        if (slow === fast) return true
    }
    return false
}

// ============================================
// MERGE K SORTED LISTS — Min Heap approach
// Time: O(n log k), Space: O(k)
// ============================================
fun mergeKLists(lists: Array<ListNode?>): ListNode? {
    val heap = java.util.PriorityQueue<ListNode>(compareBy { it.`val` })
    lists.forEach { it?.let { heap.offer(it) } }
    val dummy = ListNode(0); var curr: ListNode = dummy
    while (heap.isNotEmpty()) {
        val node = heap.poll()!!
        curr.next = node; curr = node
        node.next?.let { heap.offer(it) }
    }
    return dummy.next
}

// ============================================
// VALID PARENTHESES — Stack
// Time: O(n), Space: O(n)
// ============================================
fun isValid(s: String): Boolean {
    val stack = ArrayDeque<Char>()
    val pairs = mapOf(')' to '(', ']' to '[', '}' to '{')
    for (c in s) {
        if (c in pairs.values) {
            stack.addLast(c)
        } else {
            if (stack.isEmpty() || stack.last() != pairs[c]) return false
            stack.removeLast()
        }
    }
    return stack.isEmpty()
}

// ============================================
// BINARY SEARCH — Idiomatic Kotlin
// Time: O(log n), Space: O(1)
// ============================================
fun binarySearch(nums: IntArray, target: Int): Int {
    var left = 0; var right = nums.lastIndex
    while (left <= right) {
        val mid = left + (right - left) / 2  // avoid integer overflow vs (left+right)/2
        when {
            nums[mid] == target -> return mid
            nums[mid] < target -> left = mid + 1
            else -> right = mid - 1
        }
    }
    return -1
}

// Search in rotated sorted array
fun searchRotated(nums: IntArray, target: Int): Int {
    var left = 0; var right = nums.lastIndex
    while (left <= right) {
        val mid = left + (right - left) / 2
        if (nums[mid] == target) return mid
        // Determine which half is sorted
        if (nums[left] <= nums[mid]) {  // left half sorted
            if (target in nums[left] until nums[mid]) right = mid - 1 else left = mid + 1
        } else {  // right half sorted
            if (target in (nums[mid] + 1)..nums[right]) left = mid + 1 else right = mid - 1
        }
    }
    return -1
}</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Kotlin-Specific DSA Tips</h3>
      <pre class="code-block"><code class="language-kotlin">// Kotlin stdlib functions useful in DSA interviews

// 1. Sorting with custom comparator
val words = arrayOf("banana", "apple", "cherry")
words.sortedWith(compareBy({ it.length }, { it }))  // sort by length, then alphabetically

// 2. Priority Queue (Min Heap)
val minHeap = java.util.PriorityQueue<Int>()  // ascending by default
val maxHeap = java.util.PriorityQueue<Int>(compareByDescending { it })

// 3. Stack operations with ArrayDeque (preferred over Stack)
val stack = ArrayDeque<Int>()
stack.addLast(1)   // push
stack.removeLast() // pop
stack.last()       // peek

// 4. Queue with ArrayDeque
val queue = ArrayDeque<Int>()
queue.addLast(1)    // enqueue
queue.removeFirst() // dequeue
queue.first()       // peek

// 5. Deque (both ends)
val deque = ArrayDeque<Int>()
deque.addFirst(1); deque.addLast(2)
deque.removeFirst(); deque.removeLast()

// 6. Frequency count
val freq = "hello".groupingBy { it }.eachCount()  // {h=1, e=1, l=2, o=1}

// 7. Prefix sums
val nums = intArrayOf(1, 2, 3, 4, 5)
val prefix = IntArray(nums.size + 1)
nums.forEachIndexed { i, v -> prefix[i + 1] = prefix[i] + v }
// Range sum [l, r]: prefix[r+1] - prefix[l]

// 8. Kotlin's built-in binary search
val sorted = intArrayOf(1, 3, 5, 7, 9)
val idx = sorted.binarySearch(5)  // returns index or negative insertion point</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Production Example</h3>
      <p><strong>Android Navigation Back Stack:</strong> The back stack is literally a stack data structure. Understanding how pushBack/popBack work, and how to implement undo/redo in a text editor using two stacks, is directly applicable.</p>
      <pre class="code-block"><code class="language-kotlin">// Undo/Redo with two stacks — text editor feature
class TextEditor {
    private var current = ""
    private val undoStack = ArrayDeque<String>()
    private val redoStack = ArrayDeque<String>()

    fun type(text: String) {
        undoStack.addLast(current)
        redoStack.clear()  // new action clears redo history
        current += text
    }

    fun undo(): String {
        if (undoStack.isEmpty()) return current
        redoStack.addLast(current)
        current = undoStack.removeLast()
        return current
    }

    fun redo(): String {
        if (redoStack.isEmpty()) return current
        undoStack.addLast(current)
        current = redoStack.removeLast()
        return current
    }
}</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Integer overflow in binary search mid calculation:</strong> (left + right) / 2 overflows for large indices — ✅ Fix: Use left + (right - left) / 2</li>
        <li>❌ <strong>Using Stack class in Kotlin:</strong> Stack is synchronized (slow) and has problematic inheritance from Vector — ✅ Fix: Use ArrayDeque for stack/queue operations</li>
        <li>❌ <strong>Infinite loop in Floyd's cycle detection:</strong> Using .equals() instead of reference equality — ✅ Fix: Use === (referential equality) for pointer comparison, not ==</li>
        <li>❌ <strong>Not handling empty linked list:</strong> NPE when head is null — ✅ Fix: Always handle the null case first: if (head == null) return null</li>
        <li>❌ <strong>Forgetting the dummy head node in linked list problems:</strong> Complex edge case handling — ✅ Fix: Use a dummy/sentinel node at head to simplify insert/delete logic</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"For LRU Cache, the insight is combining two data structures: HashMap for O(1) lookup and doubly-linked list for O(1) LRU eviction. I use sentinel (dummy) head and tail nodes to eliminate null checks — a production habit that reduces bugs. I code in idiomatic Kotlin using data classes for nodes. Before each problem I verbalize: constraints, brute-force approach, optimization, and complexity. During coding I narrate my decisions: 'I'm using a deque here because I need O(1) access to both ends.' This demonstrates senior communication — thinking out loud is valued more than speed."</p>
      </div>
    </div>
  </div>

  <!-- Q&A Section -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the time complexity of HashMap get/put in Kotlin/Java and when does it degrade?</div>
      <div class="qa-answer">
        <p><strong>Average case:</strong> O(1) for both get and put — hash function computes index directly.</p>
        <p><strong>Worst case:</strong> O(n) — when many keys hash to the same bucket (hash collision), the bucket degrades to a linked list search. Java 8+ converts buckets to balanced BSTs (TreeMap) when they exceed 8 entries, giving O(log n) worst case instead of O(n).</p>
        <p><strong>When it degrades:</strong></p>
        <ul>
          <li>Poorly implemented hashCode() — e.g., hashCode() returns a constant, all keys go to one bucket</li>
          <li>Keys with natural clustering (sequential integers mod a power-of-two capacity)</li>
          <li>Adversarial input (hash flooding attack) — Java's String.hashCode() has been salted since Java 7 to prevent this</li>
        </ul>
        <p><strong>Kotlin specifics:</strong> data classes auto-generate hashCode() based on all properties in the primary constructor — generally safe and correct.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q2</span>Explain the difference between BFS and DFS. When would you choose each?</div>
      <div class="qa-answer">
        <p><strong>BFS (Breadth-First Search):</strong> Explores level by level using a queue. Finds shortest path in unweighted graphs. Space: O(w) where w is max width. Use when: shortest path, level-order traversal, finding nearby nodes.</p>
        <p><strong>DFS (Depth-First Search):</strong> Explores as deep as possible before backtracking using a stack (or recursion). Space: O(h) where h is height/depth. Use when: cycle detection, topological sort, finding all paths, connected components, maze solving.</p>
        <p><strong>Choosing between them:</strong></p>
        <ul>
          <li>Shortest path? → BFS</li>
          <li>All possible paths? → DFS</li>
          <li>Very wide graph (many branches)? → DFS (BFS would use too much memory)</li>
          <li>Very deep graph (long chains)? → BFS (DFS risks stack overflow)</li>
          <li>Detect cycle? → DFS (with in-stack tracking)</li>
          <li>Topological sort? → DFS (post-order) or Kahn's algorithm (BFS variant)</li>
        </ul>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>What is the difference between memoization and tabulation (bottom-up DP)? When is each preferred?</div>
      <div class="qa-answer">
        <p><strong>Memoization (top-down):</strong> Recursive solution with a cache (HashMap or array). Computes only needed subproblems. Easier to reason about — just write recursion + add cache. Overhead: function call stack, hash lookups. Risk: stack overflow for deep recursion.</p>
        <p><strong>Tabulation (bottom-up):</strong> Iterative, fills a DP table from base cases up. No recursion overhead. Better cache locality (sequential memory access). Harder to design — must determine iteration order.</p>
        <p><strong>When to prefer:</strong></p>
        <ul>
          <li>Only a few subproblems needed? → Memoization (avoids computing full table)</li>
          <li>Performance critical, millions of calls? → Tabulation (no recursion overhead)</li>
          <li>Deep recursion possible (n &gt; 10,000)? → Tabulation (no stack overflow)</li>
          <li>Space optimization possible? → Tabulation (can often reduce 2D table to 1D array)</li>
          <li>Interview, need to write quickly? → Memoization (more intuitive to derive)</li>
        </ul>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q4</span>Given an Android RecyclerView with 10,000 items, how would you find the top-K most viewed items efficiently?</div>
      <div class="qa-answer">
        <p>This is a Top-K problem, best solved with a Min Heap of size K.</p>
        <pre class="code-block"><code class="language-kotlin">fun topKViewed(viewCounts: Map<String, Int>, k: Int): List<String> {
    // Min heap of size k — always evicts the minimum when full
    val minHeap = java.util.PriorityQueue<Map.Entry<String, Int>>(
        compareBy { it.value }
    )
    for (entry in viewCounts.entries) {
        minHeap.offer(entry)
        if (minHeap.size > k) minHeap.poll()  // remove lowest
    }
    return minHeap.sortedByDescending { it.value }.map { it.key }
}
// Time: O(n log k) — n iterations, each heap op is log k
// Space: O(k) — heap holds at most k elements
// Better than sorting: O(n log n) for full sort vs O(n log k) for heap</code></pre>
        <p>Why Min Heap (not Max Heap)? We want top-K. Min Heap of size K lets us efficiently track the K largest by keeping the smallest of the K at the top for easy comparison and eviction.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q5</span>How would you implement an autocomplete feature for a search bar using a Trie?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">class TrieNode {
    val children = HashMap<Char, TrieNode>()
    var isEnd = false
    var frequency = 0  // for ranking suggestions
}

class AutocompleteTrie {
    private val root = TrieNode()

    fun insert(word: String, freq: Int = 1) {
        var node = root
        for (c in word) node = node.children.getOrPut(c) { TrieNode() }
        node.isEnd = true; node.frequency = freq
    }

    fun suggest(prefix: String, limit: Int = 5): List<String> {
        var node = root
        for (c in prefix) node = node.children[c] ?: return emptyList()
        val results = mutableListOf<Pair<String, Int>>()
        dfsCollect(node, StringBuilder(prefix), results)
        return results.sortedByDescending { it.second }.take(limit).map { it.first }
    }

    private fun dfsCollect(node: TrieNode, current: StringBuilder, results: MutableList<Pair<String, Int>>) {
        if (node.isEnd) results.add(Pair(current.toString(), node.frequency))
        node.children.forEach { (c, child) ->
            current.append(c)
            dfsCollect(child, current, results)
            current.deleteCharAt(current.lastIndex)
        }
    }
}
// Insert: O(m) where m = word length
// Search: O(p + n) where p = prefix length, n = nodes in subtree</code></pre>
        <p>In production, combine Trie with frequency data from analytics, and cache the top-K results per prefix in a HashMap for O(1) repeat lookups.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q6</span>What is the time and space complexity of Quicksort vs Mergesort? When would you use each on Android?</div>
      <div class="qa-answer">
        <p><strong>Quicksort:</strong> Average O(n log n), Worst O(n²) (sorted/reverse-sorted input with naive pivot). Space O(log n) average in-place. Fastest in practice due to cache locality. Kotlin's sortedArray() uses Timsort (hybrid), but Quicksort insight is important.</p>
        <p><strong>Mergesort:</strong> Always O(n log n) — guaranteed. Space O(n) — needs auxiliary array. Stable sort (preserves relative order of equal elements).</p>
        <p><strong>Android choices:</strong></p>
        <ul>
          <li>Sorting UI list items? → Kotlin's sort() (Timsort) — stable, efficient for nearly-sorted lists</li>
          <li>Need custom stable sort? → sortedWith(comparator) — Timsort</li>
          <li>Sorting primitives (IntArray)? → Arrays.sort() uses Dual-Pivot Quicksort — fastest for primitives</li>
          <li>Sorting network packets by timestamp? → Mergesort (stable, so equal timestamps keep original order)</li>
        </ul>
        <p>Key insight: stability matters when sorting by multiple keys sequentially or when original order has semantic meaning.</p>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Multiple Coding Challenges</h3>

    <p><strong>Challenge 1: Find Median from Data Stream</strong></p>
    <p>Design a class that supports addNum(int num) and findMedian(). Follow-up: optimize for streaming data.</p>
    <pre class="code-block"><code class="language-kotlin">// Two Heaps approach: Max Heap (lower half) + Min Heap (upper half)
// Time: O(log n) add, O(1) findMedian. Space: O(n)
class MedianFinder {
    private val lowerHalf = java.util.PriorityQueue<Int>(compareByDescending { it }) // max heap
    private val upperHalf = java.util.PriorityQueue<Int>()  // min heap

    fun addNum(num: Int) {
        lowerHalf.offer(num)
        upperHalf.offer(lowerHalf.poll()!!)  // balance: push max of lower to upper
        if (upperHalf.size > lowerHalf.size) lowerHalf.offer(upperHalf.poll()!!)  // rebalance
    }

    fun findMedian(): Double = if (lowerHalf.size > upperHalf.size) {
        lowerHalf.peek()!!.toDouble()
    } else {
        (lowerHalf.peek()!! + upperHalf.peek()!!) / 2.0
    }
}</code></pre>

    <p class="mt-3"><strong>Challenge 2: Word Break (DP)</strong></p>
    <p>Given a string s and dictionary wordDict, return true if s can be segmented into space-separated words from the dictionary.</p>
    <pre class="code-block"><code class="language-kotlin">// DP: dp[i] = true if s[0..i-1] can be segmented
// Time: O(n^2 * m) where m = word lookup, Space: O(n)
fun wordBreak(s: String, wordDict: List<String>): Boolean {
    val words = wordDict.toHashSet()
    val dp = BooleanArray(s.length + 1)
    dp[0] = true  // empty string is always valid
    for (i in 1..s.length) {
        for (j in 0 until i) {
            if (dp[j] && s.substring(j, i) in words) {
                dp[i] = true; break
            }
        }
    }
    return dp[s.length]
}
// wordBreak("leetcode", ["leet","code"]) == true
// wordBreak("catsandog", ["cats","dog","sand","and","cat"]) == false</code></pre>

    <p class="mt-3"><strong>Challenge 3: Trapping Rain Water</strong></p>
    <pre class="code-block"><code class="language-kotlin">// Two Pointer approach — O(n) time, O(1) space
fun trap(height: IntArray): Int {
    var left = 0; var right = height.lastIndex
    var leftMax = 0; var rightMax = 0; var water = 0
    while (left < right) {
        if (height[left] < height[right]) {
            if (height[left] >= leftMax) leftMax = height[left]
            else water += leftMax - height[left]
            left++
        } else {
            if (height[right] >= rightMax) rightMax = height[right]
            else water += rightMax - height[right]
            right--
        }
    }
    return water
}
// trap([0,1,0,2,1,0,1,3,2,1,2,1]) == 6</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="40" data-item="0"> ✅ Understood Why &amp; What</label>
    <label class="progress-check"><input type="checkbox" data-topic="40" data-item="1"> ✅ Can explain How it works internally</label>
    <label class="progress-check"><input type="checkbox" data-topic="40" data-item="2"> ✅ Reviewed Common Mistakes</label>
    <label class="progress-check"><input type="checkbox" data-topic="40" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="40" data-item="4"> ✅ Solved Coding Challenge</label>
  </div>
</section>

<!-- ============================================================ -->
<!-- TOPIC 41: Senior-Level Behavioral Questions (BONUS)          -->
<!-- ============================================================ -->
<section class="topic-section" id="topic-41">
  <div class="topic-header">
    <div class="topic-header-icon">🎯</div>
    <div class="topic-header-text">
      <h1>Senior-Level Behavioral Questions</h1>
      <p class="topic-tagline">STAR method answers for conflict resolution, technical debt, mentoring, architecture ownership, and production incidents</p>
      <div class="category-badge-group">
        <span class="cat-pill">Behavioral</span>
        <span class="cat-pill">Senior Level</span>
        <span class="cat-pill">Leadership</span>
        <span class="cat-pill">STAR Method</span>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 41-1: STAR Framework -->
  <div class="subtopic" id="subtopic-41-1">
    <h2>STAR Method &amp; Senior Engineering Mindset</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Technical skills get you in the door. Behavioral interviews determine whether you get the offer — especially at senior, staff, and principal levels where 40-60% of the interview loop is behavioral. Interviewers are assessing: Can you work with teams? Do you take ownership? Can you handle conflict? Do you have engineering judgment beyond code? Structured STAR answers demonstrate this systematically.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is the STAR Method?</h3>
      <p><strong>S — Situation:</strong> Set the context. What project? What team size? What timeframe? Be specific — "Q3 2022, 8-person team, building payment SDK."</p>
      <p><strong>T — Task:</strong> What was YOUR responsibility? Not the team's — yours specifically. "I was responsible for the architecture decision and getting buy-in from the team."</p>
      <p><strong>A — Action:</strong> What did YOU do? This is the meat. Be specific, use "I" not "we." List 3-4 concrete actions you took.</p>
      <p><strong>R — Result:</strong> Quantify the outcome. "Reduced build time by 40%, unblocked 6 engineers, delivered 2 weeks early." Numbers are crucial.</p>
      <p><strong>Senior-level STAR additions:</strong> Add your <em>reasoning</em> (why this action, not another), <em>trade-offs</em> you considered, and <em>what you'd do differently</em>.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ STAR Answer Template</h3>
      <pre class="code-block"><code class="language-kotlin">// STAR Answer Template — structure for every behavioral answer

/*
"Tell me about a time you [handled conflict / made a hard technical decision / mentored...]"

SITUATION (15-20 seconds):
"In [timeframe], I was [role] on a [description of team/project]..."
Specific context: team size, stakes, timeline pressure

TASK (5-10 seconds):
"My responsibility was specifically to..."
Own your part clearly

ACTIONS (60-90 seconds — the most important part):
"I did X because [reasoning]..."
"Then I did Y, which involved [specific detail]..."
"I also [Z action], which I chose over [alternative] because [trade-off reasoning]..."
Demonstrate judgment, not just execution

RESULT (20-30 seconds):
"As a result, [metric improvement], [timeline outcome], [team/stakeholder impact]..."
ALWAYS quantify. If no hard number, describe qualitative impact.

FOLLOW-UP (5-10 seconds — optional but powerful):
"Looking back, I'd also [what you learned / what you'd do differently]..."
Shows growth mindset
*/

// Anti-patterns to avoid:
// ❌ "We did..." — use "I" — they're evaluating YOU
// ❌ "It turned out great!" — no metric
// ❌ Vague: "I talked to people" — what people? What did you say?
// ❌ No reasoning: "I chose microservices" — why? what alternatives?
// ❌ Blame: "The PM made a bad decision..." — show how you handled it</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Key Behavioral Competencies at Senior Level</h3>
      <pre class="code-block"><code class="language-kotlin">// Senior Android Engineer behavioral signals interviewers seek:

// 1. OWNERSHIP & INITIATIVE
// Shows: You don't wait to be told. You identify problems and fix them.
// Evidence: "I noticed our crash rate was rising. I didn't wait for a ticket —
//           I dove into Firebase Crashlytics, identified the root cause,
//           fixed it in 2 days, and added a regression test."

// 2. TECHNICAL JUDGMENT UNDER UNCERTAINTY
// Shows: You make decisions with incomplete information and defend them.
// Evidence: "We had 3 competing architectures. I built proof-of-concept
//           prototypes for each, measured boot time and memory, and
//           recommended MVI because it gave us the best testability ROI."

// 3. CROSS-FUNCTIONAL INFLUENCE
// Shows: You work beyond engineering — product, design, QA, backend.
// Evidence: "I saw the backend API response was causing O(n^2) UI work.
//           I built a proposal with data, presented to the backend team,
//           and we redesigned the endpoint together."

// 4. MENTORING & GROWING THE TEAM
// Shows: You multiply team impact, not just individual.
// Evidence: "I noticed our junior devs didn't understand coroutines deeply.
//           I ran a 4-week internal workshop, created a reference
//           codebase, and reduced coroutine-related bugs by 60%."

// 5. HANDLING AMBIGUITY
// Shows: You thrive when requirements are unclear.
// Evidence: "The PM said 'make the app faster.' I ran user research,
//           identified that Time-To-Interactive was the real pain,
//           prioritized 5 high-impact changes, and reduced TTI by 2.1s."</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World STAR Example: Production Incident</h3>
      <p><strong>Question:</strong> "Tell me about a production incident you handled."</p>
      <pre class="code-block"><code class="language-kotlin">/*
SITUATION:
"In December 2023, three days before Christmas, our FinTech app's payment
flow had a 100% failure rate for all new transactions — affecting 50,000
daily active users. I was the on-call Android engineer."

TASK:
"My job was to: identify root cause quickly, communicate status to
stakeholders, and coordinate a fix — ideally in under 2 hours to meet
our SLA."

ACTIONS:
"1. I first checked Firebase Crashlytics — massive spike of
   'SSLHandshakeException: Certificate not trusted' starting at 02:14 AM.
   Immediately suspected certificate pinning failure.

2. I confirmed: we had shipped a release 6 hours earlier with an
   updated certificate pin. Our staging environment used the old cert,
   so it passed QA. Classic cert mismatch.

3. I made a data-driven call: don't rollback (would take 2-3 hours for
   Play Store review). Instead, use our server-side feature flag to
   temporarily disable certificate pinning while we fix the cert.

4. I deployed the feature flag at 02:47 AM — payments restored in
   minutes. Then I immediately pinned the correct new certificate in
   code, built a hotfix, and submitted for expedited review.

5. I wrote a postmortem proposing: test cert pinning in a dedicated
   test environment that mirrors production certs, and add a synthetic
   monitor that runs a payment transaction every 5 minutes."

RESULT:
"Downtime: 33 minutes. Impact: ~1,100 failed transactions (all
refunded automatically). Hotfix live in 4 hours. The postmortem
led to a cert testing protocol that caught 2 similar issues before
they hit production in the following 6 months."

RETROSPECTIVE:
"If I could redo it, I'd have cert rotation as a feature flagged
config value that can be updated server-side without a release —
eliminating the need for emergency feature flags entirely."
*/</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Behavioral Interview Mistakes &amp; Fixes</h3>
      <ul>
        <li>❌ <strong>Answering "we" instead of "I":</strong> The interviewer can't tell what YOU did — ✅ Fix: Specifically describe your individual actions, even if it was a team effort</li>
        <li>❌ <strong>Generic answers without specifics:</strong> "I improved the architecture" — ✅ Fix: "I refactored the data layer from AsyncTask to Coroutines, reducing 47 bugs related to lifecycle leaks"</li>
        <li>❌ <strong>No numbers in results:</strong> "The app got faster" — ✅ Fix: "Startup time dropped from 3.2s to 1.1s (66% improvement), measured on a Pixel 4a"</li>
        <li>❌ <strong>Describing failure without ownership:</strong> "The deadline was impossible" — ✅ Fix: "I should have escalated scope earlier. I learned to give weekly written status updates to flag risks proactively"</li>
        <li>❌ <strong>Answers that are too long (&gt;3 minutes):</strong> Interviewer loses focus — ✅ Fix: Practice to 90 seconds. Use silence to let them ask follow-ups</li>
        <li>❌ <strong>No conflict in "conflict" story:</strong> "We all agreed easily" — ✅ Fix: Real conflict means disagreement. Show how you navigated it with data and empathy, not just authority</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch on Behavioral Questions:</strong></p>
        <p>"I prepare 8-10 stories that I can flex to fit different questions: a failure, an influence story, a conflict story, a leadership story, a technical decision story, an ambiguity story, a mentoring story, and a 'proudest achievement' story. Each maps to STAR. I practice them out loud — reading is different from speaking. During the interview, when I get a question, I take 5 seconds to identify which story fits best, then deliver it in ~90 seconds. I always end with a result and a reflection — what I'd do differently — because that shows senior-level growth mindset, not defensiveness."</p>
      </div>
    </div>
  </div>

  <!-- SUBTOPIC 41-2: Specific Scenarios -->
  <div class="subtopic" id="subtopic-41-2">
    <h2>Specific Senior Scenarios &amp; Model Answers</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need This?</h3>
      <p>Certain behavioral questions appear in nearly every senior Android interview. Having well-prepared STAR answers for: technical debt decisions, mentoring junior devs, disagreeing with your manager, and architecture ownership separates candidates who clear the bar from those who don't. These questions test your engineering leadership and judgment, not just your ability to write code.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 The 7 Must-Prepare Scenarios</h3>
      <ul>
        <li>🔴 <strong>1. Conflict with a teammate or manager</strong> — Show diplomacy + data</li>
        <li>🟠 <strong>2. Technical debt decision</strong> — Show business judgment</li>
        <li>🟡 <strong>3. Mentoring a junior developer</strong> — Show teaching + patience</li>
        <li>🟢 <strong>4. Architecture ownership</strong> — Show vision + influence</li>
        <li>🔵 <strong>5. Production incident</strong> — Show calm, ownership, learning</li>
        <li>🟣 <strong>6. Missed deadline / failure</strong> — Show accountability + growth</li>
        <li>⚫ <strong>7. Ambiguous requirement</strong> — Show proactivity + stakeholder management</li>
      </ul>
    </div>

    <div class="card card-how">
      <h3>🛠️ Model STAR Answers</h3>
      <pre class="code-block"><code class="language-kotlin">/*
=== CONFLICT RESOLUTION ===
Q: "Tell me about a conflict with a colleague over a technical decision."

S: "In Q1 2023, my senior colleague and I disagreed on whether to use
   MVVM or MVI for our new checkout flow. He strongly advocated MVVM
   (our team's existing standard), I believed MVI was better for the
   complex state machine involved."

T: "My task was to make a clear, defensible technical decision that
   the team could move forward with confidently — not just win the debate."

A: "Instead of debating opinions, I proposed a structured evaluation.
   I wrote a 1-page doc comparing MVVM and MVI on 5 dimensions:
   testability, unidirectional data flow, debugging, team learning curve,
   and migration cost. I ran both patterns against our most complex
   state: checkout with 12 possible states and 8 error conditions.
   I shared the doc with the team for 48-hour async review, then held
   a 30-minute structured discussion where I asked my colleague to
   specifically identify which MVVM advantage he weighted most.
   His concern was team ramp-up time — valid. We compromised: use MVI
   for new checkout screens only, measure team velocity over one sprint,
   then decide on broader adoption."

R: "Checkout shipped on time. Team adopted MVI for 3 additional modules
   over the next quarter. My colleague became one of its advocates.
   Our checkout state-related bugs dropped 70% vs the previous MVVM
   implementation."

REFLECTION: "I learned that in technical conflicts, the person who
   brings data and a framework for discussion wins more often than
   the person who argues loudest."


=== TECHNICAL DEBT ===
Q: "How do you balance shipping features vs addressing technical debt?"

S: "In 2022, our Android app had accrued significant technical debt:
   our networking layer was AsyncTask-based (deprecated), our UI tests
   were flaky (60% pass rate), and we had 2,000+ TODOs in the codebase.
   Meanwhile, product wanted 4 major features in H1."

T: "As the tech lead, I needed to make a recommendation to leadership
   about how to address debt without stalling the feature roadmap."

A: "I quantified the debt's cost in developer productivity time:
   flaky tests alone cost ~6 engineer-hours per week in reruns.
   I categorized debt into: 'bleeding' (actively slowing us down),
   'wounded' (will slow us in 6 months), and 'stable' (cosmetic only).
   I proposed the 20% rule: every sprint, 20% of engineer capacity
   is dedicated to bleeding debt items. No approval needed for items
   under 4 hours. I created a debt scorecard and made it visible in
   weekly standups. I also tied debt reduction to measurable outcomes
   (test reliability, build time, incident rate) so leadership could
   see ROI."

R: "In 6 months: test pass rate went from 60% to 94%, AsyncTask
   migration completed, build time dropped by 35%. All 4 product
   features shipped on time. Leadership approved the 20% rule as
   permanent team policy."


=== MENTORING ===
Q: "Tell me about a time you mentored a junior developer."

S: "In 2023, a junior developer joined my team fresh from bootcamp.
   He was excellent at Python but struggled with Kotlin idioms and
   Android lifecycle. He was assigned a feature but was blocked for
   2 weeks and not speaking up."

T: "I noticed the pattern and took ownership of his onboarding,
   even though it wasn't formally my responsibility — my manager
   had 8 other people to support."

A: "I set up weekly 1:1s — 30 minutes, always his agenda. I asked
   what was confusing, not what he'd done wrong. I created a
   'Kotlin for Android' doc with the 20 most common patterns he'd
   encounter, including coroutines, Flow, and lifecycle-awareness.
   I reviewed his PRs not just for correctness but for idiomatic
   Kotlin — I'd offer alternatives, not mandates. I also paired
   with him on a medium-complexity feature so he could see my
   thought process. When he was blocked, I didn't give answers —
   I asked Socratic questions: 'What do you know about the issue?
   What have you tried? What does the documentation say?'"

R: "Within 3 months he was submitting PRs that needed minimal
   review. By month 6, he was reviewing junior PRs himself. He
   was promoted to mid-level engineer in 10 months — faster than
   anyone in the team's history. He told me in his promotion
   conversation that our 1:1s were transformative."

*/</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Architecture Ownership Story</h3>
      <pre class="code-block"><code class="language-kotlin">/*
Q: "Describe a time you took ownership of a major architectural decision."

S: "In 2022, our 4-year-old Android app had a monolithic architecture
   with all business logic in Activities. We had 200+ Activities,
   zero unit tests, and a 45-minute full-regression QA cycle that
   blocked every release."

T: "I was the most senior Android engineer but had no formal authority
   to mandate architecture changes. I needed to drive this through
   influence, not mandate."

A: "Step 1: I built the business case. I calculated that our QA cycle
   cost $12,000/month in engineer time. A 6-month architecture
   modernization would pay back in 14 months. I put this in a 2-page
   doc with risk analysis.

Step 2: I proposed a strangler fig migration — not a big bang rewrite.
   New features would be built in MVVM/Clean Architecture. Legacy code
   stays until touched, then gets refactored.

Step 3: I ran a 2-day internal hackathon. Split the team into 3 groups,
   each building the same feature in different architectures (MVVM,
   MVI, MVP). We voted on what to adopt. The team chose MVVM.
   Ownership transferred to them — not my choice imposed on them.

Step 4: I created the reference implementation, the architectural
   decision record (ADR), and a PR review guide for architecture
   compliance. I ran monthly architecture guild meetings."

R: "18 months later: 80% of app surface migrated, QA cycle dropped
   to 12 minutes (73% reduction), unit test coverage from 0% to 67%,
   and we onboarded 3 new engineers who said the clean architecture
   was 'the most maintainable codebase they'd worked on.'"

WHAT MAKES THIS SENIOR-LEVEL:
- Business case with numbers
- Influence without authority
- Team buy-in via inclusive decision-making
- Sustainable process (guild, ADR) not just one-time fix
- Long-term measurement
*/</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World Handling of Ambiguous Requirements</h3>
      <pre class="code-block"><code class="language-kotlin">/*
Q: "Tell me about a time you dealt with ambiguous or changing requirements."

S: "In Q3 2023, our product manager said 'we need to improve the
   app's performance' with no further specification. This was a
   critical initiative — it was in our OKRs — but the definition
   was completely vague."

T: "My job was to turn this ambiguous requirement into a concrete,
   measurable engineering plan."

A: "I ran 5 user interviews (with PM's help) and reviewed 200
   1-star Play Store reviews. The top complaint: 'app takes forever
   to load.' Not general slowness — startup time specifically.

I instrumented the app with custom traces using Perfetto/Macrobenchmark.
I identified: the top 3 startup bottlenecks were:
1. Synchronous SharedPreferences read on main thread (820ms)
2. Eagerly initializing analytics SDK before first frame (340ms)
3. Synchronous network call to fetch feature flags (1100ms)

I wrote a one-pager: 'Performance is Time-To-Interactive. Current: 3.8s.
Goal: under 2.0s. Here are 5 initiatives ranked by impact/effort.'
Got PM and EM sign-off in one meeting.

Executed: migrated SharedPreferences to DataStore (async),
lazy-initialized SDKs after first frame, implemented feature flag
caching so network call is async and uses cached value on first launch."

R: "TTI dropped from 3.8s to 1.4s (63% improvement) measured on a
   Pixel 4a (our P25 device — represents slower real-world hardware).
   Play Store rating improved from 3.8 to 4.3 over the following 8 weeks.
   This became our team's performance measurement framework, still
   used 18 months later."
*/</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Behavioral Interview Mistakes &amp; Fixes</h3>
      <ul>
        <li>❌ <strong>Picking trivial stories for conflict questions:</strong> "We disagreed on variable naming" — ✅ Fix: Choose stories with real stakes: technical direction, schedule, architectural decisions</li>
        <li>❌ <strong>Sounding defensive about failures:</strong> "It wasn't my fault because..." — ✅ Fix: Take ownership first, then explain context. "I made the call to skip the performance test. Here's what I learned."</li>
        <li>❌ <strong>Not having a "failure" story ready:</strong> Saying "I can't think of a failure" is a red flag — ✅ Fix: Every senior engineer has failures. Prepare one that shows learning, not just the mistake</li>
        <li>❌ <strong>Mentoring story that's condescending:</strong> "The junior didn't understand basic things" — ✅ Fix: Show empathy — "I remembered being in that position. I focused on what would have helped me most."</li>
        <li>❌ <strong>Not tailoring answers to the company's level:</strong> FAANG L5 vs startup senior are different bars — ✅ Fix: Research the role, understand what "senior" means at this company (scope, ambiguity level, team multiplier)</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation (How to Present in Interview)</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch on Behavioral Questions:</strong></p>
        <p>"When I prepare for behavioral interviews, I maintain a 'brag doc' — a running document where I write down significant wins, failures, and learning moments throughout the year. This gives me a rich library of specific, recent examples. For each story I practice the 'so what' — why does this matter at company scale? I always calibrate to the interviewer's level: for engineering managers, I emphasize team impact and process; for senior engineers, I emphasize technical depth and trade-offs. The best behavioral answers don't just answer the question — they reveal something unique about how you think, what you value, and why you'd be a multiplier on their team."</p>
      </div>
    </div>
  </div>

  <!-- Q&A Section -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers (STAR Format)</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q1</span>"Tell me about a time you disagreed with your manager's technical decision."</div>
      <div class="qa-answer">
        <p><strong>STAR Framework Answer Guide:</strong></p>
        <p><strong>Situation:</strong> Set context — what was the decision? What were the stakes? What was your manager's reasoning?</p>
        <p><strong>Task:</strong> Your goal was NOT to win the argument — it was to make the best technical decision for the product and team.</p>
        <p><strong>Action:</strong> Key moves for a senior engineer:</p>
        <ol>
          <li>Gather data, not opinions. Build a clear comparison.</li>
          <li>Seek first to understand your manager's constraints (timeline? team familiarity? organizational politics?)</li>
          <li>Present your case with data, acknowledging their trade-offs</li>
          <li>If overruled: "Disagree and commit" — make your concern heard once, clearly, then support the decision fully</li>
          <li>If the decision leads to problems: address without "I told you so" — "Here's what we can do now"</li>
        </ol>
        <p><strong>Result:</strong> Either your perspective was adopted (show the outcome) OR you were overruled but handled it professionally (show how you supported the team anyway).</p>
        <p><strong>Key signal for senior level:</strong> You can influence without authority and commit without resentment. You never let disagreement become obstruction.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q2</span>"Describe a situation where you had to make a hard technical trade-off with incomplete information."</div>
      <div class="qa-answer">
        <p><strong>Key insight:</strong> Senior engineers are expected to make good decisions under uncertainty. They don't wait for perfect information.</p>
        <p><strong>Strong answer structure:</strong></p>
        <ol>
          <li><strong>The uncertainty:</strong> What specifically was unknown? (User scale? Backend timeline? Team capacity?)</li>
          <li><strong>How you framed it:</strong> "I identified the key assumptions. If X is true, we should do A. If Y is true, we should do B."</li>
          <li><strong>Your decision framework:</strong> Reversibility! Prefer reversible decisions. "I chose the option we could unwind if our assumptions proved wrong."</li>
          <li><strong>How you de-risked it:</strong> Prototype? Feature flag? Small rollout? Measuring metrics?</li>
          <li><strong>The outcome:</strong> Was your bet right? If wrong, how did you recover?</li>
        </ol>
        <p><strong>What NOT to say:</strong> "We waited until we had all the information." Senior engineers don't have this luxury. Waiting IS a decision — often the wrong one.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q3</span>"Tell me about a time you improved a team process or engineering culture."</div>
      <div class="qa-answer">
        <p><strong>This question tests:</strong> Whether you're a force multiplier or just an individual contributor. Senior engineers improve the team, not just their own output.</p>
        <p><strong>Strong answer areas:</strong></p>
        <ul>
          <li><strong>Code review culture:</strong> "PRs were taking 3+ days. I proposed a 24-hour SLA, drafted a PR description template, and ran a workshop on effective code review. PR cycle time dropped to 18 hours."</li>
          <li><strong>Documentation:</strong> "We had zero architecture documentation. I started Architecture Decision Records (ADRs) for significant decisions. New engineers now onboard in 1 week instead of 3."</li>
          <li><strong>Testing culture:</strong> "Test coverage was 12%. I gamified it — team coverage leaderboard, weekly shoutouts for best test coverage PRs. Coverage reached 68% in 4 months."</li>
          <li><strong>Postmortem culture:</strong> "After incidents we never wrote postmortems — we repeated mistakes. I introduced blameless postmortems with action items tracked in Jira. Repeat incidents dropped 80%."</li>
        </ul>
        <p>Always quantify: how did you measure the improvement? What was before and after?</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q4</span>"How have you handled a situation where your team was falling behind schedule?"</div>
      <div class="qa-answer">
        <p><strong>Trap to avoid:</strong> Don't say you just worked harder/longer hours. That's not a senior answer. Senior engineers solve schedule problems systematically.</p>
        <p><strong>Senior-level approaches:</strong></p>
        <ol>
          <li><strong>Diagnose before acting:</strong> Is it scope creep? Technical unknowns? Team capacity? Wrong estimates? The solution differs.</li>
          <li><strong>Scope negotiation:</strong> "I worked with PM to cut scope ruthlessly. We identified the 20% of features that delivered 80% of user value. Shipped those, deferred the rest."</li>
          <li><strong>Unblock others:</strong> "I noticed two engineers were blocked on the same issue. I spent 2 hours pairing with each to unblock them — multiplied output more than my own coding."</li>
          <li><strong>Communicate proactively:</strong> "I wrote a weekly written status update to all stakeholders showing current status, what was at risk, and what we needed to get back on track. No surprises."</li>
          <li><strong>Request help early:</strong> "I escalated 3 weeks before the deadline — not the night before. We got 2 additional engineers for the sprint."</li>
        </ol>
        <p>Result must show: what shipped, stakeholder trust maintained, and what process change prevents this next time.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q5</span>"Tell me about a time you had to learn something new very quickly to solve a critical problem."</div>
      <div class="qa-answer">
        <p><strong>What interviewers are testing:</strong> Growth mindset, learning velocity, and comfort with being a beginner.</p>
        <p><strong>Strong answer structure:</strong></p>
        <ol>
          <li><strong>The knowledge gap:</strong> "We needed to implement ML inference on-device for a camera feature. I had never worked with TensorFlow Lite."</li>
          <li><strong>How you learned fast:</strong> "I did NOT try to learn everything. I identified exactly what I needed to know for this specific use case. I spent 1 day on the official docs, 1 day building a spike (throwaway prototype), then implemented the real thing."</li>
          <li><strong>Who you leaned on:</strong> "I found an ML engineer in a sister team and scheduled a 2-hour pairing session. I asked targeted questions, not 'teach me everything.'"</li>
          <li><strong>How you documented for the team:</strong> "I wrote a 'TFLite for Android Engineers' guide so the next person wouldn't start from scratch."</li>
          <li><strong>Result:</strong> "Shipped the feature in 2 weeks. The guide was used by 4 other engineers across the org."</li>
        </ol>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>"Where do you see yourself in 5 years? Why do you want this role?"</div>
      <div class="qa-answer">
        <p><strong>The 5-year question tests:</strong> Whether you have direction and whether this role genuinely fits your path.</p>
        <p><strong>Strong senior answer:</strong> Connect your trajectory to the company's direction. Show you've researched the role.</p>
        <p><em>"In 5 years, I want to be a Staff/Principal engineer — someone who sets technical direction at the platform or product level, not just implements features. I'm particularly interested in [company's specific engineering challenge, e.g., scaling their Android platform to support 500M users, or their investment in Compose infrastructure]. This role specifically interests me because [specific technical challenge in JD] is exactly the space where I've spent the last 3 years building expertise — [brief specific example]. I want to bring that expertise here, but also push past what I know in an environment where the engineering problems are genuinely hard."</em></p>
        <p><strong>Never say:</strong> "I want to be a manager in 5 years" (unless applying for an EM role) — it signals you don't want to code. Don't say "I don't know" — shows no direction.</p>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Behavioral Interview Preparation Checklist</h3>
    <p><strong>Problem:</strong> Build your personal STAR story library. For each scenario below, write a 90-second STAR answer with specific details and a quantified result.</p>
    <pre class="code-block"><code class="language-kotlin">// Your STAR Story Library Template

/*
REQUIRED STORIES (prepare all 8):

1. BIGGEST ACHIEVEMENT
   - Your proudest technical accomplishment
   - Quantified impact, cross-team, complex problem

2. FAILURE / MISTAKE
   - Something that went wrong and was YOUR fault
   - What you did to recover, what you learned, what changed

3. CONFLICT WITH COLLEAGUE
   - Technical disagreement (architecture, approach, tools)
   - How you resolved with data + empathy

4. CONFLICT WITH MANAGER / DISAGREED WITH DIRECTION
   - "Disagree and commit" or successfully changed direction
   - Shows you can push back professionally

5. TECHNICAL DEBT / TRADE-OFF
   - Business judgment beyond just technical correctness
   - Short-term vs long-term thinking

6. MENTORING / GROWING THE TEAM
   - Someone you helped grow significantly
   - Specific techniques, measurable improvement

7. AMBIGUOUS REQUIREMENT
   - You turned vague direction into concrete action
   - Showed initiative, stakeholder management

8. PRODUCTION INCIDENT
   - System down, users affected
   - Your role in diagnosis, recovery, and prevention

CALIBRATION QUESTIONS:
- Is my result quantified? (%, time saved, users affected)
- Did I say "I" not "we" for my specific actions?
- Is the conflict real, with real stakes?
- Does my failure show genuine accountability + learning?
- Would this story impress a senior engineer at FAANG?

PRACTICE SCHEDULE:
Week 1: Write all 8 stories in STAR format
Week 2: Practice each out loud, time yourself (target 90s)
Week 3: Have a friend/peer give you random behavioral questions
Week 4: Refine stories based on feedback
*/</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="41" data-item="0"> ✅ Understood the STAR Framework</label>
    <label class="progress-check"><input type="checkbox" data-topic="41" data-item="1"> ✅ Written 8 STAR stories from my own experience</label>
    <label class="progress-check"><input type="checkbox" data-topic="41" data-item="2"> ✅ Practiced each story out loud (timed at 90s)</label>
    <label class="progress-check"><input type="checkbox" data-topic="41" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="41" data-item="4"> ✅ Built Personal STAR Story Library</label>
  </div>
</section>
'''
