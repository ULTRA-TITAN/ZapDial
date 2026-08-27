import re

with open("app/src/main/java/com/titan/zapdial/ContactFetcher.kt", "r") as f:
    content = f.read()

# Replace DISPLAY_NAME with DISPLAY_NAME_PRIMARY in projection
content = content.replace("ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME,", "ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME_PRIMARY,")

# Replace DISPLAY_NAME with DISPLAY_NAME_PRIMARY in cursor getColumnIndex
content = content.replace("it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME)", "it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME_PRIMARY)")

# Add IN_VISIBLE_GROUP filter
old_query = """                val cursor = contentResolver.query(
                    ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                    projection, null, null,
                    "${ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME} ASC"
                )"""
new_query = """                val cursor = contentResolver.query(
                    ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                    projection,
                    "${ContactsContract.Data.IN_VISIBLE_GROUP} = 1", null,
                    "${ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME_PRIMARY} ASC"
                )"""
content = content.replace(old_query, new_query)

# Add lookupContactName function
lookup_func = """    fun lookupContactName(context: Context, phoneNumber: String): String? {
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CONTACTS) != PackageManager.PERMISSION_GRANTED) {
            return null
        }
        var contactName: String? = null
        try {
            val uri = Uri.withAppendedPath(ContactsContract.PhoneLookup.CONTENT_FILTER_URI, Uri.encode(phoneNumber))
            val projection = arrayOf(ContactsContract.PhoneLookup.DISPLAY_NAME)
            context.contentResolver.query(uri, projection, null, null, null)?.use { cursor ->
                if (cursor.moveToFirst()) {
                    val nameIdx = cursor.getColumnIndex(ContactsContract.PhoneLookup.DISPLAY_NAME)
                    if (nameIdx != -1) {
                        contactName = cursor.getString(nameIdx)
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return contactName
    }
}"""
content = content.replace("    }\n}", "    }\n\n" + lookup_func)

with open("app/src/main/java/com/titan/zapdial/ContactFetcher.kt", "w") as f:
    f.write(content)
