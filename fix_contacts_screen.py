import re

with open("app/src/main/java/com/titan/zapdial/ContactsScreen.kt", "r") as f:
    content = f.read()

old_bottom_sheet = """
    if (showContactOptionsFor != null) {
        androidx.compose.material3.ModalBottomSheet(onDismissRequest = { showContactOptionsFor = null }, containerColor = PlateBackground) {
            Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
                Text(text = showContactOptionsFor!!.name, fontSize = 20.sp, fontWeight = FontWeight.SemiBold, color = TextPrimary)
                Spacer(modifier = Modifier.height(16.dp))
                val context = LocalContext.current
                val number = showContactOptionsFor!!.phoneNumber
                val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
                val mistouchPrevention = sharedPrefs.getBoolean("KEY_MISTOUCH_PREVENTION", false)
                
                androidx.compose.material3.OutlinedButton(onClick = { if (mistouchPrevention) {} else CallManager.makeCall(context, number); showContactOptionsFor = null }, modifier = Modifier.fillMaxWidth()) { Text("Dial", fontSize = 16.sp, color = TextPrimary) }
                androidx.compose.material3.OutlinedButton(onClick = { /* Edit */ showContactOptionsFor = null }, modifier = Modifier.fillMaxWidth()) { Text("Edit", fontSize = 16.sp, color = TextPrimary) }
                androidx.compose.material3.OutlinedButton(onClick = { /* Delete */ showContactOptionsFor = null }, modifier = Modifier.fillMaxWidth()) { Text("Delete", fontSize = 16.sp, color = TextPrimary) }
            }
        }
    }
"""

new_bottom_sheet = """
    if (showContactOptionsFor != null) {
        androidx.compose.material3.ModalBottomSheet(onDismissRequest = { showContactOptionsFor = null }, containerColor = PlateBackground) {
            Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
                Text(text = showContactOptionsFor!!.name, fontSize = 20.sp, fontWeight = FontWeight.SemiBold, color = TextPrimary)
                Spacer(modifier = Modifier.height(24.dp))
                val context = LocalContext.current
                val contactId = showContactOptionsFor!!.id
                val number = showContactOptionsFor!!.phoneNumber
                
                Row(
                    modifier = Modifier.fillMaxWidth().clickable {
                        CallManager.makeCall(context, number)
                        showContactOptionsFor = null
                    }.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    androidx.compose.material3.Icon(androidx.compose.material.icons.Icons.Default.Call, contentDescription = "Dial")
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Dial Contact", fontSize = 16.sp, color = TextPrimary)
                }
                Row(
                    modifier = Modifier.fillMaxWidth().clickable {
                        val intent = android.content.Intent(android.content.Intent.ACTION_EDIT).apply {
                            try {
                                data = android.content.ContentUris.withAppendedId(android.provider.ContactsContract.Contacts.CONTENT_URI, contactId.toLong())
                            } catch (e: Exception) {}
                        }
                        try { context.startActivity(intent) } catch (e: Exception) {}
                        showContactOptionsFor = null
                    }.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    androidx.compose.material3.Icon(androidx.compose.material.icons.Icons.Default.Edit, contentDescription = "Edit")
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Edit Contact", fontSize = 16.sp, color = TextPrimary)
                }
                Row(
                    modifier = Modifier.fillMaxWidth().clickable {
                        try {
                            val uri = android.content.ContentUris.withAppendedId(android.provider.ContactsContract.Contacts.CONTENT_URI, contactId.toLong())
                            context.contentResolver.delete(uri, null, null)
                            scope.launch {
                                allContacts = ContactFetcher.fetchContacts(context)
                            }
                        } catch (e: Exception) {}
                        showContactOptionsFor = null
                    }.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    androidx.compose.material3.Icon(androidx.compose.material.icons.Icons.Default.Delete, contentDescription = "Delete", tint = Color.Red)
                    Spacer(modifier = Modifier.width(16.dp))
                    Text("Delete Contact", fontSize = 16.sp, color = Color.Red)
                }
                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }
"""

content = content.replace(old_bottom_sheet.strip(), new_bottom_sheet.strip())

# Add some missing imports
imports = """
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Delete
"""
content = re.sub(r'import androidx\.compose\.material3\.Text', imports.strip() + '\nimport androidx.compose.material3.Text', content)

with open("app/src/main/java/com/titan/zapdial/ContactsScreen.kt", "w") as f:
    f.write(content)

print("ContactsScreen updated!")
