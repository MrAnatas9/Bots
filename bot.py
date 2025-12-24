#!/usr/bin/env python3
"""
PONY TOWN БОТ ДЛЯ RENDER.COM
Автономный бот, работает 24/7 бесплатно
"""

import time
import random
import threading
from datetime import datetime
from flask import Flask, render_template_string
import requests
import json

app = Flask(__name__)

# =========== НАСТРОЙКИ ===========
MESSAGES = [
    "Напишите в Telegram @MrAnatas для вступления в клан",
    "Ищем активных игроков! Пишите @MrAnatas",
    "Присоединяйтесь к нашему комьюнити! @MrAnatas",
    "Ищем игроков в дружный клан! @MrAnatas"
]

DELAY_MIN = 120    # 2 минуты между сообщениями
DELAY_MAX = 300    # 5 минут между сообщениями
BOT_NAME = "КланРекрутер"  # Имя бота в игре
# =================================

# Логи работы
logs = []
message_count = 0
is_running = True

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🤖 Pony Town Bot</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            background: #0a0a0a; 
            color: #00ff00; 
            font-family: 'Courier New', monospace;
            padding: 20px;
            line-height: 1.6;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .header { 
            border-bottom: 2px solid #00ff00; 
            padding: 20px 0; 
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .status { 
            background: #111; 
            padding: 15px; 
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #00ff00;
        }
        .status.online { border-left-color: #00ff00; }
        .status.offline { border-left-color: #ff0000; }
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
        .log-time { color: #888; }
        .log-message { color: #00ff00; }
        .controls { margin: 20px 0; }
        button { 
            background: #00ff00; 
            color: #000; 
            border: none; 
            padding: 10px 20px; 
            margin-right: 10px;
            border-radius: 3px;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover { background: #00cc00; }
        .stats { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
        .stat-label { color: #888; font-size: 0.9em; }
        @media (max-width: 600px) {
            body { padding: 10px; }
            .header h1 { font-size: 1.8em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 PONY TOWN BOT</h1>
            <p>Автономный бот для рекламы клана</p>
        </div>
        
        <div class="status {% if running %}online{% else %}offline{% endif %}">
            <h3>📊 Статус системы</h3>
            <p>Состояние: <strong>{% if running %}✅ РАБОТАЕТ{% else %}⛔ ОСТАНОВЛЕН{% endif %}</strong></p>
            <p>Сообщения отправляются каждые {{ min_delay // 60 }}-{{ max_delay // 60 }} минут</p>
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
            <div class="stat-box">
                <div class="stat-value">{{ min_delay // 60 }}-{{ max_delay // 60 }} мин</div>
                <div class="stat-label">Интервал</div>
            </div>
        </div>
        
        <div class="controls">
            <form action="/start" method="post" style="display: inline;">
                <button type="submit">▶️ Запустить бота</button>
            </form>
            <form action="/stop" method="post" style="display: inline;">
                <button type="submit">⏹️ Остановить бота</button>
            </form>
            <form action="/send-now" method="post" style="display: inline;">
                <button type="submit">📨 Отправить сейчас</button>
            </form>
        </div>
        
        <div class="logs">
            <h3>📝 Логи работы (последние 50):</h3>
            {% for log in recent_logs %}
            <div class="log-entry">
                <span class="log-time">[{{ log.time }}]</span>
                <span class="log-message"> {{ log.message }}</span>
            </div>
            {% endfor %}
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <h4>📋 Сообщения:</h4>
                <ul style="text-align: left; margin-top: 10px;">
                    {% for msg in messages %}
                    <li style="margin: 5px 0; font-size: 0.9em;">{{ msg }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>
    
    <script>
        // Автообновление логов каждые 30 секунд
        setInterval(() => {
            window.location.reload();
        }, 30000);
        
        // Прокрутка логов вниз
        window.onload = function() {
            const logsDiv = document.querySelector('.logs');
            logsDiv.scrollTop = logsDiv.scrollHeight;
        };
    </script>
</body>
</html>
"""

def add_log(message):
    """Добавить запись в логи"""
    global logs
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {"time": timestamp, "message": message}
    logs.append(log_entry)
    
    # Ограничиваем количество логов
    if len(logs) > 100:
        logs = logs[-100:]
    
    # Выводим в консоль Render
    print(f"[{timestamp}] {message}")

def send_message():
    """Отправить сообщение (заглушка для реальной отправки)"""
    global message_count
    try:
        msg = random.choice(MESSAGES)
        message_count += 1
        
        # ЗДЕСЬ БУДЕТ РЕАЛЬНЫЙ КОД ОТПРАВКИ В PONY TOWN
        # Например, через WebSocket или API
        
        add_log(f"📨 Сообщение {message_count}: {msg}")
        
        # В реальном боте здесь будет:
        # 1. Подключение к WebSocket Pony Town
        # 2. Отправка сообщения
        # 3. Закрытие соединения
        
        return True
        
    except Exception as e:
        add_log(f"❌ Ошибка: {e}")
        return False

def bot_worker():
    """Рабочий поток бота"""
    global is_running
    
    add_log("🚀 Бот запущен!")
    add_log(f"📝 Сообщения: {len(MESSAGES)} вариантов")
    add_log(f"⏱️ Интервал: {DELAY_MIN//60}-{DELAY_MAX//60} минут")
    
    while is_running:
        try:
            if send_message():
                # Ждем перед следующим сообщением
                wait_time = random.randint(DELAY_MIN, DELAY_MAX)
                minutes = wait_time // 60
                seconds = wait_time % 60
                
                add_log(f"⏳ Следующее через {minutes}:{seconds:02d}")
                
                # Отсчет с возможностью прерывания
                for i in range(wait_time):
                    if not is_running:
                        break
                    time.sleep(1)
                    
        except Exception as e:
            add_log(f"⚠️ Ошибка в цикле: {e}")
            time.sleep(10)

# Маршруты Flask
@app.route('/')
def index():
    """Главная страница"""
    uptime = time.time() - start_time
    uptime_hours = int(uptime // 3600)
    
    return render_template_string(HTML_TEMPLATE,
        running=is_running,
        total_messages=message_count,
        uptime_hours=uptime_hours,
        min_delay=DELAY_MIN,
        max_delay=DELAY_MAX,
        recent_logs=logs[-50:][::-1],  # Последние 50, новые сверху
        messages=MESSAGES
    )

@app.route('/start', methods=['POST'])
def start_bot():
    """Запустить бота"""
    global is_running, bot_thread
    
    if not is_running:
        is_running = True
        bot_thread = threading.Thread(target=bot_worker, daemon=True)
        bot_thread.start()
        add_log("▶️ Бот запущен вручную")
    
    return '''
    <script>
        alert("Бот запущен!");
        window.location.href = "/";
    </script>
    '''

@app.route('/stop', methods=['POST'])
def stop_bot():
    """Остановить бота"""
    global is_running
    is_running = False
    add_log("⏹️ Бот остановлен вручную")
    
    return '''
    <script>
        alert("Бот остановлен!");
        window.location.href = "/";
    </script>
    '''

@app.route('/send-now', methods=['POST'])
def send_now():
    """Отправить сообщение сейчас"""
    if send_message():
        return '''
        <script>
            alert("Сообщение отправлено!");
            window.location.href = "/";
        </script>
        '''
    
    return '''
    <script>
        alert("Ошибка отправки!");
        window.location.href = "/";
    </script>
    '''

@app.route('/status')
def status():
    """JSON статус для проверки работы"""
    return {
        "status": "running" if is_running else "stopped",
        "messages_sent": message_count,
        "bot_name": BOT_NAME,
        "service": "pony-town-bot"
    }

# Точка входа
if __name__ == "__main__":
    start_time = time.time()
    
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=bot_worker, daemon=True)
    bot_thread.start()
    
    add_log("🌐 Веб-интерфейс запущен")
    add_log("🤖 Бот запускается...")
    
    # Запускаем Flask
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
