with open('app/src/main/java/com/titan/zapdial/ContactsScreen.kt', 'r') as f:
    content = f.read()

start_marker = "// A-Z Fast Scroller with Live Bubble"
end_marker = "            }\n        }\n    }\n\n    if (showAddDialog) {"

scroller_start = content.find(start_marker)
scroller_end = content.find(end_marker)

new_scroller = """// A-Z Fast Scroller with Live Bubble
                var hoveredLetter by remember { mutableStateOf<Char?>(null) }
                var isDragging by remember { mutableStateOf(false) }
                val view = LocalView.current
                
                LaunchedEffect(hoveredLetter, isDragging) {
                    if (!isDragging && hoveredLetter != null) {
                        kotlinx.coroutines.delay(400)
                        hoveredLetter = null
                    }
                }
                
                // Centered HUD Bubble
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    androidx.compose.animation.AnimatedVisibility(
                        visible = hoveredLetter != null,
                        enter = fadeIn() + scaleIn(),
                        exit = fadeOut() + scaleOut()
                    ) {
                        Box(
                            contentAlignment = Alignment.Center,
                            modifier = Modifier
                                .size(72.dp)
                                .clip(CircleShape)
                                .background(Color.White)
                                .border(1.dp, Color(0xFFE2E8F0), CircleShape)
                                .shadow(8.dp, CircleShape)
                        ) {
                            Text(
                                text = hoveredLetter?.toString() ?: "",
                                fontSize = 28.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF0F172A)
                            )
                        }
                    }
                }
                
                Box(modifier = Modifier.align(Alignment.CenterEnd).fillMaxHeight()) {
                    Column(
                        modifier = Modifier
                            .padding(end = 4.dp, top = 24.dp, bottom = 24.dp)
                            .fillMaxHeight()
                            .pointerInput(Unit) {
                                androidx.compose.foundation.gestures.detectVerticalDragGestures(
                                    onDragStart = { offset ->
                                        isDragging = true
                                        val itemHeight = size.height / alphabet.size.toFloat()
                                        val index = (offset.y / itemHeight).toInt().coerceIn(0, alphabet.lastIndex)
                                        val letter = alphabet[index]
                                        hoveredLetter = letter
                                        firstLettersIndices[letter]?.let { listIndex ->
                                            coroutineScope.launch { listState.scrollToItem(listIndex) }
                                            view.performHapticFeedback(HapticFeedbackConstants.CLOCK_TICK)
                                        }
                                    },
                                    onDragEnd = { isDragging = false },
                                    onDragCancel = { isDragging = false },
                                    onVerticalDrag = { change, _ ->
                                        val y = change.position.y
                                        val itemHeight = size.height / alphabet.size.toFloat()
                                        val index = (y / itemHeight).toInt().coerceIn(0, alphabet.lastIndex)
                                        val letter = alphabet[index]
                                        if (hoveredLetter != letter) {
                                            hoveredLetter = letter
                                            firstLettersIndices[letter]?.let { listIndex ->
                                                coroutineScope.launch { listState.scrollToItem(listIndex) }
                                                view.performHapticFeedback(HapticFeedbackConstants.CLOCK_TICK)
                                            }
                                        }
                                    }
                                )
                            },
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.SpaceEvenly
                    ) {
                        alphabet.forEach { letter ->
                            Text(
                                text = letter.toString(),
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF16A34A),
                                modifier = Modifier
                                    .pointerInput(letter) {
                                        androidx.compose.foundation.gestures.detectTapGestures(
                                            onTap = {
                                                hoveredLetter = letter
                                                firstLettersIndices[letter]?.let { listIndex ->
                                                    coroutineScope.launch { listState.scrollToItem(listIndex) }
                                                    view.performHapticFeedback(HapticFeedbackConstants.CLOCK_TICK)
                                                }
                                            }
                                        )
                                    }
                                    .padding(vertical = 1.dp, horizontal = 4.dp)
                            )
                        }
                    }
                }
"""

content = content[:scroller_start] + new_scroller + content[scroller_end:]

# add missing imports if needed
if "import androidx.compose.foundation.border" not in content:
    content = content.replace("import androidx.compose.foundation.background", "import androidx.compose.foundation.background\nimport androidx.compose.foundation.border")
if "import androidx.compose.ui.draw.shadow" not in content:
    content = content.replace("import androidx.compose.ui.draw.clip", "import androidx.compose.ui.draw.clip\nimport androidx.compose.ui.draw.shadow")

with open('app/src/main/java/com/titan/zapdial/ContactsScreen.kt', 'w') as f:
    f.write(content)
