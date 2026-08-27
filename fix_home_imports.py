with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

imports = [
    "import androidx.compose.material.icons.filled.ContentCopy",
    "import androidx.compose.material.icons.filled.Delete",
    "import kotlinx.coroutines.launch",
    "import kotlinx.coroutines.GlobalScope"
]

for imp in imports:
    if imp not in content:
        content = content.replace("import androidx.compose.material.icons.filled.Add", imp + "\nimport androidx.compose.material.icons.filled.Add")

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
