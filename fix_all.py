import re

# Fix ZapCallService
with open("/app/applet/app/src/main/java/com/titan/zapdial/ZapCallService.kt", "r") as f:
    content = f.read()
content = content.replace('android.widget.Toast.makeText(context', 'android.widget.Toast.makeText(this@ZapCallService')
with open("/app/applet/app/src/main/java/com/titan/zapdial/ZapCallService.kt", "w") as f:
    f.write(content)

# Fix ContactsScreen
with open("/app/applet/app/src/main/java/com/titan/zapdial/ContactsScreen.kt", "r") as f:
    content = f.read()

# Add imports
if 'import kotlinx.coroutines.withContext' not in content:
    content = content.replace('import kotlinx.coroutines.launch', 'import kotlinx.coroutines.launch\nimport kotlinx.coroutines.withContext\nimport kotlinx.coroutines.Dispatchers')

# Re-apply the drag handlers since they failed to replace
content = re.sub(
    r"fun onDragAt\(yInContainer: Float\).*?fun onDragEnd\(\).*?lastSnappedLetter = null\s*\}",
    """var isDragging by remember { mutableStateOf(false) }
    var bubbleYRaw by remember { mutableFloatStateOf(0f) }

    val bubbleScale by androidx.compose.animation.core.animateFloatAsState(if (isDragging) 1f else 0.2f, androidx.compose.animation.core.tween(if(isDragging) 180 else 300, easing = if(isDragging) androidx.compose.animation.core.FastOutSlowInEasing else androidx.compose.animation.core.CubicBezierEasing(0.6f, -0.1f, 0.75f, 0.15f)))
    val bubbleOpacity by androidx.compose.animation.core.animateFloatAsState(if (isDragging) 1f else 0f, androidx.compose.animation.core.tween(if(isDragging) 120 else 280))
    val stemWidthState by androidx.compose.animation.core.animateFloatAsState(if (isDragging) extendedStemWidth else 0f, androidx.compose.animation.core.tween(if(isDragging) 140 else 260, easing = if(isDragging) androidx.compose.animation.core.FastOutSlowInEasing else androidx.compose.animation.core.CubicBezierEasing(0.6f, -0.1f, 0.75f, 0.15f)))

    fun onDragAt(yInContainer: Float) {
        isDragging = true
        bubbleYRaw = yInContainer
        val relY = (yInContainer - railTopPx).coerceIn(0f, railHeightPx)
        val ratio = (relY / railHeightPx).coerceIn(0f, 1f)
        val idx = (ratio * (LETTERS.size - 1)).toInt().coerceIn(0, LETTERS.size - 1)
        currentLetter = idx
        val letter = LETTERS[idx]
        if (letter != lastSnappedLetter) {
            lastSnappedLetter = letter
            haptic.performHapticFeedback(androidx.compose.ui.hapticfeedback.HapticFeedbackType.TextHandleMove)
            scope.launch { snapToLetter(letter) }
        }
    }

    fun onDragEnd() {
        isDragging = false
        currentLetter = -1
        lastSnappedLetter = null
    }""",
    content,
    flags=re.DOTALL
)

# Replace the remaining Animatable variables if they still exist
content = re.sub(r"val bubbleY = remember \{ Animatable\(0f\) \}\n", "", content)
content = re.sub(r"val bubbleScale = remember \{ Animatable\(0\.2f\) \}\n", "", content)
content = re.sub(r"val bubbleOpacity = remember \{ Animatable\(0f\) \}\n", "", content)
content = re.sub(r"val stemWidth = remember \{ Animatable\(0f\) \}\n", "", content)

# Fix references
content = content.replace("bubbleY.value", "bubbleYRaw")
content = content.replace("bubbleScale.value", "bubbleScale")
content = content.replace("bubbleOpacity.value", "bubbleOpacity")
content = content.replace("stemWidth.value", "stemWidthState")

# Fix Icons missing imports
content = content.replace('androidx.compose.material.icons.Icons.Default.Block', 'androidx.compose.material.icons.filled.Block')
content = content.replace('androidx.compose.material.icons.Icons.Default.History', 'androidx.compose.material.icons.filled.History')

# Also, add the missing import for `androidx.compose.material.icons.filled.Block` if I just use `Icons.Default.Block`
content = content.replace('import androidx.compose.material.icons.filled.History', 'import androidx.compose.material.icons.filled.History\nimport androidx.compose.material.icons.filled.Block')

with open("/app/applet/app/src/main/java/com/titan/zapdial/ContactsScreen.kt", "w") as f:
    f.write(content)
