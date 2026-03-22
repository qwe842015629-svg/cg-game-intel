import hashlib
import logging
import mimetypes
import re
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.utils.text import slugify

from main.models import MediaAsset

logger = logging.getLogger(__name__)


class GooglePlayScraper:
    """Google Play 商店抓取工具"""

    REQUEST_TIMEOUT = 8

    HEADERS = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/123.0.0.0 Safari/537.36'
        ),
        'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
        'Referer': 'https://play.google.com/',
    }

    @staticmethod
    def extract_id_from_url(url):
        """从 URL 中提取包名 ID"""
        try:
            parsed = urlparse(url)
            query = parse_qs(parsed.query)
            package_id = query.get('id', [None])[0]
            if package_id:
                return package_id.strip()
        except Exception:
            return None
        return None

    @staticmethod
    def normalize_icon_url(icon_url):
        value = (icon_url or '').strip()
        if not value:
            return ''
        if value.startswith('//'):
            return f'https:{value}'
        return value

    @staticmethod
    def build_icon_candidates(icon_url):
        """构建多个下载候选地址，提升图标下载成功率"""
        normalized = GooglePlayScraper.normalize_icon_url(icon_url)
        if not normalized:
            return []

        candidates = [normalized]

        # 常见的 googleusercontent 尾部尺寸参数，改成更大的 s512 版本
        sized = re.sub(r'=[^/?#]+$', '=s512', normalized)
        if sized not in candidates:
            candidates.append(sized)

        # 兼容部分带 query 的链接
        base, sep, query = normalized.partition('?')
        sized_base = re.sub(r'=[^/?#]+$', '=s512', base)
        with_query = f'{sized_base}?{query}' if sep else sized_base
        if with_query not in candidates:
            candidates.append(with_query)

        return candidates

    @staticmethod
    def _guess_extension(download_url, content_type):
        ext = ''
        if content_type:
            ext = mimetypes.guess_extension(content_type.split(';')[0].strip()) or ''
        if not ext and download_url:
            parsed = urlparse(download_url)
            ext = parsed.path.rsplit('.', 1)[-1] if '.' in parsed.path else ''
            if ext:
                ext = f'.{ext.lower()}'
        if not ext:
            ext = '.png'

        # 标准化 jpeg 后缀
        if ext == '.jpe':
            ext = '.jpg'
        return ext.lstrip('.')

    @staticmethod
    def _build_filename(title, package_id, stable_key, ext):
        base_name = slugify(title) or slugify(package_id or '') or 'game-icon'
        digest = hashlib.md5(stable_key.encode('utf-8')).hexdigest()[:10]
        return f'{base_name}-{digest}.{ext}'

    def fetch_game_info(self, url):
        """抓取游戏信息"""
        package_id = self.extract_id_from_url(url) or (url or '').strip()
        if not package_id:
            return {'error': '无效的 Google Play 链接'}

        play_url = (
            'https://play.google.com/store/apps/details'
            f'?id={package_id}&hl=zh_TW&gl=HK'
        )

        try:
            response = requests.get(play_url, headers=self.HEADERS, timeout=self.REQUEST_TIMEOUT)
            if response.status_code != 200:
                return {'error': f'无法访问页面 (HTTP {response.status_code})'}

            soup = BeautifulSoup(response.text, 'html.parser')

            # 1. 标题
            title = ''
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text(strip=True)
            if not title:
                title_tag = soup.find(attrs={'itemprop': 'name'})
                if title_tag:
                    title = title_tag.get_text(strip=True)
            if not title:
                og_title = soup.find('meta', attrs={'property': 'og:title'})
                if og_title and og_title.get('content'):
                    title = og_title.get('content').strip()
                    title = re.sub(r'\s*-\s*Google Play.*$', '', title, flags=re.IGNORECASE)

            # 2. 图标
            icon_url = ''
            meta_image = soup.find('meta', attrs={'property': 'og:image'})
            if meta_image and meta_image.get('content'):
                icon_url = meta_image.get('content')

            if not icon_url:
                icon_img = soup.find('img', attrs={'itemprop': 'image'})
                if icon_img and icon_img.get('src'):
                    icon_url = icon_img.get('src')

            if not icon_url:
                imgs = soup.find_all('img', src=re.compile(r'googleusercontent'))
                for img in imgs:
                    src = (img.get('src') or '').strip()
                    if not src:
                        continue
                    if img.get('width') == '32' or img.get('height') == '32':
                        continue
                    icon_url = src
                    break

            icon_url = self.normalize_icon_url(icon_url)

            # 3. 开发商
            developer = ''
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/store/apps/dev' in href or '/store/apps/developer' in href:
                    developer = a.get_text(strip=True)
                    break

            # 4. 简介
            description = ''

            # 页面里常见两个描述节点：itemprop 可能存在但为空，优先取 data-g-id。
            desc_candidates = [
                soup.find(attrs={'data-g-id': 'description'}),
                soup.find(attrs={'itemprop': 'description'}),
            ]
            for node in desc_candidates:
                if not node:
                    continue
                text = node.get_text(' ', strip=True)
                if text:
                    description = text
                    break

            # 兜底：若正文描述仍为空，至少用 meta 描述保证“导入配齐”可用。
            if not description:
                for attrs in (
                    {'property': 'og:description'},
                    {'name': 'description'},
                ):
                    meta_desc = soup.find('meta', attrs=attrs)
                    if meta_desc and meta_desc.get('content'):
                        description = meta_desc.get('content').strip()
                        if description:
                            break

            description = re.sub(r'\s+', ' ', description).strip()[:300]

            return {
                'title': title,
                'package_id': package_id,
                'icon_url': icon_url,
                'developer': developer,
                'description': description,
            }
        except Exception as exc:
            logger.error('Scraper error: %s', exc)
            return {'error': str(exc)}

    def _download_icon(self, icon_url):
        last_error = None
        for candidate in self.build_icon_candidates(icon_url):
            try:
                response = requests.get(candidate, headers=self.HEADERS, timeout=self.REQUEST_TIMEOUT)
                if response.status_code != 200:
                    continue

                content = response.content or b''
                if not content:
                    continue

                content_type = (response.headers.get('Content-Type') or '').split(';')[0].strip().lower()
                if content_type and not content_type.startswith('image/'):
                    continue

                return candidate, content, content_type
            except Exception as exc:
                last_error = exc
                continue

        if last_error:
            logger.error('Image download error: %s', last_error)
        return None, None, None

    def save_icon_to_media_library(self, icon_url, title, package_id=''):
        """下载图标并保存到素材库"""
        normalized_icon_url = self.normalize_icon_url(icon_url)
        if not normalized_icon_url:
            return None

        resolved_url, binary, content_type = self._download_icon(normalized_icon_url)
        if not binary:
            return None

        ext = self._guess_extension(resolved_url or normalized_icon_url, content_type)
        stable_key = resolved_url or normalized_icon_url
        filename = self._build_filename(title or 'game-icon', package_id, stable_key, ext)

        existing = MediaAsset.objects.filter(name=filename).first()
        if existing:
            return existing

        media = MediaAsset(
            name=filename,
            category='icon',
            alt_text=f'{title or package_id} Icon from Google Play',
            file_size=len(binary) // 1024,
        )
        media.file.save(filename, ContentFile(binary), save=True)
        return media
