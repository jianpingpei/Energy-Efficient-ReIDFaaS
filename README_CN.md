<div align="center">

# ReIDFaaS

### 面向边缘-云连续体的节能无服务器行人重识别系统

[![Paper](https://img.shields.io/badge/IEEE-ICWS%202025-blue)](https://ieeexplore.ieee.org/document/11169601/)
[![Knative](https://img.shields.io/badge/Knative-Serverless-0865AD?logo=knative&logoColor=white)](https://knative.dev/)
[![K3s](https://img.shields.io/badge/K3s-Kubernetes-FFC61C?logo=k3s&logoColor=white)](https://k3s.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[论文](https://ieeexplore.ieee.org/document/11169601/) |
[项目主页](https://jianpingpei.github.io/Energy-Efficient-ReIDFaaS/) |
[代码](https://github.com/jianpingpei/Energy-Efficient-ReIDFaaS)

**[English Version](README.md)**

</div>

---

## 概述

**ReIDFaaS** 是一个面向边缘-云连续体的无服务器行人重识别 (Re-ID) 系统，旨在实现节能和低延迟的运行。它用基于行人运动触发的事件驱动架构取代了传统的常驻监控流水线，显著降低了资源受限边缘设备上的资源消耗。

发表于 **IEEE 国际 Web 服务会议 (ICWS) 2025**。

---

## 亮点

<table>
<tr>
<td align="center"><b>23.3%</b><br/>边缘节点<br/>可用性提升</td>
<td align="center"><b>55%</b><br/>内存占用<br/>降低</td>
<td align="center"><b>53%</b><br/>吞吐量<br/>提升</td>
<td align="center"><b>30%</b><br/>P99 延迟<br/>降低</td>
</tr>
</table>

---

## 核心贡献

1. **事件驱动重识别工作流**
   基于行人运动触发的事件驱动系统，用运动检测替代持续计算，显著减少资源使用的同时保持实时性能。

2. **节能调度**
   感知硬件状态的动态调度器，基于实时能量状态、热容器可用性和负载约束分配任务，将边缘节点可用性提升 23.3%。

3. **自适应批处理冷启动缓解**
   基于延迟约束的自适应批处理机制，通过智能请求分组减少冷启动频率，将 P99 延迟降低 30%，平均内存使用降低 55%。

---

## 系统架构

ReIDFaaS 采用三层边缘-云架构（数据源层、边缘层、云层），使用 Kafka 进行数据流传输，NFS 提供持久化存储。基于 K3s 的 Knative 实现无服务器自动扩缩容和事件驱动执行。

<p align="center">
  <img src="assets/Architecture.png" width="600" alt="ReIDFaaS 系统架构"/>
</p>

系统由五个核心无服务器函数组成：

| 函数 | 层级 | 描述 |
|------|------|------|
| **move-detector** | 边缘层 | 捕获摄像头流并通过 Lucas-Kanade 光流法检测行人运动 |
| **target-detector** | 边缘层 | 使用 YOLOX + ByteTrack 进行行人检测和跟踪 |
| **feature-extractor** | 云层 | 使用 M3L 模型提取重识别外观特征 |
| **feature-matcher** | 云层 | 通过余弦相似度匹配查询特征与候选特征 |
| **front-end** | 边缘层 | 用于上传查询图片和查看结果的 Web 界面 |

---

## 工作流程

<p align="center">
  <img src="assets/work-flow.png" width="800" alt="ReIDFaaS 工作流程"/>
</p>

15 步工作流程如下：

1. **运动检测（步骤 1-2）**：`move-detector` 处理视频流，检测行人运动，激活下游函数，并将相关帧发送到 Kafka。
2. **目标检测（步骤 3-4）**：`target-detector` 使用 YOLOX + ByteTrack 进行行人检测和跟踪，将边界框输出到 Kafka。
3. **特征提取（步骤 5-6）**：`feature-extractor` 使用 M3L 提取外观特征，将结果存储到 NFS。
4. **查询初始化（步骤 7-8）**：用户通过 `front-end` 上传查询图片，触发 `feature-matcher`。
5. **特征匹配（步骤 9-13）**：`feature-matcher` 获取查询特征，与 NFS 上的历史特征进行匹配，写入结果。
6. **结果展示（步骤 14-15）**：`front-end` 从 NFS 读取结果并展示给用户。

---

## 项目结构

```
Energy-Efficient-ReIDFaaS/
├── common/                         # 公共工具库
│   ├── BaseService.py              # 抽象基础服务（Kafka + 队列）
│   ├── DetTrackResult.py           # 检测/跟踪结果数据对象
│   ├── Get_Param.py                # 环境变量参数获取器
│   ├── Logger.py                   # 彩色日志工具
│   └── kafka/                      # Kafka 消费者/生产者封装
├── move-detector/                  # 运动检测函数
│   ├── move-detector.py            # Flask 应用（端口 3001）
│   └── optical_flow.py             # Lucas-Kanade 光流（CPU + CUDA）
├── target-detector/                # 目标检测 + 跟踪
│   ├── target-detector.py          # Flask 应用（端口 4001）
│   ├── model/bytetracker.py        # 基于 YOLOX 的 ByteTracker
│   └── yolox/                      # YOLOX 框架
├── feature-extractor/              # 特征提取函数
│   ├── feature-extractor.py        # Flask 应用（端口 6001）
│   └── M3L/                        # M3L 重识别模型架构
├── feature-matcher/                # 单请求特征匹配
│   ├── feature-matcher.py          # Flask 应用（端口 5001）
│   ├── multi_img_matching.py       # 余弦相似度匹配
│   └── store_result.py             # 保存标注结果图片
├── feature-matcher-batch/          # 批量特征匹配
│   ├── feature-matcher-batch.py    # Flask 应用（端口 5001），自适应批处理
│   ├── multi_img_matching.py       # 批量匹配逻辑
│   └── store_result.py             # 保存标注结果图片
├── front-end/                      # Web 界面函数
│   ├── front-end.py                # Flask 应用（端口 8080）
│   └── templates/result.html       # 结果展示模板
├── scheduler/                      # 节能任务调度器
│   └── scheduler.py                # 基于优先级的节点选择（端口 2001）
├── models/                         # 预训练模型权重
│   ├── m3l.pth                     # M3L 重识别模型
│   └── yolox.pth                   # YOLOX 行人检测模型
├── yaml/                           # Kubernetes/Knative 部署清单
│   ├── functions/                  # Knative 服务定义
│   ├── pv/                         # PersistentVolume（NFS）
│   └── pvc/                        # PersistentVolumeClaim
├── *.Dockerfile                    # 容器镜像定义
├── assets/                         # 论文图片
└── docs/                           # 项目主页
```

---

## 环境依赖

部署 ReIDFaaS 前，请确保以下基础设施已就绪：

| 组件 | 描述 |
|------|------|
| **K3s** | 轻量级 Kubernetes 集群（1 个 master + N 个 agent 节点） |
| **Knative** | 安装在 K3s 上的无服务器框架，支持自动扩缩容 |
| **Apache Kafka** | 分布式消息队列集群 |
| **NFS** | 网络文件系统，用于共享持久存储 |
| **Docker** | 容器运行时，用于构建镜像 |
| **NVIDIA GPU**（可选） | 用于边缘/云节点的 GPU 加速推理 |

### 硬件需求（参考测试平台）

| 节点 | CPU | GPU | 内存 | 角色 |
|------|-----|-----|------|------|
| Master | 32 核 | NVIDIA RTX 3080Ti | 256GB | 控制平面 + feature-matcher + feature-extractor |
| Agent 1 | 8 核 | NVIDIA RTX 1080Ti | 32GB | 边缘节点（5 个摄像头） |
| Agent 2 | 4 核 | 无 | 16GB | 边缘节点（1 个摄像头） |
| Agent 3 | 8 核 | 32 Tensor 核心（Jetson Orin NX） | 16GB | 边缘节点（2 个摄像头） |

---

## 部署指南

### 步骤 1：构建 Docker 镜像

使用提供的 Dockerfile 为每个函数构建容器镜像：

```bash
# GPU 函数（需要 CUDA 运行时）
docker build -f target-detector-gpu.Dockerfile -t <registry>/target-detector:latest .
docker build -f feature-extractor-gpu.Dockerfile -t <registry>/feature-extractor:latest .
docker build -f feature-matcher-gpu.Dockerfile -t <registry>/feature-matcher:latest .
# 或批量版本
docker build -f feature-matcher-batch-gpu.Dockerfile -t <registry>/feature-matcher-batch:latest .

# CPU 函数
docker build -f move-detector.Dockerfile -t <registry>/move-detector:latest .
docker build -f front-end.Dockerfile -t <registry>/front-end:latest .
docker build -f scheduler.Dockerfile -t <registry>/scheduler:latest .

# 推送到镜像仓库
docker push <registry>/target-detector:latest
# ... 推送所有镜像
```

### 步骤 2：配置环境变量

确认关键函数的 API 地址并在 YAML 文件中配置：

| 变量 | 描述 | 示例 |
|------|------|------|
| `KAFKA_BIND_ENDPOINTS` | Kafka 集群节点（竖线分隔） | `192.168.10.2:9092\|192.168.10.3:9092` |
| `url_va` | target-detector API 地址 | `http://target-detector.default.svc.cluster.local` |
| `url_fe` | feature-extractor API 地址 | `http://feature-extractor.default.svc.cluster.local` |
| `url_reid` | feature-matcher API 地址 | `http://feature-matcher.default.svc.cluster.local` |

- 将 `url_va` 和 `url_fe` 添加到 **move-detector** 的环境配置中。
- 将 `url_reid` 添加到 **front-end** 的环境配置中。

### 步骤 3：配置存储

部署 PersistentVolume 和 PersistentVolumeClaim，将 PV 绑定到 NFS 服务器：

```bash
# 编辑 yaml/pv/reid-pv.yaml 设置 NFS 服务器地址和路径
kubectl apply -f yaml/pv/reid-pv.yaml
kubectl apply -f yaml/pvc/reid-pvc.yaml
```

### 步骤 4：更新 YAML 清单

修改 `yaml/functions/` 中的 Knative 服务定义，更新以下内容：

- 容器镜像地址
- Kafka 端点环境变量
- 函数 API 地址

### 步骤 5：部署函数

```bash
# 部署所有 Knative 服务
kubectl apply -f yaml/functions/sheduler.yaml
kubectl apply -f yaml/functions/move-detector-1.yaml
kubectl apply -f yaml/functions/target-detector-1.yaml
kubectl apply -f yaml/functions/feature-extractor.yaml
kubectl apply -f yaml/functions/feature-matcher.yaml      # 或 feature-matcher-batch.yaml
kubectl apply -f yaml/functions/front-end.yaml
```

### 步骤 6：启动监控

向 `move-detector` 发送以下请求绑定摄像头：

```bash
curl -X POST http://<move-detector-endpoint>/ \
  -H "Content-Type: application/json" \
  -d '{
    "fps": "15",
    "video_id": "cam_01",
    "video_address": "rtsp://your-camera-address"
  }'
```

### 步骤 7：查询目标

在浏览器中访问 `front-end` 服务，上传查询图片并查看重识别结果：

| 上传界面 | 查询结果 |
|:--:|:--:|
| ![上传](2.png) | ![结果](1.png) |

---

## 实验结果

### 无服务器 vs. 非无服务器

ReIDFaaS 在保持**相同的重识别精度**（Market-1501 + MSMT17 上 mAP 54.5%，Rank-1 76.0%）的同时显著提升了资源效率：

| 数据集 | mAP | Rank-1 |
|--------|-----|--------|
| Market-1501 | 68.4 | 87.2 |
| MSMT17 | 40.5 | 64.9 |
| 3DPeS（真实视频） | 88.5 | 100.0 |

<p align="center">
  <img src="assets/Throughput.png" width="380" alt="吞吐量对比"/>
  <img src="assets/ARR.png" width="380" alt="响应率对比"/>
</p>
<p align="center"><i>无服务器架构实现了 53% 的吞吐量提升和 35% 的响应延迟降低。</i></p>

### 节能调度

<p align="center">
  <img src="assets/EnergyComparison.png" width="700" alt="能量对比"/>
</p>

| 调度策略 | Agent 1 | Agent 2 | Agent 3 | **总剩余能量** |
|----------|---------|---------|---------|----------------|
| Local | 1196Wh | 264Wh | 220Wh | 1680Wh |
| K3s | 1504Wh | 264Wh | 168Wh | 1936Wh |
| Random | 1412Wh | 256Wh | 200Wh | 1868Wh |
| **ReIDFaaS** | **1624Wh** | **260Wh** | **188Wh** | **2072Wh** |

ReIDFaaS 调度器实现了**最低的标准差 (0.8%) 和极差 (1.8%)**，确保异构节点间均衡的能量消耗。

### 冷启动缓解

<p align="center">
  <img src="assets/violin.png" width="450" alt="延迟小提琴图"/>
  <img src="assets/Memory_Usage.png" width="450" alt="内存使用"/>
</p>

| 方法 | P99 延迟 | 平均内存降幅 |
|------|----------|-------------|
| 未优化 | 27.0s | 基准 |
| Keep-Alive | 24.5s | +76% 开销 |
| Pre-Warm | 25.0s | 基准 |
| **批处理（本文）** | **17.2s** | **-55%** |

---

## 技术栈

| 类别 | 技术 |
|------|------|
| **编程语言** | Python 3.8 / 3.11 |
| **深度学习** | PyTorch 2.2, TorchVision 0.17 |
| **目标检测** | YOLOX-S（行人检测） |
| **多目标跟踪** | ByteTrack |
| **行人重识别** | M3L（基于记忆的多源元学习） |
| **运动检测** | Lucas-Kanade 光流（CPU + CUDA） |
| **Web 框架** | Flask 2.2 |
| **消息队列** | Apache Kafka |
| **容器编排** | K3s（轻量级 Kubernetes） |
| **无服务器** | Knative Serving |
| **GPU 运行时** | CUDA 12.1, cuDNN 9 |
| **存储** | NFS（网络文件系统） |

---

## 引用

如果您觉得这项工作有帮助，请引用我们的论文：

```bibtex
@INPROCEEDINGS{pei2025reidfaas,
  author    = {Pei, Jianping and Shu, Yanjun and Ma, Zhuangyu and Zuo, Decheng and Zhang, Zhan},
  booktitle = {2025 IEEE International Conference on Web Services (ICWS)},
  title     = {ReIDFaaS: An Energy-Efficient Serverless Person Re-Identification System Across the Edge-Cloud Continuum},
  year      = {2025},
  pages     = {365-371},
  doi       = {10.1109/ICWS67624.2025.00052}
}
```

---

## 致谢

本研究受以下项目资助：
- 国家重点研发计划（项目编号：2024YFB4506003）
- 国家自然科学基金（项目编号：61202091、62171155）

---

## 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。
