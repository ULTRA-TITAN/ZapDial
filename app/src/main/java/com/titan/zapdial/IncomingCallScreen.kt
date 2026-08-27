package com.titan.zapdial

import android.content.Context
import android.telecom.TelecomManager
import android.view.HapticFeedbackConstants
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.Orientation
import androidx.compose.foundation.gestures.draggable
import androidx.compose.foundation.gestures.rememberDraggableState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.launch
import kotlin.math.abs
import kotlin.math.roundToInt

@Composable
fun IncomingCallScreen(
    callerName: String = "Incoming Call",
    callerNumber: String = "Unknown",
    onAnswer: () -> Unit = { CallSessionManager.answerCall() },
    onReject: () -> Unit = { CallSessionManager.rejectCall() }
) {
    val context = LocalContext.current
    val view = LocalView.current
    val coroutineScope = rememberCoroutineScope()
    var isSilenced by remember { mutableStateOf(false) }

    // Background Gradient
    val avatarColor = getAvatarColor(callerName)
    val radialGradient = Brush.radialGradient(
        colors = listOf(avatarColor.copy(alpha = 0.5f), Color.Black),
        radius = 1500f
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .background(radialGradient)
            .systemBarsPadding()
            .padding(24.dp)
    ) {
        // --- Top Caller Identity Section ---
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.TopCenter)
                .padding(top = 20.dp)
        ) {
            // Pulsing Avatar Ring
            val infiniteTransition = rememberInfiniteTransition()
            val pulseScale by infiniteTransition.animateFloat(
                initialValue = 1f,
                targetValue = 1.6f,
                animationSpec = infiniteRepeatable(
                    animation = tween(2000, easing = CubicBezierEasing(0.4f, 0.0f, 0.2f, 1f)),
                    repeatMode = RepeatMode.Restart
                ),
                label = "PulseScale"
            )
            val pulseAlpha by infiniteTransition.animateFloat(
                initialValue = 0.8f,
                targetValue = 0f,
                animationSpec = infiniteRepeatable(
                    animation = tween(2000, easing = CubicBezierEasing(0.4f, 0.0f, 0.2f, 1f)),
                    repeatMode = RepeatMode.Restart
                ),
                label = "PulseAlpha"
            )

            Box(contentAlignment = Alignment.Center) {
                // Pulsing ring
                Box(
                    modifier = Modifier
                        .size(160.dp)
                        .scale(pulseScale)
                        .clip(CircleShape)
                        .background(avatarColor.copy(alpha = pulseAlpha))
                )
                // Main Avatar
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier
                        .size(120.dp)
                        .clip(CircleShape)
                        .background(avatarColor)
                ) {
                    Text(
                        text = callerName.take(1).uppercase(),
                        fontSize = 48.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color.White
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(32.dp))
            
            Text(
                text = "MOBILE",
                fontSize = 18.sp,
                letterSpacing = 1.2.sp,
                fontWeight = FontWeight.Medium,
                color = Color(0xFFB8C0CC)
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = callerName,
                fontSize = 42.sp,
                fontWeight = FontWeight.SemiBold,
                color = Color.White
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = callerNumber,
                fontSize = 18.sp,
                color = Color(0xFF94A3B8)
            )
            Spacer(modifier = Modifier.height(16.dp))
            
            // Status Pill
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center,
                modifier = Modifier
                    .clip(CircleShape)
                    .background(Color.White.copy(alpha = 0.14f))
                    .padding(horizontal = 16.dp, vertical = 6.dp)
            ) {
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .clip(CircleShape)
                        .background(if (isSilenced) Color(0xFF94A3B8) else Color(0xFF4ADE80))
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = if (isSilenced) "Silenced" else "Incoming call",
                    fontSize = 18.sp,
                    color = Color.White,
                    fontWeight = FontWeight.Medium
                )
            }
        }

        // --- Bottom Sliders Section ---
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.BottomCenter)
                .padding(bottom = 48.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Horizontal Silence Slider
            val silenceWidth = 240.dp
            val silenceHandleSize = 42.dp
            val density = LocalDensity.current
            val maxSilenceOffset = with(density) { (silenceWidth - silenceHandleSize).toPx() }
            val silenceThreshold = maxSilenceOffset * 0.6f
            
            val silenceOffset = remember { Animatable(0f) }
            
            Box(
                modifier = Modifier
                    .width(silenceWidth)
                    .height(54.dp)
                    .clip(CircleShape)
                    .background(Color.White.copy(alpha = 0.1f))
                    .border(1.dp, Color.White.copy(alpha = 0.2f), CircleShape),
                contentAlignment = Alignment.CenterStart
            ) {
                // Fill behind handle
                Box(
                    modifier = Modifier
                        .width(with(density) { silenceOffset.value.toDp() + silenceHandleSize })
                        .fillMaxHeight()
                        .clip(CircleShape)
                        .background(Color.White.copy(alpha = 0.2f))
                )
                
                Text(
                    text = "Slide to silence",
                    color = Color.White.copy(alpha = 0.5f),
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.align(Alignment.Center)
                )

                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier
                        .offset { IntOffset(silenceOffset.value.roundToInt(), 0) }
                        .size(silenceHandleSize)
                        .padding(4.dp)
                        .clip(CircleShape)
                        .background(Color.White)
                        .draggable(
                            orientation = Orientation.Horizontal,
                            state = rememberDraggableState { delta ->
                                if (!isSilenced) {
                                    val newOffset = (silenceOffset.value + delta).coerceIn(0f, maxSilenceOffset)
                                    coroutineScope.launch { silenceOffset.snapTo(newOffset) }
                                }
                            },
                            onDragStopped = {
                                if (!isSilenced) {
                                    if (silenceOffset.value >= silenceThreshold) {
                                        coroutineScope.launch { 
                                            silenceOffset.animateTo(maxSilenceOffset) 
                                            isSilenced = true
                                            view.performHapticFeedback(HapticFeedbackConstants.CLOCK_TICK)
                                            try {
                                                val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as TelecomManager
                                                telecomManager.silenceRinger()
                                            } catch (e: Exception) {}
                                        }
                                    } else {
                                        coroutineScope.launch { 
                                            silenceOffset.animateTo(0f, spring(dampingRatio = Spring.DampingRatioMediumBouncy)) 
                                        }
                                    }
                                }
                            }
                        )
                ) {
                    Icon(
                        imageVector = Icons.Default.Notifications,
                        contentDescription = "Silence",
                        tint = Color(0xFF1E293B),
                        modifier = Modifier.size(18.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Bottom Dual-Direction Answer/Decline Slider
            val trackHeight = 74.dp
            val centerHandleSize = 64.dp
            BoxWithConstraints(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(trackHeight)
                    .clip(CircleShape)
                    .background(Color.White.copy(alpha = 0.1f))
                    .border(1.dp, Color.White.copy(alpha = 0.15f), CircleShape)
            ) {
                val maxOffset = with(density) { (maxWidth - centerHandleSize).toPx() / 2f }
                val threshold = maxOffset * 0.55f
                val dragOffset = remember { Animatable(0f) }
                
                // Track Icons
                Row(
                    modifier = Modifier.fillMaxSize().padding(horizontal = 24.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.Close, contentDescription = "Decline", tint = Color(0xFFDC2626), modifier = Modifier.size(28.dp))
                    Icon(Icons.Default.Call, contentDescription = "Answer", tint = Color(0xFF16A34A), modifier = Modifier.size(28.dp))
                }

                // Dynamic Gradient Fill
                if (dragOffset.value < 0) {
                    val progress = abs(dragOffset.value) / maxOffset
                    Box(
                        modifier = Modifier
                            .fillMaxHeight()
                            .width(with(density) { (abs(dragOffset.value) + centerHandleSize.toPx() / 2).toDp() } + (centerHandleSize / 2))
                            .align(Alignment.CenterStart)
                            .clip(CircleShape)
                            .background(
                                Brush.horizontalGradient(
                                    colors = listOf(Color(0xFFDC2626).copy(alpha = progress), Color.Transparent)
                                )
                            )
                    )
                } else if (dragOffset.value > 0) {
                    val progress = dragOffset.value / maxOffset
                    Box(
                        modifier = Modifier
                            .fillMaxHeight()
                            .width(with(density) { (dragOffset.value + centerHandleSize.toPx() / 2).toDp() } + (centerHandleSize / 2))
                            .align(Alignment.CenterEnd)
                            .clip(CircleShape)
                            .background(
                                Brush.horizontalGradient(
                                    colors = listOf(Color.Transparent, Color(0xFF16A34A).copy(alpha = progress))
                                )
                            )
                    )
                }

                // Center Handle
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier
                        .align(Alignment.Center)
                        .offset { IntOffset(dragOffset.value.roundToInt(), 0) }
                        .size(centerHandleSize)
                        .padding(4.dp)
                        .clip(CircleShape)
                        .background(Color.White)
                        .draggable(
                            orientation = Orientation.Horizontal,
                            state = rememberDraggableState { delta ->
                                coroutineScope.launch {
                                    val current = dragOffset.value
                                    val newOffset = (current + delta).coerceIn(-maxOffset, maxOffset)
                                    dragOffset.snapTo(newOffset)
                                    
                                    // Haptic tick when crossing threshold
                                    if (abs(current) < threshold && abs(newOffset) >= threshold) {
                                        view.performHapticFeedback(HapticFeedbackConstants.CLOCK_TICK)
                                    }
                                }
                            },
                            onDragStopped = {
                                coroutineScope.launch {
                                    if (dragOffset.value <= -threshold) {
                                        dragOffset.animateTo(-maxOffset)
                                        onReject()
                                    } else if (dragOffset.value >= threshold) {
                                        dragOffset.animateTo(maxOffset)
                                        onAnswer()
                                    } else {
                                        dragOffset.animateTo(0f, spring(dampingRatio = Spring.DampingRatioMediumBouncy))
                                    }
                                }
                            }
                        )
                ) {
                    val iconTint = when {
                        dragOffset.value <= -threshold -> Color(0xFFDC2626)
                        dragOffset.value >= threshold -> Color(0xFF16A34A)
                        else -> Color(0xFF1E293B)
                    }
                    val handleIcon = when {
                        dragOffset.value <= -threshold -> Icons.Default.Close
                        else -> Icons.Default.Call
                    }
                    Icon(
                        imageVector = handleIcon,
                        contentDescription = "Handle",
                        tint = iconTint,
                        modifier = Modifier.size(32.dp)
                    )
                }
            }
        }
    }
}
