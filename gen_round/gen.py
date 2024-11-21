import os
from rembg import remove
from PIL import Image
import cv2
import numpy as np
import random
import time
import replicate
import requests
from dotenv import load_dotenv
from combine_res import combine_images

load_dotenv()
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
IMG_BB_API_KEY = os.getenv('IMG_BB_API_KEY')

# 貓咪生成用prompt：紅黃綠藍紫
cat_prompt = [
    "a crying cat, wearing a purple shorts, bucket hat, and holding a purple cute camera",
    "a crying cat wearing a blue dress and a white cap, holding a blue flower",
    "a cat wearing a green green coat and a green side backpack",
    "smiling cat wearing a yellow T-shirt and holding the little yellow duck",
    "smiling, mouth open, cat wearing a red dress and big red bow on the top of the head"
]
# 風景圖片地點：海灘、河岸、公園、森林、瀑布、花園 隨機選擇
scenary = [
    "a serene sandy beach with gentle waves and clear blue water",
    "a peaceful riverbank with lush green grass and flowing water",
    "a park with a beautiful fountain in the center", 
    "a dense forest with tall trees, sunlight filtering through leaves", 
    "a majestic waterfall cascading down rocks into a clear pool", 
    "a garden"
        ]

# 輸出風景圖片
def download_output(output_list, save_dir="./output"):
    # 確保輸出目錄存在
    os.makedirs(save_dir, exist_ok=True)
    
    try:
        # 只處理第二個輸出（生成的新圖片）
        output_url = str(output_list[1])  # 使用索引 1 獲取第二個輸出
        
        # 下載圖片
        response = requests.get(output_url)
        if response.status_code == 200:
            # 生成檔案名稱
            file_path = os.path.join(save_dir, "2.png")
            
            # 保存圖片
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"已保存生成的圖片: {file_path}")
            return file_path
        else:
            print(f"下載失敗，狀態碼: {response.status_code}")
    
    except Exception as e:
        print(f"處理輸出時發生錯誤: {str(e)}")

def read_image_from_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }
    
    # 獲取圖片數據
    response = requests.get(url, headers=headers)
    # 檢查 HTTP 狀態碼
    if response.status_code != 200:
        print(f"圖片下載失敗，HTTP 狀態碼: {response.status_code}")
        return
    
    # 檢查內容是否非空
    if len(response.content) == 0:
        print("圖片下載失敗，回應內容為空")
        return
    
    # 檢查內容的開頭是否包含圖片格式的標識符
    if response.content[:4] not in [b'\x89PNG', b'\xff\xd8\xff']:
        print("回應內容看起來不像圖片數據")
        return

    # 將圖片數據轉換成 numpy array
    image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    
    # 使用 cv2 解碼圖片
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    
    # 檢查是否成功解碼圖片
    if image is None:
        print("圖片解碼失敗，無法從 URL 讀取圖片")
        return
    # 顯示圖片
    # cv2.imshow("Image", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    return image

def color_preprocessor(image):
    # 使用 OpenCV resize
    # color_palette = cv2.resize(image, (6, 6))
    # color_palette = cv2.resize(color_palette, (8, 8), interpolation=cv2.INTER_LINEAR)
    # color_palette = cv2.resize(color_palette, (512, 512), interpolation=cv2.INTER_NEAREST)
    color_palette = image.resize((8, 8))
    color_palette = color_palette.resize((512, 512), resample=Image.Resampling.NEAREST)

    return color_palette

def run_color_model(imgurl):
    random.seed(time.time_ns())

    print("開始執行背景模型")
    color_prompt = "A photo of " + scenary[random.randint(0, len(scenary)-1)] + ", 4k photo, highly detailed"
    print("color prompt:", color_prompt)
    output = replicate.run(
        "gogochi/t2i-adapter-sd-color:dba7f5f41c17395348e47c8c10944037ac2d4852713d4235eef4de86e419d7f2",
        input={
            "image": imgurl,
            "prompt": color_prompt,
            "scheduler": "K_EULER_ANCESTRAL",
            "num_samples": 1,
            "guidance_scale": 8.0,
            "negative_prompt": "anime, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured",
            "num_inference_steps": 30,
            "adapter_conditioning_scale": 0.95
        }
    )
    print("執行完成")
    return read_image_from_url(output[1])

def remove_bg(cat_image):
    img = cv2.resize(cat_image, (512, 512))
    print("開始移除背景...")
    cat_rmbg = remove(img, alpha_matting=True,                           
        alpha_matting_foreground_threshold=235,       # 稍微降低，讓毛髮邊緣更自然
        alpha_matting_background_threshold=15,        # 稍微提高，改善毛髮邊緣
        alpha_matting_erode_size=10,                  # 降低侵蝕大小，保留更多毛髮細節
        post_process_mask=True, bgcolor=(0,0,0,0))
    
    cv2.imwrite('remove.png', cat_rmbg)

    return cat_rmbg    

def run_cat_model(moodscore):
    prompt = cat_prompt[moodscore]
    print("開始執行貓咪模型")
    cat = replicate.run(
        "peter65374/sdxl-cat:0ac4841eb414b90346e08e27c48be8e3b03f6e8281d5844f965be8347614d2ed",
        input={
            "width": 1024,
            "height": 1024,
            "prompt": prompt,
            "refine": "no_refiner",
            "scheduler": "K_EULER",
            "lora_scale": 0.8,
            "num_outputs": 1,
            "guidance_scale": 7.5,
            "apply_watermark": True,
            "high_noise_frac": 0.8,
            "negative_prompt": "text, logos, watermark, captions, missing ear",
            "prompt_strength": 0.8,
            "num_inference_steps": 30
        }
    )
    cat = read_image_from_url(cat[0])
    # print(cat[0])
    cat_rmbg = remove_bg(cat)
    # print("執行完成")
    return cat_rmbg

def combine_cat_and_background(cat_img, background_image, scale=0.6):
    # 讀取背景圖片並調整大小
    bg_img = cv2.resize(background_image, (512, 512))
    
    # 讀取貓咪圖片（包含 alpha 通道）
    # cat_img = cv2.imread(cat_image, cv2.IMREAD_UNCHANGED)
    # cat_img = cv2.resize(cat_img, (512, 512))

    # 計算貓咪圖片的實際大小（去除透明部分）
    mask = cat_img[:, :, 3] > 0
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    y_min, y_max = np.where(rows)[0][[0, -1]]
    x_min, x_max = np.where(cols)[0][[0, -1]]
    
    # 調整貓咪大小
    cat_height = y_max - y_min
    cat_width = x_max - x_min
    new_height = int(cat_height * scale)
    new_width = int(cat_width * scale)
    cat_resized = cv2.resize(cat_img[y_min:y_max, x_min:x_max], (new_width, new_height))

    # 計算貓咪的位置
    place = (random.randint(0, 9)-4)*35
    x_offset = ((bg_img.shape[1] - new_width) // 2) + place
    y_offset = bg_img.shape[0] - new_height

    # 提取 alpha 通道並進行羽化處理
    alpha_mask = cat_resized[:, :, 3].astype(float)
    alpha_mask = cv2.GaussianBlur(alpha_mask, (5,5), 0)
    alpha_mask = alpha_mask / 255.0

    # 創建結果圖片
    result = bg_img.copy()

    alpha = cat_resized[:, :, 3].astype(float) / 255.0

    # 創建一個更平滑的過渡效果
    edge_threshold = 0.85  # 開始處理邊緣的閾值
    edge_softness = 1.0   # 邊緣柔和度

    for y in range(new_height):
        for x in range(new_width):
            if x + x_offset < bg_img.shape[1] and y + y_offset < bg_img.shape[0]:
                if alpha[y, x] > 0:
                    # 獲取顏色
                    bg_color = result[y + y_offset, x + x_offset].astype(float)
                    fg_color = cat_resized[y, x, :3].astype(float)
                    
                    current_alpha = alpha[y, x]
                    
                    # 改進的邊緣處理
                    if current_alpha < edge_threshold:
                        # 使用更平滑的過渡函數
                        edge_factor = (current_alpha / edge_threshold) ** edge_softness
                        
                        # 在邊緣處理時考慮周圍背景顏色
                        if x > 0 and x < new_width-1 and y > 0 and y < new_height-1:
                            # 獲取周圍背景顏色的平均值
                            surrounding_bg = np.mean([
                                result[y + y_offset - 1, x + x_offset],
                                result[y + y_offset + 1, x + x_offset],
                                result[y + y_offset, x + x_offset - 1],
                                result[y + y_offset, x + x_offset + 1]
                            ], axis=0).astype(float)
                            
                            # 混合周圍背景顏色
                            bg_color = (bg_color + surrounding_bg) / 2
                        
                        # 更平滑的顏色過渡
                        fg_color = fg_color * edge_factor + bg_color * (1 - edge_factor)
                    
                    # 最終的顏色混合
                    blended = (fg_color * current_alpha + bg_color * (1 - current_alpha))
                    result[y + y_offset, x + x_offset] = blended.astype(np.uint8)

    return result

def upload_imgBB(image):
    try:
        url = "https://api.imgbb.com/1/upload"
        
        # 將 OpenCV 圖片編碼為 PNG 格式的字節
        _, img_encoded = cv2.imencode('.png', image)
        
        # 準備上傳的數據
        payload = {
            "key": IMG_BB_API_KEY,
        }
        files = {
            "image": ("image.png", img_encoded.tobytes(), "image/png")
        }
        
        # 發送請求
        print("正在上傳圖片...")
        response = requests.post(url, data=payload, files=files)
        
        # 檢查回應
        if response.status_code == 200:
            json_data = response.json()
            if json_data.get("success"):
                image_url = json_data["data"]["url"]
                print(f"上傳成功！圖片URL: {image_url}")
                return image_url
            else:
                print(f"上傳失敗: {json_data.get('error', {}).get('message')}")
        else:
            print(f"上傳失敗，狀態碼: {response.status_code}")
                
    except Exception as e:
        print(f"發生錯誤: {str(e)}")
    return None

def delete_bloack_line(image):
    height, width = image.shape[:2]
    grid_size = 8
    cell_height = height // grid_size
    cell_width = width // grid_size

    # 創建輸出圖像
    output_image = np.zeros_like(image)

    # 處理每個網格
    for i in range(grid_size):
        for j in range(grid_size):
            # 計算當前網格的範圍
            y1 = i * cell_height
            y2 = (i + 1) * cell_height
            x1 = j * cell_width
            x2 = (j + 1) * cell_width

            # 獲取中心點顏色
            center_y = (y1 + y2) // 2
            center_x = (x1 + x2) // 2
            color = image[center_y, center_x]

            # 填充網格
            output_image[y1:y2, x1:x2] = color

    output_image = cv2.resize(output_image, (512, 512))
    return output_image

def round_photo_generator(pixeled_image, avg_mood_score):
    image = delete_bloack_line(pixeled_image)  # 這裡需要放"正方形" 要用來生圖的像素畫
    # image = color_preprocessor(pixeled_image) 
    # cv2.imwrite('pixel.png', image)
    # cv2.imshow("pixel", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    url = upload_imgBB(image)

    background_img = run_color_model(url)
    
    cat_rmbg = run_cat_model(avg_mood_score) # 0 ~ 4
    combine_img = combine_cat_and_background(cat_rmbg, background_img)
    # cv2.imshow("combine_img", combine_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    combine_img = combine_images(image, combine_img, "bgcolorimg.png")
    combine_img = cv2.cvtColor(np.array(combine_img), cv2.COLOR_RGB2BGR) # 轉CV2格式
    cv2.imwrite('combine_img.png', combine_img)

    combine_url = upload_imgBB(combine_img)

    return combine_url

if __name__ == "__main__":
    # img_url = "https://i.imgur.com/QuwUUPR.png"
    # pixeled_image = read_image_from_url(img_url)
    # url = "https://i.ibb.co/YDY1b0g/img6-resize.png"
    pixeled_image = cv2.imread('./img41.png')
    round_photo_generator(pixeled_image, 0)
