# 🏠 技术文档中心

<div class="home-hero">
  <h2>综合技术资源文档中心</h2>
  <p><strong>开源 • 专业 • 全面 • 实用</strong></p>
</div>

<style>
.home-hero {
    background: linear-gradient(135deg, #1e88e5 0%, #64b5f6 100%);
    color: white;
    padding: 3rem 1rem;
    border-radius: 12px;
    margin: 1.5rem 0;
    text-align: center;
    box-shadow: 0 8px 32px rgba(30, 136, 229, 0.3);
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
    box-shadow: 0 12px 24px rgba(30, 136, 229, 0.15);
    background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
}

.card-item h3 {
    margin-top: 0;
    color: #1e88e5;
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
    background-color: #1e88e5;
    color: white;
    text-decoration: none;
    border-radius: 6px;
    transition: background-color 0.3s ease;
    border: none;
    cursor: pointer;
    font-size: 0.9rem;
}

.btn:hover {
    background-color: #0d47a1;
    color: white;
}

.md-typeset .mermaid {
    text-align: center;
    margin: 1.5rem 0;
}

.md-typeset table:not([class]) {
    box-shadow: 0 4px 6px rgba(30, 136, 229, 0.05);
    border-radius: 8px;
    overflow: hidden;
}

.md-typeset h2, .md-typeset h3 {
    color: #1e88e5;
}

.md-typeset blockquote {
    background-color: #e3f2fd;
    border-left-color: #1e88e5;
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
    
    .home-hero {
    padding: 1.5rem 0.5rem;
  }
}

/* 新增样式 */
.overview-section {
    margin: 3rem 0;
    padding: 2rem 1rem;
}

.overview-section h2 {
    text-align: center;
    margin-bottom: 2rem;
    color: var(--md-primary-fg-color);
    font-size: 1.8rem;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1.5rem;
    margin-top: 1.5rem;
}

.feature-card {
    background: linear-gradient(145deg, var(--md-default-bg-color) 0%, #f8f9fa 100%);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border: 1px solid rgba(0,0,0,0.08);
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    position: relative;
    overflow: hidden;
    z-index: 1;
}

.feature-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(145deg, transparent, rgba(var(--md-rgb-accent-fg-color), 0.05));
    z-index: -1;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.feature-card:hover::before {
    opacity: 1;
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    border-color: rgba(var(--md-rgb-accent-fg-color), 0.3);
}

.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.feature-card h3 {
    margin: 0 0 0.75rem 0;
    color: var(--md-primary-fg-color);
    font-size: 1.25rem;
}

.feature-card p {
    color: var(--md-default-fg-color--light);
    margin: 0;
    line-height: 1.6;
}

.subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
    margin: 1rem 0 0;
}
</style>

---

## 📚 快速导航

<div class="grid-cards-container">
  <div class="card-item">
    <h3>🐘 PostgreSQL</h3>
    <p>功能强大的开源对象关系型数据库系统，注重可靠性和标准兼容性。</p>
    <a href="./postgres/" class="btn">立即查看</a>
  </div>
  
  <div class="card-item">
    <h3>🐬 MySQL</h3>
    <p>世界最受欢迎的开源关系型数据库管理系统，以性能和易用性著称。</p>
    <a href="./mysql/" class="btn">立即查看</a>
  </div>
  
  <div class="card-item">
    <h3>🧩 中间件</h3>
    <p>分布式系统的核心组件，包含监控、存储和其他关键中间件技术。</p>
    <a href="./middleware/" class="btn">立即查看</a>
  </div>
  
  <div class="card-item">
    <h3>🐧 Linux</h3>
    <p>企业级操作系统平台与服务器管理，包含运维指南和最佳实践。</p>
    <a href="./linux/" class="btn">立即查看</a>
  </div>
</div>

---

## 技术中心概览

本文档中心提供多种主流技术栈的专业文档，涵盖了数据库、中间件及操作系统等核心技术领域，致力于为开发者和运维人员提供全方位的技术支持和学习资源。

### 技术分类导航

- **PostgreSQL**：功能强大、符合 SQL 标准的对象关系型数据库
- **MySQL**：广泛使用的关系型数据库管理系统，性能卓越
- **中间件**：构建分布式系统的关键组件和服务
- **Linux**：服务器操作系统与系统管理运维实践

### 知识体系框架

文档中心围绕以下技术领域构建：

**数据库技术**

- 安装部署与初始化配置
- 性能调优与查询优化
- 高可用架构与容灾设计
- 安全管理与权限控制
- 备份恢复与数据迁移

**中间件系统**

- 服务治理与消息队列
- 监控告警与日志分析
- 分布式缓存与网关管理
- 容器编排与云原生技术

**系统运维**

- Linux 操作系统优化
- 虚拟化与云计算平台管理
- 网络安全与策略配置
- 自动化运维与工具实践

## 资源特色

平台整合了多个主流开源技术的实践经验和最佳实践，帮助用户快速解决实际工作中的问题，同时促进技术团队的交流与发展。每类技术都提供了从入门到进阶的完整知识路径，支持用户的持续成长。

> ⭐ 开始您的技术探索之旅，从左侧导航栏或上方分类卡片选择感兴趣的主题深入了解
