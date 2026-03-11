import math, random

# --- 설정 및 상수 (최적화) ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FOV = math.pi / 3  
HALF_FOV = FOV / 2
CASTED_RAYS = 256  # 해상도 대비 성능 균형점 권장 : 256
STEP_ANGLE = FOV / CASTED_RAYS
WALL_HEIGHT_FACTOR = 600 # 600 해상도에 맞춰 높이 상향
MAX_DEPTH = 1600    # 맵 크기에 따라 수치 상향. 시야로 바라보는 레이저가 진행하는 경로의 길이
TILE_SIZE = 50
ACTIVE_DISTANCE = 500 # Chunk 적용 상수. 약 10타일 거리 이내의 몬스터만 AI 작동

# 1은 벽, 0은 통로
MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,0,1,0,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1],
    [1,0,1,0,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,1,0,1,1,1,0,1,0,1,1,1,0,1,0,1,1,1,1,1,1,0,1,1,0,1,0,1,1,0,1],
    [1,0,1,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,1,0,1,0,0,1,0,0,1,0,1],
    [1,0,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1,0,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,1,0,1],
    [1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1,0,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,0,1],
    [1,0,1,1,1,0,1,1,1,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1],
    [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,1],
    [1,0,1,0,1,1,1,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1],
    [1,0,1,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,1],
    [1,0,1,0,1,0,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1],
    [1,0,0,0,1,0,1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,1,0,1],
    [1,1,1,0,1,0,1,0,1,1,0,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1,0,1],
    [1,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1,0,1],
    [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1],
    [1,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1],
    [1,0,1,0,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1,0,1],
    [1,0,1,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1],
    [1,0,1,0,1,0,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1],
    [1,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
    [1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
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

    def spawn_monsters_randomly(self, count):
        """맵의 빈 공간을 찾아 지정된 수만큼 몬스터를 랜덤하게 배치"""
        self.monsters = []
        empty_tiles = []

        # 1. 맵 전체를 순회하며 빈 공간(0)인 타일의 인덱스를 수집
        for row_idx, row in enumerate(MAP):
            for col_idx, tile in enumerate(row):
                if tile == 0:
                    # 플레이어 시작 지점(1,1) 근처에는 생성되지 않도록 예외 처리 가능
                    if not (row_idx == 1 and col_idx == 1):
                        empty_tiles.append((col_idx, row_idx))

        # 2. 빈 타일 중 'count' 개수만큼 랜덤하게 선택
        if len(empty_tiles) < count:
            count = len(empty_tiles) # 빈 공간이 부족하면 최대치로 설정

        selected_tiles = random.sample(empty_tiles, count)

        # 3. 선택된 타일의 중앙 좌표로 몬스터 생성
        for col, row in selected_tiles:
            # 타일 좌표를 월드 좌표로 변환 (중앙 배치를 위해 + TILE_SIZE/2)
            world_x = (col * TILE_SIZE) + (TILE_SIZE / 2)
            world_y = (row * TILE_SIZE) + (TILE_SIZE / 2)
            self.monsters.append(Monster(world_x, world_y))

    def init_game(self):
        # 시작지점 벽 생성 지점과 겹치지 않게 주의
        self.player_x = 75.0
        self.player_y = 75.0
        self.player_angle = 0
        self.player_health = 3
        self.ammo = 20  # 총알 개수 초기 설정 (예: 20발)
        # self.monsters = [
        #     Monster(175, 170), Monster(320, 80),
        #     Monster(310, 280), Monster(75, 250) 
        # ]

        # 직접 좌표를 입력하는 대신 랜덤 함수 호출(n = 생성 몬스터 수)
        self.spawn_monsters_randomly(8)

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
        
        move_speed = 1.5 # 해상도가 크다면 속도 높일것.
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
            dist = dx**2 + dy**2 # 무거운 루트 연산 대신 제곱 연산 사용

            # 1. 플레이어 피격 판정 (매우 가까울 때만)
            if dist < 900: # 30의 제곱
                if self.damage_cooldown == 0:
                    self.player_health -= 1
                    self.damage_frames = 10
                    self.damage_cooldown = 40
                    if self.player_health <= 0: self.game_state = "GAMEOVER"

            # 2. 청크 로직: 일정 거리 안에 있을 때만 추격 AI 실행
            if dist < ACTIVE_DISTANCE**2:
                dist = math.sqrt(dist) # 여기서만 실제 거리 계산
                # 몬스터 추격 AI
                if dist > 35:
                    mx, my = (dx/dist) * 0.8, (dy/dist) * 0.8
                    if self.get_map_at(m.x + mx, m.y) == 0: m.x += mx
                    if self.get_map_at(m.x, m.y + my) == 0: m.y += my
            else:
                # 활성 거리 밖에 있는 몬스터는 '대기 상태'
                # 필요하다면 여기서 아주 가끔씩만 위치를 업데이트하는 '저사양 로직'을 넣을 수 있습니다.
                pass

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
        # 렌더링 컷오프 거리 (MAX_DEPTH보다 조금 짧게 설정하여 자연스럽게 사라지게 함)
        RENDER_DISTANCE = 1200

        for m in self.monsters:
            if not m.is_alive: continue
            dx, dy = m.x - self.player_x, m.y - self.player_y
            dist = dx**2 + dy**2

            # 너무 먼 몬스터는 계산 생략
            if dist > RENDER_DISTANCE**2: continue
            
            dist = math.sqrt(dist)
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