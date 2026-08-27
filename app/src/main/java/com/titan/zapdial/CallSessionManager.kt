package com.titan.zapdial

import android.telecom.Call
import android.telecom.CallAudioState
import kotlinx.coroutines.flow.MutableStateFlow
import java.lang.ref.WeakReference

object CallSessionManager {
    val activeCall = MutableStateFlow<Call?>(null)
    val allCalls = MutableStateFlow<List<Call>>(emptyList())
    val callState = MutableStateFlow<Int>(Call.STATE_DISCONNECTED)
    val audioState = MutableStateFlow<CallAudioState?>(null)
    
    val isMuted = MutableStateFlow(false)
    val isOnHold = MutableStateFlow(false)
    val isRecording = MutableStateFlow(false)

    var serviceRef: WeakReference<ZapCallService>? = null

    fun answerCall() {
        activeCall.value?.answer(android.telecom.VideoProfile.STATE_AUDIO_ONLY)
    }

    fun rejectCall() {
        activeCall.value?.reject(false, null)
    }
    
    fun disconnectCall() {
        activeCall.value?.disconnect()
    }

    fun toggleMute() {
        val srv = serviceRef?.get() ?: return
        val currentMuted = isMuted.value
        srv.setMuted(!currentMuted)
        isMuted.value = !currentMuted
    }

    fun toggleSpeaker() {
        val srv = serviceRef?.get() ?: return
        val currentRoute = audioState.value?.route
        if (currentRoute == CallAudioState.ROUTE_SPEAKER) {
            srv.setAudioRoute(CallAudioState.ROUTE_EARPIECE)
        } else {
            srv.setAudioRoute(CallAudioState.ROUTE_SPEAKER)
        }
    }

    fun toggleHold() {
        activeCall.value?.let { call ->
            if (call.state == Call.STATE_HOLDING) {
                call.unhold()
                isOnHold.value = false
            } else {
                call.hold()
                isOnHold.value = true
            }
        }
    }
    
    fun toggleRecord(context: android.content.Context) {
        val phoneNumber = activeCall.value?.details?.handle?.schemeSpecificPart ?: "Unknown"
        if (isRecording.value) {
            CallRecorder.stopRecording(context)
            isRecording.value = false
        } else {
            CallRecorder.startRecording(context, phoneNumber)
            isRecording.value = CallRecorder.isRecording
        }
    }

    fun mergeCalls() {
        val calls = allCalls.value
        if (calls.size >= 2) {
            val call1 = calls[0]
            val call2 = calls[1]
            call1.conference(call2)
        }
    }

    fun playDtmfTone(digit: Char) {
        activeCall.value?.playDtmfTone(digit)
    }

    fun stopDtmfTone() {
        activeCall.value?.stopDtmfTone()
    }
}
