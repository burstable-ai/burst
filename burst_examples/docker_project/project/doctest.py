import os

print ("BUILDING...")
os.system("docker build -t doctest .")
print ("RUNNING...")
os.system("docker run doctest")
print ("FINI")
