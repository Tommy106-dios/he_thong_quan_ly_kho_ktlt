# -*- coding: utf-8 -*-

class User:
    """Thực thể Người dùng (Nhân viên)"""
    def __init__(self, id, username, password, full_name, role):
        self.id = id
        self.username = username
        self.password = password
        self.full_name = full_name
        self.role = role  # Ví dụ: Admin, NhanVienKho

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "fullName": self.full_name,
            "role": self.role
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get("id"),
            username=data.get("username"),
            password=data.get("password"),
            full_name=data.get("fullName"),
            role=data.get("role")
        )
