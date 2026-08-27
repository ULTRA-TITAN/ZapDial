import re

with open("app/src/main/java/com/titan/zapdial/SettingsScreen.kt", "r") as f:
    content = f.read()

imports = """
import android.Manifest
import android.content.pm.PackageManager
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.compose.material.icons.filled.SimCard
import androidx.compose.material.icons.filled.Phone
"""
content = re.sub(r'import android\.provider\.BlockedNumberContract', 'import android.provider.BlockedNumberContract\n' + imports, content)

state_insert = """    var mistouchPrevention by remember {"""
new_state = """    var defaultSimSlot by remember { mutableStateOf(sharedPrefs.getInt("KEY_DEFAULT_SIM_SLOT", -1)) }
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

    var mistouchPrevention by remember {"""
content = content.replace(state_insert, new_state)

sim_row = """
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
"""

content = content.replace("            Spacer(modifier = Modifier.height(24.dp))\n            HorizontalDivider(color = Color(0xFFE2E8F0))\n            Spacer(modifier = Modifier.height(24.dp))", sim_row)

with open("app/src/main/java/com/titan/zapdial/SettingsScreen.kt", "w") as f:
    f.write(content)

