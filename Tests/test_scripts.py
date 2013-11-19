import unittest
import laley
import os.path
import config
import shutil


class LaleyTest(unittest.TestCase):

    def test_extract_expediente_link(self):
        current_folder = os.path.dirname(os.path.realpath(__file__))
        page = os.path.join(current_folder, "Laley/3F06B090353436A90525797C005B72B4.html")
        print page
        expediente_link = "http://www2.congreso.gob.pe/sicr/tradocestproc/Expvirt_2011.nsf/visbusqptramdoc/00686?opendocument"
        codigo = "00686"

        result = laley.extract_expediente_link(page)
        self.assertEqual(result[0], expediente_link)
        self.assertEqual(result[1], codigo)


    def test_download_exp_pagina(self):
        codigo = "00686"
        # Create needed folders
        current_folder = os.path.dirname(os.path.realpath(__file__))
        page_folder = os.path.join(current_folder, "pages")
        if not os.path.isdir(page_folder):
            os.mkdir(page_folder)
        
        filename = os.path.join(page_folder, codigo)
        filename += ".html"
        # link = [url, codigo]
        link = ["http://www2.congreso.gob.pe/sicr/tradocestproc/Expvirt_2011.nsf/visbusqptramdoc/00686?opendocument"]
        link.append(codigo)

        laley.download_exp_pagina(link)
        result = os.path.isfile(filename)
        shutil.rmtree(page_folder)
        self.assertEqual(result, 1)



if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity = 2)
    unittest.main(testRunner=runner)
