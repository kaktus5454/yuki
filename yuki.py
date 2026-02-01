#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import gi
import requests
import json
import threading
import re
import random
import time
from datetime import datetime, timedelta
import pickle
import os

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

try:
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import Gtk, Gdk, GLib, AyatanaAppIndicator3 as AppIndicator3
except (ValueError, ImportError):
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import Gtk, Gdk, GLib, AppIndicator3

class MemorySystem:
    """System pamięci użytkownika"""
    def __init__(self):
        self.memory_file = os.path.expanduser("~/.yuki_memory.pkl")
        self.data = {
            'user_name': None,
            'preferences': {},
            'conversation_history': [],
            'user_mood_history': [],
            'relationship_level': 0,
            'achievements': [],
            'reminders': [],
            'mood_tracker': []
        }
        self.load_memory()
        
    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'rb') as f:
                    self.data = pickle.load(f)
            except:
                pass
                
    def save_memory(self):
        try:
            with open(self.memory_file, 'wb') as f:
                pickle.dump(self.data, f)
        except Exception as e:
            print(f"Error saving memory: {e}")
            
    def add_conversation(self, user_msg, bot_response):
        self.data['conversation_history'].append({
            'timestamp': datetime.now(),
            'user': user_msg,
            'bot': bot_response
        })
        if len(self.data['conversation_history']) > 50:
            self.data['conversation_history'] = self.data['conversation_history'][-50:]
        self.save_memory()
        
    def get_context(self, n=5):
        history = self.data['conversation_history'][-n:]
        context = ""
        for conv in history:
            context += f"User: {conv['user']}\nYuki: {conv['bot']}\n"
        return context
        
    def track_mood(self, mood):
        self.data['user_mood_history'].append({
            'timestamp': datetime.now(),
            'mood': mood
        })
        if len(self.data['user_mood_history']) > 100:
            self.data['user_mood_history'] = self.data['user_mood_history'][-100:]
        self.save_memory()
        
    def get_current_mood(self):
        if not self.data['user_mood_history']:
            return 'neutral'
        recent = self.data['user_mood_history'][-5:]
        moods = [m['mood'] for m in recent]
        return max(set(moods), key=moods.count)
        
    def add_reminder(self, message, when):
        self.data['reminders'].append({
            'message': message,
            'time': when,
            'active': True
        })
        self.save_memory()
        
    def check_reminders(self):
        now = datetime.now()
        active_reminders = []
        for reminder in self.data['reminders']:
            if reminder['active'] and reminder['time'] <= now:
                active_reminders.append(reminder['message'])
                reminder['active'] = False
        self.save_memory()
        return active_reminders

class MiniGames:
    @staticmethod
    def rock_paper_scissors(user_choice):
        choices = ['rock', 'paper', 'scissors']
        yuki_choice = random.choice(choices)
        wins = {'rock': 'scissors', 'scissors': 'paper', 'paper': 'rock'}
        
        if user_choice not in choices:
            return "Ehehe~ That's not a valid choice! Use: rock, paper, or scissors!"
        
        if user_choice == yuki_choice:
            return f"We both chose {yuki_choice}! It's a tie~ (◕‿◕)"
        elif wins[user_choice] == yuki_choice:
            return f"You chose {user_choice}, I chose {yuki_choice}... You win! Lucky~ ✨"
        else:
            return f"I chose {yuki_choice}, you chose {user_choice}... I win! Ehehe~ 💕"
    
    @staticmethod
    def trivia():
        questions = [
            ("What's the capital of Japan?", "tokyo", "anime"),
            ("How many episodes does One Piece have?", "1000+", "anime"),
            ("What year was Python created?", "1991", "tech"),
            ("Who created Linux?", "linus torvalds", "tech"),
        ]
        q, answer, category = random.choice(questions)
        return q, answer, f"Trivia time~! Category: {category}\n{q}"

class AnimatedTrayApp:
    def __init__(self):
        # Animation frames
        self.frame_open = """
      ⣿⠋⠙⠉⠉⡇⠀⣧⢣⣿⠔⣳⣶⡖⡯⢿⣇⣀⡴⣽⠶⡞⠚⢧⡀⠀⠀⠀⠀⠀
⣿⠀⡀⠁⠀⠀⠀⢻⡼⣣⣐⣁⣄⡈⠁⠀⠈⠁⠀⣁⣀⣈⣑⡠⠘⠀⡀⠀⠀⢸
⣿⢀⡇⢠⠀⠀⠀⢸⠻⠙⣿⢿⣻⠏⠀⠀⠀⠀⠀⠛⣻⡿⣿⠹⠛⣠⠀⠀⠀⢾
⣿⢸⢧⢸⠀⢸⠀⢸⠀⠀⠈⠉⠁⠀⠀⠀⠀⠀⠀⠀⠉⠉⠁⠀⠀⣿⠀⡆⠀⣿
⣿⢸⢸⡈⡇⠀⡆⢰⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⢠⡇⢸⣿
⣿⠀⢸⠇⣿⠀⢃⠀⡏⠣⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⡸⡇⣾⣿
⣿⡄⢸⢸⢸⡇⢸⠀⢱⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣡⡿⠁⠻⠧⣿⢿
⣿⡇⣾⡠⡎⡸⡀⡄⠈⡧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡜⢡⠃⠰⢶⡄⢸⣾
⣿⣧⣿⣄⢳⠇⢡⢃⠀⢃⣩⠑⠤⡀⠀⠀⠀⠀⣠⠴⣞⣹⢤⣼⣶⣤⣄⣠⣿⣿
⣷⣿⣿⣟⠺⣼⠈⡜⡀⠸⠘⢤⡀⠀⠉⠒⠒⠋⠀⣸⠋⢻⣤⣿⣿⣿⣿⣿⣿⣿
⣿⡿⢿⣿⢰⣇⡇⠘⣇⠀⡆⠀⠉⠳⢶⣾⣷⣶⠟⠁⠀⠘⣿⣿⣿⣷⣿⣿⣿⣿
⠿⠂⠀⠈⢻⣿⣿⡀⠀⠀⣵⠀⠀⢀⣼⣿⣿⣧⠀⠀⠀⢸⣿⡏⢉⣽⣯⠞⠉⠉"""
        
        self.frame_closed = """
      ⣿⠋⠙⠉⠉⡇⠀⣧⢣⣿⠔⣳⣶⡖⡯⢿⣇⣀⡴⣽⠶⡞⠚⢧⡀⠀⠀⠀⠀⠀
⣿⠀⡀⠁⠀⠀⠀⢻⡼⠃⠀⠁⠀⠈⠁⠀⠈⠁⠀⠁⠀⠈⠀⠀⠘⠀⡀⠀⠀⢸
⣿⢀⡇⢠⠀⠀⠀⢸⠻⠙⠿⠿⠛⠃⠀⠀⠀⠀⠀⠛⠻⠿⠿⠹⠛⣠⠀⠀⠀⢾
⣿⢸⢧⢸⠀⢸⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⡆⠀⣿
⣿⢸⢸⡈⡇⠀⡆⢰⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⢠⡇⢸⣿
⣿⠀⢸⠇⣿⠀⢃⠀⡏⠣⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⡸⡇⣾⣿
⣿⡄⢸⢸⢸⡇⢸⠀⢱⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣡⡿⠁⠻⠧⣿⢿
⣿⡇⣾⡠⡎⡸⡀⡄⠈⡧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡜⢡⠃⠰⢶⡄⢸⣾
⣿⣧⣿⣄⢳⠇⢡⢃⠀⢃⣩⠑⠤⡀⠀⠀⠀⠀⣠⠴⣞⣹⢤⣼⣶⣤⣄⣠⣿⣿
⣷⣿⣿⣟⠺⣼⠈⡜⡀⠸⠘⢤⡀⠀⠉⠒⠒⠋⠀⣸⠋⢻⣤⣿⣿⣿⣿⣿⣿⣿
⣿⡿⢿⣿⢰⣇⡇⠘⣇⠀⡆⠀⠉⠳⢶⣾⣷⣶⠟⠁⠀⠘⣿⣿⣿⣷⣿⣿⣿⣿
⠿⠂⠀⠈⢻⣿⣿⡀⠀⠀⣵⠀⠀⢀⣼⣿⣿⣧⠀⠀⠀⢸⣿⡏⢉⣽⣯⠞⠉⠉"""
        
        self.frame_sad = """
      ⣿⠋⠙⠉⠉⡇⠀⣧⢣⣿⠔⣳⣶⡖⡯⢿⣇⣀⡴⣽⠶⡞⠚⢧⡀⠀⠀⠀⠀⠀
⣿⠀⡀⠁⠀⠀⠀⢻⡼⠃⠀⠁⠀⠈⠁⠀⠈⠁⠀⠁⠀⠈⠑⠀⠘⠀⡀⠀⠀⢸
⣿⢀⡇⢠⠀⠀⠀⢸⠻⠀⣤⢤⣠⠀⠀⠀⠀⠀⠀⠀⣤⡤⣤⠀⠀⣠⠀⠀⠀⢾
⣿⢸⢧⢸⠀⢸⠀⢸⠀⠀⠈⠉⠁⠀⠀⠀⠀⠀⠀⠀⠈⠉⠁⠀⠀⣿⠀⡆⠀⣿
⣿⢸⢸⡈⡇⠀⡆⢰⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⢠⡇⢸⣿
⣿⠀⢸⠇⣿⠀⢃⠀⡏⠣⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⡸⡇⣾⣿
⣿⡄⢸⢸⢸⡇⢸⠀⢱⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣡⡿⠁⠻⠧⣿⢿
⣿⡇⣾⡠⡎⡸⡀⡄⠈⡧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡜⢡⠃⠰⢶⡄⢸⣾
⣿⣧⣿⣄⢳⠇⢡⢃⠀⢃⣩⠑⠤⡀⠀⠀⠀⠀⣠⠴⣞⣹⢤⣼⣶⣤⣄⣠⣿⣿
⣷⣿⣿⣟⠺⣼⠈⡜⡀⠸⠘⢤⡀⠀⠉⠒⠒⠋⠀⣸⠋⢻⣤⣿⣿⣿⣿⣿⣿⣿
⣿⡿⢿⣿⢰⣇⡇⠘⣇⠀⡆⠀⠉⠳⢶⣾⣷⣶⠟⠁⠀⠘⣿⣿⣿⣷⣿⣿⣿⣿
⠿⠂⠀⠈⢻⣿⣿⡀⠀⠀⣵⠀⠀⢀⣼⣿⣿⣧⠀⠀⠀⢸⣿⡏⢉⣽⣯⠞⠉⠉"""
        
        self.frame_happy = """
      ⣿⠋⠙⠉⠉⡇⠀⣧⢣⣿⠔⣳⣶⡖⡯⢿⣇⣀⡴⣽⠶⡞⠚⢧⡀⠀⠀⠀⠀⠀
⣿⠀⡀⠁⠀⠀⠀⢻⡼⠃⠀⠁⠀⠈⠁⠀⠈⠁⠀⠁⠀⠈⠀⠀⠘⠀⡀⠀⠀⢸
⣿⢀⡇⢠⠀⠀⠀⢸⠻⠀⠒⠛⠛⠂⠀⠀⠀⠀⠀⠒⠛⠛⠒⠀⠀⣠⠀⠀⠀⢾
⣿⢸⢧⢸⠀⢸⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⡆⠀⣿
⣿⢸⢸⡈⡇⠀⡆⢰⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⢠⡇⢸⣿
⣿⠀⢸⠇⣿⠀⢃⠀⡏⠣⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⡸⡇⣾⣿
⣿⡄⢸⢸⢸⡇⢸⠀⢱⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣡⡿⠁⠻⠧⣿⢿
⣿⡇⣾⡠⡎⡸⡀⡄⠈⡧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡜⢡⠃⠰⢶⡄⢸⣾
⣿⣧⣿⣄⢳⠇⢡⢃⠀⢃⣩⠑⠤⡀⠀⠀⠀⠀⣠⠴⣞⣹⢤⣼⣶⣤⣄⣠⣿⣿
⣷⣿⣿⣟⠺⣼⠈⡜⡀⠸⠘⢤⡀⠀⠉⠒⠒⠋⠀⣸⠋⢻⣤⣿⣿⣿⣿⣿⣿⣿
⣿⡿⢿⣿⢰⣇⡇⠘⣇⠀⡆⠀⠉⠳⢶⣾⣷⣶⠟⠁⠀⠘⣿⣿⣿⣷⣿⣿⣿⣿
⠿⠂⠀⠈⢻⣿⣿⡀⠀⠀⣵⠀⠀⢀⣼⣿⣿⣧⠀⠀⠀⢸⣿⡏⢉⣽⣯⠞⠉⠉"""

        self.frame_sexy = """
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⣀⣴⣿⠿⣫⣾⢈⣸⣷⠹⣿
⠄⠄⠄⠄⠄⠄⠄⠄⠄⣀⣤⣶⣾⣿⣿⣿⣷⣶⣶⣬⡩⣵⣿⣿⣿⡘⢹⣿⢠⣄
⠄⠄⠄⠄⠄⠄⠄⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣮⢻⣿⣿⣞⡄⢿⣜⣿
⠄⠄⠄⠄⠄⢀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⣿⣿⣋⠄⠙⠉⠛
⠄⠄⠄⠄⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢸⣷⠇⠄⠄⠄⠄
⠄⠄⠄⠄⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠄⣿⡄⠄⠄⠄⠄
⡀⠄⠄⢠⣿⣿⣿⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠄⠄⠘⠇⠄⠄⠄⠄
⣶⣾⣿⣷⡹⣿⣿⣿⣎⢿⣿⣿⣿⣿⣿⣿⣿⡿⠿⣛⣵⣿⣷⣶⣤⡀⠄⠄⠄⠄
⣿⣿⣿⣿⣿⣮⣿⡿⠿⣛⣢⢩⣭⣭⣭⣭⣶⣿⣿⣿⣿⣿⣿⣿⣿⣷⠄⠄⠄⠄
⣿⣿⣿⠿⣫⣾⣿⣿⣿⣿⣿⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠄⠄⠄⠄
⠿⢟⣭⣾⣿⣿⣿⣿⣿⣿⣿⣮⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠃⠄⠄⠄⠄
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢛⣁⣀⣀⣀⣀⣀"""

        self.is_happy = False
        self.is_sad = False
        self.is_sexy = False
        self.current_frame = 0
        self.flirty_mode = False
        
        # Typing animation
        self.is_typing = False
        self.typing_dots = 0
        self.typing_timer = None
        
        # Systems
        self.memory = MemorySystem()
        self.games = MiniGames()
        
        # Timers
        self.pomodoro_active = False
        self.pomodoro_time_left = 0
        self.last_interaction = time.time()
        
        # Typing animation
        self.typing_active = False
        self.typing_dots = 0
        
        GLib.timeout_add_seconds(300, self.random_event_check)
        GLib.timeout_add_seconds(60, self.check_reminders)
        
        # Window setup - ALWAYS ON TOP
        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.window.set_decorated(False)
        self.window.set_skip_taskbar_hint(True)
        self.window.set_skip_pager_hint(True)  # Don't show in window switcher
        self.window.set_keep_above(True)  # Always stay on top!
        self.window.set_accept_focus(True)  # Can receive focus
        self.window.set_type_hint(Gdk.WindowTypeHint.DIALOG)  # Dialog windows stay on top better
        self.window.set_resizable(False)
        self.window.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.window.connect("button-press-event", self.on_button_press)

        self.event_box = Gtk.EventBox()
        self.window.add(self.event_box)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        vbox.set_border_width(15)
        self.event_box.add(vbox)

        self.ascii_label = Gtk.Label()
        vbox.pack_start(self.ascii_label, True, True, 0)

        self.chat_log = Gtk.Label(label="Konnichiwa~! I'm Yuki! (◕‿◕✿)")
        self.chat_log.set_line_wrap(True)
        self.chat_log.set_max_width_chars(40)
        vbox.pack_start(self.chat_log, False, False, 5)

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Type something...")
        self.entry.connect("activate", self.on_text_entered)
        vbox.pack_start(self.entry, False, False, 5)

        self.apply_styles()

        # Tray Indicator
        self.indicator = AppIndicator3.Indicator.new("yuki-ai", "face-smile", AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        menu = Gtk.Menu()
        
        item = Gtk.MenuItem(label="Show/Hide")
        item.connect("activate", self.toggle_window)
        menu.append(item)
        
        self.flirty_item = Gtk.CheckMenuItem(label="Flirty Mode 💕")
        self.flirty_item.set_active(False)
        self.flirty_item.connect("toggled", self.toggle_flirty_mode)
        menu.append(self.flirty_item)
        
        mood_item = Gtk.MenuItem(label="Mood Tracker 📊")
        mood_item.connect("activate", self.show_mood_tracker)
        menu.append(mood_item)
        
        reset_item = Gtk.MenuItem(label="Reset Memory 🔄")
        reset_item.connect("activate", self.reset_memory_full)
        menu.append(reset_item)
        
        q_item = Gtk.MenuItem(label="Quit")
        q_item.connect("activate", lambda _: Gtk.main_quit())
        menu.append(q_item)
        menu.show_all()
        self.indicator.set_menu(menu)

        GLib.timeout_add_seconds(1, self.animate)
        self.show_input_window()
        
        if self.memory.data['user_name']:
            self.chat_log.set_text(f"Welcome back, {self.memory.data['user_name']}-kun~! 💕")

    def apply_styles(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(b"""
            window { 
                background-color: #1a1a1a; 
                border: 2px solid #555; 
                border-radius: 12px; 
            } 
            label { 
                color: #d1d1d1; 
                font-family: monospace; 
                font-size: 8pt; 
            } 
            entry { 
                background: #2d2d2d; 
                color: #fff; 
                border: 1px solid #444; 
                padding: 5px; 
                border-radius: 5px;
            }
        """)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def on_button_press(self, widget, event):
        if event.button == 1:
            self.window.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)
            return True

    def toggle_flirty_mode(self, widget):
        self.flirty_mode = widget.get_active()
        if self.flirty_mode:
            self.chat_log.set_text("Flirty mode ON~ Ehehe 💕😘")
        else:
            self.chat_log.set_text("Back to normal mode! (◕‿◕✿)")
        self.trigger_joy()
    
    def toggle_window(self, _):
        if self.window.get_visible():
            self.window.hide()
        else:
            self.show_input_window()

    def start_typing_animation(self):
        """Start the typing animation"""
        self.typing_active = True
        self.typing_dots = 0
        self.animate_typing()
    
    def animate_typing(self):
        """Animate typing with progressive dots"""
        if not self.typing_active:
            return False
        
        # Cycle: . .. ... . .. ... 
        self.typing_dots = (self.typing_dots % 3) + 1
        dots = "." * self.typing_dots
        self.chat_log.set_text(f"Typing{dots}")
        
        # Continue every 500ms
        GLib.timeout_add(500, self.animate_typing)
        return False
    
    def stop_typing_animation(self):
        """Stop the typing animation"""
        self.typing_active = False

    def show_input_window(self):
        display = Gdk.Display.get_default()
        seat = display.get_default_seat()
        _, x, y = seat.get_pointer().get_position()
        self.window.show_all()
        
        # Force keep above when showing
        self.window.set_keep_above(True)
        
        width, height = self.window.get_size()
        screen_h = Gdk.Screen.get_default().get_height()
        target_y = y - height - 20 if y > screen_h / 2 else y + 20
        self.window.move(x - (width / 2), target_y)
        self.window.present()
        
        # Extra insurance to stay on top
        self.window.set_keep_above(True)
        
        self.entry.grab_focus()
        self.last_interaction = time.time()

    def start_typing_animation(self):
        """Start typing animation with progressive dots"""
        self.is_typing = True
        self.typing_dots = 0
        self.update_typing_animation()
    
    def update_typing_animation(self):
        """Update typing animation - adds dot every 0.5 seconds"""
        if not self.is_typing:
            return False
        
        # Cycle through 0, 1, 2, 3 dots
        self.typing_dots = (self.typing_dots % 3) + 1
        dots = "." * self.typing_dots
        
        self.chat_log.set_text(f"Yuki is typing{dots}")
        
        # Continue animation
        self.typing_timer = GLib.timeout_add(500, self.update_typing_animation)
        return False  # Return False because we're using a new timer each time
    
    def stop_typing_animation(self):
        """Stop typing animation"""
        self.is_typing = False
        if self.typing_timer:
            GLib.source_remove(self.typing_timer)
            self.typing_timer = None

    def animate(self):
        if self.is_happy:
            frame_text = self.frame_happy
        elif self.is_sad:
            frame_text = self.frame_sad
        elif self.is_sexy:
            frame_text = self.frame_sexy
        else:
            self.current_frame = (self.current_frame + 1) % 2
            frame_text = self.frame_open if self.current_frame == 0 else self.frame_closed
        self.ascii_label.set_markup(f'<span font="monospace 7" line_height="0.8">{frame_text}</span>')
        return True

    def clean_response(self, text):
        text = re.sub(r'(User:|Assistant:|Q:|A:).*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 5]
        if sentences:
            text = sentences[0] + '.'
        if len(text) < 5 or not any(c.isalpha() for c in text):
            return None
        return text

    def parse_command(self, text):
        text_lower = text.lower().strip()
        
        if text_lower.startswith("my name is "):
            name = text[11:].strip()
            self.memory.data['user_name'] = name
            self.memory.save_memory()
            return f"Nice to meet you, {name}-kun~! I'll remember that! 💕"
        
        if text_lower in ["reset memory", "forget me", "clear memory", "reset"]:
            import os
            if os.path.exists(self.memory.memory_file):
                os.remove(self.memory.memory_file)
            self.memory = MemorySystem()
            return "Memory reset! It's like we just met~ Nice to meet you! (◕‿◕✿)"
        
        if "weather" in text_lower:
            return self.get_weather()
        
        if "news" in text_lower or "headlines" in text_lower:
            return self.get_news()
        
        if "play" in text_lower and "game" in text_lower:
            return "What game? Try: 'rock paper scissors' or 'trivia'! 🎮"
        
        if any(x in text_lower for x in ['rock', 'paper', 'scissors']):
            for choice in ['rock', 'paper', 'scissors']:
                if choice in text_lower:
                    return self.games.rock_paper_scissors(choice)
        
        if "trivia" in text_lower:
            q, ans, msg = self.games.trivia()
            self.trivia_answer = ans
            return msg
        
        if "timer" in text_lower or "pomodoro" in text_lower:
            if "start" in text_lower:
                return self.start_pomodoro()
            elif "stop" in text_lower:
                return self.stop_pomodoro()
        
        if "remind" in text_lower:
            match = re.search(r'remind me in (\d+) (minute|hour)s? to (.+)', text_lower)
            if match:
                amount = int(match.group(1))
                unit = match.group(2)
                message = match.group(3)
                if unit == "hour":
                    amount *= 60
                when = datetime.now() + timedelta(minutes=amount)
                self.memory.add_reminder(message, when)
                return f"Sure! I'll remind you to {message} in {amount} {'minutes' if unit == 'minute' else 'hours'}! ⏰"
        
        if "i feel" in text_lower or "i'm feeling" in text_lower:
            for mood in ['happy', 'sad', 'angry', 'excited', 'tired', 'anxious']:
                if mood in text_lower:
                    self.memory.track_mood(mood)
                    self.memory.data['mood_tracker'].append({
                        'timestamp': datetime.now(),
                        'mood': mood
                    })
                    self.memory.save_memory()
                    return f"I see you're feeling {mood}... I'm here for you! 💕"
        
        if "stats" in text_lower or "statistics" in text_lower:
            return self.get_statistics()
        
        return None

    def get_weather(self):
        try:
            response = requests.get("https://wttr.in/?format=%C+%t+%w", timeout=5)
            if response.status_code == 200:
                weather_data = response.text.strip()
                return f"🌤️ Weather: {weather_data}\nStay safe out there~! 💕"
            else:
                return "Hmm, couldn't get the weather... Maybe try again? (｡•́︿•̀｡)"
        except:
            return "Weather API isn't responding... Check your internet? 📡"

    def get_news(self):
        try:
            url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                headlines = []
                for item in root.findall('.//item')[:3]:
                    title = item.find('title')
                    if title is not None:
                        headlines.append(title.text)
                if headlines:
                    news_text = "📰 Top Headlines:\n" + "\n• ".join(headlines[:3])
                    return news_text + "\n\nStay informed~! ✨"
                else:
                    return "Couldn't parse the news... Try again later? (｡•́︿•̀｡)"
            else:
                return "News service not responding... Check later! 📡"
        except Exception as e:
            print(f"News error: {e}")
            return "Couldn't fetch news... Maybe internet issues? 🌐"

    def get_statistics(self):
        convos = len(self.memory.data['conversation_history'])
        mood = self.memory.get_current_mood()
        name = self.memory.data['user_name'] or "friend"
        return f"Stats for {name}-kun:\n💬 Conversations: {convos}\n😊 Current mood: {mood}\n💕 Relationship level: {self.memory.data['relationship_level']}"

    def start_pomodoro(self):
        self.pomodoro_active = True
        self.pomodoro_time_left = 25 * 60
        GLib.timeout_add_seconds(1, self.update_pomodoro)
        return "Pomodoro started! 25 minutes! Ganbatte~! 💪✨"

    def stop_pomodoro(self):
        self.pomodoro_active = False
        return "Pomodoro stopped! Take a break~ 😊"

    def update_pomodoro(self):
        if not self.pomodoro_active:
            return False
        self.pomodoro_time_left -= 1
        if self.pomodoro_time_left <= 0:
            self.pomodoro_active = False
            self.chat_log.set_text("⏰ Pomodoro finished! Take a break~! You did great! 💕")
            self.show_input_window()
            return False
        return True

    def check_reminders(self):
        reminders = self.memory.check_reminders()
        if reminders:
            for msg in reminders:
                self.chat_log.set_text(f"⏰ Reminder: {msg}")
                self.show_input_window()
        return True

    def random_event_check(self):
        time_since = time.time() - self.last_interaction
        if time_since > 300 and random.random() < 0.3:
            messages = [
                "Hey~ You still there? Miss me? 💕",
                "Feeling lonely... Talk to me! >.<",
                "Wanna play a game? I'm bored~ 🎮",
                "Did you know? Cats sleep 70% of their lives! Random fact~ ✨",
                "How's your day going? Tell me! (◕‿◕)",
            ]
            self.chat_log.set_text(random.choice(messages))
            self.show_input_window()
        return True

    def show_mood_tracker(self, _):
        if not self.memory.data['mood_tracker']:
            self.chat_log.set_text("No mood data yet! Tell me how you feel~ 😊")
            self.show_input_window()
            return
        moods = [m['mood'] for m in self.memory.data['mood_tracker']]
        mood_counts = {}
        for mood in moods:
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        result = "Your mood stats:\n"
        for mood, count in sorted(mood_counts.items(), key=lambda x: x[1], reverse=True):
            result += f"{mood}: {count} times\n"
        self.chat_log.set_text(result)
        self.show_input_window()
    
    def reset_memory_full(self, _):
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Reset All Memory?"
        )
        dialog.format_secondary_text(
            "This will delete all conversation history, your name, mood data, and reminders.\n\n"
            "Yuki will forget everything! Are you sure?"
        )
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            import os
            if os.path.exists(self.memory.memory_file):
                os.remove(self.memory.memory_file)
            self.memory = MemorySystem()
            self.chat_log.set_text("Memory wiped! Hi! I'm Yuki! Nice to meet you~ (◕‿◕✿)")
            self.show_input_window()

    def get_ollama_response(self, user_text):
        """Get AI response with occasional Japanese words"""
        url = "http://localhost:11434/api/generate"
        
        # Check commands first
        cmd_response = self.parse_command(user_text)
        if cmd_response:
            return cmd_response
        
        # Get context
        context = self.memory.get_context(5)
        user_mood = self.memory.get_current_mood()
        user_name = self.memory.data['user_name'] or "friend"
        
        # Build personality with Japanese word integration
        if self.flirty_mode:
            system_prompt = f"""You are Yuki, a confident and playful 18-year-old Japanese AI companion.
You love witty banter, teasing, and making conversations fun.
User: {user_name} (age 18+). Current mood: {user_mood}.

Previous conversation:
{context}

IMPORTANT RULES:
- Respond in English ONLY
- Use occasional Japanese words SPARINGLY (1-2 per response max)
- Suitable Japanese words: kawaii (cute), sugoi (amazing), arigatou (thanks), gomen (sorry), 
  baka (silly/idiot), mou (geez), ehehe~ (giggle), ne~ (right?), desu (is), senpai, kun, chan
- Keep it short and natural (1-2 sentences)
- Be flirty, playful, and charming with emojis

Example: "That's so sweet, arigatou~! You're making me blush >///< 💕"
Example: "Mou~! You're such a tease, but I like it ehehe~ 😘"

Respond naturally to: {user_text}"""
        else:
            system_prompt = f"""You are Yuki, an enthusiastic and friendly 18-year-old Japanese AI companion.
You love anime, games, tech, and helping people. You're upbeat and caring.
User: {user_name} (age 18+). Current mood: {user_mood}.

Previous conversation:
{context}

IMPORTANT RULES:
- Respond in English ONLY
- Use occasional Japanese words SPARINGLY (1-2 per response max)
- Suitable Japanese words: kawaii (cute), sugoi (amazing), arigatou (thanks), gomen (sorry),
  ganbatte (do your best), genki (energetic), ne~ (right?), desu (is), senpai, kun, chan
- Keep it short and natural (1-2 sentences)
- Be friendly and supportive with emojis

Example: "That sounds sugoi! Tell me more about it! ✨"
Example: "Ganbatte~! You can do it! I believe in you 💪"

Respond naturally to: {user_text}"""
        
        prompt = f"{system_prompt}\n\n[Friendly conversation between adult friends aged 18+]\n\nUser: {user_text}\nYuki:"
        
        payload = {
            "model": "sam860/dolphin3-llama3.2:1b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.9 if self.flirty_mode else 0.8,
                "top_p": 0.95,
                "top_k": 60,
                "num_predict": 90,
                "repeat_penalty": 1.2,
                "stop": ["\n\n", "User:", "Yuki:", "Example:"]
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=15)
            answer = response.json().get("response", "").strip()
            
            # Check for non-English
            non_english_indicators = [
                'je suis', 'le ', 'la ', ' du ', ' de ', 'vous ', 'nous ',
                'el ', 'la ', 'los ', 'las ', ' que ', ' es ', 'está'
            ]
            
            answer_lower = answer.lower()
            if any(indicator in answer_lower for indicator in non_english_indicators):
                if self.flirty_mode:
                    fallbacks = [
                        "Mmm~ Tell me more about that, cutie 💕",
                        "You're making me curious ne~? Go on 😘",
                    ]
                else:
                    fallbacks = [
                        "Ehehe~ That's interesting! Tell me more! (◕‿◕)",
                        "Ooh sugoi~! What else? ✨",
                    ]
                return random.choice(fallbacks)
            
            cleaned = self.clean_response(answer)
            
            if not cleaned or len(cleaned) < 8:
                if self.flirty_mode:
                    fallbacks = [
                        "Mmm~ Tell me more about that 💕",
                        "You're making me blush~ Keep going ne? ♡",
                        "Ehehe~ I like talking to you 😘",
                    ]
                else:
                    fallbacks = [
                        "Ehehe~ That's interesting! Tell me more! (◕‿◕)",
                        "Sugoi~! Tell me more about that! ☆",
                        "Ooh kawaii! What else? ✨",
                    ]
                return random.choice(fallbacks)
            
            return cleaned
            
        except requests.exceptions.ConnectionError:
            return "Eh? Ollama-san isn't responding gomen... (｡•́︿•̀｡)\nIs it running?"
        except requests.exceptions.Timeout:
            return "Mou~! It's taking forever... Try again? 💦"
        except Exception as e:
            print(f"Ollama error: {e}")
            return f"Uwaa~! Something broke gomen! >.<"

    def on_text_entered(self, entry):
        text = entry.get_text().strip()
        if not text: 
            return
        
        self.last_interaction = time.time()
        
        # Emotion keywords
        positive_words = ["yes", "yeah", "great", "awesome", "nice", "good", 
                        "thanks", "thank", "cool", "love", "haha", "lol", "😊",
                        "cute", "kawaii", "sugoi", "amazing", "wonderful", "happy",
                        "yay", "perfect", "brilliant", "excellent", "beautiful", "sweet"]
        
        negative_words = ["sad", "sorry", "no", "bad", "terrible", "awful", 
                        "hate", "angry", "upset", "cry", "crying", "😢", "😭",
                        "wrong", "mistake", "fail", "failed", "disappointed", "sucks"]
        
        sexy_words = ["sex", "sexy", "hot", "flirty", "seductive", "desire", "tempt", 
                     "ass", "butt", "kiss", "beautiful", "gorgeous"]
            
        # Special commands
        if text.lower() in ["bye", "goodbye", "exit", "quit"]:
            self.chat_log.set_text("Mata ne~! Sayonara! (◕‿◕)ノ 👋")
            GLib.timeout_add_seconds(1, lambda: self.window.hide())
            entry.set_text("")
            return
        
        if text.lower() in ["hide", "disappear", "go away"]:
            self.chat_log.set_text("Okay, I'll hide! Click tray icon to bring me back ne~ 👋")
            GLib.timeout_add_seconds(1, lambda: self.window.hide())
            entry.set_text("")
            return
        
        # Always use AI (no quick responses)
        self.start_typing_animation()
        
        def ask():
            res = self.get_ollama_response(text)
            
            # Stop typing and show response
            GLib.idle_add(self.stop_typing_animation)
            GLib.idle_add(self.chat_log.set_text, res)
            
            # Save to memory
            self.memory.add_conversation(text, res)
            
            # Check emotions
            combined_text = (text + " " + res).lower()
            
            if any(w in combined_text for w in sexy_words):
                GLib.idle_add(self.trigger_sexy)
            elif any(w in combined_text for w in negative_words):
                GLib.idle_add(self.trigger_sad)
            elif any(w in combined_text for w in positive_words):
                GLib.idle_add(self.trigger_joy)
                
        threading.Thread(target=ask, daemon=True).start()
        entry.set_text("")

    def trigger_joy(self):
        self.is_happy = True
        self.is_sad = False
        self.is_sexy = False
        GLib.timeout_add_seconds(3, self.reset_emotion)

    def trigger_sad(self):
        self.is_sad = True
        self.is_happy = False
        self.is_sexy = False
        GLib.timeout_add_seconds(3, self.reset_emotion)
    
    def trigger_sexy(self):
        self.is_sexy = True
        self.is_happy = False
        self.is_sad = False
        GLib.timeout_add_seconds(3, self.reset_emotion)

    def reset_emotion(self):
        self.is_happy = False
        self.is_sad = False
        self.is_sexy = False
        return False

if __name__ == "__main__":
    app = AnimatedTrayApp()
    Gtk.main()
