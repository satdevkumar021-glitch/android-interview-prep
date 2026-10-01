# html_topic_23_to_27.py
# Topics 23-27: Services, BroadcastReceiver, ContentProvider, Navigation, Security

def get_topics_23_to_27_html():
    return '''
<!-- ========== TOPIC 23: Android Services ========== -->
<section class="topic-section" id="topic-23">
  <div class="topic-header">
    <div class="topic-header-icon">⚙️</div>
    <div class="topic-header-text">
      <h1>Android Services</h1>
      <p class="topic-tagline">Background execution, IPC, and foreground work — the backbone of long-running Android operations</p>
      <div class="category-badge-group">
        <span class="cat-pill">Services</span>
        <span class="cat-pill">IPC</span>
        <span class="cat-pill">Foreground</span>
        <span class="cat-pill">AIDL</span>
      </div>
    </div>
  </div>

  <!-- Subtopic 23-1: Service Types & Lifecycle -->
  <div class="subtopic" id="subtopic-23-1">
    <h2>23.1 Service Types, Lifecycle &amp; Android 14 Changes</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need Services?</h3>
      <p>Android activities are ephemeral — the moment the user navigates away, the process can be killed. But real apps need to keep working: a music player must keep streaming, a navigation app must keep tracking GPS, a chat app must keep receiving messages. <strong>Services</strong> solve the fundamental problem of needing computation that outlives any single UI component.</p>
      <p>Without services, you'd be forced to do background work in the Activity itself — which gets killed on rotation, on home press, or by the OS. Services provide a lifecycle explicitly designed for long-running, non-UI work, with proper OS contracts around when they can be killed.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is a Service?</h3>
      <p>A <strong>Service</strong> is an application component that runs in the background without a user interface. It runs on the <em>main thread</em> by default (so you must use coroutines/threads internally), and it survives Activity destruction. There are three fundamental types:</p>
      <ul>
        <li><strong>Started Service</strong> (<code>startService()</code> / <code>startForegroundService()</code>): Runs indefinitely. Must call <code>stopSelf()</code> or be stopped externally. Since Android 8.0 (API 26), background-started services are severely limited.</li>
        <li><strong>Bound Service</strong> (<code>bindService()</code>): Lives only while at least one client is bound. Exposes an IBinder interface for direct method calls. Destroyed when all clients unbind.</li>
        <li><strong>Foreground Service</strong>: A started service that shows a persistent notification. The OS will not kill it under memory pressure. Required for long-running user-visible work in Android 8+. Android 14 (API 34) requires declaring <code>foregroundServiceType</code>.</li>
      </ul>
      <p><strong>IntentService</strong> was the original way to handle async started services — it auto-created a worker thread and stopped itself. It was deprecated in API 30; use <strong>WorkManager</strong> or coroutine-based services instead.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work? — Foreground Service (Android 14)</h3>
      <p>Step-by-step lifecycle of a Foreground Service:</p>
      <ol>
        <li>Call <code>startForegroundService(intent)</code> from your Activity/ViewModel.</li>
        <li>The Service's <code>onCreate()</code> is called, then <code>onStartCommand()</code>.</li>
        <li>Within 5 seconds you MUST call <code>startForeground(notificationId, notification)</code> or the system throws <code>ForegroundServiceDidNotStartInTimeException</code>.</li>
        <li>The service shows a persistent notification; OS now treats it as foreground.</li>
        <li>Work runs on a coroutine/thread; call <code>stopSelf()</code> when done or keep running.</li>
        <li>On <code>onDestroy()</code>, release all resources.</li>
      </ol>
      <pre class="code-block"><code class="language-kotlin">// AndroidManifest.xml — Android 14 requires foregroundServiceType
// &lt;uses-permission android:name="android.permission.FOREGROUND_SERVICE" /&gt;
// &lt;uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" /&gt;
// &lt;service
//     android:name=".MusicPlayerService"
//     android:foregroundServiceType="mediaPlayback"
//     android:exported="false" /&gt;

class MusicPlayerService : Service() {

    private val serviceScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private lateinit var mediaPlayer: MediaPlayer
    private val binder = LocalBinder()

    inner class LocalBinder : Binder() {
        fun getService(): MusicPlayerService = this@MusicPlayerService
    }

    override fun onCreate() {
        super.onCreate()
        mediaPlayer = MediaPlayer()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val trackUrl = intent?.getStringExtra("TRACK_URL") ?: run {
            stopSelf()
            return START_NOT_STICKY
        }

        // MUST call within 5 seconds on Android 8+
        startForeground(NOTIFICATION_ID, buildNotification("Loading..."))

        serviceScope.launch {
            try {
                playTrack(trackUrl)
            } catch (e: Exception) {
                Log.e(TAG, "Playback error", e)
                stopSelf()
            }
        }

        // START_STICKY: OS restarts service if killed, Intent is null
        // START_NOT_STICKY: OS does NOT restart service if killed
        // START_REDELIVER_INTENT: OS restarts and re-delivers last Intent
        return START_STICKY
    }

    override fun onBind(intent: Intent): IBinder = binder

    private suspend fun playTrack(url: String) {
        withContext(Dispatchers.IO) {
            mediaPlayer.apply {
                reset()
                setDataSource(url)
                prepare() // blocking — use prepareAsync() for production
                start()
            }
        }
        updateNotification("Now Playing: $url")
    }

    private fun buildNotification(content: String): Notification {
        val channelId = "music_channel"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId, "Music Playback", NotificationManager.IMPORTANCE_LOW
            )
            getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
        }
        return NotificationCompat.Builder(this, channelId)
            .setContentTitle("Music Player")
            .setContentText(content)
            .setSmallIcon(R.drawable.ic_music)
            .setOngoing(true)
            .build()
    }

    private fun updateNotification(content: String) {
        val nm = getSystemService(NotificationManager::class.java)
        nm.notify(NOTIFICATION_ID, buildNotification(content))
    }

    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()
        mediaPlayer.release()
        // stopForeground() called automatically by system on service destroy
    }

    companion object {
        private const val TAG = "MusicPlayerService"
        private const val NOTIFICATION_ID = 1001
    }
}
</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// Starting a Foreground Service (must use startForegroundService on API 26+)
val intent = Intent(this, MusicPlayerService::class.java).apply {
    putExtra("TRACK_URL", "https://example.com/track.mp3")
}
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    startForegroundService(intent)
} else {
    startService(intent)
}

// Binding to a Service (for direct method calls)
private var musicService: MusicPlayerService? = null
private var isBound = false

private val connection = object : ServiceConnection {
    override fun onServiceConnected(name: ComponentName, service: IBinder) {
        val binder = service as MusicPlayerService.LocalBinder
        musicService = binder.getService()
        isBound = true
    }

    override fun onServiceDisconnected(name: ComponentName) {
        isBound = false
        musicService = null
    }
}

// Bind in onStart, unbind in onStop
override fun onStart() {
    super.onStart()
    bindService(Intent(this, MusicPlayerService::class.java), connection, Context.BIND_AUTO_CREATE)
}

override fun onStop() {
    super.onStop()
    if (isBound) {
        unbindService(connection)
        isBound = false
    }
}

// Stopping a service from inside
stopSelf()
stopSelf(startId) // Safe version — only stops if startId matches latest

// Stopping from outside
stopService(Intent(this, MusicPlayerService::class.java))

// Android 14+ foregroundServiceType values (must match manifest):
// camera, connectedDevice, dataSync, health, location,
// mediaPlayback, mediaProjection, microphone, phoneCall,
// remoteMessaging, shortService, specialUse, systemExempted
</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World: Healthcare — Continuous Vitals Monitoring</h3>
      <p>A healthcare app monitors patient vitals via a connected BLE device. The service must run in the foreground continuously, even when the app is backgrounded, and post alerts if readings go critical.</p>
      <pre class="code-block"><code class="language-kotlin">// Manifest:
// &lt;uses-permission android:name="android.permission.FOREGROUND_SERVICE_HEALTH" /&gt;
// &lt;service android:name=".VitalsMonitorService"
//          android:foregroundServiceType="health"
//          android:exported="false" /&gt;

class VitalsMonitorService : Service() {

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private lateinit var bleManager: BleVitalsManager

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIF_ID, buildVitalsNotification("Monitoring active"))

        scope.launch {
            bleManager.vitalFlow()
                .catch { e -> reportError(e) }
                .collect { vitals ->
                    updateNotification(vitals)
                    if (vitals.heartRate < 40 || vitals.heartRate > 180) {
                        sendCriticalAlert(vitals)
                    }
                }
        }
        return START_STICKY
    }

    private suspend fun sendCriticalAlert(vitals: Vitals) {
        // Post high-priority notification + trigger alarm sound
        withContext(Dispatchers.Main) {
            val nm = getSystemService(NotificationManager::class.java)
            nm.notify(ALERT_NOTIF_ID, buildAlertNotification(vitals))
        }
    }

    override fun onBind(intent: Intent): IBinder? = null

    override fun onDestroy() {
        scope.cancel()
        bleManager.disconnect()
    }

    companion object {
        private const val NOTIF_ID = 2001
        private const val ALERT_NOTIF_ID = 2002
    }
}
</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Blocking the main thread in onStartCommand:</strong> Service runs on main thread. Network calls crash with NetworkOnMainThreadException. ✅ Fix: Launch a coroutine with <code>Dispatchers.IO</code> immediately in <code>onStartCommand</code>.</li>
        <li>❌ <strong>Forgetting to call startForeground() within 5 seconds:</strong> Results in <code>ForegroundServiceDidNotStartInTimeException</code> crash. ✅ Fix: Call <code>startForeground()</code> as the FIRST thing in <code>onStartCommand</code>.</li>
        <li>❌ <strong>Missing foregroundServiceType in Android 14:</strong> SecurityException at runtime. ✅ Fix: Declare <code>android:foregroundServiceType="..."</code> in manifest AND request the matching permission.</li>
        <li>❌ <strong>Memory leaks via ServiceConnection:</strong> Binding but never unbinding in <code>onStop()</code> leads to leaked connections. ✅ Fix: Always unbind symmetrically in <code>onStop()</code> matching <code>onStart()</code> binding.</li>
        <li>❌ <strong>Using IntentService in 2024:</strong> Deprecated in API 30, no coroutine support. ✅ Fix: Use WorkManager for deferrable tasks, or CoroutineWorker for guaranteed execution.</li>
        <li>❌ <strong>Using startService() for background work on API 26+:</strong> The OS will kill it immediately when the app goes to background. ✅ Fix: Use <code>startForegroundService()</code> + <code>startForeground()</code> or WorkManager.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation</h3>
      <p>When asked about Android Services in an interview, demonstrate breadth across all types and depth on production constraints.</p>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"In production, my choice depends on the use case. For user-visible long-running work — music playback, navigation, health monitoring — I use a Foreground Service. Since Android 8, background services are aggressively killed, so a persistent notification is non-negotiable. With Android 14, you must also declare the foregroundServiceType in the manifest and hold the corresponding permission — for example, FOREGROUND_SERVICE_HEALTH. Inside the service, I never block the main thread; I launch coroutines with a SupervisorJob so one failure doesn't cancel sibling jobs. For IPC between processes, I choose based on complexity: a simple LocalBinder suffices for same-process binding, Messenger for simple cross-process messaging, and full AIDL only when I need high-throughput, multi-threaded IPC. For one-off background tasks, I avoid services entirely and use WorkManager — it handles device restarts, battery optimization, and constraint-based scheduling automatically."</p>
      </div>
    </div>
  </div>

  <!-- Subtopic 23-2: Bound Services, AIDL, Messenger -->
  <div class="subtopic" id="subtopic-23-2">
    <h2>23.2 Bound Services, AIDL &amp; Messenger IPC</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need IPC?</h3>
      <p>Android apps are sandboxed in separate processes. When two different apps (or an app and a system service) need to communicate, they cannot share memory directly. AIDL (Android Interface Definition Language) solves this by generating Binder-based proxy/stub code that lets you call remote methods as if they were local, with the Android IPC framework handling the serialization and cross-process marshalling transparently.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is AIDL?</h3>
      <p>AIDL generates Java/Kotlin Binder code from an interface definition file. The <strong>stub</strong> runs in the server process; the <strong>proxy</strong> runs in the client process. Each method call is serialized into a <code>Parcel</code>, sent over Binder (the Linux kernel IPC mechanism), deserialized in the server process, executed, and the result returned the same way. AIDL supports primitives, String, CharSequence, Parcelable types, and Lists/Maps of those types. For simple use cases, <strong>Messenger</strong> is a simpler alternative that uses a Handler to process messages sequentially.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does AIDL Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// Step 1: Define AIDL interface (IRemotePaymentService.aidl)
// package com.example.payment;
// interface IRemotePaymentService {
//     String processPayment(String token, double amount);
//     boolean cancelTransaction(String transactionId);
// }

// Step 2: Implement the stub in the Service
class PaymentService : Service() {

    private val binder = object : IRemotePaymentService.Stub() {
        // This runs on a Binder thread pool — thread-safe code required!
        override fun processPayment(token: String, amount: Double): String {
            // Validate on Binder thread, but never do long blocking work here
            return runBlocking {
                paymentRepository.process(token, amount)
            }
        }

        override fun cancelTransaction(transactionId: String): Boolean {
            return runBlocking {
                paymentRepository.cancel(transactionId)
            }
        }
    }

    override fun onBind(intent: Intent): IBinder = binder
}

// Step 3: Client side binding
class CheckoutActivity : AppCompatActivity() {

    private var paymentService: IRemotePaymentService? = null

    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName, service: IBinder) {
            // asInterface() returns local binder if same-process,
            // or a proxy if cross-process
            paymentService = IRemotePaymentService.Stub.asInterface(service)
        }
        override fun onServiceDisconnected(name: ComponentName) {
            paymentService = null
        }
    }

    private fun initiatePayment(token: String, amount: Double) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val result = paymentService?.processPayment(token, amount)
                    ?: throw IllegalStateException("Service not connected")
                withContext(Dispatchers.Main) {
                    showSuccess(result)
                }
            } catch (e: RemoteException) {
                // The remote service process died
                withContext(Dispatchers.Main) { showError(e) }
            } catch (e: DeadObjectException) {
                // Binder connection is dead
                reconnectService()
            }
        }
    }
}

// Simpler alternative: Messenger for one-directional IPC
class MessengerService : Service() {
    private val handler = object : Handler(Looper.getMainLooper()) {
        override fun handleMessage(msg: Message) {
            when (msg.what) {
                MSG_PROCESS -> {
                    val replyTo = msg.replyTo
                    val result = doWork(msg.data.getString("payload"))
                    replyTo?.send(Message.obtain(null, MSG_RESULT).apply {
                        data = Bundle().apply { putString("result", result) }
                    })
                }
            }
        }
    }
    private val messenger = Messenger(handler)
    override fun onBind(intent: Intent): IBinder = messenger.binder

    companion object {
        const val MSG_PROCESS = 1
        const val MSG_RESULT = 2
    }
}
</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// AIDL file lives in src/main/aidl/com/example/IMyService.aidl
// Supported types: primitive, String, CharSequence, IBinder,
//                  Parcelable, List, Map, arrays of the above

// Directionality keywords:
// in  — data flows from client to service (default)
// out — data flows from service to client (service writes to parameter)
// inout — bidirectional

// AIDL interface with callback (listener pattern):
// interface IDownloadCallback {
//     void onProgress(int percent);
//     void onComplete(String filePath);
// }
// interface IDownloadService {
//     void startDownload(String url, IDownloadCallback callback);
// }

// RemoteCallbackList — thread-safe list of remote callbacks
private val callbacks = RemoteCallbackList<IDownloadCallback>()

fun registerCallback(cb: IDownloadCallback) {
    callbacks.register(cb)
}

fun broadcastProgress(percent: Int) {
    val n = callbacks.beginBroadcast()
    for (i in 0 until n) {
        try {
            callbacks.getBroadcastItem(i).onProgress(percent)
        } catch (e: RemoteException) {
            // Client died — RemoteCallbackList auto-removes dead callbacks
        }
    }
    callbacks.finishBroadcast()
}
</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World: Automotive — Cross-App Navigation IPC</h3>
      <p>In an Automotive OS (AAOS) app cluster, the navigation app in one process needs to send route progress data to the instrument cluster app in another process. AIDL is the correct tool here.</p>
      <pre class="code-block"><code class="language-kotlin">// INavigationCluster.aidl
// interface INavigationCluster {
//     void updateRoute(String maneuver, int distanceMeters, String streetName);
//     void setNavigationActive(boolean active);
// }

class ClusterNavigationService : Service() {
    private val binder = object : INavigationCluster.Stub() {
        override fun updateRoute(maneuver: String, distanceMeters: Int, streetName: String) {
            // Runs on Binder thread; post to main thread for UI
            mainHandler.post {
                clusterDisplay.render(NavigationState(maneuver, distanceMeters, streetName))
            }
        }
        override fun setNavigationActive(active: Boolean) {
            mainHandler.post { clusterDisplay.setVisible(active) }
        }
    }

    override fun onBind(intent: Intent) = binder
    // Exported to allow navigation app to bind cross-process
    // android:exported="true" android:permission="com.example.CLUSTER_PERMISSION"
}
</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Blocking AIDL Binder threads:</strong> AIDL methods run on a thread pool; long-running blocking calls exhaust it and cause ANR. ✅ Fix: Use <code>runBlocking</code> judiciously or redesign to async callbacks.</li>
        <li>❌ <strong>Not handling RemoteException / DeadObjectException:</strong> The remote process can die at any time. ✅ Fix: Always wrap AIDL calls in try/catch for both exceptions.</li>
        <li>❌ <strong>Memory leaks with RemoteCallbackList:</strong> Not calling <code>unregister()</code> on client disconnect leaks callback objects. ✅ Fix: Always call <code>callbacks.unregister(cb)</code> in the client's <code>onServiceDisconnected</code>.</li>
        <li>❌ <strong>Exporting services without permission protection:</strong> Any app can bind to your service. ✅ Fix: Always set <code>android:permission</code> on exported services and verify with <code>checkCallingPermission()</code>.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"I choose between AIDL and Messenger based on complexity. If the client needs to call multiple methods with typed parameters and get return values, AIDL is the right choice — it generates type-safe Binder code. If I just need to send simple Messages (think command pattern), Messenger with a Handler queue is simpler and serializes calls automatically. The critical thing with AIDL in production is handling DeadObjectException — the remote process can die while you hold a reference. I always wrap calls in try/catch and implement reconnection logic via the ServiceConnection callbacks. I also protect exported services with a custom signature-level permission so only my own signed APKs can bind."</p>
      </div>
    </div>
  </div>

  <!-- Q&A Section -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers — Android Services</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the difference between a Started Service, Bound Service, and Foreground Service?</div>
      <div class="qa-answer">
        <p><strong>Started Service:</strong> Launched via <code>startService()</code>. Runs indefinitely until stopped. No direct communication back to caller. Returns <code>START_STICKY</code>, <code>START_NOT_STICKY</code>, or <code>START_REDELIVER_INTENT</code> to tell OS what to do if killed.</p>
        <p><strong>Bound Service:</strong> Launched via <code>bindService()</code>. Lives as long as at least one client is bound. Exposes an <code>IBinder</code> for direct method calls. Destroyed when last client unbinds.</p>
        <p><strong>Foreground Service:</strong> A Started Service that calls <code>startForeground(id, notification)</code> within 5 seconds. Shows a persistent notification. OS gives it elevated priority and won't kill it under normal memory pressure. Required for long-running background work since Android 8.0.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q2</span>What is START_STICKY vs START_NOT_STICKY vs START_REDELIVER_INTENT?</div>
      <div class="qa-answer">
        <p>These are return values from <code>onStartCommand()</code> that tell the OS how to behave if it kills the service due to low memory:</p>
        <ul>
          <li><strong>START_STICKY:</strong> OS will restart the service, but the Intent passed to <code>onStartCommand</code> will be null. Good for services that manage their own state (e.g., music players).</li>
          <li><strong>START_NOT_STICKY:</strong> OS will NOT restart the service. Good for services that can be restarted manually by the user if needed (e.g., one-off sync).</li>
          <li><strong>START_REDELIVER_INTENT:</strong> OS will restart the service AND re-deliver the original Intent. Good for services that need the original data to resume (e.g., file download with a URL).</li>
        </ul>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>What changed in Android 14 for Foreground Services, and how do you handle it?</div>
      <div class="qa-answer">
        <p>Android 14 (API 34) requires that every Foreground Service declare a <code>foregroundServiceType</code> attribute in the manifest. This is enforced at runtime — missing it throws a <code>MissingForegroundServiceTypeException</code>.</p>
        <p>Valid types include: <code>camera</code>, <code>connectedDevice</code>, <code>dataSync</code>, <code>health</code>, <code>location</code>, <code>mediaPlayback</code>, <code>mediaProjection</code>, <code>microphone</code>, <code>phoneCall</code>, <code>remoteMessaging</code>, <code>shortService</code>, <code>specialUse</code>, <code>systemExempted</code>.</p>
        <p>Each type has an associated permission (e.g., <code>FOREGROUND_SERVICE_MEDIA_PLAYBACK</code>, <code>FOREGROUND_SERVICE_HEALTH</code>) that must be declared in the manifest.</p>
        <pre class="code-block"><code class="language-xml">&lt;uses-permission android:name="android.permission.FOREGROUND_SERVICE" /&gt;
&lt;uses-permission android:name="android.permission.FOREGROUND_SERVICE_HEALTH" /&gt;
&lt;service
    android:name=".VitalsService"
    android:foregroundServiceType="health"
    android:exported="false" /&gt;</code></pre>
        <p>Additionally, Android 14 added <code>shortService</code> type — a time-limited foreground service (max 3 minutes) that doesn't need a user-visible notification for that duration.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q4</span>When would you use AIDL vs Messenger vs a Bound Service with LocalBinder?</div>
      <div class="qa-answer">
        <ul>
          <li><strong>LocalBinder (same process):</strong> When the Service and client are in the same process. Return a direct reference to the Service object. Zero serialization overhead, full type safety, simplest code.</li>
          <li><strong>Messenger (cross-process, simple):</strong> When you need cross-process communication with simple message passing. Messages are processed sequentially on a Handler queue. Cannot return values synchronously — must use a reply Messenger for responses. Good for command/event patterns.</li>
          <li><strong>AIDL (cross-process, complex):</strong> When you need synchronous method calls across processes, multiple concurrent calls (runs on Binder thread pool), typed parameters and return values, and callback interfaces. Required when exposing SDK-style APIs to third-party apps.</li>
        </ul>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q5</span>Your music player app crashes with ForegroundServiceDidNotStartInTimeException on some devices. How do you diagnose and fix it?</div>
      <div class="qa-answer">
        <p>This exception means <code>startForeground()</code> was not called within 5 seconds of <code>startForegroundService()</code>. Causes:</p>
        <ol>
          <li><strong>Heavy work before startForeground():</strong> You might be doing database queries or I/O before calling it. Fix: Call <code>startForeground()</code> with a "Loading..." notification immediately at the top of <code>onStartCommand()</code>; do heavy work after in a coroutine.</li>
          <li><strong>startForeground() on a background thread:</strong> Must be called on the main thread. Fix: Ensure it's called directly in <code>onStartCommand()</code> which runs on main thread.</li>
          <li><strong>Service not reaching onStartCommand():</strong> Rare, but can happen if <code>onCreate()</code> throws before <code>onStartCommand()</code>. Fix: Add try/catch in onCreate.</li>
          <li><strong>Android 12+ exact alarm restrictions:</strong> If triggered by an alarm, the app may be in a state where it can't start foreground services. Fix: Use <code>setAlarmClock()</code> or WorkManager instead.</li>
        </ol>
        <p>Fix pattern: Call <code>startForeground()</code> as literally the first line in <code>onStartCommand()</code>, then dispatch all work to coroutines.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>How would you architect a Service that needs to communicate real-time data back to an Activity?</div>
      <div class="qa-answer">
        <p>The cleanest architecture uses a combination of <strong>Bound Service + SharedFlow/StateFlow</strong>:</p>
        <pre class="code-block"><code class="language-kotlin">// In the Service: expose a Flow
class SensorService : Service() {
    private val _sensorData = MutableStateFlow&lt;SensorReading?&gt;(null)
    val sensorData: StateFlow&lt;SensorReading?&gt; = _sensorData.asStateFlow()

    inner class LocalBinder : Binder() {
        fun getService() = this@SensorService
    }
    override fun onBind(intent: Intent) = LocalBinder()
}

// In ViewModel: collect after binding
class SensorViewModel : ViewModel() {
    private var service: SensorService? = null
    val readings = MutableStateFlow&lt;SensorReading?&gt;(null)

    fun onServiceConnected(svc: SensorService) {
        service = svc
        viewModelScope.launch {
            svc.sensorData.collect { readings.value = it }
        }
    }
}

// Activity just observes ViewModel's StateFlow
// This is clean: Service owns data, Activity is just a consumer</code></pre>
        <p>Alternative for simpler cases: use a <strong>LocalBroadcastManager</strong> (deprecated but still functional) or a <strong>shared repository</strong> with a Flow that both the Service and the ViewModel reference.</p>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge — Implement a Download Service</h3>
    <p><strong>Problem:</strong> Implement a foreground service that downloads multiple files sequentially, reports progress to a bound Activity, and handles being killed and restarted gracefully (START_REDELIVER_INTENT). Include proper notification management and cancellation support.</p>
    <pre class="code-block"><code class="language-kotlin">class DownloadService : Service() {

    data class DownloadTask(val url: String, val filename: String)
    data class DownloadProgress(val filename: String, val percent: Int, val done: Boolean)

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val _progress = MutableSharedFlow&lt;DownloadProgress&gt;(replay = 1)
    val progress: SharedFlow&lt;DownloadProgress&gt; = _progress.asSharedFlow()

    inner class DownloadBinder : Binder() {
        fun getService(): DownloadService = this@DownloadService
    }

    private val binder = DownloadBinder()
    private var currentJob: Job? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Must call startForeground immediately
        startForeground(NOTIF_ID, buildNotification("Starting download..."))

        val url = intent?.getStringExtra(EXTRA_URL) ?: run {
            stopSelf(startId)
            return START_NOT_STICKY
        }
        val filename = intent.getStringExtra(EXTRA_FILENAME) ?: "download"

        currentJob = scope.launch {
            try {
                downloadFile(DownloadTask(url, filename)) { percent ->
                    _progress.tryEmit(DownloadProgress(filename, percent, false))
                    updateNotification("Downloading $filename: $percent%")
                }
                _progress.emit(DownloadProgress(filename, 100, true))
                updateNotification("Download complete: $filename")
            } catch (e: CancellationException) {
                updateNotification("Download cancelled")
            } catch (e: IOException) {
                updateNotification("Download failed: ${e.message}")
            } finally {
                stopSelf(startId) // Safe stop — only if this is the latest startId
            }
        }

        // Guarantees intent is re-delivered if service is killed during download
        return START_REDELIVER_INTENT
    }

    private suspend fun downloadFile(task: DownloadTask, onProgress: (Int) -> Unit) {
        val url = java.net.URL(task.url)
        val connection = url.openConnection() as java.net.HttpURLConnection
        val totalBytes = connection.contentLength.toLong()
        var bytesRead = 0L

        withContext(Dispatchers.IO) {
            connection.inputStream.use { input ->
                java.io.FileOutputStream(
                    java.io.File(filesDir, task.filename)
                ).use { output ->
                    val buffer = ByteArray(8192)
                    var count: Int
                    while (input.read(buffer).also { count = it } != -1) {
                        ensureActive() // Respect cancellation
                        output.write(buffer, 0, count)
                        bytesRead += count
                        val percent = if (totalBytes > 0)
                            ((bytesRead * 100) / totalBytes).toInt()
                        else 0
                        onProgress(percent)
                    }
                }
            }
        }
    }

    fun cancelDownload() {
        currentJob?.cancel()
    }

    override fun onBind(intent: Intent): IBinder = binder

    override fun onDestroy() {
        scope.cancel()
    }

    private fun buildNotification(content: String): Notification {
        val channelId = "download_channel"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel(channelId, "Downloads", NotificationManager.IMPORTANCE_LOW)
                .also { getSystemService(NotificationManager::class.java).createNotificationChannel(it) }
        }
        return NotificationCompat.Builder(this, channelId)
            .setContentTitle("File Download")
            .setContentText(content)
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .setOngoing(true)
            .build()
    }

    private fun updateNotification(content: String) {
        getSystemService(NotificationManager::class.java)
            .notify(NOTIF_ID, buildNotification(content))
    }

    companion object {
        const val EXTRA_URL = "url"
        const val EXTRA_FILENAME = "filename"
        private const val NOTIF_ID = 3001
    }
}

// Time complexity: O(n) where n = file size in bytes
// Space complexity: O(1) — streams data, 8KB buffer regardless of file size
// Key features: cancellation support, progress reporting via SharedFlow,
//               safe stopSelf(startId), START_REDELIVER_INTENT for resilience
</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="23" data-item="0"> ✅ Understood Service types &amp; lifecycle</label>
    <label class="progress-check"><input type="checkbox" data-topic="23" data-item="1"> ✅ Can explain Foreground Service Android 14 requirements</label>
    <label class="progress-check"><input type="checkbox" data-topic="23" data-item="2"> ✅ Understand AIDL vs Messenger vs LocalBinder</label>
    <label class="progress-check"><input type="checkbox" data-topic="23" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="23" data-item="4"> ✅ Solved Download Service coding challenge</label>
  </div>
</section>

<!-- ========== TOPIC 24: BroadcastReceiver ========== -->
<section class="topic-section" id="topic-24">
  <div class="topic-header">
    <div class="topic-header-icon">📡</div>
    <div class="topic-header-text">
      <h1>BroadcastReceiver</h1>
      <p class="topic-tagline">System-wide event communication — the pub/sub bus of the Android OS</p>
      <div class="category-badge-group">
        <span class="cat-pill">BroadcastReceiver</span>
        <span class="cat-pill">System Events</span>
        <span class="cat-pill">Android 14</span>
        <span class="cat-pill">Security</span>
      </div>
    </div>
  </div>

  <!-- Subtopic 24-1 -->
  <div class="subtopic" id="subtopic-24-1">
    <h2>24.1 Static vs Dynamic Registration &amp; Ordered Broadcasts</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need BroadcastReceiver?</h3>
      <p>Android is an event-driven system. When the battery is low, the network connectivity changes, the device boots, or the timezone changes — apps need a way to react to these system events without continuously polling. BroadcastReceiver is the Android pub/sub mechanism that allows components (both within an app and across apps) to publish and subscribe to system-wide intent-based events.</p>
      <p>Without BroadcastReceiver, you'd need a continuously running service to poll system state — burning battery. The receiver model means your app can be completely inactive and still wake up exactly when a relevant event occurs.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is a BroadcastReceiver?</h3>
      <p>A <strong>BroadcastReceiver</strong> is a component that listens for system-wide or app-specific <code>Intent</code> broadcasts. There are two registration methods:</p>
      <ul>
        <li><strong>Static (Manifest) Registration:</strong> Declared in <code>AndroidManifest.xml</code> with an <code>&lt;intent-filter&gt;</code>. Since Android 8.0 (API 26), most implicit broadcasts are NOT delivered to statically registered receivers. Only a small explicit whitelist of broadcasts (like <code>BOOT_COMPLETED</code>) still work statically.</li>
        <li><strong>Dynamic Registration:</strong> Registered programmatically via <code>registerReceiver()</code> in code. Delivers all broadcasts while registered. Must be unregistered to avoid leaks. Android 13 (API 33) requires declaring <code>RECEIVER_EXPORTED</code> or <code>RECEIVER_NOT_EXPORTED</code> flag.</li>
      </ul>
      <p><strong>Ordered Broadcasts:</strong> Sent via <code>sendOrderedBroadcast()</code>. Delivered to receivers one at a time in priority order. Each receiver can modify or abort the broadcast. Used for priority-based processing chains.</p>
      <p><strong>LocalBroadcastManager:</strong> Was a simplified in-process broadcast mechanism. Deprecated in AndroidX 1.1.0 — use <strong>LiveData</strong>, <strong>SharedFlow</strong>, or <strong>EventBus</strong> instead.</p>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// ===== DYNAMIC REGISTRATION (preferred modern approach) =====

class NetworkStateReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // IMPORTANT: onReceive() runs on main thread — do NOT do long work here
        // You have ~10 seconds max before ANR
        when (intent.action) {
            ConnectivityManager.CONNECTIVITY_ACTION -> {
                val cm = context.getSystemService(ConnectivityManager::class.java)
                val network = cm.activeNetwork
                val capabilities = cm.getNetworkCapabilities(network)
                val isConnected = capabilities?.hasCapability(
                    NetworkCapabilities.NET_CAPABILITY_INTERNET
                ) == true
                // Delegate to a repository or post to a shared flow
                NetworkRepository.updateConnectivity(isConnected)
            }
        }
    }
}

// In Activity or Fragment — register dynamically
class MainActivity : AppCompatActivity() {
    private val networkReceiver = NetworkStateReceiver()
    private val networkFilter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)

    override fun onStart() {
        super.onStart()
        // Android 13+ requires RECEIVER_NOT_EXPORTED or RECEIVER_EXPORTED flag
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            registerReceiver(networkReceiver, networkFilter, RECEIVER_NOT_EXPORTED)
        } else {
            registerReceiver(networkReceiver, networkFilter)
        }
    }

    override fun onStop() {
        super.onStop()
        unregisterReceiver(networkReceiver) // CRITICAL: prevents memory leak
    }
}

// ===== STATIC REGISTRATION (manifest) — only for whitelisted broadcasts =====
// In AndroidManifest.xml:
// &lt;receiver android:name=".BootReceiver" android:exported="true"&gt;
//     &lt;intent-filter&gt;
//         &lt;action android:name="android.intent.action.BOOT_COMPLETED" /&gt;
//     &lt;/intent-filter&gt;
// &lt;/receiver&gt;
// Also requires: &lt;uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" /&gt;

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            // Reschedule WorkManager jobs after boot
            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                "sync_work",
                ExistingPeriodicWorkPolicy.KEEP,
                PeriodicWorkRequestBuilder&lt;SyncWorker&gt;(1, TimeUnit.HOURS).build()
            )
        }
    }
}

// ===== ORDERED BROADCASTS =====
// Send
val intent = Intent("com.example.PROCESS_PAYMENT")
sendOrderedBroadcast(intent, "com.example.PAYMENT_PERMISSION")

// High-priority receiver (processes first, can modify/abort)
class PrimaryPaymentReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Modify result for next receiver
        setResult(RESULT_OK, "processed_by_primary", null)
        // Or abort: abortBroadcast() — prevents delivery to lower-priority receivers
    }
}

// Low-priority receiver (gets modified result)
class AuditPaymentReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val result = resultData // Gets data set by PrimaryPaymentReceiver
        logAudit(result)
    }
}
</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs</h3>
      <pre class="code-block"><code class="language-kotlin">// Sending broadcasts
context.sendBroadcast(Intent("com.example.MY_ACTION"))

// Restricted to apps with a permission
context.sendBroadcast(
    Intent("com.example.MY_ACTION"),
    "com.example.RECEIVE_MY_ACTION" // receiverPermission
)

// Explicit broadcast to a specific package (required for cross-app on Android 8+)
Intent("com.example.SYNC_DATA").apply {
    setPackage("com.example.targetapp")
}.also { context.sendBroadcast(it) }

// Ordered broadcast with result receiver
sendOrderedBroadcast(
    intent,
    null,                     // receiverPermission
    object : BroadcastReceiver() {   // resultReceiver — called LAST
        override fun onReceive(context: Context, intent: Intent) {
            val finalResult = resultData
        }
    },
    null, Activity.RESULT_OK, null, null
)

// Android 14 (API 34): Context-registered receivers exported state
// Must specify one of:
registerReceiver(receiver, filter, RECEIVER_EXPORTED)
registerReceiver(receiver, filter, RECEIVER_NOT_EXPORTED)

// Important system broadcasts that STILL work statically (Android 8+ whitelist):
// ACTION_BOOT_COMPLETED, ACTION_LOCKED_BOOT_COMPLETED
// ACTION_MY_PACKAGE_REPLACED, ACTION_PACKAGE_REPLACED (with data scheme)
// ACTION_TIME_CHANGED, ACTION_TIMEZONE_CHANGED
// ACTION_LOCALE_CHANGED
// SMS_RECEIVED (with permission)
// Full list: https://developer.android.com/guide/components/broadcast-exceptions

// Modern replacement for LocalBroadcastManager:
// Use SharedFlow for in-process event bus
object AppEventBus {
    private val _events = MutableSharedFlow&lt;AppEvent&gt;(
        replay = 0,
        extraBufferCapacity = 64,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val events: SharedFlow&lt;AppEvent&gt; = _events.asSharedFlow()

    suspend fun emit(event: AppEvent) = _events.emit(event)
    fun tryEmit(event: AppEvent) = _events.tryEmit(event)
}
</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World: FinTech — Payment Terminal State Monitoring</h3>
      <p>A payment terminal app needs to react to USB device attachment (for card readers), network changes (for payment gateway connectivity), and low battery (to warn cashiers before transactions fail). All of these require BroadcastReceiver.</p>
      <pre class="code-block"><code class="language-kotlin">class PaymentTerminalReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        val terminalRepository = TerminalRepository.getInstance()

        when (intent.action) {
            UsbManager.ACTION_USB_DEVICE_ATTACHED -> {
                val device: UsbDevice? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    intent.getParcelableExtra(UsbManager.EXTRA_DEVICE, UsbDevice::class.java)
                } else {
                    @Suppress("DEPRECATION")
                    intent.getParcelableExtra(UsbManager.EXTRA_DEVICE)
                }
                device?.let { terminalRepository.onCardReaderAttached(it) }
            }

            UsbManager.ACTION_USB_DEVICE_DETACHED -> {
                terminalRepository.onCardReaderDetached()
            }

            Intent.ACTION_BATTERY_LOW -> {
                // CRITICAL: cannot do long work here — schedule a WorkManager task
                WorkManager.getInstance(context)
                    .enqueue(OneTimeWorkRequestBuilder&lt;LowBatteryAlertWorker&gt;().build())
            }

            ConnectivityManager.CONNECTIVITY_ACTION -> {
                // Deprecated but still used for immediate notification
                // Modern alternative: NetworkCallback via ConnectivityManager.registerNetworkCallback
                terminalRepository.refreshGatewayConnection()
            }
        }
    }
}

// Register with all needed filters
val filter = IntentFilter().apply {
    addAction(UsbManager.ACTION_USB_DEVICE_ATTACHED)
    addAction(UsbManager.ACTION_USB_DEVICE_DETACHED)
    addAction(Intent.ACTION_BATTERY_LOW)
    addAction(ConnectivityManager.CONNECTIVITY_ACTION)
}
registerReceiver(paymentReceiver, filter, RECEIVER_NOT_EXPORTED)
</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Doing long work in onReceive():</strong> onReceive runs on the main thread and has a ~10s budget. ✅ Fix: Use <code>goAsync()</code> to get a <code>PendingResult</code> and finish work on a coroutine, or enqueue a WorkManager task.</li>
        <li>❌ <strong>Forgetting to unregister dynamic receivers:</strong> Causes memory leaks and potential crashes if context is destroyed. ✅ Fix: Always call <code>unregisterReceiver()</code> in the matching lifecycle method (onStop/onDestroy).</li>
        <li>❌ <strong>Using implicit broadcasts on Android 8+ with static registration:</strong> They are never delivered. ✅ Fix: Use dynamic registration for implicit broadcasts; use explicit intents with <code>setPackage()</code> for cross-app explicit broadcasts.</li>
        <li>❌ <strong>Missing RECEIVER_EXPORTED flag on Android 13+:</strong> Causes <code>SecurityException</code>. ✅ Fix: Always specify <code>RECEIVER_EXPORTED</code> or <code>RECEIVER_NOT_EXPORTED</code> when calling <code>registerReceiver()</code> on API 33+.</li>
        <li>❌ <strong>Using LocalBroadcastManager in new code:</strong> Deprecated — less efficient than Flows and requires global state. ✅ Fix: Replace with SharedFlow, StateFlow, or LiveData for in-process events.</li>
        <li>❌ <strong>Not protecting custom broadcasts with permissions:</strong> Any app can send your custom actions. ✅ Fix: Use <code>sendBroadcast(intent, permission)</code> and declare the permission with <code>android:protectionLevel="signature"</code>.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"In modern Android, I treat BroadcastReceiver as a thin dispatcher layer — its only job is to receive an event, do minimal processing, and delegate real work to WorkManager or a Service. Since Android 8, static registration is essentially dead for implicit broadcasts; I always register dynamically and register/unregister symmetrically with the component lifecycle. For in-process pub/sub, I've replaced LocalBroadcastManager entirely with SharedFlow — it integrates with structured concurrency, supports backpressure configuration, and is much easier to test. When I do use broadcasts for cross-app communication, I always protect them with a signature-level permission and verify the caller's identity in <code>onReceive()</code>. The goAsync() API is crucial for any non-trivial work — it gives you a longer execution window on a background thread while keeping the broadcast result pending."</p>
      </div>
    </div>
  </div>

  <!-- Q&A -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers — BroadcastReceiver</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the difference between static and dynamic BroadcastReceiver registration?</div>
      <div class="qa-answer">
        <p><strong>Static:</strong> Declared in AndroidManifest.xml. The system delivers broadcasts even if your app is not running (for whitelisted system broadcasts). Since Android 8.0, most implicit broadcasts are NOT delivered to statically registered receivers — only a small whitelist still works (BOOT_COMPLETED, etc.).</p>
        <p><strong>Dynamic:</strong> Registered via <code>registerReceiver()</code> in code. Only receives broadcasts while the component is alive and registered. Must be unregistered to prevent leaks. Works for all broadcast types. On Android 13+, must specify <code>RECEIVER_EXPORTED</code> or <code>RECEIVER_NOT_EXPORTED</code>.</p>
        <p><strong>Best practice:</strong> Prefer dynamic registration for most use cases. Use static only for broadcasts that must work when the app is not running (BOOT_COMPLETED, SMS_RECEIVED).</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q2</span>What is goAsync() and when would you use it?</div>
      <div class="qa-answer">
        <p><code>goAsync()</code> extends the execution window of <code>onReceive()</code>. Normally you have ~10 seconds on the main thread. By calling <code>goAsync()</code>, you get a <code>PendingResult</code> object and the broadcast is kept "alive" even after <code>onReceive()</code> returns. You can then do work on a background thread and call <code>pendingResult.finish()</code> when done.</p>
        <pre class="code-block"><code class="language-kotlin">override fun onReceive(context: Context, intent: Intent) {
    val pendingResult = goAsync()
    CoroutineScope(Dispatchers.IO).launch {
        try {
            processData(intent)
        } finally {
            pendingResult.finish() // MUST call finish or broadcast leaks
        }
    }
}</code></pre>
        <p><strong>Use when:</strong> You need to do background work but don't want to start a full Service. Good for short async operations (a few seconds). For longer work, use WorkManager instead.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>What are ordered broadcasts and how do you use priority and abort?</div>
      <div class="qa-answer">
        <p>Ordered broadcasts (sent via <code>sendOrderedBroadcast()</code>) are delivered to receivers one at a time in descending priority order (set via <code>android:priority</code> in the intent-filter, range -1000 to 1000).</p>
        <p>Each receiver can:</p>
        <ul>
          <li><strong>Pass data forward:</strong> <code>setResult(resultCode, resultData, extras)</code> — next receiver gets these values via <code>getResultData()</code> etc.</li>
          <li><strong>Abort delivery:</strong> <code>abortBroadcast()</code> — no subsequent receivers (with lower priority) receive the broadcast. System receivers with higher priority can still override this in some cases.</li>
        </ul>
        <p><strong>Real use case:</strong> SMS blocking apps intercept <code>SMS_RECEIVED</code> with high priority, validate the SMS, and abort it to prevent the default messaging app from receiving spam.</p>
        <pre class="code-block"><code class="language-kotlin">// IntentFilter with priority
val filter = IntentFilter(Telephony.Sms.Intents.SMS_RECEIVED_ACTION).apply {
    priority = 999 // Higher than default messaging apps
}
registerReceiver(smsBlocker, filter)

// In the receiver
override fun onReceive(context: Context, intent: Intent) {
    if (isSpam(intent)) {
        abortBroadcast() // Prevents messaging apps from seeing this SMS
    }
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q4</span>What Android 14 restrictions apply to BroadcastReceivers and how do you adapt?</div>
      <div class="qa-answer">
        <p>Android 14 (API 34) introduced two key changes:</p>
        <ol>
          <li><strong>Context-registered receivers must declare export state:</strong> Already required since Android 13 — <code>RECEIVER_EXPORTED</code> or <code>RECEIVER_NOT_EXPORTED</code> flag. Android 14 enforces this more strictly.</li>
          <li><strong>Broadcast queue changes:</strong> The system can now batch and defer non-manifest broadcasts to improve battery. Apps targeting API 34 may see delayed delivery for non-critical broadcasts.</li>
          <li><strong>Restricted Broadcasts:</strong> More system broadcasts are restricted from third-party apps. For example, some intent actions that were previously accessible are now protected.</li>
        </ol>
        <p><strong>Adaptation strategy:</strong></p>
        <ul>
          <li>For real-time connectivity: use <code>ConnectivityManager.registerNetworkCallback()</code> instead of <code>CONNECTIVITY_ACTION</code> broadcast.</li>
          <li>For battery changes: use <code>BatteryManager</code> APIs directly via <code>getSystemService()</code>.</li>
          <li>For in-app events: use SharedFlow/StateFlow in a singleton or ViewModel.</li>
          <li>For deferred work triggered by broadcasts: delegate immediately to WorkManager in <code>onReceive()</code>.</li>
        </ul>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q5</span>How would you ensure your custom broadcast cannot be intercepted by malicious apps?</div>
      <div class="qa-answer">
        <p>Multiple layers of protection:</p>
        <ol>
          <li><strong>Signature-level permission:</strong> Declare a custom permission with <code>android:protectionLevel="signature"</code>. Only apps signed with the same key can receive/send this broadcast.</li>
          <li><strong>Sender permission check:</strong> When sending, require receivers to hold a permission. When receiving, verify the sender holds a permission.</li>
          <li><strong>Use explicit intents for same-app broadcasts:</strong> <code>intent.setPackage(context.packageName)</code> restricts delivery to your own app.</li>
          <li><strong>Verify caller identity in onReceive:</strong> Check <code>context.checkCallingPermission()</code> or validate the sender package name.</li>
        </ol>
        <pre class="code-block"><code class="language-kotlin">// In manifest:
// &lt;permission android:name="com.example.RECEIVE_PAYMENT"
//             android:protectionLevel="signature" /&gt;
// &lt;uses-permission android:name="com.example.RECEIVE_PAYMENT" /&gt;

// Sending — only receivers with permission can receive
sendBroadcast(
    Intent("com.example.PAYMENT_EVENT"),
    "com.example.RECEIVE_PAYMENT"
)

// Receiving — only senders with this permission deliver to us
registerReceiver(
    paymentReceiver,
    IntentFilter("com.example.PAYMENT_EVENT"),
    "com.example.RECEIVE_PAYMENT", // senderPermission
    null,
    RECEIVER_NOT_EXPORTED
)</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>Your app needs to react to network changes immediately. BroadcastReceiver with CONNECTIVITY_ACTION or NetworkCallback — which and why?</div>
      <div class="qa-answer">
        <p><strong>Use NetworkCallback — always, for modern apps.</strong></p>
        <p><code>CONNECTIVITY_ACTION</code> is deprecated since API 28 for dynamic receivers and doesn't work with static receivers on API 26+. It doesn't provide detailed network capability information and isn't reliable for real-time monitoring.</p>
        <p><code>ConnectivityManager.NetworkCallback</code> is the correct modern API:</p>
        <pre class="code-block"><code class="language-kotlin">class NetworkMonitor(private val context: Context) {
    private val cm = context.getSystemService(ConnectivityManager::class.java)
    private val _isConnected = MutableStateFlow(false)
    val isConnected: StateFlow&lt;Boolean&gt; = _isConnected.asStateFlow()

    private val callback = object : ConnectivityManager.NetworkCallback() {
        override fun onAvailable(network: Network) {
            _isConnected.value = true
        }
        override fun onLost(network: Network) {
            _isConnected.value = false
        }
        override fun onCapabilitiesChanged(
            network: Network,
            capabilities: NetworkCapabilities
        ) {
            val hasInternet = capabilities.hasCapability(
                NetworkCapabilities.NET_CAPABILITY_INTERNET
            )
            _isConnected.value = hasInternet
        }
    }

    fun register() {
        val request = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .build()
        cm.registerNetworkCallback(request, callback)
    }

    fun unregister() {
        cm.unregisterNetworkCallback(callback)
    }
}</code></pre>
        <p>This gives per-network granularity, capability-based filtering (WiFi, cellular, validated internet), and works correctly on all modern API levels.</p>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge — Smart Broadcast Event Bus</h3>
    <p><strong>Problem:</strong> Implement a production-grade in-process event bus using SharedFlow that replaces LocalBroadcastManager, supports multiple event types, backpressure handling, and integrates cleanly with ViewModels. Also implement a BroadcastReceiver that safely delegates work to a coroutine using goAsync().</p>
    <pre class="code-block"><code class="language-kotlin">// Type-safe event hierarchy
sealed class AppEvent {
    data class NetworkChanged(val isConnected: Boolean) : AppEvent()
    data class UserLoggedIn(val userId: String) : AppEvent()
    data class PaymentCompleted(val transactionId: String, val amount: Double) : AppEvent()
    object SessionExpired : AppEvent()
}

// Singleton event bus with per-type filtering
object AppEventBus {
    private val _events = MutableSharedFlow&lt;AppEvent&gt;(
        replay = 0,
        extraBufferCapacity = 128,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    // Public read-only stream
    val events: SharedFlow&lt;AppEvent&gt; = _events.asSharedFlow()

    // Suspend for guaranteed delivery
    suspend fun publish(event: AppEvent) = _events.emit(event)

    // Non-suspending for fire-and-forget from non-coroutine contexts
    fun tryPublish(event: AppEvent): Boolean = _events.tryEmit(event)

    // Convenience: subscribe to specific event type only
    inline fun &lt;reified T : AppEvent&gt; Flow&lt;AppEvent&gt;.ofType(): Flow&lt;T&gt; =
        filterIsInstance&lt;T&gt;()
}

// ViewModel consuming specific events
class PaymentViewModel : ViewModel() {
    val paymentEvents = AppEventBus.events
        .filterIsInstance&lt;AppEvent.PaymentCompleted&gt;()
        .stateIn(
            viewModelScope,
            SharingStarted.WhileSubscribed(5000),
            null
        )
}

// BroadcastReceiver using goAsync() safely
class SmsSyncReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val pendingResult = goAsync()
        // Use application context — Activity context may be destroyed
        val appContext = context.applicationContext

        CoroutineScope(SupervisorJob() + Dispatchers.IO).launch {
            try {
                val messages = SmsRepository.getInstance(appContext)
                    .syncNewMessages(intent)

                // Publish to event bus for any observer
                AppEventBus.publish(AppEvent.NetworkChanged(true))

                // Update notification count
                withContext(Dispatchers.Main) {
                    BadgeManager.update(appContext, messages.size)
                }
            } catch (e: Exception) {
                Log.e("SmsSyncReceiver", "Failed to sync SMS", e)
            } finally {
                // MUST always call finish() or broadcast system resource leaks
                pendingResult.finish()
            }
        }
    }
}

// Time: O(1) for publish, O(n) for n subscribers per event
// Space: O(extraBufferCapacity) = O(128) for SharedFlow buffer
</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="24" data-item="0"> ✅ Understood Static vs Dynamic registration</label>
    <label class="progress-check"><input type="checkbox" data-topic="24" data-item="1"> ✅ Can explain Android 8+ broadcast restrictions</label>
    <label class="progress-check"><input type="checkbox" data-topic="24" data-item="2"> ✅ Know goAsync() and permission protection</label>
    <label class="progress-check"><input type="checkbox" data-topic="24" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="24" data-item="4"> ✅ Solved Event Bus coding challenge</label>
  </div>
</section>

<!-- ========== TOPIC 25: ContentProvider ========== -->
<section class="topic-section" id="topic-25">
  <div class="topic-header">
    <div class="topic-header-icon">🗃️</div>
    <div class="topic-header-text">
      <h1>ContentProvider</h1>
      <p class="topic-tagline">Structured data sharing across app boundaries — with FileProvider for secure file access</p>
      <div class="category-badge-group">
        <span class="cat-pill">ContentProvider</span>
        <span class="cat-pill">FileProvider</span>
        <span class="cat-pill">ContentResolver</span>
        <span class="cat-pill">URI Matching</span>
      </div>
    </div>
  </div>

  <div class="subtopic" id="subtopic-25-1">
    <h2>25.1 ContentProvider CRUD, URI Matching &amp; MIME Types</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need ContentProvider?</h3>
      <p>Android's process isolation means apps cannot directly access each other's databases or files. ContentProvider solves the cross-app structured data access problem. Without it, the Contacts app couldn't share your contacts with other apps, the media store couldn't expose photos to gallery apps, and you couldn't let other apps access your app's structured data in a controlled, permission-gated way.</p>
      <p>ContentProvider also provides a <strong>standardized query interface</strong> (like SQL through a URI) that allows Loaders, CursorAdapters, and ContentObservers to work uniformly across any data source — local DB, network, files — without the consumer needing to know the implementation details.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is a ContentProvider?</h3>
      <p>A <strong>ContentProvider</strong> is a component that manages shared access to a structured set of data. Clients access it via a <code>ContentResolver</code> using a <code>content://</code> URI scheme. The provider handles security, data serialization, and multi-process access internally.</p>
      <p>Key concepts:</p>
      <ul>
        <li><strong>Content URI:</strong> <code>content://authority/table/id</code> — uniquely identifies data. Authority is the provider's unique identifier (typically your package name).</li>
        <li><strong>UriMatcher:</strong> Routes incoming URIs to specific query handlers.</li>
        <li><strong>MIME Types:</strong> Describe the type of data. Collections use <code>vnd.android.cursor.dir/</code>, single items use <code>vnd.android.cursor.item/</code>.</li>
        <li><strong>ContentObserver:</strong> Notifies clients when data changes via <code>notifyChange()</code>.</li>
      </ul>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// Production ContentProvider for a medication database (Healthcare)
class MedicationProvider : ContentProvider() {

    private lateinit var database: MedicationDatabase

    companion object {
        const val AUTHORITY = "com.healthcare.app.medications"
        val CONTENT_URI: Uri = Uri.parse("content://$AUTHORITY")

        // URI pattern codes
        private const val MEDICATIONS = 100
        private const val MEDICATION_ID = 101
        private const val SCHEDULES = 200
        private const val SCHEDULE_ID = 201

        private val uriMatcher = UriMatcher(UriMatcher.NO_MATCH).apply {
            addURI(AUTHORITY, "medications", MEDICATIONS)
            addURI(AUTHORITY, "medications/#", MEDICATION_ID)  // # matches digits
            addURI(AUTHORITY, "schedules", SCHEDULES)
            addURI(AUTHORITY, "schedules/#", SCHEDULE_ID)
            // addURI(AUTHORITY, "user/*/meds", ...) // * matches any string
        }

        // MIME type constants
        const val MIME_TYPE_MEDICATIONS = "vnd.android.cursor.dir/vnd.$AUTHORITY.medications"
        const val MIME_TYPE_MEDICATION = "vnd.android.cursor.item/vnd.$AUTHORITY.medications"
    }

    override fun onCreate(): Boolean {
        // ContentProvider.onCreate() is called BEFORE Application.onCreate()
        // Keep this as lightweight as possible
        database = MedicationDatabase.getInstance(context!!)
        return true
    }

    override fun query(
        uri: Uri,
        projection: Array&lt;String&gt;?,
        selection: String?,
        selectionArgs: Array&lt;String&gt;?,
        sortOrder: String?
    ): Cursor? {
        // Validate caller has READ permission
        context?.checkCallingOrSelfPermission(
            "com.healthcare.app.READ_MEDICATIONS"
        )?.also { if (it != PackageManager.PERMISSION_GRANTED) throw SecurityException("Requires READ_MEDICATIONS permission") }

        val cursor = when (uriMatcher.match(uri)) {
            MEDICATIONS -> database.medicationDao().queryAll(
                selection, selectionArgs, sortOrder
            )
            MEDICATION_ID -> {
                val id = ContentUris.parseId(uri)
                database.medicationDao().queryById(id)
            }
            SCHEDULES -> database.scheduleDao().queryAll(selection, selectionArgs, sortOrder)
            else -> throw IllegalArgumentException("Unknown URI: $uri")
        }

        // Register cursor to watch for content changes
        cursor?.setNotificationUri(context?.contentResolver, uri)
        return cursor
    }

    override fun insert(uri: Uri, values: ContentValues?): Uri? {
        requireNotNull(values) { "ContentValues cannot be null" }
        val id = when (uriMatcher.match(uri)) {
            MEDICATIONS -> database.medicationDao().insert(Medication.from(values))
            SCHEDULES -> database.scheduleDao().insert(Schedule.from(values))
            else -> throw IllegalArgumentException("Unknown URI: $uri")
        }

        // Notify all observers of this URI that data changed
        context?.contentResolver?.notifyChange(uri, null)
        return ContentUris.withAppendedId(uri, id)
    }

    override fun update(
        uri: Uri, values: ContentValues?,
        selection: String?, selectionArgs: Array&lt;String&gt;?
    ): Int {
        val count = when (uriMatcher.match(uri)) {
            MEDICATION_ID -> {
                val id = ContentUris.parseId(uri)
                database.medicationDao().update(id, values!!)
            }
            else -> throw IllegalArgumentException("Unknown URI: $uri")
        }
        if (count > 0) context?.contentResolver?.notifyChange(uri, null)
        return count
    }

    override fun delete(uri: Uri, selection: String?, selectionArgs: Array&lt;String&gt;?): Int {
        val count = when (uriMatcher.match(uri)) {
            MEDICATION_ID -> {
                val id = ContentUris.parseId(uri)
                database.medicationDao().delete(id)
            }
            MEDICATIONS -> database.medicationDao().deleteAll()
            else -> throw IllegalArgumentException("Unknown URI: $uri")
        }
        if (count > 0) context?.contentResolver?.notifyChange(uri, null)
        return count
    }

    override fun getType(uri: Uri): String = when (uriMatcher.match(uri)) {
        MEDICATIONS -> MIME_TYPE_MEDICATIONS
        MEDICATION_ID -> MIME_TYPE_MEDICATION
        else -> throw IllegalArgumentException("Unknown URI: $uri")
    }
}
</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs — ContentResolver</h3>
      <pre class="code-block"><code class="language-kotlin">// Querying via ContentResolver (client side)
val contentResolver = context.contentResolver

// Query all medications
val cursor = contentResolver.query(
    MedicationProvider.CONTENT_URI.buildUpon().appendPath("medications").build(),
    arrayOf("_id", "name", "dosage", "frequency"), // projection
    "active = ?",                                   // selection
    arrayOf("1"),                                   // selectionArgs
    "name ASC"                                      // sortOrder
)

cursor?.use { c ->
    val nameIndex = c.getColumnIndexOrThrow("name")
    val dosageIndex = c.getColumnIndexOrThrow("dosage")
    while (c.moveToNext()) {
        val name = c.getString(nameIndex)
        val dosage = c.getString(dosageIndex)
    }
}

// Insert
val values = ContentValues().apply {
    put("name", "Aspirin")
    put("dosage", "100mg")
    put("frequency", "daily")
    put("active", 1)
}
val newUri = contentResolver.insert(
    Uri.parse("content://com.healthcare.app.medications/medications"),
    values
)

// Update
val updated = contentResolver.update(
    ContentUris.withAppendedId(
        Uri.parse("content://com.healthcare.app.medications/medications"), 42L
    ),
    ContentValues().apply { put("active", 0) },
    null, null
)

// Delete
val deleted = contentResolver.delete(
    ContentUris.withAppendedId(
        Uri.parse("content://com.healthcare.app.medications/medications"), 42L
    ),
    null, null
)

// Observe changes with ContentObserver
val observer = object : ContentObserver(Handler(Looper.getMainLooper())) {
    override fun onChange(selfChange: Boolean, uri: Uri?) {
        // Data changed — refresh UI
        lifecycleScope.launch { viewModel.refresh() }
    }
}
contentResolver.registerContentObserver(
    Uri.parse("content://com.healthcare.app.medications/medications"),
    true, // notifyForDescendants
    observer
)
// Don't forget to unregister!
contentResolver.unregisterContentObserver(observer)
</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World: FileProvider for Secure File Sharing</h3>
      <p>In Android 7.0+, you cannot share <code>file://</code> URIs with other apps (throws <code>FileUriExposedException</code>). <strong>FileProvider</strong> generates <code>content://</code> URIs with temporary, permission-scoped access — the standard for sharing camera photos, PDFs, or exported files.</p>
      <pre class="code-block"><code class="language-kotlin">// 1. Declare in AndroidManifest.xml
// &lt;provider
//     android:name="androidx.core.content.FileProvider"
//     android:authorities="${applicationId}.fileprovider"
//     android:exported="false"
//     android:grantUriPermissions="true"&gt;
//     &lt;meta-data
//         android:name="android.support.FILE_PROVIDER_PATHS"
//         android:resource="@xml/file_provider_paths" /&gt;
// &lt;/provider&gt;

// 2. Create res/xml/file_provider_paths.xml
// &lt;paths&gt;
//     &lt;files-path name="my_images" path="images/" /&gt;
//     &lt;cache-path name="my_cache" path="/" /&gt;
//     &lt;external-files-path name="my_external" path="documents/" /&gt;
// &lt;/paths&gt;

// 3. Share a file
fun shareReport(reportFile: File) {
    val contentUri = FileProvider.getUriForFile(
        context,
        "${context.packageName}.fileprovider",
        reportFile
    )

    val shareIntent = Intent(Intent.ACTION_SEND).apply {
        type = "application/pdf"
        putExtra(Intent.EXTRA_STREAM, contentUri)
        // Grant temporary read permission to the receiving app
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }
    context.startActivity(Intent.createChooser(shareIntent, "Share Report"))
}

// Camera capture with FileProvider
fun takePicture(): Uri {
    val photoFile = File(context.filesDir, "images/photo_${System.currentTimeMillis()}.jpg")
        .also { it.parentFile?.mkdirs() }

    val photoUri = FileProvider.getUriForFile(
        context,
        "${context.packageName}.fileprovider",
        photoFile
    )

    val takePictureIntent = Intent(MediaStore.ACTION_IMAGE_CAPTURE).apply {
        putExtra(MediaStore.EXTRA_OUTPUT, photoUri)
    }
    cameraLauncher.launch(takePictureIntent)
    return photoUri
}
</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Doing heavy database work in ContentProvider.onCreate():</strong> Called before Application.onCreate() and on the main thread. ✅ Fix: Initialize lazily or use a background thread for the first real query.</li>
        <li>❌ <strong>Not calling notifyChange() after mutations:</strong> ContentObservers and CursorLoaders won't refresh. ✅ Fix: Always call <code>contentResolver.notifyChange(uri, null)</code> in insert/update/delete.</li>
        <li>❌ <strong>Sharing file:// URIs on Android 7+:</strong> Throws <code>FileUriExposedException</code>. ✅ Fix: Always use FileProvider to generate content:// URIs.</li>
        <li>❌ <strong>Not closing Cursors:</strong> Memory leak and resource exhaustion. ✅ Fix: Always use <code>cursor?.use { }</code> or <code>try/finally { cursor?.close() }</code>.</li>
        <li>❌ <strong>Using ContentProvider when Room suffices:</strong> ContentProvider adds complexity. ✅ Fix: Use Room directly within your app. Only use ContentProvider when other apps need structured access to your data.</li>
        <li>❌ <strong>Not protecting with permissions:</strong> Any installed app can query your provider. ✅ Fix: Set <code>android:readPermission</code> and <code>android:writePermission</code> on the &lt;provider&gt; element.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"ContentProvider is a narrow use case in modern Android — I only use it when I genuinely need to expose structured data to other apps. Within my own app, Room with a Repository is always the right choice. When I do implement a ContentProvider, I pay attention to three critical things: First, <code>onCreate()</code> runs before <code>Application.onCreate()</code> on the main thread, so I never do heavy initialization there. Second, I always call <code>notifyChange()</code> after mutations so observers stay in sync. Third, I protect the provider with custom permissions at the signature level. For file sharing, I never use file:// URIs — FileProvider generates content:// URIs with fine-grained, time-limited permissions that are safe to pass to camera apps, email clients, or PDF viewers."</p>
      </div>
    </div>
  </div>

  <!-- Q&A -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers — ContentProvider</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the difference between ContentProvider and Room? When do you use each?</div>
      <div class="qa-answer">
        <p><strong>Room:</strong> An ORM/database abstraction for local, in-process data storage. Type-safe, compiles queries at build time, supports LiveData/Flow. Use Room for all local data persistence within your own app.</p>
        <p><strong>ContentProvider:</strong> A component that exposes data to other apps via a standardized <code>content://</code> URI interface with a <code>ContentResolver</code>. It can use Room as its backing store internally.</p>
        <p><strong>Use ContentProvider when:</strong></p>
        <ul>
          <li>Other apps need to access your data (e.g., Contacts, Calendar, MediaStore APIs).</li>
          <li>You're implementing a SyncAdapter (requires ContentProvider).</li>
          <li>You need ContentObserver-based change notifications for cross-app cursors.</li>
          <li>You're building an SDK where other developers will query your data.</li>
        </ul>
        <p><strong>Do NOT use ContentProvider when:</strong> Only your own app accesses the data. Room + Repository is simpler, faster, and type-safe.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q2</span>What is UriMatcher and what URI patterns does it support?</div>
      <div class="qa-answer">
        <p><code>UriMatcher</code> routes incoming content URIs to integer codes that your ContentProvider uses to determine which table/operation to execute.</p>
        <pre class="code-block"><code class="language-kotlin">val matcher = UriMatcher(UriMatcher.NO_MATCH).apply {
    // Matches: content://authority/notes
    addURI("com.example.app", "notes", NOTES_ALL)
    // Matches: content://authority/notes/123 (# = any digit)
    addURI("com.example.app", "notes/#", NOTES_ID)
    // Matches: content://authority/user/john/notes (* = any string)
    addURI("com.example.app", "user/*/notes", USER_NOTES)
}

when (matcher.match(uri)) {
    NOTES_ALL -> // query all notes
    NOTES_ID -> // query specific note
    UriMatcher.NO_MATCH -> throw IllegalArgumentException("Unknown URI: $uri")
}</code></pre>
        <p>Patterns: <code>#</code> matches any number, <code>*</code> matches any string of characters.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>Why does ContentProvider.onCreate() get called before Application.onCreate(), and what are the implications?</div>
      <div class="qa-answer">
        <p>The Android system initializes <code>ContentProvider</code> instances immediately after the Application object is created but <strong>before</strong> <code>Application.onCreate()</code> is called. This is because the system may need to provide data to other components (like SyncAdapters) before the app fully initializes.</p>
        <p><strong>Implications:</strong></p>
        <ul>
          <li>You cannot rely on any initialization done in <code>Application.onCreate()</code> — dependency injection, Timber logging, Sentry, etc. may not be ready.</li>
          <li>Heavy database initialization in <code>ContentProvider.onCreate()</code> blocks the main thread and slows app startup.</li>
          <li>App Startup library abuses this behavior intentionally — it uses a dummy ContentProvider to run initializers in the correct order at startup.</li>
        </ul>
        <p><strong>Best practice:</strong> In <code>ContentProvider.onCreate()</code>, only store the context reference. Initialize the database lazily in <code>query()</code> using <code>lazy()</code> or <code>synchronized()</code>.</p>
        <pre class="code-block"><code class="language-kotlin">override fun onCreate(): Boolean {
    // DON'T: database = HeavyDatabase.build(context!!)
    // DO: initialize lazily
    return true
}

private val database by lazy {
    HeavyDatabase.build(context!!)
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q4</span>How does FileProvider work internally, and why is it safer than file:// URIs?</div>
      <div class="qa-answer">
        <p><strong>file:// URIs</strong> expose the raw filesystem path. The receiving app must have READ_EXTERNAL_STORAGE permission to access it, and the file must be world-readable. Android 7.0 banned this pattern via <code>StrictMode</code> and throws <code>FileUriExposedException</code>.</p>
        <p><strong>FileProvider</strong> is a ContentProvider subclass that:</p>
        <ol>
          <li>Maps real filesystem paths to <code>content://</code> URIs based on the <code>file_provider_paths.xml</code> configuration.</li>
          <li>Grants <strong>temporary, revocable</strong> read/write permissions to the receiving app via <code>FLAG_GRANT_READ_URI_PERMISSION</code> or <code>FLAG_GRANT_WRITE_URI_PERMISSION</code>.</li>
          <li>The receiving app needs NO storage permissions — it just holds the URI token.</li>
          <li>The permission is automatically revoked when the receiving app's task stack is cleared or the grant expires.</li>
        </ol>
        <p>This makes FileProvider significantly more secure: you control exactly which files are shareable, access is time-limited, and the receiving app can't enumerate your filesystem.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q5</span>Your ContentProvider serves 1000 concurrent queries per second. It's becoming a bottleneck. How do you optimize it?</div>
      <div class="qa-answer">
        <p>ContentProvider is inherently concurrent (runs on a thread pool for remote access) but has overhead. Optimization strategies:</p>
        <ol>
          <li><strong>Batch operations:</strong> Use <code>ContentResolver.applyBatch()</code> with a list of <code>ContentProviderOperation</code> — executes in a single transaction instead of N separate cross-process calls.</li>
          <li><strong>Projection optimization:</strong> Never SELECT * — use minimal projections. Teach callers to specify exactly the columns they need.</li>
          <li><strong>Index your backing database:</strong> Add <code>@Index</code> annotations in Room for frequently queried columns.</li>
          <li><strong>Use bulkInsert():</strong> Override <code>bulkInsert()</code> to use a single Room transaction for batch inserts instead of N individual inserts.</li>
          <li><strong>Reconsider architecture:</strong> At 1000 QPS, ContentProvider's Binder IPC overhead is significant. If all callers are in the same process, consider bypassing ContentProvider and using Room directly via a shared Repository.</li>
        </ol>
        <pre class="code-block"><code class="language-kotlin">override fun bulkInsert(uri: Uri, values: Array&lt;ContentValues&gt;): Int {
    val db = database.writableDatabase
    db.beginTransaction()
    var count = 0
    try {
        values.forEach { cv ->
            db.insert("medications", null, cv)
            count++
        }
        db.setTransactionSuccessful()
    } finally {
        db.endTransaction()
    }
    context?.contentResolver?.notifyChange(uri, null)
    return count
}</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>How do you implement a ContentObserver to react to data changes from a ContentProvider in a ViewModel?</div>
      <div class="qa-answer">
        <pre class="code-block"><code class="language-kotlin">// ViewModel with ContentObserver and Flow
class MedicationsViewModel(application: Application) : AndroidViewModel(application) {

    private val contentResolver = application.contentResolver
    private val _medications = MutableStateFlow&lt;List&lt;Medication&gt;&gt;(emptyList())
    val medications: StateFlow&lt;List&lt;Medication&gt;&gt; = _medications.asStateFlow()

    private val observer = object : ContentObserver(Handler(Looper.getMainLooper())) {
        override fun onChange(selfChange: Boolean, uri: Uri?) {
            viewModelScope.launch { loadMedications() }
        }
    }

    init {
        // Register observer and load initial data
        contentResolver.registerContentObserver(
            Uri.parse("content://com.healthcare.app.medications/medications"),
            true,
            observer
        )
        viewModelScope.launch { loadMedications() }
    }

    private suspend fun loadMedications() {
        _medications.value = withContext(Dispatchers.IO) {
            contentResolver.query(
                Uri.parse("content://com.healthcare.app.medications/medications"),
                arrayOf("_id", "name", "dosage"), null, null, "name ASC"
            )?.use { cursor ->
                buildList {
                    while (cursor.moveToNext()) {
                        add(Medication.fromCursor(cursor))
                    }
                }
            } ?: emptyList()
        }
    }

    override fun onCleared() {
        // MUST unregister to prevent leak
        contentResolver.unregisterContentObserver(observer)
    }
}</code></pre>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge — Implement a Contacts Sync ContentProvider</h3>
    <p><strong>Problem:</strong> Implement a minimal ContentProvider that exposes a user contact list to other apps, supports CRUD, uses proper URI matching, MIME types, permission protection, and notifies ContentObservers on changes.</p>
    <pre class="code-block"><code class="language-kotlin">class ContactsProvider : ContentProvider() {

    companion object {
        const val AUTHORITY = "com.example.contacts"
        val BASE_URI: Uri = Uri.parse("content://$AUTHORITY")

        private const val CONTACTS_ALL = 1
        private const val CONTACT_ID = 2

        val CONTACTS_URI: Uri = BASE_URI.buildUpon().appendPath("contacts").build()

        private val matcher = UriMatcher(UriMatcher.NO_MATCH).apply {
            addURI(AUTHORITY, "contacts", CONTACTS_ALL)
            addURI(AUTHORITY, "contacts/#", CONTACT_ID)
        }

        private const val TABLE = "contacts"
        const val COL_ID = "_id"
        const val COL_NAME = "name"
        const val COL_PHONE = "phone"
        const val COL_EMAIL = "email"
    }

    private lateinit var dbHelper: ContactsDbHelper

    override fun onCreate(): Boolean {
        dbHelper = ContactsDbHelper(context!!)
        return true
    }

    override fun getType(uri: Uri): String = when (matcher.match(uri)) {
        CONTACTS_ALL -> "vnd.android.cursor.dir/vnd.$AUTHORITY.contacts"
        CONTACT_ID  -> "vnd.android.cursor.item/vnd.$AUTHORITY.contacts"
        else -> throw IllegalArgumentException("Unknown URI: $uri")
    }

    override fun query(
        uri: Uri, projection: Array&lt;String&gt;?, selection: String?,
        selectionArgs: Array&lt;String&gt;?, sortOrder: String?
    ): Cursor? {
        val db = dbHelper.readableDatabase
        val cursor = when (matcher.match(uri)) {
            CONTACTS_ALL -> db.query(TABLE, projection, selection, selectionArgs, null, null, sortOrder ?: "$COL_NAME ASC")
            CONTACT_ID -> {
                val id = ContentUris.parseId(uri)
                db.query(TABLE, projection, "$COL_ID = ?", arrayOf(id.toString()), null, null, null)
            }
            else -> throw IllegalArgumentException("Unknown URI: $uri")
        }
        cursor.setNotificationUri(context?.contentResolver, uri)
        return cursor
    }

    override fun insert(uri: Uri, values: ContentValues?): Uri? {
        if (matcher.match(uri) != CONTACTS_ALL) throw IllegalArgumentException("Invalid URI for insert: $uri")
        val id = dbHelper.writableDatabase.insertOrThrow(TABLE, null, values)
        context?.contentResolver?.notifyChange(uri, null)
        return ContentUris.withAppendedId(CONTACTS_URI, id)
    }

    override fun update(uri: Uri, values: ContentValues?, selection: String?, selectionArgs: Array&lt;String&gt;?): Int {
        val db = dbHelper.writableDatabase
        val count = when (matcher.match(uri)) {
            CONTACTS_ALL -> db.update(TABLE, values, selection, selectionArgs)
            CONTACT_ID -> {
                val id = ContentUris.parseId(uri)
                db.update(TABLE, values, "$COL_ID = ?", arrayOf(id.toString()))
            }
            else -> throw IllegalArgumentException("Unknown URI: $uri")
        }
        if (count > 0) context?.contentResolver?.notifyChange(uri, null)
        return count
    }

    override fun delete(uri: Uri, selection: String?, selectionArgs: Array&lt;String&gt;?): Int {
        val db = dbHelper.writableDatabase
        val count = when (matcher.match(uri)) {
            CONTACTS_ALL -> db.delete(TABLE, selection, selectionArgs)
            CONTACT_ID -> {
                val id = ContentUris.parseId(uri)
                db.delete(TABLE, "$COL_ID = ?", arrayOf(id.toString()))
            }
            else -> throw IllegalArgumentException("Unknown URI: $uri")
        }
        if (count > 0) context?.contentResolver?.notifyChange(uri, null)
        return count
    }
}

// SQLiteOpenHelper backing store
class ContactsDbHelper(context: Context) : SQLiteOpenHelper(context, "contacts.db", null, 1) {
    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL("""
            CREATE TABLE contacts (
                _id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT
            )
        """)
    }
    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        db.execSQL("DROP TABLE IF EXISTS contacts")
        onCreate(db)
    }
}

// Time: O(n) query, O(1) insert by ID, O(log n) with index
// Space: O(n) for result cursor
</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="25" data-item="0"> ✅ Understood ContentProvider CRUD &amp; URI matching</label>
    <label class="progress-check"><input type="checkbox" data-topic="25" data-item="1"> ✅ Know FileProvider &amp; secure file sharing</label>
    <label class="progress-check"><input type="checkbox" data-topic="25" data-item="2"> ✅ Know when to use ContentProvider vs Room</label>
    <label class="progress-check"><input type="checkbox" data-topic="25" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="25" data-item="4"> ✅ Solved Contacts Provider coding challenge</label>
  </div>
</section>

<!-- ========== TOPIC 26: Navigation Component & Deep Linking ========== -->
<section class="topic-section" id="topic-26">
  <div class="topic-header">
    <div class="topic-header-icon">🧭</div>
    <div class="topic-header-text">
      <h1>Navigation Component &amp; Deep Linking</h1>
      <p class="topic-tagline">Type-safe navigation, back stack management, and deep link handling for modern Android apps</p>
      <div class="category-badge-group">
        <span class="cat-pill">Navigation</span>
        <span class="cat-pill">Deep Links</span>
        <span class="cat-pill">Safe Args</span>
        <span class="cat-pill">Back Stack</span>
      </div>
    </div>
  </div>

  <div class="subtopic" id="subtopic-26-1">
    <h2>26.1 NavController, NavGraph &amp; Safe Args</h2>

    <div class="card card-why">
      <h3>❓ Why Do We Need Navigation Component?</h3>
      <p>Pre-Navigation Component, Android navigation was a fragmented mess: fragment transactions were error-prone (wrong back stack behavior, IllegalStateException after onSaveInstanceState), passing data between fragments required boilerplate Bundle code, deep links had to be manually handled in every Activity, and there was no single source of truth for the app's navigation graph.</p>
      <p>Navigation Component solves all of this: it provides a visual navigation graph, type-safe argument passing via Safe Args, automatic back stack management, deep link handling, and transitions — all with a single consistent API.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is Navigation Component?</h3>
      <p>The <strong>Jetpack Navigation Component</strong> consists of three key parts:</p>
      <ul>
        <li><strong>NavGraph:</strong> An XML resource that defines all destinations (fragments, activities, dialogs) and actions (transitions between destinations). The single source of truth for your app's navigation.</li>
        <li><strong>NavController:</strong> The runtime object that manages navigation within a NavHost. You navigate by calling <code>navController.navigate()</code>. Found via <code>findNavController()</code> or <code>NavHostFragment.findNavController(fragment)</code>.</li>
        <li><strong>NavHostFragment:</strong> An empty container in your Activity layout that hosts the current destination. It sets up the NavController and handles back press.</li>
        <li><strong>Safe Args:</strong> A Gradle plugin that generates type-safe Kotlin classes for passing arguments between destinations — eliminates Bundle key typos and type mismatches.</li>
      </ul>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does It Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// 1. build.gradle — Navigation dependencies
// implementation("androidx.navigation:navigation-fragment-ktx:2.7.7")
// implementation("androidx.navigation:navigation-ui-ktx:2.7.7")
// Safe Args plugin: id("androidx.navigation.safeargs.kotlin")

// 2. nav_graph.xml (res/navigation/)
// &lt;navigation xmlns:android="http://schemas.android.com/apk/res/android"
//     xmlns:app="http://schemas.android.com/apk/res-auto"
//     android:id="@+id/nav_graph"
//     app:startDestination="@id/homeFragment"&gt;
//
//     &lt;fragment android:id="@+id/homeFragment"
//         android:name="com.example.HomeFragment"&gt;
//         &lt;action android:id="@+id/action_home_to_detail"
//             app:destination="@id/detailFragment"
//             app:enterAnim="@anim/slide_in_right"
//             app:exitAnim="@anim/slide_out_left"
//             app:popEnterAnim="@anim/slide_in_left"
//             app:popExitAnim="@anim/slide_out_right" /&gt;
//     &lt;/fragment&gt;
//
//     &lt;fragment android:id="@+id/detailFragment"
//         android:name="com.example.DetailFragment"&gt;
//         &lt;argument android:name="productId"
//             app:argType="long"
//             android:defaultValue="-1" /&gt;
//         &lt;argument android:name="productName"
//             app:argType="string" /&gt;
//         &lt;deepLink app:uri="https://shop.example.com/product/{productId}" /&gt;
//     &lt;/fragment&gt;
//
//     &lt;dialog android:id="@+id/confirmDialog"
//         android:name="com.example.ConfirmDialogFragment"&gt;
//         &lt;argument android:name="message" app:argType="string" /&gt;
//     &lt;/dialog&gt;
// &lt;/navigation&gt;

// 3. Activity layout
// &lt;androidx.fragment.app.FragmentContainerView
//     android:id="@+id/nav_host_fragment"
//     android:name="androidx.navigation.fragment.NavHostFragment"
//     android:layout_width="match_parent"
//     android:layout_height="match_parent"
//     app:navGraph="@navigation/nav_graph"
//     app:defaultNavHost="true" /&gt;    &lt;!-- true = handles system back --&gt;

// 4. Navigate with Safe Args (type-safe!)
class HomeFragment : Fragment(R.layout.fragment_home) {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.productCard.setOnClickListener {
            // Safe Args generates HomeFragmentDirections
            val action = HomeFragmentDirections.actionHomeToDetail(
                productId = 42L,
                productName = "Premium Widget"
            )
            findNavController().navigate(action)
        }

        // Navigate to dialog
        binding.deleteBtn.setOnClickListener {
            findNavController().navigate(
                HomeFragmentDirections.actionHomeToConfirmDialog("Delete this item?")
            )
        }
    }
}

// 5. Receive args with Safe Args (type-safe!)
class DetailFragment : Fragment(R.layout.fragment_detail) {

    // Safe Args generates DetailFragmentArgs
    private val args: DetailFragmentArgs by navArgs()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // No bundle key strings! Compile-time type safety
        val productId: Long = args.productId
        val productName: String = args.productName
        viewModel.loadProduct(productId)
    }
}
</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs — Back Stack &amp; NavigationUI</h3>
      <pre class="code-block"><code class="language-kotlin">// Back stack manipulation
navController.navigate(R.id.detailFragment) // Simple navigate

// Pop back stack
navController.popBackStack()
navController.popBackStack(R.id.homeFragment, inclusive = false) // Pop up to homeFragment (keep it)
navController.navigateUp() // Like back but handles up navigation correctly

// Navigate with popUpTo — crucial for login flows
// Clear the entire back stack so user can't back into login
navController.navigate(
    R.id.action_login_to_home,
    NavOptions.Builder()
        .setPopUpTo(R.id.nav_graph, inclusive = true) // Pop to root, inclusive
        .build()
)

// Or in XML action:
// &lt;action app:destination="@id/homeFragment"
//         app:popUpTo="@id/nav_graph"
//         app:popUpToInclusive="true" /&gt;

// NavigationUI — connect to bottom nav / drawer / toolbar
class MainActivity : AppCompatActivity() {

    private lateinit var navController: NavController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        navController = navHostFragment.navController

        // Connect bottom navigation
        val bottomNav = findViewById&lt;BottomNavigationView&gt;(R.id.bottom_nav)
        bottomNav.setupWithNavController(navController)

        // Connect toolbar with up button
        val appBarConfig = AppBarConfiguration(
            setOf(R.id.homeFragment, R.id.searchFragment, R.id.profileFragment)
            // These are top-level destinations (no up button shown)
        )
        setupActionBarWithNavController(navController, appBarConfig)
    }

    override fun onSupportNavigateUp(): Boolean {
        return navController.navigateUp() || super.onSupportNavigateUp()
    }
}

// Nested graphs — encapsulate a sub-flow
// &lt;navigation android:id="@+id/nav_graph"&gt;
//     &lt;navigation android:id="@+id/auth_flow"
//         app:startDestination="@id/loginFragment"&gt;
//         &lt;fragment android:id="@+id/loginFragment" ... /&gt;
//         &lt;fragment android:id="@+id/registerFragment" ... /&gt;
//     &lt;/navigation&gt;
//     &lt;fragment android:id="@+id/homeFragment" ... /&gt;
// &lt;/navigation&gt;

// Navigate into a nested graph
navController.navigate(R.id.auth_flow)

// Fragment Result API — pass data back without shared ViewModel
// Sender (child) fragment:
setFragmentResult("confirmKey", bundleOf("confirmed" to true))

// Receiver (parent) fragment:
setFragmentResultListener("confirmKey") { _, bundle ->
    val confirmed = bundle.getBoolean("confirmed")
    if (confirmed) performDeletion()
}
</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World: E-Commerce — Deep Links &amp; Conditional Navigation</h3>
      <p>An e-commerce app needs to handle deep links from push notifications (go directly to a product detail page), handle authenticated vs unauthenticated states, and implement a checkout flow as a nested graph that can be completed and dismissed without affecting the main back stack.</p>
      <pre class="code-block"><code class="language-kotlin">// Deep link handling in AndroidManifest.xml (added via navGraph XML &lt;deepLink&gt; tag
// or manually):
// &lt;activity android:name=".MainActivity"&gt;
//     &lt;intent-filter&gt;
//         &lt;action android:name="android.intent.action.VIEW" /&gt;
//         &lt;category android:name="android.intent.category.DEFAULT" /&gt;
//         &lt;category android:name="android.intent.category.BROWSABLE" /&gt;
//         &lt;data android:scheme="https"
//               android:host="shop.example.com" /&gt;
//     &lt;/intent-filter&gt;
// &lt;/activity&gt;

// MainActivity handles deep links automatically via NavController
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        val navController = navHostFragment.navController

        // NavController automatically handles deep link intents
        // It builds the correct back stack (home -&gt; detail) even if launched cold

        // Handle new intents (app already running)
        // Handled by navController.handleDeepLink(intent) via onNewIntent
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        navHostFragment.navController.handleDeepLink(intent)
    }
}

// Conditional navigation — check auth state before allowing checkout
class CartFragment : Fragment() {

    private val authViewModel: AuthViewModel by activityViewModels()

    fun onCheckoutClicked() {
        if (authViewModel.isLoggedIn.value) {
            // Navigate into checkout nested graph
            findNavController().navigate(R.id.action_cart_to_checkout_flow)
        } else {
            // Navigate to auth flow, with a return destination
            val action = CartFragmentDirections.actionCartToAuthFlow()
            findNavController().navigate(action)
        }
    }
}

// Programmatic deep link construction (e.g., from a push notification)
fun navigateToProduct(context: Context, productId: Long) {
    val deepLinkUri = Uri.parse("https://shop.example.com/product/$productId")
    val pendingIntent = NavDeepLinkBuilder(context)
        .setComponentName(MainActivity::class.java)
        .setGraph(R.navigation.nav_graph)
        .setDestination(R.id.detailFragment)
        .setArguments(bundleOf("productId" to productId))
        .createPendingIntent()
    // Use in notification
    NotificationCompat.Builder(context, "push_channel")
        .setContentIntent(pendingIntent)
        .build()
}
</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Navigating after onSaveInstanceState (IllegalStateException):</strong> Navigating in an async callback after the fragment is stopped. ✅ Fix: Check <code>lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)</code> before navigating, or use <code>lifecycleScope.launch { }</code>.</li>
        <li>❌ <strong>Using fragment transactions directly alongside Navigation Component:</strong> Bypasses back stack management. ✅ Fix: Let NavController manage all navigation — never mix with direct fragment transactions.</li>
        <li>❌ <strong>Not using Safe Args for passing data:</strong> String-keyed Bundle arguments break at compile time only if you're lucky. ✅ Fix: Always use the Safe Args plugin for type-safe argument passing.</li>
        <li>❌ <strong>Double navigation on fast clicks:</strong> User taps button twice quickly, navigating to the destination twice. ✅ Fix: Check <code>navController.currentDestination?.id == R.id.sourceFragment</code> before navigating, or disable the button after first click.</li>
        <li>❌ <strong>Forgetting popUpTo for login flow:</strong> User can back-navigate into the login screen after authenticating. ✅ Fix: Use <code>popUpTo(navGraph.id, inclusive = true)</code> when navigating from login to home.</li>
        <li>❌ <strong>Finding NavController in onCreate before NavHostFragment is initialized:</strong> Returns null or throws. ✅ Fix: Find NavController after <code>setContentView()</code>, or use the NavHostFragment's <code>findNavController()</code> method.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"I use Navigation Component as the single source of truth for all navigation in my apps. The visual NavGraph makes it easy to onboard new developers and reason about user flows. Safe Args is non-negotiable — it catches argument type mismatches at compile time, not runtime. For login flows, the key insight is using popUpTo with inclusive=true when navigating to home, so the entire auth back stack is cleared. For deep links, I use NavDeepLinkBuilder to construct PendingIntents from push notifications — this correctly synthesizes the full back stack even if the app is launched cold. One gotcha I've hit in production: NavigateAfterOnSaveInstanceState crashes — I always check the lifecycle state before navigating from async callbacks. For sharing data between fragments, I prefer the Fragment Result API or a shared ViewModel over bundle arguments where possible."</p>
      </div>
    </div>
  </div>

  <!-- Q&A -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers — Navigation Component</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What are the three core components of Android Navigation Component?</div>
      <div class="qa-answer">
        <ol>
          <li><strong>NavGraph:</strong> An XML resource file (in res/navigation/) that defines all destinations and the actions connecting them. It's the "map" of your app's navigation. Destinations can be Fragments, Activities, dialog fragments, or custom destinations.</li>
          <li><strong>NavHostFragment:</strong> A special Fragment that acts as a container for the current navigation destination. It swap fragments in/out as navigation occurs. You place it in your Activity's layout with <code>app:navGraph</code> and <code>app:defaultNavHost="true"</code>.</li>
          <li><strong>NavController:</strong> The runtime object that performs navigation operations. Retrieved via <code>findNavController()</code>, <code>Navigation.findNavController(view)</code>, or from the NavHostFragment. You call <code>navigate()</code>, <code>popBackStack()</code>, and <code>navigateUp()</code> on it.</li>
        </ol>
      </div>
    </div>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q2</span>What is Safe Args and why should you use it over Bundle?</div>
      <div class="qa-answer">
        <p><strong>Safe Args</strong> is a Gradle plugin that generates Kotlin classes from your NavGraph argument definitions, providing type-safe navigation:</p>
        <ul>
          <li><strong>Type safety:</strong> Arguments are typed (Long, String, Parcelable, etc.) — wrong types are compile errors, not runtime crashes.</li>
          <li><strong>Null safety:</strong> Non-nullable args are guaranteed non-null; nullable args are explicitly marked.</li>
          <li><strong>No string keys:</strong> No risk of typos in Bundle keys — generated code handles the keys internally.</li>
          <li><strong>Default values:</strong> Declare default values in the nav graph; Safe Args respects them.</li>
        </ul>
        <pre class="code-block"><code class="language-kotlin">// Without Safe Args (error-prone):
val bundle = Bundle().apply { putLong("product_id", 42L) }
navController.navigate(R.id.detailFragment, bundle)
// In destination: val id = arguments?.getLong("product_id") ?: -1L  (could typo key)

// With Safe Args (type-safe):
val action = HomeFragmentDirections.actionHomeToDetail(productId = 42L, productName = "Widget")
navController.navigate(action)
// In destination:
val args: DetailFragmentArgs by navArgs()
val id: Long = args.productId  // Compile-time guaranteed Long</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>How do you handle the login flow with Navigation Component so users can't back into the login screen?</div>
      <div class="qa-answer">
        <p>Use <code>popUpTo</code> with <code>inclusive=true</code> when navigating from login to home to clear the entire auth back stack:</p>
        <pre class="code-block"><code class="language-kotlin">// After successful login:
navController.navigate(
    LoginFragmentDirections.actionLoginToHome(),
    NavOptions.Builder()
        .setPopUpTo(R.id.nav_graph, inclusive = true)  // Clear entire graph back stack
        .build()
)

// In XML:
// &lt;action android:id="@+id/action_login_to_home"
//         app:destination="@id/homeFragment"
//         app:popUpTo="@id/nav_graph"
//         app:popUpToInclusive="true" /&gt;</code></pre>
        <p>This works because <code>popUpTo="@id/nav_graph"</code> pops up to the root of the navigation graph, and <code>inclusive=true</code> pops the root itself. Then <code>homeFragment</code> becomes the new start of the back stack. Pressing back from home exits the app rather than going back to login.</p>
        <p><strong>Alternative:</strong> Use two separate NavGraphs — one for auth, one for main app — and navigate between graphs using <code>startActivity()</code> with <code>Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK</code>.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q4</span>How does NavDeepLinkBuilder differ from a regular deep link, and when do you use it?</div>
      <div class="qa-answer">
        <p><strong>Regular deep link</strong> (via Intent with URI): Used when an external entity (browser, another app) opens a deep link. Android dispatches the Intent to your Activity, and NavController handles it automatically, building the synthetic back stack defined by the nav graph.</p>
        <p><strong>NavDeepLinkBuilder</strong>: Used to programmatically create a <code>PendingIntent</code> that will navigate to a specific destination when activated. Primarily used for push notification actions where you need to navigate the user to a specific screen when they tap the notification.</p>
        <pre class="code-block"><code class="language-kotlin">// Use in push notification handling
fun createProductNotification(productId: Long): Notification {
    val pendingIntent = NavDeepLinkBuilder(context)
        .setComponentName(MainActivity::class.java)
        .setGraph(R.navigation.nav_graph)
        .setDestination(R.id.detailFragment)
        .setArguments(bundleOf("productId" to productId))
        .createPendingIntent()
    // NavDeepLinkBuilder builds the correct synthetic back stack:
    // home -&gt; detail, even if app is launched cold

    return NotificationCompat.Builder(context, "shop_channel")
        .setContentTitle("New Deal!")
        .setContentIntent(pendingIntent)
        .setAutoCancel(true)
        .build()
}</code></pre>
        <p>The key advantage: NavDeepLinkBuilder synthesizes the full back stack based on the nav graph's parent structure, so pressing back from the detail screen goes to home, not exits the app.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q5</span>Your app crashes with "IllegalStateException: Can not perform this action after onSaveInstanceState" during navigation. What causes this and how do you fix it?</div>
      <div class="qa-answer">
        <p>This happens when you try to navigate (which triggers a fragment transaction) after the Activity has saved its state — typically in an async callback (network response, coroutine, LiveData observer) that fires after the user presses home or the Activity pauses.</p>
        <p><strong>Root cause:</strong> Navigation Component internally uses FragmentTransactions, which cannot be committed after <code>onSaveInstanceState()</code>.</p>
        <p><strong>Fixes:</strong></p>
        <ol>
          <li><strong>Use Lifecycle-aware coroutines:</strong> Use <code>lifecycleScope.launch</code> which automatically cancels when the lifecycle is destroyed. Or use <code>repeatOnLifecycle(Lifecycle.State.STARTED)</code> to only collect while active.</li>
          <li><strong>Check lifecycle state before navigating:</strong></li>
        </ol>
        <pre class="code-block"><code class="language-kotlin">// Safe navigation helper
fun Fragment.safeNavigate(directions: NavDirections) {
    if (lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) {
        findNavController().navigate(directions)
    }
}

// Preferred: collect flows with repeatOnLifecycle
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.navigationEvent.collect { event ->
            // Safe — only collects when STARTED, auto-cancelled when STOPPED
            findNavController().navigate(event.direction)
        }
    }
}</code></pre>
        <p>The <code>repeatOnLifecycle(STARTED)</code> pattern is the gold standard — it suspends collection when the app is backgrounded and resumes when it comes back.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>How do you pass data back from a destination to its previous destination in Navigation Component?</div>
      <div class="qa-answer">
        <p>Three approaches, in order of preference:</p>
        <p><strong>1. Fragment Result API (simplest, for direct parent-child):</strong></p>
        <pre class="code-block"><code class="language-kotlin">// In child fragment (sending result back):
setFragmentResult("requestKey", bundleOf("selectedItem" to itemId))
findNavController().popBackStack()

// In parent fragment (listening for result):
setFragmentResultListener("requestKey") { _, bundle ->
    val selectedItem = bundle.getLong("selectedItem")
    handleSelection(selectedItem)
}</code></pre>
        <p><strong>2. Shared ViewModel (for multi-fragment communication in same graph):</strong></p>
        <pre class="code-block"><code class="language-kotlin">// Both fragments share ViewModel scoped to the NavBackStackEntry
val sharedViewModel: SharedViewModel by navGraphViewModels(R.id.checkout_flow)
// or: by activityViewModels() for app-wide shared state</code></pre>
        <p><strong>3. Saved State Handle on back stack entry (Navigation-scoped):</strong></p>
        <pre class="code-block"><code class="language-kotlin">// In parent — observe a key on the previous back stack entry
navController.currentBackStackEntry?.savedStateHandle
    ?.getLiveData&lt;Long&gt;("selectedId")
    ?.observe(viewLifecycleOwner) { id -> handleSelection(id) }

// In child — set the value before popping
navController.previousBackStackEntry?.savedStateHandle?.set("selectedId", selectedId)
navController.popBackStack()</code></pre>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge — Safe Navigation Extension &amp; Back Stack Manager</h3>
    <p><strong>Problem:</strong> Implement a production-safe navigation system that prevents: (1) double-tap crashes, (2) navigation after onSaveInstanceState, (3) back navigation into the login screen after logout. Include a NavController extension function and a session-aware navigation graph switcher.</p>
    <pre class="code-block"><code class="language-kotlin">// 1. Safe navigation extension — prevents double tap and post-onSaveInstanceState crashes
fun NavController.safeNavigate(directions: NavDirections) {
    try {
        navigate(directions)
    } catch (e: IllegalArgumentException) {
        // Already navigated — current destination doesn't have this action
        Log.w("Navigation", "Ignoring duplicate navigation: ${e.message}")
    } catch (e: IllegalStateException) {
        Log.w("Navigation", "Navigation attempted after state save: ${e.message}")
    }
}

// Debounced navigation for button clicks
fun NavController.debouncedNavigate(directions: NavDirections) {
    if (currentBackStackEntry?.lifecycle?.currentState?.isAtLeast(Lifecycle.State.RESUMED) == true) {
        safeNavigate(directions)
    }
}

// 2. Session-aware navigation manager
class NavigationManager(
    private val navController: NavController,
    private val authRepository: AuthRepository
) {
    private val sessionScope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)

    fun observeSession() {
        sessionScope.launch {
            authRepository.sessionState.collect { session ->
                when (session) {
                    is SessionState.Authenticated -> navigateToMain()
                    is SessionState.Unauthenticated -> navigateToLogin()
                    is SessionState.Expired -> navigateToLoginWithMessage("Session expired")
                }
            }
        }
    }

    private fun navigateToMain() {
        if (navController.currentDestination?.id != R.id.homeFragment) {
            navController.navigate(
                R.id.action_global_home,
                null,
                NavOptions.Builder()
                    .setPopUpTo(R.id.nav_graph, inclusive = true)
                    .setLaunchSingleTop(true)
                    .build()
            )
        }
    }

    private fun navigateToLogin() {
        navController.navigate(
            R.id.action_global_login,
            null,
            NavOptions.Builder()
                .setPopUpTo(R.id.nav_graph, inclusive = true)
                .setLaunchSingleTop(true)
                .build()
        )
    }

    private fun navigateToLoginWithMessage(message: String) {
        val args = LoginFragmentArgs(errorMessage = message).toBundle()
        navController.navigate(
            R.id.action_global_login,
            args,
            NavOptions.Builder()
                .setPopUpTo(R.id.nav_graph, inclusive = true)
                .build()
        )
    }

    fun destroy() = sessionScope.cancel()
}

// 3. Deep link validator — verify deep links before navigation
object DeepLinkValidator {
    private val ALLOWED_HOSTS = setOf("shop.example.com", "app.example.com")
    private val PRODUCT_PATTERN = Regex("^/product/(\\d+)$")

    fun validateAndExtract(uri: Uri): DeepLinkResult {
        if (uri.host !in ALLOWED_HOSTS) return DeepLinkResult.Invalid("Unknown host")
        if (uri.scheme != "https") return DeepLinkResult.Invalid("Insecure scheme")

        return when {
            PRODUCT_PATTERN.matches(uri.path ?: "") -> {
                val productId = PRODUCT_PATTERN.find(uri.path!!)!!
                    .groupValues[1].toLong()
                DeepLinkResult.Product(productId)
            }
            else -> DeepLinkResult.Invalid("Unknown path: ${uri.path}")
        }
    }
}

sealed class DeepLinkResult {
    data class Product(val id: Long) : DeepLinkResult()
    data class Invalid(val reason: String) : DeepLinkResult()
}

// Usage in Activity:
fun handleIncomingIntent(intent: Intent) {
    val uri = intent.data ?: return
    when (val result = DeepLinkValidator.validateAndExtract(uri)) {
        is DeepLinkResult.Product -> {
            navController.safeNavigate(
                HomeFragmentDirections.actionHomeToDetail(result.id, "")
            )
        }
        is DeepLinkResult.Invalid -> Log.w("DeepLink", "Invalid: ${result.reason}")
    }
}
</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="26" data-item="0"> ✅ Understood NavController, NavGraph &amp; NavHostFragment</label>
    <label class="progress-check"><input type="checkbox" data-topic="26" data-item="1"> ✅ Can use Safe Args for type-safe navigation</label>
    <label class="progress-check"><input type="checkbox" data-topic="26" data-item="2"> ✅ Handle deep links &amp; login flow back stack</label>
    <label class="progress-check"><input type="checkbox" data-topic="26" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="26" data-item="4"> ✅ Solved Safe Navigation coding challenge</label>
  </div>
</section>

<!-- ========== TOPIC 27: Android Security ========== -->
<section class="topic-section" id="topic-27">
  <div class="topic-header">
    <div class="topic-header-icon">🔐</div>
    <div class="topic-header-text">
      <h1>Android Security</h1>
      <p class="topic-tagline">Keystore, biometrics, SSL pinning, encryption, and the full Android security model</p>
      <div class="category-badge-group">
        <span class="cat-pill">Keystore</span>
        <span class="cat-pill">Biometric</span>
        <span class="cat-pill">SSL Pinning</span>
        <span class="cat-pill">Encryption</span>
        <span class="cat-pill">Play Integrity</span>
      </div>
    </div>
  </div>

  <div class="subtopic" id="subtopic-27-1">
    <h2>27.1 Android Keystore, Biometric Authentication &amp; Data Encryption</h2>

    <div class="card card-why">
      <h3>❓ Why Does Security Matter on Android?</h3>
      <p>Android apps handle increasingly sensitive data: biometric credentials, financial information, health records, private messages. The platform provides powerful security primitives — but developers must use them correctly. A FinTech app that stores an AES key in SharedPreferences, or a Healthcare app that pins to a compromised certificate, or a banking app that doesn't detect rooted devices — each of these failures can lead to data breaches, regulatory fines, and loss of user trust.</p>
      <p>The Android Keystore system is the cornerstone: cryptographic keys never leave the secure hardware (TEE — Trusted Execution Environment) in plaintext. Combined with biometric authentication, certificate pinning, and integrity attestation, you can build a layered security model that's extremely difficult to compromise.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 What Is the Android Security Stack?</h3>
      <ul>
        <li><strong>Android Keystore System:</strong> A hardware-backed secure container for cryptographic keys. Keys generated in Keystore never leave the TEE/StrongBox in plaintext — even if the device is rooted. Supports AES, RSA, EC key operations.</li>
        <li><strong>BiometricPrompt:</strong> Unified biometric authentication API supporting fingerprint, face, and iris (API 28+). Can be tied to Keystore key operations — the key is only unlocked after biometric verification.</li>
        <li><strong>EncryptedSharedPreferences / EncryptedFile:</strong> AndroidX Security Crypto library — transparently encrypts SharedPreferences values and files using Keystore-backed keys.</li>
        <li><strong>SSL Pinning / Certificate Transparency:</strong> Validates TLS certificates against a pinned public key or certificate hash, preventing MITM attacks even with a compromised CA.</li>
        <li><strong>ProGuard / R8:</strong> Code shrinking, obfuscation, and optimization. Renames classes/methods to make reverse engineering harder.</li>
        <li><strong>Play Integrity API:</strong> Attests that the app is running on a genuine Android device, was installed from Play Store, and the app binary hasn't been tampered with.</li>
      </ul>
    </div>

    <div class="card card-how">
      <h3>🛠️ How Does Keystore + BiometricPrompt Work?</h3>
      <pre class="code-block"><code class="language-kotlin">// ===== ANDROID KEYSTORE — Hardware-backed key generation =====

class CryptoManager {

    companion object {
        private const val KEY_ALIAS = "biometric_key"
        private const val ANDROID_KEYSTORE = "AndroidKeyStore"
    }

    // Generate a hardware-backed AES key in Keystore
    // The key NEVER leaves the TEE in plaintext
    fun generateSecretKey(): SecretKey {
        val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE).also { it.load(null) }

        // Return existing key if already generated
        keyStore.getKey(KEY_ALIAS, null)?.let { return it as SecretKey }

        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            ANDROID_KEYSTORE
        )

        val spec = KeyGenParameterSpec.Builder(
            KEY_ALIAS,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        ).apply {
            setBlockModes(KeyProperties.BLOCK_MODE_CBC)
            setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_PKCS7)
            setKeySize(256)
            setUserAuthenticationRequired(true)           // Require biometric/PIN
            setUserAuthenticationParameters(
                0,  // 0 = require auth for every use
                KeyProperties.AUTH_BIOMETRIC_STRONG or KeyProperties.AUTH_DEVICE_CREDENTIAL
            )
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                setUnlockedDeviceRequired(true)           // Key only usable when device unlocked
                setIsStrongBoxBacked(true)                // Use dedicated security chip if available
            }
            setInvalidatedByBiometricEnrollment(true)    // Key revoked if biometrics change
        }.build()

        keyGenerator.init(spec)
        return keyGenerator.generateKey()
    }

    // Create a Cipher bound to the key — must unlock via BiometricPrompt before use
    fun getCipher(): Cipher = Cipher.getInstance(
        "${KeyProperties.KEY_ALGORITHM_AES}/${KeyProperties.BLOCK_MODE_CBC}/${KeyProperties.ENCRYPTION_PADDING_PKCS7}"
    )

    fun getEncryptCipher(secretKey: SecretKey): Cipher =
        getCipher().also { it.init(Cipher.ENCRYPT_MODE, secretKey) }

    fun getDecryptCipher(secretKey: SecretKey, iv: ByteArray): Cipher =
        getCipher().also { it.init(Cipher.DECRYPT_MODE, secretKey, IvParameterSpec(iv)) }

    fun encrypt(plaintext: ByteArray, cipher: Cipher): Pair&lt;ByteArray, ByteArray&gt; {
        val encrypted = cipher.doFinal(plaintext)
        return Pair(encrypted, cipher.iv)
    }

    fun decrypt(ciphertext: ByteArray, cipher: Cipher): ByteArray =
        cipher.doFinal(ciphertext)
}

// ===== BIOMETRIC PROMPT with Keystore integration =====

class BiometricAuthManager(private val activity: FragmentActivity) {

    private val cryptoManager = CryptoManager()
    private var pendingCallback: ((Cipher) -> Unit)? = null

    fun authenticateAndEncrypt(
        data: ByteArray,
        onSuccess: (encryptedData: ByteArray, iv: ByteArray) -> Unit,
        onError: (String) -> Unit
    ) {
        val secretKey = cryptoManager.generateSecretKey()
        val cipher = cryptoManager.getEncryptCipher(secretKey)

        pendingCallback = { authenticatedCipher ->
            val (encrypted, iv) = cryptoManager.encrypt(data, authenticatedCipher)
            onSuccess(encrypted, iv)
        }

        showBiometricPrompt(cipher, onError)
    }

    fun authenticateAndDecrypt(
        encryptedData: ByteArray,
        iv: ByteArray,
        onSuccess: (ByteArray) -> Unit,
        onError: (String) -> Unit
    ) {
        val secretKey = cryptoManager.generateSecretKey()
        val cipher = cryptoManager.getDecryptCipher(secretKey, iv)

        pendingCallback = { authenticatedCipher ->
            val decrypted = cryptoManager.decrypt(encryptedData, authenticatedCipher)
            onSuccess(decrypted)
        }

        showBiometricPrompt(cipher, onError)
    }

    private fun showBiometricPrompt(cipher: Cipher, onError: (String) -> Unit) {
        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Authenticate")
            .setSubtitle("Use your biometric to access secure data")
            .setAllowedAuthenticators(
                BiometricManager.Authenticators.BIOMETRIC_STRONG or
                BiometricManager.Authenticators.DEVICE_CREDENTIAL
            )
            .build()

        val biometricPrompt = BiometricPrompt(
            activity,
            ContextCompat.getMainExecutor(activity),
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    result.cryptoObject?.cipher?.let { authenticatedCipher ->
                        pendingCallback?.invoke(authenticatedCipher)
                        pendingCallback = null
                    }
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    onError("Auth error [$errorCode]: $errString")
                    pendingCallback = null
                }

                override fun onAuthenticationFailed() {
                    // Biometric not recognized — prompt stays open, do nothing here
                }
            }
        )

        biometricPrompt.authenticate(
            promptInfo,
            BiometricPrompt.CryptoObject(cipher)
        )
    }
}

// ===== ENCRYPTED SHARED PREFERENCES (simpler alternative) =====

class SecurePreferences(context: Context) {

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)  // Uses Keystore internally
        .build()

    private val sharedPreferences = EncryptedSharedPreferences.create(
        context,
        "secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,    // Key encryption
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM   // Value encryption
    )

    fun saveToken(token: String) {
        sharedPreferences.edit().putString("auth_token", token).apply()
    }

    fun getToken(): String? = sharedPreferences.getString("auth_token", null)

    fun clearToken() {
        sharedPreferences.edit().remove("auth_token").apply()
    }
}
</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Syntax &amp; Key APIs — SSL Pinning &amp; Play Integrity</h3>
      <pre class="code-block"><code class="language-kotlin">// ===== SSL CERTIFICATE PINNING with OkHttp =====

fun createSecureOkHttpClient(): OkHttpClient {
    // Get SHA-256 hash of your server's public key:
    // openssl s_client -connect api.example.com:443 | openssl x509 -pubkey -noout |
    //   openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | base64

    val certificatePinner = CertificatePinner.Builder()
        .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
        .add("api.example.com", "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=") // Backup pin
        .build()

    return OkHttpClient.Builder()
        .certificatePinner(certificatePinner)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()
}

// Alternative: Network Security Config (no code — XML only)
// res/xml/network_security_config.xml:
// &lt;network-security-config&gt;
//     &lt;domain-config cleartextTrafficPermitted="false"&gt;
//         &lt;domain includeSubdomains="true"&gt;api.example.com&lt;/domain&gt;
//         &lt;pin-set expiration="2025-12-01"&gt;
//             &lt;pin digest="SHA-256"&gt;AAAA...&lt;/pin&gt;
//             &lt;pin digest="SHA-256"&gt;BBBB...&lt;/pin&gt;
//         &lt;/pin-set&gt;
//     &lt;/domain-config&gt;
// &lt;/network-security-config&gt;
// AndroidManifest: android:networkSecurityConfig="@xml/network_security_config"

// ===== PLAY INTEGRITY API =====

class IntegrityChecker(private val context: Context) {

    private val integrityManager = IntegrityManagerFactory.create(context)

    suspend fun checkAppIntegrity(): IntegrityVerdict {
        return withContext(Dispatchers.IO) {
            val nonce = generateNonce() // Fresh nonce per check, tied to operation

            val tokenTask = integrityManager.requestIntegrityToken(
                IntegrityTokenRequest.builder()
                    .setNonce(nonce)
                    .build()
            )

            val token = Tasks.await(tokenTask).token()

            // Send token to YOUR backend for decryption and verification
            // Your backend calls Google's API to decrypt the verdict
            apiService.verifyIntegrity(token, nonce)
        }
    }

    private fun generateNonce(): String {
        val bytes = ByteArray(32)
        java.security.SecureRandom().nextBytes(bytes)
        return Base64.encodeToString(bytes, Base64.URL_SAFE or Base64.NO_WRAP)
    }
}

// Backend receives the token and decodes the verdict:
// {
//   "requestDetails": { "requestPackageName": "com.example.app", "nonce": "..." },
//   "appIntegrity": { "appRecognitionVerdict": "PLAY_RECOGNIZED" },
//   "deviceIntegrity": { "deviceRecognitionVerdict": ["MEETS_STRONG_INTEGRITY"] },
//   "accountDetails": { "appLicensingVerdict": "LICENSED" }
// }

// ===== BIOMETRIC AVAILABILITY CHECK =====

fun checkBiometricAvailability(context: Context): BiometricStatus {
    val biometricManager = BiometricManager.from(context)
    return when (biometricManager.canAuthenticate(
        BiometricManager.Authenticators.BIOMETRIC_STRONG
    )) {
        BiometricManager.BIOMETRIC_SUCCESS -> BiometricStatus.Available
        BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE -> BiometricStatus.NoHardware
        BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE -> BiometricStatus.HardwareUnavailable
        BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> BiometricStatus.NoneEnrolled
        else -> BiometricStatus.Unknown
    }
}

enum class BiometricStatus { Available, NoHardware, HardwareUnavailable, NoneEnrolled, Unknown }
</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World: FinTech — Multi-Layer Security for a Banking App</h3>
      <p>A banking app requires: hardware-backed key storage for session tokens, biometric authentication for high-value transactions, SSL pinning to prevent MITM, Play Integrity check before allowing transfers, and ProGuard configuration to obfuscate sensitive business logic.</p>
      <pre class="code-block"><code class="language-kotlin">// Complete security stack for a banking transaction flow

class BankingSecurityManager(private val activity: FragmentActivity) {

    private val cryptoManager = CryptoManager()
    private val biometricManager = BiometricAuthManager(activity)
    private val integrityChecker = IntegrityChecker(activity)
    private val securePrefs = SecurePreferences(activity)

    suspend fun initiateSecureTransfer(
        amount: Double,
        recipientId: String,
        onApproved: () -> Unit,
        onRejected: (String) -> Unit
    ) {
        // 1. Check device integrity first
        val verdict = try {
            integrityChecker.checkAppIntegrity()
        } catch (e: Exception) {
            onRejected("Device integrity check failed")
            return
        }

        if (!verdict.deviceMeetsStrongIntegrity) {
            onRejected("This device doesn't meet security requirements")
            return
        }

        // 2. Require biometric for amounts over $100
        if (amount > 100.0) {
            val transactionData = "$amount:$recipientId:${System.currentTimeMillis()}".toByteArray()

            biometricManager.authenticateAndEncrypt(
                transactionData,
                onSuccess = { encryptedData, iv ->
                    // 3. Sign the transaction with encrypted payload
                    processSignedTransfer(encryptedData, iv, amount, recipientId, onApproved, onRejected)
                },
                onError = { error ->
                    onRejected("Biometric authentication failed: $error")
                }
            )
        } else {
            // Low-value: just verify session token
            val token = securePrefs.getToken() ?: run {
                onRejected("Session expired")
                return
            }
            onApproved()
        }
    }

    private fun processSignedTransfer(
        encryptedData: ByteArray,
        iv: ByteArray,
        amount: Double,
        recipientId: String,
        onApproved: () -> Unit,
        onRejected: (String) -> Unit
    ) {
        // 4. Use pinned OkHttp client to call backend
        val client = createSecureOkHttpClient()
        // ... POST signed transaction to backend
        // Backend verifies: PIN cert, session token, Play Integrity verdict, biometric proof
        onApproved()
    }
}

// ProGuard rules for sensitive classes (proguard-rules.pro):
// -keep class com.example.banking.model.** { *; }   # Keep API models for Gson/Retrofit
// -keepnames class com.example.banking.crypto.** { *; }  # Obfuscate but keep names for debugging
// -dontskipnonpubliclibraryclasses
// -optimizations !code/simplification/arithmetic,!field/*,!class/merging/*

// R8 full mode (build.gradle):
// android {
//     buildTypes {
//         release {
//             minifyEnabled true
//             shrinkResources true
//             proguardFiles getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro"
//         }
//     }
// }
</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Storing secrets in SharedPreferences or assets:</strong> Readable by root or backup tools. ✅ Fix: Use EncryptedSharedPreferences or Android Keystore for all sensitive data.</li>
        <li>❌ <strong>Hardcoding API keys in source code:</strong> Easily extracted from APK with dextools. ✅ Fix: Store in Keystore, fetch from server at runtime, or use Android secrets-gradle-plugin to inject at build time.</li>
        <li>❌ <strong>SSL pinning without a backup pin:</strong> If your certificate rotates, your app is broken for all users. ✅ Fix: Always pin at least 2 certificates — current and next/backup.</li>
        <li>❌ <strong>Not handling biometric enrollment changes:</strong> If the user adds/removes a fingerprint, Keystore keys with <code>setInvalidatedByBiometricEnrollment(true)</code> are deleted. ✅ Fix: Catch <code>KeyPermanentlyInvalidatedException</code> and re-generate the key, re-prompting user for auth.</li>
        <li>❌ <strong>Verifying Play Integrity verdict client-side:</strong> The token can be replayed or tampered with if verified locally. ✅ Fix: Always send the token to your backend for decryption and verification.</li>
        <li>❌ <strong>Using BiometricPrompt without a CryptoObject:</strong> "Weak" biometric auth — doesn't actually protect Keystore operations. ✅ Fix: Always use <code>BiometricPrompt.CryptoObject(cipher)</code> to tie the biometric verification to a key operation.</li>
        <li>❌ <strong>Disabling certificate validation in debug builds:</strong> If shipped in release by accident, catastrophic. ✅ Fix: Use Network Security Config XML to allow debug certs only in debug builds.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Android security is a layered discipline. At the hardware layer, I use Android Keystore with StrongBox backing where available — keys generated there physically cannot be extracted, even on a rooted device. For user authentication, I tie Keystore operations to BiometricPrompt using a CryptoObject — this means the cipher is only unlocked after genuine biometric verification, not just a boolean flag. For network security, I use OkHttp's CertificatePinner with at least two pinned SHA-256 public key hashes — always a backup pin to handle cert rotation without a forced update. For data at rest, EncryptedSharedPreferences handles the Keystore integration transparently. For anti-tampering, I integrate Play Integrity API for high-risk operations like financial transfers — the verdict is verified server-side, never client-side. And I use R8 with full mode obfuscation in release builds, combined with DexGuard for additional protection of payment logic."</p>
      </div>
    </div>
  </div>

  <!-- Subtopic 27-2 -->
  <div class="subtopic" id="subtopic-27-2">
    <h2>27.2 Android Permission Model &amp; Security Best Practices</h2>

    <div class="card card-why">
      <h3>❓ Why Is the Permission Model Critical?</h3>
      <p>Android's permission model is the gatekeeper between apps and sensitive device resources. Misusing permissions — requesting too many, not handling denials gracefully, not handling "don't ask again", or not checking permissions at runtime — leads to bad UX, Play Store rejections, and potential security vulnerabilities if sensitive operations are performed without proper checks.</p>
    </div>

    <div class="card card-what">
      <h3>🔷 Android Permission Types</h3>
      <ul>
        <li><strong>Normal permissions:</strong> Auto-granted at install (e.g., INTERNET, VIBRATE). No runtime prompt.</li>
        <li><strong>Dangerous permissions:</strong> Require explicit user approval at runtime (e.g., CAMERA, LOCATION, READ_CONTACTS). Grouped — granting one may auto-grant others in the same group (varies by Android version).</li>
        <li><strong>Signature permissions:</strong> Granted only to apps signed with the same certificate. Used for IPC protection.</li>
        <li><strong>AppOp permissions (Android 10+):</strong> Background location, package usage stats — special category with stricter user controls.</li>
        <li><strong>One-time permissions (Android 11+):</strong> Location, camera, microphone can be granted "only this time" — revoked when app goes to background.</li>
        <li><strong>Photo Picker / Partial access (Android 13+):</strong> READ_MEDIA_IMAGES/VIDEO/AUDIO replaces READ_EXTERNAL_STORAGE. Android 14 adds partial photo access.</li>
      </ul>
    </div>

    <div class="card card-how">
      <h3>🛠️ Production Permission Handling</h3>
      <pre class="code-block"><code class="language-kotlin">class CameraFragment : Fragment() {

    private val requestCameraPermission = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        when {
            isGranted -> initializeCamera()
            shouldShowRequestPermissionRationale(Manifest.permission.CAMERA) -> {
                // User denied but didn't check "Don't ask again"
                // Show rationale UI explaining WHY camera is needed
                showCameraRationaleDialog()
            }
            else -> {
                // User checked "Don't ask again" — must direct to Settings
                showPermissionPermanentlyDeniedDialog()
            }
        }
    }

    private fun checkAndRequestCamera() {
        when {
            ContextCompat.checkSelfPermission(
                requireContext(), Manifest.permission.CAMERA
            ) == PackageManager.PERMISSION_GRANTED -> {
                initializeCamera()
            }
            shouldShowRequestPermissionRationale(Manifest.permission.CAMERA) -> {
                // Show rationale BEFORE requesting
                showCameraRationaleDialog()
            }
            else -> {
                requestCameraPermission.launch(Manifest.permission.CAMERA)
            }
        }
    }

    private fun showCameraRationaleDialog() {
        MaterialAlertDialogBuilder(requireContext())
            .setTitle("Camera Access Required")
            .setMessage("We need camera access to scan product barcodes. No photos are stored.")
            .setPositiveButton("Grant Access") { _, _ ->
                requestCameraPermission.launch(Manifest.permission.CAMERA)
            }
            .setNegativeButton("Not Now", null)
            .show()
    }

    private fun showPermissionPermanentlyDeniedDialog() {
        MaterialAlertDialogBuilder(requireContext())
            .setTitle("Camera Access Denied")
            .setMessage("Enable camera access in Settings to use this feature.")
            .setPositiveButton("Open Settings") { _, _ ->
                // Open app settings
                Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                    data = Uri.fromParts("package", requireContext().packageName, null)
                    startActivity(this)
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    // Multiple permissions at once
    private val requestMultiplePermissions = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val cameraGranted = permissions[Manifest.permission.CAMERA] ?: false
        val audioGranted = permissions[Manifest.permission.RECORD_AUDIO] ?: false

        if (cameraGranted &amp;&amp; audioGranted) {
            startVideoRecording()
        } else {
            handlePermissionDenials(cameraGranted, audioGranted)
        }
    }
}
</code></pre>
    </div>

    <div class="card card-syntax">
      <h3>📝 Key Security APIs &amp; Patterns</h3>
      <pre class="code-block"><code class="language-kotlin">// ===== KEYSTORE: RSA asymmetric key for signing =====
fun generateRSAKeyPair(): KeyPair {
    val kpg = KeyPairGenerator.getInstance(
        KeyProperties.KEY_ALGORITHM_EC, "AndroidKeyStore"
    )
    kpg.initialize(
        KeyGenParameterSpec.Builder(
            "signing_key",
            KeyProperties.PURPOSE_SIGN or KeyProperties.PURPOSE_VERIFY
        ).apply {
            setDigests(KeyProperties.DIGEST_SHA256, KeyProperties.DIGEST_SHA512)
            setAlgorithmParameterSpec(ECGenParameterSpec("secp256r1"))
            setUserAuthenticationRequired(true)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                setIsStrongBoxBacked(true)
            }
        }.build()
    )
    return kpg.generateKeyPair()
}

// ===== DETECT ROOTED DEVICES =====
object RootDetector {
    fun isRooted(): Boolean {
        return checkSuperuserApk() || checkBuildTags() || checkSuBinary()
    }

    private fun checkSuperuserApk(): Boolean {
        return try {
            File("/system/app/Superuser.apk").exists() ||
            File("/system/xbin/daemonsu").exists()
        } catch (e: Exception) { false }
    }

    private fun checkBuildTags(): Boolean {
        val buildTags = Build.TAGS
        return buildTags != null &amp;&amp; buildTags.contains("test-keys")
    }

    private fun checkSuBinary(): Boolean {
        val suPaths = arrayOf(
            "/system/bin/su", "/system/xbin/su",
            "/sbin/su", "/system/su", "/vendor/bin/su"
        )
        return suPaths.any { File(it).exists() }
    }
}

// ===== SECURE RANDOM for token generation =====
fun generateSecureToken(length: Int = 32): String {
    val bytes = ByteArray(length)
    java.security.SecureRandom().nextBytes(bytes)
    return Base64.encodeToString(bytes, Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP)
}

// ===== ENCRYPTED FILE using Security Crypto =====
fun writeEncryptedFile(context: Context, filename: String, data: ByteArray) {
    val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    val encryptedFile = EncryptedFile.Builder(
        context,
        File(context.filesDir, filename),
        masterKey,
        EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
    ).build()

    encryptedFile.openFileOutput().use { output ->
        output.write(data)
    }
}

// ===== CERTIFICATE TRANSPARENCY check =====
// Using OkHttp + Conscrypt for certificate transparency
fun createCertTransparencyClient(): OkHttpClient {
    return OkHttpClient.Builder()
        .sslSocketFactory(
            // Conscrypt provides modern TLS
            Conscrypt.newSslSocketFactory(),
            Conscrypt.getDefaultX509TrustManager()
        )
        .hostnameVerifier { hostname, session ->
            HttpsURLConnection.getDefaultHostnameVerifier().verify(hostname, session)
        }
        .build()
}
</code></pre>
    </div>

    <div class="card card-realworld">
      <h3>🏭 Real-World: Healthcare — HIPAA-Compliant Data Storage</h3>
      <p>A healthcare app storing PHI (Protected Health Information) must meet HIPAA requirements: encrypted storage, biometric access control, audit logging, and certificate pinning for API calls to the EHR system.</p>
      <pre class="code-block"><code class="language-kotlin">class HipaaCompliantStorage(private val context: Context) {

    private val masterKey by lazy {
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .setUserAuthenticationRequired(true, 300) // Require auth every 5 minutes
            .build()
    }

    private val encryptedPrefs by lazy {
        EncryptedSharedPreferences.create(
            context, "phi_prefs", masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }

    fun storePatientData(patientId: String, data: PatientRecord) {
        // Encrypt with key that requires biometric
        val json = Gson().toJson(data)
        encryptedPrefs.edit()
            .putString("patient_$patientId", json)
            .apply()

        // Audit log
        AuditLogger.log(AuditEvent.DataWrite(patientId, System.currentTimeMillis()))
    }

    fun retrievePatientData(patientId: String): PatientRecord? {
        val json = encryptedPrefs.getString("patient_$patientId", null) ?: return null
        AuditLogger.log(AuditEvent.DataRead(patientId, System.currentTimeMillis()))
        return Gson().fromJson(json, PatientRecord::class.java)
    }

    fun wipeAllData() {
        // HIPAA: must be able to remote wipe
        encryptedPrefs.edit().clear().apply()
        context.deleteSharedPreferences("phi_prefs")
        // Also delete Keystore key to make old backups unrecoverable
        KeyStore.getInstance("AndroidKeyStore").apply {
            load(null)
            deleteEntry("_androidx_security_master_key")
        }
        AuditLogger.log(AuditEvent.DataWipe(System.currentTimeMillis()))
    }
}
</code></pre>
    </div>

    <div class="card card-mistakes">
      <h3>⚠️ Common Mistakes &amp; Gotchas</h3>
      <ul>
        <li>❌ <strong>Requesting permissions in onCreate() immediately:</strong> No context for the user. ✅ Fix: Request permissions only when the feature is actually needed, with rationale if appropriate.</li>
        <li>❌ <strong>Not handling "never ask again" state:</strong> Your request silently fails and the user is confused. ✅ Fix: After denial, check <code>shouldShowRequestPermissionRationale()</code>. If false after denial, direct to Settings.</li>
        <li>❌ <strong>Using Math.random() or Random() for security tokens:</strong> Predictable seeds. ✅ Fix: Always use <code>java.security.SecureRandom</code> for cryptographic randomness.</li>
        <li>❌ <strong>Logging sensitive data:</strong> Firebase Crashlytics, Logcat, and third-party SDKs can capture logs. ✅ Fix: Never log tokens, passwords, PHI, PII. Use BuildConfig.DEBUG guard for any sensitive logging.</li>
        <li>❌ <strong>Storing API keys in strings.xml or BuildConfig:</strong> Extractable from APK. ✅ Fix: Fetch from a secure server after authentication, or use Android Keystore with remote key derivation.</li>
      </ul>
    </div>

    <div class="card card-presenter">
      <h3>🎤 Senior-Level Explanation</h3>
      <div class="senior-pitch">
        <p><strong>🎯 The Senior Pitch:</strong></p>
        <p>"Android security is defense in depth. At the permission layer, I follow the principle of least privilege — only request permissions when actually needed, with clear rationale. I handle all three permission states: granted, denied-with-rationale, and permanently denied. For data security, I use EncryptedSharedPreferences for small sensitive values and EncryptedFile for larger blobs — both backed by hardware Keystore keys. For network security, I combine OkHttp certificate pinning with Android's Network Security Config for defense against MITM attacks, and always include backup pins for smooth certificate rotations. For anti-fraud in FinTech and Healthcare, I integrate Play Integrity API for server-side attestation — the client never trusts itself, the server does the verification. I also do basic root detection as an additional signal, though I don't block rooted devices entirely since many power users legitimately root their devices."</p>
      </div>
    </div>
  </div>

  <!-- Q&A -->
  <div class="qa-section">
    <h2>🎯 Interview Questions &amp; Answers — Android Security</h2>
    <p class="qa-hint">👆 Click any card to reveal the answer</p>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q1</span>What is the Android Keystore system and what security guarantee does it provide?</div>
      <div class="qa-answer">
        <p>The <strong>Android Keystore system</strong> provides a hardware-backed container for cryptographic keys. Keys generated inside the Keystore never leave the <strong>TEE (Trusted Execution Environment)</strong> or StrongBox (dedicated security chip) in plaintext. Even a rooted device cannot extract the raw key material.</p>
        <p><strong>Key guarantees:</strong></p>
        <ul>
          <li><strong>Key non-extractability:</strong> You perform crypto operations WITH the key (sign, encrypt) but can never export the key bytes.</li>
          <li><strong>User authentication binding:</strong> Keys can require biometric/PIN verification before each use (<code>setUserAuthenticationRequired(true)</code>).</li>
          <li><strong>Key invalidation:</strong> Keys can be configured to be automatically deleted if biometrics change (<code>setInvalidatedByBiometricEnrollment(true)</code>).</li>
          <li><strong>StrongBox:</strong> On supported devices (API 28+), keys can be backed by a dedicated tamper-resistant security chip, providing even stronger guarantees.</li>
        </ul>
        <p>This means an attacker with full root access and a memory dump still cannot extract your encryption keys — they'd need to clone the hardware security chip.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="basic">
      <div class="qa-question"><span class="qa-number">Q2</span>What is SSL pinning and what attack does it prevent?</div>
      <div class="qa-answer">
        <p><strong>SSL Pinning</strong> validates that the server's TLS certificate (or its public key hash) matches a pre-defined "pinned" value in your app. It prevents <strong>Man-in-the-Middle (MITM) attacks</strong>.</p>
        <p><strong>The attack it prevents:</strong> Without pinning, an attacker who installs a custom CA certificate on the device (which is possible with corporate MDM, malware, or by the user) can intercept HTTPS traffic. Your app trusts the device's CA store, so it accepts the fraudulent certificate. With pinning, your app only trusts the specific certificate or public key you've pinned — even a trusted CA-signed cert won't work if it doesn't match your pin.</p>
        <p><strong>Two pinning approaches:</strong></p>
        <ul>
          <li><strong>Certificate pinning:</strong> Pin the full certificate. Most restrictive — breaks if the server cert is renewed.</li>
          <li><strong>Public key pinning (recommended):</strong> Pin the SHA-256 hash of the server's public key. Certificate can renew (same key pair) without breaking the pin. OkHttp uses this approach.</li>
        </ul>
        <p><strong>Critical: always pin at least 2 keys</strong> — primary and backup — to handle certificate rotation without forcing an app update.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q3</span>What is the Play Integrity API and how is it different from SafetyNet (deprecated)?</div>
      <div class="qa-answer">
        <p><strong>SafetyNet Attestation API</strong> (deprecated May 2024): Checked if the device meets Android Compatibility Definition. Provided a JWS response that had to be verified by your server. Had well-known bypass techniques (Magisk Hide, etc.).</p>
        <p><strong>Play Integrity API</strong> (replacement): Provides three verdicts in one token:</p>
        <ul>
          <li><strong>App Integrity:</strong> Was the app installed from Play Store? Has the APK been modified? (<code>PLAY_RECOGNIZED</code>, <code>UNRECOGNIZED_VERSION</code>, <code>UNEVALUATED</code>)</li>
          <li><strong>Device Integrity:</strong> Does the device meet Android security requirements? Is it rooted? (<code>MEETS_STRONG_INTEGRITY</code>, <code>MEETS_DEVICE_INTEGRITY</code>, <code>MEETS_BASIC_INTEGRITY</code>, <code>NO_INTEGRITY</code>)</li>
          <li><strong>Account Details:</strong> Is the user's Google account licensed to use the app? (<code>LICENSED</code>, <code>UNLICENSED</code>)</li>
        </ul>
        <p><strong>Key improvements over SafetyNet:</strong> More detailed verdicts, better bypass resistance, server-side decryption (token is encrypted — only Google and your backend can read it), and designed to work with Play-distributed apps.</p>
        <p><strong>Critical rule:</strong> The token MUST be decrypted and verified server-side. Never trust a client-side check.</p>
      </div>
    </div>

    <div class="qa-item" data-difficulty="advanced">
      <div class="qa-question"><span class="qa-number">Q4</span>Explain the difference between BiometricPrompt with and without CryptoObject. Why does it matter?</div>
      <div class="qa-answer">
        <p><strong>Without CryptoObject:</strong> The biometric prompt just verifies the user is present (boolean result). This is "Class 2" or "Weak" biometric authentication. The app receives a success callback, but nothing cryptographically ties that authentication to any subsequent operation. An attacker who can call the success callback directly (e.g., via instrumentation) bypasses security.</p>
        <p><strong>With CryptoObject:</strong> You initialize a Cipher (or Signature/MAC) with a Keystore key that has <code>setUserAuthenticationRequired(true)</code>. The Keystore key is NOT usable until biometric verification succeeds. BiometricPrompt wraps this Cipher in a CryptoObject. When authentication succeeds, the system "unlocks" the Cipher by allowing the Keystore to process operations with that key. The Cipher returned in <code>onAuthenticationSucceeded</code> is the same Cipher, now unlocked for one use.</p>
        <p><strong>Why it matters:</strong> With CryptoObject, even if an attacker calls your callback, they get a Cipher that's only usable post-biometric. The Keystore enforces this at the hardware level — there's no software way to bypass it. This is "Class 3" or "Strong" biometric auth required for financial transactions and health data.</p>
        <pre class="code-block"><code class="language-kotlin">// Wrong (weak):
biometricPrompt.authenticate(promptInfo)  // Just a boolean

// Correct (strong):
biometricPrompt.authenticate(promptInfo, BiometricPrompt.CryptoObject(cipher))
// cipher is only usable in onAuthenticationSucceeded</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q5</span>Your app's certificate pin expired and users are getting SSL errors. How do you design a system to prevent this from happening in production?</div>
      <div class="qa-answer">
        <p>This is a classic production incident. Prevention strategy:</p>
        <ol>
          <li><strong>Always pin at least 2 keys:</strong> Current certificate's public key + next certificate's public key (pre-generated before the current cert expires). When you rotate, you've already pinned the new key.</li>
          <li><strong>Use public key pinning, not certificate pinning:</strong> Public keys can stay the same across cert renewals (just renew the cert with the same key pair). The pin never expires.</li>
          <li><strong>Set expiration dates in Network Security Config:</strong> The XML pinset supports an <code>expiration</code> attribute — after this date, pinning is disabled (graceful degradation rather than hard failure).</li>
          <li><strong>Monitor pin expiry:</strong> Set up automated alerts when pinned certs are within 90 days of expiry.</li>
          <li><strong>Remote pin update mechanism:</strong> Fetch updated pins from a separate, non-pinned endpoint. Store in EncryptedSharedPreferences with a fallback to hardcoded pins.</li>
        </ol>
        <pre class="code-block"><code class="language-kotlin">// Two-pin defensive setup in OkHttp:
CertificatePinner.Builder()
    .add("api.example.com", "sha256/CURRENT_KEY_HASH=")
    .add("api.example.com", "sha256/NEXT_KEY_HASH=")  // Pre-generated backup
    .build()

// In Network Security Config:
// &lt;pin-set expiration="2026-01-01"&gt;  &lt;!-- Fallback after this date --&gt;
//     &lt;pin digest="SHA-256"&gt;CURRENT_HASH&lt;/pin&gt;
//     &lt;pin digest="SHA-256"&gt;NEXT_HASH&lt;/pin&gt;
// &lt;/pin-set&gt;</code></pre>
      </div>
    </div>

    <div class="qa-item" data-difficulty="scenario">
      <div class="qa-question"><span class="qa-number">Q6</span>A user updates their fingerprint enrollment after installing your app. Your encrypted data becomes inaccessible. How do you handle this gracefully?</div>
      <div class="qa-answer">
        <p>When you create a Keystore key with <code>setInvalidatedByBiometricEnrollment(true)</code>, the key is permanently deleted when the user adds or removes biometrics. Subsequent Cipher initialization with that key throws <code>KeyPermanentlyInvalidatedException</code>.</p>
        <p><strong>Graceful handling strategy:</strong></p>
        <pre class="code-block"><code class="language-kotlin">fun getCipherForDecryption(iv: ByteArray): Cipher? {
    return try {
        val key = keyStore.getKey(KEY_ALIAS, null) as? SecretKey
            ?: return null
        Cipher.getInstance(TRANSFORMATION).also {
            it.init(Cipher.DECRYPT_MODE, key, IvParameterSpec(iv))
        }
    } catch (e: KeyPermanentlyInvalidatedException) {
        // Key is gone — delete it and re-generate
        keyStore.deleteEntry(KEY_ALIAS)

        // Encrypted data is now unrecoverable — must inform user
        // and prompt them to re-authenticate via password to reset
        onBiometricKeyInvalidated()
        null
    } catch (e: UnrecoverableKeyException) {
        keyStore.deleteEntry(KEY_ALIAS)
        onBiometricKeyInvalidated()
        null
    }
}

fun onBiometricKeyInvalidated() {
    // Show dialog: "Your biometric credentials changed.
    // Please sign in with your password to restore access."
    // After password auth: re-encrypt data with new key
    // This forces re-enrollment rather than silently failing
}</code></pre>
        <p><strong>Alternative:</strong> Use <code>setInvalidatedByBiometricEnrollment(false)</code> if you want keys to survive biometric changes — but this is less secure, as a stolen device where an attacker adds their fingerprint could then unlock the key.</p>
      </div>
    </div>
  </div>

  <div class="card card-coding mt-4">
    <h3>💻 Coding Challenge — Implement a Complete Secure Storage Manager</h3>
    <p><strong>Problem:</strong> Implement a <code>SecureStorageManager</code> that: (1) stores sensitive data encrypted with a Keystore-backed key, (2) requires biometric authentication to read/write, (3) handles <code>KeyPermanentlyInvalidatedException</code> gracefully, (4) provides a fallback to device PIN/password, and (5) is testable with a mock injected crypto backend.</p>
    <pre class="code-block"><code class="language-kotlin">// Interface for testability
interface CryptoBackend {
    fun encrypt(data: ByteArray): EncryptedBlob
    fun decrypt(blob: EncryptedBlob): ByteArray
    fun isKeyValid(): Boolean
    fun resetKey()
}

data class EncryptedBlob(val ciphertext: ByteArray, val iv: ByteArray)

// Production implementation
class KeystoreCryptoBackend : CryptoBackend {
    private val keyStore = KeyStore.getInstance("AndroidKeyStore").also { it.load(null) }
    private val transformation = "AES/CBC/PKCS7Padding"
    private val keyAlias = "app_secure_key_v2"

    private fun getOrCreateKey(): SecretKey {
        (keyStore.getKey(keyAlias, null) as? SecretKey)?.let { return it }
        return KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore").apply {
            init(KeyGenParameterSpec.Builder(
                keyAlias,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
            ).apply {
                setBlockModes(KeyProperties.BLOCK_MODE_CBC)
                setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_PKCS7)
                setKeySize(256)
                setUserAuthenticationRequired(true)
                setUserAuthenticationParameters(0, KeyProperties.AUTH_BIOMETRIC_STRONG or KeyProperties.AUTH_DEVICE_CREDENTIAL)
                setInvalidatedByBiometricEnrollment(true)
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) setIsStrongBoxBacked(true)
            }.build())
        }.generateKey()
    }

    override fun isKeyValid(): Boolean = try {
        val key = keyStore.getKey(keyAlias, null) as? SecretKey ?: return false
        Cipher.getInstance(transformation).init(Cipher.ENCRYPT_MODE, key)
        true
    } catch (e: KeyPermanentlyInvalidatedException) { false }
    catch (e: Exception) { false }

    override fun resetKey() {
        try { keyStore.deleteEntry(keyAlias) } catch (e: Exception) { /* ignore */ }
    }

    override fun encrypt(data: ByteArray): EncryptedBlob {
        val cipher = Cipher.getInstance(transformation).also {
            it.init(Cipher.ENCRYPT_MODE, getOrCreateKey())
        }
        return EncryptedBlob(cipher.doFinal(data), cipher.iv)
    }

    override fun decrypt(blob: EncryptedBlob): ByteArray {
        val cipher = Cipher.getInstance(transformation).also {
            it.init(Cipher.DECRYPT_MODE, getOrCreateKey(), IvParameterSpec(blob.iv))
        }
        return cipher.doFinal(blob.ciphertext)
    }
}

// Manager class — testable, handles all edge cases
class SecureStorageManager(
    private val context: Context,
    private val crypto: CryptoBackend = KeystoreCryptoBackend(),
    private val activity: FragmentActivity
) {
    private val prefs = context.getSharedPreferences("secure_storage", Context.MODE_PRIVATE)

    fun store(key: String, value: String, onResult: (Result&lt;Unit&gt;) -> Unit) {
        if (!crypto.isKeyValid()) {
            crypto.resetKey()
            onResult(Result.failure(KeyInvalidatedException()))
            return
        }

        authenticateWithBiometric(
            purpose = "Store $key",
            onAuthenticated = {
                try {
                    val blob = crypto.encrypt(value.toByteArray(Charsets.UTF_8))
                    prefs.edit()
                        .putString("${key}_ct", Base64.encodeToString(blob.ciphertext, Base64.DEFAULT))
                        .putString("${key}_iv", Base64.encodeToString(blob.iv, Base64.DEFAULT))
                        .apply()
                    onResult(Result.success(Unit))
                } catch (e: Exception) {
                    onResult(Result.failure(e))
                }
            },
            onError = { onResult(Result.failure(SecurityException(it))) }
        )
    }

    fun retrieve(key: String, onResult: (Result&lt;String&gt;) -> Unit) {
        if (!crypto.isKeyValid()) {
            crypto.resetKey()
            onResult(Result.failure(KeyInvalidatedException()))
            return
        }

        val ciphertext = prefs.getString("${key}_ct", null)
            ?.let { Base64.decode(it, Base64.DEFAULT) }
            ?: run { onResult(Result.failure(NoSuchElementException(key))); return }

        val iv = prefs.getString("${key}_iv", null)
            ?.let { Base64.decode(it, Base64.DEFAULT) }
            ?: run { onResult(Result.failure(NoSuchElementException("iv for $key"))); return }

        authenticateWithBiometric(
            purpose = "Access $key",
            onAuthenticated = {
                try {
                    val plain = crypto.decrypt(EncryptedBlob(ciphertext, iv))
                    onResult(Result.success(plain.toString(Charsets.UTF_8)))
                } catch (e: Exception) {
                    onResult(Result.failure(e))
                }
            },
            onError = { onResult(Result.failure(SecurityException(it))) }
        )
    }

    private fun authenticateWithBiometric(
        purpose: String,
        onAuthenticated: () -> Unit,
        onError: (String) -> Unit
    ) {
        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Authentication Required")
            .setSubtitle(purpose)
            .setAllowedAuthenticators(
                BiometricManager.Authenticators.BIOMETRIC_STRONG or
                BiometricManager.Authenticators.DEVICE_CREDENTIAL
            )
            .build()

        BiometricPrompt(activity, ContextCompat.getMainExecutor(activity),
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    onAuthenticated()
                }
                override fun onAuthenticationError(code: Int, msg: CharSequence) {
                    onError("[$code] $msg")
                }
                override fun onAuthenticationFailed() { /* retry */ }
            }
        ).authenticate(promptInfo)
    }
}

class KeyInvalidatedException : Exception("Keystore key was invalidated due to biometric changes")

// Time: O(n) where n = data size for encrypt/decrypt (AES block cipher)
// Space: O(n) for the encrypted blob
// Security: Hardware-backed, biometric-bound, handles key invalidation gracefully
</code></pre>
  </div>

  <div class="topic-progress-tracker">
    <h3 style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.75rem;">📋 Track Your Progress</h3>
    <label class="progress-check"><input type="checkbox" data-topic="27" data-item="0"> ✅ Understood Android Keystore &amp; TEE guarantees</label>
    <label class="progress-check"><input type="checkbox" data-topic="27" data-item="1"> ✅ Can implement BiometricPrompt with CryptoObject</label>
    <label class="progress-check"><input type="checkbox" data-topic="27" data-item="2"> ✅ Know SSL Pinning, Play Integrity, &amp; permission model</label>
    <label class="progress-check"><input type="checkbox" data-topic="27" data-item="3"> ✅ Completed Interview Q&amp;As</label>
    <label class="progress-check"><input type="checkbox" data-topic="27" data-item="4"> ✅ Solved Secure Storage coding challenge</label>
  </div>
</section>
'''
