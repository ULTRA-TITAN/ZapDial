import re

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

# Just remove the second occurrence of `import androidx.compose.material.icons.Icons`
content = content.replace("import androidx.compose.material.icons.automirrored.filled.CallMissed\nimport androidx.compose.material.icons.Icons\nimport androidx.compose.material.icons.filled.Mic", "import androidx.compose.material.icons.automirrored.filled.CallMissed\nimport androidx.compose.material.icons.filled.Mic")

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
