import re

with open("/app/applet/app/src/main/java/com/titan/zapdial/ContactsScreen.kt", "r") as f:
    content = f.read()

# Replace the synchronous directory calculation with asynchronous
old_directory_calc = """    val directory = remember(allContacts) {
        val map = mutableMapOf<Char, MutableList<Contact>>()
        allContacts.forEach { contact ->
            val firstChar = contact.name.firstOrNull()?.uppercaseChar() ?: '#'
            val key = if (firstChar in LETTERS) firstChar else '#'
            map.getOrPut(key) { mutableListOf() }.add(contact)
        }
        map.mapValues { it.value.sortedBy { c -> c.name } }
    }"""

new_directory_calc = """    var directory by remember { mutableStateOf<Map<Char, List<Contact>>>(emptyMap()) }
    var selectedFilter by remember { mutableStateOf("All") }

    LaunchedEffect(allContacts, selectedFilter) {
        withContext(Dispatchers.Default) {
            val map = mutableMapOf<Char, MutableList<Contact>>()
            val filtered = allContacts.filter { 
                when (selectedFilter) {
                    "SIM 1" -> it.accountName?.contains("SIM", true) == true
                    "Google" -> it.accountName?.contains("Google", true) == true || it.accountName?.contains("@", true) == true
                    else -> true
                }
            }
            filtered.forEach { contact ->
                val firstChar = contact.name.firstOrNull()?.uppercaseChar() ?: '#'
                val key = if (firstChar in LETTERS) firstChar else '#'
                map.getOrPut(key) { mutableListOf() }.add(contact)
            }
            directory = map.mapValues { it.value.sortedBy { c -> c.name } }
        }
    }"""

content = content.replace(old_directory_calc, new_directory_calc)

# Remove the inline var selectedFilter since we moved it up
content = re.sub(r'var selectedFilter by remember \{ mutableStateOf\("All"\) \}', '', content)

# Fix items(rows) missing key
content = content.replace("items(rows) { row ->", "items(rows, key = { row -> if (row is DirectoryRow.Header) \"H_${row.letter}\" else \"I_${(row as DirectoryRow.Item).contact.id}\" }) { row ->")

# Fix drag animation allocations
old_drag_handlers = """    fun onDragAt(yInContainer: Float) {
        val relY = (yInContainer - railTopPx).coerceIn(0f, railHeightPx)
        val ratio = (relY / railHeightPx).coerceIn(0f, 1f)
        val idx = (ratio * (LETTERS.size - 1)).toInt().coerceIn(0, LETTERS.size - 1)
        currentLetter = idx
        scope.launch { bubbleY.snapTo(yInContainer) }
        scope.launch { bubbleScale.animateTo(1f, tween(180)) }
        scope.launch { bubbleOpacity.animateTo(1f, tween(120)) }
        scope.launch { stemWidth.animateTo(extendedStemWidth, tween(140)) }
        val letter = LETTERS[idx]
        if (letter != lastSnappedLetter) {
            lastSnappedLetter = letter
            haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
            scope.launch { snapToLetter(letter) }
        }
    }

    fun onDragEnd() {
        val overshoot = CubicBezierEasing(0.6f, -0.1f, 0.75f, 0.15f)
        scope.launch { bubbleOpacity.animateTo(0f, tween(280)) }
        scope.launch { bubbleScale.animateTo(0.2f, tween(300, easing = overshoot)) }
        scope.launch { stemWidth.animateTo(0f, tween(260, easing = overshoot)) }
        currentLetter = -1
        lastSnappedLetter = null
    }"""

new_drag_handlers = """    var isDragging by remember { mutableStateOf(false) }
    var bubbleYRaw by remember { mutableFloatStateOf(0f) }

    val bubbleScale by androidx.compose.animation.core.animateFloatAsState(if (isDragging) 1f else 0.2f, tween(if(isDragging) 180 else 300, easing = if(isDragging) FastOutSlowInEasing else CubicBezierEasing(0.6f, -0.1f, 0.75f, 0.15f)))
    val bubbleOpacity by androidx.compose.animation.core.animateFloatAsState(if (isDragging) 1f else 0f, tween(if(isDragging) 120 else 280))
    val stemWidthState by androidx.compose.animation.core.animateFloatAsState(if (isDragging) extendedStemWidth else 0f, tween(if(isDragging) 140 else 260, easing = if(isDragging) FastOutSlowInEasing else CubicBezierEasing(0.6f, -0.1f, 0.75f, 0.15f)))

    fun onDragAt(yInContainer: Float) {
        isDragging = true
        bubbleYRaw = yInContainer
        val relY = (yInContainer - railTopPx).coerceIn(0f, railHeightPx)
        val ratio = (relY / railHeightPx).coerceIn(0f, 1f)
        val idx = (ratio * (LETTERS.size - 1)).toInt().coerceIn(0, LETTERS.size - 1)
        currentLetter = idx
        val letter = LETTERS[idx]
        if (letter != lastSnappedLetter) {
            lastSnappedLetter = letter
            haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
            scope.launch { snapToLetter(letter) }
        }
    }

    fun onDragEnd() {
        isDragging = false
        currentLetter = -1
        lastSnappedLetter = null
    }"""

content = content.replace(old_drag_handlers, new_drag_handlers)

# Replace Animatable declarations since we use animateFloatAsState now
content = content.replace("val bubbleY = remember { Animatable(0f) }", "")
content = content.replace("val bubbleScale = remember { Animatable(0.2f) }", "")
content = content.replace("val bubbleOpacity = remember { Animatable(0f) }", "")
content = content.replace("val stemWidth = remember { Animatable(0f) }", "")

# Replace usage
content = content.replace("bubbleY.value", "bubbleYRaw")
content = content.replace("bubbleScale.value", "bubbleScale")
content = content.replace("bubbleOpacity.value", "bubbleOpacity")
content = content.replace("stemWidth.value", "stemWidthState")

# Add History and Block to BottomSheet
old_bottom_sheet = """                Row(
                    modifier = Modifier.fillMaxWidth().clickable {
                        try {
                            val uri = android.content.ContentUris.withAppendedId(android.provider.ContactsContract.Contacts.CONTENT_URI, contactId.toLong())
                            context.contentResolver.delete(uri, null, null)
                            scope.launch {
                                allContacts = ContactFetcher.fetchContacts(context)
                            }
                        } catch (e: Exception) {}
                        showContactOptionsFor = null
                    }.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    androidx.compose.material3.Icon(androidx.compose.material.icons.Icons.Default.Delete, contentDescription = "Delete", tint = Color.Red)
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Delete Contact", fontSize = 16.sp, color = Color.Red)
                }
                Spacer(modifier = Modifier.height(32.dp))"""

new_bottom_sheet = """                Row(
                    modifier = Modifier.fillMaxWidth().clickable {
                        try {
                            val uri = android.content.ContentUris.withAppendedId(android.provider.ContactsContract.Contacts.CONTENT_URI, contactId.toLong())
                            context.contentResolver.delete(uri, null, null)
                            scope.launch {
                                allContacts = ContactFetcher.fetchContacts(context)
                            }
                        } catch (e: Exception) {}
                        showContactOptionsFor = null
                    }.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    androidx.compose.material3.Icon(androidx.compose.material.icons.Icons.Default.Delete, contentDescription = "Delete", tint = Color.Red)
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Delete Contact", fontSize = 16.sp, color = Color.Red)
                }
                Row(
                    modifier = Modifier.fillMaxWidth().clickable {
                        scope.launch(Dispatchers.IO) {
                            val prefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
                            val blocked = prefs.getStringSet("KEY_BLOCKED_NUMBERS", emptySet())?.toMutableSet() ?: mutableSetOf()
                            blocked.add(number)
                            prefs.edit().putStringSet("KEY_BLOCKED_NUMBERS", blocked).commit()
                        }
                        android.widget.Toast.makeText(context, "Contact Blocked", android.widget.Toast.LENGTH_SHORT).show()
                        showContactOptionsFor = null
                    }.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    androidx.compose.material3.Icon(androidx.compose.material.icons.Icons.Default.Block, contentDescription = "Block", tint = Color.Red)
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Block Contact", fontSize = 16.sp, color = Color.Red)
                }
                Row(
                    modifier = Modifier.fillMaxWidth().clickable {
                        val intent = android.content.Intent(android.content.Intent.ACTION_VIEW).apply {
                            type = android.provider.CallLog.Calls.CONTENT_TYPE
                            putExtra(android.provider.CallLog.Calls.EXTRA_CALL_TYPE_FILTER, android.provider.CallLog.Calls.INCOMING_TYPE)
                        }
                        try { context.startActivity(intent) } catch (e: Exception) { android.widget.Toast.makeText(context, "Action unavailable", android.widget.Toast.LENGTH_SHORT).show() }
                        showContactOptionsFor = null
                    }.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    androidx.compose.material3.Icon(androidx.compose.material.icons.Icons.Default.History, contentDescription = "History")
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("View History", fontSize = 16.sp, color = TextPrimary)
                }
                Spacer(modifier = Modifier.height(32.dp))"""

content = content.replace(old_bottom_sheet, new_bottom_sheet)

with open("/app/applet/app/src/main/java/com/titan/zapdial/ContactsScreen.kt", "w") as f:
    f.write(content)

