import re

def get_first_page(result):

    all_keys=['1. CONTRACT ID CODE','2 AMENDMENT/MODFICATIONNO','3 EFFECIVEDAIE','1 CONIRACTDCODE','4 REQUISITION/PURCHASE REQ NO','2. AMENDMENT/MODIFICATION NUMBER','EFFECTIVE DATE',' 2. AMENDMENT/MODIFICATION NO.','3.EFFECTIVE DATE','4. REQUISITION/PURCHASE REQ NO'
        ,'4. REQUISITION/PURCHASE REQUISITION NUMBER','6. ISSUED BY','6 ISSUED BY','6.ISSUED8Y AFLCMC/HBQK','6.ISSUEDBY AFLCMC/HBQK','6. ISSUED BY AFLCMC/HBQK','7 ADMINISTERED BY (Ifotherthan item 6','7. ADMINISTERED BY (If other than Item 6)','7. ADMINISTERED BY (If other than Item 6)',
        '7. ADMINISTERED BY (lf other than Item 6)','5. PROJECT NUMBER (If applicable)','5. PROJECT NO. (If applicable)','5 PROJECT NO,(lf applicsb/e)']

    boxes = []
    my_dict={'contract_code':'','amendment_no':'','effective_date':'','requisition/purchase_number':'','project_number':'','issued_by':'','administered_by':'','standard_form':''}
    # iterating over a result from OCR and saving box which have value from all_keys
    for line in result:
        if 'STANDARD FORM' in str(line[1][0]):
            my_dict['standard_form']=str(line[1][0])
        if str(line[1][0]) in all_keys:
            boxes.append([line[0],line[1][0]])

    issued_text = []
    admin_text=[]
    issuedx_coordinate = ''
    issuedy_coordinate = ''
    adminx_coordinate = ''
    adminy_coordinate = ''
    issue_code=''
    admin_code=''
    for r in result:
        contract_list=['1. CONTRACT ID CODE','1 CONIRACTDCODE']
        amendment_list=['2 AMENDMENT/MODFICATIONNO','2. AMENDMENT/MODIFICATION NUMBER',' 2. AMENDMENT/MODIFICATION NO.']
        date_list=['3 EFFECIVEDAIE','EFFECTIVE DATE','3.EFFECTIVE DATE']
        purchase_list=['4. REQUISITION/PURCHASE REQ NO','4. REQUISITION/PURCHASE REQUISITION NUMBER','4 REQUISITION/PURCHASE REQ NO']
        issued_list=['6. ISSUED BY','6 ISSUED BY','6.ISSUED8Y AFLCMC/HBQK','6.ISSUEDBY AFLCMC/HBQK','6. ISSUED BY AFLCMC/HBQK']
        project=['5. PROJECT NUMBER (If applicable)','5. PROJECT NO. (If applicable)','5 PROJECT NO,(lf applicsb/e)']
        admin=['7 ADMINISTERED BY (Ifotherthan item 6','7. ADMINISTERED BY (If other than Item 6)',
               '7. ADMINISTERED BY (lf other than Item 6)','7. ADMINISTERED BY (If other than Item 6)']


        for i in boxes:
            if admin_code=='':
                if r[1][0] in admin:
                    present = result.index(r)
                    admin_string=result[present+2][1][0]
                    digit = 0
                    for ch in admin_string:
                        if ch.isdigit():
                            digit = digit + 1
                    if digit>=3 or len(admin_string.split(' '))==1:
                        admin_code='Code: '+result[present+2][1][0]
            if issue_code=='':
                if r[1][0] in issued_list:
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
                        if digit>=3 or len(issued_string.split(' '))==1:
                            issue_code='CODE: '+ issued_string

            if (0 <= (r[0][0][1] - i[0][0][1]) < 60) and -20 <= (r[0][0][0] - i[0][0][0]) < 80 and r[1][0] not in all_keys:
                if i[1] in contract_list:
                    my_dict['contract_code']=r[1][0]
                if i[1] in amendment_list:
                    my_dict['amendment_no']=r[1][0]
                if i[1] in date_list:
                    my_dict['effective_date'] = r[1][0]
                if i[1] in purchase_list:
                    my_dict['requisition/purchase_number'] = r[1][0]
                if i[1] in project:
                    my_dict['project_number']=r[1][0]
                if i[1] in issued_list:
                    issuedx_coordinate = r[0][0][0]
                    issuedy_coordinate = r[0][0][1]
                    issued_text.append(issue_code)
                if i[1] in admin:
                    adminx_coordinate = r[0][0][0]
                    adminy_coordinate = r[0][0][1]
                    admin_text.append(admin_code)
        if adminy_coordinate:
            if -8<=(r[0][0][0]-adminx_coordinate)<10 and 0<=(r[0][0][1]-adminy_coordinate)<=60:
                admin_text.append(r[1][0])
                adminx_coordinate = r[0][0][0]
                adminy_coordinate = r[0][0][1]
        if issuedx_coordinate:
            if -8<=(r[0][0][0]-issuedx_coordinate)<10 and 0<=(r[0][0][1]-issuedy_coordinate)<=35:
                issued_text.append(r[1][0])
                issuedx_coordinate = r[0][0][0]
                issuedy_coordinate = r[0][0][1]
    if len(issued_text)>0:
        my_dict['issued_by']='\n'.join(issued_text)
    if len(admin_text)>0:
        my_dict['administered_by'] = '\n'.join(admin_text)

    return my_dict


def mains30(result):
    #to get data from first page
    mydict=get_first_page(result)
    return mydict