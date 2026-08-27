import re

with open("app/src/main/java/com/titan/zapdial/ContactFetcher.kt", "r") as f:
    content = f.read()

old_name_logic = """val name = if (nameIndex != -1) it.getString(nameIndex).orEmpty() else "Unknown"
                        val rawNumber = if (numberIndex != -1) it.getString(numberIndex).orEmpty() else ""
                        val photoUriString = if (photoIndex != -1) it.getString(photoIndex) else null"""

new_name_logic = """val rawNumber = if (numberIndex != -1) it.getString(numberIndex).orEmpty() else ""
                        var name = if (nameIndex != -1) it.getString(nameIndex).orEmpty() else ""
                        if (name.isBlank() || name == "Unknown") {
                            name = android.telephony.PhoneNumberUtils.formatNumber(rawNumber, java.util.Locale.getDefault().country) ?: rawNumber
                        }
                        val photoUriString = if (photoIndex != -1) it.getString(photoIndex) else null"""

content = content.replace(old_name_logic, new_name_logic)

with open("app/src/main/java/com/titan/zapdial/ContactFetcher.kt", "w") as f:
    f.write(content)
