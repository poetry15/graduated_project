// const url = "https://608a-125-231-22-218.ngrok-free.app";
const container = document.getElementById("moodButtonsContainer");
const slider = document.getElementById("customRange");
const body = document.body;
const emotionText = document.getElementById("MoodText");
const keywordContainer1 = document.getElementById("moodButtonsContainer1");
const keywordContainer2 = document.getElementById("moodButtonsContainer2");
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

const sadaddi = [...new Set([...neutralKeywords, ...happyKeywords].filter(item => item !== "疲憊"))];
const happyaddi = [...new Set([...sadKeywords, ...neutralKeywords].filter(item => item !== "開心"))];
const neutraladdi = [...new Set([...sadKeywords, ...happyKeywords].filter(item => (item !== "疲憊" && item !== "開心")))];


const emotionalFactors = [
  // 第一區：個人健康與心理
  // { label: "健康 ❤️", value: "health" },
  // { label: "運動 🏃‍♂️", value: "fitness" },
  // { label: "自我照顧 🛌", value: "selfCare" },
  // { label: "嗜好 🎨", value: "hobby" },
  // { label: "身分認同 👤", value: "identity" },
  // { label: "心靈 🌿", value: "mindfulness" },

  // 第二區：人際關係與社交生活
  { label: "家人 👪", value: "family" },
  { label: "朋友 👫", value: "friends" },
  { label: "伴侶 💑", value: "partner" },
  { label: "寵物 🐾", value: "pet" },

  // 第三區：日常事務與環境因素
  { label: "健康 🩺", value: "health" },
  { label: "飲食 🥤", value: "food" },
  { label: "家事 🧺", value: "housework" },
  { label: "工作 💼", value: "work" },
  { label: "學習 📚", value: "learn" },
  { label: "旅遊 🌍", value: "travel" },
  { label: "天氣 ☀️", value: "weather" },
  { label: "時事 📰", value: "news" },
  { label: "花費 💵", value: "money" },
];

let keyword = [];
let keyword_count = 0; // 確認有選擇的關鍵字數量，用來判斷是否可以進入下一步
let emotionFactor = [];
let emotionFactor_count = 0; // 確認有選擇的情緒因子數量，用來判斷是否可以送出表單
let moodscore = 0; // 情緒分數
let moodPlace = 0; // 情緒分數的位置
let currentColor = "#8ac926"; // 當前背景顏色
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
  if(value > 99){ // 邊界值特殊處理
    body.style.backgroundColor = "rgba(255, 89, 94, 0.38)";
    return;
  }
  // 根據 colorplace 計算當前滑動條在哪一個區間
  for (let i = 0; i < colorplace.length - 1; i++) {
    if (value >= colorplace[i] && value < colorplace[i + 1]) {
      moodPlace = i;
      break;
    }
  }

  // 計算當前值在 colorplace 區間中的百分比
  const percentageBetween =
    (value - colorplace[moodPlace]) /
    (colorplace[moodPlace + 1] - colorplace[moodPlace]);


  // document.getElementById("test123").innerHTML = String(value) + " " + String(percentageBetween) +" " + String(moodscore);
  currentColor = interpolateColor(
    colors[moodPlace],
    colors[moodPlace + 1] || colors[moodPlace],
    percentageBetween
  );
  
  // 更新背景顏色
  body.style.backgroundColor = currentColor;

  // document.getElementById("test").innerHTML = currentColor + ", " +  RGBTohex(currentColor);
}

function interpolateColor(color1, color2, fraction) {
  const [r1, g1, b1] = hexToRGB(color1);
  const [r2, g2, b2] = hexToRGB(color2);

  const r = Math.round(r1 + (r2 - r1) * fraction);
  const g = Math.round(g1 + (g2 - g1) * fraction);
  const b = Math.round(b1 + (b2 - b1) * fraction);

  return `rgba(${r}, ${g}, ${b}, 0.38)`;
}
function hexToRGB(hex) {
  let r = parseInt(hex.slice(1, 3), 16);
  let g = parseInt(hex.slice(3, 5), 16);
  let b = parseInt(hex.slice(5, 7), 16);
  return [r, g, b];
}

function RGBTohex(rgb) {
  // 使用正則表達式解析 rgba 字串，忽略透明度
  const result = rgb.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (!result) return null;

  const [_, r, g, b] = result;

  return `#${parseInt(r).toString(16).padStart(2, "0")}${parseInt(g).toString(16).padStart(2, "0")}${parseInt(b).toString(16).padStart(2, "0")}`;
}

// 更新第一頁的情緒關鍵字
function updateKeywords() {
  const value = slider.value;
  let newMood; // 當前的情緒狀態

  if (value >= 60) {
    newMood = value >= 80 ? "非常愉快" : "愉快";
    moodscore = newMood === "非常愉快" ? 5 : 4;
  } else if (value <= 40) {
    newMood = value <= 20 ? "非常不愉快" : "不愉快";
    moodscore = newMood === "非常不愉快" ? 1 : 2;
  } else {
    newMood = "情緒中性";
    moodscore = 3;
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
    console.log("情緒狀態沒有變化，不刷新選單" + newMood + " " + previousMood);
    return; // 結束函式，不刷新選單
  }

  // 更新前一次的情緒狀態
  previousMood = newMood;

  // 清空關鍵字容器
  keywordContainer1.innerHTML = keywordContainer2.innerHTML = "";
  toggleButton.style.display = "block"; // 顯示按鈕
  toggleButton.textContent = "▼ 顯示較多"; // 重置按鈕文本
  keyword_count = 0; // 重置關鍵字數量
  showingMore = false; // 重置顯示狀態

  // 根據情緒狀態顯示對應的關鍵字
  if (newMood === "愉快" || newMood === "非常愉快") {
    currentKeywords = happyKeywords;
    additionalKeywords = happyaddi;
  } else if (newMood === "不愉快" || newMood === "非常不愉快") {
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
function showKeywords() {
  currentKeywords.forEach((keyword) => {
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
    keywordContainer1.appendChild(div);
  });

  additionalKeywords.forEach((keyword) => {
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
    keywordContainer2.appendChild(div);
  });
}

// 點擊顯示更多按鈕後顯示其他關鍵字
function toggleMore() {
  if (!showingMore) {
    // 如果當前是顯示較多狀態，則收起
    document.getElementById("moodButtonsContainer2").style.display = "grid";
    document.getElementById("toggle-button").innerHTML = "▲ 顯示較少";

  }
  else {
    // 如果當前是收起狀態，則顯示較多
    document.getElementById("moodButtonsContainer2").style.display = "none";
    document.getElementById("toggle-button").innerHTML = "▼ 顯示較多";
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
      if (div.classList.contains("active")) {
        emotionFactor_count++;
      } else {
        emotionFactor_count--;
      }
    });
    EmotionFactorsContainer.appendChild(div);

    // 在每區的間隔處換行，但因排版是用grid，所以需要確認需跳過幾格

    if (factor.label === "寵物 🐾") {
      const spacer = document.createElement("div");
      spacer.style.gridColumn = "span 4";
      spacer.style.height = "0.5rem";
      EmotionFactorsContainer.appendChild(spacer);

    }
  });
}

// 掃Qrcode、去 bot get 目前的密碼，兩邊檢查是否正確
function scancode() {
  Swal.fire({
    title: '接下來請掃描QRcode',
    text: '讓我知道你在現場!',
    icon: "info",
    allowOutsideClick: false, // 防止用戶點擊外部關閉
    showDenyButton: true,
    denyButtonText: "不同意",
    confirmButtonText: "同意",
  })
    .then(result => {
      if (result.isDenied)
        liff.closeWindow();
    })
    .then(() => liff.scanCodeV2())
    .then(result => {
      // const resultElement = document.getElementById('result');
      // resultElement.textContent = `QR Code result: ${result.value}`;
      return result.value;
    })
    .then(scanresult => {
      fetch(url + "/check_scanres", {
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
          // alert("restext" + restext);
          // console.log("scanres:  " + scanresult + "\npassword: " + restext)
          if (restext != "ok") {
            console.log("Qrcode wrong!");
            if (liff.isInClient()) {
              liff.closeWindow(); // 關閉LIFF

            }
            else {
              window.close(); // 關閉瀏覽器
            }
          }
          else {
            console.log("正確! " + scanresult);
          }
        })
    })
    .catch(error => {
      console.error('Scan failed', error);
    });

}

function getNextHour() {
  let date = new Date();
  date = date.getHours() + 1;
  if (date >= 24) date -= 24;
  return date;
}

// 創建好要送出的表單
function flexMessage(randomPoints, emotionFactor_without_emoji) {
  let msg;
  let boxcontext = [{
    type: "text",
    text: "情緒喵帶來心情小記後出門啦~",
    size: "lg",
  },
  {
    type: "text",
    text: "紀錄時間：" + new Date().toLocaleString(),
  },
  {
    type: "text",
    text: `情緒分數：` + moodscore,
  },
  {
    type: 'text',
    text: `獲得創作積分：${randomPoints}`,
    size: 'xl',
  },
  {
    "type": "button",
    "action": {
      "type": "uri",
      "label": `請於${getNextHour()}點前點此前往創作`,
      "uri": "https://liff.line.me/2004371526-QNE54xpZ"
    },
  },
    // {
    //   type: "text",
    //   text: `情緒關鍵詞：${keyword.join(", ")}`,
    //   "wrap": true,
    // },
  ];

  // if (emotionFactor_count == 0) { // 只輸入情緒文字
  //   boxcontext.push(
  //     {
  //       type: "text",
  //       text: `情緒文字：${document.getElementById("Text").value}。`,
  //       "wrap": true,
  //     },
  //     {
  //       type: 'text',
  //       text: `你所擲出的點數為${randomPoints}`,
  //       size: 'xl',
  //     },
  //     {
  //       "type": "button",
  //       "action": {
  //         "type": "uri",
  //         "label": "前往心情地圖開始創作吧!",
  //         "uri": "https://liff.line.me/2004371526-QNE54xpZ"
  //       },
  //     }
  //   );
  // }
  // else if (document.getElementById("Text").value == "") { // 只輸入情緒因子
  //   boxcontext.push(
  //     {
  //       type: "text",
  //       text: `情緒因子：${emotionFactor_without_emoji.join(", ")}`,
  //       "wrap": true,
  //     },
  //     {
  //       type: 'text',
  //       text: `你所擲出的點數為${randomPoints}`,
  //       size: 'xl',
  //     },
  //     {
  //       "type": "button",
  //       "action": {
  //         "type": "uri",
  //         "label": "前往心情地圖開始創作吧!",
  //         "uri": "https://liff.line.me/2004371526-QNE54xpZ"
  //       },
  //     }
  //   );
  // }
  // else { // 全部都有
  //   boxcontext.push(
  //     {
  //       type: "text",
  //       text: `情緒文字：${document.getElementById("Text").value}。`,
  //       "wrap": true,
  //     },
  //     {
  //       type: "text",
  //       text: `情緒因子：${emotionFactor_without_emoji.join(", ")}`,
  //       "wrap": true,
  //     },
  //     {
  //       type: 'text',
  //       text: `你所擲出的點數為${randomPoints}`,
  //       size: 'xl',
  //     },
  //     {
  //       "type": "button",
  //       "action": {
  //         "type": "uri",
  //         "label": "前往心情地圖開始創作吧!",
  //         "uri": "https://liff.line.me/2004371526-QNE54xpZ"
  //       },
  //     });
  // }
  msg = {
    //Line Flex Message
    to: userId,
    messages: [
      {
        type: "flex",
        altText: "心情小記",
        contents: {
          type: "bubble",
          body: {
            type: "box",
            layout: "vertical",
            contents: boxcontext
          }
        }
      }]
  };
  return msg;
}

function getformData(emotionFactor_without_emoji) {
  const date = new Date(); // 當前時間
  let data = {
    Time: date.toLocaleString('zh-TW', { timeZone: 'Asia/Taipei' }),
    TimeStamp: Math.floor(date.getTime() / 1000),
    LineID: userId,
    MoodVaule: moodscore,
    MoodColor: RGBTohex(currentColor),
    MoodKeyWord: keyword.join(", "),
  };

  if (document.getElementById("Text").value == "") { // 只輸入情緒因子
    data = {
      ...data,
      MoodFactor: emotionFactor_without_emoji.join(", "),
    }
  }
  else if (emotionFactor_count == 0) { // 只輸入情緒文字
    data = {
      ...data,
      MoodWord: document.getElementById("Text").value,
    }
  }
  else { // 全部都有
    data = {
      ...data,
      MoodFactor: emotionFactor_without_emoji.join(", "),
      MoodWord: document.getElementById("Text").value,
    }
  }
  return data;
}

function pushMsg() {
  let randomPoints;
  if (document.getElementById("Text").value == "" && emotionFactor_count == 0) {
    alert("請至少選擇一個情緒因子或輸入情緒文字!");
    return;
  }
  else if (document.getElementById("Text").value == "" || emotionFactor_count == 0) {
    console.log("其中一個為空");
    randomPoints = Math.floor(Math.random() * 3) + 2; // 2~4
  }
  else {
    randomPoints = Math.floor(Math.random() * 4) + 3; // 3~6
  }

  let emotionFactor_without_emoji = [];
  emotionFactor.forEach((factor) => {
    emotionFactor_without_emoji.push(factor.split(" ")[0]);
  });

  console.log("點數：" + randomPoints);
  console.log("情緒分數：" + moodscore);
  console.log("情緒因子：" + emotionFactor_without_emoji.join(", "));
  console.log("情緒關鍵詞：" + keyword.join(", "));
  console.log("情緒文字：" + document.getElementById("Text").value);

  const message = flexMessage(randomPoints, emotionFactor_without_emoji);
  console.log(message);

  const formData = getformData(emotionFactor_without_emoji);
  Swal.fire({
    title: '骰出你的創作點數！',
    html: `
      <div class="slideshow-container">
        <img id="slideshowImage" style="height:50px" class="slideshow-image" src="static/dice1.png" />
      </div>
      <p id="showpoint" style="font-size: large"> </p>
    `,
    allowOutsideClick: false,
    showConfirmButton: false,
    didOpen: () => {
      // 獲取圖片元素
      const imgElement = document.getElementById('slideshowImage');
      const showpoint = document.getElementById('showpoint');
      const maxLoops = 12 + randomPoints - 1;
      let currentIndex = 0;
      let loopCount = 0;
      // let spmessage = `恭喜獲得 ${randomPoints} 點共創點數！`;
      const interval = setInterval(() => {
        currentIndex = (currentIndex + 1) % 6; // 輪流顯示圖片
        imgElement.src = `static/dice${currentIndex + 1}.png`; // 更新圖片
        if (++loopCount >= maxLoops) {
          // 停止輪播並顯示最終圖片
          clearInterval(interval);
          // setTimeout(() => {
          showpoint.innerHTML = `恭喜獲得 ${randomPoints} 點共創點數！`;
          // },2000);
          setTimeout(() => {
            Swal.fire({
              title: '情緒轉換中...',
              text: '請稍候',
              allowOutsideClick: false, // 防止用戶點擊外部關閉
              didOpen: () => {
                Swal.showLoading(); // 顯示內建的 loading 動畫
              }
            })
          }, 2000)
        }
      }, 200);
    },
  }).then(() => {
    fetch(url + '/moodmap', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        randomPoints: randomPoints,
        LineID: userId,
        MoodValue: moodscore,
      }),
    }).then(response => response.json())
    .then(data => {
      fetch(url + '/send-message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({message,"MoodValue": moodscore,"MoodColor": RGBTohex(currentColor),"round_ID": data.round_ID}),
      })
      .then(response => {
        console.log("成功傳送", response);
      })
    })

    fetch(url + '/api', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    })
    .then(() => {
      Swal.fire({
        icon: 'success',
        title: '轉換完成',
        allowOutsideClick: false,
        confirmButtonText: "前往心情地圖創作"
      })
        .then(result => {
          if (result.isConfirmed) { // 直接導向心情地圖
            // liff.closeWindow();
            liff.openWindow({
              url: 'https://liff.line.me/2004371526-QNE54xpZ',
              external: false
            });
          }
        });
    })
    .catch(error => {
      // 任何階段的錯誤處理
      Swal.fire({
        icon: 'error',
        title: '錯誤',
        text: '請求處理過程中發生錯誤，請稍後再試！'
      });
      console.error('There has been a problem with your fetch operation:', error);
    });
  })
      // .then(() => {
      // const formuri = `https://docs.google.com/forms/d/e/1FAIpQLSchzPdn89h3EMD0wOopOoX5OI-09vcsQ3rZ2WF4FH-77TXIQA/viewform?usp=pp_url&entry.1311539326=${userId}`
      // let msg = {
      //   to: userId, // 接收者的 User ID
      //   messages: [
      //     {
      //       type: "flex", // 訊息類型為 Flex Message
      //       altText: "開啟前測表單", // 當 Flex Message 無法顯示時的替代文字
      //       contents: {
      //         type: "bubble", // Bubble 容器
      //         body: {
      //           type: "box", // 使用 box 容器
      //           layout: "vertical", // 垂直排列內容
      //           contents: [
      //             {
      //               type: "button", // 按鈕元件
      //               action: {
      //                 type: "uri", // 按鈕動作類型為 URI
      //                 label: "開啟前測表單", // 按鈕顯示的文字
      //                 uri: formuri, // 點擊按鈕後打開的網址
      //               },
      //               style: "primary", // 按鈕樣式為主要（藍色）
      //             },
      //           ],
      //         },
      //       },
      //     },
      //   ],
      // };

      //   return fetch(url + '/send-message'), {
      //     method: 'POST',
      //     headers: {
      //       'Content-Type': 'application/json'
      //     },
      //     body: JSON.stringify(message)
      //   };
      // })
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

    // 送出資料
    pushMsg();
  });
});

