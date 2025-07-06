FROM alpine:latest

RUN apk add --no-cache curl xz tar python3 py3-pip

# Install Tectonic
RUN curl -LO https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.14.1/tectonic-0.14.1-x86_64-unknown-linux-musl.tar.gz && \
    tar -xzf tectonic-0.14.1-x86_64-unknown-linux-musl.tar.gz && \
    mv tectonic /usr/local/bin/ && \
    rm tectonic-0.14.1-x86_64-unknown-linux-musl.tar.gz

# Install Flask with override flag (without break flag cause bug, ref this commit: https://github.com/N4h0/LatexServer/tree/d366c1d0ca3a474ec8d3ade0a294af7e02a7216b)
RUN pip3 install --break-system-packages flask

WORKDIR /app
COPY . .

CMD ["python3", "server.py"]
