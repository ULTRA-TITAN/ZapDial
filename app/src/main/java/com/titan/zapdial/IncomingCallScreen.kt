package com.titan.zapdial

import android.content.Context
import android.telecom.TelecomManager
import android.view.HapticFeedbackConstants
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.outlined.Notifications
import androidx.compose.material.icons.outlined.NotificationsOff
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.launch
import kotlin.math.absoluteValue
import kotlin.math.roundToInt

private val PageBackground = Color(0xFFFDFCFA)
private val TextPrimary = Color(0xFF2A2A2E)
private val TextSecondary = Color(0xFF9A9AA2)
private val ColorGreen = Color(0xFF4C8B62)
private val ColorRed = Color(0xFFB3574F)
private val SliderTrack = Color(0xFFF1F1EE)
private val InactiveIcon = Color(0xFFC6C6C2)
private val AvatarBorder = Color(0xFFECECEA)
private val AvatarText = Color(0xFF44444C)
private val AvatarColors = listOf(
    Color(0xFFAFC4E0), Color(0xFFAECBB8), Color(0xFFE0B3AE), Color(0xFFC9BEE0),
    Color(0xFFE0B8CB), Color(0xFFE0CBA6), Color(0xFFA9CFC9), Color(0xFFC7C7CE)
)

private fun getAvatarColorLocal(name: String): Color {
    if (name.isBlank()) return AvatarColors.last()
    val hash = name.hashCode().absoluteValue
    return AvatarColors[hash % AvatarColors.size]
}

@Composable
fun IncomingCallScreen(
    callerName: String = "Incoming Call",
    callerNumber: String = "Unknown",
    onAnswer: () -> Unit = { CallSessionManager.answerCall() },
    onReject: () -> Unit = { CallSessionManager.rejectCall() }
) {
    val context = LocalContext.current
    val view = LocalView.current
    val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as TelecomManager

    // Fallbacks
    val displayLocation = "INCOMING CALL"
    val displayName = if (callerName.isNotBlank() && callerName != "Unknown Number") callerName else "?"
    val displayAvatarStr = displayName.take(1).uppercase()
    val isNumberOnly = callerName == callerNumber || callerName == "Unknown" || callerName == "Unknown Number"
    
    val actualDisplayName = if (isNumberOnly) callerNumber else callerName
    val actualDisplayNumber = if (isNumberOnly) "Mobile" else callerNumber

    Column(
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
        ) {
            Text(
                text = displayLocation,
                fontSize = 12.5.sp,
                fontWeight = FontWeight.Normal,
                color = TextSecondary,
                modifier = Modifier.padding(bottom = 16.dp)
            )

            Box(
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
            }

            Text(
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
            )

            Row(
                modifier = Modifier
                    .background(Color.White, RoundedCornerShape(16.dp))
                    .border(0.5.dp, AvatarBorder, RoundedCornerShape(16.dp))
                    .padding(vertical = 7.dp, horizontal = 14.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(7.dp)
                        .clip(CircleShape)
                        .background(ColorGreen)
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = "Incoming call",
                    fontSize = 12.5.sp,
                    fontWeight = FontWeight.Medium,
                    color = TextPrimary
                )
            }
        }

        // CONTROLS SECTION
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            SilenceSlider(telecomManager = telecomManager, view = view)
            Spacer(modifier = Modifier.height(18.dp))
            AnswerDeclineSlider(view = view, onAnswer = onAnswer, onReject = onReject)
        }
    }
}

@Composable
fun SilenceSlider(telecomManager: TelecomManager, view: android.view.View) {
    var isSilenced by remember { mutableStateOf(false) }
    val density = LocalDensity.current
    val handleSize = 38.dp
    val padding = 4.dp
    val trackHeight = 46.dp

    BoxWithConstraints(
        modifier = Modifier
            .fillMaxWidth(0.65f)
            .height(trackHeight)
            .clip(RoundedCornerShape(23.dp))
            .background(SliderTrack),
        contentAlignment = Alignment.CenterStart
    ) {
        val trackWidthPx = constraints.maxWidth.toFloat()
        val handleWidthPx = with(density) { handleSize.toPx() }
        val paddingPx = with(density) { padding.toPx() }
        val maxDragPx = trackWidthPx - handleWidthPx - (paddingPx * 2)
        
        val offset = remember { Animatable(0f) }
        val scope = rememberCoroutineScope()
        
        val dragChannel = remember { kotlinx.coroutines.channels.Channel<Float>(kotlinx.coroutines.channels.Channel.UNLIMITED) }
        LaunchedEffect(Unit) {
            for (dragAmount in dragChannel) {
                if (!isSilenced) {
                    offset.snapTo((offset.value + dragAmount).coerceIn(0f, maxDragPx))
                }
            }
        }
        
        // Background trailing fill
        val currentFillWidthPx = offset.value + handleWidthPx + (paddingPx * 2)
        Box(
            modifier = Modifier
                .height(trackHeight)
                .width(with(density) { currentFillWidthPx.toDp() })
                .background(TextPrimary.copy(alpha = 0.08f), RoundedCornerShape(23.dp))
        )
        
        // Text
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Text(
                text = if (isSilenced) "Silenced" else "Slide to silence",
                color = TextPrimary.copy(alpha = if (isSilenced) 1f else (1f - (offset.value / maxDragPx))),
                fontSize = 13.sp,
                fontWeight = FontWeight.Medium
            )
        }
        
        // Handle
        Box(
            modifier = Modifier
                .padding(start = padding)
                .offset { IntOffset(offset.value.roundToInt(), 0) }
                .size(handleSize)
                .shadow(1.dp, CircleShape)
                .background(Color.White, CircleShape)
                .pointerInput(Unit) {
                    detectHorizontalDragGestures(
                        onDragEnd = {
                            if (offset.value > maxDragPx * 0.65f) {
                                scope.launch { offset.animateTo(maxDragPx, tween(300)) }
                                if (!isSilenced) {
                                    isSilenced = true
                                    try { telecomManager.silenceRinger() } catch(e: Exception) {}
                                    view.performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)
                                }
                            } else {
                                scope.launch { offset.animateTo(0f, spring(stiffness = Spring.StiffnessMediumLow)) }
                            }
                        },
                        onDragCancel = {
                            scope.launch { offset.animateTo(0f, spring(stiffness = Spring.StiffnessMediumLow)) }
                        }
                    ) { change, dragAmount ->
                        if (!isSilenced) {
                            change.consume()
                            dragChannel.trySend(dragAmount)
                        }
                    }
                },
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = if (isSilenced) Icons.Outlined.NotificationsOff else Icons.Outlined.Notifications,
                contentDescription = null,
                tint = TextPrimary,
                modifier = Modifier.size(18.dp)
            )
        }
    }
}

@Composable
fun AnswerDeclineSlider(view: android.view.View, onAnswer: () -> Unit, onReject: () -> Unit) {
    val density = LocalDensity.current
    val trackHeight = 72.dp
    val handleSize = 62.dp

    Column(modifier = Modifier.fillMaxWidth()) {
        BoxWithConstraints(
            modifier = Modifier
                .fillMaxWidth()
                .height(trackHeight)
                .clip(RoundedCornerShape(36.dp))
                .background(SliderTrack),
            contentAlignment = Alignment.Center
        ) {
            val trackWidthPx = constraints.maxWidth.toFloat()
            val handleWidthPx = with(density) { handleSize.toPx() }
            val maxDragPx = (trackWidthPx - handleWidthPx) / 2f
            
            val offset = remember { Animatable(0f) }
            val scope = rememberCoroutineScope()
            
            val dragChannel = remember { kotlinx.coroutines.channels.Channel<Float>(kotlinx.coroutines.channels.Channel.UNLIMITED) }
            LaunchedEffect(Unit) {
                for (dragAmount in dragChannel) {
                    offset.snapTo((offset.value + dragAmount).coerceIn(-maxDragPx, maxDragPx))
                }
            }
            
            // Left/Right Background Fills
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                if (offset.value < 0) {
                    val widthPx = offset.value.absoluteValue + (handleWidthPx / 2f)
                    Box(
                        modifier = Modifier
                            .width(with(density) { widthPx.toDp() })
                            .height(trackHeight)
                            .offset { IntOffset((-widthPx / 2f).roundToInt(), 0) }
                            .background(Brush.horizontalGradient(
                                0.0f to ColorRed.copy(alpha = 0.8f),
                                0.6f to ColorRed.copy(alpha = 0.2f),
                                1.0f to Color.Transparent
                            ))
                    )
                } else if (offset.value > 0) {
                    val widthPx = offset.value + (handleWidthPx / 2f)
                    Box(
                        modifier = Modifier
                            .width(with(density) { widthPx.toDp() })
                            .height(trackHeight)
                            .offset { IntOffset((widthPx / 2f).roundToInt(), 0) }
                            .background(Brush.horizontalGradient(
                                0.0f to Color.Transparent,
                                0.4f to ColorGreen.copy(alpha = 0.2f),
                                1.0f to ColorGreen.copy(alpha = 0.8f)
                            ))
                    )
                }
            }
            
            val threshold = maxDragPx * 0.55f
            
            val leftIconColor = if (offset.value <= -threshold) ColorRed else InactiveIcon
            val rightIconColor = if (offset.value >= threshold) ColorGreen else InactiveIcon
            val handleIconColor = when {
                offset.value <= -maxDragPx * 0.2f -> ColorRed
                offset.value >= maxDragPx * 0.2f -> ColorGreen
                else -> TextPrimary
            }
            val handleIcon = if (offset.value <= -maxDragPx * 0.2f) Icons.Default.Close else Icons.Default.Call
            
            Row(
                modifier = Modifier.fillMaxSize().padding(horizontal = 24.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(Icons.Default.Close, null, tint = leftIconColor, modifier = Modifier.size(24.dp))
                Icon(Icons.Default.Call, null, tint = rightIconColor, modifier = Modifier.size(24.dp))
            }
            
            // Handle
            Box(
                modifier = Modifier
                    .offset { IntOffset(offset.value.roundToInt(), 0) }
                    .size(handleSize)
                    .shadow(2.dp, CircleShape)
                    .background(Color.White, CircleShape)
                    .pointerInput(Unit) {
                        detectHorizontalDragGestures(
                            onDragEnd = {
                                scope.launch {
                                    if (offset.value <= -threshold) {
                                        offset.animateTo(-maxDragPx, tween(200))
                                        view.performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)
                                        onReject()
                                    } else if (offset.value >= threshold) {
                                        offset.animateTo(maxDragPx, tween(200))
                                        view.performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)
                                        onAnswer()
                                    } else {
                                        offset.animateTo(0f, spring(stiffness = Spring.StiffnessMediumLow))
                                    }
                                }
                            },
                            onDragCancel = {
                                scope.launch { offset.animateTo(0f, spring(stiffness = Spring.StiffnessMediumLow)) }
                            }
                        ) { change, dragAmount ->
                            change.consume()
                            dragChannel.trySend(dragAmount)
                        }
                    },
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = handleIcon,
                    contentDescription = null,
                    tint = handleIconColor,
                    modifier = Modifier.size(28.dp)
                )
            }
        }
        
        Spacer(modifier = Modifier.height(10.dp))
        
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 10.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text("Decline", fontSize = 12.sp, fontWeight = FontWeight.Medium, color = TextSecondary)
            Text("Answer", fontSize = 12.sp, fontWeight = FontWeight.Medium, color = TextSecondary)
        }
    }
}
