import pytest
import json
from datetime import datetime
from app import app, db, Student, Grade

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_index(client):
    """Test the main index endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert data['status'] == 'running'

def test_health(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_create_student(client):
    """Test creating a new student"""
    student_data = {
        'roll_number': 'STU001',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'phone': '1234567890',
        'address': '123 Main St',
        'class_name': 'Class A'
    }
    
    response = client.post('/api/students',
                          data=json.dumps(student_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['roll_number'] == 'STU001'
    assert data['first_name'] == 'John'

def test_get_students(client):
    """Test retrieving all students"""
    # Create a student first
    student_data = {
        'roll_number': 'STU001',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'phone': '1234567890',
        'address': '123 Main St',
        'class_name': 'Class A'
    }
    
    client.post('/api/students',
               data=json.dumps(student_data),
               content_type='application/json')
    
    response = client.get('/api/students')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['students']) == 1
    assert data['students'][0]['roll_number'] == 'STU001'

def test_get_student(client):
    """Test retrieving a specific student"""
    # Create a student first
    student_data = {
        'roll_number': 'STU001',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'phone': '1234567890',
        'address': '123 Main St',
        'class_name': 'Class A'
    }
    
    create_response = client.post('/api/students',
                                 data=json.dumps(student_data),
                                 content_type='application/json')
    
    student_id = json.loads(create_response.data)['id']
    
    response = client.get(f'/api/students/{student_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == student_id
    assert data['first_name'] == 'John'

def test_update_student(client):
    """Test updating a student"""
    # Create a student first
    student_data = {
        'roll_number': 'STU001',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'phone': '1234567890',
        'address': '123 Main St',
        'class_name': 'Class A'
    }
    
    create_response = client.post('/api/students',
                                 data=json.dumps(student_data),
                                 content_type='application/json')
    
    student_id = json.loads(create_response.data)['id']
    
    # Update the student
    update_data = {'first_name': 'Jane', 'class_name': 'Class B'}
    response = client.put(f'/api/students/{student_id}',
                         data=json.dumps(update_data),
                         content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['first_name'] == 'Jane'
    assert data['class_name'] == 'Class B'

def test_delete_student(client):
    """Test deleting a student"""
    # Create a student first
    student_data = {
        'roll_number': 'STU001',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'phone': '1234567890',
        'address': '123 Main St',
        'class_name': 'Class A'
    }
    
    create_response = client.post('/api/students',
                                 data=json.dumps(student_data),
                                 content_type='application/json')
    
    student_id = json.loads(create_response.data)['id']
    
    # Delete the student
    response = client.delete(f'/api/students/{student_id}')
    assert response.status_code == 200
    
    # Verify student is deleted
    get_response = client.get(f'/api/students/{student_id}')
    assert get_response.status_code == 404

def test_create_grade(client):
    """Test creating a grade for a student"""
    # Create a student first
    student_data = {
        'roll_number': 'STU001',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'phone': '1234567890',
        'address': '123 Main St',
        'class_name': 'Class A'
    }
    
    create_response = client.post('/api/students',
                                 data=json.dumps(student_data),
                                 content_type='application/json')
    
    student_id = json.loads(create_response.data)['id']
    
    # Add a grade
    grade_data = {
        'student_id': student_id,
        'subject': 'Mathematics',
        'marks': 95.5,
        'grade': 'A',
        'semester': 'Sem 1'
    }
    
    response = client.post('/api/grades',
                          data=json.dumps(grade_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['subject'] == 'Mathematics'
    assert data['grade'] == 'A'

def test_get_student_grades(client):
    """Test retrieving grades for a student"""
    # Create a student
    student_data = {
        'roll_number': 'STU001',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'phone': '1234567890',
        'address': '123 Main St',
        'class_name': 'Class A'
    }
    
    create_response = client.post('/api/students',
                                 data=json.dumps(student_data),
                                 content_type='application/json')
    
    student_id = json.loads(create_response.data)['id']
    
    # Add grades
    grade_data = {
        'student_id': student_id,
        'subject': 'Mathematics',
        'marks': 95.5,
        'grade': 'A',
        'semester': 'Sem 1'
    }
    
    client.post('/api/grades',
               data=json.dumps(grade_data),
               content_type='application/json')
    
    # Get grades
    response = client.get(f'/api/students/{student_id}/grades')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['subject'] == 'Mathematics'