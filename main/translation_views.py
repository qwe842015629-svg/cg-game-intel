"""
翻译API视图
提供RESTful API接口供前端调用
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .translation_service import TranslationService


@csrf_exempt
@require_http_methods(["POST"])
def translate_text(request):
    """
    单文本翻译接口
    
    POST /api/translate/
    Body: {
        "text": "要翻译的文本",
        "targetLanguage": "en",
        "sourceLanguage": "zh-CN"  // 可选
    }
    """
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        target_language = data.get('targetLanguage', 'en')
        source_language = data.get('sourceLanguage')
        
        if not text:
            return JsonResponse({
                'success': False,
                'error': '文本不能为空'
            }, status=400)
        
        result = TranslationService.translate(
            text=text,
            target_language=target_language,
            source_language=source_language
        )
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'translatedText': result['text'],
                'message': result['message']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', '翻译失败'),
                'message': result.get('message', '翻译失败')
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON格式'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def translate_batch(request):
    """
    批量翻译接口
    
    POST /api/translate/batch/
    Body: {
        "texts": ["text1", "text2", "text3"],
        "targetLanguage": "en"
    }
    """
    try:
        data = json.loads(request.body)
        texts = data.get('texts', [])
        target_language = data.get('targetLanguage', 'en')
        
        if not texts or not isinstance(texts, list):
            return JsonResponse({
                'success': False,
                'error': '文本列表不能为空且必须是数组'
            }, status=400)
        
        result = TranslationService.translate_batch(
            texts=texts,
            target_language=target_language
        )
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'translatedTexts': result['texts'],
                'message': result['message']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', '批量翻译失败'),
                'message': result.get('message', '批量翻译失败')
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON格式'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def translate_multi_language(request):
    """
    多语种翻译接口（一次性翻译成多种语言）
    
    POST /api/translate/multi/
    Body: {
        "text": "要翻译的文本",
        "targetLanguages": ["en", "ja", "ko"]
    }
    """
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        target_languages = data.get('targetLanguages', [])
        
        if not text:
            return JsonResponse({
                'success': False,
                'error': '文本不能为空'
            }, status=400)
        
        if not target_languages or not isinstance(target_languages, list):
            return JsonResponse({
                'success': False,
                'error': '目标语言列表不能为空且必须是数组'
            }, status=400)
        
        result = TranslationService.translate_multi_language(
            text=text,
            target_languages=target_languages
        )
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'translations': result['translations'],
                'message': result['message']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', '多语种翻译失败'),
                'message': result.get('message', '多语种翻译失败')
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON格式'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_supported_languages(request):
    """
    获取支持的语言列表
    
    GET /api/translate/languages/
    """
    try:
        languages = TranslationService.get_supported_languages()
        return JsonResponse({
            'success': True,
            'languages': languages
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_translation_stats(request):
    """
    获取翻译统计信息
    
    GET /api/translate/stats/
    """
    try:
        stats = TranslationService.get_user_stats()
        
        if stats['success']:
            return JsonResponse({
                'success': True,
                'available': stats['available'],
                'used': stats['used'],
                'message': stats['message']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': stats.get('error', '获取统计信息失败'),
                'message': stats.get('message', '获取统计信息失败')
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
