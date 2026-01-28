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
    <h3>🔧 基础工具与系统管理</h3>
    <p>常用系统管理工具、性能监控与系统配置等。</p>
    <a href="./tools" class="btn">系统工具</a>
  </div>
  
  <div class="card-item">
    <h3>💻 虚拟化与容器技术</h3>
    <p>KVM虚拟化平台与Kubernetes容器管理。</p>
    <a href="./kvm01" class="btn">KVM虚拟化</a>
  </div>
  
  <div class="card-item">
    <h3>💾 数据恢复与备份</h3>
    <p>使用ddrescue等工具进行数据恢复的指南。</p>
    <a href="./ddrescue" class="btn">数据恢复</a>
  </div>
  
  <div class="card-item">
    <h3>🔐 安全与权限管理</h3>
    <p>用户权限、安全管理和认证等知识。</p>
    <a href="./webmanage" class="btn">安全管理</a>
  </div>
  
  <div class="card-item">
    <h3>Hardware 硬件与驱动管理</h3>
    <p>硬件监控、设备管理和驱动配置说明。</p>
    <a href="./smartctl" class="btn">硬件监控</a>
  </div>
  
  <div class="card-item">
    <h3>⚙️ 系统配置与调优</h3>
    <p>系统参数优化和内核性能调优实践。</p>
    <a href="./linux_tunning" class="btn">系统调优</a>
  </div>
  
  <div class="card-item">
    <h3>📁 存储与文件系统</h3>
    <p>LVM存储管理与文件系统操作。</p>
    <a href="./lvm" class="btn">存储管理</a>
  </div>
  
  <div class="card-item">
    <h3>Network 网络与协议</h3>
    <p>网络分析、协议分析和网络监控。</p>
    <a href="./tcpdump" class="btn">网络分析</a>
  </div>

  <div class="card-item">
    <h3>Linux 学习</h3>
    <p>一个linux学习的网站</p>
    <a href="https://www.tecmint.com/" class="btn">linux</a>
  </div>
</div>

---

## Linux 系统概述

Linux 是一套免费使用和自由传播的类 UNIX 操作系统，是一个基于 POSIX 的多用户、多任务、支持多线程和多 CPU 的操作系统。它能运行主要的 UNIX 工具软件、应用程序和网络协议，并支持 32 位和 64 位硬件。Linux 继承了 Unix 以网络为核心的设计思想，是一个性能稳定的多用户计算机操作系统。

本文档集合涵盖了 Linux 系统的各个方面，从基础的系统管理到高级系统配置，以及特定的运维实践。

### 核心组成部分

- **基础系统管理**: 包含常用系统工具、进程管理、性能监控、内存管理和磁盘管理等核心技能
- **命令行应用**: 各种常用命令和实用工具的使用详解，包括 awk、sed、vim、xargs 等经典命令
- **虚拟化与容器**: KVM 虚拟化技术和 K8s 容器编排工具的应用和管理
- **硬件管理**: 利用 smartctl、ipmitool 等工具对硬件设备进行监控和维护
- **安全管控**: 权限管理、用户管理、免密登录配置等安全相关主题
- **系统调优**: 性能参数配置、网络调优、系统启动优化等方面的深度实践
- **存储与文件系统**: LVM 存储管理、磁盘分区管理以及文件系统优化等内容
- **网络分析**: 网络协议分析、抓包工具使用及网络安全等方面的内容
- **数据恢复与备份**: 重要数据保护和恢复策略的实施指南
- **调试与问题排查**: 通过各种工具和技术对系统问题进行分析与解决

## 技术资源

我们提供了全面的 Linux 系统管理技术资源，覆盖了从入门到进阶的不同层次需求，旨在帮助用户深入理解和高效应用 Linux 技术。

## 深入学习路径

您可以按照文档分类逐步学习 Linux 知识：

1. **初学者**: 从系统工具、命令详解入手
2. **进阶者**: 掌握系统调优、网络分析和安全策略
3. **专业人员**: 深入虚拟化、容器、存储和性能优化领域

> ⭐ 深入掌握 Linux 运维技能，从基础配置到企业级实践，可参阅左侧菜单中的各个专题章节
