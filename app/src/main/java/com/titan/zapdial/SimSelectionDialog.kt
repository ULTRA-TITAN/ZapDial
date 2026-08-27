package com.titan.zapdial

import android.content.Context
import android.telecom.PhoneAccountHandle
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Call
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SimSelectionDialog(
    context: Context,
    availableSims: List<PhoneAccountHandle>,
    onSimSelected: (PhoneAccountHandle) -> Unit,
    onDismiss: () -> Unit
) {
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        containerColor = androidx.compose.ui.graphics.Color(0xFFFDFCFA)
    ) {
        Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
            Text(
                text = "Choose SIM for this call",
                fontSize = 20.sp,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.padding(bottom = 16.dp)
            )
            availableSims.forEachIndexed { index, handle ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onSimSelected(handle) }
                        .padding(vertical = 16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.Call, contentDescription = null)
                    Spacer(modifier = Modifier.width(16.dp))
                    Text(
                        text = "SIM ${index + 1}: ${CallManager.getSimLabel(context, handle)}",
                        fontSize = 18.sp
                    )
                }
            }
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}
