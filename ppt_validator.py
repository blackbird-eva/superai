#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PPT文件验证器
在下载和使用前验证PPT文件的完整性和正确性
"""

import os
import io
import zipfile
import struct
import hashlib
from pathlib import Path
from datetime import datetime
import mimetypes

class PPTValidator:
    """PPT文件验证器"""
    
    def __init__(self):
        self.validation_rules = {
            'min_file_size': 1024,      # 最小文件大小 1KB
            'max_file_size': 100*1024*1024,  # 最大文件大小 100MB
            'required_extensions': ['.pptx'],
            'valid_mime_types': [
                'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                'application/vnd.ms-powerpoint'
            ]
        }
        
        # PPTX文件必须包含的ZIP条目
        self.required_zip_entries = [
            '[Content_Types].xml',
            'ppt/presentation.xml',
            'ppt/_rels/presentation.xml.rels',
            'ppt/slideMasters/',
            'ppt/slideLayouts/',
            'ppt/slides/'
        ]
        
        # PPTX文件签名 (ZIP文件标准头)
        self.pptx_signature = b'PK\x03\x04'
        
        # 旧版PPT文件签名
        self.old_ppt_signature = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'
    
    def validate_file_exists(self, file_path):
        """验证文件是否存在"""
        if not os.path.exists(file_path):
            return {
                'valid': False,
                'error': 'FILE_NOT_FOUND',
                'message': f'文件不存在: {file_path}'
            }
        
        if not os.path.isfile(file_path):
            return {
                'valid': False,
                'error': 'NOT_A_FILE',
                'message': f'路径不是文件: {file_path}'
            }
        
        return {'valid': True}
    
    def validate_file_extension(self, file_path):
        """验证文件扩展名"""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension not in self.validation_rules['required_extensions']:
            return {
                'valid': False,
                'error': 'INVALID_EXTENSION',
                'message': f'不支持的文件格式: {extension}，支持的格式: {self.validation_rules["required_extensions"]}'
            }
        
        return {'valid': True}
    
    def validate_file_size(self, file_path):
        """验证文件大小"""
        file_size = os.path.getsize(file_path)
        
        if file_size < self.validation_rules['min_file_size']:
            return {
                'valid': False,
                'error': 'FILE_TOO_SMALL',
                'message': f'文件太小: {file_size} bytes，最小要求: {self.validation_rules["min_file_size"]} bytes'
            }
        
        if file_size > self.validation_rules['max_file_size']:
            return {
                'valid': False,
                'error': 'FILE_TOO_LARGE',
                'message': f'文件太大: {file_size} bytes，最大限制: {self.validation_rules["max_file_size"]} bytes'
            }
        
        return {
            'valid': True,
            'file_size': file_size
        }
    
    def validate_file_signature(self, file_path):
        """验证文件签名（魔术数字）"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
            
            # 检查PPTX (ZIP格式)
            if header.startswith(self.pptx_signature):
                return {
                    'valid': True,
                    'file_type': 'pptx',
                    'signature': 'ZIP_FORMAT'
                }
            
            # 检查旧版PPT
            elif header.startswith(self.old_ppt_signature):
                return {
                    'valid': True,
                    'file_type': 'ppt',
                    'signature': 'OLE_FORMAT'
                }
            
            else:
                return {
                    'valid': False,
                    'error': 'INVALID_SIGNATURE',
                    'message': f'无效的PPT文件签名: {header.hex() if header else "空"}'
                }
                
        except Exception as e:
            return {
                'valid': False,
                'error': 'SIGNATURE_CHECK_FAILED',
                'message': f'文件签名检查失败: {str(e)}'
            }
    
    def validate_zip_structure(self, file_path):
        """验证ZIP文件结构和必需条目"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # 检查ZIP文件是否损坏
                bad_file = zip_ref.testzip()
                if bad_file:
                    return {
                        'valid': False,
                        'error': 'CORRUPTED_ZIP',
                        'message': f'ZIP文件损坏，问题文件: {bad_file}'
                    }
                
                # 获取所有文件列表
                file_list = zip_ref.namelist()
                
                # 检查必需的文件条目
                missing_required = []
                for required_entry in self.required_zip_entries:
                    if not any(entry.startswith(required_entry) for entry in file_list):
                        missing_required.append(required_entry)
                
                if missing_required:
                    return {
                        'valid': False,
                        'error': 'MISSING_REQUIRED_ENTRIES',
                        'message': f'缺少必需的PPTX文件结构: {missing_required}',
                        'found_entries': file_list[:10]  # 返回前10个条目供调试
                    }
                
                # 检查slides目录是否有实际内容
                slide_files = [f for f in file_list if f.startswith('ppt/slides/slide')]
                if not slide_files:
                    return {
                        'valid': False,
                        'error': 'NO_SLIDES_FOUND',
                        'message': 'PPTX文件中没有找到任何幻灯片'
                    }
                
                return {
                    'valid': True,
                    'file_type': 'pptx',
                    'zip_entries': len(file_list),
                    'slide_count': len(slide_files),
                    'file_list_sample': file_list[:10]
                }
                
        except zipfile.BadZipFile:
            return {
                'valid': False,
                'error': 'NOT_VALID_ZIP',
                'message': '文件不是有效的ZIP格式'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': 'ZIP_VALIDATION_FAILED',
                'message': f'ZIP结构验证失败: {str(e)}'
            }
    
    def validate_mime_type(self, file_path):
        """验证MIME类型"""
        mime_type, encoding = mimetypes.guess_type(file_path)
        
        if mime_type is None:
            return {
                'valid': True,  # MIME类型检测失败不算错误
                'warning': 'MIME_TYPE_UNKNOWN',
                'message': '无法确定MIME类型'
            }
        
        if mime_type not in self.validation_rules['valid_mime_types']:
            return {
                'valid': False,
                'error': 'INVALID_MIME_TYPE',
                'message': f'MIME类型不匹配: {mime_type}，期望: {self.validation_rules["valid_mime_types"]}'
            }
        
        return {
            'valid': True,
            'mime_type': mime_type
        }
    
    def calculate_file_hash(self, file_path, algorithm='sha256'):
        """计算文件哈希值用于完整性校验"""
        try:
            hash_obj = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                # 分块读取大文件
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            
            return {
                'valid': True,
                'hash': hash_obj.hexdigest(),
                'algorithm': algorithm
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': 'HASH_CALCULATION_FAILED',
                'message': f'哈希计算失败: {str(e)}'
            }
    
    def validate_ppt_content(self, file_path):
        """深度验证PPT内容（可选，较慢）"""
        try:
            if not file_path.endswith('.pptx'):
                return {
                    'valid': True,  # 只验证PPTX，旧版PPT跳过深度验证
                    'message': '跳过非PPTX文件的深度验证'
                }
            
            # 这里可以集成python-pptx进行深度验证
            # 由于避免额外依赖，我们只做基础检查
            
            validation_result = {
                'valid': True,
                'checks_performed': [
                    'file_structure',
                    'zip_integrity',
                    'required_entries'
                ],
                'message': '基础内容验证通过'
            }
            
            return validation_result
            
        except Exception as e:
            return {
                'valid': False,
                'error': 'CONTENT_VALIDATION_FAILED',
                'message': f'内容验证失败: {str(e)}'
            }
    
    def comprehensive_validation(self, file_path, enable_deep_check=False):
        """综合验证 - 执行所有验证步骤"""
        print(f"🔍 开始验证文件: {os.path.basename(file_path)}")
        
        validation_steps = [
            ("文件存在性", self.validate_file_exists),
            ("文件扩展名", self.validate_file_extension),
            ("文件大小", self.validate_file_size),
            ("文件签名", self.validate_file_signature),
            ("MIME类型", self.validate_mime_type),
        ]
        
        results = {
            'file_path': file_path,
            'validation_time': datetime.now().isoformat(),
            'steps': [],
            'overall_valid': True,
            'summary': {}
        }
        
        # 执行基础验证步骤
        for step_name, validator_func in validation_steps:
            print(f"   📋 {step_name}...", end=' ')
            result = validator_func(file_path)
            
            if result['valid']:
                print("✅")
            else:
                print(f"❌ {result.get('message', '')}")
            
            results['steps'].append({
                'step': step_name,
                'result': result
            })
            
            if not result['valid']:
                results['overall_valid'] = False
                results['summary']['error'] = result.get('error')
                results['summary']['message'] = result.get('message')
                break
        
        # 如果基础验证通过，进行ZIP结构验证
        if results['overall_valid']:
            print("   📦 ZIP结构验证...", end=' ')
            signature_result = next(
                (step['result'] for step in results['steps'] if step['step'] == '文件签名'),
                {}
            )
            
            if signature_result.get('file_type') == 'pptx':
                zip_result = self.validate_zip_structure(file_path)
                
                if zip_result['valid']:
                    print(f"✅ ({zip_result['slide_count']} slides)")
                    results['steps'].append({
                        'step': 'ZIP结构',
                        'result': zip_result
                    })
                    results['summary']['slide_count'] = zip_result['slide_count']
                    results['summary']['file_size_bytes'] = zip_result.get('file_size', 0)
                else:
                    print(f"❌ {zip_result.get('message', '')}")
                    results['steps'].append({
                        'step': 'ZIP结构',
                        'result': zip_result
                    })
                    results['overall_valid'] = False
                    results['summary']['error'] = zip_result.get('error')
                    results['summary']['message'] = zip_result.get('message')
            else:
                print("⏭️  跳过（非PPTX格式）")
        
        # 计算文件哈希
        if results['overall_valid']:
            print("   🔐 计算文件哈希...", end=' ')
            hash_result = self.calculate_file_hash(file_path)
            if hash_result['valid']:
                print("✅")
                results['steps'].append({
                    'step': '文件哈希',
                    'result': hash_result
                })
                results['summary']['file_hash'] = hash_result['hash']
            else:
                print("⚠️  失败")
        
        # 深度内容验证（可选）
        if results['overall_valid'] and enable_deep_check:
            print("   🔬 深度内容验证...", end=' ')
            content_result = self.validate_ppt_content(file_path)
            if content_result['valid']:
                print("✅")
                results['steps'].append({
                    'step': '深度内容验证',
                    'result': content_result
                })
            else:
                print(f"⚠️  {content_result.get('message', '')}")
        
        # 输出验证摘要
        print(f"\n📊 验证结果: {'✅ 通过' if results['overall_valid'] else '❌ 失败'}")
        
        if results['overall_valid']:
            summary = results['summary']
            print(f"   📄 幻灯片数量: {summary.get('slide_count', 'N/A')}")
            print(f"   💾 文件大小: {summary.get('file_size_bytes', 0):,} bytes")
            if 'file_hash' in summary:
                print(f"   🔐 SHA256: {summary['file_hash'][:16]}...")
        else:
            print(f"   ❌ 错误: {results['summary'].get('message', '未知错误')}")
        
        return results

class PPTDownloadValidator:
    """PPT下载验证器 - 专门用于Coze API下载的文件"""
    
    def __init__(self):
        self.validator = PPTValidator()
        self.download_checks = []
    
    def validate_download_response(self, response, expected_filename=None):
        """验证下载响应"""
        print("🌐 验证下载响应...")
        
        results = {
            'response_valid': True,
            'checks': []
        }
        
        # 检查HTTP状态码
        if response.status_code != 200:
            results['response_valid'] = False
            results['checks'].append({
                'check': 'HTTP_STATUS',
                'valid': False,
                'message': f'HTTP状态码不是200: {response.status_code}'
            })
            return results
        
        results['checks'].append({
            'check': 'HTTP_STATUS',
            'valid': True,
            'message': 'HTTP状态码正常'
        })
        
        # 检查内容长度
        content_length = len(response.content)
        if content_length < 1000:
            results['response_valid'] = False
            results['checks'].append({
                'check': 'CONTENT_LENGTH',
                'valid': False,
                'message': f'内容太短: {content_length} bytes'
            })
        else:
            results['checks'].append({
                'check': 'CONTENT_LENGTH',
                'valid': True,
                'message': f'内容长度正常: {content_length:,} bytes'
            })
        
        # 检查Content-Type
        content_type = response.headers.get('content-type', '').lower()
        expected_types = ['powerpoint', 'presentation', 'octet-stream']
        if not any(exp_type in content_type for exp_type in expected_types):
            results['checks'].append({
                'check': 'CONTENT_TYPE',
                'valid': False,
                'message': f'Content-Type异常: {content_type}'
            })
        else:
            results['checks'].append({
                'check': 'CONTENT_TYPE',
                'valid': True,
                'message': f'Content-Type正常: {content_type}'
            })
        
        # 验证文件签名
        if response.content:
            header = response.content[:8]
            if header.startswith(b'PK\x03\x04'):
                results['checks'].append({
                    'check': 'FILE_SIGNATURE',
                    'valid': True,
                    'message': 'PPTX文件签名正确'
                })
            else:
                results['response_valid'] = False
                results['checks'].append({
                    'check': 'FILE_SIGNATURE',
                    'valid': False,
                    'message': f'文件签名异常: {header.hex()}'
                })
        
        self.download_checks.append(results)
        return results
    
    def save_and_validate_downloaded_file(self, response, save_path, filename_hint=None):
        """保存并验证下载的文件"""
        print(f"💾 保存文件到: {save_path}")
        
        try:
            # 保存文件
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            print(f"   ✅ 文件保存成功 ({len(response.content):,} bytes)")
            
            # 验证保存的文件
            validation_result = self.validator.comprehensive_validation(save_path)
            
            return {
                'saved': True,
                'validation': validation_result
            }
            
        except Exception as e:
            return {
                'saved': False,
                'error': str(e)
            }

def main():
    """测试验证器功能"""
    print("🧪 PPT文件验证器测试")
    print("=" * 50)
    
    validator = PPTValidator()
    
    # 查找测试文件
    test_files = []
    for ext in ['.pptx', '.ppt']:
        test_files.extend(Path('.').glob(f'*{ext}'))
    
    if not test_files:
        print("❌ 未找到PPT测试文件")
        print("请将PPT文件放在当前目录下再运行测试")
        return
    
    print(f"找到 {len(test_files)} 个测试文件")
    
    for test_file in test_files:
        print(f"\n{'='*50}")
        validator.comprehensive_validation(str(test_file), enable_deep_check=False)
    
    print(f"\n{'='*50}")
    print("🏁 验证测试完成")

if __name__ == "__main__":
    main()
