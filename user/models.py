from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.timezone import now
class UserManager(BaseUserManager):
    def create_user(self, user_name, user_pwd, identity):
        if not user_name:
            raise ValueError('用户名不能为空')
        user = self.model(user_name=user_name)
        user.set_password(user_pwd)
        user.identify = identity

        user.save(using=self._db)
        return user

class User_log(AbstractBaseUser):
    user_name = models.CharField(max_length=20, unique=True, primary_key=True)
    user_pwd = models.CharField(max_length=128, null=False)
    identity = models.CharField(max_length=30, null=False)
    opaque_password = models.CharField(max_length=100, null=False)
    last_login = models.DateTimeField(default=now)  # 添加 last_login 字段
    objects = UserManager()

    def check_password(self, raw_password):
        print(self.user_pwd)
        print(self.password)
        print(raw_password)
        if self.user_pwd == raw_password:
            return True
        return False

    def __str__(self):
        return self.user_name
