import pygame
import random
import math
import json
import os

# --- Configuration Constants ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SIM_WIDTH = 900
UI_WIDTH = SCREEN_WIDTH - SIM_WIDTH

POPULATION_SIZE = 400
AGENT_RADIUS = 5
TICKS_PER_DAY = 60
AVG_CONTACTS_PER_DAY = 8
PROFILES_FILENAME = "disease_profiles.json"

# --- SIMULATION CAMPAIGN SETTINGS ---
INITIAL_VACCINATION_PERCENTAGE = 0.10  # 10% of population starts vaccinated
DAILY_VACCINATIONS = 4                # Number of people vaccinated per day

# --- Colors ---
COLOR_S, COLOR_E, COLOR_I = (150, 150, 255), (255, 255, 100), (255, 50, 50)
COLOR_V = (200, 150, 255)
COLOR_RF, COLOR_RL, COLOR_D = (50, 200, 50), (0, 100, 0), (80, 80, 80)
BACKGROUND_COLOR, UI_BACKGROUND_COLOR = (10, 10, 20), (30, 40, 50)
TEXT_COLOR, CHART_BG_COLOR = (230, 230, 230), (15, 20, 25)
BUTTON_COLOR, BUTTON_HOVER_COLOR = (80, 100, 120), (110, 130, 150)
BUTTON_DELETE_COLOR, BUTTON_DELETE_HOVER_COLOR = (180, 50, 50), (220, 80, 80)
INPUT_BOX_COLOR, INPUT_BOX_ACTIVE_COLOR = (20, 30, 40), (100, 110, 120)
ERROR_COLOR = (255, 100, 100)

# --- Base Disease Presets with Vaccine & Campaign Data ---
BASE_DISEASE_PRESETS = {
    "Influenza": {"R0": "1.3", "incubation_days": "2", "infectious_days": "5", "fatality_rate": "0.001", "long_term_effect_rate": "0.0",
                  "vaccine_efficacy": "0.5", "vaccine_mortality_rate": "0.000001", "vaccine_long_term_effect_rate": "0.000001",
                  "initial_vax_rate": "0.4", "daily_vax_rate": "2"},
    "COVID-19": {"R0": "2.5", "incubation_days": "5", "infectious_days": "7", "fatality_rate": "0.01", "long_term_effect_rate": "0.10",
                 "vaccine_efficacy": "0.9", "vaccine_mortality_rate": "0.000002", "vaccine_long_term_effect_rate": "0.00005",
                 "initial_vax_rate": "0.0", "daily_vax_rate": "8"},
    "Ebola": {"R0": "2.0", "incubation_days": "8", "infectious_days": "6", "fatality_rate": "0.5", "long_term_effect_rate": "0.05",
              "vaccine_efficacy": "0.97", "vaccine_mortality_rate": "0.00001", "vaccine_long_term_effect_rate": "0.0001",
              "initial_vax_rate": "0.0", "daily_vax_rate": "1"},
    "Measles": {"R0": "15", "incubation_days": "10", "infectious_days": "8", "fatality_rate": "0.002", "long_term_effect_rate": "0.001",
                "vaccine_efficacy": "0.97", "vaccine_mortality_rate": "0.000001", "vaccine_long_term_effect_rate": "0.0",
                "initial_vax_rate": "0.8", "daily_vax_rate": "0"},
    "Chickenpox": {"R0": "11", "incubation_days": "14", "infectious_days": "7", "fatality_rate": "0.0001", "long_term_effect_rate": "0.0",
                   "vaccine_efficacy": "0.9", "vaccine_mortality_rate": "0.000001", "vaccine_long_term_effect_rate": "0.0",
                   "initial_vax_rate": "0.7", "daily_vax_rate": "0"},
    "Mumps": {"R0": "5", "incubation_days": "18", "infectious_days": "7", "fatality_rate": "0.0001", "long_term_effect_rate": "0.01",
              "vaccine_efficacy": "0.88", "vaccine_mortality_rate": "0.000001", "vaccine_long_term_effect_rate": "0.0",
              "initial_vax_rate": "0.8", "daily_vax_rate": "0"},
    "Pertussis": {"R0": "15", "incubation_days": "9", "infectious_days": "21", "fatality_rate": "0.005", "long_term_effect_rate": "0.0",
                  "vaccine_efficacy": "0.85", "vaccine_mortality_rate": "0.000001", "vaccine_long_term_effect_rate": "0.0",
                  "initial_vax_rate": "0.6", "daily_vax_rate": "1"},
    "Polio": {"R0": "6", "incubation_days": "10", "infectious_days": "14", "fatality_rate": "0.005", "long_term_effect_rate": "0.01",
              "vaccine_efficacy": "0.99", "vaccine_mortality_rate": "0.0000004", "vaccine_long_term_effect_rate": "0.0000004",
              "initial_vax_rate": "0.5", "daily_vax_rate": "5"},
    "Smallpox": {"R0": "6", "incubation_days": "12", "infectious_days": "9", "fatality_rate": "0.3", "long_term_effect_rate": "0.05",
                 "vaccine_efficacy": "0.95", "vaccine_mortality_rate": "0.00001", "vaccine_long_term_effect_rate": "0.0001",
                 "initial_vax_rate": "0.0", "daily_vax_rate": "10"},
}

# --- Helper Functions & Classes ---
def draw_text(screen, text, pos, font, color=TEXT_COLOR, center_x=False, center_y=False):
    surface = font.render(text, True, color); rect = surface.get_rect(topleft=pos)
    if center_x: rect.centerx = pos[0]
    if center_y: rect.centery = pos[1]
    screen.blit(surface, rect)
    return rect

class Button:
    def __init__(self, rect, text, font, color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR):
        self.rect, self.text, self.font = pygame.Rect(rect), text, font
        self.colors = {'normal': color, 'hover': hover_color}; self.is_hovered = False
    def draw(self, screen):
        color = self.colors['hover'] if self.is_hovered else self.colors['normal']
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        draw_text(screen, self.text, self.rect.center, self.font, center_x=True, center_y=True)
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION: self.is_hovered = self.rect.collidepoint(event.pos)
        return event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered

class InputBox:
    def __init__(self, rect, label, initial_text, font, numeric_only=False):
        self.rect, self.label, self.text, self.font = pygame.Rect(rect), label, initial_text, font
        self.is_active = False; self.numeric_only = numeric_only
    def draw(self, screen):
        draw_text(screen, self.label, (self.rect.x, self.rect.y - 22), self.font)
        border_color = INPUT_BOX_ACTIVE_COLOR if self.is_active else BUTTON_COLOR
        pygame.draw.rect(screen, INPUT_BOX_COLOR, self.rect); pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=3)
        draw_text(screen, self.text, (self.rect.x + 10, self.rect.y + 10), self.font)
    def handle_event(self, event, clear_error_callback):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.is_active = self.rect.collidepoint(event.pos)
            if self.is_active: clear_error_callback()
        if event.type == pygame.KEYDOWN and self.is_active:
            if event.key == pygame.K_BACKSPACE: self.text = self.text[:-1]
            elif self.numeric_only:
                if event.unicode.isdigit() or (event.unicode == '.' and '.' not in self.text): self.text += event.unicode
            else: self.text += event.unicode

class Agent:
    def __init__(self, state='S'):
        self.x, self.y = random.randint(AGENT_RADIUS, SIM_WIDTH - AGENT_RADIUS), random.randint(AGENT_RADIUS, SCREEN_HEIGHT - AGENT_RADIUS)
        self.radius, self.state, self.timer = AGENT_RADIUS, state, 0
        angle = random.uniform(0, 2 * math.pi); self.speed = random.uniform(0.5, 1.5)
        self.dx, self.dy = math.cos(angle) * self.speed, math.sin(angle) * self.speed
    def move(self):
        if self.state == 'D': return
        self.x += self.dx; self.y += self.dy
        if self.x <= self.radius or self.x >= SIM_WIDTH - self.radius: self.dx *= -1
        if self.y <= self.radius or self.y >= SCREEN_HEIGHT - self.radius: self.dy *= -1
    def update_state(self, disease_params):
        if self.state in ['E', 'I']:
            self.timer -= 1
            if self.timer <= 0:
                if self.state == 'E': self.state = 'I'; self.timer = disease_params["infectious_ticks"]
                elif self.state == 'I':
                    if random.random() < disease_params["fatality_rate"]: self.state = 'D'
                    else:
                        if random.random() < disease_params["long_term_effect_rate"]: self.state = 'R_LONG'; self.speed *= 0.4
                        else: self.state = 'R_FULL'
    def draw(self, screen):
        color_map = {'S': COLOR_S, 'V': COLOR_V, 'E': COLOR_E, 'I': COLOR_I, 'R_FULL': COLOR_RF, 'R_LONG': COLOR_RL, 'D': COLOR_D}
        pygame.draw.circle(screen, color_map.get(self.state, (255,255,255)), (int(self.x), int(self.y)), self.radius)

class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)); pygame.display.set_caption("Epidemic Simulator")
        self.clock = pygame.time.Clock()
        self.font_lg, self.font_md, self.font_sm = pygame.font.SysFont("sans-serif", 36), pygame.font.SysFont("sans-serif", 24), pygame.font.SysFont("monospace", 15)
        self.app_state = "MENU"; self.menu_error_message = ""
        self.disease_params = {}; self._load_profiles(); self._setup_menu(); self._init_sim_state_vars()
    def _init_sim_state_vars(self):
        self.population, self.stats, self.commentary = [], {}, ""; self.ticks, self.peak_infected_count, self.peak_infected_reached = 0, 0, False
        self.history, self.vaccination_counter = [], 0.0
        self.vax_deaths, self.vax_long_term_effects = 0, 0
        self.total_sick_days = 0.0
    def _load_profiles(self):
        self.all_diseases = BASE_DISEASE_PRESETS.copy()
        if os.path.exists(PROFILES_FILENAME):
            try:
                with open(PROFILES_FILENAME, 'r') as f: self.all_diseases.update(json.load(f))
            except (json.JSONDecodeError, TypeError): print(f"Warning: Could not read {PROFILES_FILENAME}.")
    def _save_profiles(self):
        custom_to_save = {name: params for name, params in self.all_diseases.items() if name not in BASE_DISEASE_PRESETS}
        with open(PROFILES_FILENAME, 'w') as f: json.dump(custom_to_save, f, indent=4)
    def _setup_menu(self):
        self.menu_buttons, self.selected_disease_name = {}, None; self._refresh_menu_buttons()
        editor_x, editor_y = 450, 120
        self.input_boxes = {
            "name": InputBox((editor_x, editor_y, 400, 40), "Disease Name", "My Disease", self.font_md),
            "R0": InputBox((editor_x, editor_y + 80, 100, 40), "R0", "3.0", self.font_md, numeric_only=True),
            "incubation_days": InputBox((editor_x + 150, editor_y + 80, 100, 40), "Incubation (d)", "5", self.font_md, numeric_only=True),
            "infectious_days": InputBox((editor_x + 300, editor_y + 80, 100, 40), "Infectious (d)", "10", self.font_md, numeric_only=True),
            "fatality_rate": InputBox((editor_x, editor_y + 160, 100, 40), "Fatality Rate", "0.03", self.font_md, numeric_only=True),
            "long_term_effect_rate": InputBox((editor_x + 150, editor_y + 160, 140, 40), "Long-Term Rate", "0.1", self.font_md, numeric_only=True),
            "vaccine_efficacy": InputBox((editor_x, editor_y + 240, 100, 40), "Vax Efficacy (0-1)", "0.95", self.font_md, numeric_only=True),
            "vaccine_mortality_rate": InputBox((editor_x+150, editor_y+240, 100, 40), "Vax Mortality", "0.000001", self.font_md, numeric_only=True),
            "vaccine_long_term_effect_rate": InputBox((editor_x+300, editor_y+240, 100, 40), "Vax Long-Term", "0.00001", self.font_md, numeric_only=True),
            "initial_vax_rate": InputBox((editor_x, editor_y + 350, 180, 40), "Initial Vax Rate (0-1)", "0.1", self.font_md, numeric_only=True),
            "daily_vax_rate": InputBox((editor_x + 220, editor_y + 350, 180, 40), "Daily Vax Rate (pop/day)", "4", self.font_md, numeric_only=True),
        }
        self.save_button = Button((editor_x, editor_y + 430, 180, 50), "Save Profile", self.font_md)
        self.delete_button = Button((editor_x + 220, editor_y + 430, 180, 50), "Delete Profile", self.font_md, BUTTON_DELETE_COLOR, BUTTON_DELETE_HOVER_COLOR)
        self.start_button = Button((editor_x, editor_y + 500, 400, 60), "Start Simulation", self.font_md)
    def _refresh_menu_buttons(self):
        self.menu_buttons.clear(); y_offset = 120
        for name in sorted(self.all_diseases.keys()):
            self.menu_buttons[name] = Button((30, y_offset, 350, 40), name, self.font_md); y_offset += 50
    def _prepare_and_start_simulation(self, params_dict, name):
        self.menu_error_message = ""
        try:
            if not name.strip(): self.menu_error_message = "Error: Disease Name cannot be empty."; return
            processed_params = {key: float(val) for key, val in params_dict.items()}
            if any(v < 0 for v in processed_params.values()): self.menu_error_message = "Error: All numeric values must be non-negative."; return
            if processed_params["infectious_days"] <= 0: self.menu_error_message = "Error: Infectious period must be > 0."; return
            if not (0 <= processed_params["vaccine_efficacy"] <= 1): self.menu_error_message = "Error: Vax Efficacy must be between 0.0 and 1.0."; return
            if not (0 <= processed_params["initial_vax_rate"] <= 1): self.menu_error_message = "Error: Initial Vax Rate must be between 0.0 and 1.0."; return

            self.disease_params = processed_params; self.disease_params["name"] = name
            self.disease_params["transmission_prob"] = self.disease_params["R0"] / (AVG_CONTACTS_PER_DAY * self.disease_params["infectious_days"])
            self.disease_params["incubation_ticks"] = int(self.disease_params["incubation_days"]) * TICKS_PER_DAY
            self.disease_params["infectious_ticks"] = int(self.disease_params["infectious_days"]) * TICKS_PER_DAY
            
            self._reset_simulation(); self.app_state = "SIMULATION"
        except ValueError: self.menu_error_message = "Error: A numeric field is empty or has invalid text."
        except KeyError as e: self.menu_error_message = f"Error: Missing parameter data for {e}."
    def _vaccinate_agent(self, agent):
        if agent.state != 'S': return
        if random.random() < self.disease_params["vaccine_mortality_rate"]:
            agent.state = 'D'; self.vax_deaths += 1
        elif random.random() < self.disease_params["vaccine_long_term_effect_rate"]:
            agent.state = 'R_LONG'; agent.speed *= 0.4; self.vax_long_term_effects += 1
        else: agent.state = 'V'
    def _reset_simulation(self):
        self._init_sim_state_vars()
        self.population = [Agent('S') for _ in range(POPULATION_SIZE)]
        if POPULATION_SIZE > 0:
            num_to_vaccinate = int(POPULATION_SIZE * self.disease_params["initial_vax_rate"])
            if len(self.population) >= num_to_vaccinate:
                for agent in random.sample(self.population, num_to_vaccinate): self._vaccinate_agent(agent)
        
        susceptible_pool = [agent for agent in self.population if agent.state == 'S']
        if susceptible_pool:
            patient_zero = random.choice(susceptible_pool)
            patient_zero.state = 'E'; patient_zero.timer = self.disease_params["incubation_ticks"]
        
        self._update_stats(); self.history.append(self.stats['counts'])
        self.commentary = "The simulation has started."
    def run(self):
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT: running = False
            if not running: break
            if self.app_state == "MENU": self.run_menu(events)
            elif self.app_state == "SIMULATION": self.run_simulation(events)
            pygame.display.flip(); self.clock.tick(60)
        pygame.quit()
    def run_menu(self, events):
        self.screen.fill(UI_BACKGROUND_COLOR)
        draw_text(self.screen, "Disease & Vaccine Simulator", (SCREEN_WIDTH / 2, 50), self.font_lg, center_x=True)
        draw_text(self.screen, "Disease Library", (205, 80), self.font_md, center_x=True)
        draw_text(self.screen, "Profile Editor", (650, 80), self.font_md, center_x=True)
        for event in events:
            for name, button in self.menu_buttons.items():
                if button.handle_event(event):
                    self.selected_disease_name = name; self.menu_error_message = ""
                    self.input_boxes["name"].text = name
                    for key, val in self.all_diseases[name].items(): self.input_boxes[key].text = str(val)
            for box in self.input_boxes.values(): box.handle_event(event, lambda: setattr(self, 'menu_error_message', ''))
            if self.save_button.handle_event(event):
                if new_name := self.input_boxes["name"].text.strip():
                    self.all_diseases[new_name] = {key: box.text for key, box in self.input_boxes.items() if key != 'name'}
                    self._save_profiles(); self._refresh_menu_buttons(); self.selected_disease_name = new_name
                else: self.menu_error_message = "Error: Disease Name cannot be empty."
            if self.delete_button.handle_event(event) and self.selected_disease_name and self.selected_disease_name not in BASE_DISEASE_PRESETS:
                del self.all_diseases[self.selected_disease_name]; self._save_profiles(); self._refresh_menu_buttons(); self.selected_disease_name = None
            if self.start_button.handle_event(event):
                self._prepare_and_start_simulation({key: box.text for key, box in self.input_boxes.items() if key != 'name'}, self.input_boxes["name"].text)
        for button in self.menu_buttons.values(): button.is_hovered = button.rect.collidepoint(pygame.mouse.get_pos()); button.draw(self.screen)
        for box in self.input_boxes.values(): box.draw(self.screen)
        self.save_button.draw(self.screen); self.start_button.draw(self.screen)
        if self.selected_disease_name and self.selected_disease_name not in BASE_DISEASE_PRESETS: self.delete_button.draw(self.screen)
        if self.menu_error_message: draw_text(self.screen, self.menu_error_message, (self.input_boxes["name"].rect.left, 640), self.font_md, color=ERROR_COLOR)
    def run_simulation(self, events):
        for event in events:
             if event.type == pygame.KEYDOWN and event.key == pygame.K_m: self.app_state = "MENU"; return
        self.ticks += 1; previous_counts = self.stats.get('counts', {}); self._update_stats(); self._update_commentary(previous_counts)
        self._handle_vaccination_campaign(); self._handle_infections()
        for agent in self.population: agent.move(); agent.update_state(self.disease_params)
        self.screen.fill(BACKGROUND_COLOR); [agent.draw(self.screen) for agent in self.population]; self._draw_simulation_ui()
    def _handle_vaccination_campaign(self):
        self.vaccination_counter += self.disease_params.get("daily_vax_rate", 0) / TICKS_PER_DAY
        if self.vaccination_counter >= 1:
            num_to_vaccinate = int(self.vaccination_counter)
            susceptible = [agent for agent in self.population if agent.state == 'S']
            if susceptible:
                for agent in random.sample(susceptible, min(num_to_vaccinate, len(susceptible))): self._vaccinate_agent(agent)
            self.vaccination_counter -= num_to_vaccinate
    def _handle_infections(self):
        infectious = [a for a in self.population if a.state == 'I'];
        if not infectious: return
        eligible_targets = [a for a in self.population if a.state in ('S', 'V')]
        vax_transmission_prob = self.disease_params["transmission_prob"] * (1 - self.disease_params["vaccine_efficacy"])
        for infector in infectious:
            for target in eligible_targets:
                if target.state in ('S', 'V') and (infector.x - target.x)**2 + (infector.y - target.y)**2 < (infector.radius * 2 + 2)**2:
                    prob = self.disease_params["transmission_prob"] if target.state == 'S' else vax_transmission_prob
                    if random.random() < prob: target.state = 'E'; target.timer = self.disease_params["incubation_ticks"]
    def _update_stats(self):
        counts = {'S': 0, 'E': 0, 'I': 0, 'V': 0, 'R_FULL': 0, 'R_LONG': 0, 'D': 0}
        for agent in self.population: counts[agent.state] = counts.get(agent.state, 0) + 1
        effective_susceptible = counts['S'] + (counts['V'] * (1 - self.disease_params.get("vaccine_efficacy", 1.0)))
        if POPULATION_SIZE > 0:
            self.stats = {"counts": counts, "elapsed_days": self.ticks // TICKS_PER_DAY, "Rt": self.disease_params.get("R0", 0) * (effective_susceptible / POPULATION_SIZE)}
            self.total_sick_days += counts['I'] / TICKS_PER_DAY
        if self.ticks > 0 and self.ticks % TICKS_PER_DAY == 0: self.history.append(self.stats['counts'])
    def _update_commentary(self, previous_counts):
        current_I, prev_I = self.stats.get("counts", {}).get("I", 0), previous_counts.get("I", 0)
        if current_I > self.peak_infected_count: self.peak_infected_count = current_I
        if current_I > 0 and prev_I == 0: self.commentary = "The outbreak has begun."
        elif current_I > prev_I and not self.peak_infected_reached: self.commentary = f"Exponential growth phase. R(t) is {self.stats.get('Rt', 0):.2f}."
        elif current_I < prev_I and not self.peak_infected_reached and current_I > 0: self.peak_infected_reached = True; self.commentary = f"Outbreak has peaked with {self.peak_infected_count} infected ({(self.peak_infected_count/POPULATION_SIZE)*100:.1f}%)."
        elif self.peak_infected_reached and current_I > 0: self.commentary = "The outbreak is receding due to immunity and vaccinations."
        elif current_I == 0 and self.stats.get("counts", {}).get('E', 0) == 0 and self.ticks > self.disease_params.get("incubation_ticks", 1)*2:
            total_dead_disease = self.stats['counts']['D'] - self.vax_deaths
            self.commentary = f"The epidemic has ended, leaving {total_dead_disease} dead from disease."
    def _draw_chart(self, rect):
        pygame.draw.rect(self.screen, CHART_BG_COLOR, rect)
        if not self.history: return
        y_scale = rect.height / POPULATION_SIZE if POPULATION_SIZE > 0 else 0
        chart_data_points = self.history[-(rect.width - 2):]
        stacking_order = ['S', 'V', 'E', 'I', 'R_FULL', 'R_LONG', 'D']
        color_map = {'S': COLOR_S, 'V': COLOR_V, 'E': COLOR_E, 'I': COLOR_I, 'R_FULL': COLOR_RF, 'R_LONG': COLOR_RL, 'D': COLOR_D}
        for i, counts in enumerate(chart_data_points):
            x, y_bottom = rect.left + 1 + i, rect.bottom -1
            for state in stacking_order:
                if (count := counts.get(state, 0)) > 0:
                    y_top = y_bottom - (count * y_scale); pygame.draw.line(self.screen, color_map[state], (x, y_bottom), (x, y_top)); y_bottom = y_top
    def _draw_simulation_ui(self):
        pygame.draw.rect(self.screen, UI_BACKGROUND_COLOR, (SIM_WIDTH, 0, UI_WIDTH, SCREEN_HEIGHT))
        y, x, margin = 10, SIM_WIDTH + 20, 20
        draw_text(self.screen, "LIVE ANALYSIS", (x + (UI_WIDTH - 2*margin)/2, y), self.font_md, center_x=True); y += 30
        draw_text(self.screen, self.disease_params.get('name', 'N/A'), (x + (UI_WIDTH-2*margin)/2, y), self.font_lg, center_x=True); y += 35
        
        # Main KPIs
        kpi_lines = [f"Elapsed Days: {self.stats.get('elapsed_days', 0)}", f"Effective R(t): {self.stats.get('Rt', 0):.2f}", f"Total Sick Days: {int(self.total_sick_days)}"]
        for line in kpi_lines: draw_text(self.screen, line, (x, y), self.font_sm); y += 18
        y += 5
        
        # Population state breakdown
        key_items = [("Susceptible", COLOR_S, 'S'), ("Vaccinated", COLOR_V, 'V'), ("Exposed", COLOR_E, 'E'),
                     ("Infectious", COLOR_I, 'I'), ("Recovered (Full)", COLOR_RF, 'R_FULL'),
                     ("Recovered (Long)", COLOR_RL, 'R_LONG'), ("Deceased", COLOR_D, 'D')]
        for label, color, state_key in key_items:
            count = self.stats.get('counts', {}).get(state_key, 0)
            percent = (count / POPULATION_SIZE) * 100 if POPULATION_SIZE > 0 else 0
            line = f"{label}: {count} ({percent:.1f}%)"
            pygame.draw.rect(self.screen, color, (x, y, 15, 15)); draw_text(self.screen, line, (x + 25, y - 1), self.font_sm); y += 20
        y += 5
        
        # Vaccine Outcomes
        draw_text(self.screen, "Vaccine Outcomes:", (x,y), self.font_sm); y += 20
        draw_text(self.screen, f"  Fatalities: {self.vax_deaths}", (x,y), self.font_sm); y += 18
        draw_text(self.screen, f"  Long-Term Effects: {self.vax_long_term_effects}", (x,y), self.font_sm); y += 25
        
        # Commentary
        draw_text(self.screen, "Commentary:", (x, y), self.font_sm); y += 20
        words = self.commentary.split(' '); lines = []; current_line = ""
        for word in words:
            if self.font_sm.size(current_line + word)[0] < UI_WIDTH - 40: current_line += word + " "
            else: lines.append(current_line); current_line = word + " "
        lines.append(current_line)
        for line in lines: draw_text(self.screen, line.strip(), (x, y), self.font_sm); y += 18
        y += 5
        
        # Chart
        draw_text(self.screen, "Population Chart (Days)", (x + (UI_WIDTH-2*margin)/2, y), self.font_sm, center_x=True); y += 20
        chart_rect = pygame.Rect(x, y, UI_WIDTH - 2*margin, 120)
        self._draw_chart(chart_rect)
        draw_text(self.screen, "Press [M] for Menu", (SIM_WIDTH + UI_WIDTH/2, SCREEN_HEIGHT - 30), self.font_sm, center_x=True)

if __name__ == "__main__":
    sim = Simulation()
    sim.run()