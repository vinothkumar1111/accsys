from django.contrib import admin
from .models import *


# Alternatively, you can register the models using admin.site.register without the decorator:
admin.site.register(Project)
admin.site.register(Issue)
admin.site.register(Todolist)
admin.site.register(TodolistFile)
admin.site.register(ArchivedProject)
admin.site.register(Task)
# admin.site.register(DeletedTask)
admin.site.register(ArchivedUser)
# admin.site.register(DeletedTask)






