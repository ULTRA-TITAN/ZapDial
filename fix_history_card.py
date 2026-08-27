import re

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

state_insert = """    var showLongPressMenu by remember { mutableStateOf(false) }"""
new_state = """    var showLongPressMenu by remember { mutableStateOf(false) }
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
    }"""

content = content.replace(state_insert, new_state)

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)
