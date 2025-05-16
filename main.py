import sys
import bomb_game
import pygame
import json
import random
import os
from datetime import datetime

# Initialize pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
LIGHT_GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
DARK_GRAY = (100, 100, 100)

class QuestionGraph:
    def __init__(self, all_questions):
        # Split questions into main sets and subsets
        self.graph = {
            'nodes': {
                'root': {
                    'type': 'choice',
                    'children': ['set1', 'set2'],
                    'title': "Main Menu"
                },
                'set1': {
                    'type': 'choice',
                    'children': ['set1_a', 'set1_b', 'set1_c'],
                    'questions': None,
                    'title': "Licenses"
                },
                'set2': {
                    'type': 'choice',
                    'children': ['set2_a', 'set2_b', 'set2_c'],
                    'questions': None,
                    'title': "Classical programming"
                },
                # Subsets for set1
                'set1_a': {
                    'type': 'question_set',
                    'children': [],
                    'questions': all_questions[:10],
                    'title': "License - definition and types"
                },
                'set1_b': {
                    'type': 'question_set',
                    'children': [],
                    'questions': all_questions[10:20],
                    'title': "Use of licences – advantages and disadvantages"
                },
                'set1_c': {
                    'type': 'question_set',
                    'children': [],
                    'questions': all_questions[20:30],
                    'title': "Emerging trends in licensing"
                },
                # Subsets for set2
                'set2_a': {
                    'type': 'question_set',
                    'children': [],
                    'questions': all_questions[30:40],
                    'title': "Classical Programming - an introduction"
                },
                'set2_b': {
                    'type': 'question_set',
                    'children': [],
                    'questions': all_questions[40:50],
                    'title': "Classical Programming - Key Programming Concepts"
                },
                'set2_c': {
                    'type': 'question_set',
                    'children': [],
                    'questions': all_questions[50:60],
                    'title': "Classical Programming - Web Programming"
                }
            },
            'edges': [
                ('root', 'set1'), ('root', 'set2'),
                ('set1', 'set1_a'), ('set1', 'set1_b'), ('set1', 'set1_c'),
                ('set2', 'set2_a'), ('set2', 'set2_b'), ('set2', 'set2_c')
            ]
        }
        
    def get_questions(self, node_id):
        """Get questions for a chosen node"""
        if node_id in self.graph['nodes']:
            node = self.graph['nodes'][node_id]
            if node['type'] == 'question_set':
                return node['questions']
        return []
    
    def get_children(self, node_id):
        """Get child nodes for navigation"""
        if node_id in self.graph['nodes']:
            return self.graph['nodes'][node_id]['children']
        return []
    
    def get_node_title(self, node_id):
        """Get the title for a node"""
        if node_id in self.graph['nodes']:
            return self.graph['nodes'][node_id]['title']
        return ""

class BeatTheBombGame:
    def __init__(self, screen_width=1500, screen_height=700):
        pygame.display.set_caption("Beat the Bomb Game")
        self.fullscreen = False
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        self.screen_width, self.screen_height = self.screen.get_size()

        self.show_welcome = True
        self.welcome_next_button = None

        self.paused_duration = 0
        self.pause_start_time = 0

        # Initialize fonts
        self.question_font = pygame.font.SysFont('Helvetica', 30)
        self.answer_font = pygame.font.SysFont('Helvetica', 26)
        self.score_font = pygame.font.SysFont('Helvetica', 32)
        self.timer_font = pygame.font.SysFont('Helvetica', 48)
        self.button_font = pygame.font.SysFont('Helvetica', 30)
        self.menu_font = pygame.font.SysFont('Helvetica', 40)
        self.subtitle_font = pygame.font.SysFont('Helvetica', 30)
    
        with open('questions.json') as f:
            all_questions = json.load(f)

        # Initialize question graph
        self.question_graph = QuestionGraph(all_questions)
        self.current_node = 'root'
        self.previous_nodes = []
        self.questions = []
        self.menu_buttons = []
        self.in_menu = True  # Track if we're in menu mode

        self.explosion_sound = pygame.mixer.Sound('explosion.wav')
        self.reset_game_state()

    def reset_game_state(self):
        """Reset all game state variables"""
        if self.questions:
            bomb_game.init_game(len(self.questions))
            
        self.current_question = 0
        self.selected_answer = -1
        self.score = 0
        self.game_over = False
        self.won_game = False
        self.clock = pygame.time.Clock()
        self.start_time = pygame.time.get_ticks() / 1000.0
        self.paused_duration = 0
        self.pause_start_time = 0
        self.show_feedback = False
        self.feedback_time = 0
        self.correct_answer_index = -1
        self.show_correct_answer = False
        self.play_again_button = None
        self.pause_button = None
        self.reset_button = None
        self.paused = False
        self.pause_menu_buttons = []
        self.resume_button = None
        self.pause_reset_button = None
        self.back_button = None

    def draw_welcome_screen(self):
        """Draw the welcome screen with game instructions"""
        self.screen.fill(WHITE)
        
        # Title
        title = self.menu_font.render("Welcome to Beat the Bomb Game!", True, BLACK)
        title_rect = title.get_rect(center=(self.screen_width//2, self.screen_height//2 - 200))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "Game Rules:",
            "1. Choose the answer for each question before the time expires.",
            "2. For correct answers you receive 10 points.",
            "3. You get a penalty of 3 secs for wrong answers.",
            "4. If you don't answer in time the bomb explodes.",
            "5. If you don't answer correctly to at least half the questions",
            "the bomb also explodes",
            "6. For resetting the game you can press R key",
            "7. For pausing the game you can press P key",
            "",
            "Select a question set from the next screen to begin!"
        ]
        
        for i, line in enumerate(instructions):
            text = self.subtitle_font.render(line, True, BLACK)
            self.screen.blit(text, (self.screen_width//2 - 300, self.screen_height//2 - 100 + i * 40))
        
        # Next button
        button_width, button_height = 200, 50
        button_x = self.screen_width - button_width - 40
        button_y = self.screen_height - button_height - 40
        
        self.welcome_next_button = pygame.Rect(button_x, button_y, button_width, button_height)
        mouse_pos = pygame.mouse.get_pos()
        button_color = LIGHT_BLUE if self.welcome_next_button.collidepoint(mouse_pos) else GRAY
        
        pygame.draw.rect(self.screen, button_color, self.welcome_next_button)
        pygame.draw.rect(self.screen, BLACK, self.welcome_next_button, 2)
        
        text = self.button_font.render("Continue", True, BLACK)
        text_rect = text.get_rect(center=self.welcome_next_button.center)
        self.screen.blit(text, text_rect)

    def handle_welcome_click(self, pos):
        """Handle clicks on the welcome screen"""
        if self.welcome_next_button and self.welcome_next_button.collidepoint(pos):
            self.show_welcome = False
            return True
        return False

    def draw_bomb(self, fuse_percent):
        center = (self.screen_width // 2, 150)
        pygame.draw.circle(self.screen, BLACK, center, 80)
        fuse_len = 150 * (fuse_percent / 100)
        fuse_start = (center[0], center[1] - 80)
        fuse_end = (center[0] + 50, center[1] - 80 - fuse_len)
        pygame.draw.line(self.screen, ORANGE, fuse_start, fuse_end, 8)
        if fuse_percent > 0:
            for _ in range(5):
                sx = fuse_end[0] + random.randint(-10, 10)
                sy = fuse_end[1] + random.randint(-20, 0)
                pygame.draw.circle(self.screen, YELLOW, (sx, sy), random.randint(2, 5))

    def draw_question(self):
        if self.current_question >= len(self.questions):
            return

        question = self.questions[self.current_question]
        self.correct_answer_index = next((i for i, ans in enumerate(question["answers"]) if ans["correct"]), -1)
        question_text = f"Q{self.current_question + 1}: {question['question']}"
        q_surface = self.question_font.render(question_text, True, BLACK)
        self.screen.blit(q_surface, (50, 250))
        
        for i, ans in enumerate(question["answers"]):
            bg_color = LIGHT_GREEN if (self.show_feedback and ans["correct"] and self.show_correct_answer) else WHITE
            answer_bg = pygame.Rect(45, 295 + i * 40, self.screen_width - 90, 32)
            pygame.draw.rect(self.screen, bg_color, answer_bg)
            checkbox_rect = pygame.Rect(50, 305 + i * 40, 20, 20)
            pygame.draw.rect(self.screen, BLACK, checkbox_rect, 2)
            
            if self.show_feedback and i == self.selected_answer:
                color = GREEN if ans["correct"] else RED
                pygame.draw.line(self.screen, color, (52, 310 + i * 40), (68, 318 + i * 40), 2)
                pygame.draw.line(self.screen, color, (68, 310 + i * 40), (52, 318 + i * 40), 2)
            
            text_color = BLUE if i == self.selected_answer else BLACK
            txt = self.answer_font.render(ans["text"], True, text_color)
            self.screen.blit(txt, (80, 300 + i * 40))

    def draw_score(self):
        score_text = f"Score: {self.score}"
        score_surface = self.score_font.render(score_text, True, BLACK)
        self.screen.blit(score_surface, (50, 50))

    def draw_timer(self):
        fuse = bomb_game.get_fuse_percentage()
        time_rem = int((fuse / 100) * 20)
        timer_text = f"Time: {max(0, time_rem)}s"
        color = RED if time_rem < 5 else BLACK
        timer_surface = self.timer_font.render(timer_text, True, color)
        self.screen.blit(timer_surface, (self.screen_width - 200, 50))

    def draw_control_buttons(self):
        # Pause button (top right)
        pause_width, pause_height = 100, 40
        pause_x = self.screen_width - pause_width - 20
        pause_y = 150
        
        self.pause_button = pygame.Rect(pause_x, pause_y, pause_width, pause_height)
        mouse_pos = pygame.mouse.get_pos()
        pause_color = LIGHT_BLUE if self.pause_button.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(self.screen, pause_color, self.pause_button)
        pygame.draw.rect(self.screen, BLACK, self.pause_button, 2)
        
        pause_text = self.button_font.render("Pause", True, BLACK)
        pause_text_rect = pause_text.get_rect(center=self.pause_button.center)
        self.screen.blit(pause_text, pause_text_rect)

        # Reset button (next to pause)
        reset_width, reset_height = 100, 40
        reset_x = pause_x - reset_width - 10
        reset_y = 150
        
        self.reset_button = pygame.Rect(reset_x, reset_y, reset_width, reset_height)
        reset_color = LIGHT_BLUE if self.reset_button.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(self.screen, reset_color, self.reset_button)
        pygame.draw.rect(self.screen, BLACK, self.reset_button, 2)
        
        reset_text = self.button_font.render("Reset", True, BLACK)
        reset_text_rect = reset_text.get_rect(center=self.reset_button.center)
        self.screen.blit(reset_text, reset_text_rect)

        # Back button (top left)
        if len(self.previous_nodes) > 0:
            back_width, back_height = 100, 40
            back_x = 20
            back_y = 150
            
            self.back_button = pygame.Rect(back_x, back_y, back_width, back_height)
            back_color = LIGHT_BLUE if self.back_button and self.back_button.collidepoint(mouse_pos) else GRAY
            pygame.draw.rect(self.screen, back_color, self.back_button)
            pygame.draw.rect(self.screen, BLACK, self.back_button, 2)
            
            back_text = self.button_font.render("Back", True, BLACK)
            back_text_rect = back_text.get_rect(center=self.back_button.center)
            self.screen.blit(back_text, back_text_rect)

    def draw_pause_menu(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Pause title
        title = self.menu_font.render("GAME PAUSED", True, WHITE)
        title_rect = title.get_rect(center=(self.screen_width//2, self.screen_height//2 - 100))
        self.screen.blit(title, title_rect)
        
        # Resume button
        resume_width, resume_height = 200, 50
        resume_x = self.screen_width//2 - resume_width//2
        resume_y = self.screen_height//2 - 20
        
        self.resume_button = pygame.Rect(resume_x, resume_y, resume_width, resume_height)
        mouse_pos = pygame.mouse.get_pos()
        resume_color = LIGHT_BLUE if self.resume_button.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(self.screen, resume_color, self.resume_button)
        pygame.draw.rect(self.screen, WHITE, self.resume_button, 2)
        
        resume_text = self.button_font.render("Resume", True, BLACK)
        resume_text_rect = resume_text.get_rect(center=self.resume_button.center)
        self.screen.blit(resume_text, resume_text_rect)
        
        # Reset button in pause menu
        pause_reset_width, pause_reset_height = 200, 50
        pause_reset_x = self.screen_width//2 - pause_reset_width//2
        pause_reset_y = self.screen_height//2 + 50
        
        self.pause_reset_button = pygame.Rect(pause_reset_x, pause_reset_y, pause_reset_width, pause_reset_height)
        pause_reset_color = LIGHT_BLUE if self.pause_reset_button.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(self.screen, pause_reset_color, self.pause_reset_button)
        pygame.draw.rect(self.screen, WHITE, self.pause_reset_button, 2)
        
        pause_reset_text = self.button_font.render("Reset Game", True, BLACK)
        pause_reset_text_rect = pause_reset_text.get_rect(center=self.pause_reset_button.center)
        self.screen.blit(pause_reset_text, pause_reset_text_rect)

    def draw_play_again_button(self):
        button_width, button_height = 200, 50
        button_x = self.screen_width // 2 - button_width // 2
        button_y = self.screen_height // 2 + 100
        
        self.play_again_button = pygame.Rect(button_x, button_y, button_width, button_height)
        mouse_pos = pygame.mouse.get_pos()
        button_color = LIGHT_BLUE if self.play_again_button.collidepoint(mouse_pos) else GRAY
        
        pygame.draw.rect(self.screen, button_color, self.play_again_button)
        pygame.draw.rect(self.screen, BLACK, self.play_again_button, 2)
        
        text = self.button_font.render("Play Again", True, BLACK)
        text_rect = text.get_rect(center=self.play_again_button.center)
        self.screen.blit(text, text_rect)

    def draw_game_over(self):
        msg = "You defused the bomb!" if self.won_game else "Boom! The bomb exploded!"
        color = GREEN if self.won_game else RED
        surface = self.score_font.render(msg, True, color)
        rect = surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 100))
        self.screen.blit(surface, rect)
        
        score_txt = self.score_font.render(f"Final Score: {self.score}", True, BLACK)
        score_rect = score_txt.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(score_txt, score_rect)
        
        self.draw_play_again_button()

    def draw_menu(self):
        """Draw the appropriate menu based on current node"""
        self.screen.fill(WHITE)
        self.menu_buttons = []
        
        # Draw title
        title = self.menu_font.render(self.question_graph.get_node_title(self.current_node), True, BLACK)
        title_rect = title.get_rect(center=(self.screen_width//2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw back button 
        back_width, back_height = 100, 40
        back_x = 20
        back_y = 20
            
        self.back_button = pygame.Rect(back_x, back_y, back_width, back_height)
        mouse_pos = pygame.mouse.get_pos()
        back_color = LIGHT_BLUE if self.back_button.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(self.screen, back_color, self.back_button)
        pygame.draw.rect(self.screen, BLACK, self.back_button, 2)
            
        back_text = self.button_font.render("Back", True, BLACK)
        back_text_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_text_rect)
        
        # Draw menu buttons for children
        children = self.question_graph.get_children(self.current_node)
        button_width, button_height = 800, 80
        start_y = 180  
    
        for i, child in enumerate(children):
            button_x = self.screen_width // 2 - button_width // 2
            button_y = start_y + i * (button_height + 20)
            
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            mouse_pos = pygame.mouse.get_pos()
            button_color = LIGHT_BLUE if button_rect.collidepoint(mouse_pos) else GRAY
            
            pygame.draw.rect(self.screen, button_color, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
            
            button_text = self.button_font.render(self.question_graph.get_node_title(child), True, BLACK)
            button_text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, button_text_rect)
            
            self.menu_buttons.append((child, button_rect))
        
        pygame.display.flip()

    def handle_menu_click(self, pos):
        """Handle clicks on the menu screen"""
        # Check menu buttons first
        for node_id, button in self.menu_buttons:
            if button.collidepoint(pos):
                if node_id not in self.question_graph.graph['nodes']:
                    continue  # Skip invalid nodes
                
                node = self.question_graph.graph['nodes'][node_id]
                if node['type'] == 'question_set':
                    # Start the game with these questions
                    self.questions = self.question_graph.get_questions(node_id)
                    if self.questions:  # Only proceed if we got questions
                        self.reset_game_state()
                        self.in_menu = False
                        return
                else:
                    # Navigate to next menu
                    self.previous_nodes.append(self.current_node)
                    self.current_node = node_id
                    self.draw_menu()
                    return
        
        # Then check back button
        if hasattr(self, 'back_button') and self.back_button and self.back_button.collidepoint(pos):
            if self.current_node == 'root':
                # If at root, go back to welcome screen
                self.show_welcome = True
            elif self.previous_nodes:
                # Otherwise navigate back in the menu hierarchy
                self.current_node = self.previous_nodes.pop()
                self.draw_menu()

    def handle_click(self, pos):
        if self.game_over and self.play_again_button and self.play_again_button.collidepoint(pos):
            self.current_node = 'root'
            self.previous_nodes = []
            self.in_menu = True
            self.game_over = False
            return
            
        if self.paused:
            if self.resume_button and self.resume_button.collidepoint(pos):
                self.paused = False
                bomb_game.set_paused(0)
                self.paused_duration += pygame.time.get_ticks() - self.pause_start_time
                return
            elif self.pause_reset_button and self.pause_reset_button.collidepoint(pos):
                 if self.questions:
                   self.reset_game_state()
                   bomb_game.init_game(len(self.questions))
                   self.paused = False
                   bomb_game.set_paused(0)
                 return
            return
            
        if self.pause_button and self.pause_button.collidepoint(pos) and not self.game_over:
            self.paused = True
            bomb_game.set_paused(1)
            self.pause_start_time = pygame.time.get_ticks()
            return
            
        if self.reset_button and self.reset_button.collidepoint(pos):
           if self.questions:  # Only reset if we have questions loaded
             self.reset_game_state()
             bomb_game.init_game(len(self.questions))  # Reinitialize with same questions
           return
            
        if hasattr(self, 'back_button') and self.back_button and self.back_button.collidepoint(pos):
            if self.previous_nodes:
                self.current_node = self.previous_nodes.pop()
                self.in_menu = True
            return
            
        if self.show_feedback or self.game_over or self.paused or self.in_menu:
            return
            
        for i in range(4):
            area = pygame.Rect(50, 300 + i * 40, self.screen_width - 100, 30)
            if area.collidepoint(pos):
                self.selected_answer = i
                self.submit_answer()
                break

    def submit_answer(self):
        if self.selected_answer == -1 or self.game_over or self.show_feedback or self.paused or self.in_menu:
            return
            
        question = self.questions[self.current_question]
        is_correct = question["answers"][self.selected_answer]["correct"]
        self.show_correct_answer = not is_correct
        
        # Update bomb fuse based on correctness
        bomb_game.answer_question(1 if is_correct else 0)
        
        if is_correct:
            self.score += 10
            
        self.show_feedback = True
        self.feedback_time = pygame.time.get_ticks()

    def update(self):
        if self.in_menu or self.game_over:
            return
            
        current_time = pygame.time.get_ticks() / 1000.0  # Current time in seconds
        
        # Calculate time accounting for pauses
        if self.paused:
            current_time = (self.pause_start_time - self.paused_duration) / 1000.0
        else:
            current_time = (pygame.time.get_ticks() - self.paused_duration) / 1000.0

        # Update timer with current time
        if bomb_game.update_timer(current_time):
            self.game_over = True
            required_score = (len(self.questions) * 10) // 2
            self.won_game = self.score >= required_score
            if not self.won_game:
                self.explosion_sound.play()

            required_score = (len(self.questions) * 10) // 2
            self.won_game = self.score >= required_score
            if not self.won_game:
                self.explosion_sound.play()
        
        # Handle question feedback
        if self.show_feedback and (pygame.time.get_ticks() - self.feedback_time) > 1000:
            self.show_feedback = False
            self.show_correct_answer = False
            self.selected_answer = -1
            self.current_question += 1
            
            if self.current_question >= len(self.questions):
                required_score = (len(self.questions) * 10) // 2
                self.won_game = self.score >= required_score
                self.game_over = True
                if not self.won_game:
                    self.explosion_sound.play()
            else:
                bomb_game.init_game(len(self.questions))

    def run(self):
        running = True
        
        while running:
            # Show welcome screen first if needed
            if self.show_welcome:
                self.draw_welcome_screen()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        self.handle_welcome_click(event.pos)
                pygame.display.flip()
                continue

            if self.in_menu:
                self.draw_menu()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        self.handle_menu_click(event.pos)
                continue
                
            self.screen.fill(WHITE)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:  # Pause with P key
                        if not self.game_over:
                            self.paused = not self.paused
                            bomb_game.set_paused(1 if self.paused else 0)
                            if self.paused:
                                self.pause_start_time = pygame.time.get_ticks()
                            else:
                                # Adjust the timer to account for pause duration
                               pause_duration = (pygame.time.get_ticks() - self.pause_start_time) / 1000.0
                               self.start_time += pause_duration
                    elif event.key == pygame.K_r:  # Reset with R key
                        if self.questions and not self.in_menu:
                           self.reset_game_state()
                           bomb_game.init_game(len(self.questions))
                    elif event.key == pygame.K_F11:
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen:
                            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        else:
                            self.screen = pygame.display.set_mode((1500, 700), pygame.RESIZABLE)
                        self.screen_width, self.screen_height = self.screen.get_size()
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.screen_width, self.screen_height = event.w, event.h

            if not self.paused and not self.in_menu:
                fuse = bomb_game.get_fuse_percentage()
                self.draw_bomb(fuse)
                self.draw_score()
                self.draw_timer()
                
                if not self.game_over:
                    self.draw_question()
                    self.draw_control_buttons()
                else:
                    self.draw_game_over()
            elif self.paused:
                fuse = bomb_game.get_fuse_percentage()
                self.draw_bomb(fuse)
                self.draw_score()
                self.draw_timer()
                if not self.game_over:
                    self.draw_question()
                self.draw_control_buttons()
                self.draw_pause_menu()
                
            pygame.display.flip()
            self.clock.tick(60)
            self.update()
            
        pygame.quit()
        bomb_game.free_game()


if __name__ == "__main__":
    game = BeatTheBombGame()
    game.run()