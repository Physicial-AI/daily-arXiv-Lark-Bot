我正在寻找关于 **具身智能** (Embodied AI) 领域中 **视觉-语言-动作模型** (VLA) 与 **机器人操控** (Manipulation) 相关的论文。重点关注以下研究方向（**包括但不限于**）：

## VLA 模型与基础模型 (Foundation Models for Robotics)

- 视觉-语言-动作（VLA）大模型的架构设计
- 预训练基础模型在具身任务中的迁移与应用

## 机器人操控 (Manipulation) 核心技术

- 精细操作、双手协同、长程任务规划（Long-horizon tasks）
- 基于视觉或触觉反馈的闭环操控策略

## 学习方法与后训练 (Learning & Post-training)

- **强化学习 (RL)**：包括离线强化学习 (Offline RL)、在线微调及高效采样策略
- **后训练技术 (Post-train)**：如针对动作策略的指令微调 (SFT)、人类反馈强化学习 (RLHF) 或自监督对齐

## 数据驱动与基础设施

- **大规模数据集 (Dataset)**：跨机器人、跨场景的动作数据集
- **人类数据 (Human Data)**：通过遥操作 (Teleoperation)、VR 或人类视频学习 (Learning from Demonstration) 获取的数据
- **仿真环境 (Simulation)**：高保真物理仿真、Sim-to-Real 迁移、自动合成数据技术

## 生成式模型与世界模型

- **世界模型 (World Model)**：用于预测环境变化和物理演化的动力学模型
- **视频模型 (Video Model)**：利用视频生成模型（如 Diffusion/Transformer）进行动作预测或数据增强

## 系统优化与效率 (Efficient Methods)

- 具身模型的量化、剪枝及实时推理优化
- 高效的微调方法（如 LoRA, Adapter）在机器人上的应用

## 多任务融合与协同 (Hybrid Tasks)

- **Manipulation + Locomotion**：全身协同控制（Whole-body control）
- **Manipulation + Navigation**：移动操控（Mobile Manipulation），即机器人在导航过程中的交互与操作

---

相关研究可能包括但不限于：新的算法架构、训练范式、基准测试 (Benchmark)、硬件适配方案以及提升泛化性/鲁棒性的实验研究。
