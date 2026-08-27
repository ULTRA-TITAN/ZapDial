import re

with open("app/src/main/java/com/titan/zapdial/OngoingCallScreen.kt", "r") as f:
    content = f.read()

# Replace the text block
old_text = """            Text(
                text = activeNumber,
                fontSize = 17.sp,
                color = ColorSlateGray
            )"""

new_text = """            Text(
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
            }"""

content = content.replace(old_text, new_text)

with open("app/src/main/java/com/titan/zapdial/OngoingCallScreen.kt", "w") as f:
    f.write(content)
