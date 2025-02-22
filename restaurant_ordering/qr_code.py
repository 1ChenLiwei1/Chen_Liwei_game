import qrcode

def generate_qr_code(table_id):
    # 定义 URL，指向正确的订单页面
    url = f"https://3a8f-118-189-129-137.ngrok-free.app"  # 假设 URL 格式是这样的

    # 生成 QR 码
    qr = qrcode.make(url)

    # 保存 QR 码为图片文件
    qr.save(f"qr_code_{table_id}.png")

# 示例: 生成指向表格 1 的 QR 码
generate_qr_code(3)
