with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

# Add ExperimentalFoundationApi for CombinedClickable
if "import androidx.compose.foundation.ExperimentalFoundationApi" not in content:
    content = content.replace("import androidx.compose.foundation.background", "import androidx.compose.foundation.background\nimport androidx.compose.foundation.ExperimentalFoundationApi\nimport androidx.compose.foundation.combinedClickable\nimport androidx.compose.ui.hapticfeedback.HapticFeedbackConstants")
    
if "@OptIn(ExperimentalMaterial3Api::class)" in content:
    content = content.replace("@OptIn(ExperimentalMaterial3Api::class)", "@OptIn(ExperimentalMaterial3Api::class, ExperimentalFoundationApi::class)")

old_frequent = """            if (showFrequentContacts) {
                item {
                    val frequent = allContacts.take(3)"""
                    
new_frequent = """            if (searchQuery.isNotEmpty()) {
                val searchResults = allContacts.filter {
                    it.name.contains(searchQuery, ignoreCase = true) || it.phoneNumber.contains(searchQuery)
                }
                
                if (searchResults.isEmpty()) {
                    item {
                        Text(
                            text = "No contacts found.",
                            fontSize = 14.sp,
                            color = TextSecondary,
                            modifier = Modifier.padding(16.dp)
                        )
                    }
                } else {
                    items(searchResults) { contact ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable {
                                    if (mistouchPrevention) {
                                        callToConfirm = Pair(contact.name, contact.phoneNumber)
                                    } else {
                                        CallManager.makeCall(context, contact.phoneNumber)
                                    }
                                }
                                .padding(vertical = 12.dp, horizontal = 8.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Avatar(name = contact.name, size = 50.dp)
                            Spacer(modifier = Modifier.width(16.dp))
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = contact.name,
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = TextPrimary
                                )
                                Spacer(modifier = Modifier.height(2.dp))
                                Text(
                                    text = contact.phoneNumber,
                                    fontSize = 14.sp,
                                    color = TextSecondary
                                )
                            }
                        }
                    }
                }
            } else {
            
            if (showFrequentContacts) {
                item {
                    val frequent = allContacts.filter { it.phoneNumber not in hiddenFavorites }.take(3)"""

content = content.replace(old_frequent, new_frequent)


old_clickable = """                                Column(
                                    horizontalAlignment = Alignment.CenterHorizontally,
                                    modifier = Modifier.clickable {
                                        if (mistouchPrevention) {
                                            callToConfirm = Pair(contact.name, contact.phoneNumber)
                                        } else {
                                            CallManager.makeCall(context, contact.phoneNumber)
                                        }
                                    }
                                ) {"""
                                
new_clickable = """                                Column(
                                    horizontalAlignment = Alignment.CenterHorizontally,
                                    modifier = Modifier.combinedClickable(
                                        onClick = {
                                            if (mistouchPrevention) {
                                                callToConfirm = Pair(contact.name, contact.phoneNumber)
                                            } else {
                                                CallManager.makeCall(context, contact.phoneNumber)
                                            }
                                        },
                                        onLongClick = {
                                            hiddenFavorites.add(contact.phoneNumber)
                                            sharedPrefs.edit().putStringSet("KEY_HIDDEN_FAVORITES", hiddenFavorites.toSet()).apply()
                                            view.performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)
                                        }
                                    )
                                ) {"""

content = content.replace(old_clickable, new_clickable)

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)
