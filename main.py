import pygame
import math
from dataclasses import dataclass



pygame.init()
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()

surface = pygame.Surface((500,500), pygame.SRCALPHA)
pygame.font.init()

font = pygame.font.SysFont('Arial', 30)


soften = 1
g_const = 200

@dataclass
class VecTwo:
    x: float
    y: float

def length_val(vec2_a: VecTwo) -> float:
    return vec2_a.x*vec2_a.x + vec2_a.y*vec2_a.y

def add(vec2_a: VecTwo, vec2_b: VecTwo) -> VecTwo:
    xr = vec2_a.x + vec2_b.x
    yr = vec2_a.y + vec2_b.y
    return VecTwo(xr, yr)

def sub(vec2_a: VecTwo, vec2_b: VecTwo) -> VecTwo:
    xr = vec2_a.x - vec2_b.x
    yr = vec2_a.y - vec2_b.y
    return VecTwo(xr, yr)

def multi(vec2_a: VecTwo, val: float) -> VecTwo:
    xr = vec2_a.x * val
    yr = vec2_a.y * val
    return VecTwo(xr, yr)

class Partical:
    def __init__(self, mass, radius, vel: VecTwo, pos: VecTwo, colour):
        self.mass = mass
        self.radius = radius
        self.pos = pos
        self.vel = vel
        self.colour = colour
        self.prev_pos = VecTwo(pos.x, pos.y)

    def gravForce(self, other: "Partical") -> VecTwo:
        r = sub(other.pos, self.pos)
        cap = max(soften, 0.5*(self.radius+other.radius))
        dist_inv = 1/math.sqrt(length_val(r) + cap*cap)
        inv_r3 = dist_inv*dist_inv*dist_inv
        mag = g_const*self.mass*other.mass*inv_r3
        F_MAX = 1e5
        f = multi(r, mag)
        return clamp(f, F_MAX)
    
    def impli(self, force: VecTwo, dt:float):
        a = multi(force, 1/self.mass)
        self.vel = add(self.vel, multi(a, dt))
        self.pos = add(self.pos, multi(self.vel, dt))

def apply_walls(p: Partical, width: int, height: int, bounce: float = 0.9):
    if p.pos.x < p.radius:
        p.pos.x = p.radius
        p.vel.x = -p.vel.x * bounce
    elif p.pos.x > width - p.radius:
        p.pos.x = width - p.radius
        p.vel.x = -p.vel.x * bounce
    if p.pos.y < p.radius:
        p.pos.y = p.radius
        p.vel.y = -p.vel.y * bounce
    elif p.pos.y > height - p.radius:
        p.pos.y = height - p.radius
        p.vel.y = -p.vel.y * bounce

def clamp(vec: VecTwo, max_mag: float) -> VecTwo:
    n = vec.x*vec.x + vec.y*vec.y
    if n <= max_mag*max_mag:
        return vec
    n = math.sqrt(n)
    m = max_mag/n
    return VecTwo(vec.x*m, vec.y*m)


running = True

particles = [
    Partical(800, 5, VecTwo( 10,  -10), VecTwo(300,200), (0,0,255)),
    Partical(800, 5, VecTwo( 10,  -10), VecTwo(200,300), (255,0,0)),
    Partical(800, 5, VecTwo( 0,  10), VecTwo(300,250), (0,255,0)),
    Partical(100000, 10, VecTwo( 0,  0), VecTwo(250,250), (255,255,0))
]

stars = [
    VecTwo(26, 57),  VecTwo(118, 34), VecTwo(212, 115), VecTwo(297, 70),  VecTwo(415, 161),
    VecTwo(56, 412), VecTwo(138, 252), VecTwo(248, 302), VecTwo(335, 228), VecTwo(439, 38),
    VecTwo(83, 190), VecTwo(164, 413), VecTwo(240, 24),  VecTwo(322, 362), VecTwo(374, 452),
    VecTwo(461, 321), VecTwo(94, 338), VecTwo(196, 472), VecTwo(276, 168), VecTwo(382, 292),
]



while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    forces = [VecTwo(0.0, 0.0) for _ in particles]
    for i in range(len(particles)):
        for j in range(i+1, len(particles)):
            f = particles[i].gravForce(particles[j])
            forces[i] = add(forces[i], f)
            forces[j] = sub(forces[j], f)

    dt = min(clock.tick(60)/1000, 1/3)
    
    for p, f in zip(particles, forces):
        p.impli(f, dt)
        apply_walls(p, *screen.get_size(), bounce=0.95)
        
        prev_x = int(p.prev_pos.x)
        prev_y = int(p.prev_pos.y)
        prev_holder = (prev_x, prev_y)
        curr_x = int(p.pos.x)
        curr_y = int(p.pos.y)
        curr_pos = (curr_x, curr_y)
        pygame.draw.line(surface, (*p.colour, 150), prev_holder, curr_pos, 2)

        p.prev_pos.x = p.pos.x
        p.prev_pos.y = p.pos.y

    screen.fill("black")
    for s in stars:
        pygame.draw.circle(screen, (100, 100, 100), (int(s.x), int(s.y)), 1)

    surface.fill((0, 0, 0, 1), special_flags=pygame.BLEND_RGBA_SUB)
    text_val = font.render('Grav-Force Simulator', True, (255, 255, 255))


    screen.blit(surface, (0, 0))

    for p in particles:
        pygame.draw.circle(screen, p.colour, (int(p.pos.x), int(p.pos.y)), p.radius)
    screen.blit(text_val, (125, 10))
    pygame.display.flip()

pygame.quit()