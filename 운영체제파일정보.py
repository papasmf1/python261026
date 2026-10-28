import os 
import glob

print(os.name)
print(os.environ)

fName = r"c:\python313\python.exe"

if os.path.exists(fName):
    print(f"{fName} 파일이 존재: {os.path.getsize(fName)} 바이트")
else:
    print(f"{fName} 파일이 존재하지 않습니다.")

print(os.path.abspath("demo.txt"))
print(os.path.basename(r"c:\work\demo.txt"))

print(glob.glob(r"c:\work\*.py"))
for item in glob.glob(r"c:\work\*.*"):
    print(item)