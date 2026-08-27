import re

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

# Add imports
imports_to_add = """
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material.icons.filled.Delete
import android.content.ClipboardManager
import android.content.ClipData
import android.widget.Toast
"""
content = re.sub(r'import androidx\.compose\.material\.icons\.filled\.Mic', imports_to_add.strip() + '\nimport androidx.compose.material.icons.filled.Mic', content)

# 1. Replace hiddenFavorites with favoriteNumbers
content = content.replace(
    "val hiddenFavorites = remember { mutableStateListOf<String>() }",
    "val favoriteNumbers = remember { mutableStateListOf<String>() }"
)
content = content.replace(
    "val hidden = sharedPrefs.getStringSet(\"KEY_HIDDEN_FAVORITES\", emptySet()) ?: emptySet()\n        hiddenFavorites.addAll(hidden)",
    "val favs = sharedPrefs.getStringSet(\"KEY_FAVORITES\", emptySet()) ?: emptySet()\n        favoriteNumbers.addAll(favs)"
)

# 2. Add launchers to HomeScreen (around line 147)
launchers_str = """
    val voiceSearchLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == android.app.Activity.RESULT_OK) {
            val matches = result.data?.getStringArrayListExtra(android.speech.RecognizerIntent.EXTRA_RESULTS)
            if (!matches.isNullOrEmpty()) {
                searchQuery = matches[0]
            }
        }
    }
    
    val audioPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            val intent = Intent(android.speech.RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(android.speech.RecognizerIntent.EXTRA_LANGUAGE_MODEL, android.speech.RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            }
            try { voiceSearchLauncher.launch(intent) } catch (e: Exception) {}
        }
    }

    LaunchedEffect(hasCallLogPermission, allContacts) {
"""
content = content.replace("    LaunchedEffect(hasCallLogPermission, allContacts) {", launchers_str)

# 3. Fix SearchBar basic padding
content = content.replace(
    "modifier = Modifier.fillMaxWidth().padding(start = if (searchQuery.isEmpty()) 0.dp else 32.dp)",
    "modifier = Modifier.fillMaxWidth().padding(start = 32.dp)"
)

# 4. Fix voice search icon button
old_mic_button = """IconButton(onClick = {
                        val intent = Intent(android.speech.RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                            putExtra(android.speech.RecognizerIntent.EXTRA_LANGUAGE_MODEL, android.speech.RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                        }
                        try { context.startActivity(intent) } catch (e: Exception) {}
                    }) {"""

new_mic_button = """IconButton(onClick = {
                        if (ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                            val intent = Intent(android.speech.RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                                putExtra(android.speech.RecognizerIntent.EXTRA_LANGUAGE_MODEL, android.speech.RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                            }
                            try { voiceSearchLauncher.launch(intent) } catch (e: Exception) {}
                        } else {
                            audioPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                        }
                    }) {"""
content = content.replace(old_mic_button, new_mic_button)

# 5. Replace Favorites section
favorites_old = """
            if (showFrequentContacts) {
                item {
                    val frequent = allContacts.filter { !hiddenFavorites.contains(it.phoneNumber) }.take(3)
                    if (frequent.isNotEmpty()) {
                        LazyRow(
                            horizontalArrangement = Arrangement.spacedBy(16.dp),
                            contentPadding = PaddingValues(start = 8.dp, top = 0.dp, end = 8.dp, bottom = 16.dp)
                        ) {
                            items(frequent) { contact ->
                                Column(
                                    horizontalAlignment = Alignment.CenterHorizontally,
                                    modifier = Modifier.combinedClickable(
                                        onClick = {
                                            if (mistouchPrevention) {
                                                callToConfirm = Pair(contact.name, contact.phoneNumber)
                                            } else {
                                                CallManager.makeCall(context, contact.phoneNumber)
                                            }
                                        },
                                        onLongClick = {
                                            hiddenFavorites.add(contact.phoneNumber)
                                            sharedPrefs.edit().putStringSet("KEY_HIDDEN_FAVORITES", hiddenFavorites.toSet()).apply()
                                            view.performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)
                                        }
                                    )
                                ) {
                                    Avatar(name = contact.name, size = 56.dp)
                                    Spacer(modifier = Modifier.height(8.dp))
                                    Text(
                                        text = contact.name.split(" ").firstOrNull() ?: "",
                                        fontSize = 13.sp,
                                        fontWeight = FontWeight.Medium,
                                        color = TextPrimary,
                                        maxLines = 1,
                                        overflow = TextOverflow.Ellipsis
                                    )
                                }
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
                                        modifier = Modifier.size(56.dp).clip(CircleShape).background(Color.White).border(1.dp, Color(0xFFE2E8F0), CircleShape)
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
                    } else {
                        Text(
                            text = "No favorites yet.",
                            fontSize = 14.sp,
                            color = TextSecondary,
                            modifier = Modifier.padding(start = 8.dp, top = 0.dp, end = 8.dp, bottom = 16.dp)
                        )
                    }
                }
            }
"""

favorites_new = """
            if (showFrequentContacts) {
                item {
                    var showContactPicker by remember { mutableStateOf(false) }
                    if (showContactPicker) {
                        ModalBottomSheet(onDismissRequest = { showContactPicker = false }, containerColor = PageBackground) {
                            LazyColumn(modifier = Modifier.fillMaxWidth().padding(16.dp).padding(bottom = 32.dp)) {
                                item {
                                    Text("Select a Favorite", fontSize = 20.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 16.dp))
                                }
                                items(allContacts) { contact ->
                                    Row(modifier = Modifier.fillMaxWidth().clickable {
                                        if (!favoriteNumbers.contains(contact.phoneNumber)) {
                                            favoriteNumbers.add(contact.phoneNumber)
                                            sharedPrefs.edit().putStringSet("KEY_FAVORITES", favoriteNumbers.toSet()).apply()
                                        }
                                        showContactPicker = false
                                    }.padding(vertical = 12.dp), verticalAlignment = Alignment.CenterVertically) {
                                        Avatar(name = contact.name, size = 40.dp)
                                        Spacer(modifier = Modifier.width(16.dp))
                                        Text(contact.name, fontSize = 16.sp)
                                    }
                                }
                            }
                        }
                    }
                    
                    val frequent = allContacts.filter { favoriteNumbers.contains(it.phoneNumber) }.take(3)
                    
                    LazyRow(
                        horizontalArrangement = Arrangement.spacedBy(16.dp),
                        contentPadding = PaddingValues(start = 8.dp, top = 0.dp, end = 8.dp, bottom = 16.dp)
                    ) {
                        items(frequent) { contact ->
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally,
                                modifier = Modifier.combinedClickable(
                                    onClick = {
                                        if (mistouchPrevention) {
                                            callToConfirm = Pair(contact.name, contact.phoneNumber)
                                        } else {
                                            CallManager.makeCall(context, contact.phoneNumber)
                                        }
                                    },
                                    onLongClick = {
                                        favoriteNumbers.remove(contact.phoneNumber)
                                        sharedPrefs.edit().putStringSet("KEY_FAVORITES", favoriteNumbers.toSet()).apply()
                                        view.performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)
                                    }
                                )
                            ) {
                                Avatar(name = contact.name, size = 56.dp)
                                Spacer(modifier = Modifier.height(8.dp))
                                Text(
                                    text = contact.name.split(" ").firstOrNull() ?: "",
                                    fontSize = 13.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = TextPrimary,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis
                                )
                            }
                        }
                        if (frequent.size < 3) {
                            item {
                                Column(
                                    horizontalAlignment = Alignment.CenterHorizontally,
                                    modifier = Modifier.clickable {
                                        showContactPicker = true
                                    }
                                ) {
                                    Box(
                                        contentAlignment = Alignment.Center,
                                        modifier = Modifier.size(56.dp).clip(CircleShape).background(Color.White).border(1.dp, Color(0xFFE2E8F0), CircleShape)
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
                    }
                }
            }
"""
content = content.replace(favorites_old.strip(), favorites_new.strip())

# 6. Fix CallHistoryItemCard
long_press_old = """
                    onLongPress = { 
                        view.performHapticFeedback(android.view.HapticFeedbackConstants.LONG_PRESS)
                        onDelete(item)
                    }
"""
long_press_new = """
                    onLongPress = { 
                        view.performHapticFeedback(android.view.HapticFeedbackConstants.LONG_PRESS)
                        showLongPressMenu = true
                    }
"""

content = content.replace(long_press_old, long_press_new)

# Add showLongPressMenu state
call_card_state_old = """
    var expanded by remember { mutableStateOf(false) }
    var callToConfirm by remember { mutableStateOf<String?>(null) }
"""
call_card_state_new = """
    var expanded by remember { mutableStateOf(false) }
    var callToConfirm by remember { mutableStateOf<String?>(null) }
    var showLongPressMenu by remember { mutableStateOf(false) }
"""
content = content.replace(call_card_state_old, call_card_state_new)

# Add bottom sheet for long press menu
menu_bs = """
    if (showLongPressMenu) {
        ModalBottomSheet(
            onDismissRequest = { showLongPressMenu = false },
            containerColor = PlateBackground
        ) {
            Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth().clickable {
                        val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
                        val clip = android.content.ClipData.newPlainText("Phone Number", item.number)
                        clipboard.setPrimaryClip(clip)
                        android.widget.Toast.makeText(context, "Copied to clipboard", android.widget.Toast.LENGTH_SHORT).show()
                        showLongPressMenu = false
                    }.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.ContentCopy, contentDescription = "Copy")
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Copy Phone Number", fontSize = 16.sp)
                }
                Row(
                    modifier = Modifier.fillMaxWidth().clickable {
                        onDelete(item)
                        showLongPressMenu = false
                    }.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.Delete, contentDescription = "Delete", tint = Color.Red)
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Delete Call Log", fontSize = 16.sp, color = Color.Red)
                }
                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }
}

@Composable
fun Avatar(name: String?, size: androidx.compose.ui.unit.Dp = 40.dp) {
"""

content = content.replace("}\n\n@Composable\nfun Avatar(name: String?, size: androidx.compose.ui.unit.Dp = 40.dp) {", menu_bs)

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)

print("HomeScreen updated!")
