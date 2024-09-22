import subprocess

def start_services():
    # # 啟動 ngrok
    # ngrok = subprocess.Popen(['./ngrok', 'http', '5000'])

    # 啟動 app.py
    app = subprocess.Popen(['python', 'app.py'])

    # 啟動 food.py
    wordcloud = subprocess.Popen(['python', '文字雲/another.py'])
    food = subprocess.Popen(['python', '心情地圖&生圖/food.py'])
    return app, wordcloud, food

if __name__ == "__main__":
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