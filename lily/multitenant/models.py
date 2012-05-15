from django.db import models

from lily.multitenant.middleware import get_current_user


class MultiTenantManager(models.Manager):
    use_for_related_fields = True
    
    def get_query_set(self):
        """
        Manipulate the returned query set by adding a filter for tenant by using the tenant linked
        to the current logged in user (received via custom middleware).
        """
        user = get_current_user()
        if user and user.is_authenticated():
            return super(MultiTenantManager, self).get_query_set().filter(tenant=user.tenant)
        else:
            return super(MultiTenantManager, self).get_query_set()


class Tenant(models.Model):
    pass


class MultiTenantMixin(models.Model):
    # Automatically filter any queryset by tenant if logged in
    objects = MultiTenantManager()
    
    # blank=True to allow form validation (tenant is set upon model.save)
    tenant = models.ForeignKey(Tenant, blank=True)
    
    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.is_authenticated():
            self.tenant = user.tenant
        
        return super(MultiTenantMixin, self).save(*args, **kwargs)
    
    class Meta:
        abstract = True