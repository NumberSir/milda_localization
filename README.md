# Milda Localization

## 新项目
[https://github.com/NumberSir/DLoMC-Localization](https://github.com/NumberSir/DLoMC-Localization)

## 简介
[黄油翻译小工具](https://github.com/NumberSir/milda_localization)

## 写在前面

游戏作者：Mlidasento

发布地址：https://subscribestar.adult/mildasento

**请自行下载游戏本体，本仓库不提供游戏本体下载，仅包含汉化文件**

本仓库将会不定期放出游戏的简体中文本地化语言文件，仅供交流学习，请于下载后 24 小时内删除。如果你未满 18 岁，请勿下载此游戏。仓库本身不含游戏相关内容，仅作为发布地址。对在其它平台下载的汉化游戏文件不保证安全性，请谨慎下载。

游戏完全免费游玩，严禁将中文本地化版本用作商业盈利用途或公开大肆传播，对于商业盈利或公开传播导致的可能法律后果完全由使用者自行承担，与汉化成员无关。

如在游玩过程中遇到任何问题，或对汉化文本有建议，请发布 issue 反馈，反馈时请附上出现问题时的截图 + 复现步骤 + 游戏版本等必要信息，在其它平台反馈问题可能得不到回应。请不要删除自己的议题, 方便后来人查阅相关问题。请注意，本仓库仅解决由于游戏汉化版本导致的问题，对在其他地方下载的汉化版出现的问题概不负责，如果问题在英文版能复现，请去[游戏官方 Discord](https://discord.gg/gWt9BYebBS) 反映。

## 汉化文件下载
1. 下载最新版 `Release` 中的压缩包
2. 根据压缩包内指示将压缩包解压至 `<游戏根目录>/www` 文件夹，替换原文件
3. 压缩包版本号说明: `<游戏版本>-chs-<汉化版本>-<翻译进度>-<润色进度>`

## 脚本食用方法
1. 脚本仅供汉化组成员使用
2. 需要 `python` 3.8+
3. 在根目录使用 `pip install -r requirements.txt` 安装依赖库
4. 在 `.env` 里填你的 `token` (`PARATRANZ_TOKEN`), 在 `https://paratranz.cn/users/my` 的设置里找
5. 在 `consts.py` 里填你的游戏本体下载地址 `DIR_ROOT` 、游戏版本 `VERSION`(https://paratranz.cn/users/my)的`设置`中找
6. 因为脚本会覆盖原游戏文本，所以运行前请先手动把 `{游戏根目录}\www\data` 下的游戏文本手动复制到 `BACKUP` 文件夹里以备份，或是注释掉 `main.py` 中的覆盖原文件一步
7. 运行 `main.py` (`python -m main`)
8. 脚本会将游戏文件中需要汉化的部分提取出来处理为键值对形式，放在 `data\fetches\{版本}` 下；然后处理为可以上传到 paratranz 的形式，放在 `data\paratranz` 下；然后下载 paratranz 已经翻译好的词典并应用，最终处理回原游戏文件，在 `data\results` 下；随即应用覆盖原游戏文件
