#!/usr/bin/env python3
"""
PONY TOWN БОТ ДЛЯ RENDER.COM
Автономный бот, работает 24/7 бесплатно
"""

import time
import random
import threading
import os
from datetime import datetime
from flask import Flask, render_template_string

app = Flask(__name__)

# =========== НАСТРОЙКИ ===========
MESSAGES = [
    "Напишите в Telegram @MrAnatas для вступления в клан",
    "Ищем активных игроков! Пишите @MrAnatas",
    "Присоединяйтесь к нашему комьюнити! @MrAnatas"
]

DELAY_MIN = 120    # 2 минуты между сообщениями
DELAY_MAX = 300    # 5 минут между сообщениями
# =================================

logs = []
message_count = 0
is_running = True
start_time = time.time()

def add_log(message):
    """Добавить запись в логи"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {"time": timestamp, "message": message}
    logs.append(log_entry)
    
    if len(logs) > 100:
        logs = logs[-100:]
    
    print(f"[{timestamp}] {message}")

def send_message():
    """Отправить сообщение"""
    global message_count
    try:
        msg = random.choice(MESSAGES)
        message_count += 1
        
        # ЗДЕСЬ БУДЕТ КОД ОТПРАВКИ В PONY TOWN
        add_log(f"📨 Сообщение {message_count}: {msg}")
        
        return True
        
    except Exception as e:
        add_log(f"❌ Ошибка: {e}")
        return False

def bot_worker():
    """Рабочий поток бота"""
    global is_running
    
    add_log("🚀 Бот запущен!")
    
    while is_running:
        try:
            if send_message():
                wait_time = random.randint(DELAY_MIN, DELAY_MAX)
                minutes = wait_time // 60
                seconds = wait_time % 60
                
                add_log(f"⏳ Следующее через {minutes}:{seconds:02d}")
                
                for i in range(wait_time):
                    if not is_running:
                        break
                    time.sleep(1)
                    
        except Exception as e:
            add_log(f"⚠️ Ошибка: {e}")
            time.sleep(10)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🤖 Pony Town Bot</title>
    <style>
        body { background: black; color: lime; font-family: monospace; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { border-bottom: 2px solid lime; padding: 20px 0; text-align: center; }
        .status { background: #111; padding: 15px; margin: 20px 0; border-left: 4px solid lime; }
        .logs { background: #111; padding: 15px; max-height: 400px; overflow-y: auto; }
        .log-entry { padding: 8px 0; border-bottom: 1px solid #222; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 PONY TOWN BOT</h1>
            <p>Автономный бот для рекламы клана</p>
        </div>
        
        <div class="status">
            <h3>📊 Статус</h3>
            <p>Состояние: <strong>{% if running %}✅ РАБОТАЕТ{% else %}⛔ ОСТАНОВЛЕН{% endif %}</strong></p>
            <p>Сообщений отправлено: {{ total_messages }}</p>
            <p>Время работы: {{ uptime_hours }} часов</p>
        </div>
        
        <div class="logs">
            <h3>📝 Логи:</h3>
            {% for log in recent_logs %}
            <div class="log-entry">[{{ log.time }}] {{ log.message }}</div>
            {% endfor %}
        </div>
    </div>
    
    <script>
        // Автообновление
        setInterval(() => { window.location.reload(); }, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    uptime = time.time() - start_time
    uptime_hours = int(uptime // 3600)
    
    return render_template_string(HTML_TEMPLATE,
        running=is_running,
        total_messages=message_count,
        uptime_hours=uptime_hours,
        recent_logs=logs[-20:][::-1]
    )

@app.route('/status')
def status():
    return {"status": "running", "messages": message_count}

if __name__ == "__main__":
    # Запускаем бота
    bot_thread = threading.Thread(target=bot_worker, daemon=True)
    bot_thread.start()
    
    add_log("🌐 Веб-интерфейс запущен")
    
    # Запускаем Flask
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
