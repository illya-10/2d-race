import pygame
import sys
import os
import math

pygame.init()
pygame.mixer.init()

# =============================
# НАЛАШТУВАННЯ
# =============================
FPS = 60
SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = SCREEN.get_size()
pygame.display.set_caption("2D Racing PRO")

FONT_BIG = pygame.font.SysFont("arial", 70, bold=True)
FONT = pygame.font.SysFont("arial", 40)
FONT_SMALL = pygame.font.SysFont("arial", 28)

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
DARK = (25, 25, 35)
GRAY = (60, 60, 80)
BLUE = (70, 130, 255)
GREEN = (50, 200, 120)
RED = (200, 50, 50)

# =============================
# КНОПКА
# =============================
class Button:
    def __init__(self, text, x, y, w, h, color=GRAY):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = BLUE

    def draw(self):
        mouse = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse) else self.color
        pygame.draw.rect(SCREEN, current_color, self.rect, border_radius=15)
        pygame.draw.rect(SCREEN, WHITE, self.rect, 2, border_radius=15)

        text = FONT_SMALL.render(self.text, True, WHITE)
        SCREEN.blit(text, text.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


# =============================
# МАШИНА
# =============================
class Car:
    def __init__(self, image, x, y, controls):
        self.original = pygame.transform.scale(image, (70, 120))
        self.image = self.original
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = 0
        self.speed = 0
        self.max_speed = 8
        self.acceleration = 0.3
        self.friction = 0.05
        self.controls = controls
        self.laps = 0
        self.finished = False

    def update(self, keys):
        if keys[self.controls["up"]]:
            self.speed += self.acceleration
        else:
            self.speed -= self.friction

        if keys[self.controls["down"]]:
            self.speed -= self.acceleration

        self.speed = max(-3, min(self.speed, self.max_speed))

        if keys[self.controls["left"]]:
            self.angle += 4
        if keys[self.controls["right"]]:
            self.angle -= 4

        rad = math.radians(self.angle)
        self.rect.x += -self.speed * math.sin(rad)
        self.rect.y += -self.speed * math.cos(rad)

        self.image = pygame.transform.rotate(self.original, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def draw(self):
        SCREEN.blit(self.image, self.rect)


# =============================
# ГРА
# =============================
class Game:
    def __init__(self):
        self.state = "menu"
        self.lap_options = [1, 5, 10]
        self.selected_laps = 1

        # Завантаження машин
        self.cars = []
        car_folder = "assets/cars"
        for file in os.listdir(car_folder):
            if file.endswith(".png"):
                self.cars.append(pygame.image.load(os.path.join(car_folder, file)).convert_alpha())

        self.selected_car1 = 0
        self.selected_car2 = 1

        # Завантаження трас
        self.tracks = []
        track_folder = "assets/tracks"
        for file in os.listdir(track_folder):
            if file.endswith(".png"):
                self.tracks.append(pygame.image.load(os.path.join(track_folder, file)).convert())

        self.selected_track = 0

    # ================= MENU =================
    def menu(self):
        play_btn = Button("ГРАТИ", WIDTH//2-200, HEIGHT//2, 400, 80, GREEN)
        exit_btn = Button("ВИЙТИ", WIDTH//2-200, HEIGHT//2+120, 400, 80, RED)

        while self.state == "menu":
            SCREEN.fill(DARK)

            title = FONT_BIG.render("2D RACING PRO", True, WHITE)
            SCREEN.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//3)))

            play_btn.draw()
            exit_btn.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if play_btn.is_clicked(event):
                    self.state = "select"
                if exit_btn.is_clicked(event):
                    pygame.quit()
                    sys.exit()

            pygame.display.update()
            clock.tick(FPS)

    # ================= SELECT =================
    def select(self):
        start_btn = Button("СТАРТ", WIDTH//2-200, HEIGHT-120, 400, 70, GREEN)

        while self.state == "select":
            SCREEN.fill((20, 40, 60))

            text = FONT.render("Вибір кіл:", True, WHITE)
            SCREEN.blit(text, (100, 100))

            # Вибір кіл
            for i, lap in enumerate(self.lap_options):
                btn = Button(f"{lap} КРУГІВ", 100, 160 + i*80, 250, 60)
                btn.draw()
                for event in pygame.event.get():
                    if btn.is_clicked(event):
                        self.selected_laps = lap

            # Вибір траси
            track_preview = pygame.transform.scale(self.tracks[self.selected_track], (400, 300))
            SCREEN.blit(track_preview, (WIDTH-500, 150))

            start_btn.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if start_btn.is_clicked(event):
                    self.state = "race"

            pygame.display.update()
            clock.tick(FPS)

    # ================= RACE =================
    def race(self):
        track = pygame.transform.scale(self.tracks[self.selected_track], (WIDTH, HEIGHT))

        finish_line = pygame.Rect(WIDTH//2-100, HEIGHT//2-10, 200, 20)

        car1 = Car(self.cars[self.selected_car1], WIDTH//2-100, HEIGHT//2+100,
                   {"up": pygame.K_UP, "down": pygame.K_DOWN,
                    "left": pygame.K_LEFT, "right": pygame.K_RIGHT})

        car2 = Car(self.cars[self.selected_car2], WIDTH//2+100, HEIGHT//2+100,
                   {"up": pygame.K_w, "down": pygame.K_s,
                    "left": pygame.K_a, "right": pygame.K_d})

        while self.state == "race":
            SCREEN.blit(track, (0, 0))
            pygame.draw.rect(SCREEN, WHITE, finish_line)

            keys = pygame.key.get_pressed()
            car1.update(keys)
            car2.update(keys)

            if car1.rect.colliderect(finish_line):
                car1.laps += 1
            if car2.rect.colliderect(finish_line):
                car2.laps += 1

            if car1.laps >= self.selected_laps:
                self.winner("Гравець 1 ПЕРЕМІГ!")
            if car2.laps >= self.selected_laps:
                self.winner("Гравець 2 ПЕРЕМІГ!")

            car1.draw()
            car2.draw()

            hud1 = FONT_SMALL.render(f"P1: {car1.laps}/{self.selected_laps}", True, WHITE)
            hud2 = FONT_SMALL.render(f"P2: {car2.laps}/{self.selected_laps}", True, WHITE)
            SCREEN.blit(hud1, (20, 20))
            SCREEN.blit(hud2, (20, 60))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()
            clock.tick(FPS)

    # ================= WIN SCREEN =================
    def winner(self, text):
        again_btn = Button("ГРАТИ ЩЕ", WIDTH//2-200, HEIGHT//2+100, 400, 70, GREEN)

        while True:
            SCREEN.fill((10, 10, 20))
            msg = FONT_BIG.render(text, True, GREEN)
            SCREEN.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2-50)))

            again_btn.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if again_btn.is_clicked(event):
                    self.state = "menu"
                    return

            pygame.display.update()
            clock.tick(FPS)

    def run(self):
        while True:
            if self.state == "menu":
                self.menu()
            if self.state == "select":
                self.select()
            if self.state == "race":
                self.race()


game = Game()
game.run()
