import re

with open('app/src/main/java/com/titan/zapdial/CallSessionManager.kt', 'r') as f:
    content = f.read()

# Add allCalls flow
add_all_calls = """    val activeCall = MutableStateFlow<Call?>(null)
    val allCalls = MutableStateFlow<List<Call>>(emptyList())"""
content = content.replace("    val activeCall = MutableStateFlow<Call?>(null)", add_all_calls)

# Update toggleRecord
toggle_record_old = """    fun toggleRecord() {
        isRecording.value = !isRecording.value
    }"""
toggle_record_new = """    fun toggleRecord(context: android.content.Context) {
        val phoneNumber = activeCall.value?.details?.handle?.schemeSpecificPart ?: "Unknown"
        if (isRecording.value) {
            CallRecorder.stopRecording(context)
            isRecording.value = false
        } else {
            CallRecorder.startRecording(context, phoneNumber)
            isRecording.value = CallRecorder.isRecording
        }
    }"""
content = content.replace(toggle_record_old, toggle_record_new)

# Add Merge functionality
merge_new = """    fun mergeCalls() {
        val calls = allCalls.value
        if (calls.size >= 2) {
            val call1 = calls[0]
            val call2 = calls[1]
            call1.conference(call2)
        }
    }"""
content = content.replace("    fun playDtmfTone", merge_new + "\n\n    fun playDtmfTone")

with open('app/src/main/java/com/titan/zapdial/CallSessionManager.kt', 'w') as f:
    f.write(content)
