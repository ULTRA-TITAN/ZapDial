package com.titan.zapdial

import android.content.Context
import android.media.MediaRecorder
import android.os.Build
import android.os.Environment
import android.util.Log
import android.widget.Toast
import java.io.File

object CallRecorder {
    private var mediaRecorder: MediaRecorder? = null
    var isRecording = false
    var currentFilePath: String? = null

    fun startRecording(context: Context, phoneNumber: String) {
        if (isRecording) return

        try {
            val dir = context.getExternalFilesDir(Environment.DIRECTORY_RECORDINGS)
            if (dir != null && !dir.exists()) {
                dir.mkdirs()
            }
            val fileName = "ZapDial_Rec_${phoneNumber}_${System.currentTimeMillis()}.m4a"
            val file = File(dir, fileName)
            currentFilePath = file.absolutePath

            mediaRecorder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                MediaRecorder(context)
            } else {
                MediaRecorder()
            }.apply {
                setAudioSource(MediaRecorder.AudioSource.VOICE_COMMUNICATION)
                setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
                setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
                setOutputFile(file.absolutePath)
                prepare()
                start()
            }
            isRecording = true
            Toast.makeText(context, "Recording started", Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            e.printStackTrace()
            isRecording = false
            Toast.makeText(context, "Failed to start recording", Toast.LENGTH_SHORT).show()
        }
    }

    fun stopRecording(context: Context) {
        if (!isRecording) return
        try {
            mediaRecorder?.stop()
            mediaRecorder?.release()
            mediaRecorder = null
            isRecording = false
            Toast.makeText(context, "Recording saved: $currentFilePath", Toast.LENGTH_LONG).show()
        } catch (e: Exception) {
            e.printStackTrace()
            Toast.makeText(context, "Error stopping recording", Toast.LENGTH_SHORT).show()
        }
    }
}
