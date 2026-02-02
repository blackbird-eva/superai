#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PPT生成后端API - 整合本地PPT生成器与Web服务
替代Coze API，提供稳定的PPT生成服务
"""

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import os
import json
import uuid
from datetime import datetime
from pathlib import Path
import threading
import time

# 导入本地PPT生成器
from local_ppt_generator import LocalPPTGenerator

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
UPLOAD_FOLDER = Path("media/ppt_files")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
GENERATED_FOLDER = Path("generated_ppts")
GENERATED_FOLDER.mkdir(parents=True, exist_ok=True)

# 全局变量
ppt_generator = LocalPPTGenerator(output_dir=str(GENERATED_FOLDER))
generation_tasks = {}  # 存储生成任务状态

# HTML模板用于测试页面
TEST_PAGE_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PPT生成API测试</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .form-group { margin: 20px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        textarea, input, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        textarea { height: 120px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { margin: 20px 0; padding: 15px; border-radius: 4px; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .task-status { background: #e2e3e5; border: 1px solid #d6d8db; color: #383d41; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 PPT生成API测试界面</h1>
        
        <form id="generateForm">
            <div class="form-group">
                <label>输入内容 (文本或选择模板):</label>
                <textarea name="content" placeholder="请输入要生成PPT的文本内容...\n支持Markdown格式，会自动解析标题和要点"></textarea>
            </div>
            
            <div class="form-group">
                <label>或选择模板:</label>
                <select name="template">
                    <option value="">-- 自定义内容 --</option>
                    <option value="business_report">商业报告</option>
                    <option value="tech_presentation">技术演示</option>
                    <option value="education_training">教育培训</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>PPT标题:</label>
                <input type="text" name="title" placeholder="输入PPT标题" value="智能生成演示文稿">
            </div>
            
            <div class="form-group">
                <label>主题风格:</label>
                <select name="theme">
                    <option value="business">商务简约</option>
                    <option value="tech">科技现代</option>
                    <option value="education">教育培训</option>
                    <option value="creative">创意活泼</option>
                    <option value="academic">学术正式</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>幻灯片数量:</label>
                <input type="number" name="slide_count" min="3" max="20" value="8">
            </div>
            
            <button type="submit">🚀 生成PPT</button>
        </form>
        
        <div id="result"></div>
        
        <div id="taskStatus" style="display:none;">
            <h3>生成进度</h3>
            <div id="progressBar" style="width: 100%; background: #f0f0f0; border-radius: 4px; overflow: hidden;">
                <div id="progressFill" style="height: 20px; background: #007bff; width: 0%; transition: width 0.3s;"></div>
            </div>
            <p id="statusText">准备中...</p>
        </div>
    </div>
    
    <script>
        let currentTaskId = null;
        
        document.getElementById('generateForm').onsubmit = async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            // 显示结果区域
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<div class="task-status">📋 提交生成任务...</div>';
            
            try {
                // 启动生成任务
                const response = await fetch('/api/generate_ppt', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    currentTaskId = result.task_id;
                    resultDiv.innerHTML = `<div class="success">✅ 任务已启动!<br>任务ID: ${result.task_id}</div>`;
                    
                    // 显示进度条
                    document.getElementById('taskStatus').style.display = 'block';
                    monitorTaskProgress(currentTaskId);
                } else {
                    resultDiv.innerHTML = `<div class="error">❌ 任务启动失败: ${result.message}</div>`;
                }
                
            } catch (error) {
                resultDiv.innerHTML = `<div class="error">❌ 请求失败: ${error.message}</div>`;
            }
        };
        
        async function monitorTaskProgress(taskId) {
            const progressFill = document.getElementById('progressFill');
            const statusText = document.getElementById('statusText');
            
            const checkProgress = async () => {
                try {
                    const response = await fetch(`/api/task_status/${taskId}`);
                    const status = await response.json();
                    
                    progressFill.style.width = status.progress + '%';
                    statusText.textContent = status.message;
                    
                    if (status.status === 'completed') {
                        progressFill.style.background = '#28a745';
                        statusText.textContent = '✅ 生成完成!';
                        
                        // 显示下载链接
                        document.getElementById('result').innerHTML += `
                            <div class="success">
                                ✅ PPT生成完成!<br>
                                文件: ${status.filename}<br>
                                <button onclick="downloadPPT('${status.filepath}')">📥 下载PPT</button>
                            </div>
                        `;
                        
                    } else if (status.status === 'failed') {
                        progressFill.style.background = '#dc3545';
                        statusText.textContent = '❌ 生成失败';
                        
                    } else {
                        // 继续监控
                        setTimeout(checkProgress, 1000);
                    }
                    
                } catch (error) {
                    statusText.textContent = '监控进度时出错';
                    setTimeout(checkProgress, 2000);
                }
            };
            
            checkProgress();
        }
        
        function downloadPPT(filepath) {
            window.open(`/api/download/${encodeURIComponent(filepath)}`, '_blank');
        }
        
        // 模板选择联动
        document.querySelector('select[name="template"]').onchange = function() {
            const contentArea = document.querySelector('textarea[name="content"]');
            if (this.value) {
                contentArea.placeholder = `已选择${this.options[this.selectedIndex].text}模板，可留空使用默认内容`;
            } else {
                contentArea.placeholder = '请输入要生成PPT的文本内容...';
            }
        };
    </script>
</body>
</html>
'''}

@app.route('/')
def index():
    """首页 - 显示测试页面"""
    return render_template_string(TEST_PAGE_HTML)

@app.route('/api/generate_ppt', methods=['POST'])
def generate_ppt_api():
    """API: 生成PPT"""
    try:
        data = request.get_json()
        
        # 提取参数
        content = data.get('content', '').strip()
        template = data.get('template', '')
        title = data.get('title', '智能生成PPT')
        theme = data.get('theme', 'business')
        slide_count = int(data.get('slide_count', 8))
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 存储任务状态
        generation_tasks[task_id] = {
            'status': 'queued',
            'progress': 0,
            'message': '任务已加入队列',
            'created_at': datetime.now().isoformat()
        }
        
        # 在后台线程中执行生成任务
        def generate_task():
            try:
                generation_tasks[task_id]['status'] = 'running'
                generation_tasks[task_id]['progress'] = 10
                generation_tasks[task_id]['message'] = '正在分析内容...'
                
                # 根据模板或内容生成PPT
                if template:
                    generation_tasks[task_id]['progress'] = 30
                    generation_tasks[task_id]['message'] = '使用模板生成内容...'
                    
                    result = ppt_generator.generate_from_template(
                        template_type=template,
                        title=title,
                        theme=theme
                    )
                else:
                    generation_tasks[task_id]['progress'] = 30
                    generation_tasks[task_id]['message'] = '正在解析文本内容...'
                    
                    result = ppt_generator.generate_from_text(
                        text=content,
                        title=title,
                        theme=theme,
                        slide_count=slide_count
                    )
                
                # 更新任务状态
                generation_tasks[task_id].update({
                    'status': 'completed',
                    'progress': 100,
                    'message': '生成完成',
                    'result': result,
                    'completed_at': datetime.now().isoformat()
                })
                
            except Exception as e:
                generation_tasks[task_id].update({
                    'status': 'failed',
                    'progress': 0,
                    'message': f'生成失败: {str(e)}',
                    'error': str(e),
                    'failed_at': datetime.now().isoformat()
                })
        
        # 启动后台任务
        thread = threading.Thread(target=generate_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'PPT生成任务已启动'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'请求处理失败: {str(e)}'
        }), 500

@app.route('/api/task_status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """API: 获取任务状态"""
    if task_id not in generation_tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    task = generation_tasks[task_id]
    
    response = {
        'task_id': task_id,
        'status': task['status'],
        'progress': task['progress'],
        'message': task['message']
    }
    
    if task['status'] == 'completed':
        response.update({
            'filename': task['result']['filename'],
            'filepath': task['result']['filepath'],
            'slide_count': task['result']['slide_count'],
            'file_size': task['result']['file_size']
        })
    
    elif task['status'] == 'failed':
        response['error'] = task.get('error', '未知错误')
    
    return jsonify(response)

@app.route('/api/download/<path:filepath>', methods=['GET'])
def download_ppt(filepath):
    """API: 下载PPT文件"""
    try:
        # 安全检查：确保文件在允许的目录中
        file_path = Path(filepath)
        if not file_path.exists():
            return jsonify({'error': '文件不存在'}), 404
        
        # 检查文件是否在生成的目录中
        if not str(file_path).startswith(str(GENERATED_FOLDER)):
            return jsonify({'error': '无权访问此文件'}), 403
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_path.name,
            mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        
    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

@app.route('/api/list_generated', methods=['GET'])
def list_generated_ppts():
    """API: 列出已生成的PPT文件"""
    try:
        files = []
        for file_path in GENERATED_FOLDER.glob('*.pptx'):
            stat = file_path.stat()
            files.append({
                'filename': file_path.name,
                'filepath': str(file_path),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
            })
        
        # 按创建时间倒序排列
        files.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            'success': True,
            'files': files,
            'count': len(files)
        })
        
    except Exception as e:
        return jsonify({'error': f'获取文件列表失败: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'service': 'Local PPT Generator API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'generated_folder': str(GENERATED_FOLDER.absolute())
    })

def main():
    """启动服务器"""
    print("🚀 启动本地PPT生成API服务...")
    print(f"📁 生成文件目录: {GENERATED_FOLDER.absolute()}")
    print("🌐 访问地址: http://localhost:5000")
    print("📋 API文档:")
    print("  POST /api/generate_ppt - 生成PPT")
    print("  GET  /api/task_status/<task_id> - 查询任务状态")
    print("  GET  /api/download/<filepath> - 下载PPT")
    print("  GET  /api/list_generated - 列出所有PPT")
    print("  GET  /health - 健康检查")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()
