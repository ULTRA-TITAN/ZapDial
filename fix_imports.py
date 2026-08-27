import re

def add_import(filename):
    with open(filename, "r") as f:
        content = f.read()

    if "import android.telecom.PhoneAccountHandle" not in content:
        content = re.sub(r'import android\.content\.Context', 'import android.content.Context\nimport android.telecom.PhoneAccountHandle', content)
        
    with open(filename, "w") as f:
        f.write(content)

add_import("app/src/main/java/com/titan/zapdial/HomeScreen.kt")
add_import("app/src/main/java/com/titan/zapdial/ContactsScreen.kt")
add_import("app/src/main/java/com/titan/zapdial/DialPadScreen.kt")
add_import("app/src/main/java/com/titan/zapdial/SimSelectionDialog.kt")
add_import("app/src/main/java/com/titan/zapdial/CallManager.kt")
