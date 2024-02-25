from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.dispatch import receiver
from django.db.models.signals import post_save

class Profile(models.Model):
    user = models.OneToOneField(
        verbose_name="Профиль",
        editable=True,
        blank=True,
        null=True,
        default=None,
        to=User,
        on_delete=models.CASCADE,
        related_name="profile",
        unique=True
    )
    is_active = models.BooleanField(verbose_name="Активность профиля", default=True)
    class Meta:
        app_label = 'auth'
        ordering = ("user",)
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"{self.user.username}"


@receiver(post_save, sender=User)
def auto_user_model(sender, instance, created, **kwargs):
    Profile.objects.get_or_create(user=instance)


class BusIdea(models.Model):
    author = models.ForeignKey(verbose_name="Автор", to=User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(verbose_name="Заголовок", max_length=200)
    description = models.TextField(verbose_name="Описание", max_length=5000)
    image = models.ImageField(verbose_name="Фотография", upload_to="images/post/", blank=True, null=True, default=None)
    file = models.FileField(verbose_name="Файл", upload_to="files/post/", null=True, blank=True)
    is_active = models.BooleanField(verbose_name="Активно", default=True)
    date_time = models.DateTimeField(verbose_name="Дата", default=now)

    class Meta:
        app_label = "my1"
        ordering = ("-date_time",)
        verbose_name = "Бизнес-идея"
        verbose_name_plural = "Бизнес-идеи"

    def __str__(self):
        return f"({self.id}) {self.title}"


class Vacan(models.Model):
    job = models.CharField(verbose_name="Должность", max_length=200)
    description = models.TextField(verbose_name="Описание", max_length=5000)
    contacts = models.CharField(verbose_name="Контакты", max_length=300)
    is_active = models.BooleanField(verbose_name="Активно", default=True)
    date_time = models.DateTimeField(verbose_name="Дата", default=now)
    file = models.FileField(verbose_name="Файл", upload_to="files/post/", null=True, blank=True)

    class Meta:
        app_label = "my1"
        ordering = ("-date_time",)
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"

    def __str__(self):
        return f"job_{self.job}"


class BusIdeaCom(models.Model):
    idea = models.ForeignKey(verbose_name="Прокомментированная идея", to=BusIdea, on_delete=models.CASCADE)
    author = models.ForeignKey(verbose_name="Автор", to=User, on_delete=models.CASCADE)
    text = models.TextField("Комментарий", max_length=2000, null=False)
    date_time = models.DateTimeField("Дата", default=now)
    is_active = models.BooleanField(verbose_name="Активно", default=True)
    class Meta:
        app_label = "my1"
        ordering = ("-date_time", "idea")
        verbose_name = "Комментарий под идеей"
        verbose_name_plural = "Комментарии под идеями"

    def __str__(self):
        return f"{self.idea}_Комментарий: {self.text[:15]}.."


class BusIdeaLikes(models.Model):
    author = models.ForeignKey(verbose_name="Оценил идею", to=User, on_delete=models.CASCADE)
    idea = models.ForeignKey(verbose_name="Оцененная идея", to=BusIdea, on_delete=models.CASCADE)
    is_liked = models.BooleanField(verbose_name="Оценка", default=False)

    class Meta:
        app_label = "my1"
        ordering = ("-idea", "author", "is_liked")
        verbose_name = "Лайк к идее"
        verbose_name_plural = "Лайки к идеям"

    def __str__(self):
        if self.is_liked:
            like = "Лайк"
        else:
            like = "Дизлайк"
        return f"{self.idea.title} {self.author.username} {like}"


class Products(models.Model):
    product = models.CharField(verbose_name="Товар", max_length=255, null=False)
    amount = models.CharField(verbose_name="Кол-во(штук)", max_length=50, default="шт.")

    class Meta:
        app_label = "my1"
        ordering = ('product',)
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return f"{self.product}- {self.amount}"


class Room(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    class Meta:
        app_label = "my1"
        ordering = ('name',)
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"


class Message(models.Model):
    room = models.ForeignKey(Room, verbose_name="Комната", related_name="messages", on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name="Пользователь", related_name="messages", on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "my1"
        ordering = ('-date_added',)
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
