import re

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

# Replace Theme Colors
theme_colors_old = """// --- Theme Colors ---
private val ColorCreamBackground = Color(0xFFFFF8E8)
private val ColorPureWhite = Color(0xFFFFFFFF)
private val ColorPureBlack = Color(0xFF000000)
private val ColorRedMissed = Color(0xFFDC2626)
private val ColorGreenSuccess = Color(0xFF16A34A)
private val ColorSlateGray = Color(0xFF64748B)

private val AvatarColors = listOf(
    Color(0xFF1E3A8A), // Blue
    Color(0xFF065F46), // Dark Green
    Color(0xFF991B1B), // Dark Red
    Color(0xFF5B21B6), // Purple
    Color(0xFF9D174D), // Pink
    Color(0xFF854D0E), // Yellow/Brown
    Color(0xFF115E59), // Teal
    Color(0xFF374151)  // Slate
)

fun getAvatarColor(name: String): Color {
    if (name.isBlank()) return ColorSlateGray
    val hash = name.hashCode().absoluteValue
    return AvatarColors[hash % AvatarColors.size]
}"""

theme_colors_new = """// --- Theme Colors ---
private val ColorGlobalBackground = Color(0xFFFAFAFA)
private val ColorPureWhite = Color(0xFFFFFFFF)
private val ColorPureBlack = Color(0xFF0F172A)
private val ColorRedMissed = Color(0xFFDC2626)
private val ColorGreenSuccess = Color(0xFF16A34A)
private val ColorFaintGreen = Color(0xFFF0FDF4)
private val ColorSlateGray = Color(0xFF94A3B8)
private val ColorBorderGray = Color(0xFFE5E7EB)

private val AvatarColors = listOf(
    Color(0xFFAEC6E8), // Pastel Blue
    Color(0xFFB6D7A8), // Pastel Green
    Color(0xFFE6B8B7), // Pastel Red
    Color(0xFFF9E4B7), // Pastel Yellow
    Color(0xFFD9D2E9), // Pastel Purple
    Color(0xFFFAD1D1), // Pastel Pink
    Color(0xFFB2DFDB), // Pastel Teal
    Color(0xFFE2E8F0)  // Pastel Slate
)

fun getAvatarColor(name: String): Color {
    if (name.isBlank()) return AvatarColors.last()
    val hash = name.hashCode().absoluteValue
    return AvatarColors[hash % AvatarColors.size]
}"""
content = content.replace(theme_colors_old, theme_colors_new)

# Update Background in HomeScreen
content = content.replace(".background(ColorCreamBackground)", ".background(ColorGlobalBackground)")
content = content.replace('color = Color(0xFF0F172A)', 'color = ColorPureBlack') # Just to standardize in one place if any

# Update Recent Calls Header
content = content.replace('Text(\n                text = "Recent Calls",\n                fontSize = 24.sp,\n                fontWeight = FontWeight.Bold,\n                color = ColorPureBlack,\n                modifier = Modifier.padding(bottom = 16.dp, start = 8.dp)\n            )', 
'Text(\n                text = "Recent",\n                fontSize = 20.sp,\n                fontWeight = FontWeight.Medium,\n                color = ColorPureBlack,\n                modifier = Modifier.padding(bottom = 16.dp, start = 8.dp)\n            )')

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
