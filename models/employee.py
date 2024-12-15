from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client['EmployeeMS']
employee_collection = db['employee']

class Employee:
    def __init__(self, name, position, contact, salary=None, department=None):
        self.name = name
        self.position = position
        self.contact = contact
        self.salary = salary
        self.department = department
        self.hire_date = datetime.now()
        self.status = "active"
    
    def save_to_db(self):
        employee_data = {
            "name": self.name,
            "position": self.position,
            "contact": self.contact,
            "salary": self.salary,
            "department": self.department,
            "hire_date": self.hire_date,
            "status": self.status
        }
        result = employee_collection.insert_one(employee_data)
        return result.acknowledged

    @staticmethod
    def get_employees_by_name(name=None, contact=None):
        if name:
            employees = employee_collection.find({"name": {"$regex": name, "$options": "i"}})
        elif contact:
            employees = employee_collection.find({"contact": contact})
        else:
            employees = []
        return list(employees)
   
    @staticmethod
    def update_employee(contact, update_data):
        result = employee_collection.update_one(
            {"contact": contact},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def get_employees_by_contact(contact):
        employees = employee_collection.find({"contact": contact})
        return list(employees)
    
    @staticmethod
    def delete_employee(contact):
        result = employee_collection.delete_one({"contact": contact})
        return result.deleted_count > 0
