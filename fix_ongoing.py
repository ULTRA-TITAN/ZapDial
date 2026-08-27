with open('app/src/main/java/com/titan/zapdial/OngoingCallScreen.kt', 'r') as f:
    content = f.read()

imports = """import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import android.Manifest
import android.content.pm.PackageManager
import androidx.core.content.ContextCompat
"""
content = content.replace("import androidx.compose.ui.unit.sp", "import androidx.compose.ui.unit.sp\n" + imports)

with open('app/src/main/java/com/titan/zapdial/OngoingCallScreen.kt', 'w') as f:
    f.write(content)
