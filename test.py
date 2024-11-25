import requests

# 使用 OAuth token 認證
access_token = 'adfd8e81b51cfa246aaa1d5b5f6e7f41353a055b'

headers = {
    "Authorization": f"Bearer {access_token}"
}

# 獲取帳戶中的所有圖片
response = requests.get("https://api.imgur.com/3/account/me/images", headers=headers)

if response.status_code == 200:
  images = response.json()["data"]
  for image in images:
    print(images)
else:
  print(f"獲取圖片失敗，錯誤代碼：{response.status_code}")
