with open('app/src/main/java/com/titan/zapdial/ContactsScreen.kt', 'r') as f:
    content = f.read()

# Add Mistouch Prevention state
state_decl = """    val callPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            // Permission granted
        }
    }"""
new_state_decl = """    val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
    var callToConfirm by remember { mutableStateOf<Pair<String, String>?>(null) }
    
    val callPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            // Permission granted
        }
    }"""
content = content.replace(state_decl, new_state_decl)

# Mistouch click action
call_action = """                                    .clickable {
                                        if (ContextCompat.checkSelfPermission(context, Manifest.permission.CALL_PHONE) == PackageManager.PERMISSION_GRANTED) {
                                            CallManager.makeCall(context, contact.phoneNumber)
                                        } else {
                                            callPermissionLauncher.launch(Manifest.permission.CALL_PHONE)
                                        }
                                    }"""
new_call_action = """                                    .clickable {
                                        if (ContextCompat.checkSelfPermission(context, Manifest.permission.CALL_PHONE) == PackageManager.PERMISSION_GRANTED) {
                                            val mistouch = sharedPrefs.getBoolean("KEY_MISTOUCH_PREVENTION", false)
                                            if (mistouch) {
                                                callToConfirm = Pair(contact.name, contact.phoneNumber)
                                            } else {
                                                CallManager.makeCall(context, contact.phoneNumber)
                                            }
                                        } else {
                                            callPermissionLauncher.launch(Manifest.permission.CALL_PHONE)
                                        }
                                    }"""
content = content.replace(call_action, new_call_action)

# Add CallConfirmationDialog to the end
end_dialog = """    if (showAddDialog) {
        AddContactDialog(
            onDismiss = { showAddDialog = false },
            onContactAdded = { refreshContacts() }
        )
    }"""
new_end_dialog = """    if (showAddDialog) {
        AddContactDialog(
            onDismiss = { showAddDialog = false },
            onContactAdded = { refreshContacts() }
        )
    }
    
    callToConfirm?.let { (name, number) ->
        CallConfirmationDialog(
            name = name,
            number = number,
            onConfirm = { CallManager.makeCall(context, number) },
            onDismiss = { callToConfirm = null }
        )
    }"""
content = content.replace(end_dialog, new_end_dialog)


# Fast scroller replacement
scroller_start = content.find('// A-Z Fast Scroller')
scroller_end = content.find('}', content.rfind('Text(', scroller_start, content.find('showAddDialog'))) + 18 # past the alphabet.forEach loop

new_scroller = """// A-Z Fast Scroller
                var hoveredLetter by remember { mutableStateOf<Char?>(null) }
                val view = LocalView.current
                
                Box(modifier = Modifier.align(Alignment.CenterEnd).fillMaxHeight()) {
                    // Floating Bubble
                    androidx.compose.animation.AnimatedVisibility(
                        visible = hoveredLetter != null,
                        enter = androidx.compose.animation.fadeIn() + androidx.compose.animation.scaleIn(),
                        exit = androidx.compose.animation.fadeOut() + androidx.compose.animation.scaleOut(),
                        modifier = Modifier.align(Alignment.CenterStart).offset(x = (-48).dp)
                    ) {
                        Box(
                            contentAlignment = Alignment.Center,
                            modifier = Modifier
                                .size(56.dp)
                                .clip(CircleShape)
                                .background(Color(0xFF16A34A))
                        ) {
                            Text(
                                text = hoveredLetter?.toString() ?: "",
                                fontSize = 24.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color.White
                            )
                        }
                    }

                    Column(
                        modifier = Modifier
                            .padding(end = 4.dp, top = 24.dp, bottom = 24.dp)
                            .fillMaxHeight()
                            .pointerInput(Unit) {
                                detectDragGestures(
                                    onDragStart = { offset ->
                                        val itemHeight = size.height / alphabet.size.toFloat()
                                        val index = (offset.y / itemHeight).toInt().coerceIn(0, alphabet.lastIndex)
                                        val letter = alphabet[index]
                                        hoveredLetter = letter
                                        firstLettersIndices[letter]?.let { listIndex ->
                                            coroutineScope.launch { listState.scrollToItem(listIndex) }
                                            view.performHapticFeedback(android.view.HapticFeedbackConstants.TEXT_HANDLE_MOVE)
                                        }
                                    },
                                    onDragEnd = { hoveredLetter = null },
                                    onDragCancel = { hoveredLetter = null },
                                    onDrag = { change, _ ->
                                        val y = change.position.y
                                        val itemHeight = size.height / alphabet.size.toFloat()
                                        val index = (y / itemHeight).toInt().coerceIn(0, alphabet.lastIndex)
                                        val letter = alphabet[index]
                                        if (hoveredLetter != letter) {
                                            hoveredLetter = letter
                                            firstLettersIndices[letter]?.let { listIndex ->
                                                coroutineScope.launch { listState.scrollToItem(listIndex) }
                                                view.performHapticFeedback(android.view.HapticFeedbackConstants.TEXT_HANDLE_MOVE)
                                            }
                                        }
                                    }
                                )
                            },
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.SpaceEvenly
                    ) {
                        alphabet.forEach { letter ->
                            Text(
                                text = letter.toString(),
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF16A34A),
                                modifier = Modifier
                                    .clickable {
                                        firstLettersIndices[letter]?.let { listIndex ->
                                            coroutineScope.launch { listState.scrollToItem(listIndex) }
                                            view.performHapticFeedback(android.view.HapticFeedbackConstants.KEYBOARD_TAP)
                                        }
                                    }
                                    .padding(vertical = 1.dp, horizontal = 4.dp)
                            )
                        }
                    }
                }
"""
content = content[:scroller_start] + new_scroller + content[scroller_end:]

# unique IDs for itemsIndexed
content = content.replace("itemsIndexed(filteredContacts, key = { _, it -> it.id })", "itemsIndexed(filteredContacts, key = { index, it -> \"${it.id}_${index}\" })")

with open('app/src/main/java/com/titan/zapdial/ContactsScreen.kt', 'w') as f:
    f.write(content)
