'''Cache functions'''

from django.contrib.auth.models import User

from drf_cached_reads.cache import BaseCache
from .models import Browser, Version


class Cache(BaseCache):
    '''Instance Cache for webplatformcompat'''
    versions = ('v1',)
    default_version = 'v1'

    def browser_v1_serializer(self, obj):
        if not obj:
            return None
        history_pks = getattr(
            obj, '_history_pks',
            list(obj.history.all().values_list('history_id', flat=True)))
        versions_pks = list(obj.versions.values_list('pk', flat=True))
        return dict((
            ('id', obj.pk),
            ('slug', obj.slug),
            ('icon', obj.icon),
            ('name', obj.name),
            ('note', obj.note),
            self.field_to_json(
                'PKList', 'history', model=obj.history.model,
                pks=history_pks),
            self.field_to_json(
                'PK', 'history_current', model=obj.history.model,
                pk=history_pks[0]),
            self.field_to_json(
                'PKList', 'versions', model=Version, pks=versions_pks),
        ))

    def browser_v1_loader(self, pk):
        queryset = Browser.objects.select_related('versions__pk')
        try:
            obj = queryset.get(pk=pk)
        except Browser.DoesNotExist:
            return None
        else:
            obj._history_pks = list(
                obj.history.all().values_list('history_id', flat=True))
            return obj

    def browser_v1_invalidator(self, obj):
        return []

    def version_v1_serializer(self, obj):
        if not obj:
            return None
        history_pks = getattr(
            obj, '_history_pks',
            list(obj.history.all().values_list('history_id', flat=True)))
        return dict((
            ('id', obj.pk),
            ('version', obj.version),
            self.field_to_json('Date', 'release_day', obj.release_day),
            self.field_to_json('Date', 'retirement_day', obj.retirement_day),
            ('status', obj.status),
            ('release_notes_uri', obj.release_notes_uri),
            ('note', obj.note),
            ('_order', obj._order),
            self.field_to_json(
                'PK', 'browser', model=Browser, pk=obj.browser_id),
            self.field_to_json(
                'PKList', 'history', model=obj.history.model,
                pks=history_pks),
            self.field_to_json(
                'PK', 'history_current', model=obj.history.model,
                pk=history_pks[0]),
        ))

    def version_v1_loader(self, pk):
        queryset = Version.objects
        try:
            obj = queryset.get(pk=pk)
        except Version.DoesNotExist:
            return None
        else:
            obj._history_pks = list(
                obj.history.all().values_list('history_id', flat=True))
            return obj

    def version_v1_invalidator(self, obj):
        return [
            ("Browser", obj.browser_id, True)]

    def historicalbrowser_v1_serializer(self, obj):
        if not obj:
            return None
        return dict((
            ('id', obj.history_id),
            self.field_to_json('DateTime', 'date', obj.history_date),
            ('event', obj.get_history_type_display().lower()),
            self.field_to_json(
                'PK', 'user', model=User, pk=obj.history_user_id),
            self.field_to_json(
                'PK', 'browser', model=Browser, pk=obj.id),
            ('browsers', {
                'id': obj.id,
                'slug': obj.slug,
                'icon': obj.icon,
                'name': obj.name,
                'note': obj.note,
                'history_current': obj.history_id
            }),
        ))

    def historicalbrowser_v1_loader(self, pk):
        queryset = Browser.history
        try:
            return queryset.get(history_id=pk)
        except Browser.history.model.DoesNotExist:
            return None

    def historicalbrowser_v1_invalidator(self, obj):
        return []

    def user_v1_serializer(self, obj):
        if not obj or not obj.is_active:
            return None
        return dict((
            ('id', obj.id),
            ('username', obj.username),
            self.field_to_json('DateTime', 'date_joined', obj.date_joined),
        ))

    def user_v1_loader(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def user_v1_invalidator(self, obj):
        return []