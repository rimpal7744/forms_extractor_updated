from fastapi import FastAPI, File, UploadFile
from paddleocr import PaddleOCR
from s26_scraper import mains26
from s30_scraper import mains30
from s33_scraper import main
import uvicorn
import numpy as np
from pdf2image import convert_from_path
import os
import re
import uuid
ocr = PaddleOCR(use_angle_cls=True, lang='en') # need to run only once to download and load model into memory

app = FastAPI()


@app.post("/upload-file/")
async def create_upload_file(file: UploadFile = File(...)):
    file_location = f"{(str(uuid.uuid1())+'.pdf')}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    print(file_location)
    images = convert_from_path(file_location,last_page=1)
    pix = np.array(images[0])
    result = ocr.ocr(pix, cls=True)
    result = result[0]
    #Different regex to detect which form it is
    form30regexp = re.compile(r'(FORM 30)|(FORM30)')
    form33regexp = re.compile(r'(FORM 33)|(FORM33)')
    form26regexp = re.compile(r'(FORM 26)|(FORM26)|(FORM 25)|(FORM25)')
    #
    Parse=False
    final_result={}
    #checking form type and implement method accordingly
    for line in result:
        if form26regexp.search(line[1][0]):
            print('26form')
            final_result=mains26(file_location,result)
            Parse=True
            break

        elif form30regexp.search(line[1][0]):
            print('30form')
            final_result=mains30(result)
            Parse=True
            break

        elif form33regexp.search(line[1][0]):
            print('33form')
            final_result=main(file_location,result)
            Parse=True
            break
        else:
            pass
    #in some cases form type not detected in sf30, this execution will take place
    if Parse==False:
        for line in result:
            Amendmentregexp = re.compile(r'(AMENDMENT)')
            Amendmentregexp2 = re.compile(r'(NO)|(NUMBER)')
            if Amendmentregexp.search(line[1][0]) and Amendmentregexp2.search(line[1][0]):
                print('30form')
                final_result = mains30(result)

    os.remove(file_location)
    return final_result



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6000)
