with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

# Add BasicTextField import
if "import androidx.compose.foundation.text.BasicTextField" not in content:
    content = content.replace("import androidx.compose.material3.*", "import androidx.compose.material3.*\nimport androidx.compose.foundation.text.BasicTextField\nimport androidx.compose.ui.text.TextStyle")

old_search_box = """                    Box(modifier = Modifier
                        .weight(1f)
                        .padding(horizontal = 8.dp)
                        .clickable {
                            val intent = Intent(Intent.ACTION_VIEW, ContactsContract.Contacts.CONTENT_URI)
                            try { context.startActivity(intent) } catch (e: Exception) {}
                        }
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Search, contentDescription = "Search", tint = TextSecondary)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Search contacts", color = TextSecondary, fontSize = 16.sp)
                        }
                    }"""

new_search_box = """                    Box(modifier = Modifier
                        .weight(1f)
                        .padding(horizontal = 8.dp),
                        contentAlignment = Alignment.CenterStart
                    ) {
                        if (searchQuery.isEmpty()) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Default.Search, contentDescription = "Search", tint = TextSecondary)
                                Spacer(modifier = Modifier.width(8.dp))
                                Text("Search contacts", color = TextSecondary, fontSize = 16.sp)
                            }
                        } else {
                            Icon(Icons.Default.Search, contentDescription = "Search", tint = TextPrimary)
                        }
                        
                        BasicTextField(
                            value = searchQuery,
                            onValueChange = { searchQuery = it },
                            modifier = Modifier.fillMaxWidth().padding(start = if (searchQuery.isEmpty()) 0.dp else 32.dp),
                            textStyle = TextStyle(fontSize = 16.sp, color = TextPrimary),
                            singleLine = true
                        )
                    }"""

content = content.replace(old_search_box, new_search_box)

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)
