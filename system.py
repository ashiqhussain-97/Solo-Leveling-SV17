"""
⚔️ SOLO LEVELING SV17 HYBRID ULTIMATE – VOICE CONTROL EDITION ⚔️
Created by: Ashiq Hussain
All Rights Reserved © 2024

Complete error-free code with full voice control:
✅ Splash/Entry screen
✅ Click sound on all buttons
✅ Strength bar on dashboard (below XP bar)
✅ Quick Stats panel (daily quests, achievements, penalties, goals)
✅ Main Goals with deadline countdown timers
✅ Main Goals EDIT/DELETE/RESET options
✅ Improved Main Goals graphics with visible text
✅ All safe_int() fixes for database loading
✅ pygame welcome message hidden
✅ Deprecation fixes (event.pos → event.position().toPoint)
✅ FULL VOICE CONTROL - Complete tasks, navigate, query stats by voice
"""

import sys
import json
import os
import random
import math
import threading
import subprocess
import sqlite3
import re
from datetime import datetime, timedelta
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtMultimedia import *

# Hide pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

# ============================================
# INSTALL MISSING PACKAGES
# ============================================
def install_package(pkg):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        return True
    except:
        return False

try:
    import pyttsx3
    VOICE_ENABLED = True
except:
    if install_package("pyttsx3"):
        import pyttsx3
        VOICE_ENABLED = True
    else:
        VOICE_ENABLED = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_ENABLED = True
except:
    if install_package("SpeechRecognition"):
        import speech_recognition as sr
        SPEECH_RECOGNITION_ENABLED = True
    else:
        SPEECH_RECOGNITION_ENABLED = False

try:
    import pygame
    PYGAME_ENABLED = True
except:
    if install_package("pygame"):
        import pygame
        PYGAME_ENABLED = True
    else:
        PYGAME_ENABLED = False

# ============================================
# CANON RANKS (Solo Leveling)
# ============================================
RANKS = [
    {'name': 'E', 'xp_required': 0, 'icon': '⬜', 'color': '#C0C0C0', 'title': 'Novice Hunter'},
    {'name': 'D', 'xp_required': 100, 'icon': '🟩', 'color': '#4CAF50', 'title': 'Apprentice Hunter'},
    {'name': 'C', 'xp_required': 300, 'icon': '🟦', 'color': '#2196F3', 'title': 'Skilled Hunter'},
    {'name': 'B', 'xp_required': 600, 'icon': '🟪', 'color': '#9C27B0', 'title': 'Expert Hunter'},
    {'name': 'A', 'xp_required': 1000, 'icon': '🟧', 'color': '#FF9800', 'title': 'Elite Hunter'},
    {'name': 'S', 'xp_required': 1500, 'icon': '🟥', 'color': '#F44336', 'title': 'Master Hunter'},
    {'name': 'SS', 'xp_required': 2500, 'icon': '⭐', 'color': '#FFD700', 'title': 'Grand Master'},
    {'name': 'SSS', 'xp_required': 4000, 'icon': '🌟', 'color': '#FF4081', 'title': 'Legendary Hunter'},
    {'name': 'NATIONAL', 'xp_required': 6000, 'icon': '👑', 'color': '#FF6D00', 'title': 'National Level'},
    {'name': 'MONARCH', 'xp_required': 10000, 'icon': '🔱', 'color': '#D500F9', 'title': 'Shadow Monarch'},
]

STAT_NAMES = {'STR': 'Strength', 'AGI': 'Agility', 'VIT': 'Vitality', 'INT': 'Intelligence', 'PER': 'Perception'}
STAT_ICONS = {'STR': '💪', 'AGI': '⚡', 'VIT': '❤️', 'INT': '🧠', 'PER': '👁️'}
STAT_COLORS = {'STR': '#FF6B6B', 'AGI': '#4ECDC4', 'VIT': '#45B7D1', 'INT': '#96CEB4', 'PER': '#FFEAA7'}

# ============================================
# COLOR THEME
# ============================================
COLORS = {
    'bg': QColor(2, 4, 10),
    'bg_light': QColor(8, 12, 24),
    'panel': QColor(15, 23, 42, 220),
    'glass': QColor(15, 23, 42, 160),
    'blue': QColor(0, 216, 255),
    'gold': QColor(255, 213, 74),
    'purple': QColor(156, 109, 255),
    'red': QColor(255, 77, 109),
    'green': QColor(53, 255, 153),
    'orange': QColor(255, 169, 39),
    'cyan': QColor(68, 232, 255),
    'white': QColor(224, 224, 224),
    'pink': QColor(255, 64, 129),
    'teal': QColor(0, 191, 165),
}

# Helper function to safely convert values to int
def safe_int(value, default=0):
    """Safely convert any value to int, returning default on failure."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

# ============================================
# SOUND MANAGER
# ============================================
class SoundManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.enabled = False
        self.sounds = {}
        if PYGAME_ENABLED:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self._create_sounds()
                self.enabled = True
            except:
                self.enabled = False

    def _create_sounds(self):
        try:
            import wave
            import struct
            sounds_dir = "sounds"
            if not os.path.exists(sounds_dir):
                os.makedirs(sounds_dir)

            def generate_sound(path, freq_start, freq_end, duration, volume=0.3):
                sample_rate = 22050
                samples = int(sample_rate * duration)
                with wave.open(path, 'w') as wav:
                    wav.setnchannels(1)
                    wav.setsampwidth(2)
                    wav.setframerate(sample_rate)
                    for i in range(samples):
                        t = i / sample_rate
                        freq = freq_start + (freq_end - freq_start) * (t / duration)
                        value = int(32767 * volume * math.sin(2 * math.pi * freq * t) *
                                   (1 - t / duration))
                        wav.writeframes(struct.pack('<h', value))

            click_path = os.path.join(sounds_dir, "click.wav")
            if not os.path.exists(click_path):
                generate_sound(click_path, 800, 800, 0.05, 0.3)
            success_path = os.path.join(sounds_dir, "success.wav")
            if not os.path.exists(success_path):
                generate_sound(success_path, 523, 784, 0.3, 0.3)
            levelup_path = os.path.join(sounds_dir, "levelup.wav")
            if not os.path.exists(levelup_path):
                generate_sound(levelup_path, 330, 660, 0.5, 0.3)

            self.sounds['click'] = pygame.mixer.Sound(click_path)
            self.sounds['success'] = pygame.mixer.Sound(success_path)
            self.sounds['levelup'] = pygame.mixer.Sound(levelup_path)
            for s in self.sounds.values():
                s.set_volume(0.3)
        except:
            self.enabled = False
            self.sounds = {}

    def play(self, sound_name):
        if self.enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass

sound_manager = SoundManager()

# ============================================
# DATABASE (SQLite)
# ============================================
class DB:
    def __init__(self):
        self.conn = sqlite3.connect('solo_sv17_final.db')
        self.c = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS player (
            id INTEGER PRIMARY KEY,
            name TEXT, title TEXT, level INTEGER, rank TEXT,
            xp INTEGER, total_xp INTEGER, small_points INTEGER, large_points INTEGER,
            power INTEGER, gold INTEGER, strength INTEGER,
            streak INTEGER, best_streak INTEGER, health_score INTEGER,
            discipline_score INTEGER, completed_quests INTEGER,
            str INTEGER, agi INTEGER, vit INTEGER, intel INTEGER, per INTEGER,
            profile_pic TEXT, last_login TEXT, goals_completed INTEGER,
            all_daily_done INTEGER
        )''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS daily_quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT, name TEXT, desc TEXT, xp INTEGER, attr TEXT,
            target INTEGER, progress INTEGER, completed INTEGER,
            date TEXT, order_num INTEGER
        )''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS main_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, desc TEXT, large_points INTEGER,
            unlocked INTEGER, completed INTEGER, progress INTEGER,
            deadline TEXT, order_num INTEGER, category TEXT
        )''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, desc TEXT, unlocked INTEGER, date_unlocked TEXT,
            category TEXT
        )''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, qty INTEGER
        )''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS daily_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, category TEXT, activity TEXT,
            xp_earned INTEGER, small_points_earned INTEGER
        )''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS weekly_review (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_start TEXT, week_end TEXT, total_xp INTEGER,
            quests_completed INTEGER, goals_progressed INTEGER,
            notes TEXT
        )''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS monthly_review (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT, year INTEGER, total_xp INTEGER,
            quests_completed INTEGER, goals_completed INTEGER,
            notes TEXT
        )''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS yearly_review (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER, total_xp INTEGER,
            quests_completed INTEGER, goals_completed INTEGER,
            rank_achieved TEXT, notes TEXT
        )''')
        self.conn.commit()

    def save_player(self, p):
        self.c.execute('''INSERT OR REPLACE INTO player
            (id, name, title, level, rank, xp, total_xp, small_points, large_points,
             power, gold, strength, streak, best_streak, health_score,
             discipline_score, completed_quests,
             str, agi, vit, intel, per, profile_pic, last_login,
             goals_completed, all_daily_done)
            VALUES (1,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (p['name'], p.get('title','Hunter'), p['level'], p['rank'],
             p['xp'], p['total_xp'], safe_int(p.get('small_points',0)), safe_int(p.get('large_points',0)),
             p['power'], p['gold'], safe_int(p.get('strength',10)),
             p['streak'], p['best_streak'], safe_int(p['health_score']),
             safe_int(p['discipline_score']), p['completed_quests'],
             safe_int(p['stats']['STR']), safe_int(p['stats']['AGI']), safe_int(p['stats']['VIT']),
             safe_int(p['stats']['INT']), safe_int(p['stats']['PER']),
             p.get('profile_pic',''), datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
             safe_int(p.get('goals_completed',0)), 1 if p.get('all_daily_done',False) else 0))
        self.conn.commit()

    def load_player(self):
        self.c.execute('SELECT * FROM player WHERE id=1')
        r = self.c.fetchone()
        if r:
            return {
                'name': r[1] if r[1] else 'Master Aurora', 
                'title': r[2] if r[2] else 'Hunter', 
                'level': safe_int(r[3], 1), 
                'rank': r[4] if r[4] else 'E',
                'xp': safe_int(r[5]), 
                'total_xp': safe_int(r[6]), 
                'small_points': safe_int(r[7]), 
                'large_points': safe_int(r[8]),
                'power': safe_int(r[9], 100), 
                'gold': safe_int(r[10], 50), 
                'strength': safe_int(r[11], 10),
                'streak': safe_int(r[12]), 
                'best_streak': safe_int(r[13]),
                'health_score': safe_int(r[14], 50), 
                'discipline_score': safe_int(r[15], 50),
                'completed_quests': safe_int(r[16]),
                'stats': {
                    'STR': safe_int(r[17], 10), 
                    'AGI': safe_int(r[18], 10), 
                    'VIT': safe_int(r[19], 10),
                    'INT': safe_int(r[20], 10), 
                    'PER': safe_int(r[21], 10)
                },
                'profile_pic': r[22] if r[22] else '', 
                'last_login': r[23] if r[23] else '',
                'goals_completed': safe_int(r[24]) if len(r)>24 else 0,
                'all_daily_done': bool(r[25]) if len(r)>25 else False
            }
        return None

    def save_daily_quests(self, qs):
        self.c.execute('DELETE FROM daily_quests')
        for i, q in enumerate(qs):
            self.c.execute('''INSERT INTO daily_quests
                (category, name, desc, xp, attr, target, progress, completed, date, order_num)
                VALUES (?,?,?,?,?,?,?,?,?,?)''',
                (q.get('category','General'), q['name'], q['desc'], q['xp'],
                 q.get('attr','STR'), q.get('target',1), q.get('progress',0),
                 1 if q.get('completed',False) else 0,
                 q.get('date', datetime.now().strftime('%Y-%m-%d')), i))
        self.conn.commit()

    def load_daily_quests(self):
        self.c.execute('SELECT * FROM daily_quests ORDER BY order_num')
        rows = self.c.fetchall()
        return [{'category': r[1], 'name': r[2], 'desc': r[3], 'xp': r[4],
                 'attr': r[5], 'target': r[6], 'progress': r[7],
                 'completed': bool(r[8]), 'date': r[9]} for r in rows]

    def save_main_goals(self, gs):
        self.c.execute('DELETE FROM main_goals')
        for i, g in enumerate(gs):
            self.c.execute('''INSERT INTO main_goals
                (name, desc, large_points, unlocked, completed, progress, deadline, order_num, category)
                VALUES (?,?,?,?,?,?,?,?,?)''',
                (g['name'], g['desc'], g.get('large_points',3),
                 1 if g.get('unlocked',False) else 0,
                 1 if g.get('completed',False) else 0,
                 g.get('progress',0), g.get('deadline',''), i, g.get('category','General')))
        self.conn.commit()

    def load_main_goals(self):
        self.c.execute('SELECT * FROM main_goals ORDER BY order_num')
        rows = self.c.fetchall()
        return [{'name': r[1], 'desc': r[2], 'large_points': r[3],
                 'unlocked': bool(r[4]), 'completed': bool(r[5]),
                 'progress': r[6], 'deadline': r[7], 'category': r[8]} for r in rows]

    def save_achievements(self, ach):
        self.c.execute('DELETE FROM achievements')
        for a in ach:
            self.c.execute('''INSERT INTO achievements (name, desc, unlocked, date_unlocked, category)
                VALUES (?,?,?,?,?)''',
                (a['name'], a['desc'], 1 if a['unlocked'] else 0,
                 a.get('date_unlocked',''), a.get('category','General')))
        self.conn.commit()

    def load_achievements(self):
        self.c.execute('SELECT name, desc, unlocked, date_unlocked, category FROM achievements')
        rows = self.c.fetchall()
        return [{'name': r[0], 'desc': r[1], 'unlocked': bool(r[2]),
                 'date_unlocked': r[3], 'category': r[4]} for r in rows]

    def save_inventory(self, inv):
        self.c.execute('DELETE FROM inventory')
        for item in inv:
            self.c.execute('INSERT INTO inventory (name, qty) VALUES (?,?)',
                           (item['name'], item['qty']))
        self.conn.commit()

    def load_inventory(self):
        self.c.execute('SELECT name, qty FROM inventory')
        return [{'name': r[0], 'qty': r[1]} for r in self.c.fetchall()]

    def add_daily_log(self, category, activity, xp, sp):
        self.c.execute('''INSERT INTO daily_log (date, category, activity, xp_earned, small_points_earned)
            VALUES (?,?,?,?,?)''',
            (datetime.now().strftime('%Y-%m-%d'), category, activity, xp, sp))
        self.conn.commit()

    def get_daily_log(self, date=None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        self.c.execute('SELECT * FROM daily_log WHERE date=?', (date,))
        return self.c.fetchall()

    def get_weekly_log(self, week_start):
        week_end = (datetime.strptime(week_start, '%Y-%m-%d') + timedelta(days=6)).strftime('%Y-%m-%d')
        self.c.execute('SELECT * FROM daily_log WHERE date >= ? AND date <= ?',
                       (week_start, week_end))
        return self.c.fetchall()

    def close(self):
        self.conn.close()

# ============================================
# ACHIEVEMENT DEFINITIONS (24 total)
# ============================================
ACHIEVEMENTS = [
    {'name': 'First Steps', 'desc': 'Complete your first quest', 'category': 'Quest'},
    {'name': 'D-Rank Hunter', 'desc': 'Reach D Rank', 'category': 'Rank'},
    {'name': 'C-Rank Hunter', 'desc': 'Reach C Rank', 'category': 'Rank'},
    {'name': 'B-Rank Hunter', 'desc': 'Reach B Rank', 'category': 'Rank'},
    {'name': 'A-Rank Hunter', 'desc': 'Reach A Rank', 'category': 'Rank'},
    {'name': 'S-Rank Hunter', 'desc': 'Reach S Rank', 'category': 'Rank'},
    {'name': 'National Level', 'desc': 'Reach National Level', 'category': 'Rank'},
    {'name': 'Shadow Monarch', 'desc': 'Reach Monarch Level', 'category': 'Rank'},
    {'name': 'Quest Master', 'desc': 'Complete 10 quests', 'category': 'Quest'},
    {'name': 'Quest Legend', 'desc': 'Complete 50 quests', 'category': 'Quest'},
    {'name': 'Gold Collector', 'desc': 'Accumulate 500 gold', 'category': 'Wealth'},
    {'name': 'Gold Tycoon', 'desc': 'Accumulate 2000 gold', 'category': 'Wealth'},
    {'name': 'Streak King', 'desc': '7-day streak', 'category': 'Discipline'},
    {'name': 'Streak God', 'desc': '30-day streak', 'category': 'Discipline'},
    {'name': 'Strong Body', 'desc': 'Reach 50 STR', 'category': 'Stats'},
    {'name': 'Peak Strength', 'desc': 'Reach 100 STR', 'category': 'Stats'},
    {'name': 'Sharp Mind', 'desc': 'Reach 50 INT', 'category': 'Stats'},
    {'name': 'Genius Level', 'desc': 'Reach 100 INT', 'category': 'Stats'},
    {'name': 'Iron Will', 'desc': 'Reach 100 Discipline', 'category': 'Discipline'},
    {'name': 'Level 10', 'desc': 'Reach Level 10', 'category': 'Level'},
    {'name': 'Level 25', 'desc': 'Reach Level 25', 'category': 'Level'},
    {'name': 'Level 50', 'desc': 'Reach Level 50', 'category': 'Level'},
    {'name': 'Goal Achiever', 'desc': 'Complete 3 main goals', 'category': 'Goal'},
    {'name': 'Perfectionist', 'desc': 'Complete all daily quests in one day', 'category': 'Quest'},
]

# ============================================
# UI COMPONENTS (Particles, Background, GlassPanel, NeonButton, AnimatedProgressBar)
# ============================================
class Particle:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-1.5, -0.1)
        self.size = random.uniform(1, 3)
        self.life = random.uniform(50, 150)
        self.max_life = self.life
        self.color = random.choice([COLORS['blue'], COLORS['cyan'], COLORS['purple'], COLORS['gold'], COLORS['pink']])
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)
        self.x += self.vx + random.uniform(-0.05, 0.05)
        self.y += self.vy
        self.vy += 0.01
        self.life -= 1
        if self.x < 0:
            self.x = self.w
        if self.x > self.w:
            self.x = 0
        if self.y < -50:
            self.y = self.h + 20
            self.x = random.randint(0, self.w)
            self.life = self.max_life
        return self.life > 0

    def get_opacity(self):
        return (self.life / self.max_life) * 255

    def get_size(self):
        return self.size * (0.5 + 0.5 * (self.life / self.max_life))

class AnimatedBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        self._timer = None
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        for _ in range(80):
            self.particles.append(Particle(random.randint(0, 1920), random.randint(0, 1080), 1920, 1080))

    def showEvent(self, e):
        super().showEvent(e)
        if not self._timer:
            self._timer = QTimer(self)
            self._timer.timeout.connect(self.update)
            self._timer.start(16)

    def hideEvent(self, e):
        super().hideEvent(e)
        if self._timer:
            self._timer.stop()
            self._timer = None

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        g = QLinearGradient(0, 0, 0, self.height())
        g.setColorAt(0, COLORS['bg'])
        g.setColorAt(0.5, COLORS['bg_light'])
        g.setColorAt(1, COLORS['bg'])
        painter.fillRect(self.rect(), g)

        for p in self.particles[:]:
            if not p.update():
                self.particles.remove(p)
                self.particles.append(Particle(random.randint(0, self.width()),
                                               self.height() + 20, self.width(), self.height()))

        for p in self.particles:
            if len(p.trail) > 1:
                for i in range(1, len(p.trail)):
                    alpha = int(255 * (i / len(p.trail)) * 0.15)
                    c = QColor(p.color)
                    c.setAlpha(alpha)
                    painter.setPen(QPen(c, 1))
                    painter.drawLine(int(p.trail[i-1][0]), int(p.trail[i-1][1]),
                                     int(p.trail[i][0]), int(p.trail[i][1]))
            c = QColor(p.color)
            c.setAlpha(int(p.get_opacity()))
            painter.setBrush(QBrush(c))
            painter.setPen(Qt.NoPen)
            s = p.get_size()
            painter.drawEllipse(QPointF(p.x, p.y), s, s)

class GlassPanel(QWidget):
    def __init__(self, parent=None, color=None):
        super().__init__(parent)
        self.custom_color = color or COLORS['glass']
        self.animation = 0
        self._timer = None
        self.setAttribute(Qt.WA_TranslucentBackground)

    def showEvent(self, e):
        super().showEvent(e)
        if not self._timer:
            self._timer = QTimer(self)
            self._timer.timeout.connect(self.update)
            self._timer.start(100)

    def hideEvent(self, e):
        super().hideEvent(e)
        if self._timer:
            self._timer.stop()
            self._timer = None

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        glass = QColor(self.custom_color)
        glass.setAlpha(180)
        painter.setBrush(QBrush(glass))
        painter.setPen(QPen(COLORS['blue'], 1))
        painter.drawRoundedRect(self.rect(), 15, 15)

        self.animation += 0.02
        glow = QColor(COLORS['blue'])
        glow.setAlpha(int(30 + 20 * math.sin(self.animation)))
        painter.setPen(QPen(glow, 2))
        painter.drawRoundedRect(self.rect().adjusted(-2, -2, 2, 2), 16, 16)

        h = QLinearGradient(0, 0, 0, self.height() / 3)
        h.setColorAt(0, QColor(255, 255, 255, 20))
        h.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(h))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height() / 3, 15, 15)

class NeonButton(QPushButton):
    def __init__(self, text, color=None, parent=None):
        super().__init__(text, parent)
        self.custom_color = color or COLORS['blue']
        self.hover_anim = 0
        self._timer = None
        self.setCursor(Qt.PointingHandCursor)
        self.setFlat(True)
        self.setMinimumHeight(35)
        self.pressed.connect(lambda: sound_manager.play('click'))

    def showEvent(self, e):
        super().showEvent(e)
        if not self._timer:
            self._timer = QTimer(self)
            self._timer.timeout.connect(self.update_anim)
            self._timer.start(50)

    def hideEvent(self, e):
        super().hideEvent(e)
        if self._timer:
            self._timer.stop()
            self._timer = None

    def update_anim(self):
        if self.underMouse():
            self.hover_anim = min(1.0, self.hover_anim + 0.1)
        else:
            self.hover_anim = max(0.0, self.hover_anim - 0.1)
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        base = QColor(self.custom_color)
        base.setAlpha(int(60 + 120 * self.hover_anim))

        g = QLinearGradient(0, 0, self.width(), self.height())
        g.setColorAt(0, base)
        g.setColorAt(1, QColor(self.custom_color.red()//2, self.custom_color.green()//2,
                               self.custom_color.blue()//2, int(60 + 120 * self.hover_anim)))
        painter.setBrush(QBrush(g))

        gw = 1 + 3 * self.hover_anim
        painter.setPen(QPen(self.custom_color, gw))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 10, 10)

        painter.setPen(QPen(QColor(255, 255, 255, int(200 + 55 * self.hover_anim))))
        font = QFont("Segoe UI", 10, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())

class AnimatedProgressBar(QProgressBar):
    def __init__(self, parent=None, color=None):
        super().__init__(parent)
        self.custom_color = color or COLORS['blue']
        self.glow_anim = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update_glow)
        self._timer.start(50)

    def update_glow(self):
        self.glow_anim += 0.05
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QColor(0, 0, 0, 100))
        painter.setPen(QPen(self.custom_color, 1))
        painter.drawRoundedRect(self.rect(), 6, 6)

        if self.value() > 0:
            w = int((self.width() - 2) * self.value() / self.maximum())
            if w > 4:
                g = QLinearGradient(0, 0, w, 0)
                g.setColorAt(0, QColor(self.custom_color))
                g.setColorAt(0.5, QColor(self.custom_color).lighter(180))
                g.setColorAt(1, QColor(self.custom_color))
                painter.setBrush(QBrush(g))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(1, 1, w, self.height() - 2, 5, 5)

                glow = QColor(self.custom_color)
                glow.setAlpha(int(30 + 20 * math.sin(self.glow_anim)))
                painter.setPen(QPen(glow, 3))
                painter.drawLine(3, self.height() // 2, w - 2, self.height() // 2)

# ============================================
# VOICE COMMAND PROCESSOR (ENHANCED)
# ============================================
class VoiceCommandProcessor(QObject):
    command_triggered = Signal(str, dict)

    def __init__(self):
        super().__init__()
        self.recognizer = None
        self.microphone = None
        self.is_listening = False
        self.voice_engine = None
        self.listening_thread = None
        self.stop_event = threading.Event()
        self.last_command = ""
        self.command_history = []

        if SPEECH_RECOGNITION_ENABLED:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Increase recognition sensitivity
                self.recognizer.energy_threshold = 300
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 0.8
            except:
                pass

        if VOICE_ENABLED:
            try:
                self.voice_engine = pyttsx3.init()
                self.voice_engine.setProperty('rate', 160)
                self.voice_engine.setProperty('volume', 0.7)
                voices = self.voice_engine.getProperty('voices')
                if voices:
                    for voice in voices:
                        if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                            self.voice_engine.setProperty('voice', voice.id)
                            break
            except:
                pass

    def speak(self, text):
        if self.voice_engine and VOICE_ENABLED:
            try:
                self.voice_engine.say(text)
                self.voice_engine.runAndWait()
            except:
                pass

    def start_listening(self):
        if not SPEECH_RECOGNITION_ENABLED or self.is_listening:
            return
        self.is_listening = True
        self.stop_event.clear()
        self.speak("I'm listening")
        self.listening_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listening_thread.start()

    def stop_listening(self):
        self.is_listening = False
        self.stop_event.set()
        if self.listening_thread:
            self.listening_thread.join(timeout=1)

    def _listen_loop(self):
        while self.is_listening and not self.stop_event.is_set():
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    try:
                        audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
                    except sr.WaitTimeoutError:
                        continue
                try:
                    text = self.recognizer.recognize_google(audio, language='en-IN')
                    if text and text.strip() and text.lower() != self.last_command:
                        self.last_command = text.lower()
                        self.command_history.append(text.lower())
                        if len(self.command_history) > 10:
                            self.command_history.pop(0)
                        self.process_command(text.lower())
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    pass
            except:
                pass

    def process_command(self, command):
        command = command.lower().strip()
        print(f"Voice command: {command}")  # Debug output
        
        # Navigation commands
        nav_map = {
            'dashboard': ['dashboard', 'home', 'main', 'overview', 'main screen'],
            'daily_quests': ['daily quests', 'daily quest', 'daily', 'quests', 'quest', 'today'],
            'main_goals': ['main goals', 'main goal', 'goals', 'goal', 'targets', 'target'],
            'analytics': ['analytics', 'stats', 'statistics', 'analysis', 'attributes'],
            'mental': ['mental', 'mind', 'brain', 'intelligence'],
            'physical': ['physical', 'fitness', 'body', 'exercise', 'workout'],
            'spiritual': ['spiritual', 'meditation', 'spirit', 'soul'],
            'achievements': ['achievements', 'badges', 'badge', 'trophy', 'trophies', 'awards'],
            'shop': ['shop', 'store', 'buy', 'purchase', 'market'],
            'reviews': ['reviews', 'review', 'weekly', 'monthly', 'yearly', 'report'],
            'profile': ['profile', 'my profile', 'character', 'avatar'],
            'settings': ['settings', 'setting', 'config', 'configuration', 'options'],
        }
        
        for page, keywords in nav_map.items():
            if any(k in command for k in keywords):
                self.command_triggered.emit('navigate', {'page': page})
                self.speak(f"Opening {page}")
                return
        
        # Back command
        if any(w in command for w in ['go back', 'back', 'previous', 'return']):
            self.command_triggered.emit('back', {})
            self.speak("Going back")
            return
        
        # Status/Information queries
        if any(w in command for w in ['status', 'how am i', 'my stats', 'my info', 'tell me about']):
            self.command_triggered.emit('status_query', {'command': command})
            return
        
        # Complete quest by name
        if any(w in command for w in ['complete', 'done', 'finish', 'do']):
            self.command_triggered.emit('complete_quest_voice', {'command': command})
            return
        
        # Fail quest by name
        if any(w in command for w in ['fail', 'skip', 'missed']):
            self.command_triggered.emit('fail_quest_voice', {'command': command})
            return
        
        # Goal progress
        if any(w in command for w in ['progress goal', 'advance goal', 'update goal']):
            self.command_triggered.emit('progress_goal', {'command': command})
            return
        
        # Add quest/goal
        if 'add quest' in command or 'add daily' in command:
            self.command_triggered.emit('add_quest', {})
            return
        
        if 'add goal' in command or 'add target' in command:
            self.command_triggered.emit('add_goal', {})
            return
        
        # Query specific stats
        if any(w in command for w in ['experience', 'xp', 'level', 'rank']):
            self.command_triggered.emit('status_query', {'command': 'experience'})
            return
        
        if any(w in command for w in ['strength', 'power', 'strong']):
            self.command_triggered.emit('status_query', {'command': 'strength'})
            return
        
        if any(w in command for w in ['gold', 'money', 'coin', 'currency']):
            self.command_triggered.emit('status_query', {'command': 'gold'})
            return
        
        if any(w in command for w in ['streak', 'days', 'consecutive']):
            self.command_triggered.emit('status_query', {'command': 'streak'})
            return
        
        if any(w in command for w in ['goal progress', 'goals done', 'goals completed']):
            self.command_triggered.emit('status_query', {'command': 'goals'})
            return
        
        if any(w in command for w in ['achievement', 'unlocked']):
            self.command_triggered.emit('status_query', {'command': 'achievements'})
            return
        
        if any(w in command for w in ['discipline', 'discipline score']):
            self.command_triggered.emit('status_query', {'command': 'discipline'})
            return
        
        if any(w in command for w in ['health', 'vitality', 'hp']):
            self.command_triggered.emit('status_query', {'command': 'health'})
            return
        
        # Toggle voice
        if any(w in command for w in ['stop listening', 'be quiet', 'silence', 'shut up']):
            self.command_triggered.emit('toggle_voice', {})
            return
        
        # Help
        if any(w in command for w in ['help', 'what can i say', 'commands', 'what can you do']):
            self.speak("You can say: open dashboard, open quests, complete morning workout, status, how much gold, what is my strength, go back, and more. Say stop listening to turn off voice.")
            return
        
        # If nothing matches
        self.speak("Command not recognized. Say help to know available commands.")

# ============================================
# SPLASH SCREEN
# ============================================
class SplashScreen(QWidget):
    def __init__(self, on_enter_callback):
        super().__init__()
        self.on_enter = on_enter_callback
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        self.setStyleSheet("background:transparent;")
        self.animation = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)
        self.show()

    def update_animation(self):
        self.animation += 0.02
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        g = QLinearGradient(0, 0, 0, h)
        g.setColorAt(0, QColor(5, 10, 25))
        g.setColorAt(0.5, QColor(10, 18, 40))
        g.setColorAt(1, QColor(2, 4, 10))
        painter.fillRect(self.rect(), g)
        for i in range(5):
            t = self.animation + i * 1.2
            x = w/2 + math.sin(t) * 250
            y = h/2 + math.cos(t*0.7) * 180
            r = 40 + 30 * math.sin(t*1.3)
            alpha = int(20 + 15 * math.sin(t*2))
            colors = [QColor(0, 216, 255, alpha), QColor(255, 213, 74, alpha),
                     QColor(156, 109, 255, alpha), QColor(53, 255, 153, alpha),
                     QColor(255, 64, 129, alpha)]
            painter.setBrush(colors[i])
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(x, y), r, r)

        font_title = QFont("Orbitron", 52, QFont.Bold)
        painter.setFont(font_title)
        painter.setPen(QColor(0, 216, 255))
        painter.drawText(QRect(0, h//3-20, w, 80), Qt.AlignCenter, "⚔️ SOLO LEVELING")

        font_sub = QFont("Orbitron", 22)
        painter.setFont(font_sub)
        painter.setPen(QColor(255, 213, 74))
        painter.drawText(QRect(0, h//3+80, w, 50), Qt.AlignCenter, "SV17 HYBRID ULTIMATE")

        font_creator = QFont("Segoe UI", 13)
        painter.setFont(font_creator)
        painter.setPen(QColor(156, 109, 255))
        painter.drawText(QRect(0, h//3+140, w, 40), Qt.AlignCenter, "Created by Ashiq Hussain")

        font_voice = QFont("Segoe UI", 11)
        painter.setFont(font_voice)
        painter.setPen(QColor(68, 232, 255))
        painter.drawText(QRect(0, h//3+190, w, 40), Qt.AlignCenter, "🎤 Voice Control Edition")

        btn_rect = QRect(w//2-120, h//2+80, 240, 65)
        pulse = 0.8 + 0.2 * math.sin(self.animation * 3)
        painter.setBrush(QColor(0, 216, 255, int(100 * pulse)))
        painter.setPen(QPen(QColor(0, 216, 255), 2))
        painter.drawRoundedRect(btn_rect, 20, 20)
        font_btn = QFont("Segoe UI", 20, QFont.Bold)
        painter.setFont(font_btn)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(btn_rect, Qt.AlignCenter, "⚔️  ENTER  ⚔️")

    def mousePressEvent(self, event):
        w, h = self.width(), self.height()
        btn_rect = QRect(w//2-120, h//2+80, 240, 65)
        if btn_rect.contains(event.position().toPoint()):
            sound_manager.play('click')
            self.timer.stop()
            self.hide()
            self.on_enter()
            self.close()

# ============================================
# MAIN APPLICATION
# ============================================
class SoloLevelingSV17(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚔️ SOLO LEVELING SV17 HYBRID ULTIMATE - VOICE CONTROL")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(100, 50, 1200, 700)   # چھوٹی ونڈو

        self.db = DB()
        self.data = self.load_data()
        self.drag_pos = None
        self.voice_processor = None
        self.is_voice_active = False
        self.current_page = None
        self.page_history = []

        self.initialize_data()

        if SPEECH_RECOGNITION_ENABLED:
            self.voice_processor = VoiceCommandProcessor()
            self.voice_processor.command_triggered.connect(self.handle_voice_command)

        self.central = QWidget()
        self.central.setStyleSheet("background:transparent;")
        self.setCentralWidget(self.central)

        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(0, 40, 0, 0)
        self.main_layout.setSpacing(0)

        self.create_title_bar()
        self.background = AnimatedBackground(self.central)
        self.background.setGeometry(0, 40, 1500, 860)
        self.background.lower()

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:transparent;")
        self.stack.setContentsMargins(12, 12, 12, 12)
        self.main_layout.addWidget(self.stack)

        self.create_all_pages()
        self.show_page('dashboard')

        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save_data)
        self.save_timer.start(30000)

        if self.voice_processor:
            QTimer.singleShot(2500, self.start_voice)

    # ═══════════════════════ DATA METHODS ═══════════════════════
    def load_data(self):
        pd = self.db.load_player()
        if pd:
            return {
                'player': pd,
                'daily_quests': self.db.load_daily_quests(),
                'main_goals': self.db.load_main_goals(),
                'achievements': self.db.load_achievements(),
                'inventory': self.db.load_inventory(),
                'reviews': {'weekly': [], 'monthly': [], 'yearly': []}
            }
        return self.create_default_data()

    def create_default_data(self):
        return {
            'player': {
                'name': 'Master Aurora', 'title': 'Novice Hunter', 'level': 1,
                'rank': 'E', 'xp': 0, 'total_xp': 0, 'small_points': 0,
                'large_points': 0, 'power': 100, 'gold': 50, 'strength': 10,
                'streak': 0, 'best_streak': 0, 'health_score': 50,
                'discipline_score': 50, 'completed_quests': 0,
                'stats': {'STR': 10, 'AGI': 10, 'VIT': 10, 'INT': 10, 'PER': 10},
                'profile_pic': '', 'last_login': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'goals_completed': 0, 'all_daily_done': False
            },
            'daily_quests': [],
            'main_goals': [
                {'name': '🇩🇪 German Language', 'desc': 'Achieve B1 level fluency',
                 'large_points': 3, 'unlocked': True, 'completed': False,
                 'progress': 0, 'deadline': '2026-12-31', 'category': 'Language'},
                {'name': '🇬🇧 English Language', 'desc': 'Achieve C2 level mastery',
                 'large_points': 3, 'unlocked': False, 'completed': False,
                 'progress': 0, 'deadline': '2027-06-30', 'category': 'Language'},
                {'name': '💻 Python Programming', 'desc': 'Become Python expert',
                 'large_points': 3, 'unlocked': False, 'completed': False,
                 'progress': 0, 'deadline': '2026-12-31', 'category': 'Technology'},
                {'name': '🎓 CS Mastering', 'desc': 'Master Computer Science fundamentals',
                 'large_points': 3, 'unlocked': False, 'completed': False,
                 'progress': 0, 'deadline': '2027-12-31', 'category': 'Education'},
                {'name': '👑 Shadow Monarch', 'desc': 'Reach Monarch rank and complete all goals',
                 'large_points': 3, 'unlocked': False, 'completed': False,
                 'progress': 0, 'deadline': '2028-12-31', 'category': 'Ultimate'},
            ],
            'achievements': [], 'inventory': [],
            'reviews': {'weekly': [], 'monthly': [], 'yearly': []}
        }

    def save_data(self):
        try:
            self.db.save_player(self.data['player'])
            self.db.save_daily_quests(self.data['daily_quests'])
            self.db.save_main_goals(self.data['main_goals'])
            self.db.save_achievements(self.data['achievements'])
            self.db.save_inventory(self.data['inventory'])
        except: pass
        try:
            with open('solo_sv17_final.json', 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except: pass

    def initialize_data(self):
        today = datetime.now().strftime('%Y-%m-%d')
        if not self.data['daily_quests'] or (self.data['daily_quests'][0].get('date') != today):
            quests = [
                ('🌅 Morning Routine', 'Wake Up Early', 'Before 6 AM', 5, 'VIT'),
                ('🌅 Morning Routine', 'Morning Exercise', '20 min workout', 5, 'STR'),
                ('🌅 Morning Routine', 'Healthy Breakfast', 'Nutritious meal', 5, 'VIT'),
                ('📚 Study', 'German Practice', '30 min language', 5, 'INT'),
                ('📚 Study', 'Python Coding', '1 hour programming', 5, 'INT'),
                ('📚 Study', 'Book Reading', '20 pages', 5, 'PER'),
                ('🌙 Night Routine', 'Katana Practice', '30 min with katana', 5, 'AGI'),
                ('🌙 Night Routine', 'Shadow Training', 'Imagination & shadow boxing', 5, 'STR'),
                ('🌙 Night Routine', 'Meditation', '15 min meditation', 5, 'PER'),
                ('🌙 Night Routine', 'SPA Relaxation', 'Self-care and relaxation', 5, 'VIT'),
            ]
            self.data['daily_quests'] = []
            for cat, name, desc, xp, attr in quests:
                self.data['daily_quests'].append({
                    'category': cat, 'name': name, 'desc': desc,
                    'xp': xp, 'attr': attr, 'target': 1,
                    'progress': 0, 'completed': False, 'date': today
                })
        self.check_penalty()
        self.save_data()

    def check_penalty(self):
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        logs = self.db.get_daily_log(yesterday)
        if not logs: return
        total_quests = len([q for q in self.data['daily_quests'] if q['date'] == yesterday])
        completed = sum(1 for q in self.data['daily_quests'] if q['date'] == yesterday and q['completed'])
        if total_quests > 0 and completed < total_quests:
            self.data['daily_quests'].append({
                'category': '⚠️ Penalty', 'name': '5min Extra Training',
                'desc': 'Penalty for incomplete yesterday\'s quests', 'xp': 0,
                'attr': 'STR', 'target': 1, 'progress': 0, 'completed': False,
                'date': datetime.now().strftime('%Y-%m-%d')
            })

    def get_rank(self, xp):
        for i, r in enumerate(RANKS):
            if xp < r['xp_required']:
                return RANKS[i-1] if i > 0 else r
        return RANKS[-1]

    def get_next_rank(self, xp):
        for r in RANKS:
            if xp < r['xp_required']:
                return r
        return None

    def check_achievements(self):
        p = self.data['player']
        achievements = self.data['achievements']
        unlocked_any = False
        for ach in ACHIEVEMENTS:
            if any(a['name'] == ach['name'] and a['unlocked'] for a in achievements): continue
            unlocked = False
            if ach['name'] == 'First Steps' and p['completed_quests'] >= 1: unlocked = True
            elif ach['name'] == 'D-Rank Hunter' and p['xp'] >= 100: unlocked = True
            elif ach['name'] == 'C-Rank Hunter' and p['xp'] >= 300: unlocked = True
            elif ach['name'] == 'B-Rank Hunter' and p['xp'] >= 600: unlocked = True
            elif ach['name'] == 'A-Rank Hunter' and p['xp'] >= 1000: unlocked = True
            elif ach['name'] == 'S-Rank Hunter' and p['xp'] >= 1500: unlocked = True
            elif ach['name'] == 'National Level' and p['xp'] >= 6000: unlocked = True
            elif ach['name'] == 'Shadow Monarch' and p['xp'] >= 10000: unlocked = True
            elif ach['name'] == 'Quest Master' and p['completed_quests'] >= 10: unlocked = True
            elif ach['name'] == 'Quest Legend' and p['completed_quests'] >= 50: unlocked = True
            elif ach['name'] == 'Gold Collector' and p['gold'] >= 500: unlocked = True
            elif ach['name'] == 'Gold Tycoon' and p['gold'] >= 2000: unlocked = True
            elif ach['name'] == 'Streak King' and p['best_streak'] >= 7: unlocked = True
            elif ach['name'] == 'Streak God' and p['best_streak'] >= 30: unlocked = True
            elif ach['name'] == 'Strong Body' and safe_int(p['stats']['STR']) >= 50: unlocked = True
            elif ach['name'] == 'Peak Strength' and safe_int(p['stats']['STR']) >= 100: unlocked = True
            elif ach['name'] == 'Sharp Mind' and safe_int(p['stats']['INT']) >= 50: unlocked = True
            elif ach['name'] == 'Genius Level' and safe_int(p['stats']['INT']) >= 100: unlocked = True
            elif ach['name'] == 'Iron Will' and p['discipline_score'] >= 100: unlocked = True
            elif ach['name'] == 'Level 10' and p['level'] >= 10: unlocked = True
            elif ach['name'] == 'Level 25' and p['level'] >= 25: unlocked = True
            elif ach['name'] == 'Level 50' and p['level'] >= 50: unlocked = True
            elif ach['name'] == 'Goal Achiever' and safe_int(p.get('goals_completed', 0)) >= 3: unlocked = True
            elif ach['name'] == 'Perfectionist' and p.get('all_daily_done', False): unlocked = True
            if unlocked:
                achievements.append({
                    'name': ach['name'], 'desc': ach['desc'],
                    'unlocked': True, 'date_unlocked': datetime.now().strftime('%Y-%m-%d'),
                    'category': ach['category']
                })
                unlocked_any = True
                sound_manager.play('success')
                self.speak(f"Achievement unlocked: {ach['name']}")
        if unlocked_any: self.save_data()

    # ═══════════════════════ GAME ACTIONS ═══════════════════════
    def complete_quest(self, idx):
        qs = self.data['daily_quests']
        if idx >= len(qs) or qs[idx]['completed']: return
        q = qs[idx]
        p = self.data['player']
        xp_gain = q['xp']
        streak_bonus = min(p['streak'], 10)
        total_xp = xp_gain + streak_bonus
        small_points_gain = 5
        p['small_points'] = safe_int(p.get('small_points', 0)) + small_points_gain
        if p['small_points'] >= 100:
            p['large_points'] = safe_int(p.get('large_points', 0)) + 1
            p['small_points'] -= 100
            sound_manager.play('levelup')
        p['xp'] = safe_int(p['xp']) + total_xp
        p['total_xp'] = safe_int(p['total_xp']) + total_xp
        p['power'] = 100 + safe_int(p['xp']) + safe_int(p.get('strength', 10)) * 2
        p['completed_quests'] = safe_int(p['completed_quests']) + 1
        p['strength'] = safe_int(p.get('strength', 10)) + 1
        p['gold'] = safe_int(p['gold']) + random.randint(5, 15)
        if q['attr'] in p['stats']:
            p['stats'][q['attr']] = min(100, safe_int(p['stats'][q['attr']]) + 1)
        p['discipline_score'] = min(100, safe_int(p['discipline_score']) + 1)
        p['streak'] = safe_int(p['streak']) + 1
        if p['streak'] > safe_int(p['best_streak']): p['best_streak'] = p['streak']
        q['completed'] = True
        q['progress'] = q.get('target', 1)
        all_done = all(q2.get('completed', False) for q2 in self.data['daily_quests'] if q2.get('category') != '⚠️ Penalty')
        if all_done:
            p['all_daily_done'] = True
            p['xp'] = safe_int(p['xp']) + 25
            p['total_xp'] = safe_int(p['total_xp']) + 25
        if safe_int(p.get('large_points', 0)) >= 5:
            p['level'] = safe_int(p['level']) + 1
            p['large_points'] = safe_int(p.get('large_points', 0)) - 5
            p['xp'] = safe_int(p['xp']) + 50
            sound_manager.play('levelup')
            self.speak(f"Level Up! Level {p['level']}")
        new_rank = self.get_rank(safe_int(p['xp']))
        if new_rank['name'] != p['rank']:
            p['rank'] = new_rank['name']
            p['title'] = new_rank['title']
            sound_manager.play('levelup')
            self.speak(f"Rank Up! {new_rank['name']} - {new_rank['title']}")
        self.db.add_daily_log(q['category'], q['name'], total_xp, small_points_gain)
        self.check_achievements()
        self.save_data()
        sound_manager.play('success')
        self.update_all_pages()
        self.speak(f"Quest complete: {q['name']}! Plus {total_xp} XP and {small_points_gain} SP")

    def fail_quest(self, idx):
        qs = self.data['daily_quests']
        if idx >= len(qs) or qs[idx]['completed']: return
        q = qs[idx]
        p = self.data['player']
        xp_loss = q['xp'] // 2
        p['xp'] = max(0, safe_int(p['xp']) - xp_loss)
        p['streak'] = 0
        p['discipline_score'] = max(0, safe_int(p['discipline_score']) - 5)
        q['completed'] = True
        self.data['daily_quests'].append({
            'category': '⚠️ Penalty', 'name': '5min Extra Training',
            'desc': f'Penalty for failing: {q["name"]}', 'xp': 0,
            'attr': 'STR', 'target': 1, 'progress': 0, 'completed': False,
            'date': datetime.now().strftime('%Y-%m-%d')
        })
        self.save_data()
        self.update_all_pages()
        self.speak(f"Quest failed: {q['name']}. Lost {xp_loss} XP, streak reset.")

    def complete_quest_by_name(self, quest_name):
        """Find and complete a quest by name (voice command)"""
        quest_name = quest_name.lower().strip()
        for i, q in enumerate(self.data['daily_quests']):
            if not q['completed'] and (quest_name in q['name'].lower() or quest_name in q['desc'].lower()):
                self.complete_quest(i)
                return True
        # Try partial match
        words = quest_name.split()
        for word in words:
            if len(word) > 3:
                for i, q in enumerate(self.data['daily_quests']):
                    if not q['completed'] and word in q['name'].lower():
                        self.complete_quest(i)
                        return True
        return False

    def fail_quest_by_name(self, quest_name):
        """Find and fail a quest by name (voice command)"""
        quest_name = quest_name.lower().strip()
        for i, q in enumerate(self.data['daily_quests']):
            if not q['completed'] and (quest_name in q['name'].lower() or quest_name in q['desc'].lower()):
                self.fail_quest(i)
                return True
        return False

    def complete_goal_progress(self, idx):
        goals = self.data['main_goals']
        if idx >= len(goals) or not goals[idx].get('unlocked'): return
        g = goals[idx]
        p = self.data['player']
        g['progress'] = safe_int(g.get('progress', 0)) + 1
        p['large_points'] = safe_int(p.get('large_points', 0)) + 1
        if g['progress'] >= 10:
            g['completed'] = True
            p['goals_completed'] = safe_int(p.get('goals_completed', 0)) + 1
            p['xp'] = safe_int(p['xp']) + 300
            p['total_xp'] = safe_int(p['total_xp']) + 300
            p['gold'] = safe_int(p['gold']) + 100
            sound_manager.play('levelup')
            self.speak(f"Goal completed: {g['name']}!")
            for i, goal in enumerate(goals):
                if i > idx and not goal.get('unlocked'):
                    goal['unlocked'] = True
                    self.speak(f"New goal unlocked: {goal['name']}")
                    break
        self.check_achievements()
        self.save_data()
        self.update_all_pages()

    def progress_goal_by_name(self, goal_name):
        """Progress a goal by name (voice command)"""
        goal_name = goal_name.lower().strip()
        for i, g in enumerate(self.data['main_goals']):
            if g.get('unlocked') and not g.get('completed') and goal_name in g['name'].lower():
                self.complete_goal_progress(i)
                return True
        return False

    def add_daily_quest(self):
        dialog = QDialog(self)
        dialog.setStyleSheet("QDialog{background:#0D1B2A;} QLabel{color:#E0E0E0;}")
        dialog.setWindowTitle("Add Daily Quest")
        dialog.setFixedSize(400, 350)
        layout = QVBoxLayout(dialog)
        categories = ['🌅 Morning Routine', '📚 Study', '🌙 Night Routine']
        cat_cb = QComboBox(); cat_cb.addItems(categories)
        cat_cb.setStyleSheet("background:#06080F;color:#E0E0E0;border:1px solid #00D8FF;border-radius:5px;padding:8px;")
        layout.addWidget(QLabel("Category:")); layout.addWidget(cat_cb)
        name_edit = QLineEdit()
        name_edit.setStyleSheet("background:#06080F;color:#E0E0E0;border:1px solid #00D8FF;border-radius:5px;padding:8px;")
        layout.addWidget(QLabel("Quest Name:")); layout.addWidget(name_edit)
        desc_edit = QLineEdit()
        desc_edit.setStyleSheet("background:#06080F;color:#E0E0E0;border:1px solid #00D8FF;border-radius:5px;padding:8px;")
        layout.addWidget(QLabel("Description:")); layout.addWidget(desc_edit)
        xp_spin = QSpinBox(); xp_spin.setRange(1, 20); xp_spin.setValue(5)
        xp_spin.setStyleSheet("background:#06080F;color:#E0E0E0;border:1px solid #00D8FF;border-radius:5px;padding:8px;")
        layout.addWidget(QLabel("XP (1-20):")); layout.addWidget(xp_spin)
        attr_cb = QComboBox(); attr_cb.addItems(['STR', 'AGI', 'VIT', 'INT', 'PER'])
        attr_cb.setStyleSheet("background:#06080F;color:#E0E0E0;border:1px solid #00D8FF;border-radius:5px;padding:8px;")
        layout.addWidget(QLabel("Attribute:")); layout.addWidget(attr_cb)
        btn_layout = QHBoxLayout()
        add_btn = NeonButton("ADD", COLORS['green'])
        add_btn.clicked.connect(lambda: self.save_new_quest(cat_cb.currentText(), name_edit.text(), desc_edit.text(), xp_spin.value(), attr_cb.currentText(), dialog))
        btn_layout.addWidget(add_btn)
        cancel_btn = NeonButton("CANCEL", COLORS['red']); cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        dialog.exec()

    def save_new_quest(self, cat, name, desc, xp, attr, dialog):
        if name.strip():
            self.data['daily_quests'].append({'category': cat, 'name': name.strip(), 'desc': desc.strip() or name.strip(), 'xp': xp, 'attr': attr, 'target': 1, 'progress': 0, 'completed': False, 'date': datetime.now().strftime('%Y-%m-%d')})
            self.save_data(); self.update_all_pages(); dialog.accept(); self.speak("Quest added")

    def add_main_goal(self):
        dialog = QDialog(self)
        dialog.setStyleSheet("QDialog{background:#0D1B2A;} QLabel{color:#E0E0E0;}")
        dialog.setWindowTitle("Add Main Goal"); dialog.setFixedSize(400, 400)
        layout = QVBoxLayout(dialog)
        name_edit = QLineEdit()
        name_edit.setStyleSheet("background:#06080F;color:#E0E0E0;border:1px solid #00D8FF;border-radius:5px;padding:8px;")
        layout.addWidget(QLabel("Goal Name:")); layout.addWidget(name_edit)
        desc_edit = QLineEdit()
        desc_edit.setStyleSheet("background:#06080F;color:#E0E0E0;border:1px solid #00D8FF;border-radius:5px;padding:8px;")
        layout.addWidget(QLabel("Description:")); layout.addWidget(desc_edit)
        cat_cb = QComboBox(); cat_cb.addItems(['Language', 'Technology', 'Education', 'Fitness', 'Career', 'Ultimate'])
        cat_cb.setStyleSheet("background:#06080F;color:#E0E0E0;border:1px solid #00D8FF;border-radius:5px;padding:8px;")
        layout.addWidget(QLabel("Category:")); layout.addWidget(cat_cb)
        lp_spin = QSpinBox(); lp_spin.setRange(1, 10); lp_spin.setValue(3)
        lp_spin.setStyleSheet("background:#06080F;color:#E0E0E0;border:1px solid #00D8FF;border-radius:5px;padding:8px;")
        layout.addWidget(QLabel("Large Points:")); layout.addWidget(lp_spin)
        deadline_edit = QDateEdit(); deadline_edit.setDate(QDate.currentDate().addYears(1))
        deadline_edit.setStyleSheet("background:#06080F;color:#E0E0E0;border:1px solid #00D8FF;border-radius:5px;padding:8px;")
        layout.addWidget(QLabel("Deadline:")); layout.addWidget(deadline_edit)
        btn_layout = QHBoxLayout()
        add_btn = NeonButton("ADD", COLORS['green'])
        add_btn.clicked.connect(lambda: self.save_new_goal(name_edit.text(), desc_edit.text(), cat_cb.currentText(), lp_spin.value(), deadline_edit.date().toString('yyyy-MM-dd'), dialog))
        btn_layout.addWidget(add_btn)
        cancel_btn = NeonButton("CANCEL", COLORS['red']); cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        dialog.exec()

    def save_new_goal(self, name, desc, cat, lp, deadline, dialog):
        if name.strip():
            self.data['main_goals'].append({'name': name.strip(), 'desc': desc.strip() or name.strip(), 'large_points': lp, 'unlocked': True, 'completed': False, 'progress': 0, 'deadline': deadline, 'category': cat})
            self.save_data(); self.update_all_pages(); dialog.accept(); self.speak("Goal added")

    # ═══════════════════════ GOAL MANAGEMENT ═══════════════════════
    def edit_goal(self, idx):
        goals = self.data['main_goals']
        if idx >= len(goals): return
        g = goals[idx]
        dialog = QDialog(self)
        dialog.setStyleSheet("QDialog{background:#0D1B2A;} QLabel{color:#E0E0E0; font-size:12px;}")
        dialog.setWindowTitle(f"Edit: {g['name']}"); dialog.setFixedSize(450, 420)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Name:"))
        name_edit = QLineEdit(g['name'])
        name_edit.setStyleSheet("background:#06080F; color:#FFF; border:2px solid #FFD54A; border-radius:8px; padding:10px;")
        layout.addWidget(name_edit)
        layout.addWidget(QLabel("Description:"))
        desc_edit = QLineEdit(g['desc'])
        desc_edit.setStyleSheet("background:#06080F; color:#FFF; border:2px solid #44E8FF; border-radius:8px; padding:10px;")
        layout.addWidget(desc_edit)
        layout.addWidget(QLabel("Category:"))
        cat_cb = QComboBox(); cat_cb.addItems(['Language', 'Technology', 'Education', 'Fitness', 'Career', 'Ultimate'])
        cat_cb.setCurrentText(g.get('category', 'General'))
        cat_cb.setStyleSheet("background:#06080F; color:#FFF; border:2px solid #9C6DFF; border-radius:8px; padding:10px;")
        layout.addWidget(cat_cb)
        layout.addWidget(QLabel("Progress (0-10):"))
        prog_spin = QSpinBox(); prog_spin.setRange(0, 10); prog_spin.setValue(safe_int(g.get('progress', 0)))
        prog_spin.setStyleSheet("background:#06080F; color:#FFF; border:2px solid #35FF99; border-radius:8px; padding:10px;")
        layout.addWidget(prog_spin)
        layout.addWidget(QLabel("Deadline:"))
        deadline_edit = QDateEdit()
        try: deadline_edit.setDate(QDate.fromString(g.get('deadline', ''), 'yyyy-MM-dd'))
        except: deadline_edit.setDate(QDate.currentDate().addYears(1))
        deadline_edit.setStyleSheet("background:#06080F; color:#FFF; border:2px solid #FFA927; border-radius:8px; padding:10px;")
        layout.addWidget(deadline_edit)
        lock_cb = QCheckBox("Unlocked"); lock_cb.setChecked(g.get('unlocked', False))
        lock_cb.setStyleSheet("color:#FFD54A; font-size:13px; font-weight:bold;")
        layout.addWidget(lock_cb)
        comp_cb = QCheckBox("Completed"); comp_cb.setChecked(g.get('completed', False))
        comp_cb.setStyleSheet("color:#35FF99; font-size:13px; font-weight:bold;")
        layout.addWidget(comp_cb)
        btn_layout = QHBoxLayout()
        save_btn = NeonButton("💾 SAVE", COLORS['green'])
        save_btn.clicked.connect(lambda: self.save_edited_goal(idx, name_edit.text(), desc_edit.text(), cat_cb.currentText(), prog_spin.value(), deadline_edit.date().toString('yyyy-MM-dd'), lock_cb.isChecked(), comp_cb.isChecked(), dialog))
        btn_layout.addWidget(save_btn)
        delete_btn = NeonButton("🗑️ DELETE", COLORS['red'])
        delete_btn.clicked.connect(lambda: self.delete_goal(idx, dialog))
        btn_layout.addWidget(delete_btn)
        cancel_btn = NeonButton("✕ CANCEL", COLORS['cyan']); cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        dialog.exec()

    def save_edited_goal(self, idx, name, desc, cat, prog, deadline, unlocked, completed, dialog):
        if name.strip():
            goals = self.data['main_goals']
            goals[idx]['name'] = name.strip(); goals[idx]['desc'] = desc.strip() or name.strip()
            goals[idx]['category'] = cat; goals[idx]['progress'] = prog
            goals[idx]['deadline'] = deadline; goals[idx]['unlocked'] = unlocked
            goals[idx]['completed'] = completed
            if completed: goals[idx]['progress'] = 10
            self.save_data(); self.update_main_goals(); dialog.accept(); self.speak("Goal updated")

    def delete_goal(self, idx, dialog):
        msg = QMessageBox()
        msg.setStyleSheet("QMessageBox{background:#0D1B2A; color:#E0E0E0;}")
        msg.setWindowTitle("Delete Goal")
        msg.setText(f"Delete '{self.data['main_goals'][idx]['name']}'?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if msg.exec() == QMessageBox.Yes:
            del self.data['main_goals'][idx]
            self.save_data(); self.update_main_goals(); dialog.reject(); self.speak("Goal deleted")

    def reset_all_goals(self):
        msg = QMessageBox()
        msg.setStyleSheet("QMessageBox{background:#0D1B2A; color:#E0E0E0;}")
        msg.setWindowTitle("Reset Goals")
        msg.setText("Reset all goals to default?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if msg.exec() == QMessageBox.Yes:
            self.data['main_goals'] = [
                {'name': '🇩🇪 German Language', 'desc': 'Achieve B1 level fluency', 'large_points': 3, 'unlocked': True, 'completed': False, 'progress': 0, 'deadline': '2026-12-31', 'category': 'Language'},
                {'name': '🇬🇧 English Language', 'desc': 'Achieve C2 level mastery', 'large_points': 3, 'unlocked': False, 'completed': False, 'progress': 0, 'deadline': '2027-06-30', 'category': 'Language'},
                {'name': '💻 Python Programming', 'desc': 'Become Python expert', 'large_points': 3, 'unlocked': False, 'completed': False, 'progress': 0, 'deadline': '2026-12-31', 'category': 'Technology'},
                {'name': '🎓 CS Mastering', 'desc': 'Master Computer Science fundamentals', 'large_points': 3, 'unlocked': False, 'completed': False, 'progress': 0, 'deadline': '2027-12-31', 'category': 'Education'},
                {'name': '👑 Shadow Monarch', 'desc': 'Reach Monarch rank and complete all goals', 'large_points': 3, 'unlocked': False, 'completed': False, 'progress': 0, 'deadline': '2028-12-31', 'category': 'Ultimate'},
            ]
            self.save_data(); self.update_main_goals(); self.speak("Goals reset")

    # ═══════════════════════ NAVIGATION ═══════════════════════
    def upload_profile_pic(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Profile Picture", "", "Images (*.png *.jpg *.jpeg *.gif *.bmp)")
        if file_path:
            self.data['player']['profile_pic'] = file_path
            self.save_data(); self.update_profile_page(); self.speak("Profile picture updated")

    def buy_item(self, price, attr, boost):
        p = self.data['player']
        if safe_int(p['gold']) >= price:
            p['gold'] = safe_int(p['gold']) - price
            if attr == 'ALL':
                for stat in ['STR', 'AGI', 'VIT', 'INT', 'PER']:
                    p['stats'][stat] = min(100, safe_int(p['stats'][stat]) + boost)
            else:
                p['stats'][attr] = min(100, safe_int(p['stats'][attr]) + boost)
            self.save_data(); self.check_achievements(); sound_manager.play('success')
            self.speak(f"Purchased! +{boost} {attr}"); self.update_all_pages()

    def show_page(self, page_name):
        if page_name in self.pages:
            if self.current_page and self.current_page != page_name:
                self.page_history.append(self.current_page)
            self.current_page = page_name
            self.stack.setCurrentWidget(self.pages[page_name])
            self.update_all_pages()

    def go_back(self):
        if self.page_history:
            prev = self.page_history.pop()
            self.current_page = prev
            self.stack.setCurrentWidget(self.pages[prev])
            self.update_all_pages()
        else: self.show_page('dashboard')

    def handle_voice_command(self, ctype, data):
        if ctype == 'navigate':
            self.show_page(data.get('page'))
        elif ctype == 'back':
            self.go_back()
        elif ctype == 'status_query':
            self.handle_status_query(data.get('command', ''))
        elif ctype == 'complete_quest_voice':
            cmd = data.get('command', '')
            # Extract quest name from command
            quest_name = cmd.replace('complete', '').replace('done', '').replace('finish', '').replace('do', '').strip()
            if quest_name:
                success = self.complete_quest_by_name(quest_name)
                if not success:
                    self.speak(f"Could not find quest: {quest_name}")
            else:
                self.speak("Which quest should I complete? Say complete followed by the quest name.")
        elif ctype == 'fail_quest_voice':
            cmd = data.get('command', '')
            quest_name = cmd.replace('fail', '').replace('skip', '').replace('missed', '').strip()
            if quest_name:
                success = self.fail_quest_by_name(quest_name)
                if not success:
                    self.speak(f"Could not find quest: {quest_name}")
            else:
                self.speak("Which quest did you fail? Say fail followed by the quest name.")
        elif ctype == 'progress_goal':
            cmd = data.get('command', '')
            goal_name = cmd.replace('progress goal', '').replace('advance goal', '').replace('update goal', '').strip()
            if goal_name:
                success = self.progress_goal_by_name(goal_name)
                if not success:
                    self.speak(f"Could not find goal: {goal_name}")
            else:
                self.speak("Which goal should I progress?")
        elif ctype == 'add_quest':
            self.add_daily_quest()
        elif ctype == 'add_goal':
            self.add_main_goal()
        elif ctype == 'toggle_voice':
            self.toggle_voice()

    def handle_status_query(self, command):
        p = self.data['player']
        rank = self.get_rank(safe_int(p['xp']))
        
        if any(w in command for w in ['experience', 'xp', 'level', 'rank']):
            next_rank = self.get_next_rank(safe_int(p['xp']))
            xp_to_next = next_rank['xp_required'] - safe_int(p['xp']) if next_rank else 0
            self.speak(f"You are level {p['level']}, {rank['name']} rank. You have {safe_int(p['xp'])} XP. {xp_to_next} XP needed for next rank.")
        elif any(w in command for w in ['strength', 'power', 'strong']):
            self.speak(f"Your strength is {safe_int(p.get('strength', 10))}. Your power level is {p['power']}. STR attribute: {safe_int(p['stats']['STR'])} out of 100.")
        elif any(w in command for w in ['gold', 'money', 'coin']):
            self.speak(f"You have {safe_int(p['gold'])} gold coins.")
        elif any(w in command for w in ['streak', 'days']):
            self.speak(f"Your current streak is {safe_int(p['streak'])} days. Best streak: {safe_int(p['best_streak'])} days.")
        elif any(w in command for w in ['goals']):
            self.speak(f"You have completed {safe_int(p.get('goals_completed', 0))} main goals.")
        elif any(w in command for w in ['achievement']):
            unlocked = sum(1 for a in self.data['achievements'] if a['unlocked'])
            self.speak(f"You have unlocked {unlocked} out of {len(ACHIEVEMENTS)} achievements.")
        elif any(w in command for w in ['discipline']):
            self.speak(f"Your discipline score is {safe_int(p['discipline_score'])} out of 100.")
        elif any(w in command for w in ['health', 'vitality', 'hp']):
            self.speak(f"Your health score is {safe_int(p.get('health_score', 50))}. VIT attribute: {safe_int(p['stats']['VIT'])} out of 100.")
        else:
            # General status
            today = datetime.now().strftime('%Y-%m-%d')
            daily_quests = [q for q in self.data['daily_quests'] if q.get('date') == today]
            done_today = sum(1 for q in daily_quests if q.get('completed'))
            total_today = len([q for q in daily_quests if q.get('category') != '⚠️ Penalty'])
            self.speak(f"Status update. Level {p['level']}, {rank['name']} rank. {done_today} of {total_today} quests done today. {safe_int(p['streak'])} day streak. {safe_int(p['gold'])} gold. {safe_int(p.get('small_points', 0))} small points.")
            self.speak(f"Your stats: Strength {safe_int(p['stats']['STR'])}, Agility {safe_int(p['stats']['AGI'])}, Vitality {safe_int(p['stats']['VIT'])}, Intelligence {safe_int(p['stats']['INT'])}, Perception {safe_int(p['stats']['PER'])}.")

    def speak(self, text):
        if self.voice_processor: self.voice_processor.speak(text)

    def start_voice(self):
        if self.voice_processor: self.is_voice_active = True; self.voice_processor.start_listening()

    def stop_voice(self):
        if self.voice_processor: self.is_voice_active = False; self.voice_processor.stop_listening()

    def toggle_voice(self):
        if self.is_voice_active: 
            self.stop_voice()
            self.speak("Voice control stopped")
        else: 
            self.start_voice()
            self.speak("Voice control activated. Say help to know available commands.")

    def toggle_fullscreen(self):
        if self.isFullScreen(): self.showNormal(); self.setGeometry(50, 30, 1500, 900)
        else: self.showFullScreen()

    def update_all_pages(self):
        if self.current_page == 'dashboard': self.update_dashboard()
        elif self.current_page == 'daily_quests': self.update_daily_quests()
        elif self.current_page == 'main_goals': self.update_main_goals()
        elif self.current_page == 'profile': self.update_profile_page()

    # ═══════════════════════ TITLE BAR ═══════════════════════
    def create_title_bar(self):
        tb = QFrame(); tb.setFixedHeight(40)
        tb.setStyleSheet("background:rgba(2,4,10,240); border-bottom:1px solid #0D2137;")
        def mousePressEvent(e): self.drag_pos = e.globalPosition().toPoint()
        def mouseMoveEvent(e):
            if hasattr(self, 'drag_pos') and self.drag_pos:
                self.move(self.pos() + e.globalPosition().toPoint() - self.drag_pos)
                self.drag_pos = e.globalPosition().toPoint()
        tb.mousePressEvent = mousePressEvent; tb.mouseMoveEvent = mouseMoveEvent
        layout = QHBoxLayout(tb); layout.setContentsMargins(15, 0, 15, 0)
        title = QLabel("⚔️ SOLO LEVELING SV17 - VOICE CONTROL")
        title.setStyleSheet("color:#00D8FF;font-family:Orbitron;font-size:12px;font-weight:bold;")
        layout.addWidget(title)
        creator = QLabel("| Ashiq Hussain")
        creator.setStyleSheet("color:#9C6DFF;font-size:11px;"); layout.addWidget(creator)
        layout.addStretch()
        voice_status = QLabel("🎤 ON" if self.is_voice_active else "🎤 OFF")
        voice_status.setStyleSheet("color:#44E8FF;font-size:11px;font-weight:bold;padding:0 10px;")
        layout.addWidget(voice_status)
        voice_btn = QPushButton("🎤"); voice_btn.setFixedSize(30, 28)
        voice_btn.setStyleSheet("background:transparent;color:#00D8FF;border:none;font-size:16px;")
        voice_btn.setToolTip("Toggle Voice Commands"); voice_btn.clicked.connect(self.toggle_voice)
        layout.addWidget(voice_btn)
        for text, color, func in [("🗕", "#E0E0E0", self.showMinimized), ("⛶", "#FFD54A", self.toggle_fullscreen), ("✕", "#FF4D6D", self.close)]:
            btn = QPushButton(text); btn.setFixedSize(30, 28)
            btn.setStyleSheet(f"background:transparent;color:{color};border:none;font-size:14px;")
            btn.clicked.connect(func); layout.addWidget(btn)
        self.main_layout.addWidget(tb)

    # ═══════════════════════ ALL PAGES ═══════════════════════
    def create_all_pages(self):
        self.pages = {}
        self.pages['dashboard'] = self.create_dashboard()
        self.pages['daily_quests'] = self.create_daily_quests_page()
        self.pages['main_goals'] = self.create_main_goals_page()
        self.pages['analytics'] = self.create_analytics_page()
        self.pages['mental'] = self.create_mental_page()
        self.pages['physical'] = self.create_physical_page()
        self.pages['spiritual'] = self.create_spiritual_page()
        self.pages['achievements'] = self.create_achievements_page()
        self.pages['shop'] = self.create_shop_page()
        self.pages['reviews'] = self.create_reviews_page()
        self.pages['profile'] = self.create_profile_page()
        self.pages['settings'] = self.create_settings_page()
        for page in self.pages.values(): self.stack.addWidget(page)

    # ═══════════════════════ DASHBOARD ═══════════════════════
    def create_dashboard(self):
        page = QWidget(); page.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(page); layout.setSpacing(10); layout.setContentsMargins(15, 15, 15, 15)
        header = QHBoxLayout()
        title = QLabel("👑 THE SYSTEM - SV17 ULTIMATE")
        title.setStyleSheet("color:#FFD54A;font-family:Orbitron;font-size:24px;font-weight:bold;")
        header.addWidget(title); header.addStretch()
        self.dash_rank_badge = QLabel("⬜ E RANK")
        self.dash_rank_badge.setStyleSheet("color:#FFD54A;font-size:14px;font-weight:bold;background:rgba(0,0,0,0.5);padding:8px 22px;border:2px solid #FFD54A;border-radius:22px;")
        header.addWidget(self.dash_rank_badge); layout.addLayout(header)

        card = GlassPanel(); card.setFixedHeight(170)
        cl = QHBoxLayout(card); cl.setSpacing(15)
        self.dash_profile_pic = QLabel("👤"); self.dash_profile_pic.setStyleSheet("font-size:60px;")
        self.dash_profile_pic.setFixedSize(80, 80); self.dash_profile_pic.setAlignment(Qt.AlignCenter)
        self.dash_profile_pic.mousePressEvent = lambda e: self.upload_profile_pic()
        self.dash_profile_pic.setCursor(Qt.PointingHandCursor); cl.addWidget(self.dash_profile_pic)

        info = QVBoxLayout()
        self.dash_name = QLabel("Master Aurora"); self.dash_name.setStyleSheet("color:#FFD54A;font-size:24px;font-weight:bold;")
        info.addWidget(self.dash_name)
        self.dash_title = QLabel("Novice Hunter"); self.dash_title.setStyleSheet("color:#9C6DFF;font-size:14px;")
        info.addWidget(self.dash_title)
        stats_row = QHBoxLayout()
        self.dash_level = QLabel("LVL 1"); self.dash_level.setStyleSheet("color:#00D8FF;font-size:15px;font-weight:bold;")
        stats_row.addWidget(self.dash_level)
        self.dash_xp = QLabel("XP: 0"); self.dash_xp.setStyleSheet("color:#35FF99;font-size:13px;")
        stats_row.addWidget(self.dash_xp); info.addLayout(stats_row)
        power_row = QHBoxLayout()
        self.dash_power = QLabel("⚡ Power: 100"); self.dash_power.setStyleSheet("color:#FFA927;font-size:14px;font-weight:bold;")
        power_row.addWidget(self.dash_power)
        self.dash_strength = QLabel("💢 Strength: 10"); self.dash_strength.setStyleSheet("color:#FF6B6B;font-size:14px;font-weight:bold;")
        power_row.addWidget(self.dash_strength); info.addLayout(power_row)
        res_row = QHBoxLayout()
        self.dash_gold = QLabel("💰 50 Gold"); self.dash_gold.setStyleSheet("color:#FFD700;font-size:13px;font-weight:bold;")
        res_row.addWidget(self.dash_gold)
        self.dash_streak = QLabel("🔥 0 days"); self.dash_streak.setStyleSheet("color:#FFA927;font-size:13px;font-weight:bold;")
        res_row.addWidget(self.dash_streak); info.addLayout(res_row)
        cl.addLayout(info); cl.addStretch()

        mini_stats = QVBoxLayout(); mini_stats.setSpacing(5)
        self.dash_sp = QLabel("🎯 SP: 0"); self.dash_sp.setStyleSheet("color:#E0E0E0;font-size:12px;font-weight:bold;"); mini_stats.addWidget(self.dash_sp)
        self.dash_lp = QLabel("💎 LP: 0"); self.dash_lp.setStyleSheet("color:#E0E0E0;font-size:12px;font-weight:bold;"); mini_stats.addWidget(self.dash_lp)
        self.dash_hp = QLabel("❤️ HP: 50"); self.dash_hp.setStyleSheet("color:#E0E0E0;font-size:12px;font-weight:bold;"); mini_stats.addWidget(self.dash_hp)
        self.dash_disc = QLabel("📊 DISC: 50"); self.dash_disc.setStyleSheet("color:#E0E0E0;font-size:12px;font-weight:bold;"); mini_stats.addWidget(self.dash_disc)
        cl.addLayout(mini_stats); layout.addWidget(card)

        xp_layout = QVBoxLayout()
        xp_header = QHBoxLayout()
        xp_label = QLabel("📈 EXPERIENCE"); xp_label.setStyleSheet("color:#35FF99;font-size:12px;font-weight:bold;"); xp_header.addWidget(xp_label)
        self.xp_text = QLabel("0 / 100"); self.xp_text.setStyleSheet("color:#35FF99;font-size:12px;"); xp_header.addWidget(self.xp_text, alignment=Qt.AlignRight)
        xp_layout.addLayout(xp_header)
        self.xp_bar = AnimatedProgressBar(color=COLORS['blue']); self.xp_bar.setRange(0, 100); self.xp_bar.setFixedHeight(16)
        xp_layout.addWidget(self.xp_bar); layout.addLayout(xp_layout)

        strength_layout = QVBoxLayout()
        str_header = QHBoxLayout()
        str_label = QLabel("💢 STRENGTH"); str_label.setStyleSheet("color:#FF6B6B;font-size:12px;font-weight:bold;"); str_header.addWidget(str_label)
        self.str_text = QLabel("10 / ∞"); self.str_text.setStyleSheet("color:#FF6B6B;font-size:12px;"); str_header.addWidget(self.str_text, alignment=Qt.AlignRight)
        strength_layout.addLayout(str_header)
        self.str_bar = AnimatedProgressBar(color=COLORS['red']); self.str_bar.setRange(0, 100); self.str_bar.setValue(10); self.str_bar.setFixedHeight(16)
        strength_layout.addWidget(self.str_bar); layout.addLayout(strength_layout)

        quick_stats = GlassPanel(); quick_stats.setFixedHeight(60)
        qs_layout = QHBoxLayout(quick_stats); qs_layout.setSpacing(20)
        self.quick_today_label = QLabel("📋 Quests Today: 0/0"); self.quick_today_label.setStyleSheet("color:#E0E0E0;font-size:12px;font-weight:bold;"); qs_layout.addWidget(self.quick_today_label)
        self.quick_ach_label = QLabel("🏆 Achievements: 0/24"); self.quick_ach_label.setStyleSheet("color:#FFD54A;font-size:12px;font-weight:bold;"); qs_layout.addWidget(self.quick_ach_label)
        self.quick_fail_label = QLabel("⚠️ Penalties: 0"); self.quick_fail_label.setStyleSheet("color:#FF4D6D;font-size:12px;font-weight:bold;"); qs_layout.addWidget(self.quick_fail_label)
        self.quick_goal_label = QLabel("🎯 Goals Done: 0"); self.quick_goal_label.setStyleSheet("color:#35FF99;font-size:12px;font-weight:bold;"); qs_layout.addWidget(self.quick_goal_label)
        self.quick_voice_label = QLabel("🎤 Voice: OFF"); self.quick_voice_label.setStyleSheet("color:#44E8FF;font-size:12px;font-weight:bold;"); qs_layout.addWidget(self.quick_voice_label)
        layout.addWidget(quick_stats)

        voice_tip = QLabel("💡 VOICE COMMANDS: Say 'open quests', 'complete morning exercise', 'status', 'how much gold', 'what is my strength', 'go back'")
        voice_tip.setStyleSheet("color:#44E8FF;font-size:10px;background:rgba(68,232,255,0.1);padding:5px;border-radius:5px;")
        voice_tip.setAlignment(Qt.AlignCenter); layout.addWidget(voice_tip)

        nav = QGridLayout(); nav.setSpacing(8)
        items = [
            ("📋 DAILY QUESTS", 'daily_quests', COLORS['cyan'], 0, 0),
            ("🎯 MAIN GOALS", 'main_goals', COLORS['gold'], 0, 1),
            ("📊 ANALYTICS", 'analytics', COLORS['purple'], 0, 2),
            ("🧠 MENTAL", 'mental', COLORS['purple'], 1, 0),
            ("💪 PHYSICAL", 'physical', COLORS['green'], 1, 1),
            ("🕉️ SPIRITUAL", 'spiritual', COLORS['orange'], 1, 2),
            ("🏆 ACHIEVEMENTS", 'achievements', COLORS['gold'], 2, 0),
            ("📝 REVIEWS", 'reviews', COLORS['teal'], 2, 1),
            ("🛒 SHOP", 'shop', COLORS['pink'], 2, 2),
        ]
        for text, pname, color, row, col in items:
            btn = NeonButton(text, color); btn.setMinimumHeight(45); btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
            btn.clicked.connect(lambda checked, p=pname: self.show_page(p)); nav.addWidget(btn, row, col)
        layout.addLayout(nav)

        bottom = QHBoxLayout(); bottom.setSpacing(10)
        profile_btn = NeonButton("👤 PROFILE", COLORS['blue']); profile_btn.setMinimumHeight(40)
        profile_btn.clicked.connect(lambda: self.show_page('profile')); bottom.addWidget(profile_btn)
        settings_btn = NeonButton("⚙️ SETTINGS", COLORS['cyan']); settings_btn.setMinimumHeight(40)
        settings_btn.clicked.connect(lambda: self.show_page('settings')); bottom.addWidget(settings_btn)
        layout.addLayout(bottom); layout.addStretch()
        return page

    def update_dashboard(self):
        p = self.data['player']; rank = self.get_rank(safe_int(p['xp']))
        self.dash_name.setText(p['name']); self.dash_title.setText(p.get('title', 'Hunter'))
        self.dash_rank_badge.setText(f"{rank['icon']} {rank['name']} RANK")
        self.dash_level.setText(f"LVL {p['level']}"); self.dash_xp.setText(f"XP: {safe_int(p['total_xp'])}")
        self.dash_power.setText(f"⚡ Power: {p['power']}"); self.dash_strength.setText(f"💢 Strength: {safe_int(p.get('strength', 10))}")
        self.dash_gold.setText(f"💰 {safe_int(p['gold'])} Gold"); self.dash_streak.setText(f"🔥 {safe_int(p['streak'])} days")
        self.dash_sp.setText(f"🎯 SP: {safe_int(p.get('small_points', 0))}"); self.dash_lp.setText(f"💎 LP: {safe_int(p.get('large_points', 0))}")
        self.dash_hp.setText(f"❤️ HP: {safe_int(p.get('health_score', 50))}"); self.dash_disc.setText(f"📊 DISC: {safe_int(p.get('discipline_score', 50))}")
        if p.get('profile_pic') and os.path.exists(p['profile_pic']):
            pixmap = QPixmap(p['profile_pic']); self.dash_profile_pic.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)); self.dash_profile_pic.setText("")

        xp_needed = self.get_next_rank(safe_int(p['xp']))['xp_required'] if self.get_next_rank(safe_int(p['xp'])) else safe_int(p['xp']) + 100
        xp_in_rank = safe_int(p['xp']) - rank['xp_required']
        xp_to_next = xp_needed - rank['xp_required'] if self.get_next_rank(safe_int(p['xp'])) else 100
        pct = (xp_in_rank / xp_to_next * 100) if xp_to_next > 0 else 100
        self.xp_bar.setValue(int(pct)); self.xp_text.setText(f"{xp_in_rank} / {xp_to_next} XP")

        strength = safe_int(p.get('strength', 10)); self.str_bar.setValue(min(strength, 100)); self.str_text.setText(f"{strength} / ∞")

        today = datetime.now().strftime('%Y-%m-%d')
        daily_quests = [q for q in self.data['daily_quests'] if q.get('date') == today]
        done_today = sum(1 for q in daily_quests if q.get('completed'))
        total_today = len([q for q in daily_quests if q.get('category') != '⚠️ Penalty'])
        self.quick_today_label.setText(f"📋 Quests Today: {done_today}/{total_today}")
        penalties = len([q for q in daily_quests if 'Penalty' in q.get('category','')])
        self.quick_fail_label.setText(f"⚠️ Penalties: {penalties}")
        unlocked = sum(1 for a in self.data['achievements'] if a['unlocked'])
        self.quick_ach_label.setText(f"🏆 Achievements: {unlocked}/{len(ACHIEVEMENTS)}")
        goals_done = safe_int(p.get('goals_completed', 0)); self.quick_goal_label.setText(f"🎯 Goals Done: {goals_done}")
        self.quick_voice_label.setText(f"🎤 Voice: {'ON' if self.is_voice_active else 'OFF'}")

    # ═══════════════════════ DAILY QUESTS ═══════════════════════
    def create_daily_quests_page(self):
        page = QWidget(); page.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(page); layout.setContentsMargins(15, 15, 15, 15); layout.setSpacing(8)
        header = QHBoxLayout()
        back_btn = NeonButton("← BACK", COLORS['cyan']); back_btn.setFixedWidth(110); back_btn.clicked.connect(self.go_back)
        header.addWidget(back_btn)
        title = QLabel("📋 DAILY QUESTS"); title.setStyleSheet("color:#00D8FF;font-family:Orbitron;font-size:22px;font-weight:bold;")
        title.setAlignment(Qt.AlignCenter); header.addWidget(title)
        self.dq_progress_label = QLabel("0/10"); self.dq_progress_label.setStyleSheet("color:#35FF99;font-size:18px;font-weight:bold;")
        header.addWidget(self.dq_progress_label); header.addStretch(); layout.addLayout(header)
        voice_tip = QLabel("💡 Say: 'complete morning exercise' or 'fail python coding'")
        voice_tip.setStyleSheet("color:#44E8FF;font-size:10px;background:rgba(68,232,255,0.1);padding:5px;border-radius:5px;"); layout.addWidget(voice_tip)
        info = QLabel("⚠️ Failed quests = Penalty Zone (5 min extra training)  |  ✓ = Complete  |  ✕ = Fail")
        info.setStyleSheet("color:#FF4D6D;font-size:12px;background:rgba(255,77,109,0.1);padding:8px;border-radius:8px;")
        info.setAlignment(Qt.AlignCenter); layout.addWidget(info)
        self.dq_scroll = QScrollArea(); self.dq_scroll.setStyleSheet("background:transparent;border:none;"); self.dq_scroll.setWidgetResizable(True)
        self.dq_container = QWidget(); self.dq_container.setStyleSheet("background:transparent;")
        self.dq_layout = QVBoxLayout(self.dq_container); self.dq_layout.setSpacing(8)
        self.dq_scroll.setWidget(self.dq_container); layout.addWidget(self.dq_scroll)
        add_btn = NeonButton("➕ ADD QUEST", COLORS['green']); add_btn.setMinimumHeight(40); add_btn.clicked.connect(self.add_daily_quest)
        layout.addWidget(add_btn); self.update_daily_quests()
        return page

    def update_daily_quests(self):
        for i in reversed(range(self.dq_layout.count())):
            widget = self.dq_layout.itemAt(i).widget()
            if widget: widget.deleteLater()
        quests_by_cat = {}
        for q in self.data['daily_quests']:
            cat = q.get('category', 'General')
            if cat not in quests_by_cat: quests_by_cat[cat] = []
            quests_by_cat[cat].append(q)
        for cat, quests in quests_by_cat.items():
            cat_label = QLabel(f"  {cat}")
            cat_label.setStyleSheet(f"color:{'#FF4D6D' if 'Penalty' in cat else '#FFD54A'};font-size:15px;font-weight:bold;padding:6px;")
            self.dq_layout.addWidget(cat_label)
            for q in quests:
                card = GlassPanel(); card.custom_color = QColor(53, 255, 153, 35) if q['completed'] else COLORS['glass']
                cl = QHBoxLayout(card); cl.setContentsMargins(12, 8, 12, 8)
                icon = QLabel("✅" if q['completed'] else "⬜"); icon.setStyleSheet("font-size:24px;"); cl.addWidget(icon)
                info = QVBoxLayout()
                name = QLabel(q['name']); name.setStyleSheet(f"color:{'#35FF99' if q['completed'] else '#E0E0E0'};font-size:13px;font-weight:bold;")
                info.addWidget(name)
                desc = QLabel(f"{q['desc']} • +{q['xp']} XP • {q.get('attr', 'STR')}"); desc.setStyleSheet("color:#44E8FF;font-size:11px;")
                info.addWidget(desc); cl.addLayout(info); cl.addStretch()
                if not q['completed']:
                    actual_idx = next((j for j, q2 in enumerate(self.data['daily_quests']) if q2['name'] == q['name'] and q2['category'] == q['category'] and not q2['completed']), None)
                    if actual_idx is not None:
                        complete_btn = NeonButton("✓", COLORS['green']); complete_btn.setFixedSize(40, 40)
                        complete_btn.clicked.connect(lambda checked, idx=actual_idx: self.complete_quest(idx)); cl.addWidget(complete_btn)
                        fail_btn = NeonButton("✕", COLORS['red']); fail_btn.setFixedSize(40, 40)
                        fail_btn.clicked.connect(lambda checked, idx=actual_idx: self.fail_quest(idx)); cl.addWidget(fail_btn)
                else:
                    status = QLabel("✅ DONE"); status.setStyleSheet("color:#35FF99;font-size:13px;font-weight:bold;"); cl.addWidget(status)
                self.dq_layout.addWidget(card)
        total = len([q for q in self.data['daily_quests'] if q.get('category') != '⚠️ Penalty'])
        completed = sum(1 for q in self.data['daily_quests'] if q['completed'])
        self.dq_progress_label.setText(f"{completed}/{total}")

    # ═══════════════════════ MAIN GOALS (IMPROVED) ═══════════════════════
    def create_main_goals_page(self):
        page = QWidget(); page.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(page); layout.setContentsMargins(15, 15, 15, 15); layout.setSpacing(8)
        header = QHBoxLayout()
        back_btn = NeonButton("← BACK", COLORS['cyan']); back_btn.setFixedWidth(110); back_btn.clicked.connect(self.go_back)
        header.addWidget(back_btn)
        title = QLabel("🎯 MAIN GOALS"); title.setStyleSheet("color:#FFD54A; font-family:Orbitron; font-size:22px; font-weight:bold;")
        title.setAlignment(Qt.AlignCenter); header.addWidget(title); header.addStretch(); layout.addLayout(header)
        voice_tip = QLabel("💡 Say: 'progress goal German Language'")
        voice_tip.setStyleSheet("color:#44E8FF;font-size:10px;background:rgba(68,232,255,0.1);padding:5px;border-radius:5px;"); layout.addWidget(voice_tip)
        info = QLabel("💡 3 Large Points per goal • Progress 10 steps to complete • Watch your deadlines!")
        info.setStyleSheet("color:#FFFFFF; font-size:12px; background:rgba(68,232,255,0.2); padding:8px; border-radius:8px;")
        info.setAlignment(Qt.AlignCenter); layout.addWidget(info)
        self.mg_scroll = QScrollArea(); self.mg_scroll.setStyleSheet("background:transparent; border:none;"); self.mg_scroll.setWidgetResizable(True)
        self.mg_container = QWidget(); self.mg_container.setStyleSheet("background:transparent;")
        self.mg_layout = QVBoxLayout(self.mg_container); self.mg_layout.setSpacing(10)
        self.mg_scroll.setWidget(self.mg_container); layout.addWidget(self.mg_scroll)
        btn_layout = QHBoxLayout()
        add_btn = NeonButton("➕ ADD GOAL", COLORS['green']); add_btn.setMinimumHeight(40); add_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        add_btn.clicked.connect(self.add_main_goal); btn_layout.addWidget(add_btn)
        reset_btn = NeonButton("🔄 RESET ALL", COLORS['orange']); reset_btn.setMinimumHeight(40); reset_btn.clicked.connect(self.reset_all_goals)
        btn_layout.addWidget(reset_btn); layout.addLayout(btn_layout); self.update_main_goals()
        return page

    def update_main_goals(self):
        for i in reversed(range(self.mg_layout.count())):
            widget = self.mg_layout.itemAt(i).widget()
            if widget: widget.deleteLater()
        for i, g in enumerate(self.data['main_goals']):
            card = GlassPanel()
            if g.get('completed'): card.custom_color = QColor(53, 255, 153, 60)
            elif g.get('unlocked'): card.custom_color = QColor(0, 216, 255, 50)
            else: card.custom_color = QColor(80, 80, 100, 50)
            main_layout = QVBoxLayout(card); main_layout.setContentsMargins(15, 12, 15, 12); main_layout.setSpacing(8)
            top_row = QHBoxLayout()
            if g.get('completed'): icon_text, name_color = "✅", "#35FF99"
            elif g.get('unlocked'): icon_text, name_color = "🔓", "#FFD54A"
            else: icon_text, name_color = "🔒", "#888888"
            icon_label = QLabel(icon_text); icon_label.setStyleSheet("font-size:28px;"); top_row.addWidget(icon_label)
            name_label = QLabel(g['name']); name_label.setStyleSheet(f"color:{name_color}; font-size:16px; font-weight:bold;"); top_row.addWidget(name_label)
            top_row.addStretch()
            edit_btn = NeonButton("✏️ EDIT", COLORS['blue']); edit_btn.setFixedSize(70, 35)
            edit_btn.clicked.connect(lambda checked, idx=i: self.edit_goal(idx)); top_row.addWidget(edit_btn)
            main_layout.addLayout(top_row)
            desc_color = "#FFFFFF" if g.get('unlocked') else "#AAAAAA"
            desc_label = QLabel(g['desc']); desc_label.setStyleSheet(f"color:{desc_color}; font-size:12px; padding-left:35px;")
            desc_label.setWordWrap(True); main_layout.addWidget(desc_label)
            bottom_row = QHBoxLayout(); bottom_row.setContentsMargins(35, 5, 0, 0)
            if g.get('deadline'):
                if g.get('unlocked') and not g.get('completed'):
                    try:
                        deadline_date = datetime.strptime(g['deadline'], '%Y-%m-%d').date()
                        days_left = (deadline_date - datetime.now().date()).days
                        if days_left > 30: d_color, d_emoji = '#35FF99', '🟢'
                        elif days_left > 7: d_color, d_emoji = '#FFA927', '🟡'
                        elif days_left >= 0: d_color, d_emoji = '#FF4D6D', '🔴'
                        else: d_color, d_emoji = '#FF0000', '💀'; days_left = abs(days_left)
                        deadline_text = f"{d_emoji} {days_left} days left"
                    except: deadline_text = f"📅 {g['deadline']}"; d_color = '#44E8FF'
                else: deadline_text = f"📅 {g['deadline']}"; d_color = '#35FF99' if g.get('completed') else '#888888'
            else: deadline_text = "📅 No deadline"; d_color = '#888888'
            deadline_label = QLabel(deadline_text)
            deadline_label.setStyleSheet(f"color:{d_color}; font-size:11px; font-weight:bold; background:rgba(0,0,0,0.3); padding:4px 10px; border-radius:5px;")
            bottom_row.addWidget(deadline_label)
            lp_color = '#9C6DFF' if g.get('unlocked') else '#888888'
            lp_label = QLabel(f"💎 {g.get('large_points', 3)} LP")
            lp_label.setStyleSheet(f"color:{lp_color}; font-size:11px; font-weight:bold; background:rgba(0,0,0,0.3); padding:4px 10px; border-radius:5px;")
            bottom_row.addWidget(lp_label); bottom_row.addStretch()
            if g.get('unlocked'):
                progress = safe_int(g.get('progress', 0))
                if g.get('completed'):
                    done_label = QLabel("✅ COMPLETED")
                    done_label.setStyleSheet("color:#35FF99; font-size:13px; font-weight:bold; background:rgba(53,255,153,0.2); padding:6px 15px; border-radius:8px;")
                    bottom_row.addWidget(done_label)
                else:
                    prog_text = QLabel(f"{progress}/10"); prog_text.setStyleSheet("color:#FFD54A; font-size:13px; font-weight:bold;"); bottom_row.addWidget(prog_text)
                    progress_bar = AnimatedProgressBar(color=COLORS['gold']); progress_bar.setRange(0, 10); progress_bar.setValue(progress); progress_bar.setFixedSize(100, 16)
                    bottom_row.addWidget(progress_bar)
                    plus_btn = NeonButton("+1", COLORS['green']); plus_btn.setFixedSize(40, 35); plus_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
                    plus_btn.clicked.connect(lambda checked, idx=i: self.complete_goal_progress(idx)); bottom_row.addWidget(plus_btn)
            else:
                lock_label = QLabel("🔒 LOCKED"); lock_label.setStyleSheet("color:#888888; font-size:12px; font-weight:bold; background:rgba(100,100,100,0.2); padding:6px 15px; border-radius:8px;")
                bottom_row.addWidget(lock_label)
            main_layout.addLayout(bottom_row); self.mg_layout.addWidget(card)

    # ═══════════════════════ ANALYTICS ═══════════════════════
    def create_analytics_page(self):
        page = QWidget(); page.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(page); layout.setContentsMargins(15, 15, 15, 15); layout.setSpacing(8)
        header = QHBoxLayout()
        back_btn = NeonButton("← BACK", COLORS['cyan']); back_btn.setFixedWidth(110); back_btn.clicked.connect(self.go_back)
        header.addWidget(back_btn)
        title = QLabel("📊 ANALYTICS DASHBOARD"); title.setStyleSheet("color:#00D8FF;font-family:Orbitron;font-size:22px;font-weight:bold;")
        title.setAlignment(Qt.AlignCenter); header.addWidget(title); header.addStretch(); layout.addLayout(header)
        p = self.data['player']; rank = self.get_rank(safe_int(p['xp']))
        stats_grid = QGridLayout(); stats_grid.setSpacing(10)
        stats_data = [
            ("Level", str(p['level']), COLORS['cyan']), ("Rank", rank['name'], COLORS['gold']),
            ("Total XP", str(safe_int(p['total_xp'])), COLORS['green']), ("Power", str(p['power']), COLORS['orange']),
            ("Strength", str(safe_int(p.get('strength', 10))), COLORS['red']), ("Gold", str(safe_int(p['gold'])), COLORS['gold']),
            ("Streak", str(safe_int(p['streak'])), COLORS['red']), ("Discipline", str(safe_int(p['discipline_score'])), COLORS['blue']),
        ]
        for i, (label, value, color) in enumerate(stats_data):
            card = GlassPanel(); card.custom_color = QColor(color.red(), color.green(), color.blue(), 35)
            cl = QVBoxLayout(card); cl.setAlignment(Qt.AlignCenter)
            lbl = QLabel(label); lbl.setStyleSheet(f"color:{color.name()};font-size:11px;"); lbl.setAlignment(Qt.AlignCenter); cl.addWidget(lbl)
            val = QLabel(value); val.setStyleSheet("color:#FFFFFF;font-size:20px;font-weight:bold;"); val.setAlignment(Qt.AlignCenter); cl.addWidget(val)
            dot = QLabel("●"); dot.setStyleSheet(f"color:{color.name()};font-size:8px;"); dot.setAlignment(Qt.AlignCenter); cl.addWidget(dot)
            stats_grid.addWidget(card, i // 4, i % 4)
        layout.addLayout(stats_grid)
        attr_card = GlassPanel(); al = QVBoxLayout(attr_card)
        al_title = QLabel("📊 ATTRIBUTE DISTRIBUTION"); al_title.setStyleSheet("color:#00D8FF;font-size:16px;font-weight:bold;"); al.addWidget(al_title)
        for stat in ['STR', 'AGI', 'VIT', 'INT', 'PER']:
            row = QHBoxLayout()
            name = QLabel(f"{STAT_ICONS[stat]} {STAT_NAMES[stat]}:"); name.setStyleSheet(f"color:{STAT_COLORS[stat]};font-size:13px;font-weight:bold;"); name.setFixedWidth(130); row.addWidget(name)
            bar = AnimatedProgressBar(color=QColor(STAT_COLORS[stat])); bar.setRange(0, 100)
            stat_value = safe_int(p['stats'].get(stat, 0)); bar.setValue(stat_value); bar.setFixedHeight(14); row.addWidget(bar)
            val = QLabel(str(stat_value)); val.setStyleSheet("color:#FFFFFF;font-size:13px;font-weight:bold;"); val.setFixedWidth(35); val.setAlignment(Qt.AlignCenter); row.addWidget(val)
            al.addLayout(row)
        layout.addWidget(attr_card)
        points_card = GlassPanel(); pl = QVBoxLayout(points_card)
        points_title = QLabel("💎 POINT SYSTEM"); points_title.setStyleSheet("color:#FFD54A;font-size:16px;font-weight:bold;"); pl.addWidget(points_title)
        points_info = [
            ("🎯 Small Points (SP)", str(safe_int(p.get('small_points', 0))), "5 SP per quest"),
            ("💎 Large Points (LP)", str(safe_int(p.get('large_points', 0))), "100 SP = 1 LP"),
            ("⬆️ Level Up", str(p['level']), "5 LP = 1 Level"),
            ("💢 Strength", str(safe_int(p.get('strength', 10))), "Increases with quests"),
        ]
        for label, value, desc in points_info:
            row = QHBoxLayout()
            lbl = QLabel(f"{label}: {value}"); lbl.setStyleSheet("color:#E0E0E0;font-size:13px;font-weight:bold;"); row.addWidget(lbl)
            dsc = QLabel(desc); dsc.setStyleSheet("color:#44E8FF;font-size:11px;"); dsc.setAlignment(Qt.AlignRight); row.addWidget(dsc)
            pl.addLayout(row)
        layout.addWidget(points_card); layout.addStretch()
        return page

    # ═══════════════════════ MENTAL / PHYSICAL / SPIRITUAL ═══════════════════════
    def create_mental_page(self):
        page = QWidget(); page.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(page); layout.setContentsMargins(15, 15, 15, 15); layout.setSpacing(10)
        back_btn = NeonButton("← BACK", COLORS['cyan']); back_btn.setFixedWidth(110); back_btn.clicked.connect(self.go_back); layout.addWidget(back_btn)
        title = QLabel("🧠 MENTAL FORTRESS"); title.setStyleSheet("color:#9C6DFF;font-family:Orbitron;font-size:22px;font-weight:bold;"); title.setAlignment(Qt.AlignCenter); layout.addWidget(title)
        val = safe_int(self.data['player']['stats']['INT'])
        card = GlassPanel(); card.custom_color = QColor(156, 109, 255, 35); cl = QVBoxLayout(card)
        label = QLabel(f"Intelligence: {val}/100"); label.setStyleSheet("color:#9C6DFF;font-size:18px;font-weight:bold;"); label.setAlignment(Qt.AlignCenter); cl.addWidget(label)
        bar = AnimatedProgressBar(color=QColor('#9C6DFF')); bar.setRange(0, 100); bar.setValue(val); bar.setFixedHeight(16); cl.addWidget(bar); layout.addWidget(card)
        activities = [("🧘 Deep Meditation", "15 min", 3, 'INT'), ("📚 Intensive Reading", "30 min", 3, 'INT'), ("✍️ Journal Writing", "20 min", 2, 'INT'), ("🎯 Focus Training", "25 min", 3, 'PER'), ("🧩 Puzzle Solving", "20 min", 2, 'INT')]
        for name, desc, pts, attr in activities:
            card = GlassPanel(); card.custom_color = QColor(156, 109, 255, 30); cl = QHBoxLayout(card)
            cl.addWidget(QLabel("🧠")); cl.addWidget(QLabel(f"<b style='color:#E0E0E0;'>{name}</b>")); cl.addWidget(QLabel(f"<span style='color:#44E8FF;'>{desc} • +{pts} XP</span>")); cl.addStretch()
            btn = NeonButton("DO IT", COLORS['purple']); btn.setFixedWidth(90); btn.clicked.connect(lambda checked, p=pts, a=attr: self.complete_activity(p, a)); cl.addWidget(btn); layout.addWidget(card)
        layout.addStretch(); return page

    def create_physical_page(self):
        page = QWidget(); page.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(page); layout.setContentsMargins(15, 15, 15, 15); layout.setSpacing(10)
        back_btn = NeonButton("← BACK", COLORS['cyan']); back_btn.setFixedWidth(110); back_btn.clicked.connect(self.go_back); layout.addWidget(back_btn)
        title = QLabel("💪 PHYSICAL MIGHT"); title.setStyleSheet("color:#35FF99;font-family:Orbitron;font-size:22px;font-weight:bold;"); title.setAlignment(Qt.AlignCenter); layout.addWidget(title)
        val = safe_int(self.data['player']['stats']['STR'])
        card = GlassPanel(); card.custom_color = QColor(53, 255, 153, 35); cl = QVBoxLayout(card)
        label = QLabel(f"Strength: {val}/100"); label.setStyleSheet("color:#35FF99;font-size:18px;font-weight:bold;"); label.setAlignment(Qt.AlignCenter); cl.addWidget(label)
        bar = AnimatedProgressBar(color=QColor('#35FF99')); bar.setRange(0, 100); bar.setValue(val); bar.setFixedHeight(16); cl.addWidget(bar); layout.addWidget(card)
        activities = [("🏋️ Morning Workout", "30 min", 3, 'STR'), ("🏃 Cardio Run", "20 min", 3, 'AGI'), ("⚔️ Katana Training", "30 min", 4, 'AGI'), ("🏋️ Night Training", "45 min", 4, 'STR'), ("🤸 Stretching", "15 min", 2, 'AGI')]
        for name, desc, pts, attr in activities:
            card = GlassPanel(); card.custom_color = QColor(53, 255, 153, 30); cl = QHBoxLayout(card)
            cl.addWidget(QLabel("💪")); cl.addWidget(QLabel(f"<b style='color:#E0E0E0;'>{name}</b>")); cl.addWidget(QLabel(f"<span style='color:#44E8FF;'>{desc} • +{pts} XP</span>")); cl.addStretch()
            btn = NeonButton("DO IT", COLORS['green']); btn.setFixedWidth(90); btn.clicked.connect(lambda checked, p=pts, a=attr: self.complete_activity(p, a)); cl.addWidget(btn); layout.addWidget(card)
        layout.addStretch(); return page

    def create_spiritual_page(self):
        page = QWidget(); page.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(page); layout.setContentsMargins(15, 15, 15, 15); layout.setSpacing(10)
        back_btn = NeonButton("← BACK", COLORS['cyan']); back_btn.setFixedWidth(110); back_btn.clicked.connect(self.go_back); layout.addWidget(back_btn)
        title = QLabel("🕉️ SPIRITUAL AWAKENING"); title.setStyleSheet("color:#FFA927;font-family:Orbitron;font-size:22px;font-weight:bold;"); title.setAlignment(Qt.AlignCenter); layout.addWidget(title)
        val = safe_int(self.data['player']['stats']['PER'])
        card = GlassPanel(); card.custom_color = QColor(255, 169, 39, 35); cl = QVBoxLayout(card)
        label = QLabel(f"Perception: {val}/100"); label.setStyleSheet("color:#FFA927;font-size:18px;font-weight:bold;"); label.setAlignment(Qt.AlignCenter); cl.addWidget(label)
        bar = AnimatedProgressBar(color=QColor('#FFA927')); bar.setRange(0, 100); bar.setValue(val); bar.setFixedHeight(16); cl.addWidget(bar); layout.addWidget(card)
        activities = [("🧘 Morning Meditation", "20 min", 3, 'PER'), ("🙏 Gratitude Practice", "10 min", 2, 'PER'), ("🌅 Visualization", "15 min", 3, 'PER'), ("🕯️ Breathing Exercise", "10 min", 2, 'VIT'), ("🌿 Nature Walk", "20 min", 3, 'PER')]
        for name, desc, pts, attr in activities:
            card = GlassPanel(); card.custom_color = QColor(255, 169, 39, 30); cl = QHBoxLayout(card)
            cl.addWidget(QLabel("🕉️")); cl.addWidget(QLabel(f"<b style='color:#E0E0E0;'>{name}</b>")); cl.addWidget(QLabel(f"<span style='color:#44E8FF;'>{desc} • +{pts} XP</span>")); cl.addStretch()
            btn = NeonButton("DO IT", COLORS['orange']); btn.setFixedWidth(90); btn.clicked.connect(lambda checked, p=pts, a=attr: self.complete_activity(p, a)); cl.addWidget(btn); layout.addWidget(card)
        layout.addStretch(); return page

    def complete_activity(self, pts, attr):
        p = self.data['player']
        p['stats'][attr] = min(100, safe_int(p['stats'][attr]) + 1)
        p['xp'] = safe_int(p['xp']) + pts; p['total_xp'] = safe_int(p['total_xp']) + pts
        p['power'] = 100 + safe_int(p['xp']) + safe_int(p.get('strength', 10)) * 2
        p['small_points'] = safe_int(p.get('small_points', 0)) + pts
        if p['small_points'] >= 100: p['large_points'] = safe_int(p.get('large_points', 0)) + 1; p['small_points'] -= 100; sound_manager.play('levelup')
        self.save_data(); self.check_achievements(); sound_manager.play('success'); self.speak(f"+{pts} XP!"); self.update_all_pages()

    # ═══════════════════════ ACHIEVEMENTS ═══════════════════════
    def create_achievements_page(self):
        page = QWidget(); page.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(page); layout.setContentsMargins(15, 15, 15, 15); layout.setSpacing(8)
        header = QHBoxLayout()
        back_btn = NeonButton("← BACK", COLORS['cyan']); back_btn.setFixedWidth(110); back_btn.clicked.connect(self.go_back); header.addWidget(back_btn)
        title = QLabel("🏆 ACHIEVEMENTS"); title.setStyleSheet("color:#FFD54A;font-family:Orbitron;font-size:22px;font-weight:bold;"); title.setAlignment(Qt.AlignCenter); header.addWidget(title)
        unlocked_count = sum(1 for a in self.data['achievements'] if a['unlocked']); total = len(ACHIEVEMENTS)
        progress = QLabel(f"{unlocked_count}/{total} unlocked"); progress.setStyleSheet("color:#35FF99;font-size:14px;font-weight:bold;"); header.addWidget(progress); layout.addLayout(header)
        scroll = QScrollArea(); scroll.setStyleSheet("background:transparent;border:none;"); scroll.setWidgetResizable(True)
        container = QWidget(); container.setStyleSheet("background:transparent;"); grid = QGridLayout(container); grid.setSpacing(10)
        for i, ach in enumerate(ACHIEVEMENTS):
            unlocked = any(a['name'] == ach['name'] and a['unlocked'] for a in self.data['achievements'])
            card = GlassPanel(); card.custom_color = QColor(255, 213, 74, 40) if unlocked else QColor(100, 100, 100, 35)
            card.setFixedSize(220, 110); cl = QVBoxLayout(card); cl.setAlignment(Qt.AlignCenter); cl.setSpacing(4)
            icon = QLabel("🏆" if unlocked else "🔒"); icon.setStyleSheet("font-size:28px;"); icon.setAlignment(Qt.AlignCenter); cl.addWidget(icon)
            name = QLabel(ach['name']); name.setStyleSheet(f"color:{'#FFD54A' if unlocked else '#666666'};font-size:12px;font-weight:bold;"); name.setAlignment(Qt.AlignCenter); cl.addWidget(name)
            desc = QLabel(ach['desc']); desc.setStyleSheet(f"color:{'#E0E0E0' if unlocked else '#666666'};font-size:10px;"); desc.setAlignment(Qt.AlignCenter); desc.setWordWrap(True); cl.addWidget(desc)
            cat = QLabel(ach['category']); cat.setStyleSheet(f"color:{'#44E8FF' if unlocked else '#666666'};font-size:9px;"); cat.setAlignment(Qt.AlignCenter); cl.addWidget(cat)
            grid.addWidget(card, i // 4, i % 4)
        scroll.setWidget(container); layout.addWidget(scroll); return page

    # ═══════════════════════ SHOP ═══════════════════════
    def create_shop_page(self):
        page = QWidget(); page.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(page); layout.setContentsMargins(15, 15, 15, 15); layout.setSpacing(10)
        header = QHBoxLayout()
        back_btn = NeonButton("← BACK", COLORS['cyan']); back_btn.setFixedWidth(110); back_btn.clicked.connect(self.go_back); header.addWidget(back_btn)
        title = QLabel("🛒 SHOP"); title.setStyleSheet("color:#FFD54A;font-family:Orbitron;font-size:22px;font-weight:bold;"); title.setAlignment(Qt.AlignCenter); header.addWidget(title); header.addStretch(); layout.addLayout(header)
        gold_card = GlassPanel(); gold_card.custom_color = QColor(255, 215, 0, 30); gold_cl = QHBoxLayout(gold_card)
        gold_label = QLabel(f"💰 Available Gold: {safe_int(self.data['player']['gold'])}"); gold_label.setStyleSheet("color:#FFD700;font-size:18px;font-weight:bold;"); gold_label.setAlignment(Qt.AlignCenter); gold_cl.addWidget(gold_label); layout.addWidget(gold_card)
        items = [
            ("💊 Health Potion", "Restore vitality", 30, 'VIT', 5, 'Common'), ("🧪 Mana Potion", "Boost intelligence", 25, 'INT', 5, 'Common'),
            ("💪 Strength Elixir", "+10 STR", 100, 'STR', 10, 'Rare'), ("⚡ Agility Elixir", "+10 AGI", 100, 'AGI', 10, 'Rare'),
            ("❤️ Vitality Elixir", "+10 VIT", 100, 'VIT', 10, 'Rare'), ("🧠 Intelligence Elixir", "+10 INT", 100, 'INT', 10, 'Rare'),
            ("👁️ Perception Elixir", "+10 PER", 100, 'PER', 10, 'Rare'), ("👑 Ultimate Elixir", "+5 ALL STATS", 500, 'ALL', 5, 'Legendary'),
        ]
        for name, desc, price, attr, boost, rarity in items:
            card = GlassPanel(); rarity_colors = {'Common': '#44E8FF', 'Rare': '#9C6DFF', 'Legendary': '#FFD54A'}
            card.custom_color = QColor(QColor(rarity_colors.get(rarity, '#44E8FF')).red(), QColor(rarity_colors.get(rarity, '#44E8FF')).green(), QColor(rarity_colors.get(rarity, '#44E8FF')).blue(), 30)
            cl = QHBoxLayout(card); info = QVBoxLayout(); info.setSpacing(2)
            info.addWidget(QLabel(f"<b style='color:{rarity_colors.get(rarity, '#E0E0E0')};'>{name}</b>"))
            info.addWidget(QLabel(f"<span style='color:#E0E0E0;'>{desc} (+{boost} {attr})</span>"))
            info.addWidget(QLabel(f"<span style='color:{rarity_colors.get(rarity, '#44E8FF')};font-size:10px;'>{rarity}</span>"))
            cl.addLayout(info); cl.addStretch()
            can_afford = safe_int(self.data['player']['gold']) >= price
            btn = NeonButton(f"🪙 {price}", COLORS['gold'] if can_afford else COLORS['red']); btn.setFixedWidth(90)
            if can_afford: btn.clicked.connect(lambda checked, p=price, a=attr, b=boost: self.buy_item(p, a, b))
            btn.setEnabled(can_afford); cl.addWidget(btn); layout.addWidget(card)
        layout.addStretch(); return page

    # ═══════════════════════ REVIEWS ═══════════════════════
    def create_reviews_page(self):
        page = QWidget(); page.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(page); layout.setContentsMargins(15, 15, 15, 15); layout.setSpacing(10)
        header = QHBoxLayout()
        back_btn = NeonButton("← BACK", COLORS['cyan']); back_btn.setFixedWidth(110); back_btn.clicked.connect(self.go_back); header.addWidget(back_btn)
        title = QLabel("📝 REVIEW SYSTEM"); title.setStyleSheet("color:#FFD54A;font-family:Orbitron;font-size:22px;font-weight:bold;"); title.setAlignment(Qt.AlignCenter); header.addWidget(title); header.addStretch(); layout.addLayout(header)
        tabs = QTabWidget(); tabs.setStyleSheet("QTabWidget::pane { background:transparent; border:1px solid #00D8FF; border-radius:10px; } QTabBar::tab { background:rgba(15,23,42,180); color:#E0E0E0; padding:10px 25px; border:1px solid #00D8FF; border-radius:8px; margin:3px; font-weight:bold; } QTabBar::tab:selected { background:#00D8FF; color:#06080F; }")
        weekly_tab = QWidget(); weekly_layout = QVBoxLayout(weekly_tab)
        weekly_label = QLabel("📅 Weekly Review"); weekly_label.setStyleSheet("color:#00D8FF;font-size:18px;font-weight:bold;"); weekly_layout.addWidget(weekly_label)
        today = datetime.now(); week_start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
        logs = self.db.get_weekly_log(week_start); total_xp = sum(log[3] for log in logs) if logs else 0; quests_done = len(logs) if logs else 0
        weekly_summary = GlassPanel(); wsl = QVBoxLayout(weekly_summary)
        wsl.addWidget(QLabel(f"Week: {week_start} - {today.strftime('%Y-%m-%d')}")); wsl.addWidget(QLabel(f"Total XP Earned: {total_xp}"))
        wsl.addWidget(QLabel(f"Quests Completed: {quests_done}")); wsl.addWidget(QLabel(f"Current Streak: {safe_int(self.data['player']['streak'])} days"))
        wsl.addWidget(QLabel(f"Best Streak: {safe_int(self.data['player']['best_streak'])} days")); weekly_layout.addWidget(weekly_summary); weekly_layout.addStretch()
        monthly_tab = QWidget(); monthly_layout = QVBoxLayout(monthly_tab)
        monthly_label = QLabel("📊 Monthly Review"); monthly_label.setStyleSheet("color:#9C6DFF;font-size:18px;font-weight:bold;"); monthly_layout.addWidget(monthly_label)
        p = self.data['player']; monthly_summary = GlassPanel(); msl = QVBoxLayout(monthly_summary)
        msl.addWidget(QLabel(f"Month: {today.strftime('%B %Y')}")); msl.addWidget(QLabel(f"Level: {p['level']}")); msl.addWidget(QLabel(f"Rank: {p['rank']}"))
        msl.addWidget(QLabel(f"Total XP: {safe_int(p['total_xp'])}")); msl.addWidget(QLabel(f"Goals Completed: {safe_int(p.get('goals_completed', 0))}"))
        msl.addWidget(QLabel(f"Gold: {safe_int(p['gold'])}")); monthly_layout.addWidget(monthly_summary); monthly_layout.addStretch()
        yearly_tab = QWidget(); yearly_layout = QVBoxLayout(yearly_tab)
        yearly_label = QLabel("🎯 Yearly Review"); yearly_label.setStyleSheet("color:#FFD54A;font-size:18px;font-weight:bold;"); yearly_layout.addWidget(yearly_label)
        yearly_summary = GlassPanel(); ysl = QVBoxLayout(yearly_summary)
        ysl.addWidget(QLabel(f"Year: {today.year}")); ysl.addWidget(QLabel(f"Level: {p['level']}")); ysl.addWidget(QLabel(f"Rank: {p['rank']}"))
        ysl.addWidget(QLabel(f"Total XP: {safe_int(p['total_xp'])}")); ysl.addWidget(QLabel(f"Best Streak: {safe_int(p['best_streak'])} days"))
        ysl.addWidget(QLabel(f"Achievements: {sum(1 for a in self.data['achievements'] if a['unlocked'])}/{len(ACHIEVEMENTS)}"))
        ysl.addWidget(QLabel(f"Total Quests: {safe_int(p['completed_quests'])}")); yearly_layout.addWidget(yearly_summary); yearly_layout.addStretch()
        tabs.addTab(weekly_tab, "📅 Weekly"); tabs.addTab(monthly_tab, "📊 Monthly"); tabs.addTab(yearly_tab, "🎯 Yearly"); layout.addWidget(tabs)
        return page

    # ═══════════════════════ PROFILE ═══════════════════════
    def create_profile_page(self):
        page = QWidget(); page.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(page); layout.setContentsMargins(15, 15, 15, 15); layout.setSpacing(10)
        back_btn = NeonButton("← BACK", COLORS['cyan']); back_btn.setFixedWidth(110); back_btn.clicked.connect(self.go_back); layout.addWidget(back_btn)
        p = self.data['player']
        card = GlassPanel(); cl = QVBoxLayout(card); cl.setAlignment(Qt.AlignCenter); cl.setSpacing(10)
        self.profile_pic_btn = QPushButton(); self.profile_pic_btn.setFixedSize(120, 120)
        self.profile_pic_btn.setStyleSheet("border:3px solid #FFD54A;border-radius:60px;font-size:60px;"); self.profile_pic_btn.clicked.connect(self.upload_profile_pic)
        if p.get('profile_pic') and os.path.exists(p['profile_pic']):
            icon = QIcon(p['profile_pic']); self.profile_pic_btn.setIcon(icon); self.profile_pic_btn.setIconSize(QSize(110, 110))
        else: self.profile_pic_btn.setText("👤")
        cl.addWidget(self.profile_pic_btn, alignment=Qt.AlignCenter)
        self.prof_name = QLabel(p['name']); self.prof_name.setStyleSheet("color:#FFD54A;font-size:26px;font-weight:bold;"); self.prof_name.setAlignment(Qt.AlignCenter); cl.addWidget(self.prof_name)
        self.prof_title = QLabel(p.get('title', 'Hunter')); self.prof_title.setStyleSheet("color:#9C6DFF;font-size:16px;"); self.prof_title.setAlignment(Qt.AlignCenter); cl.addWidget(self.prof_title)
        layout.addWidget(card)
        stats_card = GlassPanel(); sl = QVBoxLayout(stats_card); sl.setSpacing(8); sl.addWidget(QLabel("📊 ATTRIBUTES"))
        for stat in ['STR', 'AGI', 'VIT', 'INT', 'PER']:
            row = QHBoxLayout(); row.addWidget(QLabel(f"{STAT_ICONS[stat]} {STAT_NAMES[stat]}:"))
            bar = AnimatedProgressBar(color=QColor(STAT_COLORS[stat])); bar.setRange(0, 100); bar.setValue(safe_int(p['stats'][stat])); bar.setFixedHeight(14); row.addWidget(bar)
            row.addWidget(QLabel(str(safe_int(p['stats'][stat])))); sl.addLayout(row)
        layout.addWidget(stats_card); layout.addStretch(); return page

    def update_profile_page(self):
        if hasattr(self, 'prof_name'):
            p = self.data['player']; self.prof_name.setText(p['name']); self.prof_title.setText(p.get('title', 'Hunter'))
            if p.get('profile_pic') and os.path.exists(p['profile_pic']):
                icon = QIcon(p['profile_pic']); self.profile_pic_btn.setIcon(icon); self.profile_pic_btn.setIconSize(QSize(110, 110)); self.profile_pic_btn.setText("")
            else: self.profile_pic_btn.setText("👤"); self.profile_pic_btn.setIcon(QIcon())

    # ═══════════════════════ SETTINGS ═══════════════════════
    def create_settings_page(self):
        page = QWidget(); page.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(page); layout.setContentsMargins(15, 15, 15, 15); layout.setSpacing(10)
        back_btn = NeonButton("← BACK", COLORS['cyan']); back_btn.setFixedWidth(110); back_btn.clicked.connect(self.go_back); layout.addWidget(back_btn)
        title = QLabel("⚙️ SETTINGS"); title.setStyleSheet("color:#00D8FF;font-family:Orbitron;font-size:22px;font-weight:bold;"); title.setAlignment(Qt.AlignCenter); layout.addWidget(title)
        voice_status = QLabel(f"🎤 Voice Control: {'ACTIVE' if self.is_voice_active else 'OFF'} - Say 'help' to learn commands")
        voice_status.setStyleSheet("color:#44E8FF;font-size:12px;background:rgba(68,232,255,0.1);padding:10px;border-radius:8px;"); layout.addWidget(voice_status)
        settings = [("👤 Change Name", self.change_name), ("🖼️ Upload Profile Picture", self.upload_profile_pic), ("🎤 Toggle Voice Commands", self.toggle_voice), ("💾 Force Save Data", self.save_data), ("🔄 Reset All Progress", self.reset_progress), ("ℹ️ About This App", self.show_about)]
        for text, func in settings:
            card = GlassPanel(); cl = QHBoxLayout(card)
            lbl = QLabel(text); lbl.setStyleSheet("color:#E0E0E0;font-size:14px;font-weight:bold;"); cl.addWidget(lbl); cl.addStretch()
            btn = NeonButton("→", COLORS['blue']); btn.setFixedWidth(50); btn.clicked.connect(func); cl.addWidget(btn); layout.addWidget(card)
        layout.addStretch()
        version = QLabel("SOLO LEVELING SV17 HYBRID ULTIMATE - VOICE CONTROL\nCreated by Ashiq Hussain © 2024"); version.setStyleSheet("color:#44E8FF;font-size:11px;"); version.setAlignment(Qt.AlignCenter); layout.addWidget(version)
        return page

    def change_name(self):
        dialog = QDialog(self); dialog.setStyleSheet("QDialog{background:#0D1B2A;} QLabel{color:#E0E0E0;}"); dialog.setWindowTitle("Change Name"); dialog.setFixedSize(350, 150)
        layout = QVBoxLayout(dialog); layout.addWidget(QLabel("Enter new name:"))
        entry = QLineEdit(self.data['player']['name']); entry.setStyleSheet("background:#06080F;color:#E0E0E0;border:1px solid #00D8FF;border-radius:5px;padding:10px;"); layout.addWidget(entry)
        btn_layout = QHBoxLayout()
        save_btn = NeonButton("SAVE", COLORS['green']); save_btn.clicked.connect(lambda: self.save_name(entry.text(), dialog)); btn_layout.addWidget(save_btn)
        cancel_btn = NeonButton("CANCEL", COLORS['red']); cancel_btn.clicked.connect(dialog.reject); btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout); dialog.exec()

    def save_name(self, name, dialog):
        if name.strip(): self.data['player']['name'] = name.strip(); self.save_data(); self.update_all_pages(); dialog.accept(); self.speak(f"Name changed to {name}")

    def reset_progress(self):
        msg = QMessageBox(); msg.setStyleSheet("QMessageBox{background:#0D1B2A;color:#E0E0E0;}"); msg.setWindowTitle("⚠️ Reset")
        msg.setText("Reset all progress? This cannot be undone!"); msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if msg.exec() == QMessageBox.Yes:
            try: os.remove('solo_sv17_final.db'); os.remove('solo_sv17_final.json')
            except: pass
            self.data = self.create_default_data(); self.initialize_data(); self.save_data(); self.update_all_pages(); self.speak("Progress reset")

    def show_about(self):
        msg = QMessageBox(); msg.setStyleSheet("QMessageBox{background:#0D1B2A;color:#E0E0E0;}"); msg.setWindowTitle("About")
        msg.setText("<div style='text-align:center;'><h2 style='color:#FFD54A;'>⚔️ SOLO LEVELING</h2><h3 style='color:#00D8FF;'>SV17 HYBRID ULTIMATE</h3><p style='color:#44E8FF;'>🎤 VOICE CONTROL EDITION</p><p style='color:#9C6DFF;'>Created by: Ashiq Hussain</p><p style='color:#35FF99;'>Features:</p><p style='color:#E0E0E0;font-size:11px;'>• E to MONARCH Rank System<br>• Small Points (5 SP/quest) → Large Points (100 SP = 1 LP)<br>• Level Up: 5 LP = 1 Level<br>• 5 Core Attributes (STR, AGI, VIT, INT, PER)<br>• Daily Quest with Penalty System<br>• Main Goals with Deadline Countdown<br>• Achievement System (24 achievements)<br>• Weekly/Monthly/Yearly Reviews<br>• Voice Commands<br>• Shop System with Rarity<br>• Profile Picture Upload<br>• Sound Effects & Animations<br>• SQLite Database + JSON backup</p><p style='color:#445;font-size:10px;'>© 2024 All Rights Reserved</p></div>")
        msg.exec()

# ============================================
# ENTRY POINT
# ============================================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet("QToolTip { background:#0D1B2A; color:#E0E0E0; border:1px solid #00D8FF; padding:5px; border-radius:5px; } QScrollBar:vertical { background:transparent; width:8px; } QScrollBar::handle:vertical { background:#00D8FF; border-radius:4px; min-height:25px; } QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; } QScrollBar:horizontal { background:transparent; height:8px; } QScrollBar::handle:horizontal { background:#00D8FF; border-radius:4px; min-width:25px; } QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width:0; }")
    def start_app():
        window = SoloLevelingSV17()
        window.show()
    splash = SplashScreen(on_enter_callback=start_app)
    sys.exit(app.exec())