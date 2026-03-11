import math

# --- 설정 및 상수 (최적화) ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FOV = math.pi / 3  
HALF_FOV = FOV / 2
CASTED_RAYS = 256  # 해상도 대비 성능 균형점 권장 : 256
STEP_ANGLE = FOV / CASTED_RAYS
WALL_HEIGHT_FACTOR = 600 # 600 해상도에 맞춰 높이 상향
MAX_DEPTH = 800    
TILE_SIZE = 50

MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
]

class Monster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_alive = True
        self.health = 2
        self.radius = 15

class DoomGame:
    def __init__(self):
        self.init_game()

    def init_game(self):
        # 시작지점 벽 생성 지점과 겹치지 않게 주의
        self.player_x = 75.0
        self.player_y = 75.0
        self.player_angle = 0
        self.player_health = 3
        self.ammo = 10  # 총알 개수 초기 설정 (예: 20발)
        self.monsters = [
            Monster(175, 170), Monster(320, 80),
            Monster(310, 280), Monster(75, 250) 
        ]
        self.damage_frames = 0
        self.damage_cooldown = 0
        self.flash_frames = 0
        self.walk_timer = 0
        self.game_state = "PLAYING"

    def get_map_at(self, x, y):
        col, row = int(x / TILE_SIZE), int(y / TILE_SIZE)
        if 0 <= row < len(MAP) and 0 <= col < len(MAP[0]):
            return MAP[row][col]
        return 1

    def update_player(self, keys):
        if self.game_state != "PLAYING": return
        
        move_speed = 2.0 # 해상도가 크다면 속도 높일것.
        rot_speed = 0.06
        
        #회전 동작
        if 'a' in keys: self.player_angle -= rot_speed
        if 'd' in keys: self.player_angle += rot_speed

        if 'w' in keys or 's' in keys:
            direction = 1 if 'w' in keys else -1
            dx = math.cos(self.player_angle) * move_speed * direction
            dy = math.sin(self.player_angle) * move_speed * direction

            # --- 개선된 충돌 판정 (Sliding Collision) ---
            # 플레이어의 몸집(반지름)을 고려한 마진 설정 -> 플레이어를 약간의 반지름을 가진 원으로 설정
            player_radius = 5.0
            
            # X축 이동 검사: 이동할 방향에 반지름만큼 여유를 두고 벽이 있는지 확인
            margin_x = player_radius if dx > 0 else -player_radius
            if self.get_map_at(self.player_x + dx + margin_x, self.player_y) == 0:
                    self.player_x += dx

            # Y축 이동 검사: X축과 별개로 검사하여 벽을 타고 미끄러지듯 이동 가능하게 함
            margin_y = player_radius if dy > 0 else -player_radius
            if self.get_map_at(self.player_x, self.player_y + dy + margin_y) == 0:
                self.player_y += dy
            self.walk_timer += 0.2
        else:
            self.walk_timer = 0

        # 몬스터 로직 통합 업데이트
        self.update_monsters()

    def update_monsters(self):
        for m in self.monsters:
            if not m.is_alive: continue
            dx, dy = self.player_x - m.x, self.player_y - m.y
            dist = math.sqrt(dx**2 + dy**2)

            # 플레이어 피격 판정
            if dist < 30 and self.damage_cooldown == 0:
                self.player_health -= 1
                self.damage_frames = 10
                self.damage_cooldown = 40
                if self.player_health <= 0: self.game_state = "GAMEOVER"

            # 몬스터 추격 AI
            if dist > 35:
                mx, my = (dx/dist) * 0.8, (dy/dist) * 0.8
                if self.get_map_at(m.x + mx, m.y) == 0: m.x += mx
                if self.get_map_at(m.x, m.y + my) == 0: m.y += my

        if self.damage_cooldown > 0: self.damage_cooldown -= 1
        if all(not m.is_alive for m in self.monsters): self.game_state = "CLEAR"

    def cast_rays(self):
        """DDA 알고리즘을 적용한 고성능 레이캐스팅 -> DDA 생략하고 정밀도를 더 높인 레이캐스팅"""
        ray_angle = self.player_angle - HALF_FOV
        wall_data = []

        for i in range(CASTED_RAYS):
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)
            
            dist = MAX_DEPTH
            # 스텝을 1로 복구하여 계단 현상 제거 (정밀도 향상)
            # 대신 range 범위를 최적화하여 연산량을 조절합니다.
            for depth in range(1, MAX_DEPTH, 1): 
                target_x = self.player_x + cos_a * depth
                target_y = self.player_y + sin_a * depth
                
                # 맵 경계 안쪽인지 먼저 확인 (성능 최적화)
                col, row = int(target_x / TILE_SIZE), int(target_y / TILE_SIZE)
                if 0 <= row < len(MAP) and 0 <= col < len(MAP[0]):
                    if MAP[row][col] == 1:
                        # 어안렌즈 왜곡 보정
                        dist = depth * math.cos(self.player_angle - ray_angle)
                        break
                else:
                    break # 맵 밖으로 나가면 중단
            
            h = (TILE_SIZE * WALL_HEIGHT_FACTOR) / (dist + 0.1)
            wall_data.append({'height': h, 'dist': dist})
            ray_angle += STEP_ANGLE
            
        return wall_data

    def get_sprites_data(self):
        sprite_results = []
        for m in self.monsters:
            if not m.is_alive: continue
            dx, dy = m.x - self.player_x, m.y - self.player_y
            dist = math.sqrt(dx**2 + dy**2)
            theta = math.atan2(dy, dx)
            gamma = theta - self.player_angle
            
            while gamma < -math.pi: gamma += 2 * math.pi
            while gamma > math.pi: gamma -= 2 * math.pi

            if abs(gamma) < HALF_FOV + 0.2: # 가장자리 잘림 방지 마진
                sprite_x = (0.5 * (gamma / HALF_FOV) + 0.5) * SCREEN_WIDTH
                sprite_height = (TILE_SIZE * WALL_HEIGHT_FACTOR) / (dist + 0.1)
                sprite_results.append({'x': sprite_x, 'h': sprite_height, 'd': dist, 'health': m.health})
        
        return sorted(sprite_results, key=lambda x: x['d'], reverse=True)

    def attack_monster(self):
        """총알이 있을 때만 사격 가능하고 총알 소모"""
        if self.ammo <= 0:
            return False # 총알이 없으면 사격 실패

        self.ammo -= 1 # 사격 시 총알 1발 소모

        aim_tolerance = 0.2
        target, min_dist = None, float('inf')

        for m in self.monsters:
            if not m.is_alive: continue
            dx, dy = m.x - self.player_x, m.y - self.player_y
            gamma = math.atan2(dy, dx) - self.player_angle
            while gamma < -math.pi: gamma += 2 * math.pi
            while gamma > math.pi: gamma -= 2 * math.pi

            if abs(gamma) < aim_tolerance:
                dist = math.sqrt(dx**2 + dy**2)
                if dist < min_dist: min_dist, target = dist, m

        if target:
            target.health -= 1
            if target.health <= 0: target.is_alive = False
            return True
        return False