with open('app/src/main/java/com/titan/zapdial/CallActionReceiver.kt', 'r') as f:
    content = f.read()

new_actions = """        when (intent.action) {
            ACTION_TOGGLE_MUTE -> {
                CallSessionManager.toggleMute()
            }
            ACTION_END_CALL -> {
                val call = CallSessionManager.activeCall.value
                if (call?.state == android.telecom.Call.STATE_RINGING) {
                    CallSessionManager.rejectCall()
                } else {
                    CallSessionManager.disconnectCall()
                }
            }
            ACTION_ANSWER -> {
                CallSessionManager.answerCall()
                val mainIntent = Intent(context, MainActivity::class.java).apply {
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_REORDER_TO_FRONT or Intent.FLAG_ACTIVITY_SINGLE_TOP
                }
                context.startActivity(mainIntent)
            }
            ACTION_SILENCE -> {
                try {
                    val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as android.telecom.TelecomManager
                    telecomManager.silenceRinger()
                } catch (e: Exception) {}
            }
        }"""

content = content.replace("""        when (intent.action) {
            ACTION_TOGGLE_MUTE -> {
                CallSessionManager.toggleMute()
            }
            ACTION_END_CALL -> {
                // Reject call if it's ringing, otherwise disconnect
                val call = CallSessionManager.activeCall.value
                if (call?.state == android.telecom.Call.STATE_RINGING) {
                    CallSessionManager.rejectCall()
                } else {
                    CallSessionManager.disconnectCall()
                }
            }
        }""", new_actions)

content = content.replace('const val ACTION_END_CALL = "com.titan.zapdial.ACTION_END_CALL"', 'const val ACTION_END_CALL = "com.titan.zapdial.ACTION_END_CALL"\n        const val ACTION_ANSWER = "com.titan.zapdial.ACTION_ANSWER"\n        const val ACTION_SILENCE = "com.titan.zapdial.ACTION_SILENCE"')

with open('app/src/main/java/com/titan/zapdial/CallActionReceiver.kt', 'w') as f:
    f.write(content)
