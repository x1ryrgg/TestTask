import pytest
from io import StringIO
from Main import Employee, ReportGenerator
import json


@pytest.fixture
def sample_csv_data():
    return """id,email,name,department,hours_worked,hourly_rate
1,alice@example.com,Alice Johnson,Marketing,160,50
2,bob@example.com,Bob Smith,Design,150,40
3,carol@example.com,Carol Williams,Design,170,60"""


@pytest.fixture
def sample_csv_data_alt_rate():
    return """id,email,name,department,hours_worked,rate
4,dave@example.com,Dave Brown,IT,120,30
5,eve@example.com,Eve Davis,IT,140,35"""


def test_employee_creation():
    row = {
        'id': '1',
        'email': 'test@example.com',
        'name': 'Test User',
        'department': 'Test Dept',
        'hours_worked': '160',
        'rate': '50'
    }
    emp = Employee(row)
    assert emp.name == 'Test User'
    assert emp.department == 'Test Dept'
    assert emp.hours_worked == 160
    assert emp.rate == 50
    assert emp.payout == 8000


def test_employee_with_alt_rate_names():
    row1 = {'hourly_rate': '50'}
    row2 = {'rate': '60'}
    row3 = {'salary': '70'}

    emp1 = Employee(row1)
    emp2 = Employee(row2)
    emp3 = Employee(row3)

    assert emp1.rate == 50
    assert emp2.rate == 60
    assert emp3.rate == 70


def test_read_csv(sample_csv_data):
    with StringIO(sample_csv_data) as f:
        data = ReportGenerator.check_csv_file(f)
    assert len(data) == 3
    assert data[0]['name'] == 'Alice Johnson'
    assert data[1]['department'] == 'Design'


def test_generate_payout_report(sample_csv_data):
    with StringIO(sample_csv_data) as f:
        data = ReportGenerator.check_csv_file(f)
    employees = [Employee(row) for row in data]
    report = ReportGenerator.crt_payout_report(employees)

    assert 'Marketing' in report
    assert 'Design' in report
    assert len(report['Design']['employees']) == 2
    assert report['Marketing']['total_payout'] == 8000
    assert report['Design']['total_payout'] == 16200


def test_format_payout_report(sample_csv_data):
    with StringIO(sample_csv_data) as f:
        data = ReportGenerator.check_csv_file(f)
    employees = [Employee(row) for row in data]
    report = ReportGenerator.crt_payout_report(employees)
    formatted = ReportGenerator.format_of_report(report)

    assert 'Alice Johnson' in formatted
    assert 'Bob Smith' in formatted
    assert 'Carol Williams' in formatted
    assert '8000' in formatted
    assert '16200' in formatted


def test_empty_file():
    data = ReportGenerator.check_csv_file(StringIO(""))
    assert data == []


def test_csv_with_only_header():
    data = ReportGenerator.check_csv_file(StringIO("id,name,department"))
    assert data == []