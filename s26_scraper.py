import json
import re
from paddleocr import PaddleOCR
import pdfplumber
import camelot
ocr = PaddleOCR(use_angle_cls=True, lang='en')


def get_first_page(result):
    my_dict={'contract_code':'','effective_date':'','requisition/purchase_number':'','rating':'','issued_by':'','administered_by':'','standard_form':'','project_number':''}
    #giving all key pattern to extract relevant data

    all_keys=['2. CONTRACT (PROC. INST. IDENT.) NO.','2. CONTRACT (Proc Inst. Indent ) NO','3. EFFECTIVE DATE','3 EFFECTIVE DATE',' 4. REQUISITION / PURCHASE REQUEST /PROJECT NO.','[4 REQUISIT:ON/PURCHASE REQUEST/PROJECT NO.','RATING',' 6. ADMINISTERED BY (IF OTHER THAN ITEM 5)','3.EFFECTIVE DATE',
        '5. ISSUED BY AFLCMC/HBQK','5 ISSUED BY','6 ADMINISTERED BY (if other than ftem 5)','6 ADMINISTERED BY (if other than ftem 5)',' 6. ADMINISTERED BY (IF OTHER THAN ITEM 5)']

    boxes = []
    #iterating over a result from OCR and saving box which have value from all_keys

    for line in result:
        if 'STANDARD FORM' in str(line[1][0]):
            my_dict['standard_form']=str(line[1][0])
        if str(line[1][0]) in all_keys:
            boxes.append([line[0],line[1][0]])


    issued_text = []
    admin_text=[]
    lastx = ''
    lasty = ''
    adminx = ''
    adminy = ''
    admin_code=''
    issue_code=''

    for r in result:
        #lists for classifying values for matching
        contract_list=['2. CONTRACT (PROC. INST. IDENT.) NO.','2. CONTRACT (Proc Inst. Indent ) NO']
        rating_list=['RATING']
        date_list=['3. EFFECTIVE DATE','3 EFFECTIVE DATE']
        purchase_list=[' 4. REQUISITION / PURCHASE REQUEST /PROJECT NO.','[4 REQUISIT:ON/PURCHASE REQUEST/PROJECT NO.']
        isuuedd=['5. ISSUED BY','5 ISSUED BY','5. ISSUED BY AFLCMC/HBQK']
        project=['5. PROJECT NUMBER (If applicable)','5. PROJECT NO. (If applicable)','5 PROJECT NO,(lf applicsb/e)']
        admin=['6 ADMINISTERED BY (if other than ftem 5)',' 6. ADMINISTERED BY (IF OTHER THAN ITEM 5)']


        for i in boxes:
            if str(i[1]) in purchase_list:
                xx=301
                yy=35
            else:
                xx=150
                yy=60

            if admin_code=='':
                if r[1][0] in admin:
                    present = result.index(r)
                    admin_string=result[present+2][1][0]
                    digit = 0
                    for ch in admin_string:
                        if ch.isdigit():
                            digit = digit + 1
                    if digit>=3:
                        admin_code='Code: '+result[present+2][1][0]

            if issue_code=='':
                if r[1][0] in isuuedd:
                    present = result.index(r)
                    splited=result[present+1][1][0].split(' ')
                    if len(splited)==2:
                        if splited[0]=='CODE':
                            issue_code="CODE: "+splited[1]
                    if issue_code=='':
                        issued_string=result[present+2][1][0]
                        digit = 0
                        for ch in issued_string:
                            if ch.isdigit():
                                digit = digit + 1
                        if digit>=3:
                            issue_code='Code: '+result[present+2][1][0]

            if (0 <= (r[0][0][1] - i[0][0][1]) <= yy) and -20 <= (r[0][0][0] - i[0][0][0]) <= xx and r[1][0] not in all_keys:
                if i[1] in contract_list:
                    my_dict['contract_code']=r[1][0]

                if i[1] in rating_list:
                    my_dict['rating']=r[1][0]

                if i[1] in date_list:
                    if 'Mby' in r[1][0]:
                        r[1][0]=r[1][0].replace('Mby','May')
                    my_dict['effective_date'] = r[1][0]

                if i[1] in purchase_list:
                    my_dict['requisition/purchase_number'] = r[1][0]

                if i[1] in project:
                    my_dict['project_number']=r[1][0]

                if i[1] in isuuedd:
                    lastx = r[0][0][0]
                    lasty = r[0][0][1]
                    issued_text.append(issue_code)

                if i[1] in admin:
                    adminx = r[0][0][0]
                    adminy = r[0][0][1]
                    admin_text.append(admin_code)

        if adminy:
            if -8<=(r[0][0][0]-adminx)<10 and 0<=(r[0][0][1]-adminy)<=62:
                admin_text.append(r[1][0])
                adminx = r[0][0][0]
                adminy = r[0][0][1]
        if lastx:
            if -8<=(r[0][0][0]-lastx)<10 and 0<=(r[0][0][1]-lasty)<=35:
                if 'NAME AND ADDRESS' not in r[1][0]:
                    issued_text.append(r[1][0])
                    lastx = r[0][0][0]
                    lasty = r[0][0][1]
    if len(issued_text)>0:
        my_dict['issued_by']='\n'.join(issued_text)
    if len(admin_text)>0:
        my_dict['administered_by'] = '\n'.join(admin_text)

    return my_dict



#To get pages numbers which contain line items
def line_item_pages(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        # Get number of pages
        NumPages = len(pdf.pages)
        # Extract text and do the search
        target_pages=[]
        for i in range(1, NumPages):
            Text = pdf.pages[i].extract_text()
            if re.search('ITEM', Text) and re.search('SUPPLIES OR SERVICES', Text):
                target_pages.append(i+1)

    return target_pages



def get_table(pdf_path,pages):
    all_pages = ','.join(str(v) for v in pages)
    items = []
    tables = camelot.read_pdf(pdf_path,flavor='stream', edge_tol=1000, pages=str(all_pages))
    #iterating over tables and manuplating values to append in items list
    for table in tables:
        try:
            df = table.df
            count=0
            try:
                df.columns=['ITEM','SUPPLIES OR SERVICES','Purch Unit','Total Item Amount']
                main_index = df[df['ITEM'] == 'ITEM'].index.tolist()
                df=df.loc[main_index[0]+1:,:]
            except:
                df.columns = ['ITEM', 'ITEM2','SUPPLIES OR SERVICES', 'Purch Unit', 'Total Item Amount']
                df['ITEM']=df['ITEM']+df['ITEM2']
                df.drop('ITEM2', axis=1, inplace=True)
                df.columns = ['ITEM', 'SUPPLIES OR SERVICES', 'Purch Unit', 'Total Item Amount']
                main_index = df[df['ITEM'] == 'ITEM'].index.tolist()
                df = df.loc[main_index[0]+1:, :]

            index1=df[df['ITEM']!=''].index.tolist()
            for i in index1:
                new_df=df.loc[i]
                df_json = new_df.to_json()
                aDict = json.loads(df_json)
                aDict['ITEM'] = aDict['ITEM'].replace('\n','')
                res = any(chr.isdigit() for chr in aDict['ITEM'])
                if res:
                    if index1[-1] == i:
                        full_text = []
                        target_df = df.iloc[(i):]
                        for index, row in target_df.iterrows():
                            full_text.append(' '+row['SUPPLIES OR SERVICES']+' '+row['Purch Unit'])
                        str1 = ' '.join(full_text)
                        name = re.compile(r'(?:\d{2,6}.\d{1,5}?-\d{1,5})|(?:\d{2,6}.\d{1,5})')
                        clauses = name.findall(str1)
                        aDict['SUPPLIES OR SERVICES'] = str1
                        aDict['Clauses'] = clauses
                        items.append(aDict)
                        count += 1

                    else:
                        full_text = []
                        target_df = df.iloc[i :index1[count+1] ]
                        for index, row in target_df.iterrows():
                            full_text.append(row['SUPPLIES OR SERVICES']+' '+row['Purch Unit'])
                        supplies = ' '.join(full_text)
                        name = re.compile(r'(?:\d{2,6}.\d{1,5}?-\d{1,5})|(?:\d{2,6}.\d{1,5})')
                        clauses = name.findall(supplies)
                        count += 1
                        aDict['SUPPLIES OR SERVICES'] = supplies
                        aDict['Clauses'] = clauses
                        items.append(aDict)

        except Exception as e:
            pass

    return items




def get_clauses(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        NumPages = len(pdf.pages)
        clauses_list = []
        Months_list = ['random_x', 'JAN', 'FEB', 'MAR', "APR", 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

        # Extract text and do the search
        for i in range(2, NumPages):
            Text = pdf.pages[i].extract_text()
            #matching clauses pattern to get relevant line
            NumRegex = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}', flags=0)
            array = NumRegex.search(Text)
            #after matching pattern applied multiple conditions to extract clauses

            try:
                if array.group():
                    NumRegex2 = re.compile(r'\d{4}', flags=0)
                    NumRegex3 = re.compile(r'\d{4}-\d{2}', flags=0)
                    lines = Text.split('\n')
                    for line in lines:
                        splited_line = line.split(' ')
                        try:
                            next_line = lines[lines.index(line) + 1]
                            splited_next_line = next_line.split(' ')
                        except:
                            pass

                        if NumRegex.search(splited_line[0]) and NumRegex2.search(splited_next_line[-1]):
                            if not NumRegex2.search(splited_line[-1]):
                                line = line + ' ' + next_line
                                if len(line) > 20:
                                    line = line.replace('(', '')
                                    line = line.replace(')', '')
                                    new_split_line = line.split(' ')
                                    if new_split_line[-2] in Months_list:
                                        new_split_line[-2] = new_split_line[-1] + '-' + str(Months_list.index(new_split_line[-2]))
                                        new_split_line = new_split_line[:-1]
                                        line = ' '.join(new_split_line)
                                    if '/' in new_split_line[-1]:
                                        month = new_split_line[-1].split('/')[0]
                                        year = new_split_line[-1].split('/')[2]
                                        new_split_line[-1] = year + '-' + month
                                        line = ' '.join(new_split_line)
                                    clauses_list.append(line)

                        if NumRegex.search(splited_line[0]) and (NumRegex2.search(splited_line[-1])):
                            if len(line) > 20:
                                line = line.replace('(', '')
                                line = line.replace(')', '')
                                new_split_line = line.split(' ')
                                if new_split_line[-2] in Months_list:
                                    new_split_line[-2] = new_split_line[-1] + '-' + str(Months_list.index(new_split_line[-2]))
                                    new_split_line = new_split_line[:-1]
                                    line = ' '.join(new_split_line)
                                if '/' in new_split_line[-1]:
                                    month = new_split_line[-1].split('/')[0]
                                    year = new_split_line[-1].split('/')[2]
                                    new_split_line[-1] = year + '-' + month
                                    line = ' '.join(new_split_line)
                                clauses_list.append(line)

                        if NumRegex.search(splited_line[0]) and (NumRegex3.search(splited_line[-1])):
                            if len(line.split(' ')) == 2:
                                line = splited_line[0] + ' ' + lines[lines.index(line) - 1] + ' ' + lines[lines.index(line) + 1] + ' ' + splited_line[-1]
                                clauses_list.append(line)

            except Exception as e:
                pass

    #changing clauses format
    clauses_new_list = []
    for clauses in clauses_list:
        splited_clause = clauses.split(' ')
        updated_clause = splited_clause[0] + ' | ' + ' '.join(splited_clause[1:-1]) + ' | ' + splited_clause[-1]
        clauses_new_list.append(updated_clause)

    return clauses_new_list


def mains26(pdf_path,result):
    #for getting data from first_page
    my_dict=get_first_page(result)
    #for getting numbers of pages which have line_items
    page_number_list=line_item_pages(pdf_path)
    #for getting line_items from table_pages
    line_items=get_table(pdf_path,page_number_list)
    my_dict['items']=line_items
    my_dict['clauses']=get_clauses(pdf_path)
    #for returning response
    return my_dict


