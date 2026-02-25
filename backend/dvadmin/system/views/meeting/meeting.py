# -*- coding: utf-8 -*-
"""
会议录音管理接口
Created on: 2026-01-27
"""
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from dvadmin.utils.json_response import SuccessResponse, ErrorResponse


class StartRecordingView(APIView):
    """
    开始录音接口
    """
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def post(self, request):
        """
        开始录音
        """
        try:
            meeting_id = request.data.get('meeting_id')
            title = request.data.get('title', '未知会议')

            if not meeting_id:
                return ErrorResponse(msg="会议ID不能为空", code=400)

            print(f"[录音] 开始录音 - 会议ID: {meeting_id}, 会议标题: {title}")

            # 返回录音信息
            return SuccessResponse(
                data={
                    'meeting_id': meeting_id,
                    'title': title,
                    'status': 'recording',
                    'start_time': '开始录音时间戳',
                    'message': '录音已开始'
                },
                msg="录音已开始"
            )

        except Exception as e:
            print(f"[录音] 开始录音失败: {str(e)}")
            return ErrorResponse(msg=f"开始录音失败: {str(e)}", code=500)


class PauseRecordingView(APIView):
    """
    暂停录音接口
    """
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def post(self, request):
        """
        暂停录音
        """
        try:
            meeting_id = request.data.get('meeting_id')
            recording_time = request.data.get('recording_time', '00:00:00')

            if not meeting_id:
                return ErrorResponse(msg="会议ID不能为空", code=400)

            print(f"[录音] 暂停录音 - 会议ID: {meeting_id}, 已录音时长: {recording_time}")

            return SuccessResponse(
                data={
                    'meeting_id': meeting_id,
                    'status': 'paused',
                    'recording_time': recording_time,
                    'message': '录音已暂停'
                },
                msg="录音已暂停"
            )

        except Exception as e:
            print(f"[录音] 暂停录音失败: {str(e)}")
            return ErrorResponse(msg=f"暂停录音失败: {str(e)}", code=500)


class ResumeRecordingView(APIView):
    """
    继续录音接口
    """
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def post(self, request):
        """
        继续录音
        """
        try:
            meeting_id = request.data.get('meeting_id')

            if not meeting_id:
                return ErrorResponse(msg="会议ID不能为空", code=400)

            print(f"[录音] 继续录音 - 会议ID: {meeting_id}")

            return SuccessResponse(
                data={
                    'meeting_id': meeting_id,
                    'status': 'recording',
                    'message': '录音已继续'
                },
                msg="录音已继续"
            )

        except Exception as e:
            print(f"[录音] 继续录音失败: {str(e)}")
            return ErrorResponse(msg=f"继续录音失败: {str(e)}", code=500)


class StopRecordingView(APIView):
    """
    停止录音接口
    """
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def post(self, request):
        """
        停止录音
        """
        try:
            meeting_id = request.data.get('meeting_id')
            recording_time = request.data.get('recording_time', '00:00:00')
            title = request.data.get('title', '未知会议')

            if not meeting_id:
                return ErrorResponse(msg="会议ID不能为空", code=400)

            print(f"[录音] 停止录音 - 会议ID: {meeting_id}, 会议标题: {title}, 总录音时长: {recording_time}")

            return SuccessResponse(
                data={
                    'meeting_id': meeting_id,
                    'title': title,
                    'status': 'completed',
                    'recording_time': recording_time,
                    'file_path': f'/recordings/meeting_{meeting_id}_{recording_time}.wav',
                    'message': '录音已结束'
                },
                msg="录音已结束"
            )

        except Exception as e:
            print(f"[录音] 停止录音失败: {str(e)}")
            return ErrorResponse(msg=f"停止录音失败: {str(e)}", code=500)


class AddRecordingMarkView(APIView):
    """
    添加录音标记接口
    """
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def post(self, request):
        """
        添加录音标记
        """
        try:
            meeting_id = request.data.get('meeting_id')
            mark_time = request.data.get('mark_time', '00:00:00')
            label = request.data.get('label', '')

            if not meeting_id:
                return ErrorResponse(msg="会议ID不能为空", code=400)

            print(f"[录音] 添加标记 - 会议ID: {meeting_id}, 标记时间: {mark_time}, 标记内容: {label}")

            return SuccessResponse(
                data={
                    'meeting_id': meeting_id,
                    'mark_time': mark_time,
                    'label': label,
                    'message': '标记已添加'
                },
                msg="标记已添加"
            )

        except Exception as e:
            print(f"[录音] 添加标记失败: {str(e)}")
            return ErrorResponse(msg=f"添加标记失败: {str(e)}", code=500)


class SaveRecordingFileView(APIView):
    """
    保存录音文件接口
    """
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def post(self, request):
        """
        保存录音文件
        """
        try:
            meeting_id = request.data.get('meeting_id')
            title = request.data.get('title', '未知会议')
            recording_time = request.data.get('recording_time', '00:00:00')
            file_data = request.data.get('file_data', '')

            if not meeting_id:
                return ErrorResponse(msg="会议ID不能为空", code=400)

            print(f"[录音] 保存录音文件 - 会议ID: {meeting_id}, 会议标题: {title}, 录音时长: {recording_time}")
            print(f"[录音] 文件数据长度: {len(file_data)}")

            # 生成文件路径（模拟）
            file_path = f"/recordings/meeting_{meeting_id}_{recording_time.replace(':', '-')}.wav"

            return SuccessResponse(
                data={
                    'meeting_id': meeting_id,
                    'title': title,
                    'recording_time': recording_time,
                    'file_path': file_path,
                    'message': '文件已保存'
                },
                msg="录音文件已保存"
            )

        except Exception as e:
            print(f"[录音] 保存录音文件失败: {str(e)}")
            return ErrorResponse(msg=f"保存录音文件失败: {str(e)}", code=500)


class GetRecordingFilePathView(APIView):
    """
    获取录音文件路径接口
    """
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def get(self, request, meeting_id):
        """
        获取录音文件路径
        """
        try:
            if not meeting_id:
                return ErrorResponse(msg="会议ID不能为空", code=400)

            print(f"[录音] 获取录音文件路径 - 会议ID: {meeting_id}")

            # 生成文件路径（模拟）
            file_path = f"/recordings/meeting_{meeting_id}.wav"
            file_url = f"/api/media/recordings/meeting_{meeting_id}.wav"

            return SuccessResponse(
                data={
                    'meeting_id': meeting_id,
                    'file_path': file_path,
                    'file_url': file_url,
                    'message': '获取成功'
                },
                msg="获取文件路径成功"
            )

        except Exception as e:
            print(f"[录音] 获取录音文件路径失败: {str(e)}")
            return ErrorResponse(msg=f"获取文件路径失败: {str(e)}", code=500)


class DownloadRecordingFileView(APIView):
    """
    下载录音文件接口
    """
    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def get(self, request):
        """
        下载录音文件
        """
        try:
            file_path = request.GET.get('file_path')

            if not file_path:
                return ErrorResponse(msg="文件路径不能为空", code=400)

            print(f"[录音] 下载录音文件 - 文件路径: {file_path}")

            return SuccessResponse(
                data={
                    'file_path': file_path,
                    'download_url': f'/api/download?path={file_path}',
                    'message': '下载链接已生成'
                },
                msg="获取下载链接成功"
            )

        except Exception as e:
            print(f"[录音] 下载录音文件失败: {str(e)}")
            return ErrorResponse(msg=f"下载文件失败: {str(e)}", code=500)

