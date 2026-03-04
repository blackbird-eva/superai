import { request } from '/@/utils/service';

/**
 * 开始录音
 */
export function StartRecording(data: { meeting_id: number; title: string }) {
    return request({
        url: '/api/system/meeting/recording/start/',
        method: 'post',
        data: data,
    });
}

/**
 * 暂停录音
 */
export function PauseRecording(data: { meeting_id: number; recording_time: string }) {
    return request({
        url: '/api/system/meeting/recording/pause/',
        method: 'post',
        data: data,
    });
}

/**
 * 继续录音
 */
export function ResumeRecording(data: { meeting_id: number }) {
    return request({
        url: '/api/system/meeting/recording/resume/',
        method: 'post',
        data: data,
    });
}

/**
 * 停止录音
 */
export function StopRecording(data: { meeting_id: number; title: string; recording_time: string }) {
    return request({
        url: '/api/system/meeting/recording/stop/',
        method: 'post',
        data: data,
    });
}

/**
 * 添加录音标记
 */
export function AddRecordingMark(data: { meeting_id: number; mark_time: string; label: string }) {
    return request({
        url: '/api/system/meeting/recording/mark/',
        method: 'post',
        data: data,
    });
}

/**
 * 保存录音文件
 */
export function SaveRecordingFile(data: { meeting_id: number; title: string; recording_time: string; file_data: string }) {
    return request({
        url: '/api/system/meeting/recording/save/',
        method: 'post',
        data: data,
    });
}

/**
 * 获取录音文件路径
 */
export function GetRecordingFilePath(meeting_id: number) {
    return request({
        url: `/api/system/meeting/recording/file/${meeting_id}/`,
        method: 'get',
    });
}

/**
 * 下载录音文件
 */
export function DownloadRecordingFile(file_path: string) {
    return request({
        url: '/api/system/meeting/recording/download/',
        method: 'get',
        params: { file_path },
        responseType: 'blob',
    });
}

/**
 * 语音转文本（调用 SiliconFlow API）
 */
export async function TranscribeAudio(audioBlob: Blob, apiKey: string = '') {
    console.log('开始调用语音转文本 API...')
    console.log('音频文件大小:', audioBlob.size, 'bytes')
    console.log('音频文件类型:', audioBlob.type)

    const formData = new FormData();
    formData.append('file', audioBlob, 'audio.wav');
    formData.append('model', 'TeleAI/TeleSpeechASR');

    try {
        const response = await fetch('https://api.siliconflow.cn/v1/audio/transcriptions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
            },
            body: formData,
        });

        console.log('API 响应状态:', response.status, response.statusText)

        if (!response.ok) {
            let errorData
            try {
                errorData = await response.json()
            } catch (e) {
                errorData = await response.text()
            }

            console.error('API 错误响应:', errorData)

            // 尝试从不同格式中提取错误信息
            let errorMessage = `API request failed with status ${response.status}`
            if (typeof errorData === 'object' && errorData !== null) {
                errorMessage = errorData.message ||
                               errorData.error ||
                               errorData.detail ||
                               JSON.stringify(errorData)
            } else if (typeof errorData === 'string') {
                errorMessage = errorData
            }

            throw new Error(errorMessage)
        }

        const result = await response.json()
        console.log('API 成功响应:', result)
        console.log('API 响应类型:', typeof result)
        
        // 详细记录返回数据的结构
        if (typeof result === 'object' && result !== null) {
            console.log('API 响应对象的所有字段:', Object.keys(result))
            for (const key in result) {
                const value = result[key]
                const valueType = typeof value
                const valuePreview = valueType === 'string' ? `"${value.substring(0, 100)}${value.length > 100 ? '...' : ''}"` : valueType
                console.log(`  - ${key}: ${valuePreview}`)
            }
        }
        
        return result
    } catch (error: any) {
        console.error('语音转文本 API 调用异常:', error)
        throw error
    }
}



