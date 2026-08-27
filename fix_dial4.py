import re
with open('app/src/main/java/com/titan/zapdial/DialPadScreen.kt', 'r') as f:
    content = f.read()

content = content.replace("kotlinx.coroutines.GlobalScope.launch {", "coroutineScope.launch {")

with open('app/src/main/java/com/titan/zapdial/DialPadScreen.kt', 'w') as f:
    f.write(content)
