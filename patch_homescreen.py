import re

with open("/app/applet/app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

# Fix LazyColumn keys in HomeScreen
content = content.replace("items(allContacts) { contact ->", "items(allContacts, key = { it.id }) { contact ->")
content = content.replace("items(matchingCalls) { call ->", "items(matchingCalls, key = { it.id }) { call ->")

# Fix sharedPrefs synchronous loading to asynchronous
old_mistouch = """    var mistouchPrevention by remember {
        mutableStateOf(sharedPrefs.getBoolean("KEY_MISTOUCH_PREVENTION", false))
    }
    var callHistory by remember { mutableStateOf<List<HomeCallItem>>(emptyList()) }"""

new_mistouch = """    var mistouchPrevention by remember { mutableStateOf(false) }
    var callHistory by remember { mutableStateOf<List<HomeCallItem>>(emptyList()) }

    LaunchedEffect(Unit) {
        withContext(Dispatchers.IO) {
            mistouchPrevention = sharedPrefs.getBoolean("KEY_MISTOUCH_PREVENTION", false)
        }
    }"""

content = content.replace(old_mistouch, new_mistouch)

old_frequent = """    var showFrequentContacts by remember {
        mutableStateOf(sharedPrefs.getBoolean("KEY_SHOW_FREQUENT", true))
    }"""

new_frequent = """    var showFrequentContacts by remember { mutableStateOf(true) }
    LaunchedEffect(Unit) {
        withContext(Dispatchers.IO) {
            showFrequentContacts = sharedPrefs.getBoolean("KEY_SHOW_FREQUENT", true)
        }
    }"""

content = content.replace(old_frequent, new_frequent)

# Fix Favorite saving to be on IO thread (prevent main thread block)
old_fav_save = """                                        if (!favoriteNumbers.contains(contact.phoneNumber)) {
                                            favoriteNumbers.add(contact.phoneNumber)
                                            sharedPrefs.edit().putStringSet("KEY_FAVORITES", favoriteNumbers.toSet()).apply()
                                        }"""

new_fav_save = """                                        if (!favoriteNumbers.contains(contact.phoneNumber)) {
                                            favoriteNumbers.add(contact.phoneNumber)
                                            coroutineScope.launch(Dispatchers.IO) {
                                                sharedPrefs.edit().putStringSet("KEY_FAVORITES", favoriteNumbers.toSet()).commit()
                                            }
                                        }"""

content = content.replace(old_fav_save, new_fav_save)

with open("/app/applet/app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)
