import random

DERIVATIVE_TASKS = [
    ("f(x) = x³ в x=4.", 48.0),
    ("f(x) = ln(2x) в x=1.", 1.0),
    ("g(x) = e²ˣ в x=0.", 2.0),
    ("h(x) = √x в x=9.", 1/6),
    ("f(x) = 2x³−5x²+3x−7. f'(1).", -1.0),
    ("f(x) = sin(x). f'(0).", 1.0),
    ("f(x) = cos(x). f'(π/2).", -1.0),
    ("f(x) = x⁴ в x=2.", 32.0),
    ("f(x) = 3x² в x=5.", 30.0),
    ("f(x) = 1/x в x=2.", -0.25),
]

LOGARITHM_TASKS = [
    ("log₂(32) = ?", 5.0),
    ("log₃(81) = ?", 4.0),
    ("log₅(125) = ?", 3.0),
    ("log₇(49) = ?", 2.0),
    ("log₁₀(1000) = ?", 3.0),
    ("log₄(64) = ?", 3.0),
    ("log₉(81) = ?", 2.0),
    ("log₂(128) = ?", 7.0),
    ("log₃(243) = ?", 5.0),
    ("log₅(625) = ?", 4.0),
]

COMBINATORICS_TASKS = [
    ("C₄² (выбрать 2 из 4)", 6.0),
    ("Перестановки Л,Е,О", 6.0),
    ("C₅³ (выбрать 3 из 5)", 10.0),
    ("Капитан+зам из 6 чел.", 30.0),
    ("Двузначные из 1,2,3 с повт.", 9.0),
    ("C₆² (выбрать 2 из 6)", 15.0),
    ("Перестановки К,О,Т", 6.0),
    ("Рассадить 4 гостей", 24.0),
]

LORE_TASKS = [
    ("кто главный? Имя.", "Алексей"),
    ("Кто отключил камеры с терминала охраны? Имя.", "Максим"),
    ("Кто вела тайные переговоры с конкурентами? Имя.", "Елена"),
    ("Кто ночевал в офисе в ночь кражи? Имя.", "Виктор"),
    ("Кто оставил пост без присмотра? Имя. ", "Борис"),
    ("Кто был в отпуске в Турции, но его код доступа использовали? Имя.", "Николай")
]

TASK_MAP = {
    "derivative": (DERIVATIVE_TASKS, False),
    "logarithm": (LOGARITHM_TASKS, False),
    "combinatorics": (COMBINATORICS_TASKS, False),
    "lore": (LORE_TASKS, "string"),
}

def get_random_task(user, tasks, used_list):
    available = [i for i in range(len(tasks)) if i not in used_list]
    if not available:
        used_list.clear()
        available = list(range(len(tasks)))
    index = random.choice(available)
    used_list.append(index)
    return tasks[index]