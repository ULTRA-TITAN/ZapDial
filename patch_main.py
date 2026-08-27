import re

with open("app/src/main/java/com/titan/zapdial/MainActivity.kt", "r") as f:
    content = f.read()

content = content.replace("    override fun onCreate(savedInstanceState: Bundle?) {", "    override fun onResume() {\n        super.onResume()\n        CallSessionManager.isAppInForeground = true\n    }\n\n    override fun onPause() {\n        super.onPause()\n        CallSessionManager.isAppInForeground = false\n    }\n\n    override fun onCreate(savedInstanceState: Bundle?) {")

with open("app/src/main/java/com/titan/zapdial/MainActivity.kt", "w") as f:
    f.write(content)
