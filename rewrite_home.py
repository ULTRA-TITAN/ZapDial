import re

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

# Add callToConfirm State
state_decl = """    var hasCallLogPermission by remember {
        mutableStateOf(ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CALL_LOG) == PackageManager.PERMISSION_GRANTED)
    }

    val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
    var callToConfirm by remember { mutableStateOf<Pair<String, String>?>(null) }
    
    fun attemptCall(name: String, number: String) {
        val mistouchPrevention = sharedPrefs.getBoolean("KEY_MISTOUCH_PREVENTION", false)
        if (mistouchPrevention) {
            callToConfirm = Pair(name, number)
        } else {
            CallManager.makeCall(context, number)
        }
    }
"""

content = content.replace("""    var hasCallLogPermission by remember {
        mutableStateOf(ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CALL_LOG) == PackageManager.PERMISSION_GRANTED)
    }""", state_decl)


# Add CallConfirmationDialog call inside Scaffold
scaffold_start = content.find('Scaffold(')
content = content[:scaffold_start] + """    callToConfirm?.let { (name, number) ->
        CallConfirmationDialog(
            name = name,
            number = number,
            onConfirm = { CallManager.makeCall(context, number) },
            onDismiss = { callToConfirm = null }
        )
    }\n\n    """ + content[scaffold_start:]

# Replace direct CallManager.makeCall with attemptCall in CallHistoryItemCard
# Wait, CallHistoryItemCard is a separate composable!
# It doesn't have access to attemptCall.
# Let's modify CallHistoryItemCard to do it internally.
