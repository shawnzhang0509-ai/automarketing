# ai_marketing_generator.py
import sys
import os
import json
import random
import shutil
import datetime
import textwrap
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import copy

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QFileDialog, QMessageBox, QProgressBar, QTabWidget, QGroupBox,
    QCheckBox, QListWidget, QListWidgetItem, QSplitter, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QGridLayout,
    QSlider, QRadioButton, QButtonGroup, QColorDialog, QFontDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette


# ==================== 核心AI引擎 ====================

class AIVariantGenerator:
    """AI文本变体生成器"""
    
    TONES = {
        'professional': ['专业', '可靠', '值得信赖', '行业领先', '品质保证'],
        'casual': ['超棒', '绝了', '赶紧', '别错过', '快来'],
        'urgent': ['限时', '马上', '立即', '最后机会', '抢购'],
        'emotional': ['梦想', '温暖', '陪伴', '幸福', '安心'],
        'luxury': ['尊贵', '臻品', '典藏', '奢华', '非凡']
    }
    
    TEMPLATES = [
        "{hook}，{benefit}，{cta}",
        "{benefit}？{hook}！{cta}",
        "【{hook}】{benefit}。{cta}",
        "{cta}！{benefit}，{hook}",
        "你知道吗？{hook}。{benefit}，{cta}",
        "{hook}... {benefit}。现在就{cta}！",
        "🔥 {hook} 🔥\n\n{benefit}\n\n👉 {cta}",
        "❓ 为什么{hook}？\n✅ 因为{benefit}\n🎯 {cta}"
    ]
    
    SYNONYMS = {
        '便宜': ['实惠', '划算', '超值', '性价比高', '亲民价'],
        '好': ['优质', '卓越', '出色', '顶级', '一流'],
        '快': ['迅速', '高效', '即时', '闪电', '极速'],
        '新': ['全新', '创新', '前沿', '新潮', '焕新'],
        '大': ['超大', '海量', '广阔', '宏伟', '磅礴'],
        '买': ['入手', '抢购', '收藏', '拥有', '带回家'],
        '优惠': ['特惠', '折扣', '让利', '回馈', '福利'],
        '品质': ['质量', '做工', '用料', '标准', '品控']
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
        return {
            'hook': lines[0] if lines else '发现精彩',
            'benefit': lines[1] if len(lines) > 1 else '为您带来卓越体验',
            'cta': lines[-1] if len(lines) > 2 else '立即了解详情'
        }
    
    @classmethod
    def _generate_single_variant(cls, parts: Dict, tone_words: List, seed: int) -> str:
        random.seed(seed + datetime.datetime.now().microsecond)
        template = random.choice(cls.TEMPLATES)
        hook = cls._enhance_text(parts['hook'], tone_words)
        benefit = cls._enhance_text(parts['benefit'], tone_words)
        cta = cls._enhance_text(parts['cta'], tone_words, is_cta=True)
        variant = template.format(hook=hook, benefit=benefit, cta=cta)
        
        if random.random() > 0.7:
            emojis = ['✨', '🎯', '💎', '🔥', '⭐', '🚀', '💡', '🎁']
            variant = random.choice(emojis) + " " + variant
        
        return variant
    
    @classmethod
    def _enhance_text(cls, text: str, tone_words: List, is_cta: bool = False) -> str:
        result = text
        for word, synonyms in cls.SYNONYMS.items():
            if word in result and random.random() > 0.5:
                result = result.replace(word, random.choice(synonyms), 1)
        
        if not is_cta and random.random() > 0.6:
            tone = random.choice(tone_words)
            if tone not in result:
                result = f"{tone}的{result}" if random.random() > 0.5 else f"{result}，{tone}"
        
        return result


class ImageTextRenderer:
    """图片文字渲染引擎 - 把文本压到图片上"""
    
    # 预设配色方案 (背景透明度, 文字颜色, 描边颜色)
    COLOR_SCHEMES = [
        {'name': '经典黑底白字', 'bg': (0, 0, 0, 180), 'text': (255, 255, 255, 255), 'stroke': (0, 0, 0, 255)},
        {'name': '白底黑字', 'bg': (255, 255, 255, 200), 'text': (0, 0, 0, 255), 'stroke': (255, 255, 255, 255)},
        {'name': '红底白字', 'bg': (220, 53, 69, 200), 'text': (255, 255, 255, 255), 'stroke': (150, 0, 0, 255)},
        {'name': '蓝底白字', 'bg': (0, 123, 255, 200), 'text': (255, 255, 255, 255), 'stroke': (0, 80, 180, 255)},
        {'name': '金底黑字', 'bg': (255, 215, 0, 200), 'text': (0, 0, 0, 255), 'stroke': (180, 150, 0, 255)},
        {'name': '紫底白字', 'bg': (111, 66, 193, 200), 'text': (255, 255, 255, 255), 'stroke': (80, 40, 150, 255)},
        {'name': '绿底白字', 'bg': (40, 167, 69, 200), 'text': (255, 255, 255, 255), 'stroke': (20, 120, 40, 255)},
        {'name': '透明黑字', 'bg': (0, 0, 0, 0), 'text': (0, 0, 0, 255), 'stroke': (255, 255, 255, 255)},
        {'name': '透明白字', 'bg': (0, 0, 0, 0), 'text': (255, 255, 255, 255), 'stroke': (0, 0, 0, 255)},
    ]
    
    POSITIONS = ['top', 'center', 'bottom', 'top-left', 'top-right', 'bottom-left', 'bottom-right']
    
    def __init__(self):
        self.font_paths = self._find_fonts()
        self.default_font = self.font_paths[0] if self.font_paths else None
    
    def _find_fonts(self) -> List[str]:
        """查找系统中文字体"""
        possible_fonts = [
            # Windows
            "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",    # 黑体
            "C:/Windows/Fonts/simsun.ttc",    # 宋体
            "C:/Windows/Fonts/arial.ttf",     # Arial
            # macOS
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            # Linux
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        found = [f for f in possible_fonts if os.path.exists(f)]
        return found
    
    def render_text_on_image(self, image_path: str, text: str, output_path: str,
                            position: str = 'center', scheme_idx: int = 0,
                            font_size: int = 40, max_width_ratio: float = 0.9) -> str:
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
        """
        # 打开图片
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size
        
        # 创建文字层
        text_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)
        
        # 加载字体
        try:
            font = ImageFont.truetype(self.default_font, font_size) if self.default_font else ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # 获取配色方案
        scheme = self.COLOR_SCHEMES[scheme_idx % len(self.COLOR_SCHEMES)]
        
        # 处理文本换行
        max_width = int(width * max_width_ratio)
        wrapped_lines = self._wrap_text(draw, text, font, max_width)
        
        # 计算文字总高度
        line_height = font_size + 8
        total_text_height = len(wrapped_lines) * line_height + 40  # 上下padding各20
        
        # 计算位置
        x, y = self._calculate_position(position, width, height, 
                                        max_width, total_text_height)
        
        # 绘制背景条
        bg_padding = 20
        bg_left = x - bg_padding
        bg_top = y - bg_padding
        bg_right = min(x + max_width + bg_padding, width)
        bg_bottom = min(y + total_text_height + bg_padding, height)
        
        if scheme['bg'][3] > 0:  # 背景不透明才画
            draw.rectangle([bg_left, bg_top, bg_right, bg_bottom], 
                          fill=scheme['bg'])
        
        # 绘制文字（带描边）
        current_y = y
        for line in wrapped_lines:
            # 描边
            for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1), (0,-1), (0,1), (-1,0), (1,0)]:
                draw.text((x+dx, current_y+dy), line, font=font, fill=scheme['stroke'])
            # 主文字
            draw.text((x, current_y), line, font=font, fill=scheme['text'])
            current_y += line_height
        
        # 合并图层
        result = Image.alpha_composite(img, text_layer)
        result = result.convert("RGB")
        result.save(output_path, "JPEG", quality=95)
        
        return output_path
    
    def _wrap_text(self, draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont, 
                   max_width: int) -> List[str]:
        """智能换行"""
        lines = text.split('\n')
        wrapped = []
        
        for line in lines:
            if not line.strip():
                continue
                
            words = line
            current_line = ""
            
            for char in words:
                test_line = current_line + char
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        wrapped.append(current_line)
                    current_line = char
            
            if current_line:
                wrapped.append(current_line)
        
        return wrapped if wrapped else [text[:50]]
    
    def _calculate_position(self, position: str, img_w: int, img_h: int,
                           text_w: int, text_h: int) -> Tuple[int, int]:
        """计算文字位置"""
        margin = 30
        
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


class ContentMixer:
    """内容混合引擎"""
    
    COMBINATION_MODES = [
        "纯文本变体",
        "文本+图片(压图)",
        "文本+视频",
        "文本+图片+视频",
        "多文本组合",
        "全混合模式"
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
                             font_size: int = 40) -> List[Dict]:
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
                    'font_size': font_size
                }
            }
            
            # 生成压图素材
            if mode in ["文本+图片(压图)", "文本+图片+视频", "全混合模式"] and self.images:
                selected_images = random.sample(self.images, min(2, len(self.images)))
                combination['images'] = selected_images
                combination['rendered_images'] = []
                
                # 为每个变体生成压图
                for variant in variants[:2]:  # 最多为前2个变体压图，避免太多
                    for img in selected_images[:1]:  # 每张图只压一次
                        output_img = self.output_folder / f"{combination['id']}_rendered_{img.stem}.jpg"
                        try:
                            self.renderer.render_text_on_image(
                                str(img), variant, str(output_img),
                                position=text_position,
                                scheme_idx=color_scheme,
                                font_size=font_size
                            )
                            combination['rendered_images'].append(str(output_img.name))
                        except Exception as e:
                            print(f"压图失败 {img}: {e}")
            
            if mode in ["文本+视频", "文本+图片+视频", "全混合模式"] and self.videos:
                combination['videos'] = random.sample(self.videos, min(1, len(self.videos)))
            
            if mode == "多文本组合":
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
                 position: str, scheme: int, font_size: int, output_base: str):
        super().__init__()
        self.mixer = mixer
        self.mode = mode
        self.count = count
        self.variants = variants
        self.position = position
        self.scheme = scheme
        self.font_size = font_size
        self.output_base = Path(output_base)
        self._is_running = True
    
    def run(self):
        try:
            self.status.emit("正在生成素材组合...")
            combinations = self.mixer.generate_combinations(
                self.mode, self.count, self.variants,
                self.position, self.scheme, self.font_size
            )
            
            if not combinations:
                self.error.emit("没有可用的文本素材，请先添加文本文件到文本文件夹")
                return
            
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            output_folder = self.output_base / today
            output_folder.mkdir(parents=True, exist_ok=True)
            
            saved_items = []
            
            for i, combo in enumerate(combinations):
                if not self._is_running:
                    break
                
                self.status.emit(f"正在保存素材 {i+1}/{len(combinations)}: {combo['id']}")
                
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
                    f.write(f"基础文件: {combo['base_text_file']}\n")
                    f.write(f"生成模式: {combo['mode']}\n")
                    f.write(f"生成时间: {combo['timestamp']}\n")
                    f.write(f"渲染参数: 位置={combo['render_params']['position']}, "
                           f"配色={combo['render_params']['color_scheme']}, "
                           f"字号={combo['render_params']['font_size']}\n")
                    f.write("=" * 50 + "\n\n")
                    for j, variant in enumerate(combo['variants'], 1):
                        f.write(f"【变体 {j}】\n{variant}\n\n")
                
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
            
            self.status.emit(f"完成！已生成 {len(saved_items)} 组素材到 {output_folder}")
            self.finished_signal.emit(saved_items)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def stop(self):
        self._is_running = False


# ==================== GUI界面 ====================

class MarketingGeneratorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Marketing素材生成器 v2.0 - 智能压图版")
        self.setMinimumSize(1400, 900)
        
        # 默认路径
        self.base_folder = Path.home() / "MarketingAssets"
        self.text_folder = self.base_folder / "texts"
        self.image_folder = self.base_folder / "images"
        self.video_folder = self.base_folder / "videos"
        self.output_folder = self.base_folder / "output"
        self.temp_folder = self.base_folder / "temp"
        
        for folder in [self.text_folder, self.image_folder, self.video_folder, 
                       self.output_folder, self.temp_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.mixer = None
        self.worker = None
        
        self.init_ui()
        self.refresh_assets()
    
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
    
    def create_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # === 文件夹设置 ===
        folder_group = QGroupBox("📁 素材文件夹设置")
        folder_layout = QGridLayout()
        
        self.path_labels = {}
        paths = [
            ('base', '根目录', str(self.base_folder)),
            ('text', '文本素材', str(self.text_folder)),
            ('image', '图片素材', str(self.image_folder)),
            ('video', '视频素材', str(self.video_folder)),
            ('output', '输出目录', str(self.output_folder))
        ]
        
        for i, (key, label, path) in enumerate(paths):
            folder_layout.addWidget(QLabel(f"{label}:"), i, 0)
            lbl = QLabel(path)
            lbl.setStyleSheet("color: #666; font-size: 11px;")
            lbl.setWordWrap(True)
            self.path_labels[key] = lbl
            folder_layout.addWidget(lbl, i, 1)
        
        btn_change = QPushButton("更改根目录")
        btn_change.clicked.connect(self.change_base_folder)
        folder_layout.addWidget(btn_change, len(paths), 0, 1, 2)
        
        btn_open = QPushButton("打开文件夹")
        btn_open.clicked.connect(self.open_folders)
        folder_layout.addWidget(btn_open, len(paths)+1, 0, 1, 2)
        
        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)
        
        # === 生成设置 ===
        gen_group = QGroupBox("⚙️ 生成设置")
        gen_layout = QVBoxLayout()
        
        # 组合模式
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("组合模式:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(ContentMixer.COMBINATION_MODES)
        self.mode_combo.setCurrentIndex(1)
        mode_layout.addWidget(self.mode_combo)
        gen_layout.addLayout(mode_layout)
        
        # 生成数量
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("生成组数:"))
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 100)
        self.count_spin.setValue(10)
        count_layout.addWidget(self.count_spin)
        gen_layout.addLayout(count_layout)
        
        # 每文本变体数
        var_layout = QHBoxLayout()
        var_layout.addWidget(QLabel("每文本变体数:"))
        self.variant_spin = QSpinBox()
        self.variant_spin.setRange(1, 10)
        self.variant_spin.setValue(3)
        var_layout.addWidget(self.variant_spin)
        gen_layout.addLayout(var_layout)
        
        gen_group.setLayout(gen_layout)
        layout.addWidget(gen_group)
        
        # === 压图渲染设置 ===
        render_group = QGroupBox("🎨 压图渲染设置（文本+图片模式）")
        render_layout = QVBoxLayout()
        
        # 文字位置
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("文字位置:"))
        self.pos_combo = QComboBox()
        self.pos_combo.addItems(['center', 'top', 'bottom', 'top-left', 'top-right', 'bottom-left', 'bottom-right'])
        self.pos_combo.setCurrentIndex(0)
        pos_layout.addWidget(self.pos_combo)
        render_layout.addLayout(pos_layout)
        
        # 配色方案
        scheme_layout = QHBoxLayout()
        scheme_layout.addWidget(QLabel("配色方案:"))
        self.scheme_combo = QComboBox()
        for scheme in ImageTextRenderer.COLOR_SCHEMES:
            self.scheme_combo.addItem(scheme['name'])
        self.scheme_combo.setCurrentIndex(0)
        scheme_layout.addWidget(self.scheme_combo)
        render_layout.addLayout(scheme_layout)
        
        # 字体大小
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("字体大小:"))
        self.font_spin = QSpinBox()
        self.font_spin.setRange(12, 120)
        self.font_spin.setValue(40)
        font_layout.addWidget(self.font_spin)
        render_layout.addLayout(font_layout)
        
        render_group.setLayout(render_layout)
        layout.addWidget(render_group)
        
        # === 素材库状态 ===
        status_group = QGroupBox("📊 素材库状态")
        status_layout = QVBoxLayout()
        
        self.status_texts = QLabel("文本: 0 个")
        self.status_images = QLabel("图片: 0 个")
        self.status_videos = QLabel("视频: 0 个")
        self.status_fonts = QLabel("字体: 检测中...")
        
        for lbl in [self.status_texts, self.status_images, self.status_videos, self.status_fonts]:
            status_layout.addWidget(lbl)
        
        btn_refresh = QPushButton("🔄 刷新素材库")
        btn_refresh.clicked.connect(self.refresh_assets)
        status_layout.addWidget(btn_refresh)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # === 操作按钮 ===
        self.btn_generate = QPushButton("🚀 开始生成素材")
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
        
        self.btn_stop = QPushButton("⏹ 停止生成")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_generation)
        layout.addWidget(self.btn_stop)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("就绪")
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
        
        preview_layout.addWidget(QLabel("📝 最新生成的素材变体预览:"))
        self.preview_list = QListWidget()
        self.preview_list.setMaximumHeight(200)
        self.preview_list.itemClicked.connect(self.show_variant_detail)
        preview_layout.addWidget(self.preview_list)
        
        preview_layout.addWidget(QLabel("📄 选中变体详情:"))
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
        
        tabs.addTab(preview_tab, "👁 实时预览")
        
        # === 压图预览标签页 ===
        image_tab = QWidget()
        image_layout = QVBoxLayout(image_tab)
        
        image_layout.addWidget(QLabel("🖼 生成的压图素材预览:"))
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
        
        tabs.addTab(image_tab, "🖼 压图预览")
        
        # === 历史标签页 ===
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        
        history_layout.addWidget(QLabel("📅 历史生成记录（按日期）:"))
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(['日期', '素材ID', '模式', '变体数', '压图数', '文件夹'])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        history_layout.addWidget(self.history_table)
        
        btn_load_history = QPushButton("🔄 加载历史记录")
        btn_load_history.clicked.connect(self.load_history)
        history_layout.addWidget(btn_load_history)
        
        tabs.addTab(history_tab, "📚 历史记录")
        
        # === API就绪标签页 ===
        api_tab = QWidget()
        api_layout = QVBoxLayout(api_tab)
        
        api_info = QTextEdit()
        api_info.setReadOnly(True)
        api_info.setHtml("""
        <h3>🔌 API 集成指南</h3>
        <p>生成的素材已按标准结构保存，可直接对接各平台API：</p>
        <pre style="background:#f0f0f0;padding:10px;border-radius:4px;">
output/
├── 2026-05-12/
│   ├── MAT_20260512_0001_meta.json          # 元数据
│   ├── MAT_20260512_0001_variants.txt       # 文本变体
│   ├── MAT_20260512_0001_img_xxx.jpg        # 原始图片
│   ├── MAT_20260512_0001_rendered_xxx.jpg   # ⭐压图成品
│   └── MAT_20260512_0001_vid_xxx.mp4        # 关联视频
        </pre>
        <p><b>压图成品命名规则：</b></p>
        <ul>
            <li><code>MAT_xxx_rendered_[原图名].jpg</code> → 已压制文字的成品图</li>
            <li>可直接用于Facebook/Instagram/TikTok发布</li>
        </ul>
        <p><b>建议的API对接流程：</b></p>
        <ol>
            <li>扫描 output/ 下的最新日期文件夹</li>
            <li>读取 *_meta.json 获取素材信息</li>
            <li>上传 <b>rendered_*.jpg</b> 到社交平台</li>
            <li>使用 variants.txt 中的文案作为帖子描述</li>
        </ol>
        </pre>
        """)
        api_layout.addWidget(api_info)
        
        tabs.addTab(api_tab, "🔌 API就绪")
        
        layout.addWidget(tabs)
        return panel
    
    def change_base_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择素材根目录", str(self.base_folder))
        if folder:
            self.base_folder = Path(folder)
            self.text_folder = self.base_folder / "texts"
            self.image_folder = self.base_folder / "images"
            self.video_folder = self.base_folder / "videos"
            self.output_folder = self.base_folder / "output"
            self.temp_folder = self.base_folder / "temp"
            
            for folder in [self.text_folder, self.image_folder, self.video_folder, 
                           self.output_folder, self.temp_folder]:
                folder.mkdir(parents=True, exist_ok=True)
            
            self.path_labels['base'].setText(str(self.base_folder))
            self.path_labels['text'].setText(str(self.text_folder))
            self.path_labels['image'].setText(str(self.image_folder))
            self.path_labels['video'].setText(str(self.video_folder))
            self.path_labels['output'].setText(str(self.output_folder))
            
            self.refresh_assets()
    
    def open_folders(self):
        os.startfile(str(self.base_folder))
    
    def refresh_assets(self):
        self.mixer = ContentMixer(
            str(self.text_folder), 
            str(self.image_folder), 
            str(self.video_folder),
            str(self.temp_folder)
        )
        
        self.status_texts.setText(f"文本: {len(self.mixer.texts)} 个")
        self.status_images.setText(f"图片: {len(self.mixer.images)} 个")
        self.status_videos.setText(f"视频: {len(self.mixer.videos)} 个")
        
        # 检测字体
        if self.mixer.renderer.default_font:
            self.status_fonts.setText(f"字体: {os.path.basename(self.mixer.renderer.default_font)} ✅")
            self.status_fonts.setStyleSheet("color: green;")
        else:
            self.status_fonts.setText("字体: 未找到中文字体 ❌")
            self.status_fonts.setStyleSheet("color: red;")
        
        self.status_texts.setStyleSheet("color: green;" if self.mixer.texts else "color: red;")
        self.status_images.setStyleSheet("color: green;" if self.mixer.images else "color: orange;")
        self.status_videos.setStyleSheet("color: green;" if self.mixer.videos else "color: orange;")
    
    def start_generation(self):
        if not self.mixer or not self.mixer.texts:
            QMessageBox.warning(self, "素材不足", "请先添加文本素材到文本文件夹！\n路径: " + str(self.text_folder))
            return
        
        mode = self.mode_combo.currentText()
        count = self.count_spin.value()
        variants = self.variant_spin.value()
        position = self.pos_combo.currentText()
        scheme = self.scheme_combo.currentIndex()
        font_size = self.font_spin.value()
        
        self.btn_generate.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress_bar.setValue(0)
        
        self.worker = GenerationWorker(
            self.mixer, mode, count, variants,
            position, scheme, font_size,
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
        self.status_label.setText("已停止")
    
    def generation_finished(self, items: List[Dict]):
        self.btn_generate.setEnabled(True)
        self.btn_stop.setEnabled(False)
        
        # 更新文本预览
        self.preview_list.clear()
        for item in items:
            for i in range(item['variants_count']):
                list_item = QListWidgetItem(f"{item['id']} - 变体 {i+1}")
                list_item.setData(Qt.ItemDataRole.UserRole, item)
                self.preview_list.addItem(list_item)
        
        # 更新压图预览
        self.image_list.clear()
        for item in items:
            for media in item.get('media_files', []):
                if 'rendered_' in media:
                    list_item = QListWidgetItem(f"📷 {media}")
                    list_item.setData(Qt.ItemDataRole.UserRole, item)
                    self.image_list.addItem(list_item)
        
        QMessageBox.information(self, "生成完成", 
            f"成功生成 {len(items)} 组素材！\n包含压图成品，可直接用于社媒发布。\n保存位置: {self.output_folder}")
        self.load_history()
    
    def generation_error(self, error_msg: str):
        self.btn_generate.setEnabled(True)
        self.btn_stop.setEnabled(False)
        QMessageBox.critical(self, "生成错误", error_msg)
    
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
            self.image_detail.setText(f"素材ID: {data['id']}\n文件夹: {data['folder']}\n文件列表:\n" + 
                                      "\n".join(data.get('media_files', [])))
    
    def load_history(self):
        self.history_table.setRowCount(0)
        
        if not self.output_folder.exists():
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