package com.titan.zapdial

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import kotlinx.coroutines.launch
import android.content.Intent
import android.os.Build
import android.telecom.Call
import android.telecom.CallAudioState
import android.telecom.InCallService
import androidx.core.app.NotificationCompat
import java.lang.ref.WeakReference

import android.content.BroadcastReceiver
import android.content.IntentFilter

class ZapCallService : InCallService() {

    private val CHANNEL_ID = "zapdial_ongoing_call"
    private val NOTIFICATION_ID = 12345
    private val callActionReceiver = CallActionReceiver()

    private val callCallback = object : Call.Callback() {
        override fun onStateChanged(call: Call, state: Int) {
            CallSessionManager.callState.value = state
            if (state == Call.STATE_DISCONNECTED) {
                CallSessionManager.activeCall.value = null
                cancelNotification()
            } else {
                updateNotification(call)
            }
        }
    }

    override fun onCreate() {
        super.onCreate()
        CallSessionManager.serviceRef = WeakReference(this)
        createNotificationChannel()
        
        val filter = IntentFilter().apply {
            addAction(CallActionReceiver.ACTION_TOGGLE_MUTE)
            addAction(CallActionReceiver.ACTION_END_CALL)
            addAction(CallActionReceiver.ACTION_ANSWER)
            addAction(CallActionReceiver.ACTION_SILENCE)
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            registerReceiver(callActionReceiver, filter, Context.RECEIVER_NOT_EXPORTED)
        } else {
            registerReceiver(callActionReceiver, filter)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        unregisterReceiver(callActionReceiver)
    }

    override fun onCallAdded(call: Call) {
        super.onCallAdded(call)
        CallSessionManager.allCalls.value = calls
        CallSessionManager.activeCall.value = call
        CallSessionManager.callState.value = call.state
        CallSessionManager.audioState.value = callAudioState
        CallSessionManager.isMuted.value = callAudioState?.isMuted ?: false
        
        call.registerCallback(callCallback)

        updateNotification(call)

        // Launch UI for incoming/outgoing call
        if (call.state == Call.STATE_RINGING || call.state == Call.STATE_DIALING || call.state == Call.STATE_CONNECTING || call.state == Call.STATE_ACTIVE) {
            val intent = Intent(this@ZapCallService, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_REORDER_TO_FRONT or Intent.FLAG_ACTIVITY_SINGLE_TOP
            }
            try { startActivity(intent) } catch (e: Exception) { android.widget.Toast.makeText(this@ZapCallService, "Action unavailable", android.widget.Toast.LENGTH_SHORT).show() }
        }
    }

    override fun onCallRemoved(call: Call) {
        super.onCallRemoved(call)
        CallSessionManager.allCalls.value = calls
        call.unregisterCallback(callCallback)
        CallSessionManager.activeCall.value = null
        CallSessionManager.callState.value = Call.STATE_DISCONNECTED
        cancelNotification()
    }

    override fun onCallAudioStateChanged(audioState: CallAudioState?) {
        super.onCallAudioStateChanged(audioState)
        CallSessionManager.audioState.value = audioState
        CallSessionManager.isMuted.value = audioState?.isMuted ?: false
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val name = "Ongoing Call"
            val descriptionText = "Displays active call status"
            val importance = NotificationManager.IMPORTANCE_HIGH
            val channel = NotificationChannel(CHANNEL_ID, name, importance).apply {
                description = descriptionText
            }
            val notificationManager: NotificationManager =
                getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }

    private fun updateNotification(call: Call) {
        val callerNumber = call.details?.handle?.schemeSpecificPart ?: "Unknown"
        val originalName = call.details?.callerDisplayName
        
        kotlinx.coroutines.GlobalScope.launch(kotlinx.coroutines.Dispatchers.IO) {
            val resolvedName = if (callerNumber != "Unknown") ContactFetcher.lookupContactName(this@ZapCallService, callerNumber) else null
            val callerName = resolvedName ?: originalName ?: callerNumber
        
        val intent = Intent(this@ZapCallService, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP
        }
        val pendingIntent = PendingIntent.getActivity(
            this@ZapCallService, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val notificationBuilder = NotificationCompat.Builder(this@ZapCallService, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.stat_sys_phone_call)
            .setContentTitle(callerName)
            .setContentText(callerNumber)
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_CALL)
            .setOngoing(true)
            .setContentIntent(pendingIntent)
            .setFullScreenIntent(pendingIntent, true)
            .setColorized(true)
            
        val isMuted = CallSessionManager.isMuted.value
        
        if (call.state == Call.STATE_RINGING) {
            notificationBuilder.setColor(android.graphics.Color.parseColor("#1A1424"))
            
            val declineIntent = Intent(CallActionReceiver.ACTION_END_CALL).apply { setPackage(packageName) }
            val declinePendingIntent = PendingIntent.getBroadcast(this@ZapCallService, 1, declineIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
            val declineAction = NotificationCompat.Action.Builder(android.R.drawable.ic_menu_close_clear_cancel, "Decline", declinePendingIntent).build()
            
            val answerIntent = Intent(CallActionReceiver.ACTION_ANSWER).apply { setPackage(packageName) }
            val answerPendingIntent = PendingIntent.getBroadcast(this@ZapCallService, 2, answerIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
            val answerAction = NotificationCompat.Action.Builder(android.R.drawable.stat_sys_phone_call, "Answer", answerPendingIntent).build()
            
            val silenceIntent = Intent(CallActionReceiver.ACTION_SILENCE).apply { setPackage(packageName) }
            val silencePendingIntent = PendingIntent.getBroadcast(this@ZapCallService, 3, silenceIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
            val silenceAction = NotificationCompat.Action.Builder(android.R.drawable.ic_lock_silent_mode_off, "Silence", silencePendingIntent).build()
            
            notificationBuilder.addAction(declineAction)
            notificationBuilder.addAction(answerAction)
            notificationBuilder.addAction(silenceAction)
            
        } else {
            notificationBuilder.setColor(android.graphics.Color.parseColor("#0F172A"))
            
            val muteIntent = Intent(CallActionReceiver.ACTION_TOGGLE_MUTE).apply { setPackage(packageName) }
            val mutePendingIntent = PendingIntent.getBroadcast(this@ZapCallService, 4, muteIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
            val muteIcon = if (isMuted) android.R.drawable.ic_lock_silent_mode_off else android.R.drawable.ic_btn_speak_now
            val muteLabel = if (isMuted) "Unmute" else "Mute"
            val muteAction = NotificationCompat.Action.Builder(muteIcon, muteLabel, mutePendingIntent).build()
            
            val endCallIntent = Intent(CallActionReceiver.ACTION_END_CALL).apply { setPackage(packageName) }
            val endCallPendingIntent = PendingIntent.getBroadcast(this@ZapCallService, 5, endCallIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
            val endCallAction = NotificationCompat.Action.Builder(android.R.drawable.ic_menu_close_clear_cancel, "End Call", endCallPendingIntent).build()
            
            notificationBuilder.addAction(muteAction)
            notificationBuilder.addAction(endCallAction)
            
            val connectTime = call.details?.connectTimeMillis ?: 0L
            if (call.state == Call.STATE_ACTIVE && connectTime > 0L) {
                notificationBuilder.setUsesChronometer(true)
                notificationBuilder.setWhen(connectTime)
            }
        }
        
        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        if (!CallSessionManager.isAppInForeground) {
            notificationManager.notify(NOTIFICATION_ID, notificationBuilder.build())
        }
        
        if (call.state == Call.STATE_RINGING) {
            val intent = Intent(this@ZapCallService, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_REORDER_TO_FRONT or Intent.FLAG_ACTIVITY_SINGLE_TOP
            }
            try { startActivity(intent) } catch (e: Exception) { android.widget.Toast.makeText(this@ZapCallService, "Action unavailable", android.widget.Toast.LENGTH_SHORT).show() }
        }
        }
    }

    private fun cancelNotification() {
        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.cancel(NOTIFICATION_ID)
    }
}
