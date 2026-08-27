import re

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

# Add state to HomeScreen
state_new = """    val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
    var showFrequentContacts by remember {
        mutableStateOf(sharedPrefs.getBoolean("KEY_SHOW_FREQUENT_CONTACTS", true))
    }
"""

content = content.replace("    var hasCallLogPermission by remember {", state_new + "    var hasCallLogPermission by remember {")

# Wrap SpeedDialSection
speed_old = """        item {
            SpeedDialSection(
                contacts = speedDialContacts,
                onAddClick = { showContactPicker = true },
                onRemove = { contact ->
                    val prefs = context.getSharedPreferences("zapdial_prefs", Context.MODE_PRIVATE)
                    val currentSet = prefs.getStringSet("favorites", emptySet())?.toMutableSet() ?: mutableSetOf()
                    currentSet.remove(contact.phoneNumber)
                    prefs.edit().putStringSet("favorites", currentSet).apply()
                    
                    val updatedFavorites = speedDialContacts.filterNotNull().filter { it.phoneNumber != contact.phoneNumber }.toMutableList<Contact?>()
                    while (updatedFavorites.size < 5) updatedFavorites.add(null)
                    speedDialContacts = updatedFavorites
                }
            )
            Spacer(modifier = Modifier.height(32.dp))
        }"""
        
speed_new = """        item {
            androidx.compose.animation.AnimatedVisibility(visible = showFrequentContacts) {
                Column {
                    SpeedDialSection(
                        contacts = speedDialContacts,
                        onAddClick = { showContactPicker = true },
                        onRemove = { contact ->
                            val prefs = context.getSharedPreferences("zapdial_prefs", Context.MODE_PRIVATE)
                            val currentSet = prefs.getStringSet("favorites", emptySet())?.toMutableSet() ?: mutableSetOf()
                            currentSet.remove(contact.phoneNumber)
                            prefs.edit().putStringSet("favorites", currentSet).apply()
                            
                            val updatedFavorites = speedDialContacts.filterNotNull().filter { it.phoneNumber != contact.phoneNumber }.toMutableList<Contact?>()
                            while (updatedFavorites.size < 5) updatedFavorites.add(null)
                            speedDialContacts = updatedFavorites
                        }
                    )
                    Spacer(modifier = Modifier.height(32.dp))
                }
            }
        }"""

content = content.replace(speed_old, speed_new)

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
