FROM python:3.9-slim-buster

# Install all the required packages
WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app
RUN apt-get -qq update
RUN apt-get -qq install -y --no-install-recommends curl git gnupg2 unzip wget pv jq
#RUN apt install install build-essential
#RUN apt install zlib1g-dev 
# add mkvtoolnix
#RUN wget -q -O - https://mkvtoolnix.download/gpg-pub-moritzbunkus.txt | apt-key add - && \
   # wget -qO - https://ftp-master.debian.org/keys/archive-key-10.asc | apt-key add -
#RUN sh -c 'echo "deb https://mkvtoolnix.download/debian/ buster main" >> /etc/apt/sources.list.d/bunkus.org.list' && \
    #sh -c 'echo deb http://deb.debian.org/debian buster main contrib non-free | tee -a /etc/apt/sources.list' && apt update && apt install -y mkvtoolnix

# install required packages
RUN apt-get update && apt-get install -y software-properties-common && \
    rm -rf /var/lib/apt/lists/* && \
    apt-add-repository non-free && \
    apt-get -qq update && apt-get -qq install -y --no-install-recommends \
    # this package is required to fetch "contents" via "TLS"
    apt-transport-https \
    # install coreutils
    coreutils aria2 jq pv gcc g++ \
    # install encoding tools
    mediainfo \
    # miscellaneous
    neofetch python3-dev git bash build-essential nodejs npm ruby \
    python-minimal locales python-lxml nginx gettext-base xz-utils \
    # install extraction tools
    p7zip-full p7zip-rar rar unrar zip unzip \
    # miscellaneous helpers
    megatools mediainfo && \
    # clean up the container "layer", after we are done
    rm -rf /var/lib/apt/lists /var/cache/apt/archives

RUN wget https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz && \
    tar xvf ffmpeg*.xz && \
    cd ffmpeg-*-static && \
    mv "${PWD}/ffmpeg" "${PWD}/ffprobe" /usr/local/bin/

ENV LANG C.UTF-8
ENV BOT_TOKEN 1835113477:AAHyx-mzepmgHAFt-YQrRlTelI8cRN3obh0
ENV OWNER_ID -1001694051809
#RUN wget https://www.python.org/ftp/python/3.9.4/Python-3.9.4.tgz && \
 #   tar xzf Python-3.9.4.tgz && \
  #  cd Python-3.9.4 && \
 #   ./configure --enable-optimizations && \
  #  make altinstall 
    
# we don't have an interactive xTerm
ENV DEBIAN_FRONTEND noninteractive

# sets the TimeZone, to be used inside the container
ENV TZ Asia/Kolkata

# rclone ,gclone and fclone
RUN curl https://rclone.org/install.sh | bash && \
    aria2c https://git.io/gclone.sh && bash gclone.sh && \
    aria2c https://github.com/mawaya/rclone/releases/download/fclone-v0.4.1/fclone-v0.4.1-linux-amd64.zip && \
    unzip fclone-v0.4.1-linux-amd64.zip && mv fclone-v0.4.1-linux-amd64/fclone /usr/bin/ && chmod +x /usr/bin/fclone && rm -r fclone-v0.4.1-linux-amd64

#drive downloader
RUN curl -L https://github.com/jaskaranSM/drivedlgo/releases/download/1.5/drivedlgo_1.5_Linux_x86_64.gz -o drivedl.gz && \
    7z x drivedl.gz && mv drivedlgo /usr/bin/drivedl && chmod +x /usr/bin/drivedl && rm drivedl.gz

RUN pip3 install poetry
   
     
#ngrok
RUN aria2c https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip && unzip ngrok-stable-linux-amd64.zip && mv ngrok /usr/bin/ && chmod +x /usr/bin/ngrok

#install rmega
RUN gem install rmega


# Copies config(if it exists)
COPY . . 

# Install requirements and start the bot
RUN npm install

#RUN chmod u+x /usr/src/app/bin/tools/mediainfo

RUN chmod u+x /usr/src/app/bin/tools/mkvmerge

RUN chmod u+x /usr/src/app/bin/tools/mp4decrypt

RUN chmod u+x mp4decrypt/mp4decrypt

RUN chmod u+x /usr/src/app/bin/tools/mp4dump

#RUN chmod u+x /root/shell2/bin/tools/mp4dump
#RUN chmod u+x /root/shell2/bin/tools/mp4decrypt
#RUN chmod u+x /root/shell2/bin/tools/mkvmerge
#RUN chmod u+x /root/shell2/bin/tools/mediainfo

#install requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# setup workdir
COPY default.conf.template /etc/nginx/conf.d/default.conf.template
COPY nginx.conf /etc/nginx/nginx.conf
RUN dpkg --add-architecture i386 && apt-get update && apt-get -y dist-upgrade

CMD /bin/bash -c "envsubst '\$PORT' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf" && nginx -g 'daemon on;' && cd /usr/src/app && mkdir Downloads && bash start.sh
