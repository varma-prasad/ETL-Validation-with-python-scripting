# import all necessary modules

import oracledb
import  psycopg2
import configparser
import pandas as pd

# Connect to Source

config = configparser.ConfigParser()
config.read('config.ini')

# read connection details from config.ini

User = config.get('SOURCE','username')
password = config.get('SOURCE','password')
host = config.get('SOURCE','host')
port = config.get('SOURCE','port')
service_name = config.get('SOURCE','service_name')

try:
    # create connection
    source = oracledb.connect(user=User,password=password,host=host,port=port,service_name=service_name)
except Exception as err:
    print("Error while connecting to source ",err)
else:
    print("Connection Established to source")
    # read source SQL Query
    try:
        sq1 = """select * from emp
                order by emp_id"""
        s1 = pd.read_sql(sq1,source,index_col='EMP_ID')                                                # Data from Emp table
        sq2 = """select EMP_ID, EMP_NAME, DESIGNATION, department_name
                from emp e inner join departments d
                on e.e_dept_no = d.department_id
                group by EMP_ID, EMP_NAME, DESIGNATION, department_name
                order by emp_id"""
        s2 = pd.read_sql(sq2,source,index_col='EMP_ID')                        # Data from Emp & Departments table without filter
        sq3 = """select EMP_ID, EMP_NAME, DESIGNATION, department_name
                from emp e inner join departments d
                on e.e_dept_no = d.department_id
                where department_name <> 'Human Resources'
                group by EMP_ID, EMP_NAME, DESIGNATION, department_name
                order by emp_id"""
        s3 = pd.read_sql(sq3,source,index_col='EMP_ID')                        # Data from Emp & Departments table with filter
    except Exception as err:
        print("Error occured while reading queries ",err)
    else:
        print("Source Queries read to DataFrame succesfully")
finally:
    source.close()
    print("Disconnected from source")

# Connect to Target
# Read connection details from config.ini
    
db = config.get('TARGET','database')
user =config.get('TARGET','username')
password = config.get('TARGET','password')
host = config.get('TARGET','host')
port = config.get('TARGET','port')

try:
    #create connection
    target = psycopg2.connect(dbname=db,user=user,password=password,host=host,port=port)
except Exception as err:
    print("Error occured while connecting to Target ",err)
else:
    print("Connection Established to Target")
    # Read Target Queries
    try:
        tq = """select * from "T_EMPLOYEE" """
        t1 = pd.read_sql(tq,target,index_col='EMP_ID')                                                         # Data from t_employee table
    except Exception as err:
        print("Error occured while reading Target Queries ",err)
    else:
        print("Target Queries read to DataFrame Succesfullty")
finally:
    target.close()
    print("Disconnected from Target")

print("Data Validation started")

try:
    #open a file to write the test results
    f = open('Data_validation.txt','w')
    print("Writing of test results started ")
    # Count of Records
    print("*********** Test case1: Count of Records in source & Target***********\n",file=f)
    print("(Source): (Rows*Columns):\n\t",s1.shape,file=f)
    print("(Target): (Rows*Columns):\n\t",t1.shape,file=f)
    # Duplicate Check
    print("\n*********** Test case2: Check for Duplicates in source & Target***********\n",file=f)
    print("(Source Duplicates):\n",s1[s1.duplicated()],"\n",file=f)
    print("(Target Duplicates):\n",t1[t1.duplicated()],file=f)
    # Null values in source and target
    print("\n*********** Test case3: Check for Null values in source & Target***********\n",file=f)
    print('(Source):\n',s1[s1.isnull().any(axis=1)],"\n",file=f)
    print('(Target):\n',t1[t1.isnull().any(axis=1)],file=f)
    # Check for Filter Transformation
    print("\n*********** Test case4: Validate Filter Transformation ***********\n",file=f)
    print('(Source): Departments',s2['DEPARTMENT_NAME'].unique(),file=f)
    print('(Target): Departments',t1["DEPARTMENT_NAME"].unique(),file=f)
    # Data Mismatch/Truncation from source to Target
    print("\n*********** Test case5: Check for Truncation/ Data Mismatch from source to Target***********\n",file=f)
    print("Comparision from Source to Target:\n",s3.compare(t1),file=f)
    f.close()
except Exception as err:
    print("Error occured during Data Validation ",err)
else:
    print("Test Results written Successfully ")