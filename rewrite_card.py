import re

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

card_pattern = r"fun CallHistoryItemCard\(.*?\n    if \(showLongPressMenu\) \{"

new_card = """fun CallHistoryItemCard(
    item: HomeCallItem, 
    mistouchPrevention: Boolean,
    onViewHistory: () -> Unit = {},
    onDelete: (HomeCallItem) -> Unit
) {
    val context = LocalContext.current
    val view = LocalView.current
    var expanded by remember { mutableStateOf(false) }
    var callToConfirm by remember { mutableStateOf<String?>(null) }
    var showLongPressMenu by remember { mutableStateOf(false) }
    var showSimSelectionFor by remember { mutableStateOf<String?>(null) }
    var availableSimsForCall by remember { mutableStateOf<List<android.telecom.PhoneAccountHandle>>(emptyList()) }
    
    if (showSimSelectionFor != null) {
        SimSelectionDialog(
            context = context,
            availableSims = availableSimsForCall,
            onSimSelected = { handle ->
                CallManager.makeCall(context, showSimSelectionFor!!, handle)
                showSimSelectionFor = null
            },
            onDismiss = { showSimSelectionFor = null }
        )
    }
    
    val callPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            if (mistouchPrevention) callToConfirm = item.number else CallManager.initiateCallWithSimCheck(context, item.number) { sims ->
                                                    availableSimsForCall = sims
                                                    showSimSelectionFor = item.number
                                                }
        }
    }
    
    callToConfirm?.let { num ->
        CallConfirmationDialog(
            name = item.name,
            number = num,
            onConfirm = { CallManager.initiateCallWithSimCheck(context, num) { sims -> availableSimsForCall = sims; showSimSelectionFor = num } },
            onDismiss = { callToConfirm = null }
        )
    }
    
    val displayName = item.name ?: item.number
    val relativeTime = android.text.format.DateUtils.getRelativeTimeSpanString(
        item.date, System.currentTimeMillis(), android.text.format.DateUtils.MINUTE_IN_MILLIS
    ).toString()
    
    val isMissed = item.type == CallLog.Calls.MISSED_TYPE
    val isIncoming = item.type == CallLog.Calls.INCOMING_TYPE
    
    val statusColor = if (isMissed) androidx.compose.ui.graphics.Color(0xFFB3574F) else androidx.compose.ui.graphics.Color(0xFF9A9AA2)
    val statusText = when {
        isMissed -> "Missed"
        isIncoming -> "Incoming"
        else -> "Outgoing"
    }
    val statusIcon = when {
        isMissed -> Icons.AutoMirrored.Filled.CallMissed
        isIncoming -> Icons.AutoMirrored.Filled.CallReceived
        else -> Icons.AutoMirrored.Filled.CallMade
    }
    
    Card(
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = androidx.compose.ui.graphics.Color(0xFFFFFFFF)),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp),
        modifier = Modifier
            .fillMaxWidth()
            .combinedClickable(
                onClick = { expanded = !expanded },
                onLongClick = { 
                    view.performHapticFeedback(android.view.HapticFeedbackConstants.LONG_PRESS)
                    showLongPressMenu = true
                }
            )
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Left Avatar
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier.size(46.dp).clip(CircleShape).background(getAvatarColor(displayName))
                ) {
                    Text(
                        text = displayName.take(1).uppercase(),
                        fontSize = 17.sp,
                        fontWeight = FontWeight.Light,
                        color = androidx.compose.ui.graphics.Color(0xFF44444C)
                    )
                }
                Spacer(modifier = Modifier.width(16.dp))

                // Middle Column
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = displayName,
                        fontSize = 17.sp,
                        fontWeight = FontWeight.Normal,
                        color = androidx.compose.ui.graphics.Color(0xFF2A2A2E),
                        maxLines = 1,
                        overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis
                    )
                    
                    Spacer(modifier = Modifier.height(2.dp))
                    
                    Text(
                        text = "${item.location} • $relativeTime",
                        fontSize = 12.5.sp,
                        color = androidx.compose.ui.graphics.Color(0xFF9A9AA2),
                        fontWeight = FontWeight.Light
                    )
                    
                    Spacer(modifier = Modifier.height(2.dp))
                    
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = "${item.simName} • ",
                            fontSize = 12.5.sp,
                            color = androidx.compose.ui.graphics.Color(0xFF9A9AA2),
                            fontWeight = FontWeight.Normal
                        )
                        Icon(
                            imageVector = statusIcon,
                            contentDescription = statusText,
                            tint = statusColor,
                            modifier = Modifier.size(13.dp)
                        )
                        Spacer(modifier = Modifier.width(2.dp))
                        Text(
                            text = statusText,
                            fontSize = 12.5.sp,
                            color = statusColor,
                            fontWeight = FontWeight.Normal
                        )
                    }
                }
                
                Spacer(modifier = Modifier.width(8.dp))
                
                // Right Call Button
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier
                        .size(40.dp)
                        .clip(CircleShape)
                        .background(androidx.compose.ui.graphics.Color(0xFF4C8B62).copy(alpha = 0.14f))
                        .clickable {
                            if (ContextCompat.checkSelfPermission(context, Manifest.permission.CALL_PHONE) == PackageManager.PERMISSION_GRANTED) {
                                if (mistouchPrevention) callToConfirm = item.number else CallManager.initiateCallWithSimCheck(context, item.number) { sims ->
                                    availableSimsForCall = sims
                                    showSimSelectionFor = item.number
                                }
                            } else {
                                callPermissionLauncher.launch(Manifest.permission.CALL_PHONE)
                            }
                        }
                ) {
                    Icon(
                        imageVector = Icons.Default.Call,
                        contentDescription = "Call",
                        tint = androidx.compose.ui.graphics.Color(0xFF4C8B62),
                        modifier = Modifier.size(18.dp)
                    )
                }
            }
            
            AnimatedVisibility(visible = expanded) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(androidx.compose.ui.graphics.Color(0xFFFDFCFA))
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedButton(
                        onClick = onViewHistory,
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = androidx.compose.ui.graphics.Color(0xFF2A2A2E)),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Icon(Icons.Default.History, contentDescription = null, modifier = Modifier.size(20.dp))
                        Spacer(modifier = Modifier.width(12.dp))
                        Text("View Call History", fontSize = 15.sp, fontWeight = FontWeight.Medium)
                    }
                    OutlinedButton(
                        onClick = {
                            kotlinx.coroutines.GlobalScope.launch(kotlinx.coroutines.Dispatchers.IO) {
                                var contactId: String? = null
                                try {
                                    val uri = android.net.Uri.withAppendedPath(ContactsContract.PhoneLookup.CONTENT_FILTER_URI, android.net.Uri.encode(item.number))
                                    context.contentResolver.query(uri, arrayOf(ContactsContract.PhoneLookup._ID), null, null, null)?.use { cursor ->
                                        if (cursor.moveToFirst()) {
                                            val idIdx = cursor.getColumnIndex(ContactsContract.PhoneLookup._ID)
                                            if (idIdx != -1) contactId = cursor.getString(idIdx)
                                        }
                                    }
                                } catch(e: Exception) {}
                                
                                kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.Main) {
                                    if (contactId != null) {
                                        val editIntent = Intent(Intent.ACTION_EDIT).apply {
                                            data = android.net.Uri.withAppendedPath(ContactsContract.Contacts.CONTENT_URI, contactId)
                                        }
                                        try { context.startActivity(editIntent) } catch(e: Exception) {}
                                    } else {
                                        val insertIntent = Intent(Intent.ACTION_INSERT).apply {
                                            type = ContactsContract.RawContacts.CONTENT_TYPE
                                            putExtra(android.provider.ContactsContract.Intents.Insert.PHONE, item.number)
                                        }
                                        try { context.startActivity(insertIntent) } catch(e: Exception) {}
                                    }
                                }
                            }
                        },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = androidx.compose.ui.graphics.Color(0xFF2A2A2E)),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Icon(Icons.Default.Edit, contentDescription = null, modifier = Modifier.size(20.dp))
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(if (item.name == null) "Add Contact" else "Edit Contact", fontSize = 15.sp, fontWeight = FontWeight.Medium)
                    }
                }
            }
        }
    }
    if (showLongPressMenu) {"""

content = re.sub(card_pattern, new_card, content, flags=re.DOTALL)

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)
