const desert_list = [ // 巧克力蛋糕、雞胸肉、牛奶、藍莓
  "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQxT3O5XJ7fHxBXzckT4uiiHd0We26bHDU96usJVXCbddJv2Yw&s",
  "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSvyAc3xWLdjKT5q3VuMfE2-kHOICUqWDLt3_7PFdCZlUdlbww&s",
  "../assets/milk.png",
  "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ3vpf4hMc-8BVrwIBjpziVJ4L_maoZKUFasl0GrsBGYJaLJNG_&s",
  "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTf2flUG-iqoMRWipn-xBbZ5dE_cCRGx64GvYJSzmCbpA7jIl8&s",
  "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQgWD_GbDRChCD4NIMcDQmhIrubtqsanTi1OD_M_Yv_EmJSlPQ&s",
  "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRpBXysH3zaQ9FjRHLZWgzHITxxkBX6HYr-UJ1eTcf6sEGdZxI&s"
];
const desert_name = [
  "巧克力蛋糕", "雞胸肉", "牛奶", "藍莓", "魚肉", "香蕉", "堅果"
];
const delay = ms => new Promise(res => setTimeout(res, ms));

var num_arr = [[1, 2, 3, 4], [5, 6, 7], [8, 9]]; // 外圈、內圈
var num_list = [];
var click_time = 0;
var rotated = 1;

function shuffle(array) {
  for (let i = array.length - 1; i > 0; i--) {
    let j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

function rotate_picture() {
  var div = document.getElementsByClassName("food");
  // console.log(div);
  for (let i = 0; i < 2; i++)
    (div[i]).style.transform = 'rotate(' + 8 * rotated + 'deg)';
  rotated *= -1;
}

function get_desert() {
  console.log("getnewdesert");
  var cho = Math.floor(Math.random() * 7);
  var pic = document.getElementById("desert");
  var tex = document.getElementById("tex");
  var c = document.getElementById("eat");
  var ctx = c.getContext("2d");

  click_time = 0;
  pic.src = desert_list[cho];
  tex.innerHTML = desert_name[cho];
  ctx.clearRect(0, 0, c.width, c.height); // 把吃的痕跡清掉

  num_list.length = 0;
  for (let i = 0; i < 3; i++)
    num_list = num_list.concat(shuffle(num_arr[i]));
  // console.log("numlist after shuffle: " + num_list);
}

async function eat_desert() {
  console.log("點擊甜點");
  var c = document.getElementById("eat");
  var ctx = c.getContext("2d");
  ctx.fillStyle = "white";
  console.log(num_list[click_time]);
  click_time++;

  if (click_time == 10) {
    // var wait = document.getElementById("eat2");
    // wait.style.visibility = "visible";
    ctx.beginPath();
    ctx.rect(0, 0, 280, 250);
    ctx.fill();

    ctx.fillStyle = "black";
    ctx.font = "30px Verdana";
    rotated = 0;
    rotate_picture();
    rotated = 1;
    ctx.fillText("Complete !", 70, 130);
    var count = document.getElementById("click_time");
    console.log("count" + count.innerHTML);
    count.innerHTML = Number(count.innerHTML) + 1;
    await delay(150); // 明天查詢讓他這段時間不能點擊
    get_desert();
  }
  else if (click_time < 10) {
    rotate_picture();
    switch (num_list[click_time - 1]) {
      case 1: // line 1
        ctx.beginPath();
        ctx.arc(50, 10, 60, 0, 2 * Math.PI);
        ctx.fill();
        break;
      case 2:
        ctx.beginPath();
        ctx.arc(25, 85, 45, 0, 2 * Math.PI);
        ctx.fill();
        break;
      case 3:
        ctx.beginPath();
        ctx.arc(25, 160, 40, 0, 2 * Math.PI);
        ctx.fill();
        break;
      case 4:
        ctx.beginPath();
        ctx.arc(50, 245, 60, 0, 2 * Math.PI);
        ctx.fill();
        break;
      case 5: // line 2
        ctx.beginPath();
        ctx.arc(130, 20, 70, 0, 2 * Math.PI);
        ctx.fill();
        break;
      case 6:
        ctx.beginPath();
        ctx.arc(100, 125, 80, 0, 2 * Math.PI);
        ctx.fill();
        break;
      case 7:
        ctx.beginPath();
        ctx.arc(110, 240, 70, 0, 2 * Math.PI);
        ctx.fill();
        break;
      case 8: //line 3
        ctx.beginPath();
        ctx.arc(215, 20, 75, 0, 2 * Math.PI);
        ctx.fill();
        break;
      case 9:
        ctx.beginPath();
        ctx.arc(215, 250, 75, 0, 2 * Math.PI);
        ctx.fill();
        break;
    }
  }
}

$(document).ready(function () {
  console.log("ready");
});
