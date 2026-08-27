import re

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
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

old_call = """CallManager.makeCall(context, contact.phoneNumber)"""
new_call = """CallManager.initiateCallWithSimCheck(context, contact.phoneNumber) { sims ->
                                            availableSimsForCall = sims
                                            showSimSelectionFor = contact.phoneNumber
                                        }"""

content = content.replace(old_call, new_call)

old_call2 = """CallManager.makeCall(context, item.number)"""
new_call2 = """CallManager.initiateCallWithSimCheck(context, item.number) { sims ->
                                                    availableSimsForCall = sims
                                                    showSimSelectionFor = item.number
                                                }"""

content = content.replace(old_call2, new_call2)

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)
