with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

content = content.replace("""@Composable
fun SpeedDialSection(contacts: List<Contact?>, onAddClick: () -> Unit, onRemove: (Contact) -> Unit) {""", """@Composable
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
""")

content = content.replace("""                    Box(modifier = Modifier.pointerInput(Unit) {
                        detectTapGestures(
                            onLongPress = { onRemove(contact) }
                        )
                    }) {""", """                    Box(modifier = Modifier.pointerInput(Unit) {
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
                    }) {""")

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
