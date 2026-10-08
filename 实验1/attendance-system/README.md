# 签到系统

这是软件工程实验一的本地演示项目，使用 Flask、SQLite 和 HTML/CSS 实现。系统仅监听 `127.0.0.1`，适合单机实验；没有用户登录和公网部署能力。

## 功能

- 创建签到活动，并查看各活动签到人数。
- 输入学号、姓名完成签到，自动记录本机时间与时区。
- 同一活动中同一学号只允许签到一次；学号大小写统一处理。
- 按学号或姓名查询签到记录。
- 导出带 UTF-8 BOM 的 CSV，便于电子表格软件打开。

## 环境与运行

需要 Python 3.12 或兼容版本。Windows PowerShell 示例：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

浏览器访问 <http://127.0.0.1:5000>。其他系统先激活虚拟环境，再运行 `python -m pip install -r requirements.txt` 和 `python app.py`。

数据库自动创建在 `instance/attendance.sqlite3`。`instance/` 已加入 `.gitignore`，本地数据不会提交到仓库。

## 验证

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

测试覆盖创建活动、签到、防重复、查询、导出、输入校验和不存在的活动。

## 演示数据

实验截图使用虚构数据，例如活动“软件工程实验一签到”、学号 `S001` 和姓名“测试学生”。请勿在公开仓库中提交真实学号或个人签到数据。
