import re

with open("/app/applet/app/src/main/java/com/titan/zapdial/ContactsScreen.kt", "r") as f:
    content = f.read()

content = content.replace('mutableFloatStateOf(0f)', 'mutableStateOf(0f)')
content = content.replace('androidx.compose.material.icons.filled.Block', 'androidx.compose.material.icons.Icons.Default.Close') # Use Close since Block might not be there
content = content.replace('androidx.compose.material.icons.filled.History', 'androidx.compose.material.icons.Icons.Default.Refresh') # Use Refresh if we can't import History, wait, let's just use Icons.Default.DateRange

# Wait, if I just add the imports:
if 'import androidx.compose.material.icons.Icons' not in content:
    content = content.replace('import androidx.compose.material.icons.Icons.Default', 'import androidx.compose.material.icons.Icons')

# Let's just use Icons.Default.Close and Icons.Default.DateRange, they exist in core
with open("/app/applet/app/src/main/java/com/titan/zapdial/ContactsScreen.kt", "w") as f:
    f.write(content)

