class UserState:
    def __init__(self, username="неизвестный"):
        self.username = username
        self.total_solved = 0
        self.waiting_answer = False
        self.correct_answer = None
        self.is_code_task = False
        self.task_message_id = None
        self.menu_message_id = None
        self.solved_derivative = 0
        self.solved_logarithm = 0
        self.solved_combinatorics = 0
        self.solved_lore = 0
        self.solved_code = 0
        self.safe_unlocked = False
        self.safe_opened = False
        self._current_task_type = None
        self.last_task_type = None
        self.used_derivative = []
        self.used_logarithm = []
        self.used_combinatorics = []
        self.used_lore = []
        self.used_code = []
        self.interrogations_total = 0
        self.interrogations_used = []
        self.deriv_bonus_claimed = False
        self.log_bonus_claimed = False
        self.evidence_unlocked = False   # ← улики
        self.game_start_time = None
        self.game_active = False
        self.waiting_accusation = False
    def debug_unlock_all(self):
        self.evidence_unlocked = True
        self.safe_unlocked = True
        self.safe_opened = True
        self.interrogations_total = 4
        self.deriv_bonus_claimed = True
        self.log_bonus_claimed = True
        self.solved_derivative = 5
        self.solved_logarithm = 5
        self.solved_combinatorics = 2
        self.solved_lore = 2
        self.total_solved = 20

users = {}

def get_user(user_id, username=None):
    if user_id not in users:
        users[user_id] = UserState(username or "неизвестный")
    elif username and users[user_id].username == "неизвестный":
        users[user_id].username = username
    return users[user_id]

def get_all_users():
    return sorted(users.values(), key=lambda u: u.total_solved, reverse=True)