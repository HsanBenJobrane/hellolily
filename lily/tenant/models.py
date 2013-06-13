from django.db import models
from django.conf import settings

from lily.tenant.middleware import get_current_user


class TenantManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        """
        Manipulate the returned query set by adding a filter for tenant using the tenant linked
        to the current logged in user (received via custom middleware).
        """
        user = get_current_user()
        if user and user.is_authenticated():
            return super(TenantManager, self).get_query_set().filter(tenant=user.tenant)
        else:
            return super(TenantManager, self).get_query_set()


class Tenant(models.Model):
    pass

    def __unicode__(self):
        return unicode("%s %s" % (self._meta.verbose_name.title(), self.pk))


class MultiTenantMixin(models.Model):
    # Automatically filter any queryset by tenant if logged in
    objects = TenantManager()

    # blank=True to allow form validation (tenant is set upon model.save)
    tenant = models.ForeignKey(Tenant, blank=True)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.is_authenticated():
            self.tenant = user.tenant

        return super(MultiTenantMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class SingleTenantMixin(models.Model):
    tenant = models.ForeignKey(Tenant, blank=True)

    def save(self, *args, **kwargs):
        self.tenant = Tenant.objects.get_or_create(pk=1)[0]
        return super(SingleTenantMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True


TenantMixin = SingleTenantMixin
if settings.MULTI_TENANT:
    TenantMixin = MultiTenantMixin
