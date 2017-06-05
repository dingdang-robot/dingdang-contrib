# dingdang-contrib

[叮当机器人](http://github.com/wzpan/dingdang) 的用户贡献插件。

* [插件列表](https://github.com/dingdang-robot/dingdang-contrib/wiki)

## 安装

``` sh
cd /home/pi/.dingdang
git clone http://github.com/dingdang-robot/dingdang-contrib contrib
pip install -r contrib/requirements.txt
sudo apt-get install sox  # 用于播放音乐
sudo apt-get install libsox-fmt-mp3 # 添加 sox 的 mp3 格式支持
```

## 升级

``` sh
cd /home/pi/.dingdang/contrib
git pull
pip install --upgrade -r contrib/requirements.txt
```

## 如何贡献

### 流程说明

1. fork 本项目；
2. 添加你的插件；
3. 如果你的插件有依赖第三方库，将依赖项添加进 requirements.txt 。如果依赖第三方工具, 则在 README 中的[安装](#安装) 一节中补充。
4. 发起 pull request ，说明该插件的用途、指令和配置信息（如果有的话）。
5. pull request 被 accept 后，在本项目 [Wiki页](https://github.com/dingdang-robot/dingdang-contrib/wiki/neteasemusic) 中添加一项，将该插件的用途、指令和配置信息也添加到此页面中。

### 插件规范

* 每个插件只能包含一个 .py 文件。依赖的其他库文件不得放进本仓库中，否则会被当成插件而解析出错。如果确实需要分成多个文件，可以将其他文件打包发布到 PyPi ，然后将依赖加进 requirements.txt 中。
