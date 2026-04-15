from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import datetime
import random

app = Flask(__name__)
app.secret_key = "wellness_secret_2024"

# In-memory user store (in production, use a database)
users_db = {}
health_data = {}

def get_user_data(email):
    if email not in health_data:
        health_data[email] = {
            "moods": [],
            "water": [],
            "sleep": [],
            "habits": [],
            "periods": [],
            "chat_history": []
        }
    return health_data[email]

# ─── AI Chatbot Logic ─────────────────────────────────────────────────────────
STRESS_TIPS = [
    "Take 5 deep breaths right now. Inhale for 4 counts, hold for 4, exhale for 6. 🌬️",
    "Step outside for just 5 minutes. Natural light resets your nervous system. ☀️",
    "Try the 5-4-3-2-1 technique: name 5 things you see, 4 you hear, 3 you can touch, 2 you smell, 1 you taste. 🌿",
    "Drink a glass of cold water slowly. Hydration helps your brain function under stress. 💧",
    "Write down 3 things you're grateful for right now. It shifts your brain chemistry instantly. 📝",
    "Put on your favorite song and let yourself feel it. Music therapy is scientifically proven! 🎵",
    "Do 10 jumping jacks. Physical movement releases endorphins that counter stress hormones. 🏃",
    "Call or text someone you love. Social connection lowers cortisol levels naturally. 💬",
]

GREETINGS = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon", "howdy"]
STRESS_WORDS = ["stress", "stressed", "anxious", "anxiety", "worried", "panic", "overwhelmed", "nervous", "scared", "fear"]
SAD_WORDS = ["sad", "depressed", "depression", "cry", "crying", "lonely", "hopeless", "unhappy", "miserable", "down"]
TIRED_WORDS = ["tired", "exhausted", "fatigue", "sleepy", "no energy", "burnout", "drained", "weak"]
HAPPY_WORDS = ["happy", "great", "amazing", "wonderful", "good", "fantastic", "excited", "joy", "glad"]

def ai_chatbot_response(user_message, user_name, gender):
    msg = user_message.lower().strip()
    
    # Greetings
    if any(g in msg for g in GREETINGS):
        return f"Hey {user_name}! 😊 I'm Zara, your wellness companion. How are you feeling today? You can tell me anything — I'm here to listen and help! 💙"
    
    # Stress
    if any(w in msg for w in STRESS_WORDS):
        tip = random.choice(STRESS_TIPS)
        return f"I hear you, {user_name}. Stress can feel really overwhelming. 💙\n\nHere's something that can help right now:\n\n**{tip}**\n\nRemember: you've gotten through 100% of your difficult days so far. You're stronger than you think. Want me to guide you through a breathing exercise? 🌿"
    
    # Sadness
    if any(w in msg for w in SAD_WORDS):
        return f"I'm really sorry you're feeling this way, {user_name}. 🌧️ Your feelings are completely valid.\n\nSometimes sadness is just your heart asking for extra care. A few gentle things:\n\n• Be kind to yourself today\n• Reach out to someone you trust\n• Do one tiny thing that brings comfort (tea, a walk, music)\n\nIf these feelings persist, please consider talking to a mental health professional. You deserve support. 💛 I'm here — keep talking to me."
    
    # Tired
    if any(w in msg for w in TIRED_WORDS):
        return f"Feeling drained is your body's SOS signal, {user_name}. 😴\n\nQuick energy reset tips:\n• **Power nap** — 15-20 mins (set an alarm!)\n• **Hydrate** — even mild dehydration causes fatigue\n• **Stretch** — 5 mins of gentle movement wakes your body\n• **Check your sleep** — use the Sleep Tracker to find your pattern\n\nAre you getting at least 7 hours of sleep? Let's look at your sleep data together! 🌙"
    
    # Happy
    if any(w in msg for w in HAPPY_WORDS):
        return f"That's absolutely wonderful, {user_name}! 🎉 Your positive energy is contagious!\n\nCapture this feeling — log a happy mood in your Mood Tracker so you can look back on good days when things get tough. 😊\n\nWhat made today great? Share it with me! ✨"
    
    # Sleep queries
    if "sleep" in msg or "insomnia" in msg or "can't sleep" in msg:
        return f"Sleep is so crucial, {user_name}! 🌙 Here are science-backed tips:\n\n• **Consistent schedule** — same bedtime every day, even weekends\n• **No screens 1 hour before bed** — blue light blocks melatonin\n• **Keep room cool** — 65-68°F (18-20°C) is ideal\n• **Avoid caffeine after 2 PM**\n• **Try 4-7-8 breathing** — inhale 4, hold 7, exhale 8 counts\n\nUse our Sleep Tracker to monitor your patterns! 💤"
    
    # Water/hydration
    if "water" in msg or "hydrat" in msg or "drink" in msg:
        return f"Hydration hero mode activated! 💧 {user_name}, did you know your brain is 75% water?\n\nYour daily goal: **8 glasses (2 liters)**\n\nPro tips:\n• Start each morning with a big glass of water\n• Set hourly reminders on your phone\n• Add lemon or mint to make water more appealing\n• Eat water-rich foods: cucumber, watermelon, oranges\n\nLog your water intake using the Water Tracker! 🥤"
    
    # Exercise
    if "exercise" in msg or "workout" in msg or "gym" in msg or "fitness" in msg:
        return f"Love the energy, {user_name}! 💪 Regular movement is a natural antidepressant!\n\nEven if you're busy:\n• **10 min morning stretch** — sets the tone for the day\n• **Walk during calls** — multitask movement!\n• **Desk exercises** — neck rolls, shoulder shrugs, calf raises\n• **7-Minute HIIT** — science-backed quick routine\n\nMark your exercise in the Habits Checklist to build your streak! 🔥"
    
    # Periods (for female users)
    if gender == "female" and any(w in msg for w in ["period", "cycle", "pms", "cramps", "menstrual", "menstruation"]):
        return f"I understand, {user_name}. Period health is so important and often overlooked! 🌸\n\nFor period comfort:\n• **Heat therapy** — warm pad/bottle on lower abdomen\n• **Gentle yoga** — child's pose, cat-cow relieve cramps\n• **Iron-rich foods** — spinach, lentils, dark chocolate\n• **Avoid caffeine** — it worsens cramps\n• **Stay hydrated** — reduces bloating\n\nTrack your cycle in the Period Tracker to predict your next cycle and PMS days! 📅"
    
    # Meditation
    if "meditat" in msg or "mindful" in msg or "calm" in msg or "relax" in msg:
        return f"Mindfulness is your superpower, {user_name}! 🧘\n\n**Quick 2-minute meditation:**\n1. Close your eyes\n2. Take 3 deep breaths\n3. Focus only on the sensation of breathing\n4. When thoughts arise, gently return to breath\n5. Open eyes slowly\n\nEven 2 minutes daily rewires your brain for calm. Try our Breathing Exercise feature! 🌿"
    
    # Help
    if "help" in msg or "what can you do" in msg or "features" in msg:
        return f"I'm Zara, your AI wellness companion! Here's what I can help with, {user_name}:\n\n🧠 **Mental Health** — stress, anxiety, mood support\n💧 **Hydration** — water intake tracking & tips\n😴 **Sleep** — sleep quality analysis\n🏃 **Fitness** — exercise motivation & tips\n{'🌸 **Period Health** — cycle tracking & comfort tips\n' if gender == 'female' else ''}🧘 **Stress Relief** — breathing exercises, meditation\n📊 **Habit Building** — daily wellness routines\n\nJust chat naturally — I understand you! 💙"
    
    # Default response
    responses = [
        f"I'm here for you, {user_name}! 💙 Tell me more about how you're feeling. The more you share, the better I can support you.",
        f"That's really interesting, {user_name}. Your wellness journey is unique! Is there anything specific about your health or mood you'd like to explore today?",
        f"Thank you for sharing that with me, {user_name}. 🌟 Remember, every small step toward wellness counts. What's one healthy thing you can do for yourself right now?",
        f"I hear you, {user_name}. 💚 Whether it's stress, sleep, hydration, or mood — I'm here to help. What area of your wellness would you like to focus on today?",
    ]
    return random.choice(responses)

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if "user_email" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email", "").lower()
    if email in users_db:
        return jsonify({"success": False, "message": "Account already exists! Please login."})
    users_db[email] = {
        "name": data.get("name"),
        "age": data.get("age"),
        "email": email,
        "gender": data.get("gender"),
        "phone": data.get("phone", ""),
        "emergency_contact": data.get("emergency_contact", ""),
        "password": data.get("password"),
        "created": datetime.datetime.now().isoformat()
    }
    return jsonify({"success": True, "message": "Account created successfully!"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email", "").lower()
    password = data.get("password")
    user = users_db.get(email)
    if not user or user["password"] != password:
        return jsonify({"success": False, "message": "Invalid email or password."})
    session["user_email"] = email
    return jsonify({"success": True, "user": {k: v for k, v in user.items() if k != "password"}})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if "user_email" not in session:
        return redirect(url_for("index"))
    user = users_db.get(session["user_email"], {})
    return render_template("dashboard.html", user=user)

@app.route("/api/user")
def get_user():
    if "user_email" not in session:
        return jsonify({"error": "Not logged in"}), 401
    user = users_db.get(session["user_email"], {})
    return jsonify({k: v for k, v in user.items() if k != "password"})

@app.route("/api/mood", methods=["GET", "POST"])
def mood():
    if "user_email" not in session:
        return jsonify({"error": "Not logged in"}), 401
    email = session["user_email"]
    data = get_user_data(email)
    if request.method == "POST":
        entry = request.json
        entry["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        data["moods"].append(entry)
        return jsonify({"success": True, "message": "Mood logged! 😊"})
    return jsonify({"moods": data["moods"][-30:]})

@app.route("/api/water", methods=["GET", "POST"])
def water():
    if "user_email" not in session:
        return jsonify({"error": "Not logged in"}), 401
    email = session["user_email"]
    data = get_user_data(email)
    if request.method == "POST":
        entry = request.json
        today = datetime.date.today().isoformat()
        # Find today's entry or create
        today_entry = next((w for w in data["water"] if w.get("date") == today), None)
        if today_entry:
            today_entry["glasses"] = min(today_entry["glasses"] + entry.get("glasses", 1), 20)
        else:
            data["water"].append({"date": today, "glasses": entry.get("glasses", 1), "goal": 8})
        return jsonify({"success": True, "today": next((w for w in data["water"] if w.get("date") == today), {})})
    today = datetime.date.today().isoformat()
    today_entry = next((w for w in data["water"] if w.get("date") == today), {"date": today, "glasses": 0, "goal": 8})
    return jsonify({"today": today_entry, "history": data["water"][-7:]})

@app.route("/api/sleep", methods=["GET", "POST"])
def sleep():
    if "user_email" not in session:
        return jsonify({"error": "Not logged in"}), 401
    email = session["user_email"]
    data = get_user_data(email)
    if request.method == "POST":
        entry = request.json
        entry["date"] = datetime.date.today().isoformat()
        hours = entry.get("hours", 0)
        if hours >= 8:
            entry["quality"] = "Excellent 🌟"
            entry["tip"] = "Perfect sleep! You're crushing it."
        elif hours >= 7:
            entry["quality"] = "Good 😊"
            entry["tip"] = "Great job! Try to maintain this schedule."
        elif hours >= 6:
            entry["quality"] = "Fair 😐"
            entry["tip"] = "Try going to bed 30 mins earlier tonight."
        else:
            entry["quality"] = "Poor 😴"
            entry["tip"] = "You need more rest. Aim for 7-9 hours tonight."
        data["sleep"].append(entry)
        return jsonify({"success": True, "entry": entry})
    return jsonify({"sleep": data["sleep"][-14:]})

@app.route("/api/habits", methods=["GET", "POST"])
def habits():
    if "user_email" not in session:
        return jsonify({"error": "Not logged in"}), 401
    email = session["user_email"]
    data = get_user_data(email)
    today = datetime.date.today().isoformat()
    if request.method == "POST":
        entry = request.json
        today_habits = next((h for h in data["habits"] if h.get("date") == today), None)
        if not today_habits:
            today_habits = {"date": today, "completed": []}
            data["habits"].append(today_habits)
        habit = entry.get("habit")
        if habit in today_habits["completed"]:
            today_habits["completed"].remove(habit)
        else:
            today_habits["completed"].append(habit)
        return jsonify({"success": True, "completed": today_habits["completed"]})
    today_habits = next((h for h in data["habits"] if h.get("date") == today), {"date": today, "completed": []})
    return jsonify({"today": today_habits, "history": data["habits"][-7:]})

@app.route("/api/periods", methods=["GET", "POST"])
def periods():
    if "user_email" not in session:
        return jsonify({"error": "Not logged in"}), 401
    email = session["user_email"]
    user = users_db.get(email, {})
    if user.get("gender") != "female":
        return jsonify({"error": "Feature not available"}), 403
    data = get_user_data(email)
    if request.method == "POST":
        entry = request.json
        entry["logged_at"] = datetime.datetime.now().isoformat()
        data["periods"].append(entry)
        # Predict next cycle
        if len(data["periods"]) >= 1:
            last_start = datetime.datetime.strptime(entry.get("start_date", datetime.date.today().isoformat()), "%Y-%m-%d")
            next_cycle = last_start + datetime.timedelta(days=28)
            entry["next_predicted"] = next_cycle.strftime("%Y-%m-%d")
            entry["ovulation_day"] = (last_start + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
        return jsonify({"success": True, "entry": entry})
    return jsonify({"periods": data["periods"][-6:]})

@app.route("/api/chat", methods=["POST"])
def chat():
    if "user_email" not in session:
        return jsonify({"error": "Not logged in"}), 401
    email = session["user_email"]
    user = users_db.get(email, {})
    data = get_user_data(email)
    user_msg = request.json.get("message", "")
    
    bot_response = ai_chatbot_response(user_msg, user.get("name", "Friend"), user.get("gender", ""))
    
    data["chat_history"].append({
        "user": user_msg,
        "bot": bot_response,
        "time": datetime.datetime.now().strftime("%H:%M")
    })
    
    return jsonify({"response": bot_response})

@app.route("/api/dashboard_stats")
def dashboard_stats():
    if "user_email" not in session:
        return jsonify({"error": "Not logged in"}), 401
    email = session["user_email"]
    data = get_user_data(email)
    today = datetime.date.today().isoformat()
    
    today_water = next((w for w in data["water"] if w.get("date") == today), {"glasses": 0, "goal": 8})
    today_sleep = next((s for s in reversed(data["sleep"]) if s.get("date") == today), None)
    today_habits = next((h for h in data["habits"] if h.get("date") == today), {"completed": []})
    last_mood = data["moods"][-1] if data["moods"] else None
    
    return jsonify({
        "water": today_water,
        "sleep": today_sleep,
        "habits_count": len(today_habits["completed"]),
        "last_mood": last_mood,
        "total_mood_entries": len(data["moods"]),
        "streak": min(len(data["habits"]), 30)
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
