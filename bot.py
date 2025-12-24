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

# Глобальные переменные
logs = []
message_count = 0
is_running = True
start_time = time.time()

def add_log(message):
    """Добавить запись в логи"""
    global logs
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
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            background: #0a0a0a; 
            color: #00ff00; 
            font-family: 'Courier New', monospace;
            padding: 20px;
            margin: 0;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
        }
        .header { 
            border-bottom: 2px solid #00ff00; 
            padding: 20px 0; 
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 { 
            font-size: 2.5em; 
            margin: 0 0 10px 0;
            color: #00ff00;
        }
        .status { 
            background: #111; 
            padding: 15px; 
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #00ff00;
        }
        .logs { 
            background: #111; 
            padding: 15px; 
            border-radius: 5px;
            margin: 20px 0;
            max-height: 400px;
            overflow-y: auto;
        }
        .log-entry { 
            padding: 8px 0; 
            border-bottom: 1px solid #222;
            font-size: 0.9em;
        }
        .log-time { 
            color: #888; 
            margin-right: 10px;
        }
        .log-message { 
            color: #00ff00; 
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin: 20px 0;
        }
        .stat-box {
            background: #111;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #00ff00;
        }
        .stat-label {
            color: #888;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 PONY TOWN BOT</h1>
            <p>Автономный бот для рекламы клана</p>
        </div>
        
        <div class="status">
            <h3>📊 Статус системы</h3>
            <p>Состояние: <strong style="color: #00ff00;">✅ РАБОТАЕТ</strong></p>
            <p>Сообщения отправляются каждые """ + str(DELAY_MIN//60) + """-""" + str(DELAY_MAX//60) + """ минут</p>
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-value">{{ total_messages }}</div>
                <div class="stat-label">Всего сообщений</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{{ uptime_hours }}ч</div>
                <div class="stat-label">Время работы</div>
            </div>
        </div>
        
        <div class="logs">
            <h3>📝 Логи работы:</h3>
            {% for log in recent_logs %}
            <div class="log-entry">
                <span class="log-time">[{{ log.time }}]</span>
                <span class="log-message">{{ log.message }}</span>
            </div>
            {% endfor %}
        </div>
        
        <div class="status">
            <h4>📋 Активные сообщения:</h4>
            <ul>
                {% for msg in messages %}
                <li>{{ msg }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>
    
    <script>
        // Автообновление каждые 30 секунд
        setInterval(function() {
            window.location.reload();
        }, 30000);
        
        // Прокрутка логов вниз
        window.onload = function() {
            var logsDiv = document.querySelector('.logs');
            logsDiv.scrollTop = logsDiv.scrollHeight;
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Главная страница"""
    uptime = time.time() - start_time
    uptime_hours = int(uptime // 3600)
    
    recent_logs = logs[-20:]  # Последние 20 логов
    recent_logs.reverse()     # Новые сверху
    
    return render_template_string(HTML_TEMPLATE,
        total_messages=message_count,
        uptime_hours=uptime_hours,
        recent_logs=recent_logs,
        messages=MESSAGES
    )

@app.route('/status')
def status():
    """JSON статус для проверки работы"""
    return {
        "status": "running",
        "messages_sent": message_count,
        "service": "pony-town-bot"
    }

# Запускаем бота в отдельном потоке
bot_thread = threading.Thread(target=bot_worker, daemon=True)
bot_thread.start()

add_log("🚀 Бот запускается...")
add_log("🌐 Веб-интерфейс запущен")

if __name__ == "__main__":
    # Запускаем Flask
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
