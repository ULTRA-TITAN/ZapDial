import re

with open("app/src/main/java/com/titan/zapdial/CallManager.kt", "r") as f:
    content = f.read()

content = content.replace("import android.telecom.TelecomManager", "import android.telecom.TelecomManager\nimport android.telecom.PhoneAccountHandle\nimport android.telephony.SubscriptionManager")

old_makecall = """    fun makeCall(context: Context, rawPhoneNumber: String) {"""
new_makecall = """    fun getAvailableSims(context: Context): List<PhoneAccountHandle> {
        val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as TelecomManager
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_PHONE_STATE) == PackageManager.PERMISSION_GRANTED) {
            return telecomManager.callCapablePhoneAccounts
        }
        return emptyList()
    }

    fun getSimLabel(context: Context, handle: PhoneAccountHandle): String {
        val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as TelecomManager
        return telecomManager.getPhoneAccount(handle)?.label?.toString() ?: "Unknown SIM"
    }

    fun makeCall(context: Context, rawPhoneNumber: String, accountHandle: PhoneAccountHandle? = null) {"""
content = content.replace(old_makecall, new_makecall)

old_bundle = """                    Bundle().apply { putBoolean(TelecomManager.EXTRA_START_CALL_WITH_SPEAKERPHONE, false) }"""
new_bundle = """                    Bundle().apply { 
                        putBoolean(TelecomManager.EXTRA_START_CALL_WITH_SPEAKERPHONE, false)
                        if (accountHandle != null) {
                            putParcelable(TelecomManager.EXTRA_PHONE_ACCOUNT_HANDLE, accountHandle)
                        }
                    }"""
content = content.replace(old_bundle, new_bundle)

with open("app/src/main/java/com/titan/zapdial/CallManager.kt", "w") as f:
    f.write(content)

