<div align="center">

# ReIDFaaS

### An Energy-Efficient Serverless Person Re-Identification System Across the Edge-Cloud Continuum

[![Paper](https://img.shields.io/badge/IEEE-ICWS%202025-blue)](https://ieeexplore.ieee.org/document/11169601/)
[![Knative](https://img.shields.io/badge/Knative-Serverless-0865AD?logo=knative&logoColor=white)](https://knative.dev/)
[![K3s](https://img.shields.io/badge/K3s-Kubernetes-FFC61C?logo=k3s&logoColor=white)](https://k3s.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Paper](https://ieeexplore.ieee.org/document/11169601/) |
[Project Page](https://jianpingpei.github.io/Energy-Efficient-ReIDFaaS/) |
[Code](https://github.com/jianpingpei/Energy-Efficient-ReIDFaaS)

**[中文版本 (Chinese Version)](README_CN.md)**

</div>

---

## Overview

**ReIDFaaS** is a serverless person re-identification (Re-ID) system designed for energy-efficient, low-latency operation across the edge-cloud continuum. It replaces traditional always-on surveillance pipelines with an event-driven architecture triggered by pedestrian movement, significantly reducing resource consumption on energy-constrained edge devices.

Published at **IEEE International Conference on Web Services (ICWS) 2025**.

---

## Highlights

<table>
<tr>
<td align="center"><b>23.3%</b><br/>Edge Node Availability<br/>Improvement</td>
<td align="center"><b>55%</b><br/>Memory Usage<br/>Reduction</td>
<td align="center"><b>53%</b><br/>Throughput<br/>Improvement</td>
<td align="center"><b>30%</b><br/>P99 Latency<br/>Reduction</td>
</tr>
</table>

---

## Key Contributions

1. **Event-Driven Re-ID Workflow**
   An event-driven Re-ID system replacing continuous computation with pedestrian movement-triggered execution, significantly reducing resource usage while maintaining real-time performance.

2. **Energy-Efficient Scheduling**
   A hardware-aware dynamic scheduler that allocates tasks based on real-time energy states, hot container availability, and load constraints, improving edge node availability by 23.3%.

3. **Adaptive Batching for Cold-Start Mitigation**
   An adaptive batching mechanism that reduces cold-start frequency through latency-constrained request grouping, reducing 99th percentile latency by 30% and average memory usage by 55%.

---

## System Architecture

ReIDFaaS employs a three-tier edge-cloud architecture (Data Source, Edge, Cloud) with Kafka for data streaming and NFS for persistent storage. Knative on K3s enables serverless auto-scaling and event-driven execution.

<p align="center">
  <img src="assets/Architecture.png" width="600" alt="ReIDFaaS System Architecture"/>
</p>

The system consists of five core serverless functions:

| Function | Layer | Description |
|----------|-------|-------------|
| **move-detector** | Edge | Captures camera streams and detects pedestrian movement via Lucas-Kanade optical flow |
| **target-detector** | Edge | Pedestrian detection and tracking using YOLOX + ByteTrack |
| **feature-extractor** | Cloud | Extracts ReID appearance features using M3L model |
| **feature-matcher** | Cloud | Matches query features against candidates via cosine similarity |
| **front-end** | Edge | Web interface for uploading query images and viewing results |

---

## Workflow

<p align="center">
  <img src="assets/work-flow.png" width="800" alt="ReIDFaaS Workflow"/>
</p>

The 15-step workflow operates as follows:

1. **Movement Detection (Steps 1-2)**: `move-detector` processes video streams, detects pedestrian movement, activates downstream functions, and sends relevant frames to Kafka.
2. **Target Detection (Steps 3-4)**: `target-detector` uses YOLOX + ByteTrack for pedestrian detection and tracking, outputs bounding boxes to Kafka.
3. **Feature Extraction (Steps 5-6)**: `feature-extractor` uses M3L to extract appearance features, stores results to NFS.
4. **Query Initialization (Steps 7-8)**: User uploads query images via `front-end`, triggering `feature-matcher`.
5. **Feature Matching (Steps 9-13)**: `feature-matcher` obtains query features, matches against historical features on NFS, writes results.
6. **Result Visualization (Steps 14-15)**: `front-end` reads results from NFS and displays them to the user.

---

## Project Structure

```
Energy-Efficient-ReIDFaaS/
├── common/                         # Shared utilities
│   ├── BaseService.py              # Abstract base service (Kafka + queue)
│   ├── DetTrackResult.py           # Data objects for detection/tracking results
│   ├── Get_Param.py                # Environment variable parameter fetcher
│   ├── Logger.py                   # Colored logging utility
│   └── kafka/                      # Kafka consumer/producer wrappers
├── move-detector/                  # Motion detection function
│   ├── move-detector.py            # Flask app (port 3001)
│   └── optical_flow.py             # Lucas-Kanade optical flow (CPU + CUDA)
├── target-detector/                # Object detection + tracking
│   ├── target-detector.py          # Flask app (port 4001)
│   ├── model/bytetracker.py        # ByteTracker with YOLOX
│   └── yolox/                      # YOLOX framework
├── feature-extractor/              # Feature extraction function
│   ├── feature-extractor.py        # Flask app (port 6001)
│   └── M3L/                        # M3L ReID model architecture
├── feature-matcher/                # Single-request feature matching
│   ├── feature-matcher.py          # Flask app (port 5001)
│   ├── multi_img_matching.py       # Cosine similarity matching
│   └── store_result.py             # Save annotated result images
├── feature-matcher-batch/          # Batch feature matching
│   ├── feature-matcher-batch.py    # Flask app (port 5001) with adaptive batching
│   ├── multi_img_matching.py       # Batch matching logic
│   └── store_result.py             # Save annotated result images
├── front-end/                      # Web UI function
│   ├── front-end.py                # Flask app (port 8080)
│   └── templates/result.html       # Result display template
├── scheduler/                      # Energy-aware task scheduler
│   └── scheduler.py                # Priority-based node selection (port 2001)
├── models/                         # Pre-trained model weights
│   ├── m3l.pth                     # M3L ReID model
│   └── yolox.pth                   # YOLOX pedestrian detection
├── yaml/                           # Kubernetes/Knative manifests
│   ├── functions/                  # Knative service definitions
│   ├── pv/                         # PersistentVolume (NFS)
│   └── pvc/                        # PersistentVolumeClaim
├── *.Dockerfile                    # Container images
├── assets/                         # Figures from the paper
└── docs/                           # Project homepage
```

---

## Prerequisites

Before deploying ReIDFaaS, ensure the following infrastructure is ready:

| Component | Description |
|-----------|-------------|
| **K3s** | Lightweight Kubernetes cluster with 1 master + N agent nodes |
| **Knative** | Serverless framework installed on K3s for auto-scaling |
| **Apache Kafka** | Distributed message queue cluster |
| **NFS** | Network File System for shared persistent storage |
| **Docker** | Container runtime for building images |
| **NVIDIA GPU** (optional) | For GPU-accelerated inference on edge/cloud nodes |

### Hardware Requirements (Reference Testbed)

| Node | CPU | GPU | Memory | Role |
|------|-----|-----|--------|------|
| Master | 32 cores | NVIDIA RTX 3080Ti | 256GB | Control plane + feature-matcher + feature-extractor |
| Agent 1 | 8 cores | NVIDIA RTX 1080Ti | 32GB | Edge node (5 cameras) |
| Agent 2 | 4 cores | None | 16GB | Edge node (1 camera) |
| Agent 3 | 8 cores | 32 Tensor cores (Jetson Orin NX) | 16GB | Edge node (2 cameras) |

---

## Deployment

### Step 1: Build Docker Images

Build container images for each function using the provided Dockerfiles:

```bash
# GPU functions (require CUDA runtime)
docker build -f target-detector-gpu.Dockerfile -t <registry>/target-detector:latest .
docker build -f feature-extractor-gpu.Dockerfile -t <registry>/feature-extractor:latest .
docker build -f feature-matcher-gpu.Dockerfile -t <registry>/feature-matcher:latest .
# or batch version
docker build -f feature-matcher-batch-gpu.Dockerfile -t <registry>/feature-matcher-batch:latest .

# CPU functions
docker build -f move-detector.Dockerfile -t <registry>/move-detector:latest .
docker build -f front-end.Dockerfile -t <registry>/front-end:latest .
docker build -f scheduler.Dockerfile -t <registry>/scheduler:latest .

# Push to your registry
docker push <registry>/target-detector:latest
# ... push all images
```

### Step 2: Configure Environment Variables

Identify the API addresses for the key functions and configure them in the YAML files:

| Variable | Description | Example |
|----------|-------------|---------|
| `KAFKA_BIND_ENDPOINTS` | Kafka cluster nodes (pipe-separated) | `192.168.10.2:9092\|192.168.10.3:9092` |
| `url_va` | target-detector API address | `http://target-detector.default.svc.cluster.local` |
| `url_fe` | feature-extractor API address | `http://feature-extractor.default.svc.cluster.local` |
| `url_reid` | feature-matcher API address | `http://feature-matcher.default.svc.cluster.local` |

- Add `url_va` and `url_fe` to **move-detector**'s environment configuration.
- Add `url_reid` to **front-end**'s environment configuration.

### Step 3: Configure Storage

Deploy PersistentVolume and PersistentVolumeClaim, binding PV to your NFS server:

```bash
# Edit yaml/pv/reid-pv.yaml to set your NFS server address and path
kubectl apply -f yaml/pv/reid-pv.yaml
kubectl apply -f yaml/pvc/reid-pvc.yaml
```

### Step 4: Update YAML Manifests

Modify the Knative service definitions in `yaml/functions/` to update:

- Container image addresses
- Kafka endpoint environment variables
- Function API addresses

### Step 5: Deploy Functions

```bash
# Deploy all Knative services
kubectl apply -f yaml/functions/sheduler.yaml
kubectl apply -f yaml/functions/move-detector-1.yaml
kubectl apply -f yaml/functions/target-detector-1.yaml
kubectl apply -f yaml/functions/feature-extractor.yaml
kubectl apply -f yaml/functions/feature-matcher.yaml      # or feature-matcher-batch.yaml
kubectl apply -f yaml/functions/front-end.yaml
```

### Step 6: Start Surveillance

Bind a camera to `move-detector` by sending:

```bash
curl -X POST http://<move-detector-endpoint>/ \
  -H "Content-Type: application/json" \
  -d '{
    "fps": "15",
    "video_id": "cam_01",
    "video_address": "rtsp://your-camera-address"
  }'
```

### Step 7: Query Targets

Access the `front-end` service in your browser to upload query images and view Re-ID results:

| Upload Interface | Query Results |
|:--:|:--:|
| ![Upload](2.png) | ![Results](1.png) |

---

## Experimental Results

### Serverless vs. Non-Serverless

ReIDFaaS achieves **identical Re-ID accuracy** (mAP 54.5%, Rank-1 76.0% on Market-1501 + MSMT17) while significantly improving resource efficiency:

| Dataset | mAP | Rank-1 |
|---------|-----|--------|
| Market-1501 | 68.4 | 87.2 |
| MSMT17 | 40.5 | 64.9 |
| 3DPeS (real video) | 88.5 | 100.0 |

<p align="center">
  <img src="assets/Throughput.png" width="380" alt="Throughput Comparison"/>
  <img src="assets/ARR.png" width="380" alt="ARR Comparison"/>
</p>
<p align="center"><i>Serverless achieves 53% higher throughput and 35% lower response latency.</i></p>

### Energy-Efficient Scheduling

<p align="center">
  <img src="assets/EnergyComparison.png" width="700" alt="Energy Comparison"/>
</p>

| Scheduler | Agent 1 | Agent 2 | Agent 3 | **Total Remaining** |
|-----------|---------|---------|---------|---------------------|
| Local | 1196Wh | 264Wh | 220Wh | 1680Wh |
| K3s | 1504Wh | 264Wh | 168Wh | 1936Wh |
| Random | 1412Wh | 256Wh | 200Wh | 1868Wh |
| **ReIDFaaS** | **1624Wh** | **260Wh** | **188Wh** | **2072Wh** |

ReIDFaaS scheduler achieves the **lowest SD (0.8%) and range (1.8%)** in operational availability, ensuring balanced energy consumption across heterogeneous nodes.

### Cold-Start Mitigation

<p align="center">
  <img src="assets/violin.png" width="450" alt="Latency Violin Plot"/>
  <img src="assets/Memory_Usage.png" width="450" alt="Memory Usage"/>
</p>

| Method | P99 Latency | Avg Memory Reduction |
|--------|-------------|---------------------|
| Non-Optimized | 27.0s | baseline |
| Keep-Alive | 24.5s | +76% overhead |
| Pre-Warm | 25.0s | baseline |
| **Batch (Ours)** | **17.2s** | **-55%** |

---

## Tech Stack

| Category | Technologies |
|----------|-------------|
| **Language** | Python 3.8 / 3.11 |
| **Deep Learning** | PyTorch 2.2, TorchVision 0.17 |
| **Detection** | YOLOX-S (pedestrian detection) |
| **Tracking** | ByteTrack (multi-object tracking) |
| **ReID** | M3L (Memory-based Multi-source Meta-Learning) |
| **Motion Detection** | Lucas-Kanade Optical Flow (CPU + CUDA) |
| **Web Framework** | Flask 2.2 |
| **Message Queue** | Apache Kafka |
| **Container Orchestration** | K3s (lightweight Kubernetes) |
| **Serverless** | Knative Serving |
| **GPU Runtime** | CUDA 12.1, cuDNN 9 |
| **Storage** | NFS (Network File System) |

---

## Citation

If you find this work useful, please cite our paper:

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

## Acknowledgments

This research is supported by:
- National Key Research and Development Program of China (Grant No. 2024YFB4506003)
- National Natural Science Foundation of China (Grant Nos. 61202091, 62171155)

---

## License

This project is licensed under the [MIT License](LICENSE).
