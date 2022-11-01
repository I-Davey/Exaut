version = '01 November 2022 14:19'
auth = True


from subprocess import PIPE, Popen
import os
global RequiresUUIDAuth
RequiresUUIDAuth = False

class Authenticate:
    def __init__(self):
        current_machine_id = Popen(["wmic", "csproduct", "get", "UUID"], stdout=PIPE, stderr=PIPE).communicate()[0].decode("utf-8").split("\n")[1].strip()

        if current_machine_id not in ("1E008FC0-008C-5800-5F47-3085A9A452DA", "5259A1A8-7FE8-0000-0000-000000000000", "A7859628-EF42-11E5-AA37-C4AA890DF032", "1E0033A0-008C-C500-97F3-E0CB4E536AD9"):
            raise Exception("Invalid Machine ID: "+current_machine_id)
            os.close(1)
        print("Authenticated")

if auth:
    Authenticate()
    RequiresUUIDAuth = True 