import argparse
import json
from collections import defaultdict
from typing import Dict, List, Tuple, Any, Callable
from abc import ABC, abstractmethod


class Employee:
    def __init__(self, row: Dict[str, str]):
        self.id = row.get('id', '')
        self.email =row.get('email', '')
        self.name = row.get('name', '')
        self.department = row.get('department', '')
        self.hours_worked = float(row.get('hours_worked', 0))

        rate_keys = ['hourly_rate', 'rate', 'salary']
        self.rate = 0
        for key in rate_keys:
            if key in row:
                self.rate = float(row[key])
                break

    @property
    def payout(self):
        return self.hours_worked * self.rate


class Report(ABC):
    @abstractmethod
    def generate(self, employees: List[Employee]) -> Any:
        pass

    @abstractmethod
    def format(self, report_data: Any) -> str:
        pass


class PayoutReport:

    def generate(self, employees: List[Employee]):
        departments = defaultdict(list)
        for employee in employees:
            departments[employee.department].append(employee)

        report = {}
        for department, employees in departments.items():
            department_data = {
                "employees": [],
                "total_hours": 0,
                "total_payout": 0
            }

            for employee in sorted(employees, key=lambda x: x.name):
                department_data['employees'].append({
                    'name': employee.name,
                    'email': employee.email,
                    'hours': employee.hours_worked,
                    'rate': employee.rate,
                    'payout': employee.payout
                })
                department_data['total_hours'] += employee.hours_worked
                department_data['total_payout'] += employee.payout

            report[department] = department_data

        return report

    def format(self, report_data: Dict[str, Any]) -> str:
        output = []
        for department, data in report_data.items():
            output.append(department)
            output.append("-" * len(department))

            for emp in data["employees"]:
                output.append(
                    f"{emp['name']:>20} {emp['hours']:>10} {emp['rate']:>10} ${emp['payout']:>10.2f}"
                )

            output.append(
                f"{'Total':>20} {data['total_hours']:>10} {'':>10} ${data['total_payout']:>10.2f}"
            )
            output.append("")

        return "\n".join(output)


class AvgRateReport(Report):

    def generate(self, employees: List[Employee]) -> Dict[str, Any]:
        departments = defaultdict(list)
        for emp in employees:
            departments[emp.department].append(emp)

        report = {}
        for dept, emps in departments.items():
            total_rate = sum(emp.rate for emp in emps)
            avg_rate = total_rate / len(emps) if emps else 0

            report[dept] = {
                "employee_count": len(emps),
                "total_rate": total_rate,
                "avg_rate": avg_rate,
                "employees": [emp.name for emp in emps]
            }

        return report

    def format(self, report_data: Dict[str, Any]) -> str:
        output = ["Отчет по средней ставке по отделам", "=" * 40]
        for department, data in report_data.items():
            output.append(f"\nОтдел: {department}")
            output.append(f"Количество сотрудников: {data['employee_count']}")
            output.append(f"Средняя ставка: ${data['avg_rate']:.2f}/час")
            output.append(f"Сотрудники: {', '.join(data['employees'])}")

        return "\n".join(output)


class ReportGenerator:
    @staticmethod
    def check_csv_file(file_path: str) -> List[Dict[str, str]]:
        if isinstance(file_path, str):
            with open(file_path, 'r') as f:
                lines = f.readlines()
        else:
            file_path.seek(0)
            lines = file_path.readlines()

        if not lines:
            return []

        headers = [h.strip() for h in lines[0].split(',')]
        data = []

        for line in lines[1:]:
            values = [v.strip() for v in line.split(',')]
            if len(values) != len(headers):
                continue
            data.append(dict(zip(headers, values)))

        return data

    @staticmethod
    def get_report(report_type: str) -> Report:
        reports = {
            'payout': PayoutReport(),
            'avg_rate': AvgRateReport()
        }

        if report_type not in reports:
            raise ValueError(f"Unknown report type: {report_type}. "
                             f"Available reports: {', '.join(reports.keys())}")

        return reports[report_type]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_files', nargs='+')
    parser.add_argument('--report', required=True, help='payout or avg_rate ')

    args = parser.parse_args()

    try:
        report = ReportGenerator.get_report(args.report)
    except ValueError as e:
        print(e)
        return

    employees = []
    for csv_file in args.csv_files:
        try:
            data = ReportGenerator.check_csv_file(csv_file)
            employees.extend([Employee(row) for row in data])
        except Exception as e:
            print(f"Ошибка при обработке файла {csv_file}: {e}")

    if not employees:
        print((" Должны быть указаны сотрудники. "))
        return

    report_data = report.generate(employees)
    print(report.format(report_data))
    print("\n Вывод в Json")
    print(json.dumps(report_data, indent=2))


if __name__ == '__main__':
    main()