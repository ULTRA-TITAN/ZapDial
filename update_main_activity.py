import re

with open('app/src/main/java/com/titan/zapdial/MainActivity.kt', 'r') as f:
    content = f.read()

# Add standard dialer check
imports = """import android.app.role.RoleManager
import android.telecom.TelecomManager
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.LaunchedEffect
"""

# check if already imported, they are mostly there.

# Modify MainHomeScreen to include dialer check.
target = """fun MainHomeScreen(startRoute: String) {"""
replacement = """fun MainHomeScreen(startRoute: String) {
    val context = LocalContext.current
    val roleManager = context.getSystemService(Context.ROLE_SERVICE) as? RoleManager
    val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as? TelecomManager
    
    val defaultDialerLauncher = androidx.activity.compose.rememberLauncherForActivityResult(
        contract = androidx.activity.result.contract.ActivityResultContracts.StartActivityForResult()
    ) { _ -> }

    LaunchedEffect(Unit) {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.Q) {
            if (roleManager?.isRoleHeld(RoleManager.ROLE_DIALER) == false) {
                val intent = roleManager.createRequestRoleIntent(RoleManager.ROLE_DIALER)
                defaultDialerLauncher.launch(intent)
            }
        } else {
            if (telecomManager?.defaultDialerPackage != context.packageName) {
                val intent = android.content.Intent(TelecomManager.ACTION_CHANGE_DEFAULT_DIALER)
                intent.putExtra(TelecomManager.EXTRA_CHANGE_DEFAULT_DIALER_PACKAGE_NAME, context.packageName)
                defaultDialerLauncher.launch(intent)
            }
        }
    }
"""

content = content.replace(target, replacement)

with open('app/src/main/java/com/titan/zapdial/MainActivity.kt', 'w') as f:
    f.write(content)
