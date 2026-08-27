import re

with open("app/src/main/java/com/titan/zapdial/SimSelectionDialog.kt", "r") as f:
    content = f.read()

content = content.replace("androidx.compose.material.icons.Icons.Default?.let {", "")
content = content.replace("                    }", "")
content = content.replace("Icon(androidx.compose.material.icons.Icons.Default.Call", "Icon(androidx.compose.material.icons.filled.Call")

imports = """
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Call
"""
content = re.sub(r'import androidx\.compose\.runtime\.Composable', imports.strip() + '\nimport androidx.compose.runtime.Composable', content)

with open("app/src/main/java/com/titan/zapdial/SimSelectionDialog.kt", "w") as f:
    f.write(content)

