import cv2
from PIL import Image, ImageDraw
import numpy as np

def combine_images(img1, img2, bgpath):
    # 將 numpy array 轉換為 PIL Image
    if isinstance(img1, np.ndarray):
        img1 = Image.fromarray(cv2.cvtColor(img1, cv2.COLOR_BGR2RGB))
    if isinstance(img2, np.ndarray):
        img2 = Image.fromarray(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB))
    
    # 載入背景圖片
    bg_img = Image.open(bgpath)

    frame_size = 50

    new_width = img1.width + img2.width + 100 + frame_size * 2
    new_height = max(img1.height, img2.height) + frame_size * 2

    # 貼上圖片
    bg_img.paste(img1, (frame_size, frame_size))
    bg_img.paste(img2, (img1.width + 100 + frame_size, frame_size))

    # 畫箭頭
    draw = ImageDraw.Draw(bg_img)
    arrow_start = (img1.width + frame_size + 20, new_height // 2)
    arrow_end = (img1.width + frame_size + 70, new_height // 2)
    draw.line([arrow_start, arrow_end], fill="black", width=8)
    draw.polygon([(arrow_end[0], arrow_end[1] - 10), 
                 (arrow_end[0], arrow_end[1] + 10), 
                 (arrow_end[0] + 20, arrow_end[1])], fill="black")

    return bg_img

if __name__ == "__main__":
    img1 = cv2.imread("img41.png")
    img2 = cv2.imread("combine_img.png")
    res = combine_images(img1, img2, "bgcolorimg.png")
    res.show()