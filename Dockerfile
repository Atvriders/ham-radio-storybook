FROM nginx:alpine

COPY build/index.html /usr/share/nginx/html/index.html
COPY build/ham-radio-storybook.txt build/ham-radio-storybook.pdf /usr/share/nginx/html/
COPY ham-radio-storybook.md /usr/share/nginx/html/ham-radio-storybook.md
