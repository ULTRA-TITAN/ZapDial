import re

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

# Add a state for contact-specific history dialog
state_new = """    var showContactHistoryFor by remember { mutableStateOf<String?>(null) }
"""
content = content.replace("    var showSettings by remember { mutableStateOf(false) }", "    var showSettings by remember { mutableStateOf(false) }\n" + state_new)

# Wire the View History click
view_history_old = """                    Text(
                        text = "View Call History",
                        color = ColorPureBlack,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium,
                        modifier = Modifier.clickable { /* View History */ }
                    )"""
view_history_new = """                    Text(
                        text = "View Call History",
                        color = ColorPureBlack,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium,
                        modifier = Modifier.clickable { showContactHistoryFor = item.number }
                    )"""
# Note: we need to update this inside the `CallHistoryItemCard` function. But wait, `CallHistoryItemCard` doesn't have access to `showContactHistoryFor` if it's defined inside `HomeScreen`.
# Let's pass a lambda `onViewHistory: (String) -> Unit` to CallHistoryItemCard.
