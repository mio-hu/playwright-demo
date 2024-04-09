
# 项目介绍
Pytest + Playwright + Allure UI自动化demo
```text
这是一个拉取之后可以直接运行的项目，因为Demo中用到的项目是TesterHome
前提是需要做好环境准备，然后按照快速开始的步骤执行就可以。
需要注意以下两点：
1. 需要在conf文件夹下面的base_config.yaml文件中填写您自己的账号密码
2. 你需要安装正确安装Allure，如果没不想安装也可以在pytest文件中去掉 
    --alluredir=./reports/temp --clean-alluredi 这两个参数
```

目前有的功能：
-  UI自动化 Page Object Model 设计模式 (M没有完成，Demo不好封装组建)
-  Playwright 的基本使用 
-  Pytest fixture 常见的使用方式
-  Pytest 命令行各种常用的参数配置
-  Allure 报告基本的装饰器使用
-  登录状态存储在内存，避免重复登录

# 项目结构 
```text
├── README.md                  #  项目介绍及使用指南
├── reports                    #  Allure测试报告结果
├── conf                       #  配置文件的文件夹
├── logs                       #  存放日志的文件夹
├── pages                      #  根据页面封装的类文件夹
├── testcases                  #  测试用例文件夹
├── utils                      #  封装的一些常用的工具类
├── pytest.ini                 # ️pytest配置文件
├── requirements.txt           #  存放项目依赖的Python库
```

# 快速开始 

## 创建虚拟环境 
```shell
python -m venv venv
```

## 安装依赖 
```shell
pip install -r requirements.txt
```

## 安装浏览器 
```shell
playwright install
```

## 运行测试 
```shell
pytest
```

## 生成测试报告 
```shell
allure serve  ./reports/temp 
```

## 将报告保存成本地文
```shell
allure generate ./reports/temp -o ./reports/html --clean
```
# 联系我
- 微信 ： _**MioHu**