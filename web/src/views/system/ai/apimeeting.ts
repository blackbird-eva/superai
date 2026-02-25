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
