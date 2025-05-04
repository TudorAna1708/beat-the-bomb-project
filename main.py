import bomb_game
import pygame
import json
import random
import csv
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

class ScoreGraph:
    def __init__(self):
        self.nodes = []
        self.edges = []
        
    def add_score(self, score):
        self.nodes.append(score)
        if len(self.nodes) > 1:
            self.edges.append((len(self.nodes)-2, len(self.nodes)-1))
    
    def get_scores(self):
        return self.nodes
    
    def get_edges(self):
        return self.edges

class BeatTheBombGame:
    def __init__(self, screen_width=1500, screen_height=700):
        pygame.display.set_caption("Beat the Bomb Game")
        self.fullscreen = False
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        self.screen_width, self.screen_height = self.screen.get_size()

        # Initialize fonts
        self.question_font = pygame.font.SysFont('Arial', 24)
        self.answer_font = pygame.font.SysFont('Arial', 22)
        self.score_font = pygame.font.SysFont('Arial', 32)
        self.timer_font = pygame.font.SysFont('Arial', 48)
        self.graph_font = pygame.font.SysFont('Arial', 20)
        self.button_font = pygame.font.SysFont('Arial', 30)

        with open('questions.json') as f:
            self.questions = json.load(f)

        self.reset_game()

        self.explosion_sound = pygame.mixer.Sound("explosion.wav")

    def reset_game(self):
        bomb_game.init_game(len(self.questions))
        self.current_question = 0
        self.selected_answer = -1
        self.score = 0
        self.game_over = False
        self.won_game = False
        self.clock = pygame.time.Clock()
        self.last_time = pygame.time.get_ticks()
        self.show_feedback = False
        self.feedback_time = 0
        self.correct_answer_index = -1
        self.show_correct_answer = False
        self.play_again_button = None

    def save_score(self, final_score):
        with open('scores.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), final_score])
        self.score_graph.add_score(final_score)

    def load_scores(self):
        self.score_graph = ScoreGraph()
        try:
            with open('scores.csv', 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 2:
                        self.score_graph.add_score(int(row[1]))
        except FileNotFoundError:
            pass

    def draw_graph(self):
        scores = self.score_graph.get_scores()
        edges = self.score_graph.get_edges()
        
        if len(scores) == 0:
            return
        
        node_positions = []
        graph_width = min(600, self.screen_width - 100)
        graph_height = 200
        start_x = self.screen_width // 2 - graph_width // 2
        start_y = self.screen_height // 2 + 50
        
        if len(scores) > 1:
            x_spacing = graph_width / (len(scores) - 1)
        else:
            x_spacing = 0
        
        max_score = max(scores) if max(scores) > 0 else 1
        
        for i, score in enumerate(scores):
            x = start_x + i * x_spacing
            y = start_y + graph_height - (score / max_score) * graph_height
            node_positions.append((x, y))
        
        for edge in edges:
            start_pos = node_positions[edge[0]]
            end_pos = node_positions[edge[1]]
            pygame.draw.line(self.screen, BLUE, start_pos, end_pos, 2)
        
        for i, (x, y) in enumerate(node_positions):
            pygame.draw.circle(self.screen, RED, (int(x), int(y)), 8)
            score_text = self.graph_font.render(str(scores[i]), True, BLACK)
            self.screen.blit(score_text, (int(x) - 15, int(y) - 30))
        
        title_text = self.graph_font.render("Score History (Undirected Graph)", True, BLACK)
        self.screen.blit(title_text, (self.screen_width // 2 - 150, start_y - 30))
        
        if len(scores) > 0:
            recent_scores_text = self.graph_font.render(
                "Recent scores (newest first): " + ", ".join(map(str, reversed(scores[-5:]))), 
                True, BLACK
            )
            self.screen.blit(recent_scores_text, (self.screen_width // 2 - 200, start_y + graph_height + 30))

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
            checkbox_rect = pygame.Rect(50, 300 + i * 40, 20, 20)
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

    def draw_play_again_button(self):
        button_width, button_height = 200, 50
        button_x = self.screen_width // 2 - button_width // 2
        button_y = self.screen_height // 2 + 200
        
        self.play_again_button = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Button color changes when hovered
        mouse_pos = pygame.mouse.get_pos()
        button_color = LIGHT_BLUE if self.play_again_button.collidepoint(mouse_pos) else GRAY
        
        pygame.draw.rect(self.screen, button_color, self.play_again_button)
        pygame.draw.rect(self.screen, BLACK, self.play_again_button, 2)  # Border
        
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
        
        self.save_score(self.score)
        self.draw_graph()
        self.draw_play_again_button()

    def handle_click(self, pos):
        if self.game_over and self.play_again_button and self.play_again_button.collidepoint(pos):
            self.load_scores()  # Reload scores to include the just finished game
            self.reset_game()
            return
        
        if self.show_feedback or self.game_over:
            return
            
        for i in range(4):
            area = pygame.Rect(50, 300 + i * 40, self.screen_width - 100, 30)
            if area.collidepoint(pos):
                self.selected_answer = i
                self.submit_answer()
                break

    def submit_answer(self):
        if self.selected_answer == -1 or self.game_over or self.show_feedback:
            return
            
        question = self.questions[self.current_question]
        is_correct = question["answers"][self.selected_answer]["correct"]
        self.show_correct_answer = not is_correct
        bomb_game.answer_question(int(is_correct))
        
        if is_correct:
            self.score += 10
            
        self.show_feedback = True
        self.feedback_time = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        delta = (now - self.last_time) / 1000.0
        self.last_time = now
        
        if self.show_feedback and (now - self.feedback_time) > 1000:
            self.show_feedback = False
            self.show_correct_answer = False
            self.selected_answer = -1
            self.current_question += 1
            
            if self.current_question >= len(self.questions):
                self.won_game = self.score >= 300
                self.game_over = True
                if not self.won_game:
                    self.explosion_sound.play()
            else:
                bomb_game.init_game(len(self.questions))
        elif not self.game_over:
            if bomb_game.update_timer(delta):
                self.game_over = True
                self.won_game = self.score >= 300
                if not self.won_game:
                    self.explosion_sound.play()

    def run(self):
        self.load_scores()
        running = True
        
        while running:
            self.screen.fill(WHITE)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen:
                            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        else:
                            self.screen = pygame.display.set_mode((1500, 700), pygame.RESIZABLE)
                        self.screen_width, self.screen_height = self.screen.get_size()
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.screen_width, self.screen_height = event.w, event.h

            fuse = bomb_game.get_fuse_percentage()
            self.draw_bomb(fuse)
            self.draw_score()
            self.draw_timer()
            
            if not self.game_over:
                self.draw_question()
            else:
                self.draw_game_over()
                
            pygame.display.flip()
            self.clock.tick(60)
            self.update()
            
        pygame.quit()
        bomb_game.free_game()

if __name__ == "__main__":
    game = BeatTheBombGame()
    game.run()