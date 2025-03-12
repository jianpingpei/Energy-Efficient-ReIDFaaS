import math
import os
import time
from time import sleep

from flask import Flask, request, make_response
import requests
import threading
from datetime import datetime

app = Flask(__name__)

schedule_db = {
    "1": [
        # {"start_time": "1:57:07", "duration": 610}, 
        # {"start_time": "2:20:16", "duration": 572}, 
        # {"start_time": "2:38:23", "duration": 568},
        # {"start_time": "3:3:48", "duration": 553}, 
        # {"start_time": "4:22:37", "duration": 620} 
    ],
    "2": [
        # {"start_time": "0:56:17", "duration": 49}, 
        # {"start_time": "0:57:53", "duration": 41}, 
        # {"start_time": "1:55:51", "duration": 41},
        # {"start_time": "2:32:53", "duration": 39}, 
        # {"start_time": "5:15:32", "duration": 48}  
    ],
    "3": [
        {"start_time": "2:44:26", "duration": 108},  
        # {"start_time": "3:6:11", "duration": 91}, 
        # {"start_time": "4:22:33", "duration": 100}, 
        # {"start_time": "4:34:33", "duration": 94}  
    ],
    "4": [
        # {"start_time": "1:36:44", "duration": 81}, 
        # {"start_time": "1:47:58", "duration": 90}, 
        # {"start_time": "2:16:20", "duration": 102},
        # {"start_time": "2:23:19", "duration": 85}, 
        # {"start_time": "5:2:45", "duration": 90} 
    ],
    "5": [
        {"start_time": "2:26:35", "duration": 654},
        # {"start_time": "3:14:17", "duration": 642},
        # {"start_time": "3:30:46", "duration": 619},
        # {"start_time": "5:21:33", "duration": 659}
    ],
    "7": [
        # {"start_time": "1:55:10", "duration": 93}, 
        {"start_time": "2:37:25", "duration": 109},  
        # {"start_time": "3:5:22", "duration": 84},  
        # {"start_time": "3:49:52", "duration": 88}, 
        # {"start_time": "5:14:27", "duration": 93} 
    ],
    "8": [
        {"start_time": "1:54:48", "duration": 816}, 
        {"start_time": "2:9:26", "duration": 800},
        {"start_time": "2:27:20", "duration": 815},  
        {"start_time": "3:25:01", "duration": 846}, 
        {"start_time": "5:18:03", "duration": 763}  
    ],
    "9": [
        {"start_time": "2:8:14", "duration": 169}, 
        {"start_time": "2:33:22", "duration": 171}, 
        {"start_time": "3:17:02", "duration": 175},  
        {"start_time": "4:51:05", "duration": 166}, 
        {"start_time": "5:41:54", "duration": 154}  
    ]
}

node_status = {
    "1": {
        "total_energy": 936.0,  # E_i^t (Wh)
        "remaining_energy": 936.0,  # E_i^r (Wh)
        "max_tasks": 10,  # L_i^t
        "current_tasks": 0,  # L_i^n
        "num_hot_container": 0,
        "first_power": 70,
        "avg_power": 25.0,  
        "max_power": 280,
        "idle_power": 78,  
        "container_start_power": 0.357,
    },
    "2": {
        "total_energy": 144.0,  # E_i^t (Wh)
        "remaining_energy": 144.0,  # E_i^r (Wh)
        "max_tasks": 2,  # L_i^t
        "current_tasks": 0,  # L_i^n
        "num_hot_container": 0,
        "first_power": 5.5,
        "avg_power": 5,  
        "max_power": 31.5,
        "idle_power": 12, 
        "container_start_power": 0.028,
    },
    "3": {
        "total_energy": 108.0,  # E_i^t (Wh)
        "remaining_energy": 108.0,  # E_i^r (Wh)
        "max_tasks": 6,  # L_i^t
        "current_tasks": 0,  # L_i^n
        "num_hot_container": 0,
        "first_power": 3.5,
        "avg_power": 3,  
        "max_power": 24,
        "idle_power": 9, 
        "container_start_power": 0.005,
    },
}


def calculate_priority(node_id, camera_id, is_same_node):
    """计算节点优先级分数"""
    node = node_status[node_id]
    # 从预知数据库获取任务时长
    current_time = datetime.now().strftime("%H:%M:%S")
    current_time_dt = datetime.strptime(current_time, "%H:%M:%S") - start_time_dt
    current_time_dt = datetime.strptime("00:00:00", "%H:%M:%S") + current_time_dt
    duration = next(
        (item["duration"] for item in schedule_db.get(camera_id, [])
         if abs((datetime.strptime(item["start_time"], "%H:%M:%S") - current_time_dt).total_seconds()) <= 60
         ), 60)  # 默认60秒
    predict_power = node["avg_power"] * duration / 3600 if node["current_tasks"] > 0 else node["first_power"] * duration / 3600

    # 计算各分项
    energy_term = (node["remaining_energy"] / node["total_energy"]) * alpha

    # load_term = ((node["max_tasks"] - node["current_tasks"]) / node["max_tasks"]) * beta
    hot_container_term = node["num_hot_container"] * beta
    predict_term = ((node["remaining_energy"] - predict_power) / node["remaining_energy"]) * gamma
    penalty = delta * (0 if is_same_node else 1)
    load_term = math.floor(node["current_tasks"] / node["max_tasks"])
    # print(datetime.now().isoformat(), f"Node {node_id} energy_term: {energy_term}, load_term: {load_term}, "
    #                                   f"hot_container_term: {hot_container_term}, penalty: {penalty}, predict_power: {predict_power}")
    return energy_term + hot_container_term + predict_term - penalty - load_term


def select_target_node(camera_id, source_node):
    """选择最优节点"""
    max_score = -float('inf')
    best_node = None
    for node_id in node_status:
        is_same_node = (node_id == source_node)
        score = calculate_priority(node_id, camera_id, is_same_node)
        if score > max_score:
            max_score = score
            best_node = node_id
    return best_node

def update_hot_container_status(node_id):
    sleep(30)
    if node_status[node_id]["num_hot_container"] > 0:
        node_status[node_id]["num_hot_container"] -= 1

@app.route('/', methods=['POST'])
def handle_request():
    data = request.get_json()
    camera_id = data["video_id"]
    source_node = data["source_node"]

    # 1. 选择目标节点
    target_node = select_target_node(camera_id, source_node)

    # 2. 转发请求到目标节点的target-detector
    target_url = f"http://target-detector-{target_node}.default.192.168.10.82.sslip.io/"
    try:
        node_status[target_node]["current_tasks"] += 1
        if node_status[target_node]["num_hot_container"] == 0:
            node_status[target_node]["remaining_energy"] -= node_status[target_node]["container_start_power"]
        else:
            node_status[target_node]["num_hot_container"] -= 1
        response = requests.post(target_url, json=data)
        node_status[target_node]["current_tasks"] -= 1
        node_status[target_node]["num_hot_container"] += 1
        threading.Thread(target=update_hot_container_status, args=(target_node,), daemon=True).start()

        return response
    except Exception as e:
        return make_response({"error": str(e)}, 500)

def update_node_status():
    log_dir = "/home/data/energy_trace"
    os.makedirs(log_dir, exist_ok=True)  # 确保目录存在
    log_file = os.path.join(log_dir, "energy.csv")

    if not os.path.isfile(log_file):
        with open(log_file, 'w') as f:
            headers = [
                'timestamp', 'node_id',
                'remaining_energy', 'current_tasks', 'num_hot_container',
                'total_energy', 'max_tasks', 'first_power', 'avg_power',
                'max_power', 'idle_power', 'container_start_power'
            ]
            f.write(','.join(headers) + '\n')

    while True:
        current_time = datetime.now().isoformat()
        rows = []

        for node_id in node_status:
            # 原有能量计算逻辑
            node = node_status[node_id]
            if node["current_tasks"] > 1:
                power = (node["avg_power"] * (node["current_tasks"] - 1) / 60
                         + node["first_power"] * 1 / 60)
            else:
                power = node["first_power"] * node["current_tasks"] / 60

            # 更新剩余能量
            node["remaining_energy"] -= (node["idle_power"] / 60 + power)
            node["remaining_energy"] = max(node["remaining_energy"], 0)  # 防止负值

            # 构建数据行
            row = [
                current_time,
                node_id,
                node["remaining_energy"],
                node["current_tasks"],
                node["num_hot_container"],
                node["total_energy"],
                node["max_tasks"],
                node["first_power"],
                node["avg_power"],
                node["max_power"],
                node["idle_power"],
                node["container_start_power"]
            ]
            rows.append(row)

        # 追加写入文件
        with open(log_file, 'a') as f:
            for row in rows:
                f.write(','.join(map(str, row)) + '\n')

        time.sleep(60)

threading.Thread(target=update_node_status, daemon=True).start()

if __name__ == '__main__':
    # 参数初始化
    alpha = 0.8
    beta = 0.1
    gamma = 0.1
    delta = 0.05
    start_time = datetime.now().strftime("%H:%M:%S")
    start_time_dt = datetime.strptime(start_time, "%H:%M:%S")
    app.run(host='0.0.0.0', port=2001, debug=False)