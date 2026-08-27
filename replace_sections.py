import re

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

# Replace SearchBarSection
search_pattern = re.compile(r'@Composable\nfun SearchBarSection\(.*?\n\n    Row\(.*?\n    \}\n\}', re.DOTALL)
search_new = """@Composable
fun SearchBarSection(
    query: String,
    onQueryChange: (String) -> Unit,
    onSettingsClick: () -> Unit
) {
    val context = LocalContext.current
    val speechRecognizerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            val matches = result.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            if (!matches.isNullOrEmpty()) {
                onQueryChange(matches[0])
            }
        }
    }

    val recordAudioPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            }
            try {
                speechRecognizerLauncher.launch(intent)
            } catch (e: Exception) {}
        }
    }

    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .fillMaxWidth()
            .height(56.dp)
            .background(ColorPureWhite, RoundedCornerShape(50))
            .androidx.compose.foundation.border(1.dp, ColorBorderGray, RoundedCornerShape(50))
            .padding(horizontal = 16.dp)
    ) {
        IconButton(onClick = onSettingsClick, modifier = Modifier.size(36.dp)) {
            Icon(imageVector = Icons.Default.Settings, contentDescription = "Settings", tint = ColorSlateGray)
        }
        
        Spacer(modifier = Modifier.width(12.dp))

        Box(modifier = Modifier.weight(1f)) {
            if (query.isEmpty()) {
                Text(text = "Search contacts", fontSize = 16.sp, color = ColorSlateGray)
            }
            BasicTextField(
                value = query,
                onValueChange = onQueryChange,
                textStyle = TextStyle(color = ColorPureBlack, fontSize = 16.sp, fontWeight = FontWeight.Normal),
                singleLine = true,
                cursorBrush = SolidColor(ColorPureBlack),
                modifier = Modifier.fillMaxWidth()
            )
        }

        Spacer(modifier = Modifier.width(12.dp))

        IconButton(
            onClick = {
                if (ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                    val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                        putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                    }
                    try {
                        speechRecognizerLauncher.launch(intent)
                    } catch (e: Exception) {}
                } else {
                    recordAudioPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                }
            },
            modifier = Modifier.size(36.dp)
        ) {
            Icon(imageVector = Icons.Default.Mic, contentDescription = "Voice Search", tint = ColorSlateGray)
        }
    }
}"""
content = search_pattern.sub(search_new, content)

# Replace SpeedDialSection
speed_pattern = re.compile(r'@Composable\nfun SpeedDialSection.*?\}\n    \}\n\}', re.DOTALL)
speed_new = """@Composable
fun SpeedDialSection(contacts: List<Contact?>, onAddClick: () -> Unit, onRemove: (Contact) -> Unit) {
    val context = LocalContext.current
    val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
    var callToConfirm by remember { mutableStateOf<Contact?>(null) }
    
    val callPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            val mistouch = sharedPrefs.getBoolean("KEY_MISTOUCH_PREVENTION", false)
            callToConfirm?.let { contact ->
                if (mistouch) {
                    // dialog will show
                } else {
                    CallManager.makeCall(context, contact.phoneNumber)
                    callToConfirm = null
                }
            }
        }
    }
    
    callToConfirm?.let { contact ->
        val mistouch = sharedPrefs.getBoolean("KEY_MISTOUCH_PREVENTION", false)
        if (mistouch) {
            CallConfirmationDialog(
                name = contact.name,
                number = contact.phoneNumber,
                onConfirm = { CallManager.makeCall(context, contact.phoneNumber) },
                onDismiss = { callToConfirm = null }
            )
        }
    }

    LazyRow(
        horizontalArrangement = Arrangement.spacedBy(20.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        items(contacts) { contact ->
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier.width(64.dp)
            ) {
                if (contact != null) {
                    Box(modifier = Modifier.pointerInput(Unit) {
                        detectTapGestures(
                            onTap = {
                                if (ContextCompat.checkSelfPermission(context, Manifest.permission.CALL_PHONE) == PackageManager.PERMISSION_GRANTED) {
                                    val mistouch = sharedPrefs.getBoolean("KEY_MISTOUCH_PREVENTION", false)
                                    if (mistouch) callToConfirm = contact else CallManager.makeCall(context, contact.phoneNumber)
                                } else {
                                    callToConfirm = contact
                                    callPermissionLauncher.launch(Manifest.permission.CALL_PHONE)
                                }
                            },
                            onLongPress = { onRemove(contact) }
                        )
                    }) {
                        Avatar(name = contact.name, size = 64.dp)
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = contact.name.split(" ").first(),
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium,
                        color = ColorPureBlack,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                } else {
                    Box(
                        contentAlignment = Alignment.Center,
                        modifier = Modifier
                            .size(64.dp)
                            .clip(CircleShape)
                            .background(ColorPureWhite)
                            .androidx.compose.foundation.border(1.dp, ColorBorderGray, CircleShape)
                            .clickable(onClick = onAddClick)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Add,
                            contentDescription = "Add Favorite",
                            tint = ColorSlateGray,
                            modifier = Modifier.size(28.dp)
                        )
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Add",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium,
                        color = ColorSlateGray
                    )
                }
            }
        }
    }
}"""
content = speed_pattern.sub(speed_new, content)

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
