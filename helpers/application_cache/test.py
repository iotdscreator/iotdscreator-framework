import subprocess

cmd = ["python3", "application_cache.py", "-c", "~/iotdscreator-cache"]
proc = subprocess.Popen(cmd, close_fds=True)
pid = proc.pid
print ("pid: {}".format(pid))

while True:
    time.sleep(1)
    print ("test")
