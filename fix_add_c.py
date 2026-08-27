with open('app/src/main/java/com/titan/zapdial/AddContactDialog.kt', 'r') as f:
    content = f.read()

content = content.replace("fun AddContactDialog(\n    onDismiss: () -> Unit,\n    onContactAdded: () -> Unit\n) {", "fun AddContactDialog(\n    initialNumber: String = \"\",\n    onDismiss: () -> Unit,\n    onContactAdded: () -> Unit\n) {")

with open('app/src/main/java/com/titan/zapdial/AddContactDialog.kt', 'w') as f:
    f.write(content)
