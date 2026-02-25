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
