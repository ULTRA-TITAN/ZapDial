import re
with open('app/src/main/java/com/titan/zapdial/DialPadScreen.kt', 'r') as f:
    content = f.read()

content = content.replace("""        if (isGranted && number.isNotEmpty()) {
            attemptCall(number)
        }
    }
    
    val coroutineScope = rememberCoroutineScope()""", """        if (isGranted && number.isNotEmpty()) {
            attemptCall(number)
        }
    }""")

content = content.replace("    var number by remember { mutableStateOf(\"\") }", "    var number by remember { mutableStateOf(\"\") }\n    val coroutineScope = rememberCoroutineScope()")

with open('app/src/main/java/com/titan/zapdial/DialPadScreen.kt', 'w') as f:
    f.write(content)
