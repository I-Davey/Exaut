version = '13 August 2022 17:47'
auth = True


from subprocess import PIPE, Popen
import os

class Authenticate:
    def __init__(self):
        current_machine_id = Popen(["wmic", "csproduct", "get", "UUID"], stdout=PIPE, stderr=PIPE).communicate()[0].decode("utf-8").split("\n")[1].strip()

        if current_machine_id not in ("1E0033A0-008C-C500-97F3-E0CB4E536AD9", "5259A1A8-7FE8-0000-0000-000000000000"):
            raise Exception("Invalid Machine ID")
            os.close(1)
        print("Authenticated")

if auth:
    Authenticate()