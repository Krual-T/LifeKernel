---
name: windows-task-scheduler-reminders
description: 在 Windows 中创建/管理定时提醒（通知方式）。适用于用户要求“定时提醒/到点提醒/每天提醒/每周提醒”等，并需在创建计划任务前征求确认。默认使用 BurntToast 通知（当前用户会话）。
---

# Windows 定时提醒（通知）

## 概述

使用 Windows 计划任务（Task Scheduler）创建提醒。提醒方式默认为 **BurntToast 通知**；频率与时间由对话确定。创建前必须确认。默认在**当前用户会话**运行，保证通知可见。

## 关键信息收集（创建前）

- 提醒内容：标题/正文
- 触发时间：具体日期时间、每天/每周/工作日等
- 频率：按对话自定义
- 失败处理：错过提醒是否需要补发

## 流程

1. 收集参数并复述
   - 复述提醒内容与时间
   - 明确频率与时区

2. 确认创建
   - 必须询问“是否创建该提醒任务”

3. 创建计划任务（确认后）
   - 使用 PowerShell 或 `schtasks` 创建任务
   - 记录任务名称（建议规则：`reminder-YYYYMMDD-HHMM-<slug>`）
   - **默认使用当前用户会话运行**（不要用 SYSTEM）
   - 通用脚本使用 `scripts/notify.ps1`

4. 回执
   - 告知已创建任务名称与触发时间
   - 如需，展示删除/更新方法

## 脚本

- `scripts/notify.ps1`：通用通知脚本（参数 `-Title`、`-Body`）
  - 内部自动安装/导入 BurntToast
  - 失败时回退为 `msg`

**示例脚本（写在文档中，不作为脚本文件存放）：**

```powershell
$scriptPath = Join-Path $PSScriptRoot 'notify.ps1'
& $scriptPath -Title '提醒' -Body '12点发送文件给导师（戚荣志）'
```

## 记录路径（避免误写）

- 所有操作记录写入：`workspace/lifelog/YYYY/MM/DD.jsonl`
- 任务清单与完成记录路径以 `tasks-daily-jsonl` 为准

## 通用命令模板（当前用户会话）

```
$taskName = "reminder-YYYYMMDD-HHMM-<slug>"
$tr = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\Projects\LifeKernel\.codex\skills\windows-task-scheduler-reminders\scripts\notify.ps1" -Title "提醒" -Body "<内容>"'
cmd /c "schtasks /Create /SC ONCE /TN \"$taskName\" /TR \"$tr\" /ST HH:MM /SD YYYY/MM/DD /F"
```

## 提示

- 确保 **系统通知开启**，且未开启专注/勿扰。
- BurntToast 需在当前用户会话触发才可见。

## 备注

- 未经确认不得创建任务。
- 提醒内容使用中文。
- 默认使用 BurntToast 通知（如需弹窗/打开文件，需用户指定）。
