import re

def add_state(filename):
    with open(filename, "r") as f:
        content = f.read()

    state = """    var showSimSelectionFor by remember { mutableStateOf<String?>(null) }
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
"""

    if "var showSimSelectionFor" not in content:
        # replace the first instance of `val context = LocalContext.current`
        content = content.replace("val context = LocalContext.current", "val context = LocalContext.current\n" + state, 1)

    with open(filename, "w") as f:
        f.write(content)

add_state("app/src/main/java/com/titan/zapdial/HomeScreen.kt")
add_state("app/src/main/java/com/titan/zapdial/ContactsScreen.kt")
add_state("app/src/main/java/com/titan/zapdial/DialPadScreen.kt")
