FROM ubuntu:20.04

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    git \
    python3 \
    python3-venv \
    openjdk-8-jdk \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev \
    tzdata \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set environment variables
ENV ANDROID_HOME=/opt/android
ENV PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# Install Android SDK
RUN mkdir -p $ANDROID_HOME && \
    cd $ANDROID_HOME && \
    wget https://dl.google.com/android/repository/commandlinetools-linux-6609375_latest.zip && \
    unzip commandlinetools-linux-6609375_latest.zip && \
    rm commandlinetools-linux-6609375_latest.zip && \
    mkdir -p cmdline-tools/latest && \
    mv tools/* cmdline-tools/latest/ && \
    rm -rf tools

# Accept Android SDK licenses
RUN yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --licenses

# Install required Android SDK components
RUN $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager "platform-tools" "platforms;android-31" "build-tools;31.0.0" "ndk;25.2.9519653"

# Set up Python virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create a non-root user
RUN useradd -m -s /bin/bash builder && \
    chown -R builder:builder /opt/venv /opt/android && \
    mkdir -p /tmp/pip && \
    chown -R builder:builder /tmp/pip

# Switch to non-root user
USER builder

# Copy requirements and install Python packages
COPY --chown=builder:builder req.txt .
RUN pip install --no-cache-dir --timeout 1000 numpy pandas matplotlib scikit-learn tqdm streamlit plotly networkx python-dotenv psutil netifaces requests kivy buildozer && \
    pip install --no-cache-dir --timeout 1000 torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir --timeout 1000 openai

# Copy application files
COPY --chown=builder:builder . .

# Build the APK
CMD ["buildozer", "android", "debug"] 