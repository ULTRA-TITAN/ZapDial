with open('app/src/main/java/com/titan/zapdial/ZapCallService.kt', 'r') as f:
    content = f.read()

content = content.replace("notificationBuilder.setStyle(androidx.media.app.NotificationCompat.MediaStyle().setShowActionsInCompactView(0, 1))", "")

with open('app/src/main/java/com/titan/zapdial/ZapCallService.kt', 'w') as f:
    f.write(content)
