# ai_marketing_generator.py
import sys
import os
import json
import random
import shutil
import datetime
import textwrap
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import copy

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, QSpinBox,
        QFileDialog, QMessageBox, QProgressBar, QTabWidget, QGroupBox,
        QCheckBox, QListWidget, QListWidgetItem, QSplitter, QFrame,
        QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QGridLayout,
        QSlider, QRadioButton, QButtonGroup, QColorDialog, QFontDialog
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
    from PyQt6.QtGui import QFont, QIcon, QColor, QPalette, QDesktopServices
    QT_IMPORT_ERROR = None
except ImportError as exc:
    QT_IMPORT_ERROR = exc

    class _MissingQtObject:
        pass

    def pyqtSignal(*_args, **_kwargs):
        return None

    QApplication = QMainWindow = QWidget = QVBoxLayout = QHBoxLayout = _MissingQtObject
    QLabel = QPushButton = QLineEdit = QTextEdit = QComboBox = QSpinBox = _MissingQtObject
    QFileDialog = QMessageBox = QProgressBar = QTabWidget = QGroupBox = _MissingQtObject
    QCheckBox = QListWidget = QListWidgetItem = QSplitter = QFrame = _MissingQtObject
    QTableWidget = QTableWidgetItem = QHeaderView = QDialog = QGridLayout = _MissingQtObject
    QSlider = QRadioButton = QButtonGroup = QColorDialog = QFontDialog = _MissingQtObject
    Qt = QThread = QTimer = QUrl = QFont = QIcon = QColor = QPalette = QDesktopServices = _MissingQtObject


# ==================== 核心AI引擎 ====================

class AIVariantGenerator:
    """AI文本变体生成器"""
    
    TONES = {
        'professional': ['trusted', 'proven', 'reliable', 'premium', 'factory-direct'],
        'casual': ['easy', 'fresh', 'smart', 'popular', 'ready-to-ship'],
        'urgent': ['limited-time', 'fast-moving', 'today-only', 'exclusive', 'last-chance'],
        'emotional': ['confidence-boosting', 'made for you', 'feel-good', 'everyday', 'customer-loved'],
        'luxury': ['elevated', 'refined', 'signature', 'curated', 'high-end']
    }
    
    TEMPLATES = [
        "{badge}\n{headline}\n{benefit}\n{cta}",
        "{badge}\n{headline}\nFactory-direct value, ready for your next campaign.\n{cta}",
        "{badge}\n{headline}\nBetter margins, cleaner visuals, and a smoother buying experience.\n{cta}",
        "{badge}\n{headline}\nStand out in the feed with a simple offer people understand fast.\n{cta}",
        "{badge}\n{headline}\nPremium look. Direct pricing. Fast decision.\n{cta}",
    ]
    
    SYNONYMS = {
        'cheap': ['budget-friendly', 'better-priced', 'factory-direct'],
        'best price': ['factory-direct pricing', 'better direct deals', 'smarter pricing'],
        'good': ['premium', 'reliable', 'high-quality'],
        'fast': ['quick', 'ready-to-ship', 'fast-moving'],
        'new': ['fresh', 'new-season', 'new arrival'],
        'deal': ['offer', 'direct deal', 'limited offer'],
        'quality': ['premium quality', 'reliable quality', 'better finish'],
        'buy': ['shop', 'order', 'claim yours']
    }

    BADGES = [
        "FACTORY DIRECT",
        "BEST PRICE",
        "LIMITED OFFER",
        "NEW ARRIVAL",
        "DIRECT DEAL",
        "FB SPECIAL"
    ]

    DEFAULT_PARTS = {
        'hook': 'Factory-direct deals',
        'benefit': 'Premium products with better margins and a smoother buying experience',
        'cta': 'Learn More'
    }
    
    @classmethod
    def generate_variants(cls, base_text: str, count: int = 5, tone: str = 'professional') -> List[str]:
        variants = []
        tone_words = cls.TONES.get(tone, cls.TONES['professional'])
        parts = cls._parse_text(base_text)
        
        for i in range(count):
            variant = cls._generate_single_variant(parts, tone_words, i)
            variants.append(variant)
        
        return variants
    
    @classmethod
    def _parse_text(cls, text: str) -> Dict[str, str]:
        lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
        cleaned = [cls._english_or_default(line, "") for line in lines]
        cleaned = [line for line in cleaned if line]
        return {
            'hook': cleaned[0] if cleaned else cls.DEFAULT_PARTS['hook'],
            'benefit': cleaned[1] if len(cleaned) > 1 else cls.DEFAULT_PARTS['benefit'],
            'cta': cls._normalize_cta(cleaned[-1]) if len(cleaned) > 2 else cls.DEFAULT_PARTS['cta']
        }
    
    @classmethod
    def _generate_single_variant(cls, parts: Dict, tone_words: List, seed: int) -> str:
        random.seed(seed + datetime.datetime.now().microsecond)
        template = random.choice(cls.TEMPLATES)
        hook = cls._enhance_text(parts['hook'], tone_words)
        benefit = cls._enhance_text(parts['benefit'], tone_words)
        cta = cls._normalize_cta(cls._enhance_text(parts['cta'], tone_words, is_cta=True))
        badge = cls._make_badge(hook, benefit)
        headline = cls._make_headline(hook)
        variant = template.format(badge=badge, headline=headline, benefit=benefit, cta=cta)
        return cls._force_english(variant)
    
    @classmethod
    def _enhance_text(cls, text: str, tone_words: List, is_cta: bool = False) -> str:
        result = cls._english_or_default(text, cls.DEFAULT_PARTS['cta' if is_cta else 'benefit'])
        for word, synonyms in cls.SYNONYMS.items():
            if word in result.lower() and random.random() > 0.45:
                result = re.sub(re.escape(word), random.choice(synonyms), result, count=1, flags=re.IGNORECASE)
        
        if not is_cta and random.random() > 0.6:
            tone = random.choice(tone_words)
            if tone.lower() not in result.lower():
                result = f"{tone.title()} {result}" if random.random() > 0.5 else f"{result} with {tone} appeal"
        
        return cls._sentence_case(result)

    @classmethod
    def _english_or_default(cls, text: str, default: str) -> str:
        text = re.sub(r"[^\x00-\x7F]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip(" -_.,;:!?")
        return text if re.search(r"[A-Za-z]", text) else default

    @classmethod
    def _force_english(cls, text: str) -> str:
        text = re.sub(r"[^\x00-\x7F]+", " ", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r" *\n *", "\n", text)
        return text.strip()

    @classmethod
    def _make_badge(cls, hook: str, benefit: str) -> str:
        combined = f"{hook} {benefit}".lower()
        if "factory" in combined or "direct" in combined:
            return "FACTORY DIRECT"
        if "price" in combined or "deal" in combined or "offer" in combined:
            return "BEST PRICE"
        if "new" in combined or "arrival" in combined:
            return "NEW ARRIVAL"
        return random.choice(cls.BADGES)

    @classmethod
    def _make_headline(cls, hook: str) -> str:
        hook = cls._english_or_default(hook, cls.DEFAULT_PARTS['hook'])
        hook = re.sub(r"\?$", "", hook).strip()
        if len(hook) < 18:
            hook = f"{hook} shoppers notice"
        return cls._title_case_short(hook)

    @classmethod
    def _normalize_cta(cls, text: str) -> str:
        text = cls._english_or_default(text, cls.DEFAULT_PARTS['cta'])
        text = re.sub(r"^(click|tap)\s+", "", text, flags=re.IGNORECASE)
        cta_map = {
            'learn more': 'Learn More',
            'shop now': 'Shop Now',
            'order now': 'Order Now',
            'get offer': 'Get Offer',
            'claim yours': 'Claim Yours',
        }
        key = text.strip().lower()
        if key in cta_map:
            return cta_map[key]
        if len(text) > 18 or not re.search(r"\b(shop|learn|get|order|claim|discover|view)\b", text, re.IGNORECASE):
            return random.choice(['Learn More', 'Shop Now', 'Get Offer'])
        return cls._title_case_short(text)

    @classmethod
    def _sentence_case(cls, text: str) -> str:
        text = text.strip()
        if not text:
            return text
        return text[0].upper() + text[1:]

    @classmethod
    def _title_case_short(cls, text: str) -> str:
        small_words = {'a', 'an', 'and', 'as', 'at', 'for', 'in', 'of', 'on', 'or', 'the', 'to', 'with'}
        words = re.split(r"(\s+)", text.strip())
        titled = []
        word_index = 0
        for token in words:
            if token.isspace():
                titled.append(token)
                continue
            lower = token.lower()
            if word_index > 0 and lower in small_words:
                titled.append(lower)
            else:
                titled.append(token[:1].upper() + token[1:].lower())
            word_index += 1
        return "".join(titled)


class ImageTextRenderer:
    """图片文字渲染引擎 - 把文本压到图片上"""
    
    # Color palettes for English Facebook-style creatives.
    COLOR_SCHEMES = [
        {'name': 'Meta Blue', 'bg': (10, 28, 61, 218), 'text': (255, 255, 255, 255), 'stroke': (0, 0, 0, 210), 'accent': (24, 119, 242, 255), 'button': (24, 119, 242, 255)},
        {'name': 'Direct Deal Orange', 'bg': (31, 22, 14, 218), 'text': (255, 255, 255, 255), 'stroke': (0, 0, 0, 220), 'accent': (255, 184, 77, 255), 'button': (255, 122, 0, 255)},
        {'name': 'Premium Black Gold', 'bg': (13, 16, 22, 220), 'text': (255, 255, 255, 255), 'stroke': (0, 0, 0, 230), 'accent': (236, 191, 92, 255), 'button': (236, 191, 92, 255)},
        {'name': 'Clean White Blue', 'bg': (255, 255, 255, 235), 'text': (20, 27, 38, 255), 'stroke': (255, 255, 255, 255), 'accent': (24, 119, 242, 255), 'button': (24, 119, 242, 255)},
        {'name': 'Sale Red', 'bg': (126, 22, 32, 218), 'text': (255, 255, 255, 255), 'stroke': (80, 0, 0, 220), 'accent': (255, 221, 87, 255), 'button': (236, 57, 77, 255)},
        {'name': 'Luxury Purple', 'bg': (56, 36, 95, 218), 'text': (255, 255, 255, 255), 'stroke': (35, 20, 70, 230), 'accent': (255, 169, 247, 255), 'button': (133, 86, 255, 255)},
        {'name': 'Fresh Green', 'bg': (20, 87, 52, 218), 'text': (255, 255, 255, 255), 'stroke': (5, 60, 30, 220), 'accent': (191, 255, 129, 255), 'button': (37, 184, 111, 255)},
        {'name': 'Transparent Dark Text', 'bg': (0, 0, 0, 0), 'text': (23, 29, 40, 255), 'stroke': (255, 255, 255, 255), 'accent': (24, 119, 242, 255), 'button': (24, 119, 242, 255)},
        {'name': 'Transparent Light Text', 'bg': (0, 0, 0, 0), 'text': (255, 255, 255, 255), 'stroke': (0, 0, 0, 245), 'accent': (255, 196, 87, 255), 'button': (255, 122, 0, 255)},
    ]
    
    STYLE_PRESETS = [
        {'name': 'FB Feed Offer Card', 'layout': 'facebook_ad', 'card': True, 'shadow': True, 'accent': True, 'gradient': True, 'glass': False, 'badge_icon': 'tag'},
        {'name': 'FB Dark Gradient CTA', 'layout': 'facebook_ad', 'card': True, 'shadow': True, 'accent': True, 'gradient': True, 'glass': True, 'badge_icon': 'check'},
        {'name': 'FB Premium Minimal', 'layout': 'facebook_ad', 'card': True, 'shadow': True, 'accent': True, 'gradient': False, 'glass': True, 'badge_icon': 'spark'},
        {'name': 'Modern Poster Card', 'card': True, 'shadow': True, 'accent': True, 'gradient': False, 'glass': False},
        {'name': 'Outline Only', 'card': False, 'shadow': True, 'accent': False, 'gradient': False, 'glass': False},
        {'name': 'Bottom Gradient Title', 'card': False, 'shadow': True, 'accent': True, 'gradient': True, 'glass': False},
        {'name': 'Soft Glass Card', 'card': True, 'shadow': True, 'accent': True, 'gradient': False, 'glass': True},
    ]

    POSITIONS = ['top', 'center', 'bottom', 'top-left', 'top-right', 'bottom-left', 'bottom-right']
    
    def __init__(self):
        self.font_paths = self._find_fonts()
        self.default_font = self.font_paths[0] if self.font_paths else None
    
    def _find_fonts(self) -> List[str]:
        """查找系统中文字体"""
        repo_root = Path(__file__).resolve().parent
        local_font_dirs = [
            repo_root / "assets" / "fonts",
            Path.cwd() / "assets" / "fonts",
            Path.home() / "MarketingAssets" / "fonts",
        ]
        local_fonts = []
        for font_dir in local_font_dirs:
            if font_dir.exists():
                local_fonts.extend(str(p) for p in font_dir.glob("*") if p.suffix.lower() in {".ttf", ".ttc", ".otf"})
        
        possible_fonts = [
            os.environ.get("MARKETING_GENERATOR_FONT", ""),
            # Windows
            "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
            "C:/Windows/Fonts/msyhbd.ttc",    # 微软雅黑粗体
            "C:/Windows/Fonts/simhei.ttf",    # 黑体
            "C:/Windows/Fonts/simsun.ttc",    # 宋体
            "C:/Windows/Fonts/Deng.ttf",      # 等线
            "C:/Windows/Fonts/arial.ttf",     # Arial
            # macOS
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
            # Linux
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansSC-Regular.otf",
            "/usr/share/fonts/truetype/noto/NotoSansSC-Bold.otf",
            "/usr/share/fonts/truetype/arphic/ukai.ttc",
            "/usr/share/fonts/truetype/arphic/uming.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        candidates = local_fonts + [f for f in possible_fonts if f]
        found = []
        seen = set()
        for font in candidates:
            normalized = os.path.abspath(os.path.expanduser(font))
            if normalized not in seen and os.path.exists(normalized):
                found.append(normalized)
                seen.add(normalized)
        return found
    
    def render_text_on_image(self, image_path: str, text: str, output_path: str,
                            position: str = 'center', scheme_idx: int = 0,
                            font_size: int = 40, max_width_ratio: float = 0.86,
                            style_idx: int = 0) -> str:
        """
        将文本渲染到图片上
        
        Args:
            image_path: 原始图片路径
            text: 要添加的文本
            output_path: 输出路径
            position: 文字位置
            scheme_idx: 配色方案索引
            font_size: 字体大小
            max_width_ratio: 文字最大宽度占图片比例
            style_idx: 视觉样式预设
        """
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size

        text_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)

        scheme = self.COLOR_SCHEMES[scheme_idx % len(self.COLOR_SCHEMES)]
        style = self.STYLE_PRESETS[style_idx % len(self.STYLE_PRESETS)]
        if style.get('layout') == 'facebook_ad':
            self._render_facebook_ad(text_layer, draw, text, width, height, scheme, style, font_size, position)
            result = Image.alpha_composite(img, text_layer)
            result = result.convert("RGB")
            result.save(output_path, "JPEG", quality=95)
            return output_path

        font, wrapped_lines, line_height = self._fit_text(draw, text, font_size, width, height, max_width_ratio)
        line_widths = [self._text_width(draw, line, font) for line in wrapped_lines]
        text_width = max(line_widths) if line_widths else 0
        text_height = len(wrapped_lines) * line_height

        padding_x = max(22, int(font.size * 0.72)) if hasattr(font, "size") else 28
        padding_y = max(16, int(font.size * 0.55)) if hasattr(font, "size") else 22
        margin = max(24, int(min(width, height) * 0.045))
        card_width = min(width - margin * 2, text_width + padding_x * 2)
        card_height = min(height - margin * 2, text_height + padding_y * 2)
        card_x, card_y = self._calculate_position(position, width, height, card_width, card_height, margin)
        card_box = [card_x, card_y, card_x + card_width, card_y + card_height]

        if style['gradient']:
            gradient_top = max(0, int(height * 0.48))
            self._draw_bottom_gradient(text_layer, width, height, gradient_top, (0, 0, 0), 210)
            card_y = max(card_y, height - card_height - margin)
            card_box = [card_x, card_y, card_x + card_width, card_y + card_height]

        if style['shadow'] and style['card']:
            self._draw_shadow(text_layer, card_box, radius=max(16, padding_y), opacity=95 if style['card'] else 45)

        if style['card'] and scheme['bg'][3] > 0:
            radius = max(18, int(font.size * 0.45)) if hasattr(font, "size") else 20
            fill = scheme['bg']
            if style['glass']:
                fill = (fill[0], fill[1], fill[2], min(165, fill[3]))
            self._rounded_rectangle(draw, card_box, radius=radius, fill=fill)

        if style['accent']:
            accent_height = max(5, int(font.size * 0.12)) if hasattr(font, "size") else 6
            accent_box = [
                card_x + padding_x,
                card_y + card_height - padding_y + accent_height,
                min(card_x + card_width - padding_x, card_x + padding_x + max(int(card_width * 0.28), 70)),
                card_y + card_height - padding_y + accent_height * 2,
            ]
            self._rounded_rectangle(draw, accent_box, radius=accent_height, fill=scheme.get('accent', scheme['text']))

        align = self._alignment_for_position(position)
        stroke_width = max(2, int(font.size * (0.055 if style['card'] else 0.075))) if hasattr(font, "size") else 2
        current_y = card_y + padding_y
        for line in wrapped_lines:
            line_width = self._text_width(draw, line, font)
            if align == "left":
                x = card_x + padding_x
            elif align == "right":
                x = card_x + card_width - padding_x - line_width
            else:
                x = card_x + (card_width - line_width) // 2
            shadow_offset = max(2, stroke_width)
            draw.text((x + shadow_offset, current_y + shadow_offset), line, font=font, fill=(0, 0, 0, 105))
            draw.text(
                (x, current_y),
                line,
                font=font,
                fill=scheme['text'],
                stroke_width=stroke_width,
                stroke_fill=scheme['stroke'],
            )
            current_y += line_height

        result = Image.alpha_composite(img, text_layer)
        result = result.convert("RGB")
        result.save(output_path, "JPEG", quality=95)
        
        return output_path

    def _render_facebook_ad(self, layer: Image.Image, draw: ImageDraw.Draw, text: str,
                            width: int, height: int, scheme: Dict, style: Dict,
                            font_size: int, position: str):
        badge, headline, body, cta = self._parse_ad_copy(text)
        margin = max(24, int(min(width, height) * 0.045))
        position = 'bottom-left' if position == 'center' else position

        max_card_width = min(width - margin * 2, int(width * 0.86))
        max_card_height = int(height * 0.44)
        base_size = max(26, min(font_size, int(height * 0.082)))

        for size in range(base_size, 17, -2):
            headline_font = self._load_font(size)
            body_font = self._load_font(max(17, int(size * 0.54)))
            meta_font = self._load_font(max(14, int(size * 0.42)))
            cta_font = self._load_font(max(16, int(size * 0.48)))
            pad_x = max(24, int(size * 0.78))
            pad_y = max(20, int(size * 0.58))
            content_width = max_card_width - pad_x * 2
            headline_lines = self._wrap_text(draw, headline, headline_font, content_width)[:2]
            body_lines = self._wrap_text(draw, body, body_font, content_width)[:2]
            headline_h = len(headline_lines) * self._line_height(headline_font)
            body_h = len(body_lines) * self._line_height(body_font)
            badge_h = max(28, int(size * 0.62))
            cta_h = max(34, int(size * 0.72))
            gap = max(9, int(size * 0.20))
            card_height = pad_y * 2 + badge_h + gap + headline_h + gap + body_h + gap + cta_h
            if card_height <= max_card_height or size <= 20:
                break

        card_width = max_card_width
        card_x, card_y = self._calculate_position(position, width, height, card_width, card_height, margin)
        card_box = [card_x, card_y, card_x + card_width, card_y + card_height]

        if style.get('gradient'):
            gradient_top = max(0, card_y - int(height * 0.24))
            self._draw_bottom_gradient(layer, width, height, gradient_top, (0, 0, 0), 185)

        self._draw_shadow(layer, card_box, radius=max(20, int(size * 0.45)), opacity=115)

        fill = scheme['bg']
        if style.get('glass'):
            fill = (fill[0], fill[1], fill[2], min(178, fill[3]))
        self._rounded_rectangle(draw, card_box, radius=max(20, int(size * 0.42)), fill=fill)

        accent = scheme.get('accent', (24, 119, 242, 255))
        button = scheme.get('button', accent)
        text_color = scheme['text']
        muted_color = self._muted_text_color(text_color)

        cursor_x = card_x + pad_x
        cursor_y = card_y + pad_y

        badge_font = meta_font
        icon_size = int(badge_h * 0.48)
        badge_text_w = self._text_width(draw, badge, badge_font)
        badge_w = min(content_width, badge_text_w + icon_size + int(size * 0.72))
        badge_box = [cursor_x, cursor_y, cursor_x + badge_w, cursor_y + badge_h]
        self._rounded_rectangle(draw, badge_box, radius=badge_h // 2, fill=accent)
        icon_center_x = cursor_x + int(size * 0.34)
        icon_center_y = cursor_y + badge_h // 2
        self._draw_vector_icon(draw, style.get('badge_icon', 'tag'), icon_center_x, icon_center_y, icon_size, (255, 255, 255, 255))
        draw.text(
            (cursor_x + icon_size + int(size * 0.42), cursor_y + (badge_h - self._line_height(badge_font)) // 2 - 1),
            badge,
            font=badge_font,
            fill=(255, 255, 255, 255),
        )

        cursor_y += badge_h + gap
        for line in headline_lines:
            draw.text(
                (cursor_x + 2, cursor_y + 2),
                line,
                font=headline_font,
                fill=(0, 0, 0, 125),
            )
            draw.text(
                (cursor_x, cursor_y),
                line,
                font=headline_font,
                fill=text_color,
                stroke_width=max(1, int(size * 0.025)),
                stroke_fill=scheme['stroke'],
            )
            cursor_y += self._line_height(headline_font)

        cursor_y += gap
        check_size = max(14, int(size * 0.30))
        for line in body_lines:
            self._draw_vector_icon(draw, 'check', cursor_x + check_size // 2, cursor_y + self._line_height(body_font) // 2, check_size, accent)
            draw.text(
                (cursor_x + check_size + int(size * 0.18), cursor_y),
                line,
                font=body_font,
                fill=muted_color,
            )
            cursor_y += self._line_height(body_font)

        cursor_y += gap
        cta_text = cta.upper()
        cta_text_w = self._text_width(draw, cta_text, cta_font)
        cta_w = min(content_width, max(int(size * 3.6), cta_text_w + int(size * 1.1)))
        cta_box = [cursor_x, cursor_y, cursor_x + cta_w, cursor_y + cta_h]
        self._rounded_rectangle(draw, cta_box, radius=cta_h // 2, fill=button)
        draw.text(
            (cursor_x + (cta_w - cta_text_w) // 2 - int(size * 0.14), cursor_y + (cta_h - self._line_height(cta_font)) // 2 - 1),
            cta_text,
            font=cta_font,
            fill=(255, 255, 255, 255),
        )
        self._draw_arrow(draw, cursor_x + cta_w - int(size * 0.42), cursor_y + cta_h // 2, max(8, int(size * 0.16)), (255, 255, 255, 255))

        line_y = card_y + card_height - max(8, int(size * 0.12))
        self._rounded_rectangle(
            draw,
            [card_x + pad_x, line_y, card_x + pad_x + int(card_width * 0.20), line_y + max(4, int(size * 0.08))],
            radius=max(2, int(size * 0.05)),
            fill=accent,
        )

    def _parse_ad_copy(self, text: str) -> Tuple[str, str, str, str]:
        text = re.sub(r"[^\x00-\x7F]+", " ", text)
        lines = [re.sub(r"\s+", " ", line).strip(" -_.,;:") for line in text.splitlines()]
        lines = [line for line in lines if line]
        if not lines:
            return "FACTORY DIRECT", "Factory-Direct Deals", "Better pricing with a premium look.", "Learn More"

        first_is_badge = len(lines[0]) <= 28 and lines[0].upper() == lines[0] and re.search(r"[A-Z]", lines[0])
        badge = lines[0].upper() if first_is_badge else "DIRECT DEAL"
        remaining = lines[1:] if first_is_badge else lines
        headline = remaining[0] if remaining else "Factory-Direct Deals"
        body = remaining[1] if len(remaining) > 1 else "Better pricing with a premium look."
        cta = remaining[-1] if len(remaining) > 2 else "Learn More"
        return badge[:28], headline, body, self._normalize_render_cta(cta)

    def _normalize_render_cta(self, text: str) -> str:
        text = re.sub(r"[^A-Za-z ]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        if not text or len(text) > 18:
            return "Learn More"
        return text

    def _muted_text_color(self, text_color: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        if sum(text_color[:3]) > 520:
            return (226, 232, 240, 255)
        return (66, 78, 96, 255)

    def _draw_vector_icon(self, draw: ImageDraw.Draw, kind: str, cx: int, cy: int, size: int, fill):
        half = max(4, size // 2)
        if kind == 'check':
            draw.ellipse([cx - half, cy - half, cx + half, cy + half], fill=fill)
            stroke = max(2, size // 8)
            draw.line(
                [(cx - half // 2, cy), (cx - size // 10, cy + half // 3), (cx + half // 2, cy - half // 3)],
                fill=(255, 255, 255, 255),
                width=stroke,
                joint="curve",
            )
        elif kind == 'spark':
            draw.polygon([(cx, cy - half), (cx + size // 5, cy - size // 5), (cx + half, cy),
                          (cx + size // 5, cy + size // 5), (cx, cy + half), (cx - size // 5, cy + size // 5),
                          (cx - half, cy), (cx - size // 5, cy - size // 5)], fill=fill)
        else:
            points = [
                (cx - half, cy),
                (cx - size // 8, cy - half),
                (cx + half, cy - half),
                (cx + half, cy + size // 8),
                (cx + size // 8, cy + half),
                (cx - half, cy + half),
            ]
            draw.polygon(points, fill=fill)
            draw.ellipse([cx - size // 8, cy - size // 4, cx + size // 12, cy - size // 16], fill=(255, 255, 255, 255))

    def _draw_arrow(self, draw: ImageDraw.Draw, x: int, y: int, size: int, fill):
        draw.line([(x - size, y), (x + size, y)], fill=fill, width=max(2, size // 3))
        draw.polygon([(x + size, y), (x, y - size), (x, y + size)], fill=fill)

    def _load_font(self, size: int):
        try:
            return ImageFont.truetype(self.default_font, size) if self.default_font else ImageFont.load_default()
        except Exception:
            return ImageFont.load_default()

    def _fit_text(self, draw: ImageDraw.Draw, text: str, font_size: int,
                  img_w: int, img_h: int, max_width_ratio: float):
        max_height = int(img_h * 0.48)
        size = max(18, min(font_size, int(img_h * 0.13)))
        min_size = max(16, int(img_h * 0.035))

        while size >= min_size:
            font = self._load_font(size)
            max_width = max(80, int(img_w * max_width_ratio) - max(48, int(size * 1.6)))
            wrapped_lines = self._wrap_text(draw, text, font, max_width)
            line_height = self._line_height(font)
            total_height = len(wrapped_lines) * line_height
            if total_height <= max_height or size == min_size:
                return font, wrapped_lines, line_height
            size -= 2

        font = self._load_font(min_size)
        max_width = max(80, int(img_w * max_width_ratio) - max(48, int(min_size * 1.6)))
        return font, self._wrap_text(draw, text, font, max_width), self._line_height(font)
    
    def _wrap_text(self, draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont, 
                   max_width: int) -> List[str]:
        """智能换行"""
        lines = text.split('\n')
        wrapped = []
        
        for line in lines:
            if not line.strip():
                continue

            tokens = self._tokenize_for_wrap(line.strip())
            current_line = ""

            for token in tokens:
                test_line = current_line + token
                if self._text_width(draw, test_line, font) <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        wrapped.append(current_line)
                    current_line = token.lstrip()
            
            if current_line:
                wrapped.append(current_line)
        
        return wrapped if wrapped else [text[:50]]

    def _tokenize_for_wrap(self, line: str) -> List[str]:
        """中文逐字、英文按词换行，避免中英文混排被硬切得太碎。"""
        tokens = []
        for part in re.findall(r"[A-Za-z0-9_.,!?%+-]+(?:\s+|$)|\s+|.", line):
            tokens.append(part)
        return tokens

    def _text_width(self, draw: ImageDraw.Draw, text: str, font) -> int:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]

    def _line_height(self, font) -> int:
        bbox = font.getbbox("Agy")
        return int((bbox[3] - bbox[1]) * 1.32)
    
    def _calculate_position(self, position: str, img_w: int, img_h: int,
                           text_w: int, text_h: int, margin: int = 30) -> Tuple[int, int]:
        """计算文字位置"""
        positions = {
            'top': (img_w // 2 - text_w // 2, margin),
            'center': (img_w // 2 - text_w // 2, img_h // 2 - text_h // 2),
            'bottom': (img_w // 2 - text_w // 2, img_h - text_h - margin),
            'top-left': (margin, margin),
            'top-right': (img_w - text_w - margin, margin),
            'bottom-left': (margin, img_h - text_h - margin),
            'bottom-right': (img_w - text_w - margin, img_h - text_h - margin),
        }
        
        return positions.get(position, positions['center'])

    def _alignment_for_position(self, position: str) -> str:
        if position.endswith("-left"):
            return "left"
        if position.endswith("-right"):
            return "right"
        return "center"

    def _rounded_rectangle(self, draw: ImageDraw.Draw, box, radius: int, fill, outline=None, width: int = 1):
        try:
            draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
        except AttributeError:
            draw.rectangle(box, fill=fill, outline=outline, width=width)

    def _draw_shadow(self, layer: Image.Image, box, radius: int, opacity: int):
        shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        offset = max(8, radius // 2)
        shadow_box = [box[0] + offset, box[1] + offset, box[2] + offset, box[3] + offset]
        self._rounded_rectangle(shadow_draw, shadow_box, radius=radius, fill=(0, 0, 0, opacity))
        shadow = shadow.filter(ImageFilter.GaussianBlur(max(10, radius // 2)))
        layer.alpha_composite(shadow)

    def _draw_bottom_gradient(self, layer: Image.Image, width: int, height: int,
                              top_y: int, color: Tuple[int, int, int], max_alpha: int):
        gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        gradient_draw = ImageDraw.Draw(gradient)
        span = max(1, height - top_y)
        for y in range(top_y, height):
            alpha = int(max_alpha * ((y - top_y) / span))
            gradient_draw.line([(0, y), (width, y)], fill=(color[0], color[1], color[2], alpha))
        layer.alpha_composite(gradient)


class ContentMixer:
    """内容混合引擎"""
    
    COMBINATION_MODES = [
        "Text Variants",
        "Text + Image Ad",
        "Text + Video",
        "Text + Image + Video",
        "Multi-copy Combo",
        "Full Mix"
    ]
    
    def __init__(self, text_folder: str, image_folder: str, video_folder: str, output_folder: str):
        self.text_folder = Path(text_folder)
        self.image_folder = Path(image_folder)
        self.video_folder = Path(video_folder)
        self.output_folder = Path(output_folder)
        self.renderer = ImageTextRenderer()
        self._load_assets()
    
    def _load_assets(self):
        self.texts = self._load_texts()
        self.images = list(self.image_folder.glob('*')) if self.image_folder.exists() else []
        self.videos = list(self.video_folder.glob('*')) if self.video_folder.exists() else []
        
        self.images = [f for f in self.images if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']]
        self.videos = [f for f in self.videos if f.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv', '.webm']]
    
    def _load_texts(self) -> List[Dict]:
        texts = []
        if not self.text_folder.exists():
            return texts
            
        for file in self.text_folder.glob('*.txt'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        texts.append({
                            'file': file.name,
                            'content': content,
                            'title': content.split('\n')[0][:50]
                        })
            except Exception as e:
                print(f"读取文本失败 {file}: {e}")
        return texts
    
    def generate_combinations(self, mode: str, count: int, variants_per_text: int = 3,
                             text_position: str = 'center', color_scheme: int = 0,
                             font_size: int = 40, style_preset: int = 0) -> List[Dict]:
        """生成组合素材"""
        results = []
        
        if not self.texts:
            return results
        
        for i in range(count):
            base_text = random.choice(self.texts)
            
            variants = AIVariantGenerator.generate_variants(
                base_text['content'], 
                variants_per_text,
                tone=random.choice(['professional', 'casual', 'urgent', 'emotional', 'luxury'])
            )
            
            combination = {
                'id': f"MAT_{datetime.datetime.now().strftime('%Y%m%d')}_{i+1:04d}",
                'base_text_file': base_text['file'],
                'variants': variants,
                'mode': mode,
                'timestamp': datetime.datetime.now().isoformat(),
                'render_params': {
                    'position': text_position,
                    'color_scheme': color_scheme,
                    'color_scheme_name': ImageTextRenderer.COLOR_SCHEMES[color_scheme % len(ImageTextRenderer.COLOR_SCHEMES)]['name'],
                    'font_size': font_size,
                    'style_preset': style_preset,
                    'style_preset_name': ImageTextRenderer.STYLE_PRESETS[style_preset % len(ImageTextRenderer.STYLE_PRESETS)]['name'],
                    'font_name': os.path.basename(self.renderer.default_font) if self.renderer.default_font else 'Pillow default'
                }
            }
            
            # 生成压图素材
            if mode in ["文本+图片(压图)", "文本+图片+视频", "全混合模式",
                        "Text + Image Ad", "Text + Image + Video", "Full Mix"] and self.images:
                selected_images = random.sample(self.images, min(2, len(self.images)))
                combination['images'] = selected_images
                combination['rendered_images'] = []
                
                # 为每个变体生成压图
                for variant_idx, variant in enumerate(variants[:2], 1):  # 最多为前2个变体压图，避免太多
                    for img in selected_images[:1]:  # 每张图只压一次
                        output_img = self.output_folder / f"{combination['id']}_rendered_v{variant_idx}_{img.stem}.jpg"
                        try:
                            self.renderer.render_text_on_image(
                                str(img), variant, str(output_img),
                                position=text_position,
                                scheme_idx=color_scheme,
                                font_size=font_size,
                                style_idx=style_preset
                            )
                            combination['rendered_images'].append(str(output_img.name))
                        except Exception as e:
                            print(f"压图失败 {img}: {e}")
            
            if mode in ["文本+视频", "文本+图片+视频", "全混合模式",
                        "Text + Video", "Text + Image + Video", "Full Mix"] and self.videos:
                combination['videos'] = random.sample(self.videos, min(1, len(self.videos)))
            
            if mode in ["多文本组合", "Multi-copy Combo"]:
                extra_texts = random.sample(self.texts, min(random.randint(1, 2), len(self.texts)-1))
                combination['extra_texts'] = [t['content'][:100] for t in extra_texts]
            
            results.append(combination)
            
        return results
    
    def refresh_assets(self):
        self._load_assets()


# ==================== 工作线程 ====================

class GenerationWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished_signal = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, mixer: ContentMixer, mode: str, count: int, variants: int,
                 position: str, scheme: int, font_size: int, style_preset: int, output_base: str):
        super().__init__()
        self.mixer = mixer
        self.mode = mode
        self.count = count
        self.variants = variants
        self.position = position
        self.scheme = scheme
        self.font_size = font_size
        self.style_preset = style_preset
        self.output_base = Path(output_base)
        self._is_running = True
    
    def run(self):
        try:
            self.status.emit("Generating Facebook marketing creatives...")
            combinations = self.mixer.generate_combinations(
                self.mode, self.count, self.variants,
                self.position, self.scheme, self.font_size, self.style_preset
            )
            
            if not combinations:
                self.error.emit("No text assets found. Add .txt files to the text folder first.")
                return
            
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            output_folder = self.output_base / today
            output_folder.mkdir(parents=True, exist_ok=True)
            
            saved_items = []
            
            for i, combo in enumerate(combinations):
                if not self._is_running:
                    break
                
                self.status.emit(f"Saving creative {i+1}/{len(combinations)}: {combo['id']}")
                
                # 保存元数据
                meta_file = output_folder / f"{combo['id']}_meta.json"
                
                # 处理Path对象序列化
                serializable_combo = copy.deepcopy(combo)
                if 'images' in serializable_combo:
                    serializable_combo['images'] = [str(p) for p in serializable_combo['images']]
                if 'videos' in serializable_combo:
                    serializable_combo['videos'] = [str(p) for p in serializable_combo['videos']]
                
                with open(meta_file, 'w', encoding='utf-8') as f:
                    json.dump(serializable_combo, f, ensure_ascii=False, indent=2)
                
                # 保存文本变体
                combo_id = combo['id']
                text_file = output_folder / f"{combo_id}_variants.txt"
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(f"Base file: {combo['base_text_file']}\n")
                    f.write(f"Mode: {combo['mode']}\n")
                    f.write(f"Generated at: {combo['timestamp']}\n")
                    f.write(f"Render params: position={combo['render_params']['position']}, "
                           f"palette={combo['render_params']['color_scheme_name']}, "
                           f"style={combo['render_params']['style_preset_name']}, "
                           f"font_size={combo['render_params']['font_size']}, "
                           f"font={combo['render_params']['font_name']}\n")
                    f.write("=" * 50 + "\n\n")
                    for j, variant in enumerate(combo['variants'], 1):
                        f.write(f"[Variant {j}]\n{variant}\n\n")
                
                # 复制原始媒体文件
                media_refs = []
                if 'images' in combo:
                    for img in combo['images']:
                        dest = output_folder / f"{combo_id}_img_{img.name}"
                        shutil.copy2(img, dest)
                        media_refs.append(str(dest.name))
                
                if 'videos' in combo:
                    for vid in combo['videos']:
                        dest = output_folder / f"{combo_id}_vid_{vid.name}"
                        shutil.copy2(vid, dest)
                        media_refs.append(str(dest.name))
                
                # 移动已渲染的图片到输出目录
                if 'rendered_images' in combo:
                    for rendered in combo['rendered_images']:
                        src = self.mixer.output_folder / rendered
                        if src.exists():
                            dest = output_folder / rendered
                            shutil.move(str(src), str(dest))
                            media_refs.append(str(dest.name))
                
                saved_items.append({
                    'id': combo['id'],
                    'folder': str(output_folder),
                    'variants_count': len(combo['variants']),
                    'media_files': media_refs,
                    'mode': combo['mode']
                })
                
                progress = int((i + 1) / len(combinations) * 100)
                self.progress.emit(progress)
            
            self.status.emit(f"Done. Generated {len(saved_items)} creatives in {output_folder}")
            self.finished_signal.emit(saved_items)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def stop(self):
        self._is_running = False


# ==================== GUI界面 ====================

class MarketingGeneratorApp(QMainWindow):
    CONFIG_FILE = Path.home() / ".ai_marketing_generator.json"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Marketing Generator v2.2 - Facebook Ad Creatives")
        self.setMinimumSize(1400, 900)

        self.base_folder = self._load_saved_base_folder()
        self.text_folder = None
        self.image_folder = None
        self.video_folder = None
        self.output_folder = None
        self.temp_folder = None
        if self.base_folder:
            self._configure_asset_paths(self.base_folder)
        
        self.mixer = None
        self.worker = None
        
        self.init_ui()
        if self.base_folder:
            self.refresh_assets()
        else:
            self.refresh_assets()
            QTimer.singleShot(0, self.change_base_folder)
    
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([450, 950])
        
        main_layout.addWidget(splitter)

    def _load_saved_base_folder(self) -> Optional[Path]:
        try:
            if not self.CONFIG_FILE.exists():
                return None
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            folder = data.get('asset_root')
            if not folder:
                return None
            path = Path(folder).expanduser()
            return path if path.exists() and path.is_dir() else None
        except Exception:
            return None

    def _save_base_folder(self):
        if not self.base_folder:
            return
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump({'asset_root': str(self.base_folder)}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save app settings: {e}")

    def _configure_asset_paths(self, base_folder: Path):
        self.base_folder = Path(base_folder).expanduser()
        self.text_folder = self._preferred_asset_folder("texts")
        self.image_folder = self._preferred_asset_folder("images")
        self.video_folder = self._preferred_asset_folder("videos")
        self.output_folder = self.base_folder / "output"
        self.temp_folder = self.base_folder / ".marketing_generator_temp"

    def _preferred_asset_folder(self, subfolder_name: str) -> Path:
        candidate = self.base_folder / subfolder_name
        return candidate if candidate.exists() and candidate.is_dir() else self.base_folder

    def _path_text(self, path: Optional[Path]) -> str:
        return str(path) if path else "Not selected"

    def _update_path_labels(self):
        if not hasattr(self, 'path_labels'):
            return
        self.path_labels['base'].setText(self._path_text(self.base_folder))
        self.path_labels['text'].setText(self._path_text(self.text_folder))
        self.path_labels['image'].setText(self._path_text(self.image_folder))
        self.path_labels['video'].setText(self._path_text(self.video_folder))
        self.path_labels['output'].setText(self._path_text(self.output_folder))
    
    def create_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # === 文件夹设置 ===
        folder_group = QGroupBox("Asset folders")
        folder_layout = QGridLayout()
        
        self.path_labels = {}
        paths = [
            ('base', 'Selected asset folder', self._path_text(self.base_folder)),
            ('text', 'Copy source', self._path_text(self.text_folder)),
            ('image', 'Image source', self._path_text(self.image_folder)),
            ('video', 'Video source', self._path_text(self.video_folder)),
            ('output', 'Output', self._path_text(self.output_folder))
        ]
        
        for i, (key, label, path) in enumerate(paths):
            folder_layout.addWidget(QLabel(f"{label}:"), i, 0)
            lbl = QLabel(path)
            lbl.setStyleSheet("color: #666; font-size: 11px;")
            lbl.setWordWrap(True)
            self.path_labels[key] = lbl
            folder_layout.addWidget(lbl, i, 1)
        
        btn_change = QPushButton("Select asset folder")
        btn_change.clicked.connect(self.change_base_folder)
        folder_layout.addWidget(btn_change, len(paths), 0, 1, 2)
        
        btn_open = QPushButton("Open folder")
        btn_open.clicked.connect(self.open_folders)
        folder_layout.addWidget(btn_open, len(paths)+1, 0, 1, 2)
        
        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)
        
        # === 生成设置 ===
        gen_group = QGroupBox("Generation settings")
        gen_layout = QVBoxLayout()
        
        # 组合模式
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(ContentMixer.COMBINATION_MODES)
        self.mode_combo.setCurrentIndex(1)
        mode_layout.addWidget(self.mode_combo)
        gen_layout.addLayout(mode_layout)
        
        # 生成数量
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Creative count:"))
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 100)
        self.count_spin.setValue(10)
        count_layout.addWidget(self.count_spin)
        gen_layout.addLayout(count_layout)
        
        # 每文本变体数
        var_layout = QHBoxLayout()
        var_layout.addWidget(QLabel("Copy variants:"))
        self.variant_spin = QSpinBox()
        self.variant_spin.setRange(1, 10)
        self.variant_spin.setValue(3)
        var_layout.addWidget(self.variant_spin)
        gen_layout.addLayout(var_layout)
        
        gen_group.setLayout(gen_layout)
        layout.addWidget(gen_group)
        
        # === 压图渲染设置 ===
        render_group = QGroupBox("Facebook ad rendering")
        render_layout = QVBoxLayout()
        
        # 文字位置
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("Ad position:"))
        self.pos_combo = QComboBox()
        self.pos_combo.addItems(['center', 'top', 'bottom', 'top-left', 'top-right', 'bottom-left', 'bottom-right'])
        self.pos_combo.setCurrentIndex(5)
        pos_layout.addWidget(self.pos_combo)
        render_layout.addLayout(pos_layout)
        
        # 配色方案
        scheme_layout = QHBoxLayout()
        scheme_layout.addWidget(QLabel("Palette:"))
        self.scheme_combo = QComboBox()
        for scheme in ImageTextRenderer.COLOR_SCHEMES:
            self.scheme_combo.addItem(scheme['name'])
        self.scheme_combo.setCurrentIndex(0)
        scheme_layout.addWidget(self.scheme_combo)
        render_layout.addLayout(scheme_layout)

        # 视觉样式
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("Ad style:"))
        self.style_combo = QComboBox()
        for preset in ImageTextRenderer.STYLE_PRESETS:
            self.style_combo.addItem(preset['name'])
        self.style_combo.setCurrentIndex(0)
        style_layout.addWidget(self.style_combo)
        render_layout.addLayout(style_layout)
        
        # 字体大小
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Headline size:"))
        self.font_spin = QSpinBox()
        self.font_spin.setRange(12, 120)
        self.font_spin.setValue(40)
        font_layout.addWidget(self.font_spin)
        render_layout.addLayout(font_layout)
        
        render_group.setLayout(render_layout)
        layout.addWidget(render_group)
        
        # === 素材库状态 ===
        status_group = QGroupBox("Asset library")
        status_layout = QVBoxLayout()
        
        self.status_texts = QLabel("Copy files: 0")
        self.status_images = QLabel("Images: 0")
        self.status_videos = QLabel("Videos: 0")
        self.status_fonts = QLabel("Font: checking...")
        
        for lbl in [self.status_texts, self.status_images, self.status_videos, self.status_fonts]:
            status_layout.addWidget(lbl)
        
        btn_refresh = QPushButton("Refresh assets")
        btn_refresh.clicked.connect(self.refresh_assets)
        status_layout.addWidget(btn_refresh)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # === 操作按钮 ===
        self.btn_generate = QPushButton("Generate Facebook creatives")
        self.btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        self.btn_generate.clicked.connect(self.start_generation)
        layout.addWidget(self.btn_generate)
        
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_generation)
        layout.addWidget(self.btn_stop)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        return panel
    
    def create_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        tabs = QTabWidget()
        
        # === 预览标签页 ===
        preview_tab = QWidget()
        preview_layout = QVBoxLayout(preview_tab)
        
        preview_layout.addWidget(QLabel("Latest Facebook copy variants:"))
        self.preview_list = QListWidget()
        self.preview_list.setMaximumHeight(200)
        self.preview_list.itemClicked.connect(self.show_variant_detail)
        preview_layout.addWidget(self.preview_list)
        
        preview_layout.addWidget(QLabel("Selected variant detail:"))
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        preview_layout.addWidget(self.detail_text)
        
        tabs.addTab(preview_tab, "Copy preview")
        
        # === 压图预览标签页 ===
        image_tab = QWidget()
        image_layout = QVBoxLayout(image_tab)
        
        image_layout.addWidget(QLabel("Rendered image ad preview:"))
        self.image_list = QListWidget()
        self.image_list.setMaximumHeight(200)
        self.image_list.itemClicked.connect(self.show_image_detail)
        image_layout.addWidget(self.image_list)
        
        self.image_detail = QTextEdit()
        self.image_detail.setReadOnly(True)
        self.image_detail.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        image_layout.addWidget(self.image_detail)
        
        tabs.addTab(image_tab, "Image ads")
        
        # === 历史标签页 ===
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        
        history_layout.addWidget(QLabel("Generation history by date:"))
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(['Date', 'Creative ID', 'Mode', 'Variants', 'Image ads', 'Folder'])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        history_layout.addWidget(self.history_table)
        
        btn_load_history = QPushButton("Load history")
        btn_load_history.clicked.connect(self.load_history)
        history_layout.addWidget(btn_load_history)
        
        tabs.addTab(history_tab, "History")
        
        # === API就绪标签页 ===
        api_tab = QWidget()
        api_layout = QVBoxLayout(api_tab)
        
        api_info = QTextEdit()
        api_info.setReadOnly(True)
        api_info.setHtml("""
        <h3>API integration guide</h3>
        <p>Generated assets are saved in a predictable structure for platform/API workflows:</p>
        <pre style="background:#f0f0f0;padding:10px;border-radius:4px;">
output/
├── 2026-05-12/
│   ├── MAT_20260512_0001_meta.json          # metadata
│   ├── MAT_20260512_0001_variants.txt       # English ad copy
│   ├── MAT_20260512_0001_img_xxx.jpg        # source image
│   ├── MAT_20260512_0001_rendered_xxx.jpg   # rendered ad creative
│   └── MAT_20260512_0001_vid_xxx.mp4        # linked video
        </pre>
        <p><b>Rendered image naming:</b></p>
        <ul>
            <li><code>MAT_xxx_rendered_v1_[source].jpg</code> → finished ad image with copy</li>
            <li>Ready for Facebook, Instagram, and TikTok publishing flows</li>
        </ul>
        <p><b>Suggested publishing flow:</b></p>
        <ol>
            <li>Scan the latest date folder under output/</li>
            <li>Read *_meta.json for creative metadata</li>
            <li>Upload <b>rendered_*.jpg</b> to the social platform</li>
            <li>Use variants.txt copy as the post/ad description</li>
        </ol>
        </pre>
        """)
        api_layout.addWidget(api_info)
        
        tabs.addTab(api_tab, "API ready")
        
        layout.addWidget(tabs)
        return panel
    
    def change_base_folder(self):
        start_folder = str(self.base_folder) if self.base_folder else str(Path.home())
        folder = QFileDialog.getExistingDirectory(self, "Choose asset folder", start_folder)
        if folder:
            self._configure_asset_paths(Path(folder))
            self._save_base_folder()
            self._update_path_labels()
            self.refresh_assets()
    
    def open_folders(self):
        if not self.base_folder:
            self.change_base_folder()
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.base_folder)))
    
    def refresh_assets(self):
        if not self.base_folder:
            self.mixer = None
            self.status_texts.setText("Copy files: select an asset folder")
            self.status_images.setText("Images: select an asset folder")
            self.status_videos.setText("Videos: select an asset folder")
            self.status_fonts.setText("Font: select an asset folder")
            for lbl in [self.status_texts, self.status_images, self.status_videos, self.status_fonts]:
                lbl.setStyleSheet("color: orange;")
            self._update_path_labels()
            return

        self._configure_asset_paths(self.base_folder)
        self._update_path_labels()
        self.mixer = ContentMixer(
            str(self.text_folder), 
            str(self.image_folder), 
            str(self.video_folder),
            str(self.temp_folder)
        )
        
        self.status_texts.setText(f"Copy files: {len(self.mixer.texts)}")
        self.status_images.setText(f"Images: {len(self.mixer.images)}")
        self.status_videos.setText(f"Videos: {len(self.mixer.videos)}")
        
        # 检测字体
        if self.mixer.renderer.default_font:
            self.status_fonts.setText(f"Font: {os.path.basename(self.mixer.renderer.default_font)}")
            self.status_fonts.setStyleSheet("color: green;")
        else:
            self.status_fonts.setText("Font: no custom/system font found")
            self.status_fonts.setStyleSheet("color: red;")
        
        self.status_texts.setStyleSheet("color: green;" if self.mixer.texts else "color: red;")
        self.status_images.setStyleSheet("color: green;" if self.mixer.images else "color: orange;")
        self.status_videos.setStyleSheet("color: green;" if self.mixer.videos else "color: orange;")
    
    def start_generation(self):
        if not self.base_folder:
            QMessageBox.warning(self, "Select asset folder", "Please choose the folder that contains your source assets first.")
            self.change_base_folder()
            return

        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.temp_folder.mkdir(parents=True, exist_ok=True)
        self.refresh_assets()

        if not self.mixer or not self.mixer.texts:
            QMessageBox.warning(
                self,
                "Missing copy assets",
                "Add .txt copy assets to the selected folder or its texts subfolder.\nPath: " + str(self.text_folder)
            )
            return
        
        mode = self.mode_combo.currentText()
        count = self.count_spin.value()
        variants = self.variant_spin.value()
        position = self.pos_combo.currentText()
        scheme = self.scheme_combo.currentIndex()
        font_size = self.font_spin.value()
        style_preset = self.style_combo.currentIndex()
        
        self.btn_generate.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress_bar.setValue(0)
        
        self.worker = GenerationWorker(
            self.mixer, mode, count, variants,
            position, scheme, font_size, style_preset,
            str(self.output_folder)
        )
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.status.connect(self.status_label.setText)
        self.worker.finished_signal.connect(self.generation_finished)
        self.worker.error.connect(self.generation_error)
        self.worker.start()
    
    def stop_generation(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait()
        self.btn_generate.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.status_label.setText("Stopped")
    
    def generation_finished(self, items: List[Dict]):
        self.btn_generate.setEnabled(True)
        self.btn_stop.setEnabled(False)
        
        # 更新文本预览
        self.preview_list.clear()
        for item in items:
            for i in range(item['variants_count']):
                list_item = QListWidgetItem(f"{item['id']} - Variant {i+1}")
                list_item.setData(Qt.ItemDataRole.UserRole, item)
                self.preview_list.addItem(list_item)
        
        # 更新压图预览
        self.image_list.clear()
        for item in items:
            for media in item.get('media_files', []):
                if 'rendered_' in media:
                    list_item = QListWidgetItem(f"Image ad: {media}")
                    list_item.setData(Qt.ItemDataRole.UserRole, item)
                    self.image_list.addItem(list_item)
        
        QMessageBox.information(self, "Generation complete",
            f"Generated {len(items)} creative groups.\nRendered image ads are ready for social posting.\nOutput: {self.output_folder}")
        self.load_history()
    
    def generation_error(self, error_msg: str):
        self.btn_generate.setEnabled(True)
        self.btn_stop.setEnabled(False)
        QMessageBox.critical(self, "Generation error", error_msg)
    
    def show_variant_detail(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            folder = Path(data['folder'])
            var_file = folder / f"{data['id']}_variants.txt"
            if var_file.exists():
                with open(var_file, 'r', encoding='utf-8') as f:
                    self.detail_text.setText(f.read())
    
    def show_image_detail(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            self.image_detail.setText(f"Creative ID: {data['id']}\nFolder: {data['folder']}\nFiles:\n" +
                                      "\n".join(data.get('media_files', [])))
    
    def load_history(self):
        self.history_table.setRowCount(0)
        
        if not self.output_folder or not self.output_folder.exists():
            return
        
        row = 0
        for date_folder in sorted(self.output_folder.iterdir(), reverse=True):
            if date_folder.is_dir():
                for meta_file in date_folder.glob("*_meta.json"):
                    try:
                        with open(meta_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        rendered_count = len([m for m in data.get('rendered_images', []) if m])
                        
                        self.history_table.insertRow(row)
                        self.history_table.setItem(row, 0, QTableWidgetItem(date_folder.name))
                        self.history_table.setItem(row, 1, QTableWidgetItem(data['id']))
                        self.history_table.setItem(row, 2, QTableWidgetItem(data['mode']))
                        self.history_table.setItem(row, 3, QTableWidgetItem(str(len(data['variants']))))
                        self.history_table.setItem(row, 4, QTableWidgetItem(str(rendered_count)))
                        self.history_table.setItem(row, 5, QTableWidgetItem(str(date_folder)))
                        row += 1
                    except:
                        pass


def main():
    if QT_IMPORT_ERROR is not None:
        raise RuntimeError(
            "PyQt6/Qt desktop dependencies are unavailable. "
            "Install the project dependencies and required system GUI libraries, then run again."
        ) from QT_IMPORT_ERROR

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(50, 50, 50))
    app.setPalette(palette)
    
    window = MarketingGeneratorApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()