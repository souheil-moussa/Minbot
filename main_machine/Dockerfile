FROM httpd:latest

#Install Dependinces
RUN apt-get update && apt-get install -y ffmpeg inotify-tools
#Copy website code
COPY ./my-httpd.conf /usr/local/apache2/conf/httpd.conf

COPY ./website/index.html /usr/local/apache2/htdocs/
COPY ./website/page2.html /usr/local/apache2/htdocs/
COPY ./website/script.js /usr/local/apache2/htdocs/
COPY ./website/auto_convert.sh /usr/local/apache2/
RUN dos2unix /usr/local/apache2/auto_convert.sh
COPY ./website/favicon.ico /usr/local/apache2/htdocs/
#Setup enviroment
RUN touch  /usr/local/apache2/DAVLock
RUN chmod  755 /usr/local/apache2/DAVLock
RUN chown  www-data:www-data /usr/local/apache2/DAVLock
RUN mkdir -p /usr/local/apache2/htdocs/hls
RUN mkdir -p /usr/local/apache2/out
RUN chmod -R 755 /usr/local/apache2/htdocs/hls
RUN chown -R www-data:www-data /usr/local/apache2/htdocs/hls


#run startup commands
CMD ["/bin/bash", "-c", "/usr/local/apache2/auto_convert.sh & httpd-foreground"]

#expose necessary ports
EXPOSE 80
