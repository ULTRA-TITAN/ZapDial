import re

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

# Add onDelete parameter
content = content.replace(
    "fun CallHistoryItemCard(item: HomeCallItem) {",
    "fun CallHistoryItemCard(item: HomeCallItem, onDelete: (HomeCallItem) -> Unit = {}) {"
)

# Pass onDelete in LazyColumn
content = content.replace(
    "CallHistoryItemCard(item = call)",
    "CallHistoryItemCard(item = call, onDelete = { deletedItem -> callHistory = callHistory.filter { it.id != deletedItem.id } })"
)

# Add state for bottom sheet
state_addition = """    val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
    var callToConfirm by remember { mutableStateOf<String?>(null) }
    var showLongPressMenu by remember { mutableStateOf(false) }
    val view = LocalView.current
"""
content = content.replace(
    """    val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
    var callToConfirm by remember { mutableStateOf<String?>(null) }""",
    state_addition
)

# Replace clickable with combinedClickable/pointerInput
old_clickable = """        modifier = Modifier
            .fillMaxWidth()
            .clickable { expanded = !expanded }"""
new_clickable = """        modifier = Modifier
            .fillMaxWidth()
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = { expanded = !expanded },
                    onLongPress = { 
                        view.performHapticFeedback(android.view.HapticFeedbackConstants.LONG_PRESS)
                        showLongPressMenu = true
                    }
                )
            }"""
content = content.replace(old_clickable, new_clickable)

# Add long press bottom sheet
bottom_sheet_addition = """
    if (showLongPressMenu) {
        ModalBottomSheet(
            onDismissRequest = { showLongPressMenu = false },
            containerColor = ColorPureWhite
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 32.dp)
            ) {
                Text(
                    text = "Options for ${displayName}",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = ColorPureBlack,
                    modifier = Modifier.padding(16.dp)
                )
                
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable {
                            val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
                            val clip = android.content.ClipData.newPlainText("Phone Number", item.number)
                            clipboard.setPrimaryClip(clip)
                            android.widget.Toast.makeText(context, "Number copied to clipboard", android.widget.Toast.LENGTH_SHORT).show()
                            showLongPressMenu = false
                        }
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.ContentCopy, contentDescription = "Copy", tint = ColorSlateGray)
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Copy Phone Number", fontSize = 16.sp, color = ColorPureBlack)
                }
                
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable {
                            kotlinx.coroutines.GlobalScope.launch(kotlinx.coroutines.Dispatchers.IO) {
                                try {
                                    context.contentResolver.delete(
                                        CallLog.Calls.CONTENT_URI,
                                        "${CallLog.Calls._ID} = ?",
                                        arrayOf(item.id)
                                    )
                                } catch (e: Exception) {
                                    e.printStackTrace()
                                }
                            }
                            onDelete(item)
                            showLongPressMenu = false
                        }
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.Delete, contentDescription = "Delete", tint = ColorRedMissed)
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Delete Call Log", fontSize = 16.sp, color = ColorRedMissed)
                }
            }
        }
    }
"""

# Append to end of CallHistoryItemCard
# Find where the function ends. It ends just before `@Composable\nfun Avatar`
idx = content.find("@Composable\nfun Avatar")
# We need to insert bottom_sheet_addition right before the closing brace of CallHistoryItemCard
# The last part of CallHistoryItemCard is `    }\n}\n\n@Composable`
if idx != -1:
    content = content[:idx-3] + bottom_sheet_addition + content[idx-3:]

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)

