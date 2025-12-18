import os
import json
import datetime

class DataRecord:
    def __init__(self):
        self.income = []
        self.expenses = []

    def count_total(self):
        return sum(self.income) - sum(self.expenses)

    def add_income(self, amount):
        self.income.append(amount)

    def add_expense(self, amount):
        self.expenses.append(amount)

    def clear(self):
        self.income = []
        self.expenses = []


class DataManager:
    @staticmethod
    def load_users():
        if not os.path.exists("users.json"):
            return {}
        try:
            with open("users.json", 'r') as f:
                return json.load(f)
        except:
            return {}

    @staticmethod
    def save_users(users):
        with open("users.json", 'w') as f:
            json.dump(users, f, indent=4)

    @staticmethod
    def load_user_data(current_user):
        """加载指定用户的数据，返回 (transactions, goals, budget, data_record)"""
        transactions = []
        goals = []
        monthly_goal = 0.0
        data_record = DataRecord()

        if not os.path.exists("transactions.json"):
            return transactions, goals, monthly_goal, data_record

        try:
            with open("transactions.json", 'r', encoding='utf-8') as f:
                content = json.load(f)

            all_data = content if isinstance(content, dict) else {}
            user_data = all_data.get(current_user, {})

            # 兼容旧数据格式
            if isinstance(user_data, list):
                raw_trans = user_data
            else:
                raw_trans = user_data.get('transactions', [])
                goals = user_data.get('goals', [])
                monthly_goal = user_data.get('budget', 0)

            for item in raw_trans:
                # 转换日期字符串为对象
                try:
                    if isinstance(item['date'], str):
                        item['date'] = datetime.datetime.strptime(item['date'], "%Y-%m-%d %H:%M:%S")
                except:
                    item['date'] = datetime.datetime.now()

                transactions.append(item)
                if item['type'] == 'Income':
                    data_record.add_income(item['amount'])
                elif item['type'] == 'Expenses':
                    data_record.add_expense(item['amount'])

        except Exception as e:
            print(f"Error loading data: {e}")

        return transactions, goals, monthly_goal, data_record

    @staticmethod
    def save_user_data(current_user, transactions, goals, budget):
        all_data = {}
        if os.path.exists("transactions.json"):
            try:
                with open("transactions.json", 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    if isinstance(content, dict):
                        all_data = content
            except:
                pass

        # 序列化
        serializable_list = []
        for t in transactions:
            copy_t = t.copy()
            if isinstance(t['date'], (datetime.date, datetime.datetime)):
                copy_t['date'] = t['date'].strftime("%Y-%m-%d %H:%M:%S")
            serializable_list.append(copy_t)

        user_data = {
            "transactions": serializable_list,
            "goals": goals,
            "budget": budget
        }
        all_data[current_user] = user_data

        with open("transactions.json", 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=4)
