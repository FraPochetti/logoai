FROM pytorch/pytorch:1.12.1-cuda11.3-cudnn8-runtime

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 git aria2 wget -y
COPY requirements.txt /opt/requirements.txt
RUN pip install -r /opt/requirements.txt

RUN git clone https://github.com/lgvaz/ControlNet.git

WORKDIR /workspace/ControlNet

RUN aria2c --console-log-level=error \
    --summary-interval=10 \
    --header="Authorization: Bearer " \
    -c -x 16 -k 1M -s 16 -d models \
    -o control_sd15_canny.pth https://huggingface.co/lllyasviel/ControlNet/resolve/main/models/control_sd15_canny.pth

RUN wget https://gist.githubusercontent.com/lgvaz/8025ac53cc707e9d3222ab0153285fd5/raw/861a108626ee10dbdc6d18c07bef06cac5936824/prompts.txt

COPY serve ./serve
ENV PATH="/workspace/ControlNet:$PATH"

EXPOSE 8080