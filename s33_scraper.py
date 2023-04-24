import json
import pandas as pd
import tabula
import re
import pdfplumber
import camelot



def get_first_page(result):

    my_dict = {'contract_number': '', 'solicitation_number': '', 'solicitation_type': '', 'date_issued': '',
               'requisition/purchase_number': '', 'email': '', 'rating': '', 'area_code': '', 'extension': '',
               'number': '','amendment_no': [], 'date': [], 'award_date': '', 'award_amount': '', 'offer_date': ''}

    all_keys=['2 CONTRACINO','3 SOLICITATIONNO','2. CONTRA CT NO.',' 5 DAIE ISSUED','2. CONTRACT NUMBER','3. SOLICITATION NUMBER','5. DATE ISSUED','2. CONTRACT NO.','3. SOLICITATION NO.','5.DATE ISSUED','RATING','6. REQUISITION/PURCHASE NUMBER','6 REQUISITION P URCHASE NO','6.RE QUISITION/P URCHASE NO.','A. NAME'
        ,'C. E-MAIL ADDRESS','AREA CODE','AMENDMENT NO.','AMENDMENT NO','INUMBER','EXTENSION','DATE','20. AMOUNT','28. AWARD DATE','4. TYPE OF SOLICITATION','4 TYPE OF SOLICITATION|','20 AMOUNT',
        '28 AWARDDAIE','28 AWARDDATE','18. OFFERDATE','18 OFFERDATE','18. OFFER DATE']

    amendments=[]
    boxes = []
    dates_list=[]
    # iterating over a result from OCR and saving box which have value from all_keys
    for line in result:
        if 'STANDARD FORM' in str(line[1][0]):
            my_dict['STANDARD FORM']=str(line[1][0])
        if str(line[1][0]) in all_keys:
            line[0][2][1] = line[0][2][1] + 5
            line[0][3][1] = line[0][3][1] + 50
            boxes.append([line[0],line[1][0]])


    for r in result:
        for i in boxes:
            amend_list = ['AMENDMENT NO.','AMENDMENT NO']
            datelist = ['DATE']
            if i[1] in amend_list:
                if r[1][0] not in all_keys and (0<=(r[0][0][1]-i[0][0][1])<80) and 0<=(i[0][0][0]-r[0][0][0])<80:
                    amendments.append(r[1][0])
                    my_dict['AMENDMENT NO.']=amendments
            if i[1] in datelist:
                if r[1][0] not in all_keys and (0 <= (r[0][0][1] - i[0][0][1]) < 80) and 0 <= (i[0][0][0] - r[0][0][0]) < 80:
                    dates_list.append(r[1][0])
                    my_dict['Date'] = dates_list

            if (0<=(r[0][0][1]-i[0][0][1])<80) and 0<=(r[0][0][0]-i[0][0][0])<80 and r[1][0] not in all_keys :
                # lists for classifying values for matching

                Contract_names=['2 CONTRACINO','2. CONTRACT NO.','2. CONTRACT NUMBER','2. CONTRA CT NO.']
                Soliciation_names=['3 SOLICITATIONNO','3. SOLICITATION NUMBER','3. SOLICITATION NO.']
                Dates_name=['5.DATE ISSUED','5. DATE ISSUED',' 5 DAIE ISSUED']
                Purchase_names=['6. REQUISITION/PURCHASE NUMBER','6 REQUISITION P URCHASE NO','6.RE QUISITION/P URCHASE NO.']
                name_list=['A. NAME']
                email_list=['C. E-MAIL ADDRESS']
                area_list=['area_code']
                number_list=['INUMBER']
                extension_list=['EXTENSION']
                datelist=['DATE']
                Soliciation_typeee = ['4. TYPE OF SOLICITATION','4 TYPE OF SOLICITATION|']
                award_names=['20. AMOUNT','20 AMOUNT']
                awarddate=['28. AWARD DATE','28 AWARDDAIE','28 AWARDDATE']
                offerdate=['18. OFFERDATE','18. OFFER DATE']

                answer=r[1][0]
                if str(i[1]) in Contract_names:
                    name='contract_number'
                elif str(i[1]) in Soliciation_names:

                    name='solicitation_number'
                elif str(i[1]) in Dates_name:
                    name='date_issued'
                elif str(i[1]) in Purchase_names:
                    name='requisition/purchase_number'
                elif  str(i[1]) in name_list:
                    name='Name'
                elif str(i[1]) in email_list:
                    name='email'
                elif str(i[1]) in area_list:
                    name='Area Code'
                elif str(i[1]) in extension_list:
                    name='extension'
                elif str(i[1]) in number_list:
                    name='number'
                elif str(i[1]) in Soliciation_typeee:
                    name = 'solicitation_type'
                    answer = (str(r[1][0]).split(' ', 1))[1]
                    if answer[-1]=='P':
                        answer=answer+')'
                elif str(i[1]) in award_names:
                    name='award_amount'
                elif str(i[1]) in datelist:

                    dates_list.append(r[1][0])
                elif str(i[1]) in awarddate:
                    name='award_date'
                elif str(i[1]) in offerdate:
                    name='offer_date'
                else:
                    name=str(i[1])
                if name=='amendment_no':
                    my_dict[name] = amendments
                elif name=='date':
                    my_dict[name]=dates_list
                elif name=='award_date':
                    answer = r[1][0].replace('Mby', 'May')
                    my_dict[name]=answer
                else:
                    my_dict[name]=answer

                break

    return my_dict



def get_tables_pages(pdf_path):
    #for getting page numbers having line item tables and also method to manupulate data
    method = ''
    with pdfplumber.open(pdf_path) as pdf:
        # Get number of pages
        NumPages = len(pdf.pages)
        String = "ITEM NO"
        String2="QUANTITY UNIT"
        String3="Item"
        String4="Unit Price"
        String5="Supplies/Service"
        string6="MAX UNIT"
        # Extract text and do the search for checking method and pages
        table_pages=[]
        for i in range(0, NumPages):
            Text = pdf.pages[i].extract_text()
            if re.search(String,Text):
                if re.search(string6,Text):
                    method='third'
                    table_pages.append(i)
            if re.search(String,Text):
                if re.search(String2,Text):
                    method='first'
                    table_pages.append(i)
            if re.search(String3, Text) and re.search(String4, Text) and re.search(String5,Text):
                method='second'
                table_pages.append(i)

    return table_pages,method


def method1(pdf_path,pages):
    all_pages=','.join(str(v) for v in pages)
    items = []
    try:
        tables = camelot.read_pdf(pdf_path,flavor='stream', edge_tol=500, pages=all_pages)
        second_method=False
        for table in tables:
            try:
                index_change=False
                df = table.df
                try:
                    df.columns = ['ITEM NO', 'SUPPLIES/SERVICES', 'QUANTITY', 'UNIT', 'UNIT PRICE', 'AMOUNT']
                except:
                    df.columns = ['ITEM NO', 'SUPPLIES/SERVICES', 'QUANTITY', 'UNIT', 'AMOUNT']
                    second_method=True
                index1 = df.loc[df['ITEM NO'] == 'ITEM NO'].index
                if len(index1) == 0:
                    index1 = df.loc[df['ITEM NO'] == 'ITEM NO \nSUPPLIES/SERVICES'].index
                    index_change = True
                count = 0
                for i in index1:
                    dff = df.iloc[i + 1]

                    if second_method==True:
                        split_units = dff['UNIT'].split('\n')
                        if len(split_units) > 1:
                            dff['UNIT PRICE'] = split_units[1]
                        else:
                            dff['UNIT PRICE'] = ''

                    if index_change == True:
                        data_change = [dff['SUPPLIES/SERVICES'], dff['QUANTITY'], dff['UNIT']]
                        dff['QUANTITY'] = data_change[0]
                        dff['UNIT'] = data_change[1]
                        dff['UNIT PRICE'] = data_change[2]
                    json1 = dff.to_json()
                    aDict = json.loads(json1)

                    if index1[-1] == i:
                        full_text = []
                        target_df = df.iloc[(i + 2):]
                        for index, row in target_df.iterrows():
                            full_text.append(row['SUPPLIES/SERVICES'])
                            full_text.append(row['QUANTITY'])
                        str1 = ''.join(full_text)
                        name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                        supplies_clauses = name.findall(str1)
                        aDict['SUPPLIES/SERVICES'] = str1
                        aDict['Clauses'] = supplies_clauses
                        items.append(aDict)
                        count += 1
                    else:
                        full_text = []
                        target_df = df.iloc[i + 2:index1[count + 1] - 1]
                        for index, row in target_df.iterrows():
                            full_text.append(row['SUPPLIES/SERVICES'])
                            full_text.append(row['QUANTITY'])

                        str1 = ''.join(full_text)
                        name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                        supplies_clauses = name.findall(str1)
                        count += 1
                        aDict['SUPPLIES/SERVICES'] = str1
                        aDict['Clauses'] = supplies_clauses
                        items.append(aDict)

            except:
                pass
    except:
        pass

    #returning all line items
    return items


def method2(pdf_path,pages):
    items=[]
    for p in pages:
        start_page=p
        end_page=start_page+10
        df = tabula.read_pdf(pdf_path, pages=str(start_page)+'-'+str(end_page),stream=True)
        tables_list = []
        tables = df
        count = 0
        data = []
        for t in tables:
            try:
                if count == 0:
                    value = t.columns
                    t.columns = value
                    supplies_list = t['Supplies/Service'].values.tolist()
                    data.append(' '.join(str(v) for v in supplies_list))
                    t.drop('Supplies/Service', axis=1, inplace=True)
                    t.dropna(axis=0, how='all', inplace=True)
                    count += 1
                    tables_list.append(t)
                else:
                    t.columns = value
                    supplies_list = t['Supplies/Service'].values.tolist()
                    data.append(' '.join(str(v) for v in supplies_list))
                    t.drop('Supplies/Service', axis=1, inplace=True)
                    t.dropna(axis=0, how='all', inplace=True)
                    tables_list.append(t)
            except:
                pass
    supplies_data = '.'.join(data)
    new_list = []
    supplies_data = supplies_data.replace('Firm Fixed Price', 'Firm Fixed Price fffff')
    supplies_data = supplies_data.replace('Cost No Fee', 'Cost No Fee fffff')
    supplies_data = supplies_data.split('fffff')
    line_clauses=[]
    for f in supplies_data:
        new_list.append(f)
        name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
        supplies_clauses = name.findall(f)
        line_clauses.append(supplies_clauses)

    dff = pd.concat(tables_list, axis=0, ignore_index=True)
    target_df = dff.loc[pd.isna(dff["Item"]), :].index

    for target in target_df:
        if pd.notnull(dff['Unit Price'][target]):
            if pd.notnull(dff['Unit Price'][target - 1]):
                dff.iloc[target - 1, 3] = str(dff.iloc[target - 1, 3]) + ' ' + str(dff.iloc[target, 3])
            if pd.isnull(dff['Unit Price'][target - 1]):
                dff.iloc[target - 1, 3] = str(dff.iloc[target, 3])
        if pd.notnull(dff['Amount'][target]):
            if pd.notnull(dff['Amount'][target + 1]):
                dff.iloc[target + 1, 4] = str(dff.iloc[target, 4]) + '\n' + str(dff.iloc[target + 1, 4])
            elif pd.isnull(dff['Amount'][target + 1]):
                dff.iloc[target + 1, 4] = str(dff.iloc[target, 4])

    dff.dropna(thresh=2, axis=0, inplace=True)
    dff['Supplies/Services'] = new_list
    dff['Clauses'] = line_clauses
    items_json=dff.to_json(orient="index")
    items_json=json.loads(items_json)
    for it in items_json:
        items.append(items_json[str(it)])
    for i in items:
        item_value=str(int(i['Item']))
        item_value_updated = item_value
        if len(item_value)==1:
            item_value_updated='000'+item_value
        elif len(item_value)==2:
            item_value_updated='00'+item_value
        elif len(item_value)==3:
            item_value_updated='0'+item_value
        i['Item']=item_value_updated

    return items


def method3(pdf_path,pages):
    all_pages=','.join(str(v) for v in pages)
    items = []
    try:
        tables = camelot.read_pdf(pdf_path,flavor='stream', edge_tol=500, pages=all_pages)
        for table in tables:
            df = table.df
            df.columns = ['ITEM NO', 'SUPPLIES/SERVICES', 'QUANTITY', 'UNIT', 'UNIT PRICE', 'AMOUNT']
            index1 = df.loc[df['ITEM NO'] == 'ITEM NO'].index

            count = 0
            for i in index1:
                dff = df.iloc[i + 2]
                json1 = dff.to_json()
                aDict = json.loads(json1)
                if index1[-1] == i:
                    full_text = []
                    target_df = df.iloc[(i + 2):]
                    for index, row in target_df.iterrows():
                        full_text.append(row['SUPPLIES/SERVICES'])
                    str1 = ''.join(full_text)
                    aDict['SUPPLIES/SERVICES'] = str1
                    name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                    supplies_clauses = name.findall(str1)
                    aDict['Clauses'] = supplies_clauses
                    items.append(aDict)
                    count += 1
                else:
                    full_text = []
                    target_df = df.iloc[i + 2:index1[count + 1] - 1]
                    for index, row in target_df.iterrows():
                        full_text.append(row['SUPPLIES/SERVICES'])
                    str1 = ''.join(full_text)
                    count += 1
                    name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                    supplies_clauses = name.findall(str1)
                    aDict['SUPPLIES/SERVICES'] = str1
                    aDict['Clauses'] = supplies_clauses
                    items.append(aDict)

    except:
        pass
    return items

def get_clauses(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        #get number of pages
        NumPages = len(pdf.pages)
        clauses_list=[]
        #list of all months to match
        Months_list=['ggg','JAN','FEB','MAR',"APR",'MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
        # Extract text and do the search
        for i in range(2, NumPages):
            Text = pdf.pages[i].extract_text()
            NumRegex = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}', flags=0)
            array = NumRegex.search(Text)
            array_length = NumRegex.findall(Text)

            try:
                # if pattern match then implementing various algos
                if array.group():
                    NumRegex2 = re.compile(r'\d{4}', flags=0)
                    NumRegex3 = re.compile(r'\d{4}-\d{2}', flags=0)
                    lines = Text.split('\n')
                    for line in lines:
                        third_string = False
                        current_line_split = line.split(' ')
                        try:
                            next_line = lines[lines.index(line) + 1]
                            next_line_split=next_line.split(' ')
                        except:
                            pass

                        if NumRegex.search(current_line_split[0]) and NumRegex2.search(next_line_split[-1]):
                            if not NumRegex2.search(current_line_split[-1]):
                                full_line = line + ' ' + next_line
                                if len(full_line) > 20:
                                    full_line = full_line.replace('(', '')
                                    full_line = full_line.replace(')', '')
                                    full_line_splited = full_line.split(' ')
                                    if full_line_splited[-2] in Months_list:
                                        full_line_splited[-2] = full_line_splited[-1] + '-' + str(Months_list.index(full_line_splited[-2]))
                                        full_line_splited = full_line_splited[:-1]
                                        line = ' '.join(full_line_splited)
                                    if '/' in full_line_splited[-1]:
                                        month = full_line_splited[-1].split('/')[0]
                                        year = full_line_splited[-1].split('/')[2]
                                        full_line_splited[-1] = year + '-' + month
                                        line = ' '.join(full_line_splited)
                                    clauses_list.append(line)


                        if NumRegex.search(current_line_split[0]) and (NumRegex2.search(current_line_split[-1])) :
                            second_string = False
                            try:
                                next_string=lines[lines.index(line)+1]

                                next_string_split=next_string.split(' ')

                                if len(line)>=65 and len(array_length)>3:
                                    if not NumRegex.search(next_string_split[0]):
                                        second_string=True
                                        if line!=lines[-1] or line!=lines[-2] :
                                            third_line=lines[lines.index(line) + 2]
                                            third_line_splited = lines[lines.index(line) + 2].split(' ')
                                            if not NumRegex.search(third_line_splited[0]) and len(third_line_splited[0])<70 and len(array_length)>8:
                                                third_string=True
                            except:
                                pass
                            if len(line)>20:
                                line=line.replace('(','')
                                line=line.replace(')','')
                                splited_line=line.split(' ')
                                if splited_line[-2] in Months_list:
                                    splited_line[-2]=splited_line[-1]+'-'+str(Months_list.index(splited_line[-2]))
                                    splited_line=splited_line[:-1]
                                    line=' '.join(splited_line)
                                if '/' in splited_line[-1]:
                                    month=splited_line[-1].split('/')[0]
                                    year=splited_line[-1].split('/')[2]
                                    splited_line[-1]=year+'-'+month
                                    line=' '.join(splited_line)
                                if second_string==True and third_string==False:
                                    line=line.split(' ')
                                    line=' '.join(line[0:-1])+' '+next_string+' '+line[-1]
                                elif second_string==True and third_string==True:
                                    line = line.split(' ')
                                    line = ' '.join(line[0:-1]) + ' ' + next_string +' '+third_line+ ' ' + line[-1]
                                clauses_list.append(line)

                        if NumRegex.search(current_line_split[0]) and (NumRegex3.search(current_line_split[-1])):
                            if len(line.split(' '))==2:
                                target_clause=current_line_split[0]+' '+lines[lines.index(line)-1]+' '+lines[lines.index(line)+1]+' '+current_line_split[-1]
                                clauses_list.append(target_clause)
            except Exception as e:
                pass

    clauses_new_list = []
    for old_clause in clauses_list:
        splited_clause = old_clause.split(' ')
        clause_value = splited_clause[0] + ' | ' + ' '.join(splited_clause[1:-1]) + ' | ' + splited_clause[-1]
        clauses_new_list.append(clause_value)

    return clauses_new_list







def main(pdf_path,result):

    #getting_data_from_first_page from results getting from paddleOCR
    mydict=get_first_page(result)
    #getting method and page numbers
    page_numbers,method=get_tables_pages(pdf_path)
    #different methods to get lineitems depend on method
    if method=='first':
        all_items=method1(pdf_path,page_numbers)
        mydict['items']=all_items
    elif method=='second':
        all_items=method2(pdf_path,page_numbers)
        mydict['items'] = all_items
    elif method=='third':
        all_items=method3(pdf_path,page_numbers)
        mydict['items']=all_items
    #for getting clauses
    all_clauses=get_clauses(pdf_path)
    mydict['clauses']=all_clauses
    return mydict


