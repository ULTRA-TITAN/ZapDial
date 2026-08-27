with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

old_state = """    var showFrequentContacts by remember {
        mutableStateOf(sharedPrefs.getBoolean("KEY_SHOW_FREQUENT", true))
    }
    var selectedHistoryContact by remember { mutableStateOf<String?>(null) }"""

new_state = """    var showFrequentContacts by remember {
        mutableStateOf(sharedPrefs.getBoolean("KEY_SHOW_FREQUENT", true))
    }
    var selectedHistoryContact by remember { mutableStateOf<String?>(null) }
    var searchQuery by remember { mutableStateOf("") }
    val hiddenFavorites = remember { mutableStateListOf<String>() }
    
    LaunchedEffect(Unit) {
        val hidden = sharedPrefs.getStringSet("KEY_HIDDEN_FAVORITES", emptySet()) ?: emptySet()
        hiddenFavorites.addAll(hidden)
    }"""

content = content.replace(old_state, new_state)

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)
