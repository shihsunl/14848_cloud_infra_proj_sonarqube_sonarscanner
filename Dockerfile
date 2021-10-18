FROM ubuntu:18.04
ENV DEBIAN_FRONTEND noninteractive
MAINTAINER Shih-Sung-Lin
EXPOSE 9000 80 22 8080 443 9022 5000
ENV PORT 8080
RUN echo "#!/bin/sh\nexit 0" > /usr/sbin/policy-rc.d
ENV JAVA_HOME=/usr/lib/jdk1.8.0_211
ENV SONAR_WEB_CONTEXT /sonarqube
ENV SONAR_ES_BOOTSTRAP_CHECKS_DISABLE true
ENV SONAR_HOME=/opt/sonarqube
ENV SONAR_SCANNER_HOME=/opt/sonar-scanner
ENV PATH=$PATH:$JAVA_HOME/bin:$SONAR_HOME/bin:$SONAR_SCANNER_HOME/bin

# setup
RUN mkdir /temp
RUN apt-get clean && apt-get update &&\
    apt-get install -y git g++ software-properties-common build-essential language-pack-en unzip curl wget vim libpam0g-dev libssl-dev cmake cron libssl-dev openssl iputils-ping openssh-server sudo net-tools
RUN apt-get install -y apache2 php libapache2-mod-php python3 && add-apt-repository ppa:deadsnakes/ppa -y && apt-get install -y python3-pip
RUN pip3 install Flask==2.0.1 gunicorn==20.1.0

# Create test user for launching SonarQube
RUN useradd -rm -d /home/ubuntu -s /bin/bash -g root -G sudo -u 1000 test &&\
    echo 'test:test' | chpasswd # sets the password for the user test to test

# install postgresql
WORKDIR /temp
RUN apt-get -y install postgresql postgresql-contrib postgresql-common
RUN /etc/init.d/postgresql start &&\
    echo "CREATE USER sonar;ALTER USER sonar WITH ENCRYPTED password 'P@ssword';CREATE DATABASE sonar OWNER sonar;GRANT ALL PRIVILEGES ON DATABASE sonar TO sonar;ALTER USER sonar SUPERUSER CREATEDB;" | sudo -u postgres psql

# install JAVA
RUN wget https://github.com/frekele/oracle-java/releases/download/8u211-b12/jdk-8u211-linux-x64.tar.gz
RUN tar -zxvf jdk-8u211-linux-x64.tar.gz &&\
    cp -R /temp/jdk1.8.0_211 /usr/lib/jdk1.8.0_211 &&\
    ln -s /usr/lib/jdk1.8.0_211/bin/java /etc/alternatives/java

# install sonarqube
RUN wget https://binaries.sonarsource.com/Distribution/sonarqube/sonarqube-7.3.zip &&\
    unzip sonarqube-7.3.zip -d /opt &&\
    mv /opt/sonarqube-7.3 /opt/sonarqube
RUN echo "sonar.web.context=/sonarqube\nsonar.jdbc.username=sonar\nsonar.jdbc.password=P@ssword\nsonar.jdbc.url=jdbc:postgresql://localhost/sonar\nsonar.web.javaAdditionalOpts=-server" >> /opt/sonarqube/conf/sonar.properties
RUN /opt/sonarqube/bin/linux-x86-64/sonar.sh start &&\
    sudo chown -R test:root /opt/sonarqube/

# install sonar-scanner
RUN mkdir /opt/sonar-scanner
WORKDIR /opt/sonar-scanner
RUN wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-3.2.0.1227-linux.zip &&\
    unzip sonar-scanner-cli-3.2.0.1227-linux.zip &&\
    rm sonar-scanner-cli-3.2.0.1227-linux.zip &&\
    mv sonar-scanner-3.2.0.1227-linux/* /opt/sonar-scanner/ &&\
    rm -r sonar-scanner-3.2.0.1227-linux/
RUN echo "sonar.host.url=http://localhost:9000/sonarqube" >> /opt/sonar-scanner/conf/sonar-scanner.properties
RUN chmod -R 777 /opt/sonar-scanner/bin/sonar-scanner &&\
    chown -R test:root /opt/sonar-scanner/ &&\
    ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner

# get repo for launching sonar scanner server
WORKDIR /temp
RUN git clone https://github.com/shihsunl/14848_cloud_infra_proj_sonarqube_sonarscanner.git
RUN mv /temp/14848_cloud_infra_proj_sonarqube_sonarscanner/* /temp/ && rm -r /temp/14848_cloud_infra_proj_sonarqube_sonarscanner/

# Entrypoint
CMD /etc/init.d/postgresql start &&\ 
    sudo -u test SONAR_WEB_CONTEXT=/sonarqube JAVA_HOME=/usr/lib/jdk1.8.0_211 SONAR_HOME=/opt/sonarqube PATH=$PATH:$JAVA_HOME/bin:$SONAR_HOME/bin /opt/sonarqube/bin/linux-x86-64/sonar.sh start &&\
    /etc/init.d/ssh restart &&\
    cd /temp &&\
    python3 server.py

#exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 hello:app
