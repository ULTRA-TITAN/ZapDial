with open('app/src/main/java/com/titan/zapdial/PermissionPrimerScreen.kt', 'r') as f:
    content = f.read()

new_btn = """        Button(
            onClick = {
                permissionLauncher.launch(
                    arrayOf(
                        Manifest.permission.READ_CONTACTS,
                        Manifest.permission.WRITE_CONTACTS,
                        Manifest.permission.CALL_PHONE,
                        Manifest.permission.READ_CALL_LOG,
                        Manifest.permission.RECORD_AUDIO
                    )
                )
                if (!CallManager.isDefaultDialer(context)) {
                    CallManager.requestDefaultDialer(context)
                }
            },"""

content = content.replace("        Button(\n            onClick = {\n                permissionLauncher.launch(\n                    arrayOf(\n                        Manifest.permission.READ_CONTACTS,\n                        Manifest.permission.WRITE_CONTACTS,\n                        Manifest.permission.CALL_PHONE,\n                        Manifest.permission.READ_CALL_LOG,\n                        Manifest.permission.RECORD_AUDIO\n                    )\n                )\n            },", new_btn)

card_new = """            PermissionCard(
                icon = Icons.Default.Call,
                iconTint = Color(0xFF16A34A),
                title = "Set as Default Dialer",
                subtitle = "Required to place calls and show the incoming call screen."
            )
            PermissionCard(
                icon = Icons.Default.Person,"""

content = content.replace("            PermissionCard(\n                icon = Icons.Default.Person,", card_new)

with open('app/src/main/java/com/titan/zapdial/PermissionPrimerScreen.kt', 'w') as f:
    f.write(content)
