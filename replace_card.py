import re

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

card_pattern = re.compile(r'@Composable\nfun CallHistoryItemCard\(.*?\n    \}\n\}', re.DOTALL)
card_new = """@Composable
fun CallHistoryItemCard(item: HomeCallItem, onViewHistory: (String) -> Unit = {}, onDelete: (HomeCallItem) -> Unit = {}) {
    val context = LocalContext.current
    var expanded by remember { mutableStateOf(false) }
    
    val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
    var callToConfirm by remember { mutableStateOf<String?>(null) }
    var showLongPressMenu by remember { mutableStateOf(false) }
    val view = LocalView.current
    
    val callPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            val mistouch = sharedPrefs.getBoolean("KEY_MISTOUCH_PREVENTION", false)
            if (mistouch) callToConfirm = item.number else CallManager.makeCall(context, item.number)
        }
    }
    
    callToConfirm?.let { num ->
        CallConfirmationDialog(
            name = item.name,
            number = num,
            onConfirm = { CallManager.makeCall(context, num) },
            onDismiss = { callToConfirm = null }
        )
    }
    
    val displayName = item.name ?: item.number
    val relativeTime = DateUtils.getRelativeTimeSpanString(
        item.date, System.currentTimeMillis(), DateUtils.MINUTE_IN_MILLIS
    ).toString()
    
    val isMissed = item.type == CallLog.Calls.MISSED_TYPE
    val statusColor = if (isMissed) ColorRedMissed else ColorSlateGray
    val statusIcon = when (item.type) {
        CallLog.Calls.INCOMING_TYPE -> androidx.compose.material.icons.Icons.AutoMirrored.Filled.CallReceived
        CallLog.Calls.OUTGOING_TYPE -> androidx.compose.material.icons.Icons.AutoMirrored.Filled.CallMade
        CallLog.Calls.MISSED_TYPE -> androidx.compose.material.icons.Icons.AutoMirrored.Filled.CallMissed
        else -> androidx.compose.material.icons.Icons.AutoMirrored.Filled.CallReceived
    }
    val statusText = when (item.type) {
        CallLog.Calls.INCOMING_TYPE -> "Incoming"
        CallLog.Calls.OUTGOING_TYPE -> "Outgoing"
        CallLog.Calls.MISSED_TYPE -> "Missed"
        else -> "Unknown"
    }

    Card(
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = ColorPureWhite),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
        modifier = Modifier
            .fillMaxWidth()
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = { expanded = !expanded },
                    onLongPress = { 
                        view.performHapticFeedback(android.view.HapticFeedbackConstants.LONG_PRESS)
                        showLongPressMenu = true
                    }
                )
            }
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Left: Avatar
                Avatar(name = displayName, size = 52.dp)
                
                Spacer(modifier = Modifier.width(16.dp))
                // Middle Column: Contact Info
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = displayName,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium,
                        color = ColorPureBlack,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                    
                    Spacer(modifier = Modifier.height(2.dp))
                    
                    Text(
                        text = "${item.location} • $relativeTime",
                        fontSize = 13.sp,
                        color = ColorSlateGray,
                        fontWeight = FontWeight.Normal
                    )
                    
                    Spacer(modifier = Modifier.height(2.dp))
                    
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = item.simName,
                            fontSize = 13.sp,
                            color = ColorSlateGray,
                            fontWeight = FontWeight.Normal
                        )
                        Text(text = " • ", fontSize = 13.sp, color = ColorSlateGray)
                        Icon(
                            imageVector = statusIcon,
                            contentDescription = statusText,
                            tint = statusColor,
                            modifier = Modifier.size(12.dp)
                        )
                        Spacer(modifier = Modifier.width(2.dp))
                        Text(
                            text = statusText,
                            fontSize = 13.sp,
                            color = statusColor,
                            fontWeight = if (isMissed) FontWeight.Bold else FontWeight.Normal
                        )
                    }
                }
                Spacer(modifier = Modifier.width(12.dp))
                // Right: Call Button
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier
                        .size(48.dp)
                        .clip(CircleShape)
                        .background(ColorFaintGreen)
                        .clickable {
                            if (ContextCompat.checkSelfPermission(context, Manifest.permission.CALL_PHONE) == PackageManager.PERMISSION_GRANTED) {
                                val mistouch = sharedPrefs.getBoolean("KEY_MISTOUCH_PREVENTION", false)
                                if (mistouch) callToConfirm = item.number else CallManager.makeCall(context, item.number)
                            } else {
                                callPermissionLauncher.launch(Manifest.permission.CALL_PHONE)
                            }
                        }
                ) {
                    Icon(
                        imageVector = Icons.Default.Call,
                        contentDescription = "Call",
                        tint = ColorGreenSuccess,
                        modifier = Modifier.size(24.dp)
                    )
                }
            }
            AnimatedVisibility(visible = expanded) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(Color(0xFFF8FAFC))
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    Text(
                        text = "View Call History",
                        color = ColorPureBlack,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium,
                        modifier = Modifier.clickable { onViewHistory(item.number) }
                    )
                    Text(
                        text = if (item.name == null) "Add Contact" else "Edit Contact",
                        color = ColorPureBlack,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium,
                        modifier = Modifier.clickable {
                            val intent = Intent(Intent.ACTION_INSERT_OR_EDIT).apply {
                                type = ContactsContract.Contacts.CONTENT_ITEM_TYPE
                                putExtra(android.provider.ContactsContract.Intents.Insert.PHONE, item.number)
                            }
                            try { context.startActivity(intent) } catch(e: Exception) {}
                        }
                    )
                }
            }
        }
    }
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
}"""

content = card_pattern.sub(card_new, content)

avatar_pattern = re.compile(r'@Composable\nfun Avatar\(.*?\n    \}\n\}', re.DOTALL)
avatar_new = """@Composable
fun Avatar(name: String, size: Dp) {
    val color = remember(name) { getAvatarColor(name) }
    Box(
        contentAlignment = Alignment.Center,
        modifier = Modifier
            .size(size)
            .clip(CircleShape)
            .background(color)
    ) {
        Text(
            text = name.take(1).uppercase(),
            color = Color(0xFF0F172A),
            fontSize = (size.value * 0.4f).sp,
            fontWeight = FontWeight.Medium
        )
    }
}"""
content = avatar_pattern.sub(avatar_new, content)

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
