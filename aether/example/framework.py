"""
╔══════════════════════════════════════════════════════════════╗
║   3D Sandbox Survival Crafting Game Framework               ║
║   ──────────────────────────────────────────────────────     ║
║   Systems: Terrain Gen, Voxel World, First-Person Camera,   ║
║   Block Place/Break, Inventory, Crafting, Survival Stats,   ║
║   Day/Night Cycle, Chunk Loading, HUD                       ║
║                                                              ║
║   Controls:                                                  ║
║     WASD          Move                                       ║
║     Space         Jump                                       ║
║     Mouse         Look around                                ║
║     Left Click    Break block                                ║
║     Right Click   Place block                                ║
║     1-9 / Scroll  Select hotbar slot                         ║
║     E             Inventory                                  ║
║     C             Crafting menu                              ║
║     F3            Debug overlay                              ║
║     R             Respawn                                    ║
║     ESC           Release/capture mouse                      ║
║                                                              ║
║   pip install pygame PyOpenGL numpy                          ║
╚══════════════════════════════════════════════════════════════╝
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import random
import sys

# ═══════════════════════════ CONSTANTS ═══════════════════════════
WINDOW_W, WINDOW_H = 1280, 720
CHUNK_SIZE = 16
WORLD_HEIGHT = 64
RENDER_DISTANCE = 3          # chunks in each direction
GRAVITY = -25.0
JUMP_FORCE = 8.5
PLAYER_HEIGHT = 1.8
PLAYER_WIDTH = 0.6
PLAYER_SPEED = 5.0
PLAYER_SPRINT_SPEED = 8.5
MOUSE_SENS = 0.002

# ───────────── Block Type Registry ─────────────
class B:
    """Block type constants."""
    AIR = 0; GRASS = 1; DIRT = 2; STONE = 3; WOOD = 4; LEAVES = 5
    SAND = 6; WATER = 7; COAL_ORE = 8; IRON_ORE = 9; PLANKS = 10
    COBBLESTONE = 11; CRAFTING_TABLE = 12; FURNACE = 13; GLASS = 14
    BRICK = 15

BLOCK_COLOR = {
    B.GRASS: (.30, .72, .18),  B.DIRT: (.55, .32, .10),
    B.STONE: (.52, .52, .52),  B.WOOD: (.62, .42, .12),
    B.LEAVES: (.15, .52, .12), B.SAND: (.91, .86, .59),
    B.WATER: (.22, .38, .82),  B.COAL_ORE: (.32, .32, .32),
    B.IRON_ORE: (.62, .52, .42), B.PLANKS: (.72, .52, .22),
    B.COBBLESTONE: (.44, .44, .44), B.CRAFTING_TABLE: (.60, .42, .16),
    B.FURNACE: (.46, .46, .46), B.GLASS: (.75, .85, .92),
    B.BRICK: (.72, .30, .22),
}
BLOCK_NAME = {
    B.GRASS:"Grass", B.DIRT:"Dirt", B.STONE:"Stone", B.WOOD:"Wood",
    B.LEAVES:"Leaves", B.SAND:"Sand", B.WATER:"Water", B.COAL_ORE:"Coal Ore",
    B.IRON_ORE:"Iron Ore", B.PLANKS:"Planks", B.COBBLESTONE:"Cobblestone",
    B.CRAFTING_TABLE:"Crafting Table", B.FURNACE:"Furnace", B.GLASS:"Glass",
    B.BRICK:"Brick",
}
TRANSPARENT = {B.AIR: True, B.WATER: True, B.GLASS: True}

# ═══════════════════════════ NOISE ═══════════════════════════════
class PerlinNoise:
    """2D Perlin-like noise for terrain generation."""
    def __init__(self, seed=0):
        rng = random.Random(seed)
        self.p = list(range(256)); rng.shuffle(self.p)
        self.p *= 2
        self.g = [(math.cos(2*math.pi*i/256), math.sin(2*math.pi*i/256))
                   for i in range(256)]

    @staticmethod
    def _fade(t): return t*t*t*(t*(t*6-15)+10)
    @staticmethod
    def _lerp(a,b,t): return a+t*(b-a)

    def _grad(self, h, x, y):
        g = self.g[h % 256]; return g[0]*x + g[1]*y

    def noise2(self, x, y):
        X, Y = int(math.floor(x)) & 255, int(math.floor(y)) & 255
        x -= math.floor(x); y -= math.floor(y)
        u, v = self._fade(x), self._fade(y)
        aa = self.p[self.p[X]+Y];     ba = self.p[self.p[X+1]+Y]
        ab = self.p[self.p[X]+Y+1];   bb = self.p[self.p[X+1]+Y+1]
        return self._lerp(
            self._lerp(self._grad(aa,x,y),   self._grad(ba,x-1,y),   u),
            self._lerp(self._grad(ab,x,y-1), self._grad(bb,x-1,y-1), u), v)

    def fbm(self, x, y, octaves=4, persistence=.5, lacunarity=2.0):
        total = amp = 0.; freq = 1.; mx = 0.
        for _ in range(octaves):
            total += self.noise2(x*freq, y*freq)*amp if amp else self.noise2(x*freq, y*freq)
            amp_val = persistence ** _; total += self.noise2(x*freq, y*freq)*amp_val
            mx += amp_val; freq *= lacunarity
        return total / mx if mx else 0

# ═══════════════════════════ CHUNK ════════════════════════════════
class Chunk:
    """A 16×64×16 column of voxels with display-list rendering."""
    __slots__ = ('cx','cz','blocks','dl','dirty','solid')

    def __init__(self, cx, cz):
        self.cx, self.cz = cx, cz
        self.blocks = np.zeros((CHUNK_SIZE, WORLD_HEIGHT, CHUNK_SIZE), dtype=np.uint8)
        self.dl = None; self.dirty = True; self.solid = 0

    # ── Block access ──
    def get(self, x, y, z):
        if 0<=x<CHUNK_SIZE and 0<=y<WORLD_HEIGHT and 0<=z<CHUNK_SIZE:
            return int(self.blocks[x,y,z])
        return B.AIR

    def put(self, x, y, z, bt):
        if 0<=x<CHUNK_SIZE and 0<=y<WORLD_HEIGHT and 0<=z<CHUNK_SIZE:
            old = self.blocks[x,y,z]; self.blocks[x,y,z] = bt
            if old==B.AIR and bt!=B.AIR: self.solid+=1
            elif old!=B.AIR and bt==B.AIR: self.solid-=1
            self.dirty = True

    # ── Face visibility (only render exposed faces) ──
    def _face_vis(self, world, x, y, z, dx, dy, dz):
        ny = y+dy
        if ny<0 or ny>=WORLD_HEIGHT: return True
        nx, nz = x+dx, z+dz
        if not (0<=nx<CHUNK_SIZE and 0<=nz<CHUNK_SIZE):
            nb = world.get_block(self.cx*CHUNK_SIZE+nx, ny, self.cz*CHUNK_SIZE+nz)
        else:
            nb = int(self.blocks[nx,ny,nz])
        return TRANSPARENT.get(nb, False)

    # ── Build OpenGL display list ──
    def build_dl(self, world):
        if self.dl: glDeleteLists(self.dl, 1)
        self.dl = glGenLists(1)
        glNewList(self.dl, GL_COMPILE)
        wx0, wz0 = self.cx*CHUNK_SIZE, self.cz*CHUNK_SIZE
        glBegin(GL_QUADS)
        for x in range(CHUNK_SIZE):
            for y in range(WORLD_HEIGHT):
                for z in range(CHUNK_SIZE):
                    bt = int(self.blocks[x,y,z])
                    if bt==B.AIR: continue
                    col = BLOCK_COLOR.get(bt, (1,1,1))
                    px, py, pz = wx0+x, y, wz0+z
                    # 6 face checks
                    if self._face_vis(world,x,y,z, 0, 1, 0):  self._quad_top(px,py,pz,col,bt)
                    if self._face_vis(world,x,y,z, 0,-1, 0):  self._quad_bot(px,py,pz,col,bt)
                    if self._face_vis(world,x,y,z, 0, 0, 1):  self._quad_fr (px,py,pz,col,bt)
                    if self._face_vis(world,x,y,z, 0, 0,-1):  self._quad_bk (px,py,pz,col,bt)
                    if self._face_vis(world,x,y,z, 1, 0, 0):  self._quad_rt (px,py,pz,col,bt)
                    if self._face_vis(world,x,y,z,-1, 0, 0):  self._quad_lt (px,py,pz,col,bt)
        glEnd()
        glEndList()
        self.dirty = False

    # ── Face renderers with per-face shading & grass special case ──
    @staticmethod
    def _set_col(col, shade, bt, face):
        if bt==B.GRASS:
            if face=='top':    glColor3f(.30*shade, .72*shade, .18*shade)
            elif face=='bot':  glColor3f(.55*shade, .32*shade, .10*shade)
            else:              glColor3f(.48*shade, .38*shade, .16*shade)
        elif bt==B.WOOD and face in ('top','bot'):
            glColor3f(.50*shade, .36*shade, .10*shade)
        else:
            glColor3f(col[0]*shade, col[1]*shade, col[2]*shade)

    def _quad_top(self,x,y,z,c,bt):
        s=1.0; self._set_col(c,s,bt,'top'); glNormal3f(0,1,0)
        glVertex3f(x,y+1,z); glVertex3f(x+1,y+1,z)
        glVertex3f(x+1,y+1,z+1); glVertex3f(x,y+1,z+1)
    def _quad_bot(self,x,y,z,c,bt):
        s=.5; self._set_col(c,s,bt,'bot'); glNormal3f(0,-1,0)
        glVertex3f(x,y,z+1); glVertex3f(x+1,y,z+1)
        glVertex3f(x+1,y,z); glVertex3f(x,y,z)
    def _quad_fr(self,x,y,z,c,bt):
        s=.85; self._set_col(c,s,bt,'fr'); glNormal3f(0,0,1)
        glVertex3f(x,y,z+1); glVertex3f(x,y+1,z+1)
        glVertex3f(x+1,y+1,z+1); glVertex3f(x+1,y,z+1)
    def _quad_bk(self,x,y,z,c,bt):
        s=.65; self._set_col(c,s,bt,'bk'); glNormal3f(0,0,-1)
        glVertex3f(x+1,y,z); glVertex3f(x+1,y+1,z)
        glVertex3f(x,y+1,z); glVertex3f(x,y,z)
    def _quad_rt(self,x,y,z,c,bt):
        s=.9; self._set_col(c,s,bt,'rt'); glNormal3f(1,0,0)
        glVertex3f(x+1,y,z+1); glVertex3f(x+1,y+1,z+1)
        glVertex3f(x+1,y+1,z); glVertex3f(x+1,y,z)
    def _quad_lt(self,x,y,z,c,bt):
        s=.7; self._set_col(c,s,bt,'lt'); glNormal3f(-1,0,0)
        glVertex3f(x,y,z); glVertex3f(x,y+1,z)
        glVertex3f(x,y+1,z+1); glVertex3f(x,y,z+1)

    def cleanup(self):
        if self.dl: glDeleteLists(self.dl, 1); self.dl = None

# ═══════════════════════════ WORLD ════════════════════════════════
class World:
    """Manages chunks, block access, and terrain generation."""
    def __init__(self, seed=None):
        self.seed = seed or random.randint(0, 999999)
        self.noise = PerlinNoise(self.seed)
        self.noise2 = PerlinNoise(self.seed + 100)  # secondary noise for biomes
        self.chunks = {}
        self.mods = {}  # player modifications: (x,y,z)->bt

    def _ck(self, cx, cz): return (cx, cz)

    def get_chunk(self, cx, cz): return self.chunks.get(self._ck(cx,cz))

    # ── World-coordinate block access ──
    def get_block(self, wx, wy, wz):
        if (wx,wy,wz) in self.mods: return self.mods[(wx,wy,wz)]
        cx = wx // CHUNK_SIZE if wx >= 0 else (wx - CHUNK_SIZE + 1) // CHUNK_SIZE
        cz = wz // CHUNK_SIZE if wz >= 0 else (wz - CHUNK_SIZE + 1) // CHUNK_SIZE
        ch = self.get_chunk(cx, cz)
        if ch is None: return B.AIR
        return ch.get(wx - cx*CHUNK_SIZE, wy, wz - cz*CHUNK_SIZE)

    def set_block(self, wx, wy, wz, bt):
        cx = wx // CHUNK_SIZE if wx >= 0 else (wx - CHUNK_SIZE + 1) // CHUNK_SIZE
        cz = wz // CHUNK_SIZE if wz >= 0 else (wz - CHUNK_SIZE + 1) // CHUNK_SIZE
        ch = self.get_chunk(cx, cz)
        if ch is None: return
        ch.put(wx - cx*CHUNK_SIZE, wy, wz - cz*CHUNK_SIZE, bt)
        self.mods[(wx,wy,wz)] = bt
        # Mark neighbor chunks dirty on border
        lx, lz = wx - cx*CHUNK_SIZE, wz - cz*CHUNK_SIZE
        for dcx, dcz in ((-1,0),(1,0),(0,-1),(0,1)):
            if (lx==0 and dcx==-1) or (lx==CHUNK_SIZE-1 and dcx==1) or \
               (lz==0 and dcz==-1) or (lz==CHUNK_SIZE-1 and dcz==1):
                nc = self.get_chunk(cx+dcx, cz+dcz)
                if nc: nc.dirty = True

    # ── Terrain generation ──
    def generate_chunk(self, cx, cz):
        key = self._ck(cx, cz)
        if key in self.chunks: return self.chunks[key]
        ch = Chunk(cx, cz)
        rng = random.Random(cx * 73856093 ^ cz * 19349663)

        for x in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                wx, wz = cx*CHUNK_SIZE+x, cz*CHUNK_SIZE+z
                # Height from fractal noise
                h = int(self.noise.fbm(wx*0.008, wz*0.008, 5, 0.5) * 20 + 25)
                h = max(1, min(WORLD_HEIGHT-2, h))

                # Biome value (temperature / moisture proxy)
                biome = self.noise2.fbm(wx*0.003, wz*0.003, 3, 0.5)

                for y in range(h):
                    if (wx,y,wz) in self.mods:
                        ch.put(x, y, z, self.mods[(wx,y,wz)])
                    else:
                        if y == h-1:
                            if h < 18:   ch.put(x,y,z, B.SAND)
                            elif biome > 0.3: ch.put(x,y,z, B.SAND)
                            else:        ch.put(x,y,z, B.GRASS)
                        elif y > h-4:   ch.put(x,y,z, B.DIRT)
                        else:
                            r = rng.random()
                            if y<12 and r<.025: ch.put(x,y,z, B.COAL_ORE)
                            elif y<8 and r<.015: ch.put(x,y,z, B.IRON_ORE)
                            else:                ch.put(x,y,z, B.STONE)
                # Water fill below sea level
                for y in range(h, 18):
                    if ch.get(x,y,z)==B.AIR: ch.put(x,y,z, B.WATER)

                # Trees
                if h >= 19 and rng.random() < 0.012 and biome <= 0.3:
                    self._tree(ch, x, h, z, rng)

        self.chunks[key] = ch
        return ch

    def _tree(self, ch, x, by, z, rng):
        trunk = rng.randint(4,6)
        for y in range(by, by+trunk):
            if 0<=y<WORLD_HEIGHT: ch.put(x,y,z, B.WOOD)
        top = by+trunk
        for ly in range(top-2, top+3):
            r = 2 if ly < top else 1
            for lx in range(-r, r+1):
                for lz in range(-r, r+1):
                    if abs(lx)==r and abs(lz)==r: continue
                    nx, nz = x+lx, z+lz
                    if 0<=nx<CHUNK_SIZE and 0<=nz<CHUNK_SIZE and 0<=ly<WORLD_HEIGHT:
                        if ch.get(nx,ly,nz)==B.AIR:
                            ch.put(nx,ly,nz, B.LEAVES)

    def ensure_chunks(self, px, pz):
        pcx, pcz = int(px)//CHUNK_SIZE, int(pz)//CHUNK_SIZE
        for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE+1):
            for dz in range(-RENDER_DISTANCE, RENDER_DISTANCE+1):
                if dx*dx+dz*dz <= RENDER_DISTANCE*RENDER_DISTANCE:
                    self.generate_chunk(pcx+dx, pcz+dz)

# ═══════════════════════════ PLAYER ═══════════════════════════════
class Player:
    """First-person player with physics, survival stats, inventory, raycasting."""
    def __init__(self, world):
        self.world = world
        self.x, self.y, self.z = 8., 40., 8.
        self.vx, self.vy, self.vz = 0., 0., 0.
        self.yaw, self.pitch = 0., 0.
        self.on_ground = False
        self.sprinting = False

        # Survival
        self.health = 20.; self.max_health = 20.
        self.hunger = 20.; self.max_hunger = 20.
        self.hunger_rate = 0.025  # per second

        # Inventory: {block_type: count}
        self.inv = {}
        self.hotbar = [B.DIRT, B.STONE, B.WOOD, B.PLANKS, B.COBBLESTONE,
                       B.GRASS, B.SAND, B.GLASS, B.BRICK]
        self.sel = 0
        self.inv_open = False
        self.craft_open = False
        self.reach = 7.

        # Raycast result
        self.target = None
        self.target_face = None

        # Starter items
        for bt, n in [(B.DIRT,64),(B.STONE,64),(B.WOOD,32),(B.PLANKS,64),
                       (B.COBBLESTONE,64),(B.GLASS,32),(B.BRICK,32)]:
            self.inv[bt] = n

    def add_item(self, bt, n=1):
        self.inv[bt] = self.inv.get(bt,0)+n
    def rem_item(self, bt, n=1):
        if self.inv.get(bt,0)>=n:
            self.inv[bt]-=n
            if self.inv[bt]<=0: del self.inv[bt]
            return True
        return False
    def sel_block(self):
        bt = self.hotbar[self.sel]
        return bt if self.inv.get(bt,0)>0 else None

    # ── Physics update ──
    def update(self, dt, keys):
        fwd = (-math.sin(self.yaw), 0, -math.cos(self.yaw))
        rgt = ( math.cos(self.yaw), 0, -math.sin(self.yaw))
        spd = PLAYER_SPRINT_SPEED if self.sprinting else PLAYER_SPEED
        dx = dz = 0.
        if keys.get(K_w): dx+=fwd[0]; dz+=fwd[2]
        if keys.get(K_s): dx-=fwd[0]; dz-=fwd[2]
        if keys.get(K_a): dx-=rgt[0]; dz-=rgt[2]
        if keys.get(K_d): dx+=rgt[0]; dz+=rgt[2]
        ln = math.sqrt(dx*dx+dz*dz)
        if ln>0: dx/=ln; dz/=ln
        self.vx, self.vz = dx*spd, dz*spd
        self.sprinting = keys.get(K_LSHIFT, False)

        self.vy += GRAVITY * dt
        if keys.get(K_SPACE) and self.on_ground:
            self.vy = JUMP_FORCE; self.on_ground = False

        # Move with collision per axis
        nx, ny, nz = self.x+self.vx*dt, self.y+self.vy*dt, self.z+self.vz*dt
        if not self._collides(nx, self.y, self.z): self.x = nx
        else: self.vx = 0
        if not self._collides(self.x, self.y, nz): self.z = nz
        else: self.vz = 0
        if not self._collides(self.x, ny, self.z):
            self.y = ny; self.on_ground = False
        else:
            if self.vy < 0: self.on_ground = True; self.y = math.floor(self.y)+.01
            self.vy = 0
        if self.y < -10: self.y = 40  # void safety

        # Survival
        hr = self.hunger_rate * (3 if self.sprinting else 1)
        self.hunger = max(0, self.hunger - hr*dt)
        if self.hunger <= 0: self.health = max(0, self.health - dt)
        elif self.hunger > 18 and self.health < self.max_health:
            self.health = min(self.max_health, self.health + .5*dt)
        self.health = max(0, min(self.max_health, self.health))

        self._raycast()

    def _collides(self, x, y, z):
        hw = PLAYER_WIDTH / 2
        for cy in range(int(y), int(y+PLAYER_HEIGHT)+1):
            for cx in (int(x-hw), int(x+hw)):
                for cz in (int(z-hw), int(z+hw)):
                    b = self.world.get_block(cx, cy, cz)
                    if b != B.AIR and b != B.WATER: return True
        return False

    def _raycast(self):
        dx = -math.sin(self.yaw)*math.cos(self.pitch)
        dy = math.sin(self.pitch)
        dz = -math.cos(self.yaw)*math.cos(self.pitch)
        ex, ey, ez = self.x, self.y+PLAYER_HEIGHT-.2, self.z
        step = .05; prev = None
        for i in range(int(self.reach/step)):
            d = i*step
            rx, ry, rz = ex+dx*d, ey+dy*d, ez+dz*d
            bx, by, bz = int(math.floor(rx)), int(math.floor(ry)), int(math.floor(rz))
            b = self.world.get_block(bx, by, bz)
            if b != B.AIR and not TRANSPARENT.get(b, False):
                self.target = (bx, by, bz)
                self.target_face = (bx-prev[0], by-prev[1], bz-prev[2]) if prev else (0,1,0)
                return
            prev = (bx, by, bz)
        self.target = self.target_face = None

    def break_block(self):
        if self.target:
            bt = self.world.get_block(*self.target)
            if bt not in (B.AIR, B.WATER):
                self.world.set_block(*self.target, B.AIR)
                self.add_item(bt)
                return True
        return False

    def place_block(self):
        sb = self.sel_block()
        if not sb or not self.target or not self.target_face: return False
        px = self.target[0]+self.target_face[0]
        py = self.target[1]+self.target_face[1]
        pz = self.target[2]+self.target_face[2]
        hw = PLAYER_WIDTH/2
        if int(self.x-hw)<=px<=int(self.x+hw) and int(self.z-hw)<=pz<=int(self.z+hw) \
           and int(self.y)<=py<int(self.y+PLAYER_HEIGHT): return False
        if self.world.get_block(px,py,pz) in (B.AIR, B.WATER):
            self.world.set_block(px,py,pz, sb)
            self.rem_item(sb)
            return True
        return False

# ═══════════════════════════ CRAFTING ═════════════════════════════
class CraftingSystem:
    """Recipe registry & crafting logic."""
    def __init__(self):
        self.recipes = [
            {'name':'Planks x4',       'result':B.PLANKS,         'count':4,  'ing':[(B.WOOD,1)]},
            {'name':'Crafting Table',   'result':B.CRAFTING_TABLE, 'count':1,  'ing':[(B.PLANKS,4)]},
            {'name':'Furnace',          'result':B.FURNACE,        'count':1,  'ing':[(B.COBBLESTONE,8)]},
            {'name':'Cobblestone x4',   'result':B.COBBLESTONE,    'count':4,  'ing':[(B.STONE,4)]},
            {'name':'Glass x4',         'result':B.GLASS,          'count':4,  'ing':[(B.SAND,4),(B.COAL_ORE,1)]},
            {'name':'Brick x4',         'result':B.BRICK,          'count':4,  'ing':[(B.COBBLESTONE,4)]},
            {'name':'Stick (Wood→Planks)', 'result':B.PLANKS,      'count':2,  'ing':[(B.WOOD,1)]},
        ]

    def can_craft(self, r, inv):
        return all(inv.get(bt,0)>=n for bt,n in r['ing'])

    def craft(self, r, inv):
        if not self.can_craft(r, inv): return None
        for bt,n in r['ing']:
            inv[bt] -= n
            if inv[bt] <= 0: del inv[bt]
        inv[r['result']] = inv.get(r['result'],0) + r['count']
        return r['result']

    def craftable(self, inv):
        return [r for r in self.recipes if self.can_craft(r, inv)]

# ═══════════════════════════ DAY/NIGHT ════════════════════════════
class DayNight:
    """Simple day/night cycle controller."""
    def __init__(self):
        self.t = .25  # 0=midnight, .25=sunrise, .5=noon, .75=sunset
        self.speed = 1/600.  # full cycle in 600s

    def update(self, dt):
        self.t = (self.t + dt*self.speed) % 1.0

    def sky(self):
        if .2<=self.t<=.8:
            a = math.sin((self.t-.2)/.6*math.pi)
            return (.1+.45*a, .15+.55*a, .25+.65*a)
        return (.02,.02,.06)

    def ambient(self):
        return .15 + .85*max(0, math.sin((self.t-.2)/.6*math.pi)) if .2<=self.t<=.8 else .15

    def time_str(self):
        h = int(self.t*24)%24; m = int(self.t*24*60)%60
        tag = "Day" if .25<=self.t<=.75 else "Night"
        return f"{h:02d}:{m:02d} ({tag})"

# ═══════════════════════════ UI ═══════════════════════════════════
class UI:
    """2D overlay rendering: HUD, menus, crosshair."""
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.debug = False
        self.craft_sel = 0
        self.font = self.font_lg = self.font_sm = None

    def init_fonts(self):
        self.font    = pygame.font.SysFont('consolas', 18)
        self.font_lg = pygame.font.SysFont('consolas', 24)
        self.font_sm = pygame.font.SysFont('consolas', 14)

    def _text(self, txt, x, y, font=None, color=(255,255,255)):
        f = font or self.font
        s = f.render(txt, True, color)
        d = pygame.image.tostring(s, "RGBA", True)
        sw, sh = s.get_size()
        try:
            glRasterPos2f(x, y+sh)
            glDrawPixels(sw, sh, GL_RGBA, GL_UNSIGNED_BYTE, d)
        except: pass

    def _bar(self, x, y, w, h, frac, col):
        frac = max(0, min(1, frac))
        glColor3f(.15,.15,.15)
        glBegin(GL_QUADS)
        glVertex2f(x,y); glVertex2f(x+w,y); glVertex2f(x+w,y+h); glVertex2f(x,y+h)
        glEnd()
        glColor3f(*col)
        glBegin(GL_QUADS)
        glVertex2f(x,y); glVertex2f(x+w*frac,y); glVertex2f(x+w*frac,y+h); glVertex2f(x,y+h)
        glEnd()
        glColor3f(.4,.4,.4)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x,y); glVertex2f(x+w,y); glVertex2f(x+w,y+h); glVertex2f(x,y+h)
        glEnd()

    def _rect(self, x, y, w, h, col):
        glColor4f(*col)
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBegin(GL_QUADS)
        glVertex2f(x,y); glVertex2f(x+w,y); glVertex2f(x+w,y+h); glVertex2f(x,y+h)
        glEnd()
        glDisable(GL_BLEND)

    def begin2d(self):
        glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
        glOrtho(0, self.w, self.h, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
        glDisable(GL_DEPTH_TEST); glDisable(GL_LIGHTING)

    def end2d(self):
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW); glPopMatrix()

    def draw_hud(self, player, day, fps, world):
        self.begin2d()

        # ── Crosshair ──
        cx, cy = self.w//2, self.h//2
        glColor3f(1,1,1); glLineWidth(2)
        glBegin(GL_LINES)
        glVertex2f(cx-12,cy); glVertex2f(cx+12,cy)
        glVertex2f(cx,cy-12); glVertex2f(cx,cy+12)
        glEnd()

        # ── Hotbar ──
        hby = self.h - 56
        hbx0 = self.w//2 - 9*25
        for i in range(9):
            bx = hbx0 + i*50
            sel = (i==player.sel)
            self._rect(bx, hby, 46, 46, (.85,.85,.25,.9) if sel else (.25,.25,.25,.8))
            bt = player.hotbar[i]
            if bt is not None and bt in BLOCK_COLOR:
                c = BLOCK_COLOR[bt]
                self._rect(bx+6, hby+6, 34, 34, (*c, 1.))
                cnt = player.inv.get(bt, 0)
                if cnt > 0:
                    self._text(str(cnt), bx+8, hby+28, self.font_sm)
            # Slot number
            self._text(str(i+1), bx+2, hby+1, self.font_sm, (180,180,180))

        # ── Health & Hunger ──
        self._bar(10, 10, 200, 20, player.health/player.max_health, (.8,.1,.1))
        self._text(f"HP {player.health:.0f}/{player.max_health:.0f}", 12, 12, self.font_sm)
        self._bar(10, 36, 200, 20, player.hunger/player.max_hunger, (.8,.6,.1))
        self._text(f"Hunger {player.hunger:.0f}/{player.max_hunger:.0f}", 12, 38, self.font_sm)

        # ── Target block ──
        if player.target:
            bt = world.get_block(*player.target)
            nm = BLOCK_NAME.get(bt, "?")
            self._text(f"Looking at: {nm}", 10, 62)
        sb = player.sel_block()
        if sb:
            nm = BLOCK_NAME.get(sb,"?")
            self._text(f"Selected: {nm} x{player.inv.get(sb,0)}", 10, 80)

        # ── Time ──
        self._text(day.time_str(), self.w-160, 10)
        self._text(f"FPS: {fps:.0f}", self.w-100, 30)

        # ── Debug ──
        if self.debug:
            self._text(f"Pos: ({player.x:.1f}, {player.y:.1f}, {player.z:.1f})", 10, 110)
            self._text(f"Yaw: {math.degrees(player.yaw):.1f}  Pitch: {math.degrees(player.pitch):.1f}", 10, 128)
            self._text(f"Chunks: {len(world.chunks)}  Grounded: {player.on_ground}", 10, 146)

        # ── Help text ──
        self._text("[E] Inventory  [C] Craft  [F3] Debug  [R] Respawn", self.w//2-200, self.h-75, self.font_sm, (160,160,160))

        self.end2d()

    def draw_inventory(self, player):
        self.begin2d()
        self._rect(self.w*.2, self.h*.15, self.w*.6, self.h*.7, (0,0,0,.82))
        self._text("INVENTORY  (E to close)", self.w*.35, self.h*.17, self.font_lg)
        y = self.h*.24
        for bt, cnt in player.inv.items():
            nm = BLOCK_NAME.get(bt, f"Block#{bt}")
            self._text(f"  {nm}  x{cnt}", self.w*.25, y)
            y += 24
            if y > self.h*.8: break
        self.end2d()

    def draw_crafting(self, crafting, player):
        self.begin2d()
        self._rect(self.w*.12, self.h*.08, self.w*.76, self.h*.84, (0,0,0,.85))
        self._text("CRAFTING  (C to close, ↑↓ select, Enter craft)",
                   self.w*.15, self.h*.1, self.font_lg)
        y = self.h*.18
        craftable = crafting.craftable(player.inv)
        for i, r in enumerate(crafting.recipes):
            can = r in craftable
            if i == self.craft_sel:
                self._rect(self.w*.14, y-4, self.w*.72, 28, (.2,.2,.4,.7))
            marker = "[CRAFT]" if can else "       "
            ing = ", ".join(f"{BLOCK_NAME.get(b,'?')}x{n}" for b,n in r['ing'])
            col = (255,255,255) if can else (110,110,110)
            self._text(f"{marker} {r['name']}  ←  {ing}", self.w*.16, y, color=col)
            y += 32
        self.end2d()

# ═══════════════════════════ RENDERER ═════════════════════════════
class Renderer:
    def __init__(self, w, h):
        self.w, self.h = w, h

    def init_gl(self):
        glEnable(GL_DEPTH_TEST); glEnable(GL_CULL_FACE); glCullFace(GL_BACK)
        glEnable(GL_LIGHTING); glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL); glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glShadeModel(GL_SMOOTH)
        glLightfv(GL_LIGHT0, GL_SPECULAR, (.1,.1,.1,1))
        glClearColor(.5,.7,1,1)

    def set_projection(self):
        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluPerspective(70, self.w/self.h, .1, 400)
        glMatrixMode(GL_MODELVIEW)

    def render(self, world, player, day):
        sky = day.sky(); glClearColor(*sky,1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        amb = day.ambient()
        glLightfv(GL_LIGHT0, GL_AMBIENT, (amb*.5,amb*.5,amb*.5,1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (amb,amb,amb*.95,1))
        sa = day.t * 2 * math.pi
        glLightfv(GL_LIGHT0, GL_POSITION, (math.cos(sa)*100, math.sin(sa)*100, 50, 0))

        glLoadIdentity()
        glRotatef(math.degrees(player.pitch), 1,0,0)
        glRotatef(math.degrees(player.yaw), 0,1,0)
        ey = player.y + PLAYER_HEIGHT - .2
        glTranslatef(-player.x, -ey, -player.z)

        # Target highlight
        if player.target:
            self._highlight(player.target)

        # Chunks
        for key, ch in world.chunks.items():
            cx2, cz2 = key[0]*CHUNK_SIZE+8, key[1]*CHUNK_SIZE+8
            d = math.hypot(cx2-player.x, cz2-player.z)
            if d > (RENDER_DISTANCE+1.5)*CHUNK_SIZE: continue
            if ch.dirty or ch.dl is None:
                ch.build_dl(world)
            if ch.dl: glCallList(ch.dl)

    def _highlight(self, pos):
        x,y,z = pos
        glDisable(GL_LIGHTING); glColor3f(0,0,0); glLineWidth(2.5)
        for dy in (0,1):
            glBegin(GL_LINE_LOOP)
            for dx,dz in ((0,0),(1,0),(1,1),(0,1)):
                glVertex3f(x+dx,y+dy,z+dz)
            glEnd()
        glBegin(GL_LINES)
        for dx,dz in ((0,0),(1,0),(1,1),(0,1)):
            glVertex3f(x+dx,y,z+dz); glVertex3f(x+dx,y+1,z+dz)
        glEnd()
        glEnable(GL_LIGHTING)

# ═══════════════════════════ GAME ENGINE ══════════════════════════
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("3D Sandbox Survival Crafting Game")
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), DOUBLEBUF|OPENGL)
        self.clock = pygame.time.Clock()
        self.fps = 60.; self.running = True
        self.grabbed = True

        self.world    = World(42)
        self.player   = Player(self.world)
        self.renderer = Renderer(WINDOW_W, WINDOW_H)
        self.ui       = UI(WINDOW_W, WINDOW_H)
        self.crafting = CraftingSystem()
        self.day      = DayNight()

        self.renderer.init_gl(); self.renderer.set_projection()
        self.ui.init_fonts()
        pygame.event.set_grab(True); pygame.mouse.set_visible(False)

        # Generate spawn area & find ground
        self.world.ensure_chunks(self.player.x, self.player.z)
        self._find_spawn()
        self.keys = {}

    def _find_spawn(self):
        for y in range(WORLD_HEIGHT-1, -1, -1):
            if self.world.get_block(8,y,8) not in (B.AIR, B.WATER):
                self.player.x, self.player.y, self.player.z = 8.5, y+1.5, 8.5
                break

    def run(self):
        while self.running:
            dt = min(self.clock.tick(60)/1000., .05)
            self.fps = self.clock.get_fps()
            self._events()
            self._update(dt)
            self._draw()
            pygame.display.flip()
        self._quit()

    def _events(self):
        for e in pygame.event.get():
            if e.type == QUIT: self.running = False
            elif e.type == KEYDOWN:
                self.keys[e.key] = True; self._keydn(e.key)
            elif e.type == KEYUP:
                self.keys[e.key] = False
            elif e.type == MOUSEMOTION and self.grabbed \
                    and not self.player.inv_open and not self.player.craft_open:
                self.player.yaw   += e.rel[0]*MOUSE_SENS
                self.player.pitch  = max(-1.5, min(1.5, self.player.pitch - e.rel[1]*MOUSE_SENS))
            elif e.type == MOUSEBUTTONDOWN and self.grabbed \
                    and not self.player.inv_open and not self.player.craft_open:
                if e.button == 1: self.player.break_block()
                elif e.button == 3: self.player.place_block()
                elif e.button == 4: self.player.sel = (self.player.sel-1) % 9
                elif e.button == 5: self.player.sel = (self.player.sel+1) % 9

    def _toggle_grab(self, on):
        self.grabbed = on
        pygame.event.set_grab(on); pygame.mouse.set_visible(not on)

    def _keydn(self, k):
        p = self.player
        if k == K_ESCAPE:
            if p.inv_open: p.inv_open = False; self._toggle_grab(True)
            elif p.craft_open: p.craft_open = False; self._toggle_grab(True)
            else: self._toggle_grab(not self.grabbed)
        elif k == K_e:
            p.craft_open = False
            p.inv_open = not p.inv_open
            self._toggle_grab(not p.inv_open)
        elif k == K_c:
            p.inv_open = False
            p.craft_open = not p.craft_open
            self.ui.craft_sel = 0
            self._toggle_grab(not p.craft_open)
        elif k == K_F3: self.ui.debug = not self.ui.debug
        elif k == K_r: self._find_spawn(); p.health=p.max_health; p.hunger=p.max_hunger; p.vy=0
        elif K_1<=k<=K_9: p.sel = k-K_1
        elif p.craft_open:
            if k == K_UP:   self.ui.craft_sel = max(0, self.ui.craft_sel-1)
            if k == K_DOWN: self.ui.craft_sel = min(len(self.crafting.recipes)-1, self.ui.craft_sel+1)
            if k == K_RETURN:
                if 0 <= self.ui.craft_sel < len(self.crafting.recipes):
                    self.crafting.craft(self.crafting.recipes[self.ui.craft_sel], p.inv)

    def _update(self, dt):
        if not self.player.inv_open and not self.player.craft_open:
            self.player.update(dt, self.keys)
        self.day.update(dt)
        self.world.ensure_chunks(self.player.x, self.player.z)
        if self.player.health <= 0:
            self._find_spawn()
            self.player.health = self.player.max_health
            self.player.hunger = self.player.max_hunger/2

    def _draw(self):
        self.renderer.render(self.world, self.player, self.day)
        self.ui.draw_hud(self.player, self.day, self.fps, self.world)
        if self.player.inv_open:   self.ui.draw_inventory(self.player)
        if self.player.craft_open: self.ui.draw_crafting(self.crafting, self.player)

    def _quit(self):
        for ch in self.world.chunks.values(): ch.cleanup()
        pygame.quit(); sys.exit()

# ═══════════════════════════ ENTRY POINT ══════════════════════════
if __name__ == "__main__":
    print("╔═══════════════════════════════════════════════════╗")
    print("║  3D Sandbox Survival Crafting Game Framework     ║")
    print("╠═══════════════════════════════════════════════════╣")
    print("║  WASD = Move    Space = Jump    Mouse = Look     ║")
    print("║  LClick = Break  RClick = Place  Scroll = Slot   ║")
    print("║  E = Inventory   C = Crafting   F3 = Debug       ║")
    print("║  R = Respawn     ESC = Release mouse              ║")
    print("╚═══════════════════════════════════════════════════╝")
    print()
    Game().run()