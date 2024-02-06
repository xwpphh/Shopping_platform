# Register your models here.
from django.contrib import admin


from .models import User
from .models import Addr
from .models import Area
from .models import VerifCode


"""
hxp
12345678
"""

admin.site.register(User)
admin.site.register(Addr)
admin.site.register(Area)
admin.site.register(VerifCode)