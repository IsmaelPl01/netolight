FROM node:16-alpine as builder

WORKDIR /opt/netolight/web

COPY web/package*.json web/jsconfig.json web/.eslintrc web/.prettierrc ./

RUN npm install

COPY web/public public
COPY web/src src

RUN npm run build


FROM nginx:1.24.0-alpine

COPY web/nginx.conf.template /etc/nl-web/nginx.conf.template
COPY web/run.sh .

RUN rm -rf /usr/share/nginx/html/*

COPY --from=builder /opt/netolight/web/build /usr/share/nginx/html

CMD sh run.sh
