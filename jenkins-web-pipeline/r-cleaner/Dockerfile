FROM rocker/r-ver:4.2.2

# Install system dependencies and MySQL client
RUN apt-get update && apt-get install -y \
    libssl-dev \
    libcurl4-openssl-dev \
    libxml2-dev \
    netcat \
    && apt-get clean

RUN R -e "install.packages(c('filelock'), repos='https://cloud.r-project.org')"

# Set working directory
WORKDIR /app

# Copy files
COPY dadosAlagamento.R .

# Start with wait script
CMD ["Rscript", "dadosAlagamento.R"]
