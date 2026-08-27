with open('app/src/main/java/com/titan/zapdial/ZapCallService.kt', 'r') as f:
    content = f.read()

filters_old = """        val filter = IntentFilter().apply {
            addAction(CallActionReceiver.ACTION_TOGGLE_MUTE)
            addAction(CallActionReceiver.ACTION_END_CALL)
        }"""
filters_new = """        val filter = IntentFilter().apply {
            addAction(CallActionReceiver.ACTION_TOGGLE_MUTE)
            addAction(CallActionReceiver.ACTION_END_CALL)
            addAction(CallActionReceiver.ACTION_ANSWER)
            addAction(CallActionReceiver.ACTION_SILENCE)
        }"""
content = content.replace(filters_old, filters_new)

# Rebuild updateNotification function entirely
update_notif_old = """    private fun updateNotification(call: Call) {"""
import re
end_idx = content.find("    private fun cancelNotification() {")
before_update = content[:content.find("    private fun updateNotification(call: Call) {")]
after_update = content[end_idx:]

new_update_notif = """    private fun updateNotification(call: Call) {
        val callerNumber = call.details?.handle?.schemeSpecificPart ?: "Unknown"
        val callerName = call.details?.callerDisplayName ?: callerNumber
        
        val intent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP
        }
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val notificationBuilder = NotificationCompat.Builder(this, CHANNEL_ID)
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
            val declinePendingIntent = PendingIntent.getBroadcast(this, 1, declineIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
            val declineAction = NotificationCompat.Action.Builder(android.R.drawable.ic_menu_close_clear_cancel, "Decline", declinePendingIntent).build()
            
            val answerIntent = Intent(CallActionReceiver.ACTION_ANSWER).apply { setPackage(packageName) }
            val answerPendingIntent = PendingIntent.getBroadcast(this, 2, answerIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
            val answerAction = NotificationCompat.Action.Builder(android.R.drawable.stat_sys_phone_call, "Answer", answerPendingIntent).build()
            
            val silenceIntent = Intent(CallActionReceiver.ACTION_SILENCE).apply { setPackage(packageName) }
            val silencePendingIntent = PendingIntent.getBroadcast(this, 3, silenceIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
            val silenceAction = NotificationCompat.Action.Builder(android.R.drawable.ic_lock_silent_mode_off, "Silence", silencePendingIntent).build()
            
            notificationBuilder.addAction(declineAction)
            notificationBuilder.addAction(answerAction)
            notificationBuilder.addAction(silenceAction)
            notificationBuilder.setStyle(androidx.media.app.NotificationCompat.MediaStyle().setShowActionsInCompactView(0, 1))
        } else {
            notificationBuilder.setColor(android.graphics.Color.parseColor("#0F172A"))
            
            val muteIntent = Intent(CallActionReceiver.ACTION_TOGGLE_MUTE).apply { setPackage(packageName) }
            val mutePendingIntent = PendingIntent.getBroadcast(this, 4, muteIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
            val muteIcon = if (isMuted) android.R.drawable.ic_lock_silent_mode_off else android.R.drawable.ic_btn_speak_now
            val muteLabel = if (isMuted) "Unmute" else "Mute"
            val muteAction = NotificationCompat.Action.Builder(muteIcon, muteLabel, mutePendingIntent).build()
            
            val endCallIntent = Intent(CallActionReceiver.ACTION_END_CALL).apply { setPackage(packageName) }
            val endCallPendingIntent = PendingIntent.getBroadcast(this, 5, endCallIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
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
        notificationManager.notify(NOTIFICATION_ID, notificationBuilder.build())
    }

"""

content = before_update + new_update_notif + after_update

with open('app/src/main/java/com/titan/zapdial/ZapCallService.kt', 'w') as f:
    f.write(content)
