import re

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

content = content.replace(".androidx.compose.foundation.border", ".border")
content = content.replace("androidx.compose.material.icons.Icons.AutoMirrored.Filled.CallReceived", "Icons.AutoMirrored.Filled.CallReceived")
content = content.replace("androidx.compose.material.icons.Icons.AutoMirrored.Filled.CallMade", "Icons.AutoMirrored.Filled.CallMade")
content = content.replace("androidx.compose.material.icons.Icons.AutoMirrored.Filled.CallMissed", "Icons.AutoMirrored.Filled.CallMissed")

if "import androidx.compose.foundation.border" not in content:
    content = content.replace("import androidx.compose.foundation.background", "import androidx.compose.foundation.background\nimport androidx.compose.foundation.border")

if "import androidx.compose.material.icons.automirrored.filled.CallReceived" not in content:
    content = content.replace("import androidx.compose.material.icons.filled.CallReceived", "import androidx.compose.material.icons.filled.CallReceived\nimport androidx.compose.material.icons.automirrored.filled.CallReceived\nimport androidx.compose.material.icons.automirrored.filled.CallMade\nimport androidx.compose.material.icons.automirrored.filled.CallMissed\nimport androidx.compose.material.icons.Icons")

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
