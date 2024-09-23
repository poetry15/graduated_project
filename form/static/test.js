var color = ["rgb(254, 233, 254)","rgb(236, 213, 252)", "rgb(233, 206, 253)", "rgb(209, 214, 255)", "rgb(205, 242, 255)"]; // 冷色：寒冷冷靜放鬆，紫色：中性色，暖色：愉悅陽光熱情
var keyword = [];
var userId = 'no';
var alert_message = '';

function change(){ // 拖拉條文字顯示
  let rangeValue = document.getElementById("customRange");
  let MoodText = document.getElementById("MoodText");
  switch (rangeValue.value) { // 非常愉快、愉快 、、情緒中性 7等級
    case "1":
      MoodText.innerHTML = "非常不開心";
      break;
    case "2":
      MoodText.innerHTML = "不太開心";
      break;
    case "3":
      MoodText.innerHTML = "情緒中性";
      break;
    case "4":
      MoodText.innerHTML = "開心";
      break;
    case "5":
      MoodText.innerHTML = "非常開心";
      break;
    default:
      MoodText.innerHTML = "Error";
  }
  document.body.style.background = color[parseInt(rangeValue.value)-1];
}

function clickButton(name){
  let but = document.getElementById(name);
  if (but) {
    but.classList.toggle('active');
    console.log(`Element after toggle:`, but);
  } else {
    console.error(`Element with ID '${name}' not found.`);
  }
}

// 掃Qrcode、去 bot get 目前的密碼，兩邊檢查是否正確
function scancode() {
  liff.scanCodeV2()
    .then(result => {
      const resultElement = document.getElementById('result');
      resultElement.textContent = `QR Code result: ${result.value}`;
      return result.value;
    })
    .then(scanresult => {
      fetch(url+"/check_scanres", {
        method: 'POST',
        headers: {
          "ngrok-skip-browser-warning": true,
        },
        body: JSON.stringify({
          "UserID": userId,
          "ScanResult": scanresult
        })
      })
      .then(res => res.text())
        // .then(restext => {
            // console.log("scanres:  " + scanresult + "\npassword: " + restext)
            // if(restext != scanresult){
            //   console.log("Qrcode wrong!");
            //   liff
            //     .sendMessages([
            //       {
            //         type: "text",
            //         text: "Qrcode錯誤，請再試一次!",
            //       },
            //     ])
            //     .then(() =>  {
            //       alert("send complete");
            //       liff.closeWindow();
            //     })
            //     .catch((error) => alert("send failed" + error))
              
            // }
            // else{
            //   console.log("正確! " + scanresult);
            // }
        // })
    })
    .catch(error => {
      console.error('Scan failed', error);
    });
        
}

function checkfivemin(){
  fetch(url+"/check_userlast", {
    method: 'POST',
    headers: {
      "ngrok-skip-browser-warning": true,
    }, 
    body: JSON.stringify({
      "LINEID": userId
    })
  })
  .then(res => res.text())
  .then(req => {
    if( req == 'reject' ){ // 有找到 300 秒內輸入過
      alert("我知道你有很多想說的話! 但距離上次來抒發情緒才剛過沒多久，請間隔一段時間再來");
      liff.closeWindow();
    }
    else {
      console.log("checkfivemin no problem");
    }
  })
}

function pushMsg(mscore, mkeyword, mtext) {
  if (mscore == '' || mkeyword == '' || mtext == '') {  //資料檢查
    alert('每個項目都必須輸入！');
    return;
  }
  else if(mtext.length < 10){
    alert('文字太短啦，請努力多敘述一些現在心中的想法!');
    return;
  }
  const randomPoints = Math.floor(Math.random() * 6) + 1;
				const message = { //Line Flex Message
					to: userId,
					messages: [{
						type: 'flex',
						altText: '情緒分析結果',
						contents: {
							type: 'bubble',
							body: {
								type: 'box',
								layout: 'vertical',
								contents: [
									{
										type: 'text',
										text: '目前圖片結果',	
										size: 'xl',
									},
									{
										type: "image",
										url: url+"/picture",
										size: "full",
										aspectRatio: "1792:1024",
									},
									{
										type: 'text',
										text: '紀錄時間：'+new Date().toLocaleString(),
									},
									{
										type: 'text',
										text: `情緒分數：${mscore}`,
									},
									{
										type: 'text',
										text: `情緒關鍵詞：${mkeyword}`,
									},
									{
										type: 'text',
										text: `情緒文字：${mtext}。`,
									},
									{
										type: 'text',
										text: `你所擲出的點數為${randomPoints}`,
										size: 'xl',
									},
									{
										"type": "button",
										"action": {
											"type": "uri",
											"label": "前往心情地圖察看結果",
											"uri": "https://liff.line.me/2004371526-QNE54xpZ"
										},
									}
								]
							}
						}
					}]
				};

				fetch(url+'/send-message', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify(message),
			})
			.then(response => {
					console.log('訊息發送成功:', response.data);
			})
			.catch(error => {
					console.error('訊息發送失敗:', error.response ? error.response.data : error.message);
			});
      const date = new Date(); // 當前時間
      const timestampInSeconds = Math.floor(date.getTime() / 1000);
      const formData = {
        Time: date.toLocaleString(),
	      TimeStamp: timestampInSeconds,
        LineID: userId,
        MoodVaule: mscore,
        MoodKeyWord: mkeyword,
        MoodWord: mtext,
      };

      fetch(url + '/api', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        console.log(data);
        liff.closeWindow();
      })
      .catch(error => {
        console.error('There has been a problem with your fetch operation:', error);
      });

      fetch(url+'/moodmap',{
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          randomPoints: randomPoints,
          LineID: userId,
        }),
      });
}



document.addEventListener('DOMContentLoaded', function () {
  $('#submit').click(function (e) {  //按下確定鈕
    console.log("click submit button");
    var buttons = document.querySelectorAll('.button.active');
    // 抓取所有有選擇的關鍵詞，準備送出
    var buttonText;
    keyword.length = 0; // 清空 keywords
    buttons.forEach(function(button) {
      buttonText = button.textContent;
      keyword.push(buttonText);
    });
    console.log("關鍵字是：" + keyword);
    pushMsg(parseInt($('#customRange').val()), keyword, $('#Text').val());
  });
});

