import pymysql
import sys

def create_database():
    try:
        # 连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host='192.168.18.145',
            user='root',
            password='123456',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # 检查数据库是否存在
            cursor.execute("SHOW DATABASES LIKE 'app'")
            result = cursor.fetchone()
            
            if result:
                print("数据库'app'已存在")
            else:
                # 创建数据库
                cursor.execute("CREATE DATABASE app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print("数据库'app'创建成功")
        
        # 关闭连接
        connection.close()
        return True
    
    except Exception as e:
        print(f"操作失败: {e}")
        return False

if __name__ == "__main__":
    success = create_database()
    sys.exit(0 if success else 1)
