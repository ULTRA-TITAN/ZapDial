import re

with open("/app/applet/app/src/main/java/com/titan/zapdial/IncomingCallScreen.kt", "r") as f:
    content = f.read()

# For SilenceSlider
old_silence_drag = """        val offset = remember { Animatable(0f) }
        val scope = rememberCoroutineScope()"""

new_silence_drag = """        val offset = remember { Animatable(0f) }
        val scope = rememberCoroutineScope()
        
        val dragChannel = remember { kotlinx.coroutines.channels.Channel<Float>(kotlinx.coroutines.channels.Channel.UNLIMITED) }
        LaunchedEffect(Unit) {
            for (dragAmount in dragChannel) {
                if (!isSilenced) {
                    offset.snapTo((offset.value + dragAmount).coerceIn(0f, maxDragPx))
                }
            }
        }"""

content = content.replace(old_silence_drag, new_silence_drag)

old_silence_on_drag = """                    ) { change, dragAmount ->
                        if (!isSilenced) {
                            change.consume()
                            scope.launch {
                                val newOffset = (offset.value + dragAmount).coerceIn(0f, maxDragPx)
                                offset.snapTo(newOffset)
                            }
                        }
                    }"""

new_silence_on_drag = """                    ) { change, dragAmount ->
                        if (!isSilenced) {
                            change.consume()
                            dragChannel.trySend(dragAmount)
                        }
                    }"""

content = content.replace(old_silence_on_drag, new_silence_on_drag)

# For AnswerDeclineSlider
old_ad_drag = """        val offset = remember { Animatable(0f) }
            val scope = rememberCoroutineScope()"""

new_ad_drag = """        val offset = remember { Animatable(0f) }
            val scope = rememberCoroutineScope()
            
            val dragChannel = remember { kotlinx.coroutines.channels.Channel<Float>(kotlinx.coroutines.channels.Channel.UNLIMITED) }
            LaunchedEffect(Unit) {
                for (dragAmount in dragChannel) {
                    offset.snapTo((offset.value + dragAmount).coerceIn(-maxDragPx, maxDragPx))
                }
            }"""

content = content.replace(old_ad_drag, new_ad_drag)

old_ad_on_drag = """                        ) { change, dragAmount ->
                            change.consume()
                            scope.launch {
                                val newOffset = (offset.value + dragAmount).coerceIn(-maxDragPx, maxDragPx)
                                offset.snapTo(newOffset)
                            }
                        }"""

new_ad_on_drag = """                        ) { change, dragAmount ->
                            change.consume()
                            dragChannel.trySend(dragAmount)
                        }"""

content = content.replace(old_ad_on_drag, new_ad_on_drag)

with open("/app/applet/app/src/main/java/com/titan/zapdial/IncomingCallScreen.kt", "w") as f:
    f.write(content)

