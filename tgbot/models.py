from __future__ import annotations

from typing import Union, Optional, Tuple

from django.db import models
from django.db.models import QuerySet, Manager
from telegram import Update
from telegram.ext import CallbackContext

from dtb.settings import DEBUG
from tgbot.handlers.utils.info import extract_user_data_from_update
from utils.models import CreateUpdateTracker, nb, CreateTracker, GetOrNoneManager

class Schedule(models.Model):
    
    class Day(models.TextChoices):
        MONDAY = 'Пн'
        TUESDAY = 'Вт'
        WEDNSDAY = 'Ср'
        THURSDAY = 'Чт'
        FRIDAY = 'Пт'
        SATURDAY = 'Сб'

    class Time(models.TextChoices):
        first = '8:30'
        second = '10:10'
        third = '11:50'
        fourth = '13:50'
        fifth = '15:30'
        sixth = '17:10'
        seventh = '18:50'
        eighth = '20:30'

    day = models.CharField(max_length=2, choices=Day.choices)
    time = models.CharField(max_length=5, choices=Time.choices, default="")
    lesson = models.CharField(max_length=200, default="")
    group = models.CharField(max_length=200, default="")
    teacher = models.CharField(max_length=200, default="")
    isOnline = models.CharField(max_length=200, default="")
    

    @property
    def get_id(self):
        return self.pk

class Links(models.Model):
    url = models.URLField(max_length=200, default="")
    lesson = models.CharField(max_length=200, default="")

class Books(models.Model):
    name = models.CharField(max_length=200, default="")
    url = models.URLField(max_length=500, default="")

class Requirements(models.Model):
    name = models.CharField(max_length=200, default="")
    text = models.CharField(max_length=5000, default="")
    photo_id = models.CharField(max_length=500, default="")
    
class RequirementFile(models.Model):
    requirements = models.ForeignKey(Requirements, on_delete=models.CASCADE)
    file_field = models.FileField(default=None, null=True)

class Homework(models.Model):
    name = models.CharField(max_length=200, default="")
    task_doc = models.FileField(default=None, null=True)
    task_text = models.CharField(max_length=5000, default="")
    task_photo_id = models.CharField(max_length=500, default="")

class Solution(models.Model):
    name = models.CharField(max_length=200, default="")
    file_field = models.FileField(default=None, null=True)
    photo_id = models.CharField(max_length=500, default="")    
    text = models.CharField(max_length=200, default="")

class AdminUserManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_admin=True)

class User(CreateUpdateTracker):
    user_id = models.PositiveBigIntegerField(primary_key=True)  # telegram_id
    username = models.CharField(max_length=32, **nb)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256, **nb)
    deep_link = models.CharField(max_length=64, **nb)

    is_blocked_bot = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)

    objects = GetOrNoneManager()  # user = User.objects.get_or_none(user_id=<some_id>)
    admins = AdminUserManager()  # User.admins.all()

    def __str__(self):
        return f'@{self.username}' if self.username is not None else f'{self.user_id}'

    @classmethod
    def get_user_and_created(cls, update: Update, context: CallbackContext) -> Tuple[User, bool]:
        """ python-telegram-bot's Update, Context --> User instance """
        data = extract_user_data_from_update(update)
        update.message.reply_text(text="before")
        try:
            user, created = cls.objects.update_or_create(user_id=data["user_id"], defaults=data)
        except Exception as e:
            update.message.reply_text(text=str(e))
        # u, created = cls.objects.update_or_create(user_id=data["user_id"], defaults=data)
        # if created:
        #     # Save deep_link to User model
        #     if context is not None and context.args is not None and len(context.args) > 0:
        #         payload = context.args[0]
        #         if str(payload).strip() != str(data["user_id"]).strip():  # you can't invite yourself
        #             u.deep_link = payload
        #             u.save()

        return user, created

    @classmethod
    def get_user(cls, update: Update, context: CallbackContext) -> User:
        u, _ = cls.get_user_and_created(update, context)
        return u

    @classmethod
    def get_user_by_username_or_user_id(cls, username_or_user_id: Union[str, int]) -> Optional[User]:
        """ Search user in DB, return User or None if not found """
        username = str(username_or_user_id).replace("@", "").strip().lower()
        if username.isdigit():  # user_id
            return cls.objects.filter(user_id=int(username)).first()
        return cls.objects.filter(username__iexact=username).first()

    @property
    def invited_users(self) -> QuerySet[User]:
        return User.objects.filter(deep_link=str(self.user_id), created_at__gt=self.created_at)

    @property
    def tg_str(self) -> str:
        if self.username:
            return f'@{self.username}'
        return f"{self.first_name} {self.last_name}" if self.last_name else f"{self.first_name}"

    @property
    def get_user_id(self):
        return self.user_id

