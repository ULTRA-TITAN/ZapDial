import re

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

# Update Search Bar
old_search_box = """                    Box(modifier = Modifier.weight(1f).padding(horizontal = 8.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Search, contentDescription = "Search", tint = TextSecondary)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Search contacts", color = TextSecondary, fontSize = 16.sp)
                        }
                    }

                    IconButton(onClick = { /* Voice Search */ }) {"""

new_search_box = """                    Box(modifier = Modifier
                        .weight(1f)
                        .padding(horizontal = 8.dp)
                        .clickable {
                            val intent = Intent(Intent.ACTION_VIEW, ContactsContract.Contacts.CONTENT_URI)
                            try { context.startActivity(intent) } catch (e: Exception) {}
                        }
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Search, contentDescription = "Search", tint = TextSecondary)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Search contacts", color = TextSecondary, fontSize = 16.sp)
                        }
                    }

                    IconButton(onClick = {
                        val intent = Intent(android.speech.RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                            putExtra(android.speech.RecognizerIntent.EXTRA_LANGUAGE_MODEL, android.speech.RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                        }
                        try { context.startActivity(intent) } catch (e: Exception) {}
                    }) {"""

content = content.replace(old_search_box, new_search_box)

# Update Favorites text and horizontal list
# Remove "Favorites" text
old_favorites_text = """                item {
                    Text(
                        text = "Favorites",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Medium,
                        color = TextPrimary,
                        modifier = Modifier.padding(bottom = 12.dp, start = 8.dp)
                    )
                }
                
                item {"""

new_favorites_text = """                item {"""

content = content.replace(old_favorites_text, new_favorites_text)

# Add "Add" button to lazy row
old_lazy_row_end = """                                }
                            }
                        }
                    } else {"""
                    
new_lazy_row_end = """                                }
                            }
                            item {
                                Column(
                                    horizontalAlignment = Alignment.CenterHorizontally,
                                    modifier = Modifier.clickable {
                                        val intent = Intent(Intent.ACTION_INSERT, ContactsContract.Contacts.CONTENT_URI)
                                        try { context.startActivity(intent) } catch(e: Exception) {}
                                    }
                                ) {
                                    Box(
                                        contentAlignment = Alignment.Center,
                                        modifier = Modifier.size(56.dp).clip(CircleShape).background(Color.White).androidx.compose.foundation.border(1.dp, Color(0xFFE2E8F0), CircleShape)
                                    ) {
                                        Text("+", fontSize = 24.sp, color = TextSecondary, fontWeight = FontWeight.Light)
                                    }
                                    Spacer(modifier = Modifier.height(8.dp))
                                    Text(
                                        text = "Add",
                                        fontSize = 13.sp,
                                        fontWeight = FontWeight.Medium,
                                        color = TextSecondary,
                                        maxLines = 1,
                                        overflow = TextOverflow.Ellipsis
                                    )
                                }
                            }
                        }
                    } else {"""

content = content.replace(old_lazy_row_end, new_lazy_row_end)

# Also need to limit to 3 contacts
content = content.replace("val frequent = allContacts.take(8)", "val frequent = allContacts.take(3)")


# Now fix CallHistoryItemCard
old_card_content = """        Column(modifier = Modifier.fillMaxWidth()) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier.size(50.dp).clip(CircleShape).background(getAvatarColor(displayName))
                ) {
                    Text(
                        text = displayName.take(1).uppercase(),
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Medium,
                        color = Color.White
                    )
                }
                Spacer(modifier = Modifier.width(16.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = displayName,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Normal,
                        color = if (isMissed) ColorRedMissed else TextPrimary,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                    
                    Spacer(modifier = Modifier.height(3.dp))
                    
                    Text(
                        text = "${item.location} • $relativeTime",
                        fontSize = 13.sp,
                        color = TextSecondary,
                        fontWeight = FontWeight.Light
                    )
                    
                    Spacer(modifier = Modifier.height(3.dp))
                    
                    Text(
                        text = item.simName,
                        fontSize = 13.sp,
                        color = TextSecondary,
                        fontWeight = FontWeight.Light
                    )
                }
                
                IconButton(onClick = {
                    if (ContextCompat.checkSelfPermission(context, Manifest.permission.CALL_PHONE) == PackageManager.PERMISSION_GRANTED) {
                        if (mistouchPrevention) callToConfirm = item.number else CallManager.makeCall(context, item.number)
                    } else {
                        callPermissionLauncher.launch(Manifest.permission.CALL_PHONE)
                    }
                }) {
                    Icon(Icons.Default.Call, contentDescription = "Call", tint = ColorGreenSuccess)
                }
            }"""

new_card_content = """        Column(modifier = Modifier.fillMaxWidth()) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier.size(50.dp).clip(CircleShape).background(getAvatarColor(displayName))
                ) {
                    Text(
                        text = displayName.take(1).uppercase(),
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Medium,
                        color = TextPrimary
                    )
                }
                Spacer(modifier = Modifier.width(16.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = displayName,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium,
                        color = TextPrimary,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                    
                    Spacer(modifier = Modifier.height(2.dp))
                    
                    Text(
                        text = "${item.location} • $relativeTime",
                        fontSize = 13.sp,
                        color = TextSecondary,
                        fontWeight = FontWeight.Normal
                    )
                    
                    Spacer(modifier = Modifier.height(2.dp))
                    
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = "${item.simName} • ",
                            fontSize = 13.sp,
                            color = TextSecondary,
                            fontWeight = FontWeight.Normal
                        )
                        val icon = when (item.type) {
                            CallLog.Calls.INCOMING_TYPE -> Icons.AutoMirrored.Filled.CallReceived
                            CallLog.Calls.MISSED_TYPE -> Icons.AutoMirrored.Filled.CallMissed
                            else -> Icons.AutoMirrored.Filled.CallMade
                        }
                        Icon(icon, contentDescription = null, tint = if (isMissed) ColorRedMissed else TextSecondary, modifier = Modifier.size(12.dp))
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = when (item.type) {
                                CallLog.Calls.INCOMING_TYPE -> "Incoming"
                                CallLog.Calls.MISSED_TYPE -> "Missed"
                                else -> "Outgoing"
                            },
                            fontSize = 13.sp,
                            color = if (isMissed) ColorRedMissed else TextSecondary,
                            fontWeight = FontWeight.Normal
                        )
                    }
                }
                
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(CircleShape)
                        .background(Color(0xFFE8F3EB))
                        .clickable {
                            if (ContextCompat.checkSelfPermission(context, Manifest.permission.CALL_PHONE) == PackageManager.PERMISSION_GRANTED) {
                                if (mistouchPrevention) callToConfirm = item.number else CallManager.makeCall(context, item.number)
                            } else {
                                callPermissionLauncher.launch(Manifest.permission.CALL_PHONE)
                            }
                        },
                    contentAlignment = Alignment.Center
                ) {
                    Icon(Icons.Default.Call, contentDescription = "Call", tint = Color(0xFF2A7840), modifier = Modifier.size(20.dp))
                }
            }"""

content = content.replace(old_card_content, new_card_content)

# We need to make the avatar text black instead of white
content = content.replace("""        Text(
            text = displayName.take(1).uppercase(),
            fontSize = (size.value * 0.45).sp,
            fontWeight = FontWeight.Medium,
            color = Color.White
        )""", """        Text(
            text = displayName.take(1).uppercase(),
            fontSize = (size.value * 0.45).sp,
            fontWeight = FontWeight.Medium,
            color = TextPrimary
        )""")


with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)
