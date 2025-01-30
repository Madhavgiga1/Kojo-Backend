from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
# Create your models here.

class StudentManager(BaseUserManager):
    
    def create_user(self):
        student = self.model()
        student.set_password()
        student.save(using=self._db)

        return student
    
    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        student = self.create_user(email, password)
        
        student.save(using=self._db)

        return student

class Student(AbstractBaseUser,PermissionsMixin):

    application_no=models.BigIntegerField()
    name=models.CharField(max_length=200)


    objects=StudentManager()
    USERNAME_FIELD='application_no'
