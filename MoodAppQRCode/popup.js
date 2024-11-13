// 全局變數定義
let ngrok_url;
let refresh_sec = 0; // 添加這個變數定義
// 修改圖片插入的位置
const qrcodeImg = document.createElement('img');
qrcodeImg.width = 200;
document.getElementById('qrcode-container').appendChild(qrcodeImg);

function gen_password(length) {
    const cha_set = '012qrstNOPQ789ablR34uvwJKLM56xyzABCDEFcdefghnopSTUVWijkGHImXYZ';
    let pw = '';
    for(let i = 0; i < length; i++) {
        let index = Math.floor(Math.random() * cha_set.length);
        pw += cha_set[index];
    }
    console.log("pw is: " + pw);
    return pw;
}

function updateQRCode() {
    if(refresh_sec <= 0) {
        refresh_sec = 20;
        console.log("倒數完成，刷新密碼");
        
        const pw = "https://line.me/R/ti/p/@084xgtuv?text=" + gen_password(10);
        const URL = "https://quickchart.io/qr?text=" + pw + "&size=25";
        qrcodeImg.src = URL;
        
        console.log("刷新結果: " + pw + "\n完整url: " + URL);
        
        if (ngrok_url) {
            fetch(ngrok_url + "/qrcode/genpassword", {
                method: 'POST',
                headers: {
                    'content-type': 'application/json',
                    "ngrok-skip-browser-warning": true,
                },
                body: JSON.stringify({
                    "password": pw
                })
            })
            .catch(e => console.log('error' + e));
        }
    }
    refresh_sec--;
    // console.log("倒數：", refresh_sec); // 添加倒數日誌
}

// 獲取 ngrok_url 並開始更新
chrome.runtime.sendMessage({type: "GET_NGROK_URL"}, function(response) {
    ngrok_url = response.url;
    updateQRCode(); // 立即執行一次
    setInterval(updateQRCode, 1000);
});