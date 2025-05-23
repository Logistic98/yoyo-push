# 基于python:3.7-slim创建新镜像
FROM python:3.7-slim
# 创建容器内部目录
RUN mkdir /code
# 将项目复制到内部目录
ADD . /code/
# 切换到工作目录
WORKDIR /code
# 安装项目依赖
RUN pip install -r requirements.txt
# 启动项目
ENTRYPOINT ["nohup","python","yoyo-push.py","&"]