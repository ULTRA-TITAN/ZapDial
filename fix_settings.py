import re

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

settings_new = """        var mistouchPrevention by remember {
            mutableStateOf(sharedPrefs.getBoolean("KEY_MISTOUCH_PREVENTION", false))
        }
        var showFrequentContacts by remember {
            mutableStateOf(sharedPrefs.getBoolean("KEY_SHOW_FREQUENT_CONTACTS", true))
        }"""
content = content.replace("""        var mistouchPrevention by remember {
            mutableStateOf(sharedPrefs.getBoolean("KEY_MISTOUCH_PREVENTION", false))
        }""", settings_new)

row_new = """        Row(modifier = Modifier.fillMaxWidth().padding(vertical = 12.dp), verticalAlignment = Alignment.CenterVertically) {
            Column(modifier = Modifier.weight(1f)) {
                Text("Show Frequent Contacts", fontSize = 18.sp, color = ColorPureBlack)
                Text("Display speed-dial contacts on Home", fontSize = 14.sp, color = ColorSlateGray)
            }
            Switch(
                checked = showFrequentContacts,
                onCheckedChange = { checked ->
                    showFrequentContacts = checked
                    sharedPrefs.edit().putBoolean("KEY_SHOW_FREQUENT_CONTACTS", checked).apply()
                }
            )
        }"""
content = content.replace('        Row(modifier = Modifier.fillMaxWidth().padding(vertical = 12.dp).clickable { /* Blocked */ }, verticalAlignment = Alignment.CenterVertically) {\n            Text("Blocked Numbers", fontSize = 18.sp, color = ColorPureBlack, modifier = Modifier.weight(1f))\n        }', row_new)

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
