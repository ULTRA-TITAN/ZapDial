with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

# Add lambda to signature
sig_old = """fun CallHistoryItemCard(item: HomeCallItem, onDelete: (HomeCallItem) -> Unit) {"""
sig_new = """fun CallHistoryItemCard(item: HomeCallItem, onDelete: (HomeCallItem) -> Unit, onViewHistory: (String) -> Unit) {"""
content = content.replace(sig_old, sig_new)

# Wire the click
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
                        modifier = Modifier.clickable { onViewHistory(item.number) }
                    )"""
content = content.replace(view_history_old, view_history_new)

# Update the caller inside HomeScreen
caller_old = """CallHistoryItemCard(item = call, onDelete = { deletedItem ->"""
caller_new = """CallHistoryItemCard(item = call, onViewHistory = { number -> showContactHistoryFor = number }, onDelete = { deletedItem ->"""
content = content.replace(caller_old, caller_new)

# Add the dialog UI at the bottom of HomeScreen()
dialog_ui = """    if (showContactHistoryFor != null) {
        ModalBottomSheet(
            onDismissRequest = { showContactHistoryFor = null },
            containerColor = ColorPureWhite
        ) {
            val contactHistory = callHistory.filter { android.telephony.PhoneNumberUtils.compare(it.number, showContactHistoryFor) }
            Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
                Text("History with $showContactHistoryFor", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = ColorPureBlack)
                Spacer(modifier = Modifier.height(16.dp))
                if (contactHistory.isEmpty()) {
                    Text("No call history with this contact", fontSize = 16.sp, color = ColorSlateGray)
                } else {
                    LazyColumn {
                        items(contactHistory) { log ->
                            Row(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                                val typeIcon = when(log.type) {
                                    android.provider.CallLog.Calls.INCOMING_TYPE -> Icons.Default.CallReceived
                                    android.provider.CallLog.Calls.OUTGOING_TYPE -> Icons.Default.CallMade
                                    android.provider.CallLog.Calls.MISSED_TYPE -> Icons.Default.CallMissed
                                    else -> Icons.Default.Call
                                }
                                val typeColor = if (log.type == android.provider.CallLog.Calls.MISSED_TYPE) ColorRedMissed else ColorGreenSuccess
                                Icon(typeIcon, null, tint = typeColor, modifier = Modifier.size(24.dp))
                                Spacer(modifier = Modifier.width(16.dp))
                                Column {
                                    val dateStr = java.text.SimpleDateFormat("MMM dd, h:mm a", java.util.Locale.getDefault()).format(java.util.Date(log.date))
                                    Text(dateStr, fontSize = 16.sp, color = ColorPureBlack)
                                    val durationStr = if (log.type == android.provider.CallLog.Calls.MISSED_TYPE) "Missed" else "${log.duration / 60}m ${log.duration % 60}s"
                                    Text(durationStr, fontSize = 14.sp, color = ColorSlateGray)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
"""

content = content.replace("    if (showContactPicker) {", dialog_ui + "\n    if (showContactPicker) {")

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
