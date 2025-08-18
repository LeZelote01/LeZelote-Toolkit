# Metasploit Framework Container
# Pentest-USB Toolkit - Docker Configuration
# Version: 1.0.0

FROM ubuntu:22.04

LABEL maintainer="Pentest-USB Team"
LABEL description="Metasploit Framework for Pentest-USB Toolkit"
LABEL version="1.0.0"

# Avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV MSF_DATABASE_CONFIG=/opt/metasploit-framework/config/database.yml

# Update system and install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg2 \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    lsb-release \
    build-essential \
    ruby \
    ruby-dev \
    git \
    autoconf \
    libtool \
    libffi-dev \
    libssl-dev \
    libyaml-dev \
    libreadline-dev \
    libncurses5-dev \
    libgdbm-dev \
    sqlite3 \
    libsqlite3-dev \
    postgresql \
    postgresql-contrib \
    postgresql-client \
    libpq-dev \
    nmap \
    netcat \
    john \
    hashcat \
    hydra \
    nikto \
    dirb \
    gobuster \
    sqlmap \
    binwalk \
    foremost \
    steghide \
    exiftool \
    && rm -rf /var/lib/apt/lists/*

# Install Metasploit Framework
RUN curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && \
    chmod 755 msfinstall && \
    ./msfinstall

# Create msf user
RUN useradd -ms /bin/bash msf && \
    usermod -aG sudo msf

# Create necessary directories
RUN mkdir -p /opt/metasploit-framework/config \
    /home/msf/.msf4 \
    /var/lib/postgresql/data \
    /opt/payloads \
    /opt/exploits \
    /opt/scripts

# Set up PostgreSQL for Metasploit
RUN service postgresql start && \
    sudo -u postgres createuser msf && \
    sudo -u postgres createdb msf_database && \
    sudo -u postgres psql -c "ALTER USER msf WITH PASSWORD 'msfpassword';" && \
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE msf_database TO msf;"

# Configure Metasploit database
RUN echo "production:" > /opt/metasploit-framework/config/database.yml && \
    echo "  adapter: postgresql" >> /opt/metasploit-framework/config/database.yml && \
    echo "  database: msf_database" >> /opt/metasploit-framework/config/database.yml && \
    echo "  username: msf" >> /opt/metasploit-framework/config/database.yml && \
    echo "  password: msfpassword" >> /opt/metasploit-framework/config/database.yml && \
    echo "  host: localhost" >> /opt/metasploit-framework/config/database.yml && \
    echo "  port: 5432" >> /opt/metasploit-framework/config/database.yml && \
    echo "  pool: 75" >> /opt/metasploit-framework/config/database.yml && \
    echo "  timeout: 5" >> /opt/metasploit-framework/config/database.yml

# Install additional gems for Metasploit
RUN gem install bundler && \
    cd /opt/metasploit-framework && \
    bundle install

# Install custom Metasploit modules and scripts
COPY exploits/ /opt/exploits/
COPY payloads/ /opt/payloads/
COPY scripts/ /opt/scripts/

# Set permissions
RUN chown -R msf:msf /home/msf/.msf4 \
    /opt/payloads \
    /opt/exploits \
    /opt/scripts

# Expose Metasploit RPC and web service ports
EXPOSE 55552 55553 4444 4445 8080 8443

# Set working directory
WORKDIR /opt/metasploit-framework

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to msf user
USER msf

# Set environment variables
ENV PATH="/opt/metasploit-framework:${PATH}"
ENV MSF_ROOT="/opt/metasploit-framework"

ENTRYPOINT ["/entrypoint.sh"]
CMD ["msfconsole"]