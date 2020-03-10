# XJCraft Apply
小鸡服新玩家申请处理

## 食用说明
### 后端
1. 安装`Python3`和`pip3`
2. 首次使用执行下面的代码安装依赖

    ```shell script
    pip3 install -r requirements.txt
    ```
3. 执行下面的代码启动
    ```shell script
    python3 main.py
    ```

### 前端
> 推荐使用`yarn`，如希望使用`npm`，请自行变通一下指令
>
> 操作均在 ui 目录中进行

1. 安装`NodeJS`
2. 安装全局依赖

    ```shell script
    npm i -g yarn
    yarn global add @vue/cli
    ```
3. 安装依赖

    ```shell script
    yarn
    ```
4. 调试运行

    ```shell script
    yarn run dev
    ```
4. 生成构建文件

    ```shell script
    yarn run build:prod
    ```
   
   构建结果会生成在 dist 目录中

### 反代(Nginx 为栗子
#### 开发参考配置
```
server {
    listen       8843;

    location / {
        proxy_pass http://127.0.0.1:9527;
        proxy_set_header Host $host;
        proxy_set_header X-Real-Ip $remote_addr;
        proxy_set_header X-Forward-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forward-Proto $schema;
    }

    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-Ip $remote_addr;
        proxy_set_header X-Forward-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forward-Proto $scheme;
    }
}
```

#### 产品参考配置
```
server {
    listen       8843;

    root /var/www/xjapply;  # 前端打包结果的存放路径

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-Ip $remote_addr;
        proxy_set_header X-Forward-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forward-Proto $scheme;
    }
}
```

### 目录结构
```
/
|-- ui 前端目录
|   |-- TODO
|-- app.py web 接口
|-- main.py 启动文件
|-- model.py DB 模型文件
|-- requirements.txt 依赖包列表
|-- setting.py 配置信息
|-- util.py 工具代码
|-- webbase.py web 开发的基础环境

```
