import re

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

old_card_pattern = r"fun CallHistoryItemCard\([\s\S]*?Icon\(Icons\.Default\.Edit, contentDescription = null, modifier = Modifier\.size\(20\.dp\)\)\n\s*Spacer\(modifier = Modifier\.width\(12\.dp\)\)\n\s*Text\(\"Edit Contact\", fontSize = 15\.sp, fontWeight = FontWeight\.Medium\)\n\s*\}\n\s*\}\n\s*\}\n\s*\}"

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
    val relativeTime = DateUtils.getRelativeTimeSpanString(
        item.date, System.currentTimeMillis(), DateUtils.MINUTE_IN_MILLIS
    ).toString()
    
    val isMissed = item.type == CallLog.Calls.MISSED_TYPE
    val isIncoming = item.type == CallLog.Calls.INCOMING_TYPE
    
    val statusColor = if (isMissed) Color(0xFFB3574F) else Color(0xFF9A9AA2)
    val statusText = when {
        isMissed -> "Missed"
        isIncoming -> "Incoming"
        else -> "Outgoing"
    }
    val statusIcon = when {
        isMissed -> Icons.Default.CallMissed
        isIncoming -> Icons.Default.CallReceived
        else -> Icons.Default.CallMade
    }
    
    Card(
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFFFFFFF)),
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
                        color = Color(0xFF44444C)
                    )
                }
                Spacer(modifier = Modifier.width(16.dp))

                // Middle Column
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = displayName,
                        fontSize = 17.sp,
                        fontWeight = FontWeight.Normal,
                        color = Color(0xFF2A2A2E),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                    
                    Spacer(modifier = Modifier.height(2.dp))
                    
                    Text(
                        text = "${item.location} • $relativeTime",
                        fontSize = 12.5.sp,
                        color = Color(0xFF9A9AA2),
                        fontWeight = FontWeight.Light
                    )
                    
                    Spacer(modifier = Modifier.height(2.dp))
                    
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = "${item.simName} • ",
                            fontSize = 12.5.sp,
                            color = Color(0xFF9A9AA2),
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
                        .background(Color(0xFF4C8B62).copy(alpha = 0.14f))
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
                        tint = Color(0xFF4C8B62),
                        modifier = Modifier.size(18.dp)
                    )
                }
            }
            
            AnimatedVisibility(visible = expanded) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(Color(0xFFFAFAF9))
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedButton(
                        onClick = onViewHistory,
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFF2A2A2E)),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Icon(Icons.Default.History, contentDescription = null, modifier = Modifier.size(20.dp))
                        Spacer(modifier = Modifier.width(12.dp))
                        Text("View Call History", fontSize = 15.sp, fontWeight = FontWeight.Medium)
                    }
                    OutlinedButton(
                        onClick = {
                            val intent = Intent(Intent.ACTION_INSERT_OR_EDIT).apply {
                                type = ContactsContract.Contacts.CONTENT_ITEM_TYPE
                                putExtra(android.provider.ContactsContract.Intents.Insert.PHONE, item.number)
                            }
                            try { context.startActivity(intent) } catch(e: Exception) {}
                        },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFF2A2A2E)),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Icon(Icons.Default.Edit, contentDescription = null, modifier = Modifier.size(20.dp))
                        Spacer(modifier = Modifier.width(12.dp))
                        Text("Edit Contact", fontSize = 15.sp, fontWeight = FontWeight.Medium)
                    }
                }
            }
        }
    }"""

content = re.sub(old_card_pattern, new_card, content)

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)
