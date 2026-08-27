import re

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

content = content.replace("@androidx.compose.material3.ExperimentalMaterial3Api\n@Composable\nfun CallHistoryItemCard", 
                          "@androidx.compose.material3.ExperimentalMaterial3Api\n@androidx.compose.foundation.ExperimentalFoundationApi\n@Composable\nfun CallHistoryItemCard")

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)

