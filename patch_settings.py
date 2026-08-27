import re

with open("app/src/main/java/com/titan/zapdial/SettingsScreen.kt", "r") as f:
    content = f.read()

old_click = """                    .clickable {
                        try {
                            val intent = Intent(android.telecom.TelecomManager.ACTION_CHANGE_DEFAULT_DIALER)
                            intent.putExtra(android.telecom.TelecomManager.EXTRA_CHANGE_DEFAULT_DIALER_PACKAGE_NAME, context.packageName)
                            // If they are default dialer they can open BlockedNumberContract UI
                            val blockedNumbersIntent = Intent(android.telecom.TelecomManager.ACTION_MANAGE_BLOCKED_NUMBERS)
                            context.startActivity(blockedNumbersIntent)
                        } catch (e: Exception) {
                            try {
                                val intent = Intent("android.intent.action.MAIN")
                                intent.setClassName("com.android.phone", "com.android.phone.settings.BlockedNumberActivity")
                                context.startActivity(intent)
                            } catch (e2: Exception) {}
                        }
                    }"""

new_click = """                    .clickable {
                        try {
                            val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as android.telecom.TelecomManager
                            val intent = telecomManager.createManageBlockedNumbersIntent()
                            context.startActivity(intent)
                        } catch (e: Exception) {
                            try {
                                val intent = Intent("android.intent.action.MAIN")
                                intent.setClassName("com.android.phone", "com.android.phone.settings.BlockedNumberActivity")
                                context.startActivity(intent)
                            } catch (e2: Exception) {}
                        }
                    }"""

content = content.replace(old_click, new_click)

with open("app/src/main/java/com/titan/zapdial/SettingsScreen.kt", "w") as f:
    f.write(content)
