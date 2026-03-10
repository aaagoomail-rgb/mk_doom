import math

# --- 설정 및 상수 ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
# 권장 사양 : width=640 , height=480

FOV = math.pi / 3  # 시야각 (60도)
HALF_FOV = FOV / 2

CASTED_RAYS = 256  # 광선 개수 (성능에 따라 조절)
# 권장 사양 : 180

WALL_HEIGHT_FACTOR = 400
# 해상도의 따라 벽의 높이 보정(초기값 400 -> 600).

STEP_ANGLE = FOV / CASTED_RAYS
MAX_DEPTH = 800    # 최대 가시 거리

# 맵 데이터 (1은 벽, 0은 빈 공간)
MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
]
TILE_SIZE = 50

class Monster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_alive = True
        self.health = 2  # 몬스터 체력 2
        self.radius = 15  # 몬스터의 물리적 반지름 추가

class DoomGame:
    def __init__(self):
        self.init_game()

    def init_game(self):
        self.player_x = 100
        self.player_y = 100
        self.player_angle = 0
        self.player_health = 3  # 플레이어 체력 3
        # 몬스터 목록 추가
        # 몬스터 좌표를 타일 중앙(TILE_SIZE // 2)으로 보정하여 배치
        self.monsters = [
            Monster(175, 170), # 중앙 부근
            Monster(320, 80),
            Monster(310, 280),
            Monster(75, 250) 
        ]
        self.damage_frames = 0 # 데미지 입었을 때 붉은 효과용
        self.damage_cooldown = 0 # 연속 데미지 방지 쿨타임
        self.flash_frames = 0  # 여기에 추가
        self.walk_timer = 0  # 걷는 시간을 기록할 타이머 추가
        self.game_state = "PLAYING" # PLAYING, GAMEOVER, CLEAR
        
    def update_player(self, keys):
        if self.game_state != "PLAYING":
            return
        # 이동 속도와 회전 속도 설정
        move_speed = 1.12
        rot_speed = 0.08
        
        # 회전 처리 (A, D)
        if 'a' in keys:
            self.player_angle -= rot_speed
        if 'd' in keys:
            self.player_angle += rot_speed

        # 이동 처리 (W, S)
        if 'w' in keys or 's' in keys:
            direction = 1 if 'w' in keys else -1
            
            # 이동할 예상 좌표 계산
            new_x = self.player_x + math.cos(self.player_angle) * move_speed * direction
            new_y = self.player_y + math.sin(self.player_angle) * move_speed * direction
            
            # --- 충돌 검사 로직 ---
            # X축 이동 검사
            if self.get_map_at(new_x, self.player_y) == 0:
                self.player_x = new_x
            
            # Y축 이동 검사
            if self.get_map_at(self.player_x, new_y) == 0:
                self.player_y = new_y

        # W나 S키를 눌러 이동 중일 때 타이머 증가
        if 'w' in keys or 's' in keys:
            self.walk_timer += 0.15  # 흔들림 속도 조절
        else:
            # 멈춰 있을 때는 부드럽게 0으로 수렴 (또는 바로 0)
            self.walk_timer = 0


        # 몬스터와의 거리 체크 (근접 데미지)
        for m in self.monsters:
            if not m.is_alive: continue
            dx = m.x - self.player_x
            dy = m.y - self.player_y
            dist = math.sqrt(dx**2 + dy**2)
            
            # 몬스터와 너무 가까우면 (거리 30 미만)
            if dist < 30 and self.damage_cooldown == 0:
                self.player_health -= 1
                self.damage_frames = 10 # 붉은색 번쩍임
                self.damage_cooldown = 60 # 약 1초간 무적 (60프레임)
                if self.player_health <= 0:
                    print("Game Over") # 콘솔 출력용

        # 데미지 쿨타임 감소
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
            
        if self.player_health <= 0:
            self.game_state = "GAMEOVER"
            
        # 모든 몬스터 처치 시 클리어 상태 전환
        if all(not m.is_alive for m in self.monsters):
            self.game_state = "CLEAR"

    def get_sprites_data(self):
        """몬스터의 상대적 위치와 거리를 계산하여 HTML로 전달"""
        sprite_results = []
        for m in self.monsters:
            if not m.is_alive: continue

            # 플레이어와 몬스터 사이의 거리 및 각도 계산
            dx = m.x - self.player_x
            dy = m.y - self.player_y
            dist = math.sqrt(dx**2 + dy**2)

            # 플레이어가 바라보는 방향과 몬스터 사이의 상대 각도
            theta = math.atan2(dy, dx)
            gamma = theta - self.player_angle
            
            # 각도 보정 (-pi ~ pi 사이로)
            while gamma < -math.pi: gamma += 2 * math.pi
            while gamma > math.pi: gamma -= 2 * math.pi

            # 시야각(FOV) 안에 있는지 확인
            if abs(gamma) < HALF_FOV:
                # 화면상 X 좌표 및 높이 계산
                sprite_x = (0.5 * (gamma / HALF_FOV) + 0.5) * SCREEN_WIDTH
                sprite_height = (TILE_SIZE * 400) / (dist + 0.1)
                sprite_results.append({
                    'x': sprite_x,
                    'h': sprite_height,
                    'd': dist
                })
        
        # 거리에 따라 정렬 (멀리 있는 것부터 그려야 겹침이 자연스러움)
        return sorted(sprite_results, key=lambda x: x['d'], reverse=True)
    
    def spawn_monster_safely(self, grid_x, grid_y):
        """벽에서 떨어진 안전한 중앙 좌표에 몬스터 생성"""
        # 타일의 정중앙 좌표로 계산
        safe_x = (grid_x * TILE_SIZE) + (TILE_SIZE / 2)
        safe_y = (grid_y * TILE_SIZE) + (TILE_SIZE / 2)
        return Monster(safe_x, safe_y)
    
    def update_monsters(self):
        for m in self.monsters:
            if not m.is_alive: continue
            
            # 플레이어 방향으로 아주 조금씩 이동 (사운드가 없으니 움직임이 중요!)
            dx = self.player_x - m.x
            dy = self.player_y - m.y
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist > 40: # 플레이어와 너무 가깝지 않을 때만 이동
                move_x = (dx / dist) * 0.5
                move_y = (dy / dist) * 0.5
                
                # 벽 충돌 검사 후 이동
                if self.get_map_at(m.x + move_x, m.y) == 0:
                    m.x += move_x
                if self.get_map_at(m.x, m.y + move_y) == 0:
                    m.y += move_y

    def get_map_at(self, x, y):
        """특정 좌표의 맵 데이터를 반환하는 헬퍼 함수"""
        col = int(x / TILE_SIZE)
        row = int(y / TILE_SIZE)
        
        # 맵 범위 밖으로 나가는 경우 벽으로 간주하여 방지
        if 0 <= row < len(MAP) and 0 <= col < len(MAP[0]):
            return MAP[row][col]
        return 1

    def cast_rays(self):
        start_angle = self.player_angle - HALF_FOV
        wall_data = [] # 높이와 거리를 모두 담을 리스트
        
        for ray in range(CASTED_RAYS):
            found_wall = False
            for depth in range(1, MAX_DEPTH):
                target_x = self.player_x + math.cos(start_angle) * depth
                target_y = self.player_y + math.sin(start_angle) * depth
                
                col = int(target_x / TILE_SIZE)
                row = int(target_y / TILE_SIZE)
                
                if 0 <= row < len(MAP) and 0 <= col < len(MAP[0]):
                    if MAP[row][col] == 1:
                        # 어안렌즈 효과 보정된 거리
                        dist = depth * math.cos(self.player_angle - start_angle)
                        wall_height = (TILE_SIZE * WALL_HEIGHT_FACTOR) / (dist + 0.0001)
                        
                        # 중요: 거리(dist) 정보를 함께 저장합니다.
                        wall_data.append({'height': wall_height, 'dist': dist})
                        found_wall = True
                        break
            
            if not found_wall:
                wall_data.append({'height': 0, 'dist': MAX_DEPTH})
            
            start_angle += STEP_ANGLE
            
        return wall_data
    
    def attack_monster(self):
        """화면 중앙 조준점에 있는 몬스터를 찾아 제거"""
        # 플레이어 시야 정중앙의 각도는 0 (gamma = 0)
        # 조준점의 허용 오차 (각도 기준, 작을수록 정밀 조준 필요)
        aim_tolerance = 0.15 
        
        target_monster = None
        min_dist = float('inf')

        for m in self.monsters:
            if not m.is_alive: continue

            # 플레이어와 몬스터 사이의 각도 계산 (get_sprites_data 로직 활용)
            dx = m.x - self.player_x
            dy = m.y - self.player_y
            theta = math.atan2(dy, dx)
            gamma = theta - self.player_angle
            
            # 각도 보정
            while gamma < -math.pi: gamma += 2 * math.pi
            while gamma > math.pi: gamma -= 2 * math.pi

            # 조준점 범위(gamma가 0에 가까움) 안에 있고 가장 가까운 몬스터 선택
            if abs(gamma) < aim_tolerance:
                dist = math.sqrt(dx**2 + dy**2)
                if dist < min_dist:
                    min_dist = dist
                    target_monster = m

        if target_monster:
            target_monster.health -= 1 # 체력 감소
            if target_monster.health <= 0:
                target_monster.is_alive = False
            return True # 명중 시 True 반환
        return False

# 로직 실행 예시
game = DoomGame()
# 브라우저의 이벤트 루프에서 game.update_player()와 game.cast_rays()가 반복 호출됩니다.