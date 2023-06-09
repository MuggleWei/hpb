ARG IMAGE
FROM ${IMAGE} as builder

ARG PYPI_MIRROR
RUN apk add --no-cache py-pip
RUN if [ -n "$PYPI_MIRROR" ]; then \
		#python -m pip install --upgrade pip; \
		echo "use pypi mirror $PYPI_MIRROR";  \
		python -m pip config set global.index-url $PYPI_MIRROR; \
	fi

RUN mkdir -p /app/src/hpb
WORKDIR /app/src/hpb/
COPY hpb ./hpb
COPY share ./share
COPY etc ./etc
COPY doc ./doc
COPY README.md ./
COPY README_cn.md ./
COPY LICENSE ./
COPY requirements.dev.txt ./
COPY pyinstaller_pkg.sh ./
RUN sed -i 's/bash/sh/' pyinstaller_pkg.sh
RUN ./pyinstaller_pkg.sh

FROM ${IMAGE}
RUN mkdir -p /opt/hpb
COPY --from=builder /app/src/hpb/dist/hpb/hpb /usr/local/bin/
COPY --from=builder /app/src/hpb/dist/hpb/etc /usr/local/etc/hpb
COPY --from=builder /app/src/hpb/dist/hpb/share /usr/local/share/hpb
