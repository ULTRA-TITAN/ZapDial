import re

with open('app/src/main/java/com/titan/zapdial/CallManager.kt', 'r') as f:
    content = f.read()

imports = """import android.app.role.RoleManager
import android.content.Context
import android.content.Intent
import android.telecom.TelecomManager
import android.widget.Toast
import android.os.Build"""

new_methods = """
    fun isDefaultDialer(context: Context): Boolean {
        val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as TelecomManager
        return telecomManager.defaultDialerPackage == context.packageName
    }

    fun requestDefaultDialer(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val roleManager = context.getSystemService(Context.ROLE_SERVICE) as RoleManager
            val intent = roleManager.createRequestRoleIntent(RoleManager.ROLE_DIALER)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
            context.startActivity(intent)
        } else {
            val intent = Intent(TelecomManager.ACTION_CHANGE_DEFAULT_DIALER)
            intent.putExtra(TelecomManager.EXTRA_CHANGE_DEFAULT_DIALER_PACKAGE_NAME, context.packageName)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
            context.startActivity(intent)
        }
    }
"""

content = content.replace("import android.telecom.TelecomManager", imports)

make_call_new = """    fun makeCall(context: Context, rawPhoneNumber: String) {
        if (!isDefaultDialer(context)) {
            requestDefaultDialer(context)
            return
        }

        val cleanNumber = rawPhoneNumber.replace("[^0-9+]".toRegex(), "")"""
        
content = content.replace('    fun makeCall(context: Context, rawPhoneNumber: String) {\n        // Strip any spaces', make_call_new)
content = content.replace("object CallManager {", "object CallManager {" + new_methods)

with open('app/src/main/java/com/titan/zapdial/CallManager.kt', 'w') as f:
    f.write(content)
