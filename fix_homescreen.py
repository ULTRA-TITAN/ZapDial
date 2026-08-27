import re

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'r') as f:
    content = f.read()

# Add imports for Snackbar
imports = """
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.SnackbarResult
import androidx.compose.runtime.rememberCoroutineScope
import kotlinx.coroutines.delay
"""
content = content.replace("import androidx.compose.material3.Text", "import androidx.compose.material3.Text" + imports)

# Add snackbar state inside HomeScreen()
snackbar_state = """
    val snackbarHostState = remember { SnackbarHostState() }
    val coroutineScope = rememberCoroutineScope()
"""
content = content.replace("    var hasCallLogPermission by remember {", snackbar_state + "\n    var hasCallLogPermission by remember {")

# Wrap LazyColumn inside a Box and add SnackbarHost
old_lazy_column = """    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(ColorCreamBackground)
            .padding(horizontal = 16.dp),
        contentPadding = PaddingValues(vertical = 16.dp)
    ) {"""
new_lazy_column = """    Box(modifier = Modifier.fillMaxSize()) {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(ColorCreamBackground)
            .padding(horizontal = 16.dp),
        contentPadding = PaddingValues(vertical = 16.dp)
    ) {"""
content = content.replace(old_lazy_column, new_lazy_column)

old_end_of_lazy = """                    callLogPermissionLauncher.launch(Manifest.permission.READ_CALL_LOG)
                }
            }
        }
    }

    // --- Bottom Sheets & Modals ---"""

new_end_of_lazy = """                    callLogPermissionLauncher.launch(Manifest.permission.READ_CALL_LOG)
                }
            }
        }
    }
        SnackbarHost(
            hostState = snackbarHostState,
            modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 64.dp)
        )
    }

    // --- Bottom Sheets & Modals ---"""
content = content.replace(old_end_of_lazy, new_end_of_lazy)

# Update the CallHistoryItemCard onDelete callback logic in HomeScreen
old_on_delete_call = """CallHistoryItemCard(item = call, onDelete = { deletedItem -> callHistory = callHistory.filter { it.id != deletedItem.id } })"""
new_on_delete_call = """CallHistoryItemCard(item = call, onDelete = { deletedItem ->
                    val previousHistory = callHistory
                    callHistory = callHistory.filter { it.id != deletedItem.id }
                    
                    coroutineScope.launch {
                        val result = snackbarHostState.showSnackbar(
                            message = "Call log deleted",
                            actionLabel = "UNDO",
                            duration = androidx.compose.material3.SnackbarDuration.Short
                        )
                        if (result == SnackbarResult.ActionPerformed) {
                            callHistory = previousHistory
                        } else {
                            kotlinx.coroutines.GlobalScope.launch(kotlinx.coroutines.Dispatchers.IO) {
                                try {
                                    context.contentResolver.delete(
                                        android.provider.CallLog.Calls.CONTENT_URI,
                                        "${android.provider.CallLog.Calls._ID} = ?",
                                        arrayOf(deletedItem.id)
                                    )
                                } catch (e: Exception) {
                                    e.printStackTrace()
                                }
                            }
                        }
                    }
                })"""
content = content.replace(old_on_delete_call, new_on_delete_call)

# Now, we need to remove the hard-delete from CallHistoryItemCard
old_hard_delete = """                            kotlinx.coroutines.GlobalScope.launch(kotlinx.coroutines.Dispatchers.IO) {
                                try {
                                    context.contentResolver.delete(
                                        CallLog.Calls.CONTENT_URI,
                                        "${CallLog.Calls._ID} = ?",
                                        arrayOf(item.id)
                                    )
                                } catch (e: Exception) {
                                    e.printStackTrace()
                                }
                            }
                            onDelete(item)"""
new_hard_delete = """                            onDelete(item)"""
content = content.replace(old_hard_delete, new_hard_delete)

with open('app/src/main/java/com/titan/zapdial/HomeScreen.kt', 'w') as f:
    f.write(content)
