import re

with open("app/src/main/java/com/titan/zapdial/OngoingCallScreen.kt", "r") as f:
    content = f.read()

# 1. Add state for simLabel
state_insert = """    var activeNumber = callerNumber"""
state_new = """    var activeNumber = callerNumber
    var simLabel by remember { mutableStateOf<String?>(null) }
    val callDetails = activeCall?.details
    val accountHandle = callDetails?.accountHandle
    
    LaunchedEffect(accountHandle) {
        if (accountHandle != null) {
            val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as android.telecom.TelecomManager
            val label = telecomManager.getPhoneAccount(accountHandle)?.label?.toString()
            if (label != null) {
                if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_PHONE_STATE) == PackageManager.PERMISSION_GRANTED) {
                    val sims = CallManager.getAvailableSims(context)
                    if (sims.size > 1) {
                        val index = sims.indexOf(accountHandle)
                        simLabel = if (index != -1) "SIM ${index + 1} • $label" else label
                    }
                }
            }
        }
    }"""
content = content.replace(state_insert, state_new)

# 2. Add UI for simLabel
ui_insert = """            Text(
                text = activeNumber,
                fontSize = 17.sp,
                color = ColorSlateGray,"""
ui_new = """            Text(
                text = activeNumber,
                fontSize = 17.sp,
                color = ColorSlateGray
            )
            if (simLabel != null) {
                Spacer(modifier = Modifier.height(12.dp))
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(12.dp))
                        .background(ColorSlateGray.copy(alpha = 0.15f))
                        .padding(horizontal = 12.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = "via $simLabel",
                        fontSize = 12.sp,
                        color = ColorSlateGray,
                        fontWeight = FontWeight.Medium
                    )
                }
            }
            Text(
                text = "",
                fontSize = 0.sp,"""
content = content.replace(ui_insert, ui_new)

with open("app/src/main/java/com/titan/zapdial/OngoingCallScreen.kt", "w") as f:
    f.write(content)
