// const url = "";
const container = document.getElementById("moodButtonsContainer");
const slider = document.getElementById("customRange");
const body = document.body;
const emotionText = document.getElementById("MoodText");
const keywordContainer = document.getElementById("moodButtonsContainer");
const EmotionFactorsContainer = document.getElementById(
  "EmotionFactorsContainer"
);
const toggleButton = document.getElementById("toggle-button");

const sadKeywords = [
  "生氣",
  "焦慮",
  "害怕",
  "不堪負荷",
  "羞愧",
  "厭惡",
  "尷尬",
  "挫折",
  "不開心",
  "嫉妒",
  "壓力大",
  "擔心",
  "內疚",
  "驚訝",
  "絕望",
  "焦躁",
  "寂寞",
  "哀傷",
  "失望",
  "疲憊",
  "傷心",
];

const happyKeywords = [
  "驚奇",
  "興奮",
  "驚訝",
  "熱情",
  "快樂",
  "喜悅",
  "勇敢",
  "自豪",
  "自信",
  "充滿希望",
  "被逗樂",
  "滿意",
  "安心",
  "感恩",
  "開心",
];

const neutralKeywords = ["開心", "平靜", "平和", "漠然", "疲憊"];

const sadaddi = [...neutralKeywords, ...happyKeywords];
const happyaddi = [...sadKeywords, ...neutralKeywords];
const neutraladdi = [...sadKeywords, ...happyKeywords];

const emotionalFactors = [
  // 第一區：個人健康與心理
  { label: "健康 ❤️", value: "health" },
  { label: "運動 🏃‍♂️", value: "fitness" },
  { label: "自我照顧🛌", value: "selfCare" },
  { label: "嗜好 🎨", value: "hobby" },
  { label: "身分認同👤", value: "identity" },
  { label: "心靈 🌿", value: "mindfulness" },

  // 第二區：人際關係與社交生活
  { label: "社區 🏘️", value: "community" },
  { label: "家庭 👪", value: "family" },
  { label: "朋友 👫", value: "friends" },
  { label: "伴侶 💑", value: "partner" },
  { label: "約會 🌹", value: "dating" },

  // 第三區：日常事務與環境因素
  { label: "家務 🧺", value: "housework" },
  { label: "工作 💼", value: "work" },
  { label: "教育 📚", value: "education" },
  { label: "旅遊 🌍", value: "travel" },
  { label: "天氣 ☀️", value: "weather" },
  { label: "時事 📰", value: "news" },
  { label: "金錢 💵", value: "money" },
];

let keyword = [];
let keyword_count = 0; // 確認有選擇的關鍵字數量，用來判斷是否可以進入下一步
let emotionFactor = [];
let emotionFactor_count = 0; // 確認有選擇的情緒因子數量，用來判斷是否可以送出表單
let moodscore = 0; // 情緒分數
let userId = "no";
let alert_message = "";

let showingMore = false;
let currentKeywords = neutralKeywords; // 當前顯示的關鍵字集
let additionalKeywords = neutraladdi; // 額外顯示的關鍵字集
let previousMood = null; // 用來儲存前一次的情緒狀態

const emotions = ["非常不愉快", "不太愉快", "情緒中性", "有點愉快", "非常愉快"];
const colors = ["#6a4c93", "#1982c4", "#8ac926", "#ffca3a", "#ff595e"];

// 分界點設置為20, 40, 60, 80
const breakpoints = [0, 20, 40, 60, 80, 100];
const colorplace = [0, 30, 50, 70, 100];
slider.addEventListener("input", function () {
  changebgcolor();
  updateKeywords();
});
// 更換背景顏色
function changebgcolor() {
  const value = slider.value;
  // 根據分界點計算當前滑動條在哪一個區間
  for (let i = 0; i < breakpoints.length - 1; i++) {
    if (value >= breakpoints[i] && value < breakpoints[i + 1]) {
      moodscore = i;
      break;
    }
  }
  const percentageBetween = 
    (value - colorplace[moodscore]) / 
    (colorplace[moodscore + 1] - colorplace[moodscore]);

  // document.getElementById("test123").innerHTML = String(value) + " " + String(percentageBetween);
  const currentColor = interpolateColor(
    colors[moodscore],
    colors[moodscore + 1] || colors[moodscore],
    percentageBetween
  );

  // 更新背景顏色
  body.style.backgroundColor = currentColor;
}

function interpolateColor(color1, color2, fraction) {
  const [r1, g1, b1] = hexToRGB(color1);
  const [r2, g2, b2] = hexToRGB(color2);

  const r = Math.round(r1 + (r2 - r1) * fraction);
  const g = Math.round(g1 + (g2 - g1) * fraction);
  const b = Math.round(b1 + (b2 - b1) * fraction);

  return `rgb(${r}, ${g}, ${b}, 0.38)`;
}
function hexToRGB(hex) {
  let r = parseInt(hex.slice(1, 3), 16);
  let g = parseInt(hex.slice(3, 5), 16);
  let b = parseInt(hex.slice(5, 7), 16);
  return [r, g, b];
}

// 更新第一頁的情緒關鍵字
function updateKeywords() {
  const value = slider.value;
  let newMood; // 當前的情緒狀態

  if (value >= 60) {
    newMood = value >= 80 ? "非常愉快" : "愉快";
  } else if (value <= 40) {
    newMood = value <= 20 ? "非常不愉快" : "不愉快";
  } else {
    newMood = "情緒中性";
  }

  // 更新情緒文字
  emotionText.textContent = newMood;

  // 如果情緒狀態沒有變化，則不更新選單，此外，非常愉快/愉快互相切換、非常不愉快/不愉快互相切換也不更新選單
  if (
    newMood === previousMood ||
    (newMood === "非常愉快" && previousMood === "愉快") ||
    (newMood === "愉快" && previousMood === "非常愉快") ||
    (newMood === "非常不愉快" && previousMood === "不愉快") ||
    (newMood === "不愉快" && previousMood === "非常不愉快")
  ) {
    return; // 結束函式，不刷新選單
  }

  // 更新前一次的情緒狀態
  previousMood = newMood;

  // 清空關鍵字容器
  keywordContainer.innerHTML = "";
  toggleButton.style.display = "block"; // 顯示按鈕
  toggleButton.textContent = "▼ 顯示較多"; // 重置按鈕文本
  keyword_count = 0; // 重置關鍵字數量
  showingMore = false; // 重置顯示狀態

  // 根據情緒狀態顯示對應的關鍵字
  if (newMood === "愉快") {
    currentKeywords = happyKeywords;
    additionalKeywords = happyaddi;
  } else if (newMood === "不愉快") {
    currentKeywords = sadKeywords;
    additionalKeywords = sadaddi;
  } else {
    currentKeywords = neutralKeywords;
    additionalKeywords = neutraladdi;
  }

  showKeywords(currentKeywords); // 顯示當前關鍵字集
  showingMore = false; // 重置顯示更多狀態
  toggleButton.onclick = toggleMore;
}
// 顯示關鍵字
function showKeywords(keywords) {
  keywords.forEach((keyword) => {
    const div = document.createElement("div");
    div.classList.add("keyword");
    div.textContent = keyword;
    // div.classList.add('button');
    div.addEventListener("click", () => {
      if (div) {
        div.classList.toggle("active");
        console.log(`Element after toggle:`, div);
      } else {
        console.error(`Element with ID '${div.id}' not found.`);
      }

      // 如果關鍵字class多active，則keyword_count+1
      if (div.classList.contains("active")) {
        keyword_count++;
      } else {
        keyword_count--;
      }
      if (keyword_count > 0) {
        // 顯示id為nextstep的按鈕
        document.getElementById("nextstep").style.display = "block";
      }
      // document.getElementById("MoodTextArea").style.display = "block";
    });
    keywordContainer.appendChild(div);
  });
}
// 點擊顯示更多按鈕後顯示其他關鍵字
function toggleMore() {
  if (showingMore) {
    // 如果當前是顯示較多狀態，則收起
    keywordContainer.innerHTML = ""; // 清空容器
    showKeywords(currentKeywords); // 重新顯示當前關鍵字集
  } else {
    showKeywords(additionalKeywords); // 只顯示額外的關鍵字
    toggleButton.style.display = "none"; // 隱藏按鈕
  }
  showingMore = !showingMore; // 切換顯示狀態
}

// 顯示下一步
function nextstep() {
  if (keyword_count == 0) {
    alert("請選擇至少一個關鍵字");
    return;
  }
  // alert("已選擇" + keyword_count + "個關鍵字");
  document.getElementById("form2").style.display = "block";
  document.getElementById("form1").style.display = "none";
}
// 顯示上一步
function previousstep() {
  document.getElementById("form1").style.display = "block";
  document.getElementById("form2").style.display = "none";
}

// 初次加載時初始化關鍵字
updateKeywords();
changebgcolor();
showEmotionFactor();

// 顯示情緒因子
function showEmotionFactor() {
  emotionalFactors.forEach((factor) => {
    const div = document.createElement("div");
    div.classList.add("emotion-factor");
    div.textContent = factor.label;
    // console.log(factor.label);
    div.addEventListener("click", () => {
      div.classList.toggle("active");
    });
    EmotionFactorsContainer.appendChild(div);

    // 在每區的間隔處換行，但因排版是用grid，所以需要確認需跳過幾格
    
    if (factor.label === "心靈 🌿") {
      for (let i=0;i<2;i++){
        const emptyDiv = document.createElement("div");
        EmotionFactorsContainer.appendChild(emptyDiv);
      }
      // 添加更多空白空間
      const spacer = document.createElement("div");
      spacer.style.gridColumn = "span 4"; // 占據兩個網格單元
      spacer.style.height = "0.5rem";
      EmotionFactorsContainer.appendChild(spacer);

    } else if (factor.label === "約會 🌹") {
      for (let i=0;i<3;i++){
        const emptyDiv = document.createElement("div");
        EmotionFactorsContainer.appendChild(emptyDiv);
      }
      const spacer = document.createElement("div");
      spacer.style.gridColumn = "span 4"; // 占據兩個網格單元
      spacer.style.height = "0.5rem";
      EmotionFactorsContainer.appendChild(spacer);
      
    }
  });
}

// 掃Qrcode、去 bot get 目前的密碼，兩邊檢查是否正確
function scancode() {
  liff.scanCodeV2()
    .then(result => {
      // const resultElement = document.getElementById('result');
      // resultElement.textContent = `QR Code result: ${result.value}`;
      return result.value;
    })
    .then(scanresult => {
      fetch(url+"/check_scanres", {
        method: 'POST',
        headers: {
          "Content-Type": "application/json",
          "ngrok-skip-browser-warning": true,
        },
        body: JSON.stringify({
          "UserID": userId,
          "ScanResult": scanresult
        })
      })
      .then(res => res.text())
        .then(restext => {
            console.log("scanres:  " + scanresult + "\npassword: " + restext)
            if(restext != scanresult){
              console.log("Qrcode wrong!");
              window.close();
            }
            else{
              console.log("正確! " + scanresult);
            }
        })
    })
    .catch(error => {
      console.error('Scan failed', error);
    });
        
}

function checkfivemin(){
  fetch(url+"/check_userlast", {
    method: 'POST',
    headers: {
      "Content-Type": "application/json",
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

// 創建好要送出的表單
function flexMessage() {
  let msg;
  if(document.getElementById("Text").value != ""){
    msg = {
      //Line Flex Message
      to: userId,
      messages: [
        {
          type: "flex",
          altText: "情緒分析結果",
          contents: {
            type: "bubble",
            body: {
              type: "box",
              layout: "vertical",
              contents: [
                {
                  type: "text",
                  text: "目前圖片結果",
                  size: "xl",
                },
                {
                  type: "image",
                  url: url + "picture",
                  size: "full",
                  aspectRatio: "1792:1024",
                },
                {
                  type: "text",
                  text: "紀錄時間：" + new Date().toLocaleString(),
                },
                {
                  type: "text",
                  text: `情緒分數：${Math.floor((slider.value - 1) / 20) + 1}`,
                },
                {
                  type: "text",
                  text: `情緒關鍵詞：${keyword.join(", ")}`,
                },
                {
                  type: "text",
                  text: `情緒因子：${emotionFactor.join(", ")}`,
                },
                {
                  type: "text",
                  text: `情緒文字：${document.getElementById("Text").value}。`,
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
  }
  else{
    msg = {
      //Line Flex Message
      to: userId,
      messages: [
        {
          type: "flex",
          altText: "情緒分析結果",
          contents: {
            type: "bubble",
            body: {
              type: "box",
              layout: "vertical",
              contents: [
                {
                  type: "text",
                  text: "目前圖片結果",
                  size: "xl",
                },
                {
                  type: "image",
                  url: url + "picture",
                  size: "full",
                  aspectRatio: "1792:1024",
                },
                {
                  type: "text",
                  text: "紀錄時間：" + new Date().toLocaleString(),
                },
                {
                  type: "text",
                  text: `情緒分數：${Math.floor((slider.value - 1) / 20) + 1}`,
                },
                {
                  type: "text",
                  text: `情緒關鍵詞：${keyword.join(", ")}`,
                },
                {
                  type: "text",
                  text: `情緒因子：${emotionFactor.join(", ")}`,
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
  }
  return msg;
}

function pushMsg() {
  let randomPoints;
  if(document.getElementById("Text").value != ""){
    console.log("文字框不為空");
    randomPoints = Math.floor(Math.random() * 4) + 2; // 2~5
  }
  else {
    randomPoints = Math.floor(Math.random() * 3) + 1; // 1~3
  }
  console.log("點數：" + randomPoints);
  console.log("情緒分數：" + Math.floor((slider.value - 1) / 20) + 1);
  console.log("情緒因子：" + emotionFactor.join(", "));
  console.log("情緒關鍵詞：" + keyword.join(", "));
  console.log("情緒文字：" + document.getElementById("Text").value);
      
      const message = flexMessage();

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
        MoodVaule: Math.floor((slider.value - 1) / 20) + 1,
        MoodKeyWord: keyword.join(", "),
        MoodFactor: emotionFactor.join(", "),
        MoodWord: document.getElementById("Text").value
        // 顏色後端自己抓
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

      // fetch(url+'/moodmap',{
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify({
      //     randomPoints: randomPoints,
      //     LineID: userId,
      //   }),
      // });
}



document.addEventListener('DOMContentLoaded', function () {
  $('#submit').click(function () {  //按下確定鈕
    var keywordButtons = document.querySelectorAll(".keyword.active");
    // 抓取所有有選擇的關鍵詞，準備送出
    keyword.length = 0; // 清空 keywords
    keywordButtons.forEach(function (button) {
      keyword.push(button.textContent);
    });
    console.log("第一頁關鍵字是：" + keyword);

    var emotionFactorsButtons = document.querySelectorAll(".emotion-factor.active");
    emotionFactor.length = 0; // 清空 emotionFactor
    emotionFactorsButtons.forEach(function (button) {
      emotionFactor.push(button.textContent);
    });
    console.log("第二頁情緒因子是：" + emotionFactor);

    if(emotionFactor.length == 0){
      alert("請選擇至少一個情緒因子");
    }
    // 送出資料
    pushMsg();
  });
});

