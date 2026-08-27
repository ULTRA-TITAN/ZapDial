import re

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

content = content.replace("    if (showContactPicker) {", "        SnackbarHost(\n            hostState = snackbarHostState,\n            modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 64.dp)\n        )\n    }\n\n    if (showContactPicker) {")

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
