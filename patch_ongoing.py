import re

with open("/app/applet/app/src/main/java/com/titan/zapdial/OngoingCallScreen.kt", "r") as f:
    content = f.read()

# Replace the top Box and layout
old_layout = """    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(ColorCreamBackground)
            .systemBarsPadding()
    ) {
        // --- Top Caller Identity Section ---
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.TopCenter)
                .padding(top = 64.dp)
        ) {"""

new_layout = """    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(ColorCreamBackground)
            .systemBarsPadding(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // --- Top Caller Identity Section ---
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 64.dp)
        ) {"""

content = content.replace(old_layout, new_layout)

# Replace the Bottom Controls Cluster and add Spacer
old_bottom = """        }

        // --- Compact Bottom Controls Cluster ---
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.BottomCenter)
                .padding(bottom = 40.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {"""

new_bottom = """        }

        Spacer(modifier = Modifier.weight(1f))

        // --- Compact Bottom Controls Cluster ---
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 40.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {"""

content = content.replace(old_bottom, new_bottom)

with open("/app/applet/app/src/main/java/com/titan/zapdial/OngoingCallScreen.kt", "w") as f:
    f.write(content)
