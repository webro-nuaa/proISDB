# InsertQ 数据库设计

## 项目简介

InsertQ 是一个专门用于存储和管理 IS 元素（插入序列）数据的网站数据库系统。该系统支持数据搜索、科普知识管理、用户数据提交以及管理员审核等功能。

## 功能模块

### 访客端功能
1. **搜索功能** - 对 IS 元素数据进行全文搜索，查看详细信息
2. **科普知识** - 浏览由管理员发布的科普文章
3. **数据提交** - 提交新的 IS 元素数据，等待审核
4. **关于我们** - 网站介绍和联系信息

### 管理员端功能
1. **数据审核** - 审核用户提交的数据
2. **批量导入** - 通过 Excel 文件批量导入数据
3. **内容管理** - 发布和管理科普文章
4. **用户管理** - 管理用户账户和权限
5. **统计分析** - 查看网站访问和使用统计

## 数据库结构

### 核心表结构

#### 1. 用户管理
- `users` - 用户信息表（管理员、访客）

#### 2. IS 元素数据
- `is_elements` - IS 元素主表（包含所有核心数据字段）
- `submission_history` - 数据提交历史
- `batch_imports` - 批量导入记录

#### 3. 内容管理
- `knowledge_categories` - 知识分类
- `knowledge_articles` - 科普文章
- `knowledge_tags` - 文章标签
- `article_tags` - 文章标签关联

#### 4. 系统管理
- `search_logs` - 搜索日志
- `page_views` - 访问统计
- `system_configs` - 系统配置
- `admin_logs` - 管理员操作日志

## 安装和使用

### 1. 环境要求

- Python 3.7+
- MySQL 5.7+ 或 MariaDB 10.2+
- 必需的 Python 包：
  ```bash
  conda activate ple  # 激活你的 conda 环境
  # pandas 和 openpyxl 已在环境中可用
  pip install mysql-connector-python  # 如果需要的话
  ```

### 2. 数据库初始化

1. **修改数据库配置**
   编辑 `setup_database.py` 和 `import_sample_data.py` 中的数据库连接配置：
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'your_username',
       'password': 'your_password',
       'charset': 'utf8mb4'
   }
   ```

2. **创建数据库和表**
   ```bash
   python setup_database.py
   ```

3. **导入示例数据**
   ```bash
   python import_sample_data.py
   ```

### 3. 数据字段说明

基于示例数据，主要字段包括：

| 字段名 | 说明 | 类型 |
|--------|------|------|
| name | IS 元素名称 | VARCHAR(100) |
| family | IS 家族 | VARCHAR(100) |
| group_name | IS 组 | VARCHAR(100) |
| host | 宿主生物 | VARCHAR(200) |
| is_length | IS 长度 | INT |
| dna_sequence | DNA 序列 | LONGTEXT |
| orf_function | ORF 功能 | TEXT |
| comment | 备注信息 | TEXT |
| status | 审核状态 | ENUM('pending', 'approved', 'rejected') |

### 4. 主要功能实现

#### 搜索功能
- 使用全文索引支持多字段搜索
- 支持按家族、宿主、功能等条件筛选
- 记录搜索日志用于分析

#### 数据提交和审核
- 新提交数据默认状态为 `pending`
- 管理员可以批准（`approved`）或拒绝（`rejected`）
- 完整的审核历史记录

#### 批量导入
- 支持 Excel 文件格式
- 自动数据清理和验证
- 导入进度和错误记录

## 安全考虑

1. **用户认证** - 密码哈希存储
2. **权限控制** - 基于角色的访问控制
3. **数据验证** - 输入数据长度和格式验证
4. **操作日志** - 完整的管理员操作记录

## 性能优化

1. **索引优化** - 为常用查询字段创建索引
2. **全文搜索** - MySQL 全文索引支持
3. **分页查询** - 避免大数据量查询
4. **视图优化** - 预定义常用统计查询

## 扩展建议

1. **API 接口** - 可考虑添加 RESTful API
2. **数据导出** - 支持多种格式数据导出
3. **高级搜索** - 序列比对和相似性搜索
4. **数据可视化** - IS 元素分布图表
5. **版本控制** - 数据变更版本管理

## 维护建议

1. **定期备份** - 设置自动数据库备份
2. **日志清理** - 定期清理过期的访问日志
3. **性能监控** - 监控数据库查询性能
4. **数据完整性** - 定期检查数据一致性

## 文件说明

- `database_schema.sql` - 完整的数据库结构定义
- `setup_database.py` - 数据库初始化脚本
- `import_sample_data.py` - 示例数据导入脚本
- `read_excel.py` - Excel 文件读取工具
- `示例数据.xlsx` - 原始示例数据
- `示例数据_converted.csv` - 转换后的 CSV 数据

## 联系方式

如有问题或建议，请联系开发团队。
