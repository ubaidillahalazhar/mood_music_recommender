FROM nginx:latest
RUN rm /etc/nginx/conf.d/default.conf
COPY . /usr/share/nginx/html
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
