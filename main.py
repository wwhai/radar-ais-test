import time
import tkinter as tk
import math
import threading
import http.server
import json

# 创建主窗口
root = tk.Tk()
root.title("Radar Scan")
root.geometry("600x600")

# 定义雷达的参数
center_x = 300  # 中心点的x坐标
center_y = 300  # 中心点的y坐标
radius = 250  # 雷达的半径

# 创建画布
canvas = tk.Canvas(root, width=600, height=600, bg="white")
canvas.pack()

# 初始化雷达数据
radar_data = []


# 绘制雷达的扫描圆圈和刻度线
def draw_radar_scan():
    canvas.delete("all")  # 清空画布

    # 绘制雷达的扫描圆圈
    canvas.create_oval(
        center_x - radius,
        center_y - radius,
        center_x + radius,
        center_y + radius,
        outline="gray",
        width=2,
    )

    # 绘制扫描线
    scan_angle = (360 - (int(time.time()) % 2) * 180) % 360  # 计算当前扫描线的角度
    scan_x = center_x + radius * math.cos(math.radians(scan_angle))
    scan_y = center_y - radius * math.sin(math.radians(scan_angle))
    canvas.create_line(center_x, center_y, scan_x, scan_y, fill="red", width=1)

    # 绘制刻度线、标签和连接线
    for angle in range(0, 360, 30):
        x1 = center_x + (radius - 10) * math.cos(math.radians(angle))
        y1 = center_y - (radius - 10) * math.sin(math.radians(angle))
        x2 = center_x + (radius + 10) * math.cos(math.radians(angle))
        y2 = center_y - (radius + 10) * math.sin(math.radians(angle))
        canvas.create_line(x1, y1, x2, y2, fill="gray", width=2)
        canvas.create_text(x2, y2, text=str(angle), fill="gray")

        # 绘制连接线
        canvas.create_line(center_x, center_y, x2, y2, fill="gray", width=1)

    # 绘制雷达数据点
    for point in radar_data:
        x = point["x"]
        y = point["y"]
        label = point.get("label", "")

        point_x = center_x + x
        point_y = center_y - y

        # 绘制点
        canvas.create_oval(
            point_x - 5, point_y - 5, point_x + 5, point_y + 5, fill="blue"
        )

        # 绘制标签
        canvas.create_text(point_x + 10, point_y, text=label, anchor="w", fill="black")

    root.after(100, draw_radar_scan)


# 自定义请求处理程序
class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/update_radar_data":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))

            global radar_data
            radar_data = data

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Radar data updated successfully.")
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Resource not found.")

    def log_message(self, format, *args):
        return  # 禁止日志输出


# 创建HTTP服务器并运行
def run_http_server():
    server_address = ("", 8000)
    httpd = http.server.HTTPServer(server_address, RequestHandler)
    httpd.serve_forever()


# 启动HTTP服务器线程
http_thread = threading.Thread(target=run_http_server)
http_thread.start()


# 定义鼠标移动事件处理函数
def mouse_move(event):
    x = event.x - center_x
    y = center_y - event.y
    distance = math.sqrt(x**2 + y**2)
    canvas.create_text(
        event.x + 10,
        event.y - 10,
        text="X: {}, Y: {}, Distance: {}".format(x, y, distance),
    )


# 将鼠标移动事件绑定到画布
canvas.bind("<Motion>", mouse_move)

# 启动雷达扫描
draw_radar_scan()

root.mainloop()
