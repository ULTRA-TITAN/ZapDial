import re

with open("app/src/main/java/com/titan/zapdial/ContactsScreen.kt", "r") as f:
    content = f.read()

state_insert = """    var callToConfirm by remember { mutableStateOf<String?>(null) }"""
new_state = """    var callToConfirm by remember { mutableStateOf<String?>(null) }
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

old_call = """CallManager.makeCall(context, contact.phoneNumber)"""
new_call = """CallManager.initiateCallWithSimCheck(context, contact.phoneNumber) { sims ->
                availableSimsForCall = sims
                showSimSelectionFor = contact.phoneNumber
            }"""
content = content.replace(old_call, new_call)

old_call_confirm = """CallManager.makeCall(context, num)"""
new_call_confirm = """CallManager.initiateCallWithSimCheck(context, num) { sims ->
                availableSimsForCall = sims
                showSimSelectionFor = num
            }"""
content = content.replace(old_call_confirm, new_call_confirm)

with open("app/src/main/java/com/titan/zapdial/ContactsScreen.kt", "w") as f:
    f.write(content)
