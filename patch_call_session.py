import re

with open("app/src/main/java/com/titan/zapdial/CallSessionManager.kt", "r") as f:
    content = f.read()

content = content.replace("    var serviceRef: WeakReference<ZapCallService>? = null\n\n    fun answerCall() {", "    var serviceRef: WeakReference<ZapCallService>? = null\n    var isAppInForeground = false\n\n    fun answerCall() {")

with open("app/src/main/java/com/titan/zapdial/CallSessionManager.kt", "w") as f:
    f.write(content)
