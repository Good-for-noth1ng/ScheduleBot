# django-telegram-bot
Telegram bot (Django + python-telegram-bot) based on template of [this guy](https://github.com/ohld/django-telegram-bot/).

[![Sparkline](https://stars.medv.io/Naereen/badges.svg)](https://stars.medv.io/Naereen/badges)


### Check the example bot that uses the code from Main branch: [t.me/djangotelegrambot](https://t.me/djangotelegrambot)

## Features

* Database: Sqlite3
* Telegram API usage in pooling or [webhook mode](https://core.telegram.org/bots/api#setwebhook)
* Native telegram [commands in menu](https://github.com/ohld/django-telegram-bot/blob/main/.github/imgs/bot_commands_example.jpg)

Built-in Telegram bot methods:
* `/start` — start django-bot
* `/sendschedule` — bot sends you info about your schedule (time, lessons, teachers...)
* `/links` — sending list of useful or necessary urls, for ex. commands in msteams 
* `/books` - sending list of useful or necessary urls for downloading books
* `/requirements` - showing list of teacher's requirements (for example, num of tests)
* `/homework` - sending for homework
* `/solutions` - sending other people solutions they shared with
* `/edit<any of commands above>` - allows users to send files, photos and texts. Makes easier to share and keep in one place all of the data
 
![Alt text](url "/.github/imgs/example1.jpg")