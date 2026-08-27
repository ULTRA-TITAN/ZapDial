import re

with open("/app/applet/app/src/main/java/com/titan/zapdial/ZapCallService.kt", "r") as f:
    content = f.read()

old_code = """        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        if (!CallSessionManager.isAppInForeground) {
            notificationManager.notify(NOTIFICATION_ID, notificationBuilder.build())
        }
        }
    }"""

new_code = """        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        if (!CallSessionManager.isAppInForeground) {
            notificationManager.notify(NOTIFICATION_ID, notificationBuilder.build())
        }
        
        if (call.state == Call.STATE_RINGING) {
            val intent = Intent(this@ZapCallService, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_REORDER_TO_FRONT or Intent.FLAG_ACTIVITY_SINGLE_TOP
            }
            startActivity(intent)
        }
        }
    }"""

content = content.replace(old_code, new_code)

with open("/app/applet/app/src/main/java/com/titan/zapdial/ZapCallService.kt", "w") as f:
    f.write(content)
