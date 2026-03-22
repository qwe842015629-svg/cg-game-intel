from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError, PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Banner,
    HomeLayout,
    SiteConfig,
    MediaAsset,
    NovelDraft,
    NovelWork,
    PlazaPost,
    PlazaLike,
    PlazaComment,
)
from .media_library import upsert_media_asset
from .serializers import (
    BannerSerializer,
    BannerListSerializer,
    HomeLayoutSerializer,
    SiteConfigSerializer,
    MediaAssetSerializer,
    NovelDraftSerializer,
    NovelWorkSerializer,
    PlazaPostSerializer,
    PlazaCommentSerializer,
)
import sys
import os
import io
import wave
import base64
import json
import tempfile
import threading


def _normalize_client_id(value):
    return str(value or "").strip()[:64]


_COQUI_TTS_MODEL_CACHE = {}
_COQUI_TTS_MODEL_LOCK = threading.Lock()


def _coqui_tts_enabled():
    return bool(getattr(settings, "COQUI_TTS_ENABLED", False))


def _coqui_default_model_name():
    return str(
        getattr(settings, "COQUI_TTS_DEFAULT_MODEL", "tts_models/multilingual/multi-dataset/xtts_v2")
    ).strip()


def _coqui_default_language():
    return str(getattr(settings, "COQUI_TTS_DEFAULT_LANGUAGE", "zh-cn")).strip()


def _coqui_default_speaker():
    return str(getattr(settings, "COQUI_TTS_DEFAULT_SPEAKER", "")).strip()


def _coqui_use_gpu():
    return bool(getattr(settings, "COQUI_TTS_USE_GPU", False))


def _coqui_apply_tos_env():
    # Coqui checks os.environ directly; mirror Django settings into process env.
    if os.environ.get("COQUI_TOS_AGREED") == "1":
        return
    if bool(getattr(settings, "COQUI_TOS_AGREED", False)):
        os.environ["COQUI_TOS_AGREED"] = "1"


def _load_coqui_tts_model(model_name):
    model_key = f"{model_name}|gpu:{int(_coqui_use_gpu())}"
    with _COQUI_TTS_MODEL_LOCK:
        cached = _COQUI_TTS_MODEL_CACHE.get(model_key)
        if cached is not None:
            return cached

        _coqui_apply_tos_env()
        try:
            from TTS.api import TTS as CoquiTTS
        except Exception as exc:
            raise RuntimeError("Coqui TTS dependency missing. Run `pip install TTS`.") from exc

        model = CoquiTTS(model_name=model_name, progress_bar=False, gpu=_coqui_use_gpu())
        _COQUI_TTS_MODEL_CACHE[model_key] = model
        return model


def _coqui_model_speakers(tts_model):
    candidates = []
    for attr_name in ("speakers",):
        value = getattr(tts_model, attr_name, None)
        if isinstance(value, (list, tuple)):
            candidates.extend([str(item).strip() for item in value if str(item).strip()])

    synthesizer = getattr(tts_model, "synthesizer", None)
    if synthesizer is not None:
        synth_speakers = getattr(synthesizer, "speakers", None)
        if isinstance(synth_speakers, (list, tuple)):
            candidates.extend([str(item).strip() for item in synth_speakers if str(item).strip()])

    deduped = []
    seen = set()
    for item in candidates:
        if not item or item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


_COQUI_FEMALE_HINT_TOKENS = (
    "female",
    "woman",
    "girl",
    "shimmer",
    "nova",
    "coral",
    "\u5973",
    "\u5c11\u5973",
    "\u59d0",
    "\u59b9",
)
_COQUI_MALE_HINT_TOKENS = (
    "male",
    "man",
    "boy",
    "onyx",
    "ash",
    "echo",
    "fable",
    "\u7537",
    "\u5c11\u5e74",
    "\u54e5",
    "\u53d4",
)
_COQUI_FEMALE_SPEAKER_NAME_HINTS = (
    "female",
    "woman",
    "girl",
    "speaker_f",
    "\u5973",
    "\u5c11\u5973",
    "\u59d0",
    "\u59b9",
)
_COQUI_MALE_SPEAKER_NAME_HINTS = (
    "male",
    "man",
    "boy",
    "speaker_m",
    "\u7537",
    "\u5c11\u5e74",
    "\u54e5",
    "\u53d4",
)
_COQUI_FEMALE_SPEAKER_PREFERRED = (
    "Claribel Dervla",
    "Daisy Studious",
    "Gracie Wise",
    "Tammie Ema",
    "Alison Dietlinde",
    "Ana Florence",
    "Annmarie Nele",
    "Asya Anara",
    "Brenda Stern",
    "Gitta Nikolina",
    "Henriette Usha",
    "Sofia Hellen",
    "Tammy Grit",
    "Tanja Adelina",
    "Vjollca Johnnie",
    "Nova Hogarth",
    "Maja Ruoho",
    "Uta Obando",
    "Lidiya Szekeres",
    "Chandra MacFarland",
    "Szofi Granger",
    "Camilla Holmstr枚m",
    "Lilya Stainthorpe",
    "Zofija Kendrick",
    "Narelle Moon",
    "Barbora MacLean",
    "Alexandra Hisakawa",
    "Alma Mar铆a",
    "Rosemary Okafor",
    "Ige Behringer",
)
_COQUI_MALE_SPEAKER_PREFERRED = (
    "Andrew Chipper",
    "Badr Odhiambo",
    "Dionisio Schuyler",
    "Royston Min",
    "Viktor Eka",
    "Abrahan Mack",
    "Adde Michal",
    "Baldur Sanjin",
    "Craig Gutsy",
    "Damien Black",
    "Gilberto Mathias",
    "Ilkin Urbano",
    "Kazuhiko Atallah",
    "Ludvig Milivoj",
    "Suad Qasim",
    "Torcull Diarmuid",
    "Viktor Menelaos",
    "Zacharie Aimilios",
    "Filip Traverse",
    "Damjan Chapman",
    "Wulf Carlevaro",
    "Aaron Dreschner",
    "Kumar Dahl",
    "Eugenio Matarac谋",
    "Ferran Simen",
    "Xavier Hayasaka",
    "Luis Moray",
    "Marcos Rudaski",
)


def _normalize_hint_text(value):
    return str(value or "").strip().lower()


def _match_speaker_case_insensitive(speakers, target):
    target_lower = _normalize_hint_text(target)
    for item in speakers:
        if _normalize_hint_text(item) == target_lower:
            return item
    return ""


def _speaker_name_contains_token(normalized_name, normalized_token):
    if not normalized_name or not normalized_token:
        return False
    if re.fullmatch(r"[a-z0-9_]+", normalized_token or ""):
        # For latin tokens use boundary-like matching to avoid false hits
        # such as token "man" matching "Damjan".
        pattern = rf"(?:^|[^a-z0-9]){re.escape(normalized_token)}(?:$|[^a-z0-9])"
        return bool(re.search(pattern, normalized_name))
    return normalized_token in normalized_name


def _find_first_speaker_by_tokens(speakers, tokens):
    normalized_tokens = tuple(_normalize_hint_text(token) for token in tokens if token)
    for item in speakers:
        normalized_item = _normalize_hint_text(item)
        if any(_speaker_name_contains_token(normalized_item, token) for token in normalized_tokens):
            return item
    return ""


def _find_first_speaker_by_preferred_names(speakers, preferred_names):
    if not speakers:
        return ""
    index_map = {_normalize_hint_text(item): item for item in speakers}
    for preferred in preferred_names:
        matched = index_map.get(_normalize_hint_text(preferred))
        if matched:
            return matched
    return ""


def _pick_coqui_speaker(tts_model, explicit_speaker, voice_hint):
    speakers = _coqui_model_speakers(tts_model)
    speaker = str(explicit_speaker or "").strip()
    if speaker:
        if speakers:
            matched = _match_speaker_case_insensitive(speakers, speaker)
            if matched:
                return matched
            # Explicit speaker does not exist in this model's speaker list.
            # Ignore it and continue with hint-based selection.
        else:
            # Keep explicit speaker for models that support dynamic speaker names.
            return speaker

    if not speakers:
        return ""

    hint = _normalize_hint_text(voice_hint)
    female_hint = any(token in hint for token in _COQUI_FEMALE_HINT_TOKENS)
    male_hint = any(token in hint for token in _COQUI_MALE_HINT_TOKENS)

    if female_hint and not male_hint:
        matched = _find_first_speaker_by_preferred_names(speakers, _COQUI_FEMALE_SPEAKER_PREFERRED)
        if matched:
            return matched
        matched = _find_first_speaker_by_tokens(speakers, _COQUI_FEMALE_SPEAKER_NAME_HINTS)
        if matched:
            return matched
        return speakers[0]

    if male_hint and not female_hint:
        matched = _find_first_speaker_by_preferred_names(speakers, _COQUI_MALE_SPEAKER_PREFERRED)
        if matched:
            return matched
        matched = _find_first_speaker_by_tokens(speakers, _COQUI_MALE_SPEAKER_NAME_HINTS)
        if matched:
            return matched
        return speakers[min(1, len(speakers) - 1)]

    return speakers[0]


def _coqui_model_supports_language(tts_model):
    languages = getattr(tts_model, "languages", None)
    return isinstance(languages, (list, tuple)) and len(languages) > 0


def _coqui_sample_rate(tts_model):
    synthesizer = getattr(tts_model, "synthesizer", None)
    for source in [tts_model, synthesizer]:
        if source is None:
            continue
        value = getattr(source, "output_sample_rate", None) or getattr(source, "sample_rate", None)
        if isinstance(value, (int, float)) and value > 0:
            return int(value)
    return 24000


def _coqui_waveform_to_wav_bytes(waveform, sample_rate):
    try:
        import numpy as np

        arr = np.asarray(waveform, dtype=np.float32).flatten()
        arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
        arr = np.clip(arr, -1.0, 1.0)
        pcm = (arr * 32767.0).astype("<i2").tobytes()
    except Exception:
        pcm_values = bytearray()
        for item in waveform if isinstance(waveform, (list, tuple)) else []:
            try:
                value = float(item)
            except Exception:
                value = 0.0
            value = max(-1.0, min(1.0, value))
            int_value = int(value * 32767.0)
            pcm_values.extend(int_value.to_bytes(2, byteorder="little", signed=True))
        pcm = bytes(pcm_values)

    output = io.BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(int(sample_rate) if int(sample_rate) > 0 else 24000)
        wav_file.writeframes(pcm)
    return output.getvalue()


def _decode_speaker_wav_base64(raw_payload):
    payload = str(raw_payload or "").strip()
    if not payload:
        return b""
    if payload.startswith("data:") and "," in payload:
        payload = payload.split(",", 1)[1]
    try:
        return base64.b64decode(payload, validate=True)
    except Exception as exc:
        raise ValidationError({"speaker_wav_base64": "Invalid base64 payload"}) from exc


class CoquiTtsSynthesizeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "enabled": _coqui_tts_enabled(),
                "default_model": _coqui_default_model_name(),
                "default_language": _coqui_default_language(),
                "default_speaker": _coqui_default_speaker(),
                "supports_clone_voice": True,
            }
        )

    def post(self, request):
        if not _coqui_tts_enabled():
            return Response(
                {"detail": "Coqui TTS is disabled on server. Set COQUI_TTS_ENABLED=true."},
                status=503,
            )

        text = str(request.data.get("text") or "").strip()
        if not text:
            raise ValidationError({"text": "text is required"})
        if len(text) > 4000:
            raise ValidationError({"text": "text is too long (max 4000 chars)"})

        model_name = str(request.data.get("model_name") or _coqui_default_model_name()).strip()
        language = str(request.data.get("language") or _coqui_default_language()).strip()
        speaker = str(request.data.get("speaker") or _coqui_default_speaker()).strip()
        voice_hint = str(request.data.get("voice_hint") or "").strip()
        speed_raw = request.data.get("speed", 1.0)
        try:
            speed = float(speed_raw)
        except Exception:
            speed = 1.0
        speed = max(0.5, min(2.0, speed))

        speaker_wav_bytes = _decode_speaker_wav_base64(request.data.get("speaker_wav_base64"))
        temp_speaker_wav_path = ""
        selected_speaker = ""
        synthesis_kwargs = {}

        try:
            tts_model = _load_coqui_tts_model(model_name)
            selected_speaker = _pick_coqui_speaker(tts_model, speaker, voice_hint)

            if _coqui_model_supports_language(tts_model) and language:
                synthesis_kwargs["language"] = language
            if selected_speaker:
                synthesis_kwargs["speaker"] = selected_speaker
            if speaker_wav_bytes:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                    temp_file.write(speaker_wav_bytes)
                    temp_speaker_wav_path = temp_file.name
                synthesis_kwargs["speaker_wav"] = temp_speaker_wav_path

            if abs(speed - 1.0) > 0.001:
                synthesis_kwargs["speed"] = speed

            try:
                waveform = tts_model.tts(text=text, **synthesis_kwargs)
            except TypeError:
                # Some Coqui models do not accept speed argument.
                synthesis_kwargs.pop("speed", None)
                waveform = tts_model.tts(text=text, **synthesis_kwargs)

            wav_bytes = _coqui_waveform_to_wav_bytes(waveform, _coqui_sample_rate(tts_model))
        except ValidationError:
            raise
        except Exception as exc:
            return Response(
                {
                    "detail": "Coqui synthesis failed",
                    "error": str(exc),
                    "model_name": model_name,
                },
                status=500,
            )
        finally:
            if temp_speaker_wav_path and os.path.exists(temp_speaker_wav_path):
                try:
                    os.remove(temp_speaker_wav_path)
                except Exception:
                    pass

        response = HttpResponse(wav_bytes, content_type="audio/wav")
        response["Cache-Control"] = "no-store"
        response["X-Coqui-Model"] = model_name
        if selected_speaker:
            response["X-Coqui-Speaker"] = selected_speaker
        return response


def _resolve_owner_context(request, require_identity=False):
    user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
    candidate_client = request.data.get("client_id") if hasattr(request, "data") else None
    if not candidate_client:
        candidate_client = request.query_params.get("client_id")
    client_id = _normalize_client_id(candidate_client)

    if user:
        return f"user:{user.pk}", user, client_id
    if client_id:
        return f"client:{client_id}", None, client_id
    if require_identity:
        raise ValidationError({"client_id": "client_id is required for anonymous requests"})
    return "", None, ""

def trigger_wiki_update(request):
    """Trigger the data fetcher script manually"""
    try:
        # Ensure we can import data_fetcher from root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        if project_root not in sys.path:
            sys.path.append(project_root)
            
        import data_fetcher
        
        # Run the fetcher
        generated = data_fetcher.main(return_data=True)

        # Fallback: read latest generated file when function did not return payload.
        if not isinstance(generated, dict):
            generated = {}
            data_file = getattr(data_fetcher, "DATA_FILE", "")
            if data_file and os.path.exists(data_file):
                with open(data_file, "r", encoding="utf-8") as input_file:
                    generated = json.load(input_file)

        return JsonResponse(
            {
                'status': 'success',
                'message': 'Data updated successfully',
                'data': generated,
            }
        )
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def get_wiki_hub_data(request):
    """Return latest generated wiki hub payload without triggering a new crawl."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        if project_root not in sys.path:
            sys.path.append(project_root)

        import data_fetcher

        data_file = getattr(data_fetcher, "DATA_FILE", "")
        if not data_file or not os.path.exists(data_file):
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Wiki hub data file not found',
                },
                status=404,
            )

        with open(data_file, "r", encoding="utf-8") as input_file:
            payload = json.load(input_file)

        return JsonResponse(
            {
                'status': 'success',
                'data': payload,
            }
        )
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

class MediaAssetViewSet(viewsets.ModelViewSet):
    """Media asset management viewset."""
    queryset = MediaAsset.objects.all()
    serializer_class = MediaAssetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'alt_text']
    ordering_fields = ['created_at', 'file_size']
    ordering = ['-created_at']

    def create(self, request, *args, **kwargs):
        file_obj = request.data.get('file')
        if not file_obj:
            return Response({'error': 'No file provided'}, status=400)
        requested_name = request.data.get('name', getattr(file_obj, 'name', ''))
        category = request.data.get('category', 'other')
        alt_text = request.data.get('alt_text', '')

        try:
            instance, created = upsert_media_asset(
                file_obj=file_obj,
                requested_name=requested_name,
                category=category,
                alt_text=alt_text,
                create_thumbnail=True,
            )
        except ValueError as exc:
            return Response({'error': str(exc)}, status=400)
        except Exception as exc:
            return Response({'error': f'Upload failed: {str(exc)}'}, status=500)

        serializer = self.get_serializer(instance)
        response_payload = dict(serializer.data)
        response_payload['deduped'] = not created
        return Response(response_payload, status=201 if created else 200)

    def perform_destroy(self, instance):
        # Delete files from storage
        if instance.file:
            instance.file.delete(save=False)
        if instance.thumbnail:
            instance.thumbnail.delete(save=False)
        instance.delete()


class SiteConfigViewSet(viewsets.ModelViewSet):
    """Site configuration viewset."""
    queryset = SiteConfig.objects.all()
    serializer_class = SiteConfigSerializer
    pagination_class = None

    @action(detail=False, methods=['post'])
    def update_global(self, request):
        """Update global site configuration in bulk."""
        theme_config = request.data.get('theme_config')
        if not theme_config:
            return Response({'detail': '缂哄皯鍙傛暟'}, status=400)
            
        # 杩欓噷鍋囪 SiteConfig 瀛樺偍浜嗗叏灞€涓婚閰嶇疆锛屾垨鑰呮垜浠彲浠ユ牴鎹?key 瀛樺偍
        config, created = SiteConfig.objects.get_or_create(id=1)
        # 灏?CSS 鍙橀噺瀛樺叆 config 瀛楁
        current = dict(config.theme_config or {})
        current.update(theme_config)
        config.theme_config = current
        config.save(update_fields=['theme_config', 'updated_at'])
        return Response({'status': 'success'})
    
    def list(self, request, *args, **kwargs):
        """Return singleton site configuration."""
        config = SiteConfig.objects.first()
        if not config:
            # 濡傛灉涓嶅瓨鍦紝鍒欏垱寤轰竴涓粯璁ら厤缃?
            config = SiteConfig.objects.create(site_name='CYPHER GAME BUY')
        
        serializer = self.get_serializer(config)
        return Response(serializer.data)


class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    """Banner read-only viewset."""
    queryset = Banner.objects.filter(status='active').order_by('sort_order', '-created_at')
    serializer_class = BannerSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['sort_order', 'created_at', 'view_count']
    
    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return BannerListSerializer
        return BannerSerializer
    
    @action(detail=True, methods=['post'])
    def click(self, request, pk=None):
        """Record banner click."""
        banner = self.get_object()
        banner.increase_click_count()
        return Response({
            'status': 'success',
            'click_count': banner.click_count
        })
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """Return default banner or fallback first active banner."""
        default_banner = Banner.objects.filter(
            status='active',
            is_default=True
        ).first()
        
        if default_banner:
            serializer = self.get_serializer(default_banner)
            return Response(serializer.data)
        
        # 濡傛灉娌℃湁榛樿杞挱鍥撅紝杩斿洖绗竴涓椿鍔ㄧ殑杞挱鍥?
        first_banner = self.get_queryset().first()
        if first_banner:
            serializer = self.get_serializer(first_banner)
            return Response(serializer.data)
        
        return Response({'detail': 'No banners available.'}, status=404)


class HomeLayoutViewSet(viewsets.ModelViewSet):
    """Homepage layout viewset."""
    queryset = HomeLayout.objects.all().order_by('sort_order', 'created_at')
    serializer_class = HomeLayoutSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['sort_order', 'created_at']
    pagination_class = None
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        """Return all enabled layout sections in order."""
        layouts = self.get_queryset().filter(is_enabled=True)
        serializer = self.get_serializer(layouts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get', 'patch'])
    def section(self, request):
        """Get or update section config by section_key."""
        section_key = request.query_params.get('key')
        if not section_key:
            return Response({'detail': '缂哄皯section_key鍙傛暟'}, status=400)
        
        try:
            layout = HomeLayout.objects.get(section_key=section_key)
        except HomeLayout.DoesNotExist:
            # 濡傛灉涓嶅瓨鍦紝灏濊瘯鏍规嵁 SECTION_CHOICES 鍒涘缓涓€涓粯璁ょ殑
            section_name = dict(HomeLayout.SECTION_CHOICES).get(section_key, section_key)
            layout = HomeLayout.objects.create(
                section_key=section_key,
                section_name=section_name,
                is_enabled=True,
                sort_order=99
            )
        
        if request.method == 'PATCH':
            # 鏇存柊閰嶇疆
            config_data = request.data.get('config')
            if config_data:
                # 娣卞害鍚堝苟
                layout.config = {**layout.config, **config_data}
                layout.save()
                return Response({'status': 'success', 'config': layout.config})
            
        # GET 璇锋眰閫昏緫
        layout.increase_view_count()
        serializer = self.get_serializer(layout)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """閲嶆柊鎺掑簭鏉垮潡"""
        order_data = request.data.get('order', [])
        if not order_data:
            return Response({'status': 'error', 'message': '缂哄皯鎺掑簭鏁版嵁'}, status=400)
        
        try:
            for item in order_data:
                layout_id = item.get('id')
                sort_order = item.get('sort_order')
                if layout_id is not None and sort_order is not None:
                    HomeLayout.objects.filter(id=layout_id).update(sort_order=sort_order)
            
            return Response({'status': 'success'})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=500)


class NovelDraftCurrentView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        owner_key, _, _ = _resolve_owner_context(request, require_identity=True)
        draft = NovelDraft.objects.filter(owner_key=owner_key).first()
        if not draft:
            return Response({"detail": "Draft not found"}, status=404)
        serializer = NovelDraftSerializer(draft)
        return Response(serializer.data)

    def post(self, request):
        owner_key, user, client_id = _resolve_owner_context(request, require_identity=True)
        draft, _ = NovelDraft.objects.get_or_create(owner_key=owner_key)

        state = request.data.get("state")
        if state is None:
            state = {}
        if not isinstance(state, dict):
            raise ValidationError({"state": "state must be a JSON object"})

        draft.title = str(request.data.get("title") or "").strip()[:200]
        draft.state = state
        if user and draft.user_id != user.id:
            draft.user = user
        if client_id and draft.client_id != client_id:
            draft.client_id = client_id
        draft.save()
        serializer = NovelDraftSerializer(draft)
        return Response(serializer.data)


class NovelWorkViewSet(viewsets.ModelViewSet):
    serializer_class = NovelWorkSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        owner_key, _, _ = _resolve_owner_context(self.request, require_identity=False)
        if not owner_key:
            return NovelWork.objects.none()
        return NovelWork.objects.filter(owner_key=owner_key).order_by("-updated_at", "-id")

    def perform_create(self, serializer):
        owner_key, user, client_id = _resolve_owner_context(self.request, require_identity=True)
        serializer.save(owner_key=owner_key, user=user, client_id=client_id)


class PlazaPostViewSet(viewsets.ModelViewSet):
    serializer_class = PlazaPostSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["post_type"]
    ordering_fields = ["created_at", "updated_at", "like_count", "comment_count"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = PlazaPost.objects.all().select_related("user").prefetch_related("comments", "likes")
        owner_key, user, _ = _resolve_owner_context(self.request, require_identity=False)

        if user:
            followee_ids = []
            try:
                # Local import avoids circular import during Django app initialization.
                from users.models import UserFollow

                followee_ids = list(
                    UserFollow.objects.filter(follower=user).values_list("following_id", flat=True)
                )
            except Exception:
                # Gracefully degrade if follow relation tables are not ready.
                followee_ids = []
            own_scope = f"user:{user.pk}"
            visibility_filter = (
                Q(user=user)
                | Q(user__isnull=True, owner_key=own_scope)
                | Q(visibility=PlazaPost.Visibility.PUBLIC)
                | Q(visibility=PlazaPost.Visibility.FOLLOWERS, user_id__in=followee_ids)
            )
            return queryset.filter(visibility_filter).distinct().order_by("-created_at", "-id")

        if owner_key:
            visibility_filter = Q(visibility=PlazaPost.Visibility.PUBLIC) | Q(owner_key=owner_key)
            return queryset.filter(visibility_filter).distinct().order_by("-created_at", "-id")

        return queryset.filter(visibility=PlazaPost.Visibility.PUBLIC).order_by("-created_at", "-id")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        owner_key, _, _ = _resolve_owner_context(self.request, require_identity=False)
        context["owner_key"] = owner_key
        return context

    def perform_create(self, serializer):
        owner_key, user, client_id = _resolve_owner_context(self.request, require_identity=True)
        author_name = str(self.request.data.get("author_name") or "").strip()[:80]
        author_avatar = str(self.request.data.get("author_avatar") or "").strip()[:2000]
        if not author_name and user:
            author_name = str(getattr(user, "name", "") or getattr(user, "username", "") or "").strip()[:80]
        serializer.save(
            owner_key=owner_key,
            user=user,
            client_id=client_id,
            author_name=author_name,
            author_avatar=author_avatar,
        )

    def destroy(self, request, *args, **kwargs):
        owner_key, _, _ = _resolve_owner_context(request, require_identity=True)
        instance = self.get_object()
        if instance.owner_key != owner_key:
            raise PermissionDenied("You can only delete your own posts")
        self.perform_destroy(instance)
        return Response(status=204)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        owner_key, user, client_id = _resolve_owner_context(request, require_identity=True)
        post = self.get_object()
        liked = False

        existing = PlazaLike.objects.filter(post=post, owner_key=owner_key).first()
        if existing:
            existing.delete()
        else:
            PlazaLike.objects.create(post=post, owner_key=owner_key, user=user, client_id=client_id)
            liked = True

        post.like_count = post.likes.count()
        post.save(update_fields=["like_count", "updated_at"])
        return Response({"liked": liked, "like_count": post.like_count})

    @action(detail=True, methods=["post"], url_path="comments")
    def create_comment(self, request, pk=None):
        owner_key, user, client_id = _resolve_owner_context(request, require_identity=True)
        post = self.get_object()
        input_serializer = PlazaCommentSerializer(data=request.data, context=self.get_serializer_context())
        input_serializer.is_valid(raise_exception=True)

        author_name = str(request.data.get("author_name") or "").strip()[:80]
        author_avatar = str(request.data.get("author_avatar") or "").strip()[:2000]
        if not author_name and user:
            author_name = str(getattr(user, "name", "") or getattr(user, "username", "") or "").strip()[:80]

        comment = PlazaComment.objects.create(
            post=post,
            owner_key=owner_key,
            user=user,
            client_id=client_id,
            author_name=author_name,
            author_avatar=author_avatar,
            content=input_serializer.validated_data["content"],
        )
        post.comment_count = post.comments.count()
        post.save(update_fields=["comment_count", "updated_at"])
        output_serializer = PlazaCommentSerializer(comment, context=self.get_serializer_context())
        return Response(output_serializer.data, status=201)

    @action(detail=True, methods=["delete"], url_path=r"comments/(?P<comment_id>[^/.]+)")
    def delete_comment(self, request, pk=None, comment_id=None):
        owner_key, _, _ = _resolve_owner_context(request, require_identity=True)
        post = self.get_object()
        comment = get_object_or_404(PlazaComment, post=post, pk=comment_id)
        if comment.owner_key != owner_key and post.owner_key != owner_key:
            raise PermissionDenied("You can only delete your own comments")

        comment.delete()
        post.comment_count = post.comments.count()
        post.save(update_fields=["comment_count", "updated_at"])
        return Response({"comment_count": post.comment_count})


@require_http_methods(["GET"])
def index(request):
    """Homepage view returning a simple HTML page."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Game Recharge Site</title>
    </head>
    <body>
        <h1>Game Recharge Site</h1>
        <p>Backend service is running.</p>
    </body>
    </html>
    """
    return HttpResponse(html_content)


