FROM python:3.13-slim
ENV PYTHONHASHSEED=20260723 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 MPLBACKEND=Agg
WORKDIR /app
COPY requirements-lock.txt .
RUN pip install --no-cache-dir -r requirements-lock.txt
COPY . .
RUN pip install --no-deps -e .
ENTRYPOINT ["trace-r"]
