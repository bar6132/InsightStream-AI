FROM node:20-alpine
WORKDIR /app

# התקנת תלויות בלבד
COPY package*.json ./
RUN npm install

# אנחנו לא עושים BUILD כאן כי אנחנו משתמשים ב-Volumes 
# כדי להריץ את הקוד ישירות מהתיקייה שלך
COPY . .

EXPOSE 3000

# הרצה במצב פיתוח (Dev) במקום Start
CMD ["npm", "run", "dev"]