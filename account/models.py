from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None, user_type="student"):
        if not email:
            raise ValueError("Les utilisateurs doivent avoir une adresse e-mail")
        if not username:
            raise ValueError("Les utilisateurs doivent avoir un nom d'utilisateur")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            user_type=user_type,
        )

        user.set_password(password)
        user.is_staff = True

        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, user_type="admin"):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
            user_type="admin",
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    user_type = models.CharField(max_length=255, default="Student")
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=255,default='')
    country = models.CharField(max_length=50,default='Morocco')
    picture = models.ImageField(upload_to='profile_pics', null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "user_type"]

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
    





class Professeur(models.Model):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='professeur')

    def __str__(self):
        return self.user.username

class Course(models.Model):
    professor = models.ForeignKey(Professeur, on_delete=models.CASCADE, default=1)
    course_title = models.CharField(max_length=60 , unique=True)
    course_level = models.CharField(max_length=100)
    course_description = models.TextField()
    course_pdf = models.FileField(upload_to='pdfs/')
    video_url = models.URLField()
    cover_image = models.ImageField(upload_to='images/', blank=True)
    duration_hours = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=0)
    created_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.course_title



class Etudiant(models.Model):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    date_inscription = models.DateField(auto_now_add=True)
    is_subscribed = models.BooleanField(default=False)
    courses = models.ManyToManyField(Course, through='Enrollment')

    def __str__(self):
        return self.user.username

class Enrollment(models.Model):
    student = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    is_opened = models.BooleanField(default=False)

    def __str__(self):
        return f"Enrollment: {self.student.user.username} - {self.course.course_title}"


class DemandeAcces(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, limit_choices_to={'user_type': 'teacher'})
    date_demande = models.DateField(auto_now_add=True)
    accepte = models.BooleanField(default=False)

    def __str__(self):
        return f"Demande d'accès de {self.user.username}"
    


#Quiz
class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    quiz_name = models.CharField(max_length=255,default="test quiz")
    quiz_duration = models.IntegerField(default=0)

    def __str__(self):
        return f"Quiz for {self.course}: {self.quiz_name}"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)

    def __str__(self):
        return self.question_text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.response_text