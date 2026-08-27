import re

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

frequent_pattern = re.compile(r'        item \{\n            androidx\.compose\.animation\.AnimatedVisibility\(visible = showFrequentContacts\) \{\n                Column \{\n                    SpeedDialSection\([\s\S]*?Spacer\(modifier = Modifier\.height\(32\.dp\)\)\n                \}\n            \}\n        \}')

frequent_replacement = """        if (showFrequentContacts) {
            item {
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
content = frequent_pattern.sub(frequent_replacement, content)

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
