import json
import pandas as pd
import tabula
import re
import pdfplumber
import camelot



def get_key_boxes(result):
    #match regex for all key values from OCR result and get their boxes
    boxes=[]
    #to append names given in forms for key values
    names=[]
    actual_names=[]
    for element in result:
        #all regex matching for keys respectively
        Contract_regexp = re.compile(r'(CONTRACT)|(CONIRACT)|(CONTRACI)|(CONTRA CT)')
        Contract_regexp2 = re.compile(r'(NO)|(NO.)|(NUMBER)')
        Date_regexp = re.compile(r'(DAIE)|(DATE)')
        Date_regexp2 = re.compile(r'(ISSUED)')
        Rating_regexp = re.compile(r'(RATING)|(RAIING)')
        Email_regexp = re.compile(r'(E-MAIL ADDRESS)|(E-MAILADDRESS)')
        Email_regexp2 = re.compile(r'(C)|(C.)')
        Requisition_regexp = re.compile(r'(REQUISITION)|(SOLICITAIION)')
        Requisition_regexp2 = re.compile(r'(NUMBER)|(NO.)|(NO)')
        Solicitation_regexp = re.compile(r'(SOLICITATION)|(SOLICITAIION)')
        Solicitation_regexp2 = re.compile(r'(NO)|(NUMBER)|(NO.)')
        Solicitation_type_regexp = re.compile(r'(SOLICITATION)')
        Solicitation_type_regexp2 = re.compile(r'(TYPE)')
        Amendmentno_regexp = re.compile(r'(AMENDMENT)')
        Amendmentno_regexp2 = re.compile(r'(NO)|(NUMBER)')
        Award_amount_regexp = re.compile(r'(AMOUNT)')
        Award_amount_regexp2 = re.compile(r'(20)')
        Award_date_regexp = re.compile(r'(AWARDDAIE)|(AWARDDATE)|(AWARD DATE)')
        Award_date_regexp2 = re.compile(r'(28)|(28.)')
        Offer_date_regexp = re.compile(r'(OFFERDATE)|(OFFERDAIE)|(OFFER DATE)')
        Offer_date_regexp2 = re.compile(r'(18)|(18.)')
        Area_code_regexp = re.compile(r'(AREA CODE)|(area_code)')
        Extension_regexp = re.compile(r'(EXTENSION)')
        Name_regexp = re.compile(r'(NAME)|(name)')
        Name_regexp2 = re.compile(r'(A.)|(A)')
        Name_regexp3 = re.compile(r'(FOR INFORMATION)')
        Telephone_regexp = re.compile(r'(B. TELEPHONE)|(B.TELEPHONE)')
        Telephone_regexp2 = re.compile(r'(Include)')
        number_regexp = re.compile(r'(INUMBER)')
        if Rating_regexp.search(element[1][0]) :
            if 'rating' not in actual_names:
                names.append(element[1][0])
                actual_names.append('rating')
                boxes.append([element[0], 'rating'])
        if Contract_regexp.search(element[1][0]) and Contract_regexp2.search(element[1][0]):
            if ('2') in element[1][0]:
                if 'contract_number' not in actual_names:
                    names.append(element[1][0])
                    actual_names.append('contract_number')
                    boxes.append([element[0], 'contract_number'])
        if Date_regexp.search(element[1][0]) and Date_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'date_issued'])
        if Requisition_regexp.search(element[1][0]) and Requisition_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'requisition/purchase_number'])
        if Solicitation_regexp.search(element[1][0]) and Solicitation_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'solicitation_number'])
        if Solicitation_type_regexp.search(element[1][0]) and Solicitation_type_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'solicitation_type'])
        if Amendmentno_regexp.search(element[1][0]) and Amendmentno_regexp2.search(element[1][0]):
            if '14' not in element[1][0]:
                names.append(element[1][0])
                boxes.append([element[0], 'amendment_no'])
        if Award_date_regexp.search(element[1][0]) and Award_date_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'award_date'])
        if Offer_date_regexp.search(element[1][0]) and Offer_date_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'offer_date'])
        if Award_amount_regexp.search(element[1][0]) and Award_amount_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'award_amount'])
        if Email_regexp.search(element[1][0]) and Email_regexp2.search(element[1][0]):
            names.append(element[1][0])
            boxes.append([element[0], 'email'])
        if Name_regexp.search(element[1][0]) and Name_regexp2.search(element[1][0]):
            if 'name' not in actual_names:
                if not Name_regexp3.search(element[1][0]):
                    names.append(element[1][0])
                    actual_names.append('name')
                    boxes.append([element[0], 'first_name'])
                elif  Name_regexp3.search(element[1][0]):
                    names.append(element[1][0])
                    actual_names.append('name')
                    boxes.append([element[0], 'second_name'])
        if Area_code_regexp.search(element[1][0]):
            if 'area_code' not in actual_names:
                names.append(element[1][0])
                actual_names.append( 'area_code')
                boxes.append([element[0], 'area_code'])
        if number_regexp.search(element[1][0]):
            if 'number' not in actual_names:
                names.append(element[1][0])
                actual_names.append( 'number')
                boxes.append([element[0], 'number'])
        if Extension_regexp.search(element[1][0]):
            if 'extension' not in actual_names:
                names.append(element[1][0])
                actual_names.append('extension')
                boxes.append([element[0], 'extension'])
        if Telephone_regexp.search(element[1][0]) and Telephone_regexp2.search(element[1][0]):
            if 'full_number' not in actual_names:
                names.append(element[1][0])
                actual_names.append( 'full_number')
                boxes.append([element[0], 'full_number'])
        if element[1][0]=='DATE':
            names.append(element[1][0])
            boxes.append([element[0], 'date'])
    #returning boxes list having coordinates of all key values with their name like given below list
    # [[[651.0, 133.0], [815.0, 133.0], [815.0, 156.0], [651.0, 156.0]],effective_date]
    return boxes,names


def get_first_page(result):

    my_dict = {'contract_number': '', 'solicitation_number': '', 'solicitation_type': '', 'date_issued': '',
               'requisition/purchase_number': '', 'email': '', 'rating': '','name':'', 'area_code': '', 'extension': '',
               'number': '','amendment_no': [], 'date': [], 'award_date': '', 'award_amount': '', 'offer_date': '','full_number':''}

    boxes, names = get_key_boxes(result)
    amendments=[]
    dates_list=[]
    # iterating over a result from OCR and saving box which have value from all_keys
    for line in result:
        if 'STANDARD FORM' in str(line[1][0]):
            my_dict['standard_form']=str(line[1][0])

    for r in result:
        for i in boxes:
            if i[1]=='amendment_no':
                y=50
                x=50
                if (0 <= (r[0][0][1] - i[0][0][1]) < y) and -80 <= (r[0][0][0] - i[0][0][0]) < x and r[1][0] not in names:
                    amendments.append(r[1][0])
                    my_dict[i[1]]=amendments
            elif i[1]=='date':
                x=50
                y=50
                if (0 <= (r[0][0][1] - i[0][0][1]) < y) and -30 <= (r[0][0][0] - i[0][0][0]) < x and r[1][0] not in names:
                    dates_list.append(r[1][0])
                    my_dict[i[1]]=dates_list
            elif i[1]=='second_name':
                x=250
                y=40
                if (0 <= (r[0][0][1] - i[0][0][1]) < y) and 100 <= (r[0][0][0] - i[0][0][0]) < x and r[1][0] not in names:
                    my_dict['name'] = r[1][0]
            elif i[1]=='full_number':
                x=80
                y=50
                if (0 <= (r[0][0][1] - i[0][0][1]) < y) and 0 <= (r[0][0][0] - i[0][0][0]) < x and r[1][0] not in names:
                    my_dict['full_number'] = r[1][0]

            else:
                x=80
                y=80
                if (0<=(r[0][0][1]-i[0][0][1])<y) and -10<=(r[0][0][0]-i[0][0][0])<x and r[1][0] not in names :
                    value = r[1][0]
                    if i[1]=='first_name':
                        my_dict['name']=value
                    elif i[1]=='solicitation_type':
                        if "X" not in r[1][0]:
                            value='SEALED BID (IFB)'
                            my_dict[i[1]] = value
                        elif "X" in r[1][0]:
                            value='NEGOTIATED (RFP)'
                            my_dict[i[1]]=value
                    elif i[1]=='award_date':
                        value=r[1][0].replace('Mby','May')
                        my_dict[i[1]] = value

                    else:
                        # lists for classifying values for matching
                        my_dict[i[1]] = value

    if my_dict['full_number']!='':
        my_dict['number']=my_dict['full_number']
        my_dict.pop('full_number', None)
    elif my_dict['full_number']=='':
        my_dict.pop('full_number', None)
    if 'CALL' in my_dict['name']:
        my_dict['name']=''
    return my_dict


def get_tabless_pages(pdf_path):
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
        table_pagess=[]
        for i in range(0, NumPages):
            Text = pdf.pages[i].extract_text()
            if re.search(String,Text):
                if re.search(string6,Text):
                    method='third'
                    table_pagess.append(i)
            if re.search(String,Text):
                if re.search(String2,Text):
                    method='first'
                    table_pagess.append(i)
            if re.search(String3, Text) and re.search(String4, Text) and re.search(String5,Text):
                method='second'
                table_pagess.append(i)
        if len(table_pagess)>0 :
            if method=='first' or method=='third':
                table_pagess.append(table_pagess[-1]+1)

    return table_pagess,method


def first_method(pdf_path,pagess):
    pagesss=','.join(str(v) for v in pagess)
    itemss = []
    try:
        tables = camelot.read_pdf(pdf_path,flavor='stream', edge_tol=500, pages=pagesss)
        seconddd=False
        for table in tables:
            try:
                index_change=False
                df = table.df
                try:
                    df.columns = ['ITEM NO', 'SUPPLIES/SERVICES', 'QUANTITY', 'UNIT', 'UNIT PRICE', 'AMOUNT']
                except:
                    df.columns = ['ITEM NO', 'SUPPLIES/SERVICES', 'QUANTITY', 'UNIT', 'AMOUNT']
                    seconddd=True
                indexxx = df.loc[df['ITEM NO'] == 'ITEM NO'].index
                if len(indexxx) == 0:
                    indexxx = df.loc[df['ITEM NO'] == 'ITEM NO \nSUPPLIES/SERVICES'].index
                    index_change = True
                count = 0
                for i in indexxx:
                    dff = df.iloc[i + 1]

                    if seconddd==True:
                        sss = dff['UNIT'].split('\n')
                        if len(sss) > 1:
                            dff['UNIT PRICE'] = sss[1]
                        else:
                            dff['UNIT PRICE'] = ''

                    if index_change == True:
                        data_change = [dff['SUPPLIES/SERVICES'], dff['QUANTITY'], dff['UNIT']]
                        dff['QUANTITY'] = data_change[0]
                        dff['UNIT'] = data_change[1]
                        dff['UNIT PRICE'] = data_change[2]
                    json1 = dff.to_json()
                    aDict = json.loads(json1)

                    if indexxx[-1] == i:
                        full_text = []
                        ccc = df.iloc[(i + 2):]
                        for index, row in ccc.iterrows():
                            full_text.append(row['SUPPLIES/SERVICES'])
                            full_text.append(row['QUANTITY'])
                        str1 = ''.join(full_text)
                        name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                        array = name.findall(str1)
                        aDict['SUPPLIES/SERVICES'] = str1
                        aDict['Clauses'] = array
                        itemss.append(aDict)
                        count += 1
                    else:
                        full_text = []
                        ccc = df.iloc[i + 2:indexxx[count + 1] - 1]
                        for index, row in ccc.iterrows():
                            full_text.append(row['SUPPLIES/SERVICES'])
                            full_text.append(row['QUANTITY'])

                        str1 = ''.join(full_text)
                        name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                        array = name.findall(str1)
                        count += 1
                        aDict['SUPPLIES/SERVICES'] = str1
                        aDict['Clauses'] = array
                        itemss.append(aDict)

            except:
                pass
    except:
        pass
    return itemss


def method2(pdf_path,pages):
    itemss_list=[]
    for p in pages:
        pp=p+10
        df = tabula.read_pdf(pdf_path, pages=str(p)+'-'+str(pp),stream=True)
        tables_list = []
        tables = df
        count = 0
        data = []
        for t in tables:
            try:
                if count == 0:
                    value = t.columns
                    t.columns = value
                    ff = t['Supplies/Service'].values.tolist()
                    data.append(' '.join(str(v) for v in ff))
                    t.drop('Supplies/Service', axis=1, inplace=True)
                    t.dropna(axis=0, how='all', inplace=True)
                    count += 1
                    tables_list.append(t)
                else:
                    t.columns = value
                    ff = t['Supplies/Service'].values.tolist()
                    data.append(' '.join(str(v) for v in ff))
                    t.drop('Supplies/Service', axis=1, inplace=True)
                    t.dropna(axis=0, how='all', inplace=True)
                    tables_list.append(t)
            except:
                pass
    d = '.'.join(data)
    new_list = []
    d = d.replace('Firm Fixed Price', 'Firm Fixed Price fffff')
    d = d.replace('Cost No Fee', 'Cost No Fee fffff')
    d = d.split('fffff')
    line_clauses=[]
    for f in d:
        new_list.append(f)
        name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
        array = name.findall(f)
        line_clauses.append(array)

    dff = pd.concat(tables_list, axis=0, ignore_index=True)
    vv = dff.loc[pd.isna(dff["Item"]), :].index

    for v in vv:
        if pd.notnull(dff['Unit Price'][v]):
            if pd.notnull(dff['Unit Price'][v - 1]):
                dff.iloc[v - 1, 3] = str(dff.iloc[v - 1, 3]) + ' ' + str(dff.iloc[v, 3])
            if pd.isnull(dff['Unit Price'][v - 1]):
                dff.iloc[v - 1, 3] = str(dff.iloc[v, 3])
        if pd.notnull(dff['Amount'][v]):
            if pd.notnull(dff['Amount'][v + 1]):
                dff.iloc[v + 1, 4] = str(dff.iloc[v, 4]) + '\n' + str(dff.iloc[v + 1, 4])
            elif pd.isnull(dff['Amount'][v + 1]):
                dff.iloc[v + 1, 4] = str(dff.iloc[v, 4])

    dff.dropna(thresh=2, axis=0, inplace=True)
    dff['Supplies/Services'] = new_list
    dff['Clauses'] = line_clauses
    itemsss=dff.to_json(orient="index")
    itemsss=json.loads(itemsss)
    for it in itemsss:
        itemss_list.append(itemsss[str(it)])
    for i in itemss_list:
        item_value=str(int(i['Item']))
        item_value_updated = item_value
        if len(item_value)==1:
            item_value_updated='000'+item_value
        elif len(item_value)==2:
            item_value_updated='00'+item_value
        elif len(item_value)==3:
            item_value_updated='0'+item_value
        i['Item']=item_value_updated

    return itemss_list


def third_method(pdf_path,pagess):
    pagesss=','.join(str(v) for v in pagess)
    itemss = []
    try:
        tables = camelot.read_pdf(pdf_path,flavor='stream', edge_tol=500, pages=pagesss)
        for table in tables:
            try:
                df = table.df
                df.columns = ['ITEM NO', 'SUPPLIES/SERVICES', 'QUANTITY', 'UNIT', 'UNIT PRICE', 'AMOUNT']
                indexxx = df.loc[df['ITEM NO'] == 'ITEM NO'].index

                count = 0
                for i in indexxx:
                    dff = df.iloc[i + 2]
                    json1 = dff.to_json()
                    aDict = json.loads(json1)
                    if indexxx[-1] == i:
                        full_text = []
                        ccc = df.iloc[(i + 2):]
                        for index, row in ccc.iterrows():
                            full_text.append(row['SUPPLIES/SERVICES'])
                        str1 = ''.join(full_text)
                        aDict['SUPPLIES/SERVICES'] = str1
                        name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                        array = name.findall(str1)
                        aDict['Clauses'] = array
                        itemss.append(aDict)
                        count += 1
                    else:
                        full_text = []
                        ccc = df.iloc[i + 2:indexxx[count + 1] - 1]
                        for index, row in ccc.iterrows():
                            full_text.append(row['SUPPLIES/SERVICES'])
                        str1 = ''.join(full_text)
                        count += 1
                        name = re.compile(r'\d{2,6}.\d{1,5}-\d{1,5}')
                        array = name.findall(str1)
                        aDict['SUPPLIES/SERVICES'] = str1
                        aDict['Clauses'] = array
                        itemss.append(aDict)
            except:
                pass

    except:
        pass

    return itemss

def get_clausess(pdf_path):
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
            lenarray = NumRegex.findall(Text)
            #if pattern match then implementing various algos
            try:
                if array.group():
                    NumRegex2 = re.compile(r'\d{4}', flags=0)
                    NumRegex3 = re.compile(r'\d{4}-\d{2}', flags=0)
                    gg = Text.split('\n')
                    for g in gg:
                        third = False
                        ggg = g.split(' ')
                        try:
                            next_linee = gg[gg.index(g) + 1]
                            nn=next_linee.split(' ')
                        except:
                            pass
                        ccc=''
                        if NumRegex.search(ggg[0]) and NumRegex2.search(nn[-1]):
                            if not NumRegex2.search(ggg[-1]):
                                ccc = g + ' ' + next_linee
                                if len(ccc) > 20:
                                    ccc = ccc.replace('(', '')
                                    ccc = ccc.replace(')', '')
                                    yy = ccc.split(' ')
                                    if yy[-2] in Months_list:
                                        yy[-2] = yy[-1] + '-' + str(Months_list.index(yy[-2]))
                                        yy = yy[:-1]
                                        g = ' '.join(yy)
                                    if '/' in yy[-1]:
                                        month = yy[-1].split('/')[1]
                                        year = yy[-1].split('/')[2]
                                        yy[-1] = year + '-' + month
                                        g = ' '.join(yy)
                                    clauses_list.append(g)


                        if NumRegex.search(ggg[0]) and (NumRegex2.search(ggg[-1])) :
                            lennn = False
                            try:
                                next_index=gg[gg.index(g)+1]

                                nexxx=next_index.split(' ')

                                if len(g)>=65 and len(lenarray)>3:
                                    if not NumRegex.search(nexxx[0]):
                                        lennn=True
                                        if g!=gg[-1] or g!=gg[-2] :
                                            thirddd=gg[gg.index(g) + 2]
                                            third_index = gg[gg.index(g) + 2].split(' ')
                                            if not NumRegex.search(third_index[0]) and len(third_index[0])<70 and len(lenarray)>8:
                                                third=True
                            except:
                                pass
                            if len(g)>20:
                                g=g.replace('(','')
                                g=g.replace(')','')
                                yy=g.split(' ')
                                if yy[-2] in Months_list:
                                    yy[-2]=yy[-1]+'-'+str(Months_list.index(yy[-2]))
                                    yy=yy[:-1]
                                    g=' '.join(yy)
                                if '/' in yy[-1]:
                                    month=yy[-1].split('/')[1]
                                    year=yy[-1].split('/')[2]
                                    yy[-1]=year+'-'+month
                                    g=' '.join(yy)
                                if lennn==True and third==False:
                                    g=g.split(' ')
                                    g=' '.join(g[0:-1])+' '+next_index+' '+g[-1]
                                elif lennn==True and third==True:
                                    g = g.split(' ')
                                    g = ' '.join(g[0:-1]) + ' ' + next_index +' '+thirddd+ ' ' + g[-1]
                                clauses_list.append(g)

                        if NumRegex.search(ggg[0]) and (NumRegex3.search(ggg[-1])):
                            if len(g.split(' '))==2:
                                cc=ggg[0]+' '+gg[gg.index(g)-1]+' '+gg[gg.index(g)+1]+' '+ggg[-1]
                                clauses_list.append(cc)
            except Exception as e:
                pass

    clausess_new_list = []
    for c in clauses_list:
        cc = c.split(' ')
        clausee = cc[0] + ' | ' + ' '.join(cc[1:-1]) + ' | ' + cc[-1]
        clausess_new_list.append(clausee)
    return clausess_new_list




def main(pdf_path,result):

    #getting_data_from_first_page
    mydict=get_first_page(result)

    #getting method and page numbers
    pagess,method=get_tabless_pages(pdf_path)

    #different methods to get lineitems depend on method
    if method=='first':
        iteemms=first_method(pdf_path,pagess)
        mydict['items']=iteemms
    elif method=='second':
        iteemms=method2(pdf_path,pagess)
        mydict['items'] = iteemms
    elif method=='third':
        iteemms=third_method(pdf_path,pagess)
        mydict['items']=iteemms
    elif method=='':
        mydict['items']=[]
    #for getting clauses
    clausess=get_clausess(pdf_path)
    mydict['clauses']=clausess
    return mydict


