import re

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

if "import androidx.compose.material.icons.filled.CallMissed" not in content:
    content = content.replace("import androidx.compose.material.icons.filled.Call", "import androidx.compose.material.icons.filled.Call\nimport androidx.compose.material.icons.filled.CallMissed\nimport androidx.compose.material.icons.filled.CallReceived\nimport androidx.compose.material.icons.filled.CallMade")

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)
