from typing import Dict, Any, Optional, Union
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder


class BaseResponse:

    def __init__(
            self,
            is_success: bool = False,
            message: str = "",
            data: Optional[Dict[str, Any]] = None,
            status_code: int = 200
    ):
        self.is_success = is_success
        self.message = message
        self.data = data or {}
        self.status_code = status_code
        self._errors = {}
        self._warnings = []
        self._meta = {}

    def add_error(self, field: str, message: str) -> None:
        """Add field-specific error message"""
        if field not in self._errors:
            self._errors[field] = []
        self._errors[field].append(message)

    def add_warning(self, message: str) -> None:
        """Add a warning message"""
        self._warnings.append(message)

    def add_meta(self, key: str, value: Any) -> None:
        """Add metadata to response"""
        self._meta[key] = value

    def to_dict(self, include_empty: bool = False) -> Dict[str, Any]:
        """Convert response to dictionary"""
        result = {
            'status': 'success' if self.is_success else 'error',
            'message': self.message,
            'data': self.data,
        }

        if include_empty or self._errors:
            result['errors'] = self._errors

        if include_empty or self._warnings:
            result['warnings'] = self._warnings

        if include_empty or self._meta:
            result['meta'] = self._meta

        return result

    def to_json_response(self, include_empty: bool = False) -> JsonResponse:
        """Convert to Django JsonResponse"""
        return JsonResponse(
            self.to_dict(include_empty),
            status=self.status_code,
            encoder=DjangoJSONEncoder,
            safe=False
        )


class AjaxResponse(BaseResponse):
    """
    Enhanced AJAX response handler with form and datatable support
    """

    def __init__(
            self,
            is_success: bool = False,
            message: str = "",
            data: Optional[Dict[str, Any]] = None,
            forms: Optional[Dict[str, Any]] = None,
            datatable: Optional[Dict[str, Any]] = None,
            status_code: int = 200
    ):
        super().__init__(is_success, message, data, status_code)
        self._forms = forms or {}
        self._datatable = datatable or {}

    def add_form(self, form_name: str, form_data: Dict[str, Any]) -> None:
        """Add form data to response"""
        self._forms[form_name] = form_data

    def get_form(self, form_name: str) -> Dict[str, Any]:
        """Get form data by name"""
        return self._forms.get(form_name, {})

    def set_datatable(
            self,
            data: list,
            total_records: int,
            filtered_records: Optional[int] = None,
            extra_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Configure datatable response"""
        self._datatable = {
            'data': data,
            'recordsTotal': total_records,
            'recordsFiltered': filtered_records or total_records,
            **(extra_data or {})
        }

    def to_dict(self, include_empty: bool = False) -> Dict[str, Any]:
        """Convert response to dictionary with forms and datatable"""
        result = super().to_dict(include_empty)

        if include_empty or self._forms:
            result['forms'] = self._forms

        if include_empty or self._datatable:
            result.update(self._datatable)

        return result

    def set_redirect(self, url: str, delay: int = 0) -> None:
        """Set redirect information"""
        self.data['redirect'] = {
            'url': url,
            'delay': delay
        }

    @classmethod
    def from_exception(cls, exception: Exception, status_code: int = 400) -> 'AjaxResponse':
        """Create error response from exception"""
        response = cls(is_success=False, message=str(exception), status_code=status_code)

        if hasattr(exception, 'error_dict'):
            for field, errors in exception.error_dict.items():
                for error in errors:
                    response.add_error(field, str(error))

        return response


class APIResponse(BaseResponse):
    """
    Standardized API response format
    """

    def to_dict(self, include_empty: bool = False) -> Dict[str, Any]:
        """Standard API response format"""
        return {
            'success': self.is_success,
            'code': self.status_code,
            'message': self.message,
            'data': self.data,
            'errors': self._errors if (include_empty or self._errors) else None,
            'warnings': self._warnings if (include_empty or self._warnings) else None,
            'meta': self._meta if (include_empty or self._meta) else None,
        }