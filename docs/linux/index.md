# 🐧 Linux 专业文档中心

<div class="linux-hero">
  <h2>开源操作系统的基石与核心</h2>
  <p><strong>稳定 • 安全 • 高效 • 自由</strong></p>
</div>

<style>
.linux-hero {
    background: linear-gradient(135deg, #303f9f 0%, #5c6bc0 100%);
    color: white;
    padding: 3rem 1rem;
    border-radius: 12px;
    margin: 1.5rem 0;
    text-align: center;
    box-shadow: 0 8px 32px rgba(48, 63, 159, 0.3);
}

.grid-cards-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.card-item {
    background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 10px;
    padding: 1.5rem;
    text-align: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border: 1px solid #dee2e6;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.card-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.1);
    background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
}

.card-item h3 {
    margin-top: 0;
    color: #333;
    font-size: 1.25rem;
    margin-bottom: 0.75rem;
}

.card-item p {
    color: #666;
    margin-bottom: 1.5rem;
    line-height: 1.5;
}

.btn {
    display: inline-block;
    padding: 0.5rem 1rem;
    background-color: #303f9f;
    color: white;
    text-decoration: none;
    border-radius: 6px;
    transition: background-color 0.3s ease;
    border: none;
    cursor: pointer;
    font-size: 0.9rem;
}

.btn:hover {
    background-color: #283593;
    color: white;
}

.md-typeset .mermaid {
    text-align: center;
    margin: 1.5rem 0;
}

.md-typeset table:not([class]) {
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    border-radius: 8px;
    overflow: hidden;
}

.md-typeset h2, .md-typeset h3 {
    color: #303f9f;
}

.md-typeset blockquote {
    background-color: #e8eaf6;
    border-left-color: #5c6bc0;
}

.md-typeset blockquote > :first-child {
    margin-top: 0;
}

.md-typeset blockquote > :last-child {
    margin-bottom: 0;
}

@media (max-width: 768px) {
    .grid-cards-container {
        grid-template-columns: 1fr;
    }
    
    .linux-hero {
        padding: 1.5rem 0.5rem;
    }
}
</style>

---

## 📚 快速导航

<div class="grid-cards-container">
  <div class="card-item">
    <h3>🔧 系统管理工具</h3>
    <p>常用的 Linux 系统管理工具与实用程序。</p>
    <a href="./tools" class="btn">详情</a>
  </div>
  
  <div class="card-item">
    <h3>💻 KVM 虚拟化</h3>
    <p>KVM 虚拟化平台配置与管理指南。</p>
    <a href="./kvm01" class="btn">详情</a>
  </div>
  
  <div class="card-item">
    <h3>📦 数据恢复</h3>
    <p>使用 ddrescue 进行数据恢复的技术说明。</p>
    <a href="./ddrescue" class="btn">详情</a>
  </div>
  
  <div class="card-item">
    <h3>🔐 安全管理</h3>
    <p>Linux 系统安全管理与防护实践。</p>
    <a href="./webmanage" class="btn">详情</a>
  </div>
  
  <div class="card-item">
    <h3>🔍 硬件监控</h3>
    <p>利用 smartctl 和 ipmitool 监控硬件健康状态。</p>
    <a href="./smartctl" class="btn">详情</a>
  </div>
  
  <div class="card-item">
    <h3>🧩 ELF 工具</h3>
    <p>elfutil 等二进制文件处理工具详解。</p>
    <a href="./elfutil" class="btn">详情</a>
  </div>
  
  <div class="card-item">
    <h3>🔧 补丁管理</h3>
    <p>Linux 系统补丁管理与更新流程。</p>
    <a href="./patch" class="btn">详情</a>
  </div>
  
  <div class="card-item">
    <h3>ernetes K8s 工具</h3>
    <p>kuberctl 等 Kubernetes 管理工具使用指南。</p>
    <a href="./kuberctl" class="btn">详情</a>
  </div>
</div>

---

## Linux 系统概述

Linux 是一套免费使用和自由传播的类 UNIX 操作系统，是一个基于 POSIX 的多用户、多任务、支持多线程和多 CPU 的操作系统。它能运行主要的 UNIX 工具软件、应用程序和网络协议，并支持 32 位和 64 位硬件。Linux 继承了 Unix 以网络为核心的设计思想，是一个性能稳定的多用户计算机操作系统。

本文档集合涵盖了 Linux 系统的各个方面，从基础的系统管理到高级系统配置，以及特定的运维实践。

### 核心组成部分

- **系统管理**: 系统监控、进程管理、服务配置等基础知识
- **虚拟化技术**: KVM 等虚拟化平台的应用
- **硬件管理**: 利用专用工具进行硬件监控和维护
- **安全管控**: 权限管理、访问控制和安全加固
- **集群管理**: Kubernetes 等容器编排技术
- **应急维护**: 数据恢复、系统补丁等维护任务

## 系统资源

### Linux 工具与实用程序总览

涵盖常用的命令行工具，以及在运维场景中使用的重要工具如 ddrescue 用于数据恢复，elfutil 进行 ELF 文件分析等。

### 系统维护

- KVM 虚拟化技术的安装和配置
- 系统补丁管理的正确流程和注意事项
- 利用 smartctl 和 ipmitool 进行硬件监控

### 相关主题文章

- Web 管理与系统安全设置
- kuberctl 与容器编排实践
- 硬件级管理和 IPMI 工具的应用

> ⭐ 深入掌握 Linux 运维技能，从基础配置到企业级实践，可参阅以上各个专题章节
