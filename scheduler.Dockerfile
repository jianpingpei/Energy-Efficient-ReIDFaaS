FROM  python:3.8-slim
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple flask requests

COPY ./scheduler /home/work/scheduler
WORKDIR /home/work/scheduler

ENV PYTHONPATH "${PYTHONPATH}:/home/work"

ENTRYPOINT ["python"]
CMD ["scheduler.py"]