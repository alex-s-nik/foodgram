from typing import Dict, Union
from django.db.models import Manager, Model
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, SerializerMetaclass


class M2MAddRemoveHelper:
    '''
    Вспомогательный миксин для добавления объекта в другой 
    или удаления объекта из другого,
    связанного соотношением Many-to-Many.
    '''
    def m2m_add_remove(
        self,
        m2m_manager_of_changing_object: Manager,
        object_for_action: Model,
        object_serializer: Union[ModelSerializer, SerializerMetaclass],
        request_method: str,
        fail_messages: Dict[str, str]
    ) -> Response:
        '''
        Добавляет в объект другой объект, связанный
        отношением Many-to-Many

        Параметры:

        m2m_manager_of_changing_object - many-to-many manager объекта,
        в который надо добавить другой объект

        object_for_action - добавляемый объект

        object_serializer - сериализатор добавляемого объекта

        request_method - название HTTP-метода из запроса на действие

        fail_message - сообщение об ошибке при добавлении
        '''
        if request_method == 'POST':
            return self._m2m_add(
                m2m_manager_of_changing_object=m2m_manager_of_changing_object,
                object_for_action=object_for_action,
                object_serializer=object_serializer,
                fail_message=fail_messages['add_fail']
            )
        elif request_method == 'DELETE':
            return self._m2m_remove(
                m2m_manager_of_changing_object=m2m_manager_of_changing_object,
                object_for_action=object_for_action,
                fail_message=fail_messages['remove_fail']
            )
        else:
            raise ValidationError(
                {'errors': f'Метод {request_method} не поддерживается'}
            )

    def _m2m_add(
        self,
        m2m_manager_of_changing_object: Manager,
        object_for_action: Model,
        object_serializer: Union[ModelSerializer, SerializerMetaclass],
        fail_message: str
    ) -> Response:
        if m2m_manager_of_changing_object.filter(
            id=object_for_action.id
        ).exists():
            raise ValidationError(
                {'errors': fail_message}
            )
        
        try:
            m2m_manager_of_changing_object.add(object_for_action)
        except IntegrityError as e:
            raise ValidationError(
                {'errors': fail_message}
            )
        
        context = self.get_serializer_context()
        return Response(
            object_serializer(instance=object_for_action, context=context).data,
            status=status.HTTP_201_CREATED
        )
        
    def _m2m_remove(
        self,
        m2m_manager_of_changing_object: Manager,
        object_for_action: Model,
        fail_message: str
    ) -> Response:
        if not m2m_manager_of_changing_object.filter(
            id=object_for_action.id
        ).exists():
            raise ValidationError(
                {'errors': fail_message}
            )

        m2m_manager_of_changing_object.remove(object_for_action.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
