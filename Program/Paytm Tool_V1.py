import PyPDF2
import pandas as pd
import numpy as np


# PDF file Directory
path = 'C:/Users/u281311/Desktop/Paytm Analytics Tool/Data/'
PDFfilename = "Paytm_data.pdf"
sys_text = 'This is system generated wallet transaction history. If you have any queries,call us at 0120-3888388.'

###############################################
#### Function to create PDF into CSV file #####
###############################################
def convert_pdf(file_name,path,sys_text):
    pfr = PyPDF2.PdfFileReader(open(path+file_name, "rb"))
    
    page_data=[]
    for i in range(pfr.getNumPages()):
        page_data.append((pfr.getPage(i)).extractText())
    # Converting list to string    
    total_data = " ".join(page_data)
    
    # Removing Address & System generated messages
    total_data= total_data.replace(sys_text,'')
    #total_data= total_data.replace(add_text,'')
    unwanted_text =total_data.find("DETAILSAMOUNTTRANSACTION STATUS",1)+len("DETAILSAMOUNTTRANSACTION STATUS")
    total_data = total_data[unwanted_text:]
    
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
            new_list.append(k1)
        else:
            break
    
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
    
    # Creating a dataframe 
    paytm_data= pd.DataFrame([])
    for i in new_list:
        paytm_data=paytm_data.append(Seperator_add(i))
        
    return(paytm_data)

#Calling Function
final_data = convert_pdf('paytm_data.pdf',path,sys_text)

len(final_data)

