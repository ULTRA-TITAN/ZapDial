package com.titan.zapdial

import android.telecom.Call
import android.telecom.CallAudioState
import android.view.HapticFeedbackConstants
import android.widget.Toast
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import android.Manifest
import android.content.pm.PackageManager
import androidx.core.content.ContextCompat
import kotlin.math.absoluteValue
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

// --- Theme Colors from Home Screen ---
private val ColorCreamBackground = Color(0xFFFDFCFA)
private val ColorPureWhite = Color(0xFFFFFFFF)
private val ColorPureBlack = Color(0xFF2A2A2E)
private val ColorRedMissed = Color(0xFFB3574F)
private val ColorGreenSuccess = Color(0xFF4C8B62)
private val ColorSlateGray = Color(0xFF9A9AA2)
private val ColorAvatarText = Color(0xFF44444C)

private val AvatarColors = listOf(
    Color(0xFFAFC4E0), Color(0xFFAECBB8), Color(0xFFE0B3AE), Color(0xFFC9BEE0),
    Color(0xFFE0B8CB), Color(0xFFE0CBA6), Color(0xFFA9CFC9), Color(0xFFC7C7CE)
)

private fun getOngoingAvatarColor(name: String): Color {
    if (name.isBlank()) return ColorSlateGray
    val hash = name.hashCode().absoluteValue
    return AvatarColors[hash % AvatarColors.size]
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OngoingCallScreen(callerName: String = "Unknown Caller", callerNumber: String = "Unknown Number") {
    val context = LocalContext.current
    val view = LocalView.current
    
    // Core Call State bindings
    val activeCall by CallSessionManager.activeCall.collectAsState()
    val callState by CallSessionManager.callState.collectAsState()
    val audioState by CallSessionManager.audioState.collectAsState()
    val isMuted by CallSessionManager.isMuted.collectAsState()
    val isOnHold by CallSessionManager.isOnHold.collectAsState()
    val isRecording by CallSessionManager.isRecording.collectAsState()
    val allCalls by CallSessionManager.allCalls.collectAsState()
    val recordPermissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { isGranted ->
        if (isGranted) {
            CallSessionManager.toggleRecord(context)
        }
    }

    var showKeypad by remember { mutableStateOf(false) }
    var durationSeconds by remember { mutableStateOf(0) }
    var recordSeconds by remember { mutableStateOf(0) }

    
    var activeNumber = callerNumber
    var simLabel by remember { mutableStateOf<String?>(null) }
    val callDetails = activeCall?.details
    val accountHandle = callDetails?.accountHandle
    
    LaunchedEffect(accountHandle) {
        if (accountHandle != null) {
            val telecomManager = context.getSystemService(android.content.Context.TELECOM_SERVICE) as android.telecom.TelecomManager
            val label = telecomManager.getPhoneAccount(accountHandle)?.label?.toString()
            if (label != null) {
                if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_PHONE_STATE) == PackageManager.PERMISSION_GRANTED) {
                    val sims = CallManager.getAvailableSims(context)
                    if (sims.size > 1) {
                        val index = sims.indexOf(accountHandle)
                        simLabel = if (index != -1) "SIM ${index + 1} • $label" else label
                    }
                }
            }
        }
    }
    activeCall?.details?.handle?.schemeSpecificPart?.let {
        activeNumber = it
    }


    // Chronometer ticker
    LaunchedEffect(callState) {
        if (callState == Call.STATE_ACTIVE) {
            while (true) {
                delay(1000)
                durationSeconds++
            }
        }
    }
    
    LaunchedEffect(isRecording) {
        if (isRecording) {
            while(true) {
                delay(1000)
                recordSeconds++
            }
        } else {
            recordSeconds = 0
        }
    }

    
    val minutes = durationSeconds / 60
    val seconds = durationSeconds % 60
    val timeString = String.format("%02d:%02d", minutes, seconds)

    val isSpeakerOn = audioState?.route == CallAudioState.ROUTE_SPEAKER

    Box(
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
        ) {
            Box(
                contentAlignment = Alignment.Center,
                modifier = Modifier
                    .size(120.dp)
                    .clip(CircleShape)
                    .background(getOngoingAvatarColor(callerName))
            ) {
                Text(
                    text = callerName.take(1).uppercase(),
                    fontSize = 46.sp,
                    fontWeight = FontWeight.Light,
                    color = ColorAvatarText
                )
            }
            Spacer(modifier = Modifier.height(32.dp))
            Text(
                text = callerName,
                fontSize = 28.sp,
                fontWeight = FontWeight.Normal,
                color = ColorPureBlack
            )
            Spacer(modifier = Modifier.height(6.dp))
            Text(
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
            }
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
            }
            Text(
                text = "",
                fontSize = 0.sp,
                fontWeight = FontWeight.Light
            )
            Spacer(modifier = Modifier.height(28.dp))
            
            // Live Duration Pill
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center,
                modifier = Modifier
                    .clip(RoundedCornerShape(26.dp))
                    .background(ColorPureWhite)
                    .padding(horizontal = 20.dp, vertical = 10.dp)
            ) {
                val infiniteTransition = rememberInfiniteTransition()
                val dotAlpha by infiniteTransition.animateFloat(
                    initialValue = 1f,
                    targetValue = 0.2f,
                    animationSpec = infiniteRepeatable(
                        animation = tween(800, easing = LinearEasing),
                        repeatMode = RepeatMode.Reverse
                    ), label = "DotAlpha"
                )
                
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .clip(CircleShape)
                        .background(if (isRecording) ColorRedMissed.copy(alpha = dotAlpha) else ColorGreenSuccess.copy(alpha = if (isOnHold) 0f else dotAlpha))
                )
                Spacer(modifier = Modifier.width(10.dp))
                val recMinutes = recordSeconds / 60
                val recSecs = recordSeconds % 60
                val recString = String.format("%02d:%02d", recMinutes, recSecs)
                
                Text(
                    text = if (isRecording) "REC $recString" else if (isOnHold) "ON HOLD" else timeString,
                    fontSize = 16.sp,
                    color = if (isRecording) ColorRedMissed else ColorPureBlack,
                    fontWeight = FontWeight.Normal
                )
            }
        }

        // --- Compact Bottom Controls Cluster ---
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.BottomCenter)
                .padding(bottom = 40.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                CallActionGridButton(
                    icon = Icons.Default.PersonAdd,
                    label = "Add call",
                    isActive = false,
                    activeContainerColor = ColorSlateGray.copy(alpha = 0.1f),
                    activeIconColor = ColorPureBlack,
                    onClick = { Toast.makeText(context, "Add Call", Toast.LENGTH_SHORT).show() }
                )
                CallActionGridButton(
                    icon = Icons.Default.Dialpad,
                    label = "Keypad",
                    isActive = showKeypad,
                    activeContainerColor = ColorSlateGray.copy(alpha = 0.15f), 
                    activeIconColor = ColorPureBlack,
                    onClick = { showKeypad = true }
                )
                CallActionGridButton(
                    icon = Icons.Default.VolumeUp,
                    label = "Speaker",
                    isActive = isSpeakerOn,
                    activeContainerColor = ColorGreenSuccess.copy(alpha = 0.14f),
                    activeIconColor = ColorGreenSuccess,
                    onClick = { CallSessionManager.toggleSpeaker() }
                )
            }
            Spacer(modifier = Modifier.height(28.dp))
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                CallActionGridButton(
                    icon = Icons.Default.FiberManualRecord,
                    label = "Record",
                    isActive = isRecording,
                    activeContainerColor = ColorRedMissed.copy(alpha = 0.14f), 
                    activeIconColor = ColorRedMissed,
                    isRecordButton = true,
                    onClick = { 
                        CallSessionManager.toggleRecord(context)
                        view.performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)
                    }
                )
                CallActionGridButton(
                    icon = if (isOnHold) Icons.Default.PlayArrow else Icons.Default.Pause,
                    label = "Hold",
                    isActive = isOnHold,
                    activeContainerColor = ColorSlateGray.copy(alpha = 0.15f),
                    activeIconColor = ColorPureBlack,
                    onClick = { CallSessionManager.toggleHold() }
                )
                CallActionGridButton(
                    icon = if (isMuted) Icons.Default.MicOff else Icons.Default.Mic,
                    label = "Mute",
                    isActive = isMuted,
                    activeContainerColor = ColorSlateGray.copy(alpha = 0.15f),
                    activeIconColor = ColorPureBlack,
                    onClick = { CallSessionManager.toggleMute() }
                )
            }
            
            Spacer(modifier = Modifier.height(32.dp))

            // Bottom Full-Width End Call Bar
            Box(
                modifier = Modifier
                    .fillMaxWidth(0.85f)
                    .height(64.dp)
                    .clip(RoundedCornerShape(32.dp))
                    .background(ColorRedMissed)
                    .clickable {
                        CallSessionManager.rejectCall()
                        CallSessionManager.disconnectCall()
                    },
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.CallEnd,
                    contentDescription = "End Call",
                    tint = ColorPureWhite,
                    modifier = Modifier.size(32.dp)
                )
            }
        }
    }

    // --- In-Call DTMF Keypad Bottom Sheet ---
    if (showKeypad) {
        val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
        ModalBottomSheet(
            onDismissRequest = { showKeypad = false },
            sheetState = sheetState,
            containerColor = ColorPureWhite,
            dragHandle = { BottomSheetDefaults.DragHandle(color = ColorSlateGray) }
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp)
                    .padding(bottom = 32.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "Keypad",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Normal,
                    color = ColorPureBlack
                )
                Spacer(modifier = Modifier.height(32.dp))
                
                val keys = listOf(
                    listOf('1', '2', '3'),
                    listOf('4', '5', '6'),
                    listOf('7', '8', '9'),
                    listOf('*', '0', '#')
                )
                for (row in keys) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        for (key in row) {
                            Box(
                                contentAlignment = Alignment.Center,
                                modifier = Modifier
                                    .size(72.dp)
                                    .clip(CircleShape)
                                    .background(ColorCreamBackground)
                                    .clickable {
                                        CallSessionManager.playDtmfTone(key)
                                        view.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP)
                                    }
                            ) {
                                Text(
                                    text = key.toString(),
                                    fontSize = 32.sp,
                                    fontWeight = FontWeight.Light,
                                    color = ColorPureBlack
                                )
                            }
                        }
                    }
                    Spacer(modifier = Modifier.height(20.dp))
                }
            }
        }
    }
}

@Composable
fun CallActionGridButton(
    icon: ImageVector,
    label: String,
    isActive: Boolean,
    activeContainerColor: Color,
    activeIconColor: Color,
    isRecordButton: Boolean = false,
    onClick: () -> Unit
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()
    
    val scale by animateFloatAsState(targetValue = if (isPressed) 0.9f else 1f, label = "Scale")
    val view = LocalView.current

    val containerColor by animateColorAsState(
        targetValue = if (isActive) activeContainerColor else ColorPureWhite,
        label = "ContainerColor"
    )
    val iconColor by animateColorAsState(
        targetValue = if (isActive) activeIconColor else ColorSlateGray,
        label = "IconColor"
    )
    
    val infiniteTransition = rememberInfiniteTransition()
    val pulseBorderAlpha by infiniteTransition.animateFloat(
        initialValue = 0.2f,
        targetValue = 0.8f,
        animationSpec = infiniteRepeatable(
            animation = tween(800, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "PulseBorder"
    )

    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier
                .size(76.dp)
                .scale(scale)
                .clip(CircleShape)
                .background(containerColor)
                .let {
                    if (isRecordButton && isActive) {
                        it.border(2.dp, ColorRedMissed.copy(alpha = pulseBorderAlpha), CircleShape)
                    } else it
                }
                .clickable(
                    interactionSource = interactionSource,
                    indication = null, 
                    onClick = {
                        view.performHapticFeedback(HapticFeedbackConstants.CLOCK_TICK)
                        onClick()
                    }
                )
        ) {
            Icon(
                imageVector = icon,
                contentDescription = label,
                tint = iconColor,
                modifier = Modifier.size(36.dp)
            )
        }
        Spacer(modifier = Modifier.height(10.dp))
        Text(
            text = label,
            fontSize = 14.sp,
            color = ColorSlateGray,
            fontWeight = FontWeight.Normal
        )
    }
}
