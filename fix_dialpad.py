import re

with open('app/src/main/java/com/titan/zapdial/DialPadScreen.kt', 'r') as f:
    content = f.read()

helper = """fun mapNameToDigits(name: String): String {
    val map = mapOf(
        'A' to '2', 'B' to '2', 'C' to '2',
        'D' to '3', 'E' to '3', 'F' to '3',
        'G' to '4', 'H' to '4', 'I' to '4',
        'J' to '5', 'K' to '5', 'L' to '5',
        'M' to '6', 'N' to '6', 'O' to '6',
        'P' to '7', 'Q' to '7', 'R' to '7', 'S' to '7',
        'T' to '8', 'U' to '8', 'V' to '8',
        'W' to '9', 'X' to '9', 'Y' to '9', 'Z' to '9'
    )
    return name.uppercase().mapNotNull { map[it] }.joinToString("")
}

@Composable
"""
content = content.replace("@Composable\nfun DialPadScreen() {", helper + "fun DialPadScreen() {")

state_new = """    var number by remember { mutableStateOf("") }
    var allContacts by remember { mutableStateOf<List<Contact>>(emptyList()) }
    val context = LocalContext.current
    val view = LocalView.current
    val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
    
    LaunchedEffect(Unit) {
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CONTACTS) == PackageManager.PERMISSION_GRANTED) {
            allContacts = ContactFetcher.fetchContacts(context)
        }
    }
    
    val matchedContacts by remember(number, allContacts) {
        derivedStateOf {
            if (number.isEmpty()) emptyList()
            else allContacts.filter { 
                it.number.replace("[^0-9+]".toRegex(), "").contains(number) || 
                mapNameToDigits(it.name).contains(number) 
            }.take(5)
        }
    }
    val showAddContact = number.length >= 3 && !allContacts.any { it.number.replace("[^0-9+]".toRegex(), "") == number }
    var showAddDialog by remember { mutableStateOf(false) }
    
    if (showAddDialog) {
        AddContactDialog(
            initialNumber = number,
            onDismiss = { showAddDialog = false },
            onContactAdded = {
                kotlinx.coroutines.GlobalScope.launch(kotlinx.coroutines.Dispatchers.Main) {
                    if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CONTACTS) == PackageManager.PERMISSION_GRANTED) {
                        allContacts = ContactFetcher.fetchContacts(context)
                    }
                }
            }
        )
    }
"""
content = content.replace("    var number by remember { mutableStateOf(\"\") }\n    val context = LocalContext.current\n    val view = LocalView.current\n    val sharedPrefs = context.getSharedPreferences(\"ZapDialPrefs\", Context.MODE_PRIVATE)", state_new)

display_old = """        // Display Area
        Box(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth(),
            contentAlignment = Alignment.BottomCenter
        ) {
            Text(
                text = number,
                fontSize = 42.sp,
                fontWeight = FontWeight.SemiBold,
                color = Color(0xFF0F172A), // Deep Slate
                maxLines = 1,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(bottom = 24.dp)
            )
        }"""
display_new = """        // Display Area
        Column(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth(),
            verticalArrangement = Arrangement.Bottom,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            if (matchedContacts.isNotEmpty() || showAddContact) {
                androidx.compose.foundation.lazy.LazyRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    contentPadding = PaddingValues(horizontal = 16.dp),
                    modifier = Modifier.padding(bottom = 16.dp).fillMaxWidth()
                ) {
                    items(matchedContacts.size) { index ->
                        val contact = matchedContacts[index]
                        Surface(
                            shape = CircleShape,
                            color = Color.White,
                            shadowElevation = 2.dp,
                            modifier = Modifier.clickable { attemptCall(contact.number) }
                        ) {
                            Row(modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                                Text(contact.name, fontSize = 14.sp, fontWeight = FontWeight.Medium, color = Color(0xFF0F172A))
                            }
                        }
                    }
                    if (showAddContact) {
                        item {
                            Surface(
                                shape = CircleShape,
                                color = Color(0xFFE0F2FE),
                                modifier = Modifier.clickable { showAddDialog = true }
                            ) {
                                Row(modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                                    Text("+ Add to Contacts", fontSize = 14.sp, fontWeight = FontWeight.Medium, color = Color(0xFF0284C7))
                                }
                            }
                        }
                    }
                }
            }
            Text(
                text = number,
                fontSize = 42.sp,
                fontWeight = FontWeight.SemiBold,
                color = Color(0xFF0F172A),
                maxLines = 1,
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(bottom = 24.dp)
            )
        }"""
content = content.replace(display_old, display_new)

with open('app/src/main/java/com/titan/zapdial/DialPadScreen.kt', 'w') as f:
    f.write(content)
