"""
翻译服务 - 集成翻译之家API
提供文本翻译、批量翻译等功能
"""
import requests
import json
from typing import List, Dict, Optional


class TranslationService:
    """翻译服务类"""
    
    BASE_URL = "http://www.trans-home.com"
    API_TOKEN = "mnnwBJkNAlkt7UHWxqo2"
    
    # 语言代码映射
    LANGUAGE_MAP = {
        'en': 'en',        # 英文
        'ja': 'ja',        # 日文
        'ko': 'ko',        # 韩文
        'th': 'th',        # 泰文
        'vi': 'vi',        # 越南文
        'zh-CN': 'zh-cn',  # 简体中文
        'zh-TW': 'zh-tw',  # 繁体中文
        'fr': 'fr',        # 法文
        'de': 'de',        # 德文
    }
    
    @classmethod
    def translate(
        cls, 
        text: str, 
        target_language: str, 
        source_language: Optional[str] = None,
        mime_type: int = 0
    ) -> Dict:
        """
        单文本翻译
        
        Args:
            text: 待翻译文本
            target_language: 目标语言代码
            source_language: 源语言代码（可选）
            mime_type: 翻译格式 0:text, 1:html
            
        Returns:
            翻译结果字典
        """
        url = f"{cls.BASE_URL}/api/index/translate?token={cls.API_TOKEN}"
        
        # 转换语言代码
        target_lang = cls.LANGUAGE_MAP.get(target_language, target_language)
        
        payload = {
            "keywords": text,
            "targetLanguage": target_lang,
            "mimeType": mime_type
        }
        
        if source_language:
            source_lang = cls.LANGUAGE_MAP.get(source_language, source_language)
            payload["sourceLanguage"] = source_lang
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 1:
                return {
                    'success': True,
                    'text': result['data']['text'],
                    'message': result.get('info', '翻译成功')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('info', '翻译失败'),
                    'message': result.get('info', '翻译失败')
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'message': '翻译请求失败'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '翻译处理失败'
            }
    
    @classmethod
    def translate_batch(
        cls,
        texts: List[str],
        target_language: str,
        mime_type: int = 0
    ) -> Dict:
        """
        批量翻译（谷歌引擎）
        
        Args:
            texts: 待翻译文本列表
            target_language: 目标语言代码
            mime_type: 翻译格式 0:text, 1:html
            
        Returns:
            翻译结果字典
        """
        url = f"{cls.BASE_URL}/api/index/translateBatch?token={cls.API_TOKEN}"
        
        # 转换语言代码
        target_lang = cls.LANGUAGE_MAP.get(target_language, target_language)
        
        payload = {
            "keywords": texts,
            "targetLanguage": target_lang,
            "mimeType": mime_type
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 1:
                return {
                    'success': True,
                    'texts': result['data']['text'],
                    'message': result.get('info', '批量翻译成功')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('info', '批量翻译失败'),
                    'message': result.get('info', '批量翻译失败')
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'message': '批量翻译请求失败'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '批量翻译处理失败'
            }
    
    @classmethod
    def translate_multi_language(
        cls,
        text: str,
        target_languages: List[str]
    ) -> Dict:
        """
        多语种翻译（一次性翻译成多种语言）
        
        Args:
            text: 待翻译文本
            target_languages: 目标语言代码列表
            
        Returns:
            翻译结果字典
        """
        url = f"{cls.BASE_URL}/api/index/transBatchLanguage?token={cls.API_TOKEN}"
        
        # 转换语言代码
        target_langs = [cls.LANGUAGE_MAP.get(lang, lang) for lang in target_languages]
        
        payload = {
            "keywords": text,
            "targetLanguage": target_langs
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 1:
                return {
                    'success': True,
                    'translations': result['data'],
                    'message': result.get('info', '多语种翻译成功')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('info', '多语种翻译失败'),
                    'message': result.get('info', '多语种翻译失败')
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'message': '多语种翻译请求失败'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '多语种翻译处理失败'
            }
    
    @classmethod
    def get_user_stats(cls) -> Dict:
        """
        获取用户翻译统计信息
        
        Returns:
            统计信息字典
        """
        url = f"{cls.BASE_URL}/api/index/getUserNums?token={cls.API_TOKEN}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 1:
                data = result.get('data', {})
                return {
                    'success': True,
                    'available': data.get('use_num', 0),
                    'used': data.get('is_used', 0),
                    'message': result.get('info', '获取成功')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('info', '获取失败'),
                    'message': result.get('info', '获取失败')
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '获取统计信息失败'
            }
    
    @classmethod
    def get_supported_languages(cls) -> List[Dict[str, str]]:
        """
        获取支持的语言列表
        
        Returns:
            语言列表
        """
        return [
            {'code': 'en', 'name': 'English', 'native_name': 'English'},
            {'code': 'ja', 'name': 'Japanese', 'native_name': '日本語'},
            {'code': 'ko', 'name': 'Korean', 'native_name': '한국어'},
            {'code': 'th', 'name': 'Thai', 'native_name': 'ไทย'},
            {'code': 'vi', 'name': 'Vietnamese', 'native_name': 'Tiếng Việt'},
            {'code': 'zh-CN', 'name': 'Chinese Simplified', 'native_name': '简体中文'},
            {'code': 'zh-TW', 'name': 'Chinese Traditional', 'native_name': '繁體中文'},
            {'code': 'fr', 'name': 'French', 'native_name': 'Français'},
            {'code': 'de', 'name': 'German', 'native_name': 'Deutsch'},
        ]
