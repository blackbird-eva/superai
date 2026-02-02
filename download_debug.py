#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PPT下载调试工具
用于诊断PPT生成后无法打开的问题
"""

import requests
import json
import os
from datetime import datetime

# 配置信息
BASE_URL = "https://api.coze.cn"
WORKFLOW_ID = "7518128870178832422"
USER_ID = "test_user_001"
API_KEY = "pat_OpOtxYPsdoqHvzMezDkPm8Lr5U8iZyGhTzfWPtN9aXKfVuBnQjRxZyCmYwSaJtC"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def debug_workflow_execution():
    """
    调试工作流执行过程
    """
    print("=" * 80)
    print("🔍 开始调试PPT生成流程")
    print("=" * 80)
    
    # 1. 执行工作流
    print("\n📋 步骤1: 执行PPT生成工作流...")
    url = f"{BASE_URL}/v1/workflow/run"
    payload = {
        "workflow_id": WORKFLOW_ID,
        "parameters": {
            "input": "人工智能发展趋势分析报告"
        },
        "user_id": USER_ID
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   响应状态: {result.get('data', {}).get('status')}")
            
            # 检查响应结构
            print(f"   \n🔍 响应结构分析:")
            print(f"   - 是否有data字段: {'data' in result}")
            if 'data' in result:
                data = result['data']
                print(f"   - data中是否有status: {'status' in data}")
                print(f"   - data中是否有outputs: {'outputs' in data}")
                print(f"   - data中是否有file_list: {'file_list' in data}")
                
                if 'file_list' in data:
                    file_list = data['file_list']
                    print(f"   - file_list长度: {len(file_list)}")
                    
                    if file_list:
                        file_info = file_list[0]
                        print(f"   - 文件信息键: {list(file_info.keys())}")
                        print(f"   - file_url: {file_info.get('file_url', 'N/A')}")
                        print(f"   - file_name: {file_info.get('file_name', 'N/A')}")
                        print(f"   - file_type: {file_info.get('file_type', 'N/A')}")
                        
                        # 检查file_url是否有效
                        file_url = file_info.get('file_url')
                        if file_url:
                            print(f"   \n🌐 步骤2: 测试文件URL可访问性...")
                            test_file_url(file_url, file_info.get('file_name'))
                    else:
                        print("   ⚠️  file_list为空!")
                else:
                    print("   ❌ 响应中没有file_list字段!")
                    print(f"   完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            else:
                print("   ❌ 响应中没有data字段!")
                print(f"   完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
        else:
            print(f"   ❌ 请求失败: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 执行出错: {str(e)}")

def test_file_url(file_url, file_name):
    """
    测试文件URL的可访问性和内容
    """
    try:
        print(f"   正在访问: {file_url[:100]}...")
        
        # 测试URL是否可访问
        head_response = requests.head(file_url, timeout=30)
        print(f"   HEAD请求状态码: {head_response.status_code}")
        
        if head_response.status_code == 200:
            content_type = head_response.headers.get('content-type', '')
            content_length = head_response.headers.get('content-length', '未知')
            print(f"   内容类型: {content_type}")
            print(f"   文件大小: {content_length} bytes")
            
            # 检查内容类型是否正确
            if 'powerpoint' not in content_type.lower() and 'presentation' not in content_type.lower():
                print(f"   ⚠️  警告: 内容类型不是PPT格式: {content_type}")
            
            # 下载文件进行测试
            print(f"   \n⬇️  步骤3: 下载文件进行测试...")
            download_response = requests.get(file_url, timeout=60)
            print(f"   GET请求状态码: {download_response.status_code}")
            
            if download_response.status_code == 200:
                # 保存临时文件
                temp_file = f"temp_debug_{int(datetime.now().timestamp())}.pptx"
                
                with open(temp_file, 'wb') as f:
                    f.write(download_response.content)
                
                file_size = os.path.getsize(temp_file)
                print(f"   ✅ 文件下载成功!")
                print(f"   - 保存为: {temp_file}")
                print(f"   - 文件大小: {file_size} bytes ({file_size/1024:.1f} KB)")
                
                # 验证文件头
                validate_ppt_file_header(temp_file)
                
                # 清理临时文件
                os.remove(temp_file)
                print(f"   - 临时文件已清理")
            else:
                print(f"   ❌ 文件下载失败: {download_response.text}")
        else:
            print(f"   ❌ URL不可访问: {head_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 测试URL时出错: {str(e)}")

def validate_ppt_file_header(file_path):
    """
    验证PPT文件头是否正确
    """
    print(f"   \n🔍 步骤4: 验证PPT文件格式...")
    
    try:
        with open(file_path, 'rb') as f:
            header = f.read(8)
        
        print(f"   文件头 (hex): {header.hex()}")
        print(f"   文件头 (bytes): {header}")
        
        # PPTX文件应该以PK开头 (ZIP格式)
        expected_headers = [
            b'PK\x03\x04',  # ZIP文件标准头
            b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'  # OLD PPT格式
        ]
        
        is_valid = False
        for expected in expected_headers:
            if header.startswith(expected):
                is_valid = True
                if expected == b'PK\x03\x04':
                    print(f"   ✅ 有效的PPTX文件 (ZIP格式)")
                else:
                    print(f"   ✅ 有效的旧版PPT文件")
                break
        
        if not is_valid:
            print(f"   ❌ 无效的PPT文件格式!")
            print(f"   PPTX文件应以 'PK\\x03\\x04' 开头")
            
        # 尝试用zipfile验证
        try:
            import zipfile
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                print(f"   📦 ZIP包含 {len(file_list)} 个文件")
                
                # 检查必要的PPTX文件结构
                required_files = ['[Content_Types].xml', 'ppt/presentation.xml']
                missing_files = [f for f in required_files if f not in file_list]
                
                if not missing_files:
                    print(f"   ✅ PPTX文件结构完整")
                else:
                    print(f"   ⚠️  缺少必要文件: {missing_files}")
                    print(f"   文件列表前10个: {file_list[:10]}")
                    
        except zipfile.BadZipFile:
            print(f"   ❌ 不是有效的ZIP文件!")
        except Exception as e:
            print(f"   ⚠️  ZIP验证出错: {str(e)}")
            
    except Exception as e:
        print(f"   ❌ 文件验证出错: {str(e)}")

def test_alternative_download_methods():
    """
    测试不同的下载方法
    """
    print("\n" + "=" * 80)
    print("🔄 测试替代下载方法")
    print("=" * 80)
    
    # 重新执行工作流获取file_url
    url = f"{BASE_URL}/v1/workflow/run"
    payload = {
        "workflow_id": WORKFLOW_ID,
        "parameters": {"input": "测试下载方法"},
        "user_id": USER_ID
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        if response.status_code == 200:
            result = response.json()
            file_url = result.get('data', {}).get('file_list', [{}])[0].get('file_url')
            
            if file_url:
                print(f"\n📥 测试不同的下载方式:")
                
                # 方法1: 直接requests下载
                print(f"\n   方法1: 直接requests.get()")
                try:
                    r = requests.get(file_url, timeout=60)
                    print(f"     状态码: {r.status_code}, 大小: {len(r.content)} bytes")
                except Exception as e:
                    print(f"     ❌ 失败: {str(e)}")
                
                # 方法2: 带headers下载
                print(f"\n   方法2: 带浏览器headers")
                browser_headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://www.coze.cn/',
                    'Accept': '*/*'
                }
                try:
                    r = requests.get(file_url, headers=browser_headers, timeout=60)
                    print(f"     状态码: {r.status_code}, 大小: {len(r.content)} bytes")
                except Exception as e:
                    print(f"     ❌ 失败: {str(e)}")
                
                # 方法3: 流式下载
                print(f"\n   方法3: 流式下载")
                try:
                    r = requests.get(file_url, stream=True, timeout=60)
                    content = b''
                    for chunk in r.iter_content(chunk_size=8192):
                        content += chunk
                    print(f"     状态码: {r.status_code}, 大小: {len(content)} bytes")
                except Exception as e:
                    print(f"     ❌ 失败: {str(e)}")
                    
    except Exception as e:
        print(f"❌ 获取file_url失败: {str(e)}")

if __name__ == "__main__":
    print("PPT下载问题诊断工具")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行调试
    debug_workflow_execution()
    
    # 测试替代方法
    test_alternative_download_methods()
    
    print("\n" + "=" * 80)
    print("🔍 调试完成，请查看上述输出分析问题原因")
    print("=" * 80)
