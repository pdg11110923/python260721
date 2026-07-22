# 랜던연습.py
import random

print(random.random())  # 0.0 이상 1.0 미만의 랜덤한 실수 출력'
print(random.random())
print(random.uniform(2.0, 5.0))  
print([random.randrange(20) for i in range(10)])  # 0 이상 20 미만의 랜덤한 정수 출력 
print([random.randrange(20) for i in range(10)])
print(random.sample(range(20), 5))  # 0 이상 20 미만의 숫자 중 5개를 랜덤하게 뽑아 리스트로 반환

#로또번호 만들기
print(random.sample(range(1,46),5))  # 1~45까지의 숫자 중 5개를 랜덤하게 뽑아 리스트로 반환

from os.path import *
print(abspath("python.exe"))
print(basename("c:\\python313\\python.exe"))
fileName = "c:\\python313\\python.exe"
if exists(fileName):
    print("파일이 존재합니다.")
    print(getsize(fileName))
else:
    print("파일이 없습니다.")

import os
print("운영체제명:", os.name)

#파일목록
import glob
print(glob.glob(r"c:\work\*.py"))  # c:\work 폴더 안에 있는 모든 .py 파일을 리스트로 반환
for item in glob.glob(r"c:\work\*.py"):
    print(item)
    