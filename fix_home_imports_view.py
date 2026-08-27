with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

content = content.replace("import androidx.compose.ui.platform.LocalContext", "import androidx.compose.ui.platform.LocalContext\nimport androidx.compose.ui.platform.LocalView")

content = content.replace("fun CallHistoryItemCard(item: HomeCallItem, onDelete: (HomeCallItem) -> Unit = {}) {", "@OptIn(ExperimentalMaterial3Api::class)\n@Composable\nfun CallHistoryItemCard(item: HomeCallItem, onDelete: (HomeCallItem) -> Unit = {}) {")
content = content.replace("@Composable\n@OptIn(ExperimentalMaterial3Api::class)\n@Composable", "@OptIn(ExperimentalMaterial3Api::class)\n@Composable")

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
