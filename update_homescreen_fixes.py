import re

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

# 1. Add withContext import
if "import kotlinx.coroutines.withContext" not in content:
    content = content.replace("import kotlinx.coroutines.launch", "import kotlinx.coroutines.launch\nimport kotlinx.coroutines.withContext")

# 2. Fix CallConfirmationDialog in HomeScreen
old_confirm = """    callToConfirm?.let { (name, number) ->
        CallConfirmationDialog(
            name = name,
            number = number,
            onConfirm = { CallManager.makeCall(context, number) },
            onDismiss = { callToConfirm = null }
        )
    }"""
new_confirm = """    callToConfirm?.let { (name, number) ->
        CallConfirmationDialog(
            name = name,
            number = number,
            onConfirm = { 
                CallManager.initiateCallWithSimCheck(context, number) { sims -> 
                    availableSimsForCall = sims
                    showSimSelectionFor = number 
                } 
            },
            onDismiss = { callToConfirm = null }
        )
    }"""
content = content.replace(old_confirm, new_confirm)

# 3. Add withContext(Dispatchers.IO) to CallLogFetcher & ContactFetcher
old_call_log_launcher = """        if (isGranted) {
            coroutineScope.launch {
                callHistory = CallLogFetcher.fetchCallHistory(context, defaultLocation, allContacts)
            }
        }"""
new_call_log_launcher = """        if (isGranted) {
            coroutineScope.launch {
                val history = withContext(Dispatchers.IO) {
                    CallLogFetcher.fetchCallHistory(context, defaultLocation, allContacts)
                }
                callHistory = history
            }
        }"""
content = content.replace(old_call_log_launcher, new_call_log_launcher)

old_launched_effect_1 = """    LaunchedEffect(hasCallLogPermission, allContacts) {

        if (hasCallLogPermission) {
            callHistory = CallLogFetcher.fetchCallHistory(context, defaultLocation, allContacts)
        }
    }"""
new_launched_effect_1 = """    LaunchedEffect(hasCallLogPermission, allContacts) {
        if (hasCallLogPermission) {
            val history = withContext(Dispatchers.IO) {
                CallLogFetcher.fetchCallHistory(context, defaultLocation, allContacts)
            }
            callHistory = history
        }
    }"""
content = content.replace(old_launched_effect_1, new_launched_effect_1)

old_launched_effect_2 = """    LaunchedEffect(Unit) {
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CONTACTS) == PackageManager.PERMISSION_GRANTED) {
            allContacts = ContactFetcher.fetchContacts(context)
        }
    }"""
new_launched_effect_2 = """    LaunchedEffect(Unit) {
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CONTACTS) == PackageManager.PERMISSION_GRANTED) {
            val contacts = withContext(Dispatchers.IO) {
                ContactFetcher.fetchContacts(context)
            }
            allContacts = contacts
        }
    }"""
content = content.replace(old_launched_effect_2, new_launched_effect_2)

# 4. Replace pointerInput with combinedClickable in CallHistoryItemCard
old_pointer_input = """        modifier = Modifier
            .fillMaxWidth()
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = { expanded = !expanded },
                    onLongPress = { 
                        view.performHapticFeedback(android.view.HapticFeedbackConstants.LONG_PRESS)
                        showLongPressMenu = true
                    }
                )
            }"""
new_combined_clickable = """        modifier = Modifier
            .fillMaxWidth()
            .combinedClickable(
                onClick = { expanded = !expanded },
                onLongClick = { 
                    view.performHapticFeedback(android.view.HapticFeedbackConstants.LONG_PRESS)
                    showLongPressMenu = true
                }
            )"""
content = content.replace(old_pointer_input, new_combined_clickable)

# 5. Fix Experimental annotations
content = content.replace("@androidx.compose.material3.ExperimentalMaterial3Api\n@Composable\nfun CallHistoryItemCard", 
                          "@androidx.compose.material3.ExperimentalMaterial3Api\n@androidx.compose.foundation.ExperimentalFoundationApi\n@Composable\nfun CallHistoryItemCard")

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)

