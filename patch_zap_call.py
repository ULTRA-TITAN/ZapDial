import re

with open("app/src/main/java/com/titan/zapdial/ZapCallService.kt", "r") as f:
    content = f.read()

old_notif = """        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.notify(NOTIFICATION_ID, notificationBuilder.build())
        }
    }"""
new_notif = """        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        if (!CallSessionManager.isAppInForeground) {
            notificationManager.notify(NOTIFICATION_ID, notificationBuilder.build())
        }
        }
    }"""
content = content.replace(old_notif, new_notif)

with open("app/src/main/java/com/titan/zapdial/ZapCallService.kt", "w") as f:
    f.write(content)
