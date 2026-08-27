with open('app/src/main/java/com/titan/zapdial/ContactsScreen.kt', 'r') as f:
    content = f.read()

content = content.replace("import androidx.compose.foundation.gestures.detectDragGestures", "import androidx.compose.foundation.gestures.detectDragGestures\nimport androidx.compose.foundation.gestures.detectVerticalDragGestures\nimport androidx.compose.foundation.gestures.detectTapGestures")
content = content.replace("androidx.compose.foundation.gestures.detectVerticalDragGestures(", "detectVerticalDragGestures(")
content = content.replace("androidx.compose.foundation.gestures.detectTapGestures(", "detectTapGestures(")

with open('app/src/main/java/com/titan/zapdial/ContactsScreen.kt', 'w') as f:
    f.write(content)
