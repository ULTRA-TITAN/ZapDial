with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "r") as f:
    content = f.read()

content = content.replace("import androidx.compose.ui.hapticfeedback.HapticFeedbackConstants", "import android.view.HapticFeedbackConstants")
content = content.replace("not in hiddenFavorites", "!hiddenFavorites.contains(it.phoneNumber)")

if "val view = LocalView.current" not in content[:content.find("var mistouchPrevention") + 500]:
    content = content.replace("val context = LocalContext.current", "val context = LocalContext.current\n    val view = LocalView.current")

with open("app/src/main/java/com/titan/zapdial/HomeScreen.kt", "w") as f:
    f.write(content)
