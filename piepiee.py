import pygame
import random
import math

# Инициализация Pygame
pygame.init()

# Размеры для Trinket
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CARD_WIDTH = 120
CARD_HEIGHT = 160
PANEL_WIDTH = 180
FPS = 60

# Цвета
BLACK = (26, 26, 26)
GOLD = (212, 175, 55)
DARK_GRAY = (42, 42, 42)
LIGHT_GRAY = (58, 58, 58)
RED = (139, 0, 0)
GREEN = (0, 100, 0)
PURPLE = (75, 0, 130)
ORANGE = (255, 140, 0)
BLUE = (30, 144, 255)

class Card:
    def __init__(self, title, description, card_type, value=None, x=None, y=None):
        self.title = title
        self.description = description
        self.type = card_type
        self.value = value
        self.x = x if x is not None else random.randint(20, SCREEN_WIDTH - PANEL_WIDTH - CARD_WIDTH - 20)
        self.y = y if y is not None else random.randint(80, SCREEN_HEIGHT - CARD_HEIGHT - 120)
        self.dragging = False
        self.hovered = False
        self.z_index = 0
        
        # Цвета границ по типам (как в HTML)
        self.border_colors = {
            'aspect': RED,      # Красный для аспектов
            'follower': GREEN,  # Зеленый для последователей
            'location': PURPLE, # Фиолетовый для мест
            'lore': ORANGE,     # Оранжевый для знаний
            'resource': BLUE,   # Синий для ресурсов
            'cult': GOLD        # Золотой для культа
        }
        self.border_color = self.border_colors.get(card_type, GOLD)
        self.border_width = 3 if card_type == 'cult' else 2
        
        # Эмодзи
        self.emojis = {
            'aspect': '🔮',
            'follower': '👤',
            'location': '🏛️',
            'lore': '📖',
            'resource': '💰',
            'cult': '☪️'
        }
        self.emoji = self.emojis.get(card_type, '❓')
    
    def draw(self, screen, small_font):
        # Эффект при наведении
        if self.hovered:
            scale = 1.05
            width = int(CARD_WIDTH * scale)
            height = int(CARD_HEIGHT * scale)
            x = self.x - (width - CARD_WIDTH) // 2
            y = self.y - (height - CARD_HEIGHT) // 2
        else:
            width, height = CARD_WIDTH, CARD_HEIGHT
            x, y = self.x, self.y
        
        # Тень
        pygame.draw.rect(screen, (0, 0, 0, 100), (x+2, y+2, width, height), border_radius=3)
        
        # Карта
        pygame.draw.rect(screen, DARK_GRAY, (x, y, width, height), border_radius=3)
        pygame.draw.rect(screen, self.border_color, (x, y, width, height), self.border_width, border_radius=3)
        
        # Заголовок с эмодзи
        title_text = f"{self.emoji} {self.title}"
        title_lines = self.wrap_text(title_text, small_font, width - 20)
        for i, line in enumerate(title_lines[:2]):
            title_surf = small_font.render(line, True, GOLD)
            screen.blit(title_surf, (x + 5, y + 5 + i*15))
        
        # Разделитель под заголовком
        pygame.draw.line(screen, GOLD, (x+5, y+35), (x+width-5, y+35), 1)
        
        # Описание
        desc_lines = self.wrap_text(self.description, small_font, width - 10)
        for i, line in enumerate(desc_lines[:3]):
            desc_surf = small_font.render(line, True, GOLD)
            screen.blit(desc_surf, (x + 5, y + 40 + i*15))
        
        # Значение для ресурсов
        if self.value is not None:
            value_surf = small_font.render(str(self.value), True, GOLD)
            screen.blit(value_surf, (x + width - 25, y + height - 25))
    
    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def is_clicked(self, pos):
        return (self.x <= pos[0] <= self.x + CARD_WIDTH and 
                self.y <= pos[1] <= self.y + CARD_HEIGHT)
    
    def update_hover(self, pos):
        self.hovered = self.is_clicked(pos)
        return self.hovered

class Button:
    def __init__(self, x, y, w, h, text, visible=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.visible = visible
        self.hovered = False
        self.disabled = False
    
    def draw(self, screen, font):
        if not self.visible:
            return
        
        if self.disabled:
            color = (DARK_GRAY[0]//2, DARK_GRAY[1]//2, DARK_GRAY[2]//2)
            text_color = (GOLD[0]//2, GOLD[1]//2, GOLD[2]//2)
        elif self.hovered:
            color = LIGHT_GRAY
            text_color = GOLD
        else:
            color = DARK_GRAY
            text_color = GOLD
        
        pygame.draw.rect(screen, color, self.rect, border_radius=3)
        pygame.draw.rect(screen, text_color, self.rect, 2, border_radius=3)
        
        text_surf = font.render(self.text, True, text_color)
        text_x = self.rect.x + (self.rect.width - text_surf.get_width()) // 2
        text_y = self.rect.y + (self.rect.height - text_surf.get_height()) // 2
        screen.blit(text_surf, (text_x, text_y))
    
    def is_clicked(self, pos):
        return self.visible and not self.disabled and self.rect.collidepoint(pos)
    
    def update_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

class CultGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Тайный Культ")
        self.clock = pygame.time.Clock()
        
        # Шрифты
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Игровое состояние
        self.health = 10
        self.reason = 10
        self.funds = 5
        self.cards = []
        self.log_entries = ["Вы начинаете свой путь в тайных знаниях..."]
        self.cult_created = False
        self.has_ancient_knowledge = False
        self.has_first_follower = False
        
        # Концовки
        self.endings = {
            "ASCENSION": {
                "title": "ВОЗНЕСЕНИЕ",
                "description": "Вы собрали все компоненты и провели Великий Ритуал. Древние силы признали вас достойным и вознесли за пределы материального мира."
            },
            "MADNESS": {
                "title": "БЕЗУМИЕ",
                "description": "Вы заглянули слишком глубоко в бездну. Ваш разум не выдержал столкновения с невыразимыми истинами."
            },
            "CULT_LEADER": {
                "title": "ЛИДЕР КУЛЬТА",
                "description": "Вы основали процветающий культ. Члены поклоняются вам как пророку. Ваше влияние растет с каждым днем."
            },
            "FORGOTTEN": {
                "title": "ЗАБЫТЫЙ",
                "description": "Ваши поиски привели в забытые уголки мира, но вы так и не нашли того, что искали. Постепенно о вас забыли."
            }
        }
        
        # Создаем начальные карты
        self.create_card("Здоровье", "Ваша жизненная сила", 'resource', self.health, 20, 100)
        self.create_card("Рассудок", "Ваша ментальная стабильность", 'resource', self.reason, 160, 100)
        self.create_card("Деньги", "Средства к существованию", 'resource', self.funds, 300, 100)
        self.create_card("Старая книга", "Тайные знания ждут изучения", 'lore', None, 20, 280)
        self.create_card("Таинственный незнакомец", "Проявил интерес к оккультному", 'follower', None, 160, 280)
        
        # Кнопки действий
        self.buttons = [
            Button(SCREEN_WIDTH - PANEL_WIDTH + 10, 80, PANEL_WIDTH - 20, 30, "Работать"),
            Button(SCREEN_WIDTH - PANEL_WIDTH + 10, 120, PANEL_WIDTH - 20, 30, "Изучать"),
            Button(SCREEN_WIDTH - PANEL_WIDTH + 10, 160, PANEL_WIDTH - 20, 30, "Сны"),
            Button(SCREEN_WIDTH - PANEL_WIDTH + 10, 200, PANEL_WIDTH - 20, 30, "Беседовать"),
            Button(SCREEN_WIDTH - PANEL_WIDTH + 10, 240, PANEL_WIDTH - 20, 30, "Исследовать"),
            Button(SCREEN_WIDTH - PANEL_WIDTH + 10, 280, PANEL_WIDTH - 20, 30, "Отдых"),
            Button(SCREEN_WIDTH - PANEL_WIDTH + 10, 320, PANEL_WIDTH - 20, 30, "Ритуал", False),
            Button(SCREEN_WIDTH - PANEL_WIDTH + 10, 360, PANEL_WIDTH - 20, 30, "Создать культ", False)
        ]
        
        self.game_state = "menu"  # menu, game, ending
        self.current_ending = None
    
    def create_card(self, title, desc, card_type, value=None, x=None, y=None):
        card = Card(title, desc, card_type, value, x, y)
        self.cards.append(card)
        return card
    
    def update_resources(self):
        for card in self.cards:
            if card.title == "Здоровье":
                card.value = self.health
            elif card.title == "Рассудок":
                card.value = self.reason
            elif card.title == "Деньги":
                card.value = self.funds
    
    def add_log(self, text):
        self.log_entries.append(text)
        if len(self.log_entries) > 5:
            self.log_entries.pop(0)
    
    def check_cult_creation(self):
        has_knowledge = any(c.type == 'lore' and "Древнее знание" in c.title for c in self.cards)
        has_follower = any(c.type == 'follower' for c in self.cards)
        
        self.has_ancient_knowledge = has_knowledge
        self.has_first_follower = has_follower
        
        # Обновляем кнопки
        self.buttons[7].visible = has_knowledge and has_follower and not self.cult_created
        self.buttons[6].visible = self.cult_created
        
        return has_knowledge and has_follower and not self.cult_created
    
    def perform_ritual_check(self):
        """Проверяет условия для концовок через ритуалы"""
        lore_cards = [c for c in self.cards if c.type == 'lore']
        follower_cards = [c for c in self.cards if c.type == 'follower']
        aspect_cards = [c for c in self.cards if c.type == 'aspect']
        location_cards = [c for c in self.cards if c.type == 'location']
        has_cult = any(c.type == 'cult' for c in self.cards)
        
        if not has_cult:
            return None
        
        # Ритуал Вознесения
        if len(lore_cards) >= 3 and len(follower_cards) >= 2:
            return "ASCENSION"
        
        # Ритуал Безумия
        if len(aspect_cards) >= 5:
            return "MADNESS"
        
        # Ритуал Лидера Культа
        if len(follower_cards) >= 5:
            return "CULT_LEADER"
        
        # Ритуал Забвения
        if len(location_cards) >= 3:
            return "FORGOTTEN"
        
        return None
    
    def perform_action(self, action):
        msg = ""
        
        if action == "Работать":
            if self.health > 2:
                self.funds += 2
                self.health -= 1
                msg = "Вы работаете и зарабатываете деньги. Здоровье ухудшается."
                
                if random.random() > 0.8:
                    # Исправленная подпись: не "последователь", пока культ не создан
                    if self.cult_created:
                        self.create_card("Последователь", "Член вашего культа", 'follower')
                        msg += " Вы находите нового последователя."
                    else:
                        self.create_card("Заинтересованный", "Проявил интерес к вашим идеям", 'follower')
                        msg += " Кто-то проявил интерес."
            else:
                msg = "Вы слишком истощены для работы."
        
        elif action == "Изучать":
            if self.reason > 1:
                lore_cards = [c for c in self.cards if c.type == 'lore']
                if lore_cards:
                    self.reason -= 1
                    msg = "Вы изучаете древние тексты. Рассудок страдает."
                    
                    if random.random() > 0.7:
                        self.create_card("Древнее знание", "Запретные знания предков", 'lore')
                        self.has_ancient_knowledge = True
                        msg += " Вы находите древнее знание."
                else:
                    msg = "У вас нет материалов для изучения."
            else:
                msg = "Ваш рассудок слишком хрупок."
        
        elif action == "Сны":
            if self.reason > 0:
                self.reason -= 1
                msg = "Вы погружаетесь в странные сны. Рассудок страдает."
                
                if random.random() > 0.7:
                    self.create_card("Видение", "Образ из снов", 'aspect')
                    msg += " Вы получаете видение."
            else:
                msg = "Вы слишком близки к безумию, чтобы спать."
        
        elif action == "Беседовать":
            msg = "Вы ищете единомышленников."
            
            if random.random() > 0.5:
                # Исправленная подпись в зависимости от наличия культа
                if self.cult_created:
                    self.create_card("Новичок", "Новый член культа", 'follower')
                    msg += " Вы находите нового члена культа."
                else:
                    self.create_card("Сочувствующий", "Интересуется оккультизмом", 'follower')
                    self.has_first_follower = True
                    msg += " Вы находите сочувствующего."
            else:
                msg += " Никто не проявил интереса."
        
        elif action == "Исследовать":
            if self.funds > 0:
                self.funds -= 1
                msg = "Вы исследуете окрестности."
                
                if random.random() > 0.6:
                    self.create_card("Заброшенный храм", "Место, полное тайн", 'location')
                    msg += " Вы находите заброшенный храм."
            else:
                msg = "У вас недостаточно денег."
        
        elif action == "Отдых":
            if self.funds > 0:
                self.funds -= 1
                self.health = min(10, self.health + 2)
                self.reason = min(10, self.reason + 1)
                msg = "Вы отдыхаете и восстанавливаете силы."
            else:
                msg = "У вас недостаточно денег для отдыха."
        
        elif action == "Ритуал":
            if not self.cult_created:
                msg = "Сначала создайте культ!"
            else:
                ritual_result = self.perform_ritual_check()
                if ritual_result:
                    self.game_state = "ending"
                    self.current_ending = ritual_result
                    return
                else:
                    if self.health > 1 and self.reason > 1:
                        self.health -= 1
                        self.reason -= 1
                        msg = "Вы проводите таинственный ритуал."
                        
                        if random.random() > 0.8:
                            self.create_card("Древний артефакт", "Предмет невероятной силы", 'lore')
                            msg += " Ритуал увенчался успехом!"
                        else:
                            msg += " Ритуал не принес результатов."
                    else:
                        msg = "Недостаточно здоровья или рассудка."
        
        elif action == "Создать культ":
            if self.check_cult_creation():
                self.create_card("Тайный культ", "Ваша организация", 'cult')
                self.cult_created = True
                msg = "Вы создали Тайный культ! Теперь можете проводить ритуалы."
                
                # Переименовываем существующих "сочувствующих" в "последователей"
                for card in self.cards:
                    if card.type == 'follower':
                        if "Сочувствующий" in card.title:
                            card.title = "Последователь"
                            card.description = "Член вашего культа"
                        elif "Заинтересованный" in card.title:
                            card.title = "Последователь"
                            card.description = "Член вашего культа"
            else:
                msg = "Нужно Древнее знание и хотя бы один сочувствующий."
        
        self.add_log(msg)
        self.update_resources()
        self.check_cult_creation()
        
        # Автоматические концовки (без ритуала)
        if self.reason <= 0:
            self.game_state = "ending"
            self.current_ending = "MADNESS"
            return
        
        if self.health <= 0:
            self.game_state = "ending"
            self.current_ending = "FORGOTTEN"
            return
        
        # Много видений = безумие
        aspect_cards = [c for c in self.cards if c.type == 'aspect']
        if len(aspect_cards) >= 7:
            self.game_state = "ending"
            self.current_ending = "MADNESS"
            return
    
    def draw_menu(self):
        self.screen.fill(BLACK)
        
        title = self.title_font.render("ТАЙНЫЙ КУЛЬТ", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        subtitle = self.font.render("Нажмите SPACE чтобы начать", True, GOLD)
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 300))
        
        controls = self.small_font.render("Тащите карты. Используйте кнопки справа", True, GOLD)
        self.screen.blit(controls, (SCREEN_WIDTH//2 - controls.get_width()//2, 400))
        
        tip = self.small_font.render("Соберите Древнее знание и последователя для создания культа", True, GOLD)
        self.screen.blit(tip, (SCREEN_WIDTH//2 - tip.get_width()//2, 450))
    
    def draw_game(self):
        # Фон
        self.screen.fill(BLACK)
        
        # Заголовок
        title = self.title_font.render("ТАЙНЫЙ КУЛЬТ", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 10))
        
        # Разделительная линия
        pygame.draw.line(self.screen, GOLD, (20, 45), (SCREEN_WIDTH - PANEL_WIDTH - 20, 45), 2)
        
        # Ресурсы
        resources = self.font.render(f"Здоровье: {self.health} | Рассудок: {self.reason} | Деньги: {self.funds}", True, GOLD)
        self.screen.blit(resources, (20, 55))
        
        # Панель действий
        panel = pygame.Rect(SCREEN_WIDTH - PANEL_WIDTH, 0, PANEL_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, DARK_GRAY, panel)
        pygame.draw.rect(self.screen, GOLD, panel, 2)
        
        panel_title = self.font.render("Действия", True, GOLD)
        self.screen.blit(panel_title, (SCREEN_WIDTH - PANEL_WIDTH + 20, 40))
        
        # Кнопки
        for btn in self.buttons:
            btn.draw(self.screen, self.small_font)
        
        # Карты (сортировка по z_index)
        sorted_cards = sorted(self.cards, key=lambda c: c.z_index)
        mouse_pos = pygame.mouse.get_pos()
        for card in sorted_cards:
            card.update_hover(mouse_pos)
            card.draw(self.screen, self.small_font)
        
        # Журнал
        log_rect = pygame.Rect(10, SCREEN_HEIGHT - 100, SCREEN_WIDTH - PANEL_WIDTH - 20, 90)
        pygame.draw.rect(self.screen, DARK_GRAY, log_rect)
        pygame.draw.rect(self.screen, GOLD, log_rect, 2)
        
        log_title = self.font.render("Журнал событий:", True, GOLD)
        self.screen.blit(log_title, (20, SCREEN_HEIGHT - 90))
        
        for i, entry in enumerate(self.log_entries[-4:]):
            entry_surf = self.small_font.render(entry, True, GOLD)
            self.screen.blit(entry_surf, (20, SCREEN_HEIGHT - 65 + i*20))
    
    def draw_ending(self):
        self.screen.fill(BLACK)
        
        if self.current_ending in self.endings:
            ending = self.endings[self.current_ending]
            title = self.title_font.render(ending["title"], True, GOLD)
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
            
            # Разбиваем описание на строки
            words = ending["description"].split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if self.font.size(test_line)[0] < SCREEN_WIDTH - 100:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            for i, line in enumerate(lines):
                line_surf = self.font.render(line, True, GOLD)
                self.screen.blit(line_surf, (50, 180 + i*30))
        else:
            title = self.title_font.render("КОНЕЦ ИГРЫ", True, GOLD)
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
        
        restart = self.font.render("Нажмите R для новой игры", True, GOLD)
        self.screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, 450))
        
        menu = self.font.render("Нажмите ESC для выхода в меню", True, GOLD)
        self.screen.blit(menu, (SCREEN_WIDTH//2 - menu.get_width()//2, 500))
    
    def run(self):
        running = True
        dragged_card = None
        drag_offset = (0, 0)
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            # Обновление hover для кнопок
            for btn in self.buttons:
                btn.update_hover(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.game_state == "menu":
                        self.game_state = "game"
                    elif event.key == pygame.K_r and self.game_state == "ending":
                        self.__init__()  # Полный рестарт
                    elif event.key == pygame.K_ESCAPE:
                        if self.game_state == "ending":
                            self.game_state = "menu"
                
                elif event.type == pygame.MOUSEBUTTONDOWN and self.game_state == "game":
                    # Проверка кнопок
                    for btn in self.buttons:
                        if btn.is_clicked(mouse_pos):
                            self.perform_action(btn.text)
                            break
                    
                    # Проверка карт
                    for card in self.cards:
                        if card.is_clicked(mouse_pos):
                            dragged_card = card
                            drag_offset = (mouse_pos[0] - card.x, mouse_pos[1] - card.y)
                            card.z_index = 100  # Поднимаем наверх
                            # Перемещаем в конец списка для отрисовки поверх
                            self.cards.remove(card)
                            self.cards.append(card)
                            break
                
                elif event.type == pygame.MOUSEBUTTONUP and self.game_state == "game":
                    dragged_card = None
                
                elif event.type == pygame.MOUSEMOTION and self.game_state == "game":
                    if dragged_card:
                        new_x = mouse_pos[0] - drag_offset[0]
                        new_y = mouse_pos[1] - drag_offset[1]
                        
                        # Границы игрового поля (без панели)
                        new_x = max(10, min(new_x, SCREEN_WIDTH - PANEL_WIDTH - CARD_WIDTH - 10))
                        new_y = max(70, min(new_y, SCREEN_HEIGHT - CARD_HEIGHT - 110))
                        
                        dragged_card.x = new_x
                        dragged_card.y = new_y
            
            # Отрисовка
            if self.game_state == "menu":
                self.draw_menu()
            elif self.game_state == "game":
                self.draw_game()
            elif self.game_state == "ending":
                self.draw_ending()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

# Запуск игры
game = CultGame()
game.run()