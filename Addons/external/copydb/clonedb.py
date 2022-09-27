from __important.PluginInterface import PluginInterface
import os
import psycopg2
import tempfile
class clonedb(PluginInterface):
    load = True
    types = {"source":3,"target":4}
    #type_types = {"source":{"type":"drag_drop_folder", "description":"please select the Source Folder", "optional":True}}

    callname = "clonepg"
    hooks_handler = ["log"]
    Popups = object



    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self, source,target) -> bool:
        source = source.split("|")
        target = target.split("|")

        if len(source)==4:
            source.append(self.variables["pg_pass"])
        if len(target)==4:
            target.append(self.variables["pg_pass"])

        source_dict = {"db":source[0],"uname":source[1], "ip":source[2], "port":source[3], "pw":source[4]}
        target_dict = {"db":target[0],"uname":target[1], "ip":target[2], "port":target[3], "pw":target[4]}

        source_uri = f"postgresql://{source_dict['uname']}:{source_dict['pw']}@{source_dict['ip']}:{source_dict['port']}/{source_dict['db']}"
        target_uri = f"postgresql://{target_dict['uname']}:{target_dict['pw']}@{target_dict['ip']}:{target_dict['port']}"


        self.logger.info(f"copying from {source_dict['ip']}:{source_dict['port']}/{source_dict['db']} to {target_dict['ip']}:{target_dict['port']}/{target_dict['db']}")
        with tempfile.TemporaryDirectory() as tmpdirname:
            self.logger.info(f"created temporary directory {tmpdirname}")

            self.logger.info(f"dumping source db..")
            os.system(f"pg_dump -Fc -f {tmpdirname}/source.sql {source_uri}")
            self.logger.success(f"dumping source db to {tmpdirname}/source.sql was successful")
            
            self.logger.info(f"creating target db..")
            cnn = psycopg2.connect(target_uri)
            cur = cnn.cursor()
            cnn.autocommit = True
            cur.execute(f"CREATE DATABASE {target_dict['db']}")
            cnn.close()
            self.logger.success(f"creating target db successful")


            
            self.logger.info(f"restoring dump to target db..")
            os.system(f"pg_restore -Fc -d {target_uri}/{target_dict['db']} {tmpdirname}/source.sql")
            self.logger.success(f"restoring dump to target db successful")


