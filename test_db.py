import pymysql
import sys

def test_connection():
    try:
        # 尝试连接到MySQL数据库
        connection = pymysql.connect(
            host='192.168.18.145',
            user='root',
            password='123456',
            db='app',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("数据库连接成功！")
        
        # 检查数据库版本
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"MySQL版本: {version['VERSION()']}")
        
        # 关闭连接
        connection.close()
        return True
    
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
