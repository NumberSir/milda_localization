# Milda Localization

## 简介
[黄油翻译小工具 0v0](https://github.com/NumberSir/milda_localization)

## 食用方法
1. 需要 `python` 3.8+
2. 在根目录使用 `pip install -r requirements.txt` 安装依赖库
3. 在 `consts.py` 里填你的游戏本体下载地址 `DIR_ROOT` 、游戏版本 `VERSION`，以及 paratranz 个人 token, 在[这里](https://paratranz.cn/users/my)的`设置`中找
4. 因为脚本会覆盖原游戏文本，所以运行前请先手动把 `{游戏根目录}\www\data` 下的游戏文本手动复制到 `BACKUP` 文件夹里以备份，或是注释掉 `main.py` 中的覆盖原文件一步
5. 运行 `main.py` (`python -m main`)
6. 脚本会将游戏文件中需要汉化的部分提取出来处理为键值对形式，放在 `data\fetches\{版本}` 下；然后处理为可以上传到 paratranz 的形式，放在 `data\paratranz` 下；然后下载 paratranz 已经翻译好的词典并应用，最终处理回原游戏文件，在 `data\results` 下；随即应用覆盖原游戏文件