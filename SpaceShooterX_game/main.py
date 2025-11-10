import os
import sys
import json
import random
import math
import wave
import struct
import pygame
from pygame import Rect

# Constants
WIDTH, HEIGHT = 640, 800
FPS = 60
PLAYER_SPEED = 6
BULLET_SPEED = -10
ENEMY_BASE_SPEED = 2.0
SPAWN_INTERVAL = 900  # milliseconds
POWERUP_CHANCE = 0.2
MAX_WEAPON_LEVEL = 3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HIGHSCORE_FILE = os.path.join(BASE_DIR, "highscore.json")
BGM_FILE = os.path.join(BASE_DIR, "bgm.wav")
SND_SHOOT = os.path.join(BASE_DIR, "snd_shoot.wav")
SND_EXPLODE = os.path.join(BASE_DIR, "snd_explode.wav")

# Utility: generate simple WAV sounds (sine tones) if not present
def generate_sine_wav(path, freq=440.0, duration=2.0, volume=0.2, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    with wave.open(path, 'w') as wav:
        nchannels = 1
        sampwidth = 2
        wav.setparams((nchannels, sampwidth, sample_rate, n_samples, 'NONE', 'not compressed'))
        max_amp = 32767 * volume
        for i in range(n_samples):
            t = float(i) / sample_rate
            sample = int(max_amp * math.sin(2 * math.pi * freq * t))
            wav.writeframes(struct.pack('<h', sample))

def ensure_sounds():
    if not os.path.exists(BGM_FILE):
        # generate a short looping background "melody" by combining tones sequentially
        # We'll create a 5-second clip that will loop
        sample_rate = 44100
        duration = 5.0
        n_samples = int(sample_rate * duration)
        freqs = [220.0, 277.0, 330.0, 392.0]  # A set of notes
        with wave.open(BGM_FILE, 'w') as wav:
            nchannels = 1
            sampwidth = 2
            wav.setparams((nchannels, sampwidth, sample_rate, n_samples, 'NONE', 'not compressed'))
            max_amp = 16000
            for i in range(n_samples):
                t = float(i) / sample_rate
                # layered tones to sound nicer
                v = 0.0
                for j, f in enumerate(freqs):
                    # small amplitude envelope
                    v += (max_amp // (j + 1)) * math.sin(2 * math.pi * f * t) * (0.5 + 0.5 * math.sin(0.5 * t + j))
                # clip
                sample = max(-32767, min(32767, int(v * 0.25)))
                wav.writeframes(struct.pack('<h', sample))
    if not os.path.exists(SND_SHOOT):
        generate_sine_wav(SND_SHOOT, freq=880.0, duration=0.08, volume=0.6)
    if not os.path.exists(SND_EXPLODE):
        generate_sine_wav(SND_EXPLODE, freq=120.0, duration=0.2, volume=0.7)

# High score helpers
def load_highscore():
    try:
        with open(HIGHSCORE_FILE, 'r') as f:
            data = json.load(f)
            return int(data.get('highscore', 0))
    except Exception:
        return 0

def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE, 'w') as f:
            json.dump({'highscore': int(score)}, f)
    except Exception as e:
        print("Failed to save highscore:", e)

# Game objects
class Player:
    def __init__(self):
        self.width = 40
        self.height = 24
        self.x = WIDTH // 2
        self.y = HEIGHT - 60
        self.speed = PLAYER_SPEED
        self.rect = Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)
        self.cooldown = 250  # ms
        self.last_shot = 0
        self.lives = 3
        self.weapon_level = 1

    def move(self, dx):
        self.x += dx * self.speed
        self.x = max(self.width // 2, min(WIDTH - self.width // 2, self.x))
        self.rect.centerx = int(self.x)

    def can_shoot(self, now):
        return now - self.last_shot >= self.cooldown

    def shoot(self, now):
        self.last_shot = now
        bullets = []
        if self.weapon_level == 1:
            bullets.append(Bullet(self.x, self.y - self.height // 2, 0))
        elif self.weapon_level == 2:
            bullets.append(Bullet(self.x - 10, self.y - self.height // 2, -0.05))
            bullets.append(Bullet(self.x + 10, self.y - self.height // 2, 0.05))
        else:
            bullets.append(Bullet(self.x, self.y - self.height // 2, 0))
            bullets.append(Bullet(self.x - 14, self.y - self.height // 2, -0.12))
            bullets.append(Bullet(self.x + 14, self.y - self.height // 2, 0.12))
        return bullets

    def draw(self, surf):
        # simple spaceship as polygon
        points = [
            (self.x, self.y - self.height // 2),
            (self.x - self.width // 2, self.y + self.height // 2),
            (self.x + self.width // 2, self.y + self.height // 2),
        ]
        pygame.draw.polygon(surf, (50, 200, 255), points)
        # cockpit
        pygame.draw.circle(surf, (255, 255, 255), (int(self.x), int(self.y - 4)), 4)

class Bullet:
    def __init__(self, x, y, xvel=0.0):
        self.x = x
        self.y = y
        self.radius = 4
        self.vx = xvel * 10
        self.vy = BULLET_SPEED
        self.rect = Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.topleft = (int(self.x - self.radius), int(self.y - self.radius))

    def draw(self, surf):
        pygame.draw.circle(surf, (255, 240, 80), (int(self.x), int(self.y)), self.radius)

class Enemy:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.size = random.randint(24, 48)
        self.speed = speed
        self.rect = Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)
        self.color = (255, random.randint(80, 200), random.randint(40, 120))

    def update(self):
        self.y += self.speed
        self.rect.topleft = (int(self.x - self.size//2), int(self.y - self.size//2))

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)
        # eyes
        pygame.draw.circle(surf, (0,0,0), (int(self.x - self.size*0.18), int(self.y - self.size*0.08)), max(1, self.size//12))
        pygame.draw.circle(surf, (0,0,0), (int(self.x + self.size*0.18), int(self.y - self.size*0.08)), max(1, self.size//12))

class Powerup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 18
        self.vy = 2.5
        self.rect = Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)

    def update(self):
        self.y += self.vy
        self.rect.topleft = (int(self.x - self.size//2), int(self.y - self.size//2))

    def draw(self, surf):
        # draw a star-ish shape
        cx, cy = int(self.x), int(self.y)
        points = []
        for i in range(5):
            ang = i * (2*math.pi/5) - math.pi/2
            x = cx + int(math.cos(ang) * self.size//2)
            y = cy + int(math.sin(ang) * self.size//2)
            points.append((x,y))
        pygame.draw.polygon(surf, (255, 220, 30), points)

# Main game class
class SpaceShooter:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        ensure_sounds()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Shooter")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Consolas', 24)
        self.bigfont = pygame.font.SysFont('Consolas', 48)

        # Load sounds
        try:
            pygame.mixer.music.load(BGM_FILE)
            pygame.mixer.music.set_volume(0.4)
        except Exception as e:
            print("bgm load error", e)
        try:
            self.snd_shoot = pygame.mixer.Sound(SND_SHOOT)
            self.snd_explode = pygame.mixer.Sound(SND_EXPLODE)
        except Exception as e:
            self.snd_shoot = None
            self.snd_explode = None

        self.reset_game()
        self.highscore = load_highscore()
        self.state = 'menu'  # menu, playing, paused, gameover

    def reset_game(self):
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.powerups = []
        self.score = 0
        self.enemy_speed = ENEMY_BASE_SPEED
        self.last_spawn = pygame.time.get_ticks()
        self.spawn_interval = SPAWN_INTERVAL
        self.level = 1

    def spawn_enemy(self):
        x = random.randint(30, WIDTH - 30)
        e = Enemy(x, -40, self.enemy_speed + random.random()*0.8)
        self.enemies.append(e)

    def update_difficulty(self):
        # every 10 points increase enemy speed slightly
        target_level = 1 + self.score // 10
        if target_level != self.level:
            self.level = target_level
            self.enemy_speed = ENEMY_BASE_SPEED + 0.6 * (self.level - 1)
            # tighten spawn interval a bit
            self.spawn_interval = max(350, SPAWN_INTERVAL - (self.level-1)*60)

    def run(self):
        # Start bgm
        try:
            pygame.mixer.music.play(-1)
        except Exception:
            pass

        running = True
        while running:
            dt = self.clock.tick(FPS)
            now = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == 'menu' and event.key == pygame.K_RETURN:
                        self.reset_game()
                        self.state = 'playing'
                    elif self.state == 'gameover' and event.key == pygame.K_RETURN:
                        self.reset_game()
                        self.state = 'playing'
                    elif event.key == pygame.K_p:
                        if self.state == 'playing':
                            self.state = 'paused'
                        elif self.state == 'paused':
                            self.state = 'playing'
                    elif event.key == pygame.K_ESCAPE:
                        if self.state == 'playing':
                            self.state = 'paused'
                        elif self.state == 'paused':
                            self.state = 'playing'

            keys = pygame.key.get_pressed()
            if self.state == 'playing':
                dx = 0
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    dx = -1
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    dx = 1
                self.player.move(dx)

                if keys[pygame.K_SPACE] and self.player.can_shoot(now):
                    bullets = self.player.shoot(now)
                    self.bullets.extend(bullets)
                    if self.snd_shoot:
                        self.snd_shoot.play()

                # spawn enemies
                if now - self.last_spawn >= self.spawn_interval:
                    self.spawn_enemy()
                    self.last_spawn = now

                # updates
                for b in list(self.bullets):
                    b.update()
                    if b.y < -10 or b.y > HEIGHT + 10:
                        self.bullets.remove(b)

                for e in list(self.enemies):
                    e.update()
                    if e.y - e.size//2 > HEIGHT:
                        # enemy crossed screen: player loses life
                        self.enemies.remove(e)
                        self.player.lives -= 1
                        if self.snd_explode:
                            self.snd_explode.play()
                        if self.player.lives <= 0:
                            # game over
                            if self.score > self.highscore:
                                self.highscore = self.score
                                save_highscore(self.highscore)
                            self.state = 'gameover'

                for p in list(self.powerups):
                    p.update()
                    if p.y > HEIGHT + 20:
                        self.powerups.remove(p)

                # collisions bullets vs enemies
                for b in list(self.bullets):
                    for e in list(self.enemies):
                        if b.rect.colliderect(e.rect):
                            try:
                                self.bullets.remove(b)
                            except ValueError:
                                pass
                            try:
                                self.enemies.remove(e)
                            except ValueError:
                                pass
                            self.score += 1
                            if self.snd_explode:
                                self.snd_explode.play()
                            # chance to drop power-up
                            if random.random() < POWERUP_CHANCE:
                                self.powerups.append(Powerup(e.x, e.y))
                            break

                # player vs powerups
                for p in list(self.powerups):
                    if self.player.rect.colliderect(p.rect):
                        self.powerups.remove(p)
                        # upgrade weapon
                        self.player.weapon_level = min(MAX_WEAPON_LEVEL, self.player.weapon_level + 1)

                # update difficulty
                self.update_difficulty()

            # Drawing
            self.screen.fill((12, 12, 28))
            if self.state == 'menu':
                title = self.bigfont.render('SPACE SHOOTER', True, (255,255,255))
                self.screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
                info = self.font.render('Press ENTER to start  •  Arrow keys to move  •  Space to shoot', True, (200,200,200))
                self.screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT//2))
                info2 = self.font.render('P to pause during play. Collect stars to upgrade weapon.', True, (180,180,180))
                self.screen.blit(info2, (WIDTH//2 - info2.get_width()//2, HEIGHT//2 + 30))
                hs = self.font.render(f'High Score: {self.highscore}', True, (255,200,120))
                self.screen.blit(hs, (10, 10))

            elif self.state in ('playing', 'paused'):
                # Draw player
                self.player.draw(self.screen)

                # Draw bullets
                for b in self.bullets:
                    b.draw(self.screen)

                # Draw enemies
                for e in self.enemies:
                    e.draw(self.screen)

                # Draw powerups
                for p in self.powerups:
                    p.draw(self.screen)

                # HUD: score, lives, weapon level
                score_surf = self.font.render(f'Score: {self.score}', True, (220,220,220))
                self.screen.blit(score_surf, (10, 10))
                level_surf = self.font.render(f'Lv: {self.level}  Weapon: {self.player.weapon_level}', True, (200,200,255))
                self.screen.blit(level_surf, (10, 40))

                # Lives / health bar
                for i in range(self.player.lives):
                    pygame.draw.rect(self.screen, (200,40,40), (WIDTH - 20 - i*26, 10, 20, 12))

                # If paused overlay
                if self.state == 'paused':
                    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    overlay.fill((0,0,0,160))
                    self.screen.blit(overlay, (0,0))
                    paused = self.bigfont.render('PAUSED', True, (255,255,255))
                    self.screen.blit(paused, (WIDTH//2 - paused.get_width()//2, HEIGHT//2 - paused.get_height()//2))

            elif self.state == 'gameover':
                over = self.bigfont.render('GAME OVER', True, (255,180,120))
                self.screen.blit(over, (WIDTH//2 - over.get_width()//2, HEIGHT//3))
                s = self.font.render(f'Your Score: {self.score}', True, (230,230,230))
                self.screen.blit(s, (WIDTH//2 - s.get_width()//2, HEIGHT//2))
                hs = self.font.render(f'High Score: {self.highscore}', True, (255,230,140))
                self.screen.blit(hs, (WIDTH//2 - hs.get_width()//2, HEIGHT//2 + 30))
                info = self.font.render('Press ENTER to play again', True, (200,200,200))
                self.screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT//2 + 80))

            # FPS
            fps_surf = self.font.render(str(int(self.clock.get_fps())), True, (100,255,100))
            self.screen.blit(fps_surf, (WIDTH - 40, HEIGHT - 30))

            pygame.display.flip()

        pygame.quit()


if __name__ == '__main__':
    game = SpaceShooter()
    game.run()
