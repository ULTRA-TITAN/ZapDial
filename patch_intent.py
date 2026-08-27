import re

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

old_intent = """                    OutlinedButton(
                        onClick = {
                            val intent = Intent(Intent.ACTION_INSERT_OR_EDIT).apply {
                                type = ContactsContract.Contacts.CONTENT_ITEM_TYPE
                                putExtra(android.provider.ContactsContract.Intents.Insert.PHONE, item.number)
                            }
                            try { context.startActivity(intent) } catch(e: Exception) {}
                        },"""

new_intent = """                    OutlinedButton(
                        onClick = {
                            kotlinx.coroutines.GlobalScope.launch(kotlinx.coroutines.Dispatchers.IO) {
                                var contactId: String? = null
                                try {
                                    val uri = Uri.withAppendedPath(ContactsContract.PhoneLookup.CONTENT_FILTER_URI, Uri.encode(item.number))
                                    context.contentResolver.query(uri, arrayOf(ContactsContract.PhoneLookup._ID), null, null, null)?.use { cursor ->
                                        if (cursor.moveToFirst()) {
                                            val idIdx = cursor.getColumnIndex(ContactsContract.PhoneLookup._ID)
                                            if (idIdx != -1) contactId = cursor.getString(idIdx)
                                        }
                                    }
                                } catch(e: Exception) {}
                                
                                kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.Main) {
                                    if (contactId != null) {
                                        val editIntent = Intent(Intent.ACTION_EDIT).apply {
                                            data = Uri.withAppendedPath(ContactsContract.Contacts.CONTENT_URI, contactId)
                                        }
                                        try { context.startActivity(editIntent) } catch(e: Exception) {}
                                    } else {
                                        val insertIntent = Intent(Intent.ACTION_INSERT).apply {
                                            type = ContactsContract.RawContacts.CONTENT_TYPE
                                            putExtra(android.provider.ContactsContract.Intents.Insert.PHONE, item.number)
                                        }
                                        try { context.startActivity(insertIntent) } catch(e: Exception) {}
                                    }
                                }
                            }
                        },"""

content = content.replace(old_intent, new_intent)

if "import kotlinx.coroutines.launch" not in content:
    content = content.replace("import kotlinx.coroutines.Dispatchers\n", "import kotlinx.coroutines.Dispatchers\nimport kotlinx.coroutines.launch\n")
if "import android.net.Uri" not in content:
    content = content.replace("import android.content.Intent\n", "import android.content.Intent\nimport android.net.Uri\n")

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)
