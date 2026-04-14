"""
清空数据库但保留用户表
"""
import pymysql
import os

# 项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from config import DB_CONFIG

def clear_database():
    """清空除用户外的所有表"""
    mysql_config = {
        "host": DB_CONFIG['host'],
        "port": DB_CONFIG['port'],
        "user": DB_CONFIG['user'],
        "password": DB_CONFIG['password'],
        "charset": DB_CONFIG['charset']
    }

    db_name = DB_CONFIG['database']

    try:
        conn = pymysql.connect(**mysql_config, connect_timeout=10)
        cursor = conn.cursor()

        print(f"连接到数据库: {db_name}")

        # 切换到数据库
        cursor.execute(f"USE `{db_name}`")

        # 需要清空的表（按依赖顺序）
        tables_to_clear = [
            'interview_answers',  # 先清空回答（依赖interviews）
            'interviews',         # 再清空面试（依赖resumes和jobs）
            'resumes',            # 清空简历（依赖users）
            'jobs',               # 最后清空职位
        ]

        # 禁用外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        for table in tables_to_clear:
            cursor.execute(f"TRUNCATE TABLE `{table}`")
            print(f"  - 清空表: {table}")

        # 重新启用外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        conn.commit()
        print("\n数据库清空完成！")
        print("保留的表: users")

        # 显示各表记录数
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"\n当前用户数量: {user_count}")

    except Exception as e:
        print(f"错误: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    confirm = input("警告：此操作将清空所有简历、面试记录和职位数据，但保留用户。\n确认继续？(y/n): ")
    if confirm.lower() == 'y':
        clear_database()
    else:
        print("已取消")