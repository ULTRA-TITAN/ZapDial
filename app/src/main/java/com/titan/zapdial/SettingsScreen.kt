package com.titan.zapdial

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Block
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import android.content.Intent
import android.provider.BlockedNumberContract

import android.Manifest
import android.content.pm.PackageManager
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.compose.material.icons.filled.SimCard
import androidx.compose.material.icons.filled.Phone


@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(onBack: () -> Unit) {
    val context = LocalContext.current
    val sharedPrefs = context.getSharedPreferences("ZapDialPrefs", Context.MODE_PRIVATE)
    
    var defaultSimSlot by remember { mutableStateOf(sharedPrefs.getInt("KEY_DEFAULT_SIM_SLOT", -1)) }
    var showSimSelectionDialog by remember { mutableStateOf(false) }
    var availableSims by remember { mutableStateOf<List<android.telecom.PhoneAccountHandle>>(emptyList()) }
    
    val phoneStatePermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            availableSims = CallManager.getAvailableSims(context)
            if (availableSims.isNotEmpty()) {
                showSimSelectionDialog = true
            } else {
                Toast.makeText(context, "No SIM cards found", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    if (showSimSelectionDialog) {
        AlertDialog(
            onDismissRequest = { showSimSelectionDialog = false },
            title = { Text("Default SIM", fontWeight = FontWeight.Bold) },
            text = {
                Column {
                    availableSims.forEachIndexed { index, handle ->
                        Row(
                            modifier = Modifier.fillMaxWidth().clickable {
                                defaultSimSlot = index
                                sharedPrefs.edit().putInt("KEY_DEFAULT_SIM_SLOT", index).apply()
                                showSimSelectionDialog = false
                            }.padding(16.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            RadioButton(selected = defaultSimSlot == index, onClick = null)
                            Spacer(Modifier.width(8.dp))
                            Text("SIM ${index + 1}: ${CallManager.getSimLabel(context, handle)}", fontSize = 16.sp)
                        }
                    }
                    Row(
                        modifier = Modifier.fillMaxWidth().clickable {
                            defaultSimSlot = -1
                            sharedPrefs.edit().putInt("KEY_DEFAULT_SIM_SLOT", -1).apply()
                            showSimSelectionDialog = false
                        }.padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        RadioButton(selected = defaultSimSlot == -1, onClick = null)
                        Spacer(Modifier.width(8.dp))
                        Text("Ask every time", fontSize = 16.sp)
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { showSimSelectionDialog = false }) { Text("Cancel") }
            }
        )
    }

    var mistouchPrevention by remember {
        mutableStateOf(sharedPrefs.getBoolean("KEY_MISTOUCH_PREVENTION", false))
    }
    
    var showFrequentContacts by remember {
        mutableStateOf(sharedPrefs.getBoolean("KEY_SHOW_FREQUENT", true))
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Settings", fontSize = 22.sp, fontWeight = FontWeight.Medium) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = Color(0xFFFDFCFA))
            )
        },
        containerColor = Color(0xFFFDFCFA)
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(24.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Mistouch Prevention",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color(0xFF0F172A)
                    )
                    Text(
                        text = "Confirm before placing calls",
                        fontSize = 14.sp,
                        color = Color(0xFF64748B)
                    )
                }
                Switch(
                    checked = mistouchPrevention,
                    onCheckedChange = { checked ->
                        mistouchPrevention = checked
                        sharedPrefs.edit().putBoolean("KEY_MISTOUCH_PREVENTION", checked).apply()
                    },
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = Color.White,
                        checkedTrackColor = Color(0xFF16A34A)
                    )
                )
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Show Favorites Bar",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color(0xFF0F172A)
                    )
                    Text(
                        text = "Display frequent contacts on home screen",
                        fontSize = 14.sp,
                        color = Color(0xFF64748B)
                    )
                }
                Switch(
                    checked = showFrequentContacts,
                    onCheckedChange = { checked ->
                        showFrequentContacts = checked
                        sharedPrefs.edit().putBoolean("KEY_SHOW_FREQUENT", checked).apply()
                    },
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = Color.White,
                        checkedTrackColor = Color(0xFF16A34A)
                    )
                )
            }
            

            Spacer(modifier = Modifier.height(24.dp))
            HorizontalDivider(color = Color(0xFFE2E8F0))
            Spacer(modifier = Modifier.height(24.dp))
            
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable {
                        if (ContextCompat.checkSelfPermission(context, Manifest.permission.READ_PHONE_STATE) == PackageManager.PERMISSION_GRANTED) {
                            availableSims = CallManager.getAvailableSims(context)
                            if (availableSims.isNotEmpty()) {
                                showSimSelectionDialog = true
                            } else {
                                Toast.makeText(context, "No SIM cards found", Toast.LENGTH_SHORT).show()
                            }
                        } else {
                            phoneStatePermissionLauncher.launch(Manifest.permission.READ_PHONE_STATE)
                        }
                    }
                    .padding(vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(Icons.Default.SimCard, contentDescription = "Calling Account", tint = Color(0xFF0F172A))
                Spacer(modifier = Modifier.width(16.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Calling Account",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color(0xFF0F172A)
                    )
                    Text(
                        text = if (defaultSimSlot == -1) "Ask every time" else "SIM ${defaultSimSlot + 1}",
                        fontSize = 14.sp,
                        color = Color(0xFF64748B)
                    )
                }
            }

            
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable {
                        try {
                            val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as android.telecom.TelecomManager
                            val intent = telecomManager.createManageBlockedNumbersIntent()
                            context.startActivity(intent)
                        } catch (e: Exception) {
                            try {
                                val intent = Intent("android.intent.action.MAIN")
                                intent.setClassName("com.android.phone", "com.android.phone.settings.BlockedNumberActivity")
                                context.startActivity(intent)
                            } catch (e2: Exception) {}
                        }
                    }
                    .padding(vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(Icons.Default.Block, contentDescription = "Blocked Numbers", tint = Color(0xFF0F172A))
                Spacer(modifier = Modifier.width(16.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Blocked Numbers",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color(0xFF0F172A)
                    )
                    Text(
                        text = "Manage blocked calls and texts",
                        fontSize = 14.sp,
                        color = Color(0xFF64748B)
                    )
                }
            }
        }
    }
}
