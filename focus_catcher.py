#!/usr/bin/env python3
"""
Focus Catcher - Visual Attention Game
A therapeutic game to improve selective attention and impulse control
"""

import pygame
import random
import math
import json
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from enum import Enum
from dataclasses import dataclass, asdict
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
COLORS = {
    'background': (102, 126, 234),
    'purple': (118, 75, 162),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (255, 107, 107),
    'green': (78, 205, 196),
    'blue': (69, 183, 209),
    'yellow': (249, 202, 36),
    'orange': (240, 147, 43),
    'gray': (149, 165, 166),
    'dark_gray': (127, 140, 141),
    'light_gray': (189, 195, 199),
}

# Game States
class GameState(Enum):
    MENU = "menu"
    LEVEL_SELECT = "level_select"
    PLAYING = "playing"
    PAUSED = "paused"
    PROGRESS = "progress"

# Object Types
class ObjectType(Enum):
    STAR = "star"
    BALLOON = "balloon"
    HEART = "heart"
    CIRCLE = "circle"
    TRIANGLE = "triangle"

@dataclass
class LevelConfig:
    level: int
    name: str
    description: str
    target_type: ObjectType
    distractor_types: List[ObjectType]
    spawn_rate: float  # objects per second
    object_lifespan: int  # milliseconds
    target_ratio: float  # 0-1, ratio of targets to total objects
    max_objects: int
    required_correct_clicks: int
    max_incorrect_clicks: int
    background_speed: float
    time_limit: Optional[int] = None  # seconds

@dataclass
class GameSession:
    id: str
    level: int
    start_time: float
    end_time: Optional[float] = None
    correct_clicks: int = 0
    incorrect_clicks: int = 0
    total_targets: int = 0
    reaction_times: List[float] = None
    accuracy: float = 0.0
    average_reaction_time: float = 0.0

    def __post_init__(self):
        if self.reaction_times is None:
            self.reaction_times = []

@dataclass
class LevelProgress:
    level: int
    best_accuracy: float = 0.0
    best_reaction_time: float = 0.0
    times_played: int = 0
    last_played: float = 0.0

class GameObject:
    def __init__(self, obj_type: ObjectType, x: float, y: float, is_target: bool, spawn_time: float, lifespan: int = 3000):
        self.id = f"obj_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
        self.type = obj_type
        self.x = x
        self.y = y
        self.is_target = is_target
        self.spawn_time = spawn_time
        self.lifespan = lifespan
        
        # Size and appearance
        base_size = 60
        size_variation = 20
        self.size = base_size + (random.random() - 0.5) * size_variation
        
        # Colors
        target_colors = [COLORS['red'], COLORS['green'], COLORS['blue'], COLORS['yellow'], COLORS['orange']]
        distractor_colors = [COLORS['gray'], COLORS['dark_gray'], COLORS['light_gray']]
        self.color = random.choice(target_colors if is_target else distractor_colors)
        
        # Movement
        max_velocity = 50
        self.velocity_x = (random.random() - 0.5) * max_velocity
        self.velocity_y = (random.random() - 0.5) * max_velocity
        
        # Animation
        self.rotation = 0
        self.rotation_speed = (random.random() - 0.5) * 4
        self.scale = 1.0
        self.scale_direction = 1
        
    def update(self, delta_time: float):
        # Update position
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        
        # Update rotation
        self.rotation += self.rotation_speed * delta_time
        
        # Update scale (breathing effect)
        self.scale += self.scale_direction * delta_time * 0.5
        if self.scale > 1.2:
            self.scale = 1.2
            self.scale_direction = -1
        elif self.scale < 0.8:
            self.scale = 0.8
            self.scale_direction = 1
    
    def draw(self, screen: pygame.Surface):
        center_x = int(self.x + self.size / 2)
        center_y = int(self.y + self.size / 2)
        scaled_size = int(self.size * self.scale)
        
        if self.type == ObjectType.STAR:
            self._draw_star(screen, center_x, center_y, scaled_size // 2)
        elif self.type == ObjectType.BALLOON:
            self._draw_balloon(screen, center_x, center_y, scaled_size // 2)
        elif self.type == ObjectType.HEART:
            self._draw_heart(screen, center_x, center_y, scaled_size // 2)
        elif self.type == ObjectType.CIRCLE:
            self._draw_circle(screen, center_x, center_y, scaled_size // 2)
        elif self.type == ObjectType.TRIANGLE:
            self._draw_triangle(screen, center_x, center_y, scaled_size // 2)
    
    def _draw_star(self, screen: pygame.Surface, x: int, y: int, radius: int):
        points = []
        spikes = 5
        outer_radius = radius
        inner_radius = radius * 0.4
        
        for i in range(spikes * 2):
            angle = (i * math.pi) / spikes
            r = outer_radius if i % 2 == 0 else inner_radius
            px = x + math.cos(angle) * r
            py = y + math.sin(angle) * r
            points.append((px, py))
        
        pygame.draw.polygon(screen, self.color, points)
        if self.is_target:
            pygame.draw.polygon(screen, COLORS['white'], points, 3)
    
    def _draw_balloon(self, screen: pygame.Surface, x: int, y: int, radius: int):
        # Balloon body
        pygame.draw.ellipse(screen, self.color, (x - radius, y - radius, radius * 2, radius * 2))
        if self.is_target:
            pygame.draw.ellipse(screen, COLORS['white'], (x - radius, y - radius, radius * 2, radius * 2), 3)
        
        # Balloon string
        pygame.draw.line(screen, COLORS['black'], (x, y + radius), (x, y + radius + 20), 2)
    
    def _draw_heart(self, screen: pygame.Surface, x: int, y: int, size: int):
        # Simplified heart shape using circles and polygon
        heart_points = [
            (x, y + size // 4),
            (x - size // 2, y - size // 4),
            (x - size // 2, y),
            (x - size // 4, y - size // 4),
            (x, y - size // 8),
            (x + size // 4, y - size // 4),
            (x + size // 2, y),
            (x + size // 2, y - size // 4),
            (x, y + size // 2)
        ]
        pygame.draw.polygon(screen, self.color, heart_points)
        if self.is_target:
            pygame.draw.polygon(screen, COLORS['white'], heart_points, 3)
    
    def _draw_circle(self, screen: pygame.Surface, x: int, y: int, radius: int):
        pygame.draw.circle(screen, self.color, (x, y), radius)
        if self.is_target:
            pygame.draw.circle(screen, COLORS['white'], (x, y), radius, 3)
    
    def _draw_triangle(self, screen: pygame.Surface, x: int, y: int, size: int):
        height = int(size * math.sqrt(3) / 2)
        points = [
            (x, y - height // 2),
            (x - size // 2, y + height // 2),
            (x + size // 2, y + height // 2)
        ]
        pygame.draw.polygon(screen, self.color, points)
        if self.is_target:
            pygame.draw.polygon(screen, COLORS['white'], points, 3)
    
    def is_point_inside(self, px: int, py: int) -> bool:
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        distance = math.sqrt((px - center_x) ** 2 + (py - center_y) ** 2)
        return distance <= (self.size / 2) * self.scale
    
    def is_expired(self, current_time: float) -> bool:
        return (current_time - self.spawn_time) > self.lifespan

class FocusCatcherGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Focus Catcher - Visual Attention Game")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.game_state = GameState.MENU
        self.current_level = 1
        self.current_session: Optional[GameSession] = None
        self.sessions: List[GameSession] = []
        self.level_progress: List[LevelProgress] = []
        self.game_score = 0
        self.lives = 3
        
        # Game objects
        self.game_objects: List[GameObject] = []
        self.last_spawn_time = 0
        self.background_offset = 0
        self.game_time = 0
        self.start_time = 0
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Level configurations
        self.level_configs = self._create_level_configs()
        
        # Load saved data
        self._load_saved_data()
    
    def _create_level_configs(self) -> List[LevelConfig]:
        return [
            LevelConfig(1, "Star Gazing", "Click only the bright stars!", ObjectType.STAR, 
                       [ObjectType.CIRCLE], 0.5, 4000, 0.7, 3, 10, 3, 0),
            LevelConfig(2, "Balloon Pop", "Pop the red balloons only!", ObjectType.BALLOON,
                       [ObjectType.CIRCLE, ObjectType.TRIANGLE], 0.7, 3500, 0.6, 4, 12, 3, 10),
            LevelConfig(3, "Heart Hunt", "Find the hearts among the shapes!", ObjectType.HEART,
                       [ObjectType.STAR, ObjectType.CIRCLE, ObjectType.TRIANGLE], 0.8, 3000, 0.5, 5, 15, 4, 15),
            LevelConfig(4, "Shape Shifter", "Quick! Click the triangles!", ObjectType.TRIANGLE,
                       [ObjectType.STAR, ObjectType.CIRCLE, ObjectType.HEART, ObjectType.BALLOON], 1.0, 2800, 0.4, 6, 18, 4, 20),
            LevelConfig(5, "Circle Challenge", "Focus on circles only!", ObjectType.CIRCLE,
                       [ObjectType.STAR, ObjectType.TRIANGLE, ObjectType.HEART, ObjectType.BALLOON], 1.2, 2500, 0.35, 7, 20, 5, 25),
            LevelConfig(6, "Speed Stars", "Catch the fast-moving stars!", ObjectType.STAR,
                       [ObjectType.CIRCLE, ObjectType.TRIANGLE, ObjectType.HEART, ObjectType.BALLOON], 1.5, 2200, 0.3, 8, 22, 5, 30),
            LevelConfig(7, "Balloon Bonanza", "Pop balloons in the chaos!", ObjectType.BALLOON,
                       [ObjectType.STAR, ObjectType.CIRCLE, ObjectType.TRIANGLE, ObjectType.HEART], 1.8, 2000, 0.25, 9, 25, 6, 35),
            LevelConfig(8, "Heart Rush", "Find hearts in the storm!", ObjectType.HEART,
                       [ObjectType.STAR, ObjectType.CIRCLE, ObjectType.TRIANGLE, ObjectType.BALLOON], 2.0, 1800, 0.2, 10, 28, 6, 40),
            LevelConfig(9, "Triangle Tornado", "Triangles in the whirlwind!", ObjectType.TRIANGLE,
                       [ObjectType.STAR, ObjectType.CIRCLE, ObjectType.HEART, ObjectType.BALLOON], 2.5, 1600, 0.18, 12, 30, 7, 45),
            LevelConfig(10, "Master Focus", "Ultimate attention challenge!", ObjectType.STAR,
                       [ObjectType.CIRCLE, ObjectType.TRIANGLE, ObjectType.HEART, ObjectType.BALLOON], 3.0, 1400, 0.15, 15, 35, 8, 50, 60),
        ]
    
    def _load_saved_data(self):
        try:
            if os.path.exists('focus_game_sessions.json'):
                with open('focus_game_sessions.json', 'r') as f:
                    data = json.load(f)
                    self.sessions = [GameSession(**session) for session in data]
            
            if os.path.exists('focus_game_progress.json'):
                with open('focus_game_progress.json', 'r') as f:
                    data = json.load(f)
                    self.level_progress = [LevelProgress(**progress) for progress in data]
        except Exception as e:
            print(f"Error loading saved data: {e}")
    
    def _save_data(self):
        try:
            with open('focus_game_sessions.json', 'w') as f:
                json.dump([asdict(session) for session in self.sessions], f)
            
            with open('focus_game_progress.json', 'w') as f:
                json.dump([asdict(progress) for progress in self.level_progress], f)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def get_level_config(self, level: int) -> Optional[LevelConfig]:
        return next((config for config in self.level_configs if config.level == level), None)
    
    def get_level_stats(self, level: int) -> Optional[LevelProgress]:
        return next((progress for progress in self.level_progress if progress.level == level), None)
    
    def start_game(self, level: int):
        self.current_level = level
        session_id = f"session_{int(time.time() * 1000)}"
        self.current_session = GameSession(session_id, level, time.time())
        self.game_state = GameState.PLAYING
        self.game_score = 0
        self.lives = 3
        self.game_objects = []
        self.last_spawn_time = 0
        self.background_offset = 0
        self.game_time = 0
        self.start_time = time.time()
    
    def end_game(self):
        if not self.current_session:
            return
        
        # Complete session
        end_time = time.time()
        total_clicks = self.current_session.correct_clicks + self.current_session.incorrect_clicks
        accuracy = (self.current_session.correct_clicks / total_clicks * 100) if total_clicks > 0 else 0
        avg_reaction_time = (sum(self.current_session.reaction_times) / len(self.current_session.reaction_times)) if self.current_session.reaction_times else 0
        
        self.current_session.end_time = end_time
        self.current_session.accuracy = accuracy
        self.current_session.average_reaction_time = avg_reaction_time
        
        # Update level progress
        existing_progress = self.get_level_stats(self.current_level)
        if existing_progress:
            existing_progress.best_accuracy = max(existing_progress.best_accuracy, accuracy)
            if existing_progress.best_reaction_time > 0:
                existing_progress.best_reaction_time = min(existing_progress.best_reaction_time, avg_reaction_time)
            else:
                existing_progress.best_reaction_time = avg_reaction_time
            existing_progress.times_played += 1
            existing_progress.last_played = end_time
        else:
            new_progress = LevelProgress(self.current_level, accuracy, avg_reaction_time, 1, end_time)
            self.level_progress.append(new_progress)
        
        # Save completed session
        self.sessions.append(self.current_session)
        self.current_session = None
        
        # Save data
        self._save_data()
        
        # Return to menu
        self.game_state = GameState.MENU
    
    def record_click(self, is_correct: bool, reaction_time: float):
        if not self.current_session:
            return
        
        if is_correct:
            self.current_session.correct_clicks += 1
            self.game_score += 10
        else:
            self.current_session.incorrect_clicks += 1
            self.game_score = max(0, self.game_score - 5)
            self.lives -= 1
        
        self.current_session.reaction_times.append(reaction_time)
        
        # Check win/lose conditions
        level_config = self.get_level_config(self.current_level)
        if level_config:
            if self.current_session.correct_clicks >= level_config.required_correct_clicks:
                self.end_game()
            elif self.lives <= 0:
                self.end_game()
    
    def spawn_object(self):
        level_config = self.get_level_config(self.current_level)
        if not level_config or len(self.game_objects) >= level_config.max_objects:
            return
        
        current_time = time.time() * 1000
        spawn_interval = 1000 / level_config.spawn_rate
        
        if current_time - self.last_spawn_time < spawn_interval:
            return
        
        self.last_spawn_time = current_time
        
        # Determine if target or distractor
        is_target = random.random() < level_config.target_ratio
        obj_type = level_config.target_type if is_target else random.choice(level_config.distractor_types)
        
        # Random position
        margin = 50
        x = margin + random.random() * (SCREEN_WIDTH - 2 * margin - 60)
        y = margin + random.random() * (SCREEN_HEIGHT - 2 * margin - 60)
        
        obj = GameObject(obj_type, x, y, is_target, current_time, level_config.object_lifespan)
        self.game_objects.append(obj)
    
    def update_objects(self, delta_time: float):
        current_time = time.time() * 1000
        
        # Update existing objects
        for obj in self.game_objects[:]:
            obj.update(delta_time)
            
            # Remove expired objects
            if obj.is_expired(current_time):
                self.game_objects.remove(obj)
            
            # Remove off-screen objects
            elif (obj.x < -obj.size or obj.x > SCREEN_WIDTH + obj.size or 
                  obj.y < -obj.size or obj.y > SCREEN_HEIGHT + obj.size):
                self.game_objects.remove(obj)
    
    def handle_click(self, pos: Tuple[int, int]):
        if self.game_state != GameState.PLAYING:
            return
        
        click_time = time.time() * 1000
        hit_object = None
        
        # Find clicked object (topmost)
        for obj in reversed(self.game_objects):
            if obj.is_point_inside(pos[0], pos[1]):
                hit_object = obj
                break
        
        if hit_object:
            reaction_time = click_time - hit_object.spawn_time
            self.game_objects.remove(hit_object)
            self.record_click(hit_object.is_target, reaction_time)
        else:
            # Clicked empty space - incorrect
            reaction_time = click_time - self.start_time * 1000
            self.record_click(False, reaction_time)
    
    def draw_background(self):
        # Gradient background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(COLORS['background'][0] * (1 - ratio) + COLORS['purple'][0] * ratio)
            g = int(COLORS['background'][1] * (1 - ratio) + COLORS['purple'][1] * ratio)
            b = int(COLORS['background'][2] * (1 - ratio) + COLORS['purple'][2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Moving pattern
        pattern_size = 50
        for x in range(-pattern_size, SCREEN_WIDTH + pattern_size, pattern_size):
            for y in range(-pattern_size, SCREEN_HEIGHT + pattern_size, pattern_size):
                offset_x = x + (self.background_offset % (pattern_size * 2))
                offset_y = y + (self.background_offset % (pattern_size * 2))
                pygame.draw.circle(self.screen, (*COLORS['white'][:3], 25), (int(offset_x), int(offset_y)), 3)
    
    def draw_menu(self):
        self.screen.fill(COLORS['background'])
        
        # Title
        title = self.font_large.render("Focus Catcher", True, COLORS['white'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_medium.render("Visual Attention Game", True, COLORS['white'])
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Description
        desc = self.font_small.render("Improve focus and impulse control", True, COLORS['white'])
        desc_rect = desc.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(desc, desc_rect)
        
        # Buttons
        button_width, button_height = 200, 50
        start_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, 400, button_width, button_height)
        progress_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, 480, button_width, button_height)
        
        pygame.draw.rect(self.screen, COLORS['white'], start_button)
        pygame.draw.rect(self.screen, COLORS['white'], progress_button)
        
        start_text = self.font_medium.render("Start Game", True, COLORS['black'])
        start_text_rect = start_text.get_rect(center=start_button.center)
        self.screen.blit(start_text, start_text_rect)
        
        progress_text = self.font_medium.render("View Progress", True, COLORS['black'])
        progress_text_rect = progress_text.get_rect(center=progress_button.center)
        self.screen.blit(progress_text, progress_text_rect)
        
        return start_button, progress_button
    
    def draw_level_select(self):
        self.screen.fill(COLORS['background'])
        
        # Title
        title = self.font_large.render("Select Level", True, COLORS['white'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Level buttons
        buttons = []
        cols = 5
        rows = 2
        button_width, button_height = 200, 120
        start_x = (SCREEN_WIDTH - cols * button_width - (cols - 1) * 20) // 2
        start_y = 150
        
        for i, config in enumerate(self.level_configs):
            row = i // cols
            col = i % cols
            x = start_x + col * (button_width + 20)
            y = start_y + row * (button_height + 30)
            
            # Check if level is unlocked
            stats = self.get_level_stats(config.level)
            is_unlocked = config.level == 1 or (stats and stats.best_accuracy >= 70)
            
            button_rect = pygame.Rect(x, y, button_width, button_height)
            color = COLORS['white'] if is_unlocked else COLORS['gray']
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, COLORS['black'], button_rect, 2)
            
            # Level info
            level_text = self.font_medium.render(f"Level {config.level}", True, COLORS['black'])
            name_text = self.font_small.render(config.name, True, COLORS['black'])
            desc_text = self.font_small.render(config.description[:25] + "...", True, COLORS['black'])
            
            self.screen.blit(level_text, (x + 10, y + 10))
            self.screen.blit(name_text, (x + 10, y + 40))
            self.screen.blit(desc_text, (x + 10, y + 65))
            
            if stats:
                accuracy_text = self.font_small.render(f"Best: {int(stats.best_accuracy)}%", True, COLORS['black'])
                self.screen.blit(accuracy_text, (x + 10, y + 90))
            
            if is_unlocked:
                buttons.append((button_rect, config.level))
        
        # Back button
        back_button = pygame.Rect(50, 50, 100, 40)
        pygame.draw.rect(self.screen, COLORS['white'], back_button)
        back_text = self.font_small.render("Back", True, COLORS['black'])
        back_text_rect = back_text.get_rect(center=back_button.center)
        self.screen.blit(back_text, back_text_rect)
        
        return buttons, back_button
    
    def draw_game_ui(self):
        if not self.current_session:
            return
        
        level_config = self.get_level_config(self.current_level)
        if not level_config:
            return
        
        # Top UI bar
        ui_height = 80
        pygame.draw.rect(self.screen, (*COLORS['white'], 200), (0, 0, SCREEN_WIDTH, ui_height))
        
        # Level info
        level_text = self.font_medium.render(f"Level {self.current_level}: {level_config.name}", True, COLORS['black'])
        self.screen.blit(level_text, (20, 10))
        
        # Score
        score_text = self.font_small.render(f"Score: {self.game_score}", True, COLORS['black'])
        self.screen.blit(score_text, (20, 40))
        
        # Progress
        progress = (self.current_session.correct_clicks / level_config.required_correct_clicks) * 100
        progress_text = self.font_small.render(f"Progress: {self.current_session.correct_clicks}/{level_config.required_correct_clicks}", True, COLORS['black'])
        self.screen.blit(progress_text, (200, 40))
        
        # Lives
        for i in range(3):
            color = COLORS['red'] if i < self.lives else COLORS['gray']
            pygame.draw.circle(self.screen, color, (SCREEN_WIDTH - 150 + i * 30, 30), 10)
        
        # Accuracy
        total_clicks = self.current_session.correct_clicks + self.current_session.incorrect_clicks
        accuracy = (self.current_session.correct_clicks / total_clicks * 100) if total_clicks > 0 else 0
        accuracy_text = self.font_small.render(f"Accuracy: {int(accuracy)}%", True, COLORS['black'])
        self.screen.blit(accuracy_text, (400, 40))
        
        # Target reminder
        target_text = self.font_small.render(f"Target: {level_config.target_type.value.title()}s", True, COLORS['black'])
        self.screen.blit(target_text, (600, 40))
        
        # Pause button
        pause_button = pygame.Rect(SCREEN_WIDTH - 80, 10, 60, 30)
        pygame.draw.rect(self.screen, COLORS['white'], pause_button)
        pygame.draw.rect(self.screen, COLORS['black'], pause_button, 2)
        pause_text = self.font_small.render("Pause", True, COLORS['black'])
        pause_text_rect = pause_text.get_rect(center=pause_button.center)
        self.screen.blit(pause_text, pause_text_rect)
        
        return pause_button
    
    def draw_paused(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(COLORS['black'])
        self.screen.blit(overlay, (0, 0))
        
        # Pause dialog
        dialog_width, dialog_height = 400, 200
        dialog_rect = pygame.Rect((SCREEN_WIDTH - dialog_width) // 2, (SCREEN_HEIGHT - dialog_height) // 2, dialog_width, dialog_height)
        pygame.draw.rect(self.screen, COLORS['white'], dialog_rect)
        pygame.draw.rect(self.screen, COLORS['black'], dialog_rect, 3)
        
        # Text
        paused_text = self.font_large.render("Game Paused", True, COLORS['black'])
        paused_rect = paused_text.get_rect(center=(dialog_rect.centerx, dialog_rect.centery - 40))
        self.screen.blit(paused_text, paused_rect)
        
        # Resume button
        resume_button = pygame.Rect(dialog_rect.centerx - 80, dialog_rect.centery + 20, 160, 40)
        pygame.draw.rect(self.screen, COLORS['green'], resume_button)
        resume_text = self.font_medium.render("Resume", True, COLORS['white'])
        resume_text_rect = resume_text.get_rect(center=resume_button.center)
        self.screen.blit(resume_text, resume_text_rect)
        
        return resume_button
    
    def draw_progress(self):
        self.screen.fill(COLORS['background'])
        
        # Title
        title = self.font_large.render("Progress Report", True, COLORS['white'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Overall stats
        total_sessions = len(self.sessions)
        avg_accuracy = sum(s.accuracy for s in self.sessions) / len(self.sessions) if self.sessions else 0
        levels_completed = len([p for p in self.level_progress if p.best_accuracy >= 70])
        
        stats_y = 120
        stats = [
            f"Total Sessions: {total_sessions}",
            f"Average Accuracy: {int(avg_accuracy)}%",
            f"Levels Completed: {levels_completed}/10"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.font_medium.render(stat, True, COLORS['white'])
            self.screen.blit(stat_text, (50, stats_y + i * 30))
        
        # Level progress
        progress_y = 250
        progress_title = self.font_medium.render("Level Progress:", True, COLORS['white'])
        self.screen.blit(progress_title, (50, progress_y))
        
        for i, progress in enumerate(self.level_progress[:10]):  # Show first 10 levels
            y = progress_y + 40 + i * 30
            level_text = f"Level {progress.level}: {int(progress.best_accuracy)}% accuracy, {int(progress.best_reaction_time)}ms reaction"
            text = self.font_small.render(level_text, True, COLORS['white'])
            self.screen.blit(text, (70, y))
        
        # Back button
        back_button = pygame.Rect(50, SCREEN_HEIGHT - 80, 100, 40)
        pygame.draw.rect(self.screen, COLORS['white'], back_button)
        back_text = self.font_small.render("Back", True, COLORS['black'])
        back_text_rect = back_text.get_rect(center=back_button.center)
        self.screen.blit(back_text, back_text_rect)
        
        return back_button
    
    def run(self):
        while self.running:
            delta_time = self.clock.tick(FPS) / 1000.0
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        pos = pygame.mouse.get_pos()
                        
                        if self.game_state == GameState.MENU:
                            start_button, progress_button = self.draw_menu()
                            if start_button.collidepoint(pos):
                                self.game_state = GameState.LEVEL_SELECT
                            elif progress_button.collidepoint(pos):
                                self.game_state = GameState.PROGRESS
                        
                        elif self.game_state == GameState.LEVEL_SELECT:
                            level_buttons, back_button = self.draw_level_select()
                            if back_button.collidepoint(pos):
                                self.game_state = GameState.MENU
                            else:
                                for button_rect, level in level_buttons:
                                    if button_rect.collidepoint(pos):
                                        self.start_game(level)
                                        break
                        
                        elif self.game_state == GameState.PLAYING:
                            pause_button = self.draw_game_ui()
                            if pause_button and pause_button.collidepoint(pos):
                                self.game_state = GameState.PAUSED
                            else:
                                self.handle_click(pos)
                        
                        elif self.game_state == GameState.PAUSED:
                            resume_button = self.draw_paused()
                            if resume_button.collidepoint(pos):
                                self.game_state = GameState.PLAYING
                        
                        elif self.game_state == GameState.PROGRESS:
                            back_button = self.draw_progress()
                            if back_button.collidepoint(pos):
                                self.game_state = GameState.MENU
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_state == GameState.PLAYING:
                            self.game_state = GameState.PAUSED
                        elif self.game_state == GameState.PAUSED:
                            self.game_state = GameState.PLAYING
                        else:
                            self.game_state = GameState.MENU
            
            # Update game logic
            if self.game_state == GameState.PLAYING:
                level_config = self.get_level_config(self.current_level)
                if level_config:
                    self.background_offset += level_config.background_speed * delta_time
                    self.game_time += delta_time
                    self.spawn_object()
                    self.update_objects(delta_time)
            
            # Draw everything
            if self.game_state == GameState.MENU:
                self.draw_menu()
            elif self.game_state == GameState.LEVEL_SELECT:
                self.draw_level_select()
            elif self.game_state == GameState.PLAYING:
                self.draw_background()
                for obj in self.game_objects:
                    obj.draw(self.screen)
                self.draw_game_ui()
            elif self.game_state == GameState.PAUSED:
                self.draw_background()
                for obj in self.game_objects:
                    obj.draw(self.screen)
                self.draw_game_ui()
                self.draw_paused()
            elif self.game_state == GameState.PROGRESS:
                self.draw_progress()
            
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    game = FocusCatcherGame()
    game.run()