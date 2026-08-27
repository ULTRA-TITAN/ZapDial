import re

with open("app/src/main/java/com/titan/zapdial/CallManager.kt", "r") as f:
    content = f.read()

new_logic = """    fun getAvailableSims(context: Context): List<PhoneAccountHandle> {
        val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as TelecomManager
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_PHONE_STATE) == PackageManager.PERMISSION_GRANTED) {
            val activeSubs = android.telephony.SubscriptionManager.from(context).activeSubscriptionInfoList
            return telecomManager.callCapablePhoneAccounts
        }
        return emptyList()
    }"""

content = re.sub(r'    fun getAvailableSims\(context: Context\): List<PhoneAccountHandle> \{.*?\n    }', new_logic, content, flags=re.DOTALL)

with open("app/src/main/java/com/titan/zapdial/CallManager.kt", "w") as f:
    f.write(content)
