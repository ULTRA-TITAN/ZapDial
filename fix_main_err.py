import re
with open('app/src/main/java/com/titan/zapdial/MainActivity.kt', 'r') as f:
    content = f.read()

content = content.replace("    val callState by CallSessionManager.callState.collectAsState()\n    val callState by CallSessionManager.callState.collectAsState()", "    val callState by CallSessionManager.callState.collectAsState()")

with open('app/src/main/java/com/titan/zapdial/MainActivity.kt', 'w') as f:
    f.write(content)
