with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

content = content.replace("""    val filteredHistory by remember(callHistory, searchQuery) {
        derivedStateOf {
            callHistory.filter { 
                (it.name?.contains(searchQuery, ignoreCase = true) == true) || 
                it.number.contains(searchQuery) 
            }
        }
    }""", """    val filteredHistory by remember(callHistory, searchQuery) {
        derivedStateOf {
            if (searchQuery.isEmpty()) {
                callHistory
            } else {
                callHistory.filter { 
                    (it.name?.contains(searchQuery, ignoreCase = true) == true) || 
                    it.number.contains(searchQuery) 
                }
            }
        }
    }""")

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
