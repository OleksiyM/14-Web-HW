"""
Role Access Services
"""

from fastapi import Request, Depends, HTTPException, status
from entity.models import Role, User
from services.auth import auth_service
from conf.messages import FORBIDDEN


class RoleAccess:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, user: User = Depends(auth_service.get_current_user)):
        # print(user.role, self.allowed_roles)
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=FORBIDDEN)
