package com.titan.zapdial

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

class CallActionReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
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
                try { context.startActivity(mainIntent) } catch (e: Exception) { android.widget.Toast.makeText(context, "Action unavailable", android.widget.Toast.LENGTH_SHORT).show() }
            }
            ACTION_SILENCE -> {
                try {
                    val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as android.telecom.TelecomManager
                    telecomManager.silenceRinger()
                } catch (e: Exception) {}
            }
        }
    }

    companion object {
        const val ACTION_TOGGLE_MUTE = "com.titan.zapdial.ACTION_TOGGLE_MUTE"
        const val ACTION_END_CALL = "com.titan.zapdial.ACTION_END_CALL"
        const val ACTION_ANSWER = "com.titan.zapdial.ACTION_ANSWER"
        const val ACTION_SILENCE = "com.titan.zapdial.ACTION_SILENCE"
    }
}
