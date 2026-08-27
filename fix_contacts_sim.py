import re

with open("app/src/main/java/com/titan/zapdial/ContactsScreen.kt", "r") as f:
    content = f.read()

# Add states for SimSelection
state_add = """
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
    }

    Scaffold(
"""
content = content.replace("    Scaffold(", state_add)

old_call = """CallManager.makeCall(context, number)"""
new_call = """CallManager.initiateCallWithSimCheck(context, number) { sims ->
                            availableSimsForCall = sims
                            showSimSelectionFor = number
                        }"""

content = content.replace(old_call, new_call)

with open("app/src/main/java/com/titan/zapdial/ContactsScreen.kt", "w") as f:
    f.write(content)
