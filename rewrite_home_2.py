with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

# For CallHistoryItemCard:
content = content.replace("""    val callPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            CallManager.makeCall(context, item.number)
        }
    }""", """    val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
    var callToConfirm by remember { mutableStateOf<String?>(null) }
    
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
    }""")

content = content.replace("""                        .clickable {
                            if (ContextCompat.checkSelfPermission(context, Manifest.permission.CALL_PHONE) == PackageManager.PERMISSION_GRANTED) {
                                CallManager.makeCall(context, item.number)
                            } else {
                                callPermissionLauncher.launch(Manifest.permission.CALL_PHONE)
                            }
                        }""", """                        .clickable {
                            if (ContextCompat.checkSelfPermission(context, Manifest.permission.CALL_PHONE) == PackageManager.PERMISSION_GRANTED) {
                                val mistouch = sharedPrefs.getBoolean("KEY_MISTOUCH_PREVENTION", false)
                                if (mistouch) callToConfirm = item.number else CallManager.makeCall(context, item.number)
                            } else {
                                callPermissionLauncher.launch(Manifest.permission.CALL_PHONE)
                            }
                        }""")

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
