import PyPDF2
import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None  # default='warn'

def list_create(sentence):
    sent_1 = sentence.split('Seperator')
    sent_2 = sent_1[:2]
    sent_3 = sent_1[3:-2]
    sent_4= sent_1[6]
    sent_3.append(k4)
    sent_2.extend(sent_3)
    sent_2.append(sent_1[5]+sent_1[2])
    return(sent_2)

def Seperator_add_format_2(k2):
    # Variable-1
    if(k2[0:22].find(' PM')>0):
        k2=k2.replace(' PM',' PM Seperator ',1)   
    if(k2[0:22].find(' AM')>0):
        k2=k2.replace(' AM',' AM Seperator ',1)
        
    #Variable-2
    k2=k2.replace('Paytm Cash Txn',' Seperator Paytm Cash Txn',1)
    
    # Variable-3
    k2 = k2.replace('Rs','Seperator',1)
    
    # Variable-4
    first_index =k2.find("ID  #",1)+len("ID  #")
    #last_index =k2.find(" Order",1)+len(" Order")
    
    if(k2[first_index:].find('+')>0):
        k2 = k2.replace('+','SeperatorCreditSeperator',1)
    else:
        k2 = k2.replace('-','SeperatorDebitSeperator',1)
    
    # Variable-5
    if(k2[-7:]=='SUCCESS'):
        k2= k2[:-7]+" SeperatorSUCCESS "
    elif(k2[-7:]=='FAILURE'):
        k2= k2[:-7]+"SeperatorFAILURE"
    else:
        k2= k2[:-13]+" SeperatorREFUNDED_BACK" 
        
    k3 = pd.DataFrame(list_create(k2))
    k4 = k3.T
    k4.columns = ['Date','Activity','Amount','Amount_type','Amount_Status','Order_info']
    return(k4)

def Seperator_add(k2):
    if(k2[0:22].find(' PM')>0):
        k2=k2.replace(' PM',' PM Seperator ',1)   
    if(k2[0:22].find(' AM')>0):
        k2=k2.replace(' AM',' AM Seperator ',1)
    #k2=k2.replace(' AM',' AM Seperator ',1)
    k2=k2.replace('Rs.',' Seperator ',1)
    k2=k2.replace('+SUCCESS',' Seperator Credit Seperator SUCCESS Seperator',1)
    k2=k2.replace('+FAILURE',' Seperator Credit Seperator FAILURE Seperator',1)
    k2=k2.replace('-SUCCESS',' Seperator Debit Seperator SUCCESS Seperator',1)
    k2=k2.replace('-FAILURE',' Seperator Debit Seperator FAILURE Seperator',1)
    k2=k2.replace('+REFUNDED_BACK',' Seperator Debit Seperator REFUNDED_BACK Seperator',1)
    k2=k2.replace('-REFUNDED_BACK',' Seperator Debit Seperator REFUNDED_BACK Seperator',1)
    #k2=k2.replace('SUCCESS','SUCCESS Seperator ')
    #k2=k2.replace('FAILURE','FAILURE Seperator ')
    k3 = k2.split('Seperator')
    k3 = pd.DataFrame(k3)
    k4 = k3.T
    k4.columns = ['Date','Activity','Amount','Amount_type','Amount_Status','Order_info']
    return(k4)


def fun_selection(new_list,function_type):
    paytm_data= pd.DataFrame([])
    for i in new_list:
            #print(i)
            paytm_data=paytm_data.append(function_type(i))
    return(paytm_data)    


def data_preparation(final_data):
    var = final_data.columns.tolist()
    for i in var: 
        final_data[i]=final_data[i].str.strip()
        final_data[i]=final_data[i].str.lower()
        
    # Removing unwanted data
    final_data = final_data[final_data['Amount_Status']!='failure']
    final_data = final_data[final_data['Activity']!='refunded back']
    final_data = final_data[final_data['Activity']!='on hold for order']
        
    # Extracting Name variable from Activity and order info variable
    final_data[['Money_sent_tag','Money_sent_name']] = final_data.Activity.str.split(' to ',expand=True)
    final_data.Money_sent_tag = final_data.Money_sent_tag.str.strip()
        
    # Order ID Seperation
    final_data[['Order_for','Order_ID']] = final_data.Order_info.str.split('paytm cash txn',expand=True)
        
    #final_data.Order_for = final_data.Order_for.str.replace("Order",'')
    final_data.Order_ID = final_data.Order_ID.str.replace("id",'')

    # Order ID Seperation
    final_data[['Order_for_name','Order_New_Tag']] = final_data.Order_for.str.split('order',expand=True)
    
    final_data.Money_sent_name.fillna(final_data.Order_for_name,inplace=True)
    final_data.Money_sent_name = final_data.Money_sent_name.str.strip()
    #final_data['Receiver_Name'] = np.where(final_data.Money_sent_name==''& np.where(final_data.Amount_Status=='debit'),'blank',final_data.Money_sent_name)

    final_data['Receiver_Name'] = np.where(final_data.Money_sent_name=='','blank',final_data.Money_sent_name)
    final_data.Receiver_Name = final_data.Receiver_Name.str.replace('  ',' ')
    #final_data['Money_Received_from_name'] = final_data.Activity.str.split(' from ',expand=True)[1]
    #final_data['Money_Received_from_name'].fillna('no_received',inplace=True)
    
    # converting Amount to float type
    final_data.Amount = final_data.Amount.astype(float)
    final_data['Date_var'] = final_data['Date'].map(lambda x: x[0:9])
    final_data.Date_var = pd.to_datetime(final_data.Date_var,format='%d %b %y')
    
    var_updated = var+['Receiver_Name','Date_var','Money_sent_name']
    final_data = final_data[var_updated]
    return(final_data)

###############################################
#### Function to create PDF into CSV file #####
###############################################

def convert_pdf(input_data):
    pfr = PyPDF2.PdfFileReader(open(input_data, "rb"))
    sys_text = 'This is system generated wallet transaction history. If you have any queries,call us at 0120-3888388.'
    page_data=[]
    for i in range(pfr.getNumPages()):
        page_data.append((pfr.getPage(i)).extractText())
    # Converting list to string    
    total_data = " ".join(page_data)
    
    # Removing Address & System generated messages
    total_data= total_data.replace(sys_text,'')
    
    unwanted_text_fun2 =total_data.find("DETAILSAMOUNTTRANSACTION STATUS",1)+len("DETAILSAMOUNTTRANSACTION STATUS")
    flag=0
    
    if(total_data.find("ACCOUNT DETAILS",1)>0):
        unwanted_text_fun1 =total_data.find("ACCOUNT DETAILS",1)+len("ACCOUNT DETAILS")
        flag=1
        total_data = total_data[unwanted_text_fun1:]
    else:
        total_data = total_data[unwanted_text_fun2:]
    
    # Splitting paragraph into rows 
    months = [" JAN "," FEB "," MAR ",' APR ',' MAY ',' JUN ',' JUL '," AUG ",' SEP '," OCT "," NOV "," DEC "]
    
    for i in months:
        match = str(str('TAG_REMOVER')+i)
        total_data = total_data.replace(i,match)
    final_data = total_data.split('TAG_REMOVER')
    
    # Changing rows into complete row
    new_list=[]
    for i in range(len(final_data)-1):
        if(i<len(final_data)):
            k1 = final_data[i][-2:]+ final_data[i+1][:-2]
            k1 = k1.strip()
            new_list.append(k1)
        else:
            break
            
    if(flag==0):
        paytm_data = fun_selection(new_list,Seperator_add)
    else:
        paytm_data = fun_selection(new_list,Seperator_add_format_2)
    final_data = data_preparation(paytm_data)   
    return(final_data)