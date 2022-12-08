from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


class M2MCreateDelete():
    def m2m_create_delete(
        self,
        obj1_m2m_manager,
        obj2,
        request,
        serializer,
        errors
    ):
        if request.method == 'POST':
            if obj1_m2m_manager.filter(id=obj2.id).exists():
                raise ValidationError(
                    {'errors': errors['create_fail']}
                )
            try:
                obj1_m2m_manager.add(obj2)
            except IntegrityError as e:
                raise ValidationError(
                    {'errors': e}
                )
            context = self.get_serializer_context()
            response = Response(
                serializer(instance=obj2, context=context).data,
                status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            if not obj1_m2m_manager.filter(id=obj2.id).exists():
                raise ValidationError(
                    {'errors': 'Этого рецепта нет в избранном'})
            obj1_m2m_manager.remove(obj2.id)
            response = Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError(
                {'errors': f'Метод {request.method} не поддерживается'})

        return response
