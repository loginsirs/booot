# Улики и условия их открытия.
# Каждая улика: название, путь к файлу, функция-условие (принимает user), подсказка.
EVIDENCE_ITEMS = [
    {
        "name": "📞 Записи звонков Алексея",
        "file": "images/calls.png",
        "unlocked": lambda user: user.evidence_unlocked,  # после 2 лор‑вопросов
        "hint": "Решите 2 лор‑вопроса",
        "caption": "Детализация звонков Алексея за последнюю неделю."
    },
    {
        "name": "📷 Снимок камеры 04:00",
        "file": "images/cctv_5am.png",
        "unlocked": lambda user: "Николай" in user.interrogations_used,  # допрос Николая
        "hint": "Допросите Николая",
        "caption": "На камере видно, что в 04:00 ч утра Алексей вышел из лаборатории. Но кража же была раньше?"
    },
    {
        "name": "🔓 Содержимое сейфа",
        "file": "images/safe_content.png",
        "unlocked": lambda user: user.safe_opened,
        "hint": "Решите 2 комбинаторики",
        "caption": "пустой сейф..."
    },
    {
        "name": "🖐️ Отпечатки пальцев с сейфа",
        "file": "images/fingerprints.png",
        "unlocked": lambda user: user.solved_derivative >= 5,  # после 5/5 производных
        "hint": "Решите 5 производных",
        "caption": "Анализ отпечатков совпадает с отпечатками Елены"
    },
    {
        "name": "📱 Номер на столе Алексея",
        "file": "images/doctor_phone.png",
        "unlocked": lambda user: "Зухра" in user.interrogations_used,  # допрос Зухра
        "hint": "Допросите Зухра",
        "caption": "Странный номер на столе Алексея"
    },
    {
        "name": "🧾 Мусорка",
        "file": "images/Mysorka.png",
        "unlocked": lambda user: user.solved_logarithm >= 5,  # после 5/5 логарифмов
        "hint": "Решите 5 логарифмов",
        "caption": "То что Борис оставил в мусорке."
    }
]