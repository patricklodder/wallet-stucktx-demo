FROM ubuntu:focal

RUN apt update && apt install -y gcc git python3-dev python3-zmq curl

WORKDIR /demo

# Get binaries
RUN curl -L -O https://github.com/dogecoin/dogecoin/releases/download/v1.14.5/dogecoin-1.14.5-x86_64-linux-gnu.tar.gz && \
    tar xfv dogecoin-1.14.5-x86_64-linux-gnu.tar.gz && \
    mv dogecoin-1.14.5/bin ./ && \
    rm -rf dogecoin-1.14.5*

# Copy test_framework stuffs
RUN git clone -b v1.14.5 https://github.com/dogecoin/dogecoin.git && \
    cp -r dogecoin/qa/rpc-tests/test_framework ./ && \
    dogecoin/qa/pull-tester/install-deps.sh && \
    rm -rf dogecoin


