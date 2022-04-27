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
        eighth = '+'

    day = models.CharField(max_length=2, choices=Day.choices)
    time = models.CharField(max_length=5, choices=Time.choices, default="")
    lesson = models.CharField(max_length=200, default="")
    group = models.CharField(max_length=200, default="")
    teacher = models.CharField(max_length=200, default="")
    isOnline = models.CharField(max_length=200, default="")
    
    @classmethod
    def update_schedule(cls, context: CallbackContext):
        schedule, created = cls.objects.update_or_create(
            day=context.user_data["day"],
            time=context.user_data["time"],
            defaults={
                'lesson': context.user_data["lesson"],
                'teacher': context.user_data["teacher"],
                'group': context.user_data['group'],
                'isOnline': context.user_data['isOnline']
            }
        )
        schedule.save()

    @classmethod
    def deleting_schedule(cls, context: CallbackContext):
        schedule = cls.objects.all().filter(day=context.user_data["day"], time=context.user_data["time"])
        for sched in schedule:
            if sched:
                sched.delete()

#user sends url
#url to google disk with large files or url to website 
class ExternalResource(models.Model):
    name = models.CharField(max_length=200, default="")
    url = models.URLField(max_length=500, default="")
    is_link_to_book = models.BooleanField(default=False)
    is_link_to_command = models.BooleanField(default=False)

    @classmethod
    def get_books(cls):
        return cls.objects.all().filter(is_link_to_book=True)

    @classmethod
    def get_urls(cls):
        return cls.objects.all().filter(is_link_to_command=True)

    @classmethod
    def get_books_num(cls):
        return cls.objects.all().filter(is_link_to_book=True).count()

    @classmethod
    def get_urls_num(cls):
        return cls.objects.all().filter(is_link_to_command=True).count()
    
    @classmethod
    def make_string_for_choosing(cls, is_link_to_book=False, is_link_to_command=False):
        if is_link_to_book:
            ext_res = cls.objects.all().filter(is_link_to_book=True)
        elif is_link_to_command:
            ext_res = cls.objects.all().filter(is_link_to_command=True)
        text = ""
        for i in range(0, len(ext_res)):
            text += f"{i+1} - {ext_res[i].name}\n"
        return text
    
    @classmethod
    def deleting_by_index(cls, index, is_link_to_book=False, is_link_to_command=False):
        if is_link_to_book:
            ext_res = cls.objects.all().filter(is_link_to_book=True)
        elif is_link_to_command:
            ext_res = cls.objects.all().filter(is_link_to_command=True)
        ext_res[index].delete()
    
    @classmethod
    def sending_chosen_ext_res(cls, index, update: Update, is_link_to_book=False, is_link_to_command=False):
        if is_link_to_book:
            ext_res = cls.objects.all().filter(is_link_to_book=True)
        elif is_link_to_command:
            ext_res = cls.objects.all().filter(is_link_to_command=True)
        
        text = f"🔍 {ext_res[index].name} 🔗 {ext_res[index].url}"
        update.message.reply_text(text=text)
    
#user sends photo, file or text. This set can be requirement, homework or soluton
#telegram will store these photos and files, db will store the text 
class InternalResource(models.Model):
    name = models.CharField(max_length=2000, default="")
    file_id = models.CharField(max_length=1000, default="")
    photo_id = models.CharField(max_length=1000, default="")    
    text = models.CharField(max_length=5000, default="")
    is_requirement = models.BooleanField(default=False)
    is_homework = models.BooleanField(default=False)
    is_solution = models.BooleanField(default=False)

    @classmethod
    def get_requirements(cls):
        return cls.objects.all().filter(is_requirement=True)
    
    @classmethod
    def get_requirements(cls):
        return cls.objects.all().filter(is_homework=True)
    
    @classmethod
    def get_requirements(cls):
        return cls.objects.all().filter(is_solution=True)

    @classmethod
    def get_num_of_requirements(cls):
        return cls.objects.all().filter(is_requirement=True).count()
    
    @classmethod
    def get_num_of_homeworks(cls):
        return cls.objects.all().filter(is_homework=True).count()
    
    @classmethod
    def get_num_of_solutions(cls):
        return cls.objects.all().filter(is_solution=True).count()
    
    @classmethod
    def make_string_for_choosing(cls, is_requirement=False, is_homework=False, is_solution=False):
        if is_requirement:
            int_res = cls.objects.all().filter(is_requirement=True)
        elif is_homework:
            int_res = cls.objects.all().filter(is_homework=True)
        elif is_solution:
            int_res = cls.objects.all().filter(is_solution=True)
        text = ""
        for i in range(0, len(int_res)):
            text += f"{i+1} - {int_res[i].name}\n"
        return text
    
    @classmethod
    def deleting_requirements_by_index(cls, index):
        int_res = cls.objects.all().filter(is_requirement=True)
        int_res[index].delete()
    
    @classmethod
    def deleting_homework_by_index(cls, index):
        int_res = cls.objects.all().filter(is_homework=True)
        int_res[index].delete()
    
    @classmethod
    def deleting_solutions_by_index(cls, index):
        int_res = cls.objects.all().filter(is_solution=True)
        int_res[index].delete()
    
    @classmethod
    def sending_chosen_int_res(cls, index, update: Update, is_requirement=False, is_homework=False, is_solution=False):
        if is_requirement:
            int_res = cls.objects.all().filter(is_requirement=True)
        elif is_homework:
            int_res = cls.objects.all().filter(is_homework=True)
        elif is_solution:
            int_res = cls.objects.all().filter(is_solution=True)
        
        text = f"🧭 {int_res[index].name}\n"
        
        if int_res[index].text:
            text += f"{int_res[index].text}"
            update.message.reply_text(text=text)
        elif int_res[index].file_id:
            update.message.reply_text(text=text)
            update.message.reply_document(document=int_res[index].file_id)
        elif int_res[index].photo_id:
            update.message.reply_text(text=text)
            update.message.reply_photo(photo=int_res[index].photo_id)

###############################
class Requirements(models.Model):
    name = models.CharField(max_length=200, default="")
    text = models.CharField(max_length=5000, default="")
    photo_id = models.CharField(max_length=1000, default="")
    file_id = models.CharField(max_length=1000, default="")

class RequirementFile(models.Model):
    requirements = models.ForeignKey(Requirements, on_delete=models.CASCADE)
    file_field = models.FileField(default=None, null=True)
##############################

class Homework(models.Model):
    name = models.CharField(max_length=200, default="")
    task_file_id = models.CharField(max_length=1000, default="")
    task_text = models.CharField(max_length=5000, default="")
    task_photo_id = models.CharField(max_length=1000, default="")

    @classmethod
    def make_string_for_choosing_homework(cls):
        text = ""
        homeworks = cls.objects.all()
        for i in range(0, len(homeworks)):
            text += f"{i+1} - {homeworks[i].name}\n"
        return text

    @classmethod
    def deleting_homework(cls, index):
        homeworks = cls.objects.all()
        homeworks[index].delete()

    @classmethod
    def sending_chosed_homewor(cls, index, update: Update):
        text = ""
        homeworks = cls.objects.all()
        text += f"🧭 {homeworks[index].name}\n"
        if homeworks[index].task_text:
            text += f"{homeworks[index].task_text}"
            update.message.reply_text(text=text)
        elif homeworks[index].task_file_id:
            update.message.reply_text(text=text)
            update.message.reply_document(document=homeworks[index].task_file_id)
        elif homeworks[index].task_photo_id:
            update.message.reply_text(text=text)
            update.message.reply_photo(photo=homeworks[index].task_photo_id)

    @classmethod
    def get_num_of_homework(cls):
        return cls.objects.count()
        
class Solution(models.Model):
    name = models.CharField(max_length=200, default="")
    file_id = models.CharField(max_length=1000, default="")
    photo_id = models.CharField(max_length=500, default="")    
    text = models.CharField(max_length=5000, default="")

    @classmethod
    def make_string_for_choosing_solution(cls):
        text = ""
        solutions = cls.objects.all()
        for i in range(len(solutions)):
            text += f"{i+1} - {solutions[i].name}\n"
        return text

    @classmethod
    def deleting_solution(cls, index):
        solutions = cls.objects.all()
        solutions[index].delete()

    @classmethod
    def sending_chosed_solution(cls, index, update: Update):
        text = ""
        solutions = cls.objects.all()
        text += f"🧭 {solutions[index].name}:\n"
        if solutions[index].text:
            text += f"🗺️ {solutions[index].text}\n"
            update.message.reply_text(text=text)
        elif solutions[index].file_id:
            update.message.reply_text(text=text)
            update.message.reply_document(document=solutions[index].file_id)
        elif solutions[index].photo_id:
            update.message.reply_text(text=text)
            update.message.reply_photo(photo=solutions[index].photo_id)

    @classmethod
    def get_num_of_solutions(cls):
        return cls.objects.count()

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
        u, created = cls.objects.update_or_create(user_id=data["user_id"], defaults=data)
        if created:
            # Save deep_link to User model
            if context is not None and context.args is not None and len(context.args) > 0:
                payload = context.args[0]
                if str(payload).strip() != str(data["user_id"]).strip():  # you can't invite yourself
                    u.deep_link = payload
                    u.save()
        return u, created

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

