import re

with open("app/src/main/java/com/titan/zapdial/ZapCallService.kt", "r") as f:
    content = f.read()

if "import kotlinx.coroutines.launch" not in content:
    content = content.replace("import android.content.Context", "import android.content.Context\nimport kotlinx.coroutines.launch")

with open("app/src/main/java/com/titan/zapdial/ZapCallService.kt", "w") as f:
    f.write(content)
