import subprocess
import os
from dotenv import load_dotenv

def start_services():
    env = os.environ.copy()
    route = r'.\testenv\Scripts\python.exe'
    # # 啟動 ngrok
    # ngrok = subprocess.Popen(['./ngrok', 'http', '5000'])

    # 啟動 app.py
    app = subprocess.Popen([route, 'app.py'], env=env)

    # 啟動 food.py
    wordcloud = subprocess.Popen([route, '文字雲/another.py'], env=env)
    food = subprocess.Popen([route, '心情地圖&生圖/food.py'], env=env)
    return app, wordcloud, food

if __name__ == "__main__":
    load_dotenv()
    app, food,wordcloud = start_services()

    try:
        # 等待所有進程結束
        # ngrok.wait()
        app.wait()
        food.wait()
        wordcloud.wait()
    except KeyboardInterrupt:
        # 捕捉 Ctrl+C 事件並終止所有進程
        # ngrok.terminate()
        app.terminate()
        food.terminate()
        wordcloud.terminate()