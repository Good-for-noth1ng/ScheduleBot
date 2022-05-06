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

    day = models.CharField(max_length=2, choices=Day.choices, default="")
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
    def get_books_by_name(cls, name):
        if cls.objects.all().filter(is_link_to_book=True):
            return cls.objects.all().filter(is_link_to_book=True).filter(name=name)[0]
        else:
            return False

    @classmethod
    def get_urls(cls):
        return cls.objects.all().filter(is_link_to_command=True)

    @classmethod
    def get_urls_by_name(cls, name):
        if cls.objects.all().filter(is_link_to_command=True):
            return cls.objects.all().filter(is_link_to_command=True).filter(name=name)[0]
        else:
            return False

    @classmethod
    def get_books_num(cls):
        return cls.objects.all().filter(is_link_to_book=True).count()

    @classmethod
    def get_urls_num(cls):
        return cls.objects.all().filter(is_link_to_command=True).count()
    
    @classmethod
    def deleting_book_by_name(cls, name):
        ext_res = cls.get_books_by_name(name=name)
        ext_res.delete()

    @classmethod
    def deleting_link_by_name(cls, name):
        ext_res = cls.get_urls_by_name(name=name)
        ext_res.delete()

    @classmethod
    def extract_names_for_keyboard(cls, is_book=False, is_link=False):
        if is_book:
            ext_res = cls.objects.all().filter(is_link_to_book=True)
        elif is_link:
            ext_res = cls.objects.all().filter(is_link_to_command=True)
        buttons = []
        for external_resource in ext_res:
            buttons.append(external_resource.name)
        return buttons

#user sends photo, file or text. This set can be requirement, homework or soluton
#telegram will store these photos and files, db will store the text 
class InternalResource(models.Model):
    name = models.CharField(max_length=2000, default="")    
    text = models.CharField(max_length=5000, default="")
    is_requirement = models.BooleanField(default=False)
    is_homework = models.BooleanField(default=False)
    is_solution = models.BooleanField(default=False)
    is_schedule = models.BooleanField(default=False)

    @classmethod
    def get_requirements(cls):
        return cls.objects.all().filter(is_requirement=True)
    
    @classmethod
    def get_requirement_by_name(cls, name):
        if cls.objects.all().filter(is_requirement=True).filter(name=name):
            return cls.objects.all().filter(is_requirement=True).filter(name=name)[0]
        else:
            return False

    @classmethod
    def get_homeworks(cls):
        return cls.objects.all().filter(is_homework=True)
    
    @classmethod
    def get_homework_by_name(cls, name):
        if cls.objects.filter(is_homework=True).filter(name=name):
            return cls.objects.all().filter(is_homework=True).filter(name=name)[0]
        else:
            return False

    @classmethod
    def get_solutions(cls):
        return cls.objects.all().filter(is_solution=True)

    @classmethod
    def get_solutions_by_name(cls, name):
        if cls.objects.filter(is_solution=True).filter(name=name):
            return cls.objects.filter(is_solution=True).filter(name=name)[0]
        else:
            return False

    @classmethod
    def get_schedule(cls):
        return cls.objects.all().filter(is_schedule=True)

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
    def get_num_of_schedule(cls):
        return cls.objects.all().filter(is_schedule=True).count()

    @classmethod
    def get_name_by_index(cls, index, is_solution=False, is_homework=False, is_requirement=False):
        return cls.objects.filter(is_homework=is_homework, is_solution=is_solution, is_requirement=is_requirement)[index].name

    @classmethod
    def does_exist(cls, name, is_solution=False, is_requirement=False, is_homework=False):
        does_exist = cls.objects.filter(
            name=name, 
            is_requirement=is_requirement, 
            is_homework=is_homework, 
            is_solution=is_solution
        ).exists()
        return does_exist
    
    @classmethod
    def extract_names_for_keyboard(cls, is_requirement=False, is_homework=False, is_solution=False):
        if is_requirement:
            int_res = cls.objects.all().filter(is_requirement=True)
        elif is_homework:
            int_res = cls.objects.all().filter(is_homework=True)
        elif is_solution:
            int_res = cls.objects.all().filter(is_solution=True)
        buttons = []
        for internal_resource in int_res:
            buttons.append(internal_resource.name)
        return buttons

    @classmethod
    def deleting_requirements_by_name(cls, name):
        int_res = cls.get_requirement_by_name(name=name)
        int_res.delete()

    @classmethod
    def deleting_homework_by_name(cls, name):
        int_res = cls.get_homework_by_name(name=name)
        int_res.delete()

    @classmethod
    def deleting_solutions_by_name(cls, name):
        int_res = cls.get_solutions_by_name(name=name)
        int_res.delete()
    

    @classmethod
    def update_int_res(cls, name, is_solution=False, is_requirement=False, is_homework=False, is_schedule=False):
        int_res, created = cls.objects.update_or_create(
            name=name,
            defaults={
                'is_solution': is_solution,
                'is_requirement': is_requirement,
                'is_homework': is_homework,
                'is_schedule': is_schedule
            }
        )
        int_res.save()
        return int_res

class InternalResourceFile(models.Model):
    internal_resource = models.ForeignKey(to=InternalResource, on_delete=models.CASCADE, null=True, blank=True)
    photo_id = models.CharField(max_length=500, default="")
    file_id = models.CharField(max_length=500, default="")

    @classmethod
    def get_files(cls, internal_resource):
        return cls.objects.all().filter(internal_resource=internal_resource)
    
    @classmethod
    def delete_chosen_file(cls, index):
        internal_resource = InternalResource.get_schedule()
        internal_files = cls.get_files(internal_resource=internal_resource[0])
        internal_files[index].delete()

    @classmethod
    def get_files_num(cls, internal_resource):
        return cls.objects.all().filter(internal_resource=internal_resource).count()
        
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

