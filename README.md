# Rasa-Weather
Rasa天气查询机器人

特点：
1. 调用[WebService服务](http://www.webxml.com.cn/zh_cn/web_services.aspx)，不使用API


# 效果
![效果.gif](https://s1.ax1x.com/2020/06/11/tblRne.gif)

# 使用方法
1. 安装Rasa
```bash
pip install rasa-x -i https://pypi.rasa.com/simple
```
2. 训练模型
```bash
rasa train
```
3. 启动自定义动作（此过程需要约30s）
```bash
rasa run actions
```
4. 启动对话
```bash
rasa shell
```

# TODO
1. 对[Weather](https://github.com/vba34520/Weather)建立本地缓存机制，不用每次初始化几十秒