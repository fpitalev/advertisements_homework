from rest_framework.permissions import BasePermission


class IsAdvertisementAuthor(BasePermission):
    message = "Изменять и удалять объявление может только его автор."

    def has_object_permission(self, request, view, obj):
        return obj.creator_id == request.user.id
