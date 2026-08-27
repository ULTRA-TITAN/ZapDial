with open('app/src/main/java/com/titan/zapdial/AddContactDialog.kt', 'r') as f:
    content = f.read()

sig_old = "fun AddContactDialog(onDismiss: () -> Unit, onContactAdded: () -> Unit) {"
sig_new = "fun AddContactDialog(initialNumber: String = \"\", onDismiss: () -> Unit, onContactAdded: () -> Unit) {"
content = content.replace(sig_old, sig_new)

mobile_old = "var mobileNumber by remember { mutableStateOf(\"\") }"
mobile_new = "var mobileNumber by remember { mutableStateOf(initialNumber) }"
content = content.replace(mobile_old, mobile_new)

with open('app/src/main/java/com/titan/zapdial/AddContactDialog.kt', 'w') as f:
    f.write(content)
