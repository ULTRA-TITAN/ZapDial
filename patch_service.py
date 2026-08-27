import re

with open("app/src/main/java/com/titan/zapdial/ZapCallService.kt", "r") as f:
    content = f.read()

old_func_top = """    private fun updateNotification(call: Call) {
        val callerNumber = call.details?.handle?.schemeSpecificPart ?: "Unknown"
        val callerName = call.details?.callerDisplayName ?: callerNumber"""

new_func_top = """    private fun updateNotification(call: Call) {
        val callerNumber = call.details?.handle?.schemeSpecificPart ?: "Unknown"
        val originalName = call.details?.callerDisplayName
        
        kotlinx.coroutines.GlobalScope.launch(kotlinx.coroutines.Dispatchers.IO) {
            val resolvedName = if (callerNumber != "Unknown") ContactFetcher.lookupContactName(this@ZapCallService, callerNumber) else null
            val callerName = resolvedName ?: originalName ?: callerNumber"""

content = content.replace(old_func_top, new_func_top)

# Since we wrapped in a launch, we must close the brace at the end of the method
content = content.replace("notificationManager.notify(NOTIFICATION_ID, notificationBuilder.build())\n    }", "notificationManager.notify(NOTIFICATION_ID, notificationBuilder.build())\n        }\n    }")

# Also, 'this' becomes 'this@ZapCallService'
# Let's replace 'this, ' with 'this@ZapCallService, ' in PendingIntents
content = content.replace("Intent(this, ", "Intent(this@ZapCallService, ")
content = content.replace("PendingIntent.getActivity(\n            this,", "PendingIntent.getActivity(\n            this@ZapCallService,")
content = content.replace("Builder(this, CHANNEL_ID)", "Builder(this@ZapCallService, CHANNEL_ID)")
content = content.replace("PendingIntent.getBroadcast(this,", "PendingIntent.getBroadcast(this@ZapCallService,")

with open("app/src/main/java/com/titan/zapdial/ZapCallService.kt", "w") as f:
    f.write(content)
