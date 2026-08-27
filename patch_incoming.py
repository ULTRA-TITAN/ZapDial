import re

with open("/app/applet/app/src/main/java/com/titan/zapdial/IncomingCallScreen.kt", "r") as f:
    content = f.read()

# 1. Update positioning
content = content.replace("""    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(PageBackground)
            .padding(top = 64.dp, bottom = 48.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        
        Spacer(modifier = Modifier.weight(0.15f))
        
        // CALLER IDENTITY SECTION
        Column(
            modifier = Modifier.weight(1f),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {""", """    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(PageBackground)
            .padding(top = 80.dp, bottom = 48.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        
        // CALLER IDENTITY SECTION
        Column(
            modifier = Modifier.weight(1f),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {""")

# 2. Update Avatar sizing
content = content.replace("""            Box(
                contentAlignment = Alignment.Center,
                modifier = Modifier
                    .padding(bottom = 20.dp)
                    .size(116.dp)
                    .clip(CircleShape)
                    .background(getAvatarColorLocal(displayName))
                    .border(1.dp, AvatarBorder, CircleShape)
            ) {
                Text(
                    text = displayAvatarStr,
                    fontSize = 42.sp,
                    fontWeight = FontWeight.Light,
                    color = AvatarText
                )
            }""", """            Box(
                contentAlignment = Alignment.Center,
                modifier = Modifier
                    .padding(bottom = 20.dp)
                    .size(140.dp)
                    .clip(CircleShape)
                    .background(getAvatarColorLocal(displayName))
                    .border(1.dp, AvatarBorder, CircleShape)
            ) {
                Text(
                    text = displayAvatarStr,
                    fontSize = 48.sp,
                    fontWeight = FontWeight.Light,
                    color = AvatarText
                )
            }""")

# 3. Update Text sizes
content = content.replace("""            Text(
                text = actualDisplayName,
                fontSize = 27.sp,
                fontWeight = FontWeight.Medium,
                color = TextPrimary
            )
            Text(
                text = actualDisplayNumber,
                fontSize = 16.sp,
                fontWeight = FontWeight.Normal,
                color = TextSecondary,
                modifier = Modifier.padding(top = 4.dp, bottom = 18.dp)
            )""", """            Text(
                text = actualDisplayName,
                fontSize = 34.sp,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimary
            )
            Text(
                text = actualDisplayNumber,
                fontSize = 18.sp,
                fontWeight = FontWeight.Normal,
                color = TextSecondary,
                modifier = Modifier.padding(top = 4.dp, bottom = 18.dp)
            )""")

# 4. Update Slider Sizes
content = content.replace("""@Composable
fun AnswerDeclineSlider(view: android.view.View, onAnswer: () -> Unit, onReject: () -> Unit) {
    val density = LocalDensity.current
    val trackHeight = 72.dp
    val handleSize = 62.dp
    Column(modifier = Modifier.fillMaxWidth()) {
        BoxWithConstraints(
            modifier = Modifier
                .fillMaxWidth()
                .height(trackHeight)
                .clip(RoundedCornerShape(36.dp))""", """@Composable
fun AnswerDeclineSlider(view: android.view.View, onAnswer: () -> Unit, onReject: () -> Unit) {
    val density = LocalDensity.current
    val trackHeight = 84.dp
    val handleSize = 72.dp
    Column(modifier = Modifier.fillMaxWidth()) {
        BoxWithConstraints(
            modifier = Modifier
                .fillMaxWidth()
                .height(trackHeight)
                .clip(RoundedCornerShape(42.dp))""")

# 5. Update Slider Gradients
content = content.replace("""                            .background(Brush.horizontalGradient(
                                0.0f to ColorRed.copy(alpha = 0.28f),
                                1.0f to Color.Transparent
                            ))""", """                            .background(Brush.horizontalGradient(
                                0.0f to ColorRed.copy(alpha = 0.8f),
                                0.6f to ColorRed.copy(alpha = 0.2f),
                                1.0f to Color.Transparent
                            ))""")

content = content.replace("""                            .background(Brush.horizontalGradient(
                                0.0f to Color.Transparent,
                                1.0f to ColorGreen.copy(alpha = 0.28f)
                            ))""", """                            .background(Brush.horizontalGradient(
                                0.0f to Color.Transparent,
                                0.4f to ColorGreen.copy(alpha = 0.2f),
                                1.0f to ColorGreen.copy(alpha = 0.8f)
                            ))""")

with open("/app/applet/app/src/main/java/com/titan/zapdial/IncomingCallScreen.kt", "w") as f:
    f.write(content)
