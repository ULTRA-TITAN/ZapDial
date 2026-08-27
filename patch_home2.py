import re

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

# Add callToConfirm
state_decl = """    var selectedHistoryContact by remember { mutableStateOf<String?>(null) }
    var callToConfirm by remember { mutableStateOf<Pair<String, String>?>(null) }"""

content = content.replace("    var selectedHistoryContact by remember { mutableStateOf<String?>(null) }", state_decl)


# Add CallConfirmationDialog call inside HomeScreen
box_start = content.find("Box(modifier = Modifier.fillMaxSize()) {")

dialog = """    callToConfirm?.let { (name, number) ->
        CallConfirmationDialog(
            name = name,
            number = number,
            onConfirm = { CallManager.makeCall(context, number) },
            onDismiss = { callToConfirm = null }
        )
    }
    
    Box"""

content = content.replace("    Box(modifier = Modifier.fillMaxSize()) {", dialog)

old_mistouch = """                                    modifier = Modifier.clickable {
                                        if (mistouchPrevention) {
                                            // Handling in ContactCard directly or CallManager
                                        } else {
                                            CallManager.makeCall(context, contact.phoneNumber)
                                        }
                                    }"""
                                    
new_mistouch = """                                    modifier = Modifier.clickable {
                                        if (mistouchPrevention) {
                                            callToConfirm = Pair(contact.name, contact.phoneNumber)
                                        } else {
                                            CallManager.makeCall(context, contact.phoneNumber)
                                        }
                                    }"""

content = content.replace(old_mistouch, new_mistouch)


with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)
