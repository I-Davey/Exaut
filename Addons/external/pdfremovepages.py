from __important.PluginInterface import PluginInterface
from PyPDF2 import PdfFileReader, PdfFileWriter
class pdfremovepages(PluginInterface):
    load = True
    types = {"source":3,"target":4,"databasepath":5,"filename":1,"folderpath":0}
    type_types = {
    "source":{"type":"text", "description":"enter start page"},
    "target":{"type":"text", "description":"enter end page"},
    "databasepath":{"type":"drag_drop_file", "description":"select pdf"},
    "filename":{"type":"text", "description":"enter new file name"},
    "folderpath":{"type":"drag_drop_file", "description":"select save location"},
    "__Name":"PDF: Remove other Pages"}
    callname = "pdfremovepages"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def main(self, start, end, file, savename, saveloc, Popups) -> bool:
        with open(file, 'rb') as f:
            #save all pages between start and end, write to savename in saveloc
            pdf = PdfFileReader(f)
            writer = PdfFileWriter()
            for i in range(int(start), int(end)):
                writer.addPage(pdf.getPage(i))
            with open(saveloc + "\\" + savename, 'wb') as out:
                writer.write(out)
            self.logger.success(f"removed pages {start} to {end} from {file} and saved to: {saveloc + '/' + savename}")