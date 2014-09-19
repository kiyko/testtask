import sys

from django.contrib import admin

from probe import models


def setup_admin():
    mod = sys.modules[__name__]  # current module
    mdls = models.get_models()  # classes of all models
    # Creates admin models
    for (cls_name, cls) in mdls:
        setattr(mod, cls_name, type(cls_name, (admin.ModelAdmin,),
                                    {'__module__': __name__}))
        admin.site.register(cls, getattr(mod, cls_name))


setup_admin()
