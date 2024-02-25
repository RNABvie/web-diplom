from django.contrib import admin
from . import models


class BusIdeaAdmin(admin.ModelAdmin):
    """display bus-idea"""
    list_display = ("author", "title", "description", "image", "file", "date_time", "is_active")
    list_display_links = ("author",)
    list_editable = ("is_active",)
    list_filter = ("is_active", "date_time", "author", "title", "image", "file")
    fieldsets = (
        (
            "Основное", {"fields": ("author", "title", "description", "image", "file", "date_time")}
        ),
        (
            "Техническое", {"fields": ("is_active",)}
        ),
    )
    search_fields = ["author", "title", "description", "date_time"]


class BusIdeaComAdmin(admin.ModelAdmin):
    """display bus-idea-comments"""
    list_display = ("author", "text", "idea", "is_active", "date_time")
    list_display_links = ("author",)
    list_editable = ("is_active",)
    list_filter = ("is_active", "date_time", "author", "text")
    fieldsets = (
        (
            "Основное", {"fields": ("author", "text", "idea", "date_time")}
        ),
        (
            "Техническое", {"fields": ("is_active",)}
        ),
    )
    search_fields = ["author", "text", "idea", "date_time"]


class VacanAdmin(admin.ModelAdmin):
    """display vacancy"""
    list_display = ("job", "description", "contacts", "file", "date_time", "is_active")
    list_display_links = ("job",)
    list_editable = ("is_active",)
    list_filter = ("is_active", "date_time", "job")
    fieldsets = (
        (
            "Основное", {"fields": ("job", "description", "contacts", "file", "date_time")}
        ),
        (
            "Техническое", {"fields": ("is_active",)}
        ),
    )
    search_fields = ["job", "description", "date_time"]


class ProductsAdmin(admin.ModelAdmin):
    """display vacancy"""
    list_display = ("product", "amount")
    list_display_links = ("product",)
    list_editable = ('amount',)
    list_filter = ("product", "amount")

    search_fields = ["product", "amount"]


admin.site.register(models.Profile)
admin.site.register(models.Message)
admin.site.register(models.Room)

admin.site.register(models.BusIdea, BusIdeaAdmin)
admin.site.register(models.BusIdeaCom, BusIdeaComAdmin)
admin.site.register(models.BusIdeaLikes)

admin.site.register(models.Vacan, VacanAdmin)
admin.site.register(models.Products, ProductsAdmin)

