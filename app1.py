from flask import Flask,request
import pickle
import pandas as pd


with open("Anomaly.pkl",'rb') as f:
    clf=pickle.load(f)

app = Flask(__name__)


@app.route('/')
def rep():
    return "Welcome Default Page"



    
@app.route('/sata' , methods=["POST"])
def sata():
    data=request.get_json()
    #response = {
        #'message': 'JSON received successfully!',
        #'received_data': data
   # }
    data1=dict(data)
    #df=pd.DataFrame(data1)
    # Convert JSON data to DataFrame
    df = pd.DataFrame([data1])
    #df=df.to_dict()

  
    #df=pd.DataFrame.from_dict(data1,orient='index',columns=['value'])
    #df = pd.DataFrame(data1, columns=columns, index=index)
    #print(df.columns)
    ## New feature srcbytes/sec
    df['srcbytes/sec'] = df.apply(lambda row : row['srcbytes']/row['duration'] if row['duration'] != 0 else row['srcbytes']/(row['duration'] + 0.001),axis=1 )

    ## New feature dstbytes/sec
    df['dstbytes/sec'] = df.apply(lambda row : row['dstbytes']/row['duration'] if row['duration'] != 0 else row['dstbytes']/(row['duration'] + 0.001), axis=1)
    ##Creating new feature with  rate features with respective counts for Source hosts
    ## Create df['serrorrate_count']
    df['serrorrate_count']=df['serrorrate']*df['count']

    ## Create df['rerrorrate_count']
    df['rerrorrate_count']=df['rerrorrate']*df['count']

    ## Create df['samesrvrate_count]
    df['samesrvrate_count']=df['samesrvrate']*df['count']

    ## Create df['diffsrvrate_count']
    df['diffsrvrate_count']=df['diffsrvrate']*df['count']

    ##Create df['srvserrorrate_count']
    df['srvserrorrate_count']=df['srvserrorrate']*df['srvcount']

    ##Create df['srvrerrorrate_count']
    df['srvrerrorrate_count']=df['srvrerrorrate']*df['srvcount']

    ##Create df['srvdiffhostrate_count']
    df['srvdiffhostrate_count']=df['srvdiffhostrate']*df['srvcount']
    ##Creating new feature with  rate features with respective counts for destination hosts

    ## Create df[dsthosterrorrate_count']
    df['dsthostrerrorrate_count']=df['dsthostserrorrate']*df['dsthostcount']

    ## Create df['dsthostserrorrate_count']
    df['dsthostserrorrate_count']=df['dsthostserrorrate']*df['dsthostcount']

    ## Create df['dsthostsamesrvrate']
    df['dsthostsamesrvrate_count']=df['dsthostsamesrvrate']*df['dsthostcount']

    ## Create df['dsthostdiffsrvrate']
    df['dsthostdiffsrvrate_count']=df['dsthostdiffsrvrate']*df['dsthostcount']

    ## Create df['dsthostsrvserrorrate_count']
    df['dsthostsrvserrorrate_count']=df['dsthostsrvserrorrate']*df['dsthostsrvcount']

    ## Create df['dsthostsrvrerrorrate_count']
    df['dsthostsrvrerrorrate_count']=df['dsthostsrvrerrorrate']*df['dsthostsrvcount']

    ## Create df['dsthostsamesrcportrate_count']
    df['dsthostsamesrcportrate_count']=df['dsthostsamesrcportrate']*df['dsthostcount']

    ## Create df['dsthostsrvdiffhostrate_count']
    df['dsthostsrvdiffhostrate_count']=df['dsthostsrvdiffhostrate']*df['dsthostsrvcount']
    
    ## Create a new feature called "flag_category" Flag group based on their type.
    Success_Flag = ['SF']
    S_Flag = ['S0', 'S1', 'S2', 'S3']
    R_Flag = ['REJ']
    Reset_Flag = ['RSTR', 'RSTO', 'RSTOS0']
    SH_Oth_Flag = ['SH','OTH']

    for j in range(df.shape[0]):
        if df['flag'][j] in Success_Flag:
            df['flag']='Success Flag'
        elif df['flag'][j] in S_Flag:
            df['flag']='S Flag'
        elif df['flag'][j] in R_Flag:
            df['flag']='R Flag'
        elif df['flag'][j] in Reset_Flag:
            df['flag']='Reset Flag'
        else:
            df['flag']='SH&Oth Flag'
        
       ## Converting 'suattempted' feature to binary
    df['suattempted']=df['suattempted'].apply(lambda x : 0 if x == 0 else 1) 
    
    ## Create a new feature called "service_category" Service group based on the type of Service it meant for
    srv_ftp=['ftp_data','tftp_u','ftp','printer','uucp','uucp_path','printer','pm_dump']
    srv_http=['http','http_443','http_2784','http_8001','gopher','whois','Z39_50','efs']
    srv_other=['other','private','iso_tsap','eco_i','ecr_i','urp_i','urh_i','red_i','tim_i','sunrpc','X11','rje','auth','csnet_ns', 'aol','ctf','finger','vmnet','link','harvest','courier','time','exec','bgp', 'daytime']
    srv_ras=['telnet','shell','ssh','kshell','klogin','login','supdup','rje','remote_job']
    srv_msg =['imap4','pop_3', 'smtp', 'pop_2','nntp','IRC','nnsp']
    srv_nw_dns=['netbios_dgm','hostnames','domain' , 'netbios_ns', 'netbios_ssn' ,'domain_u','ntp_u','name']
    srv_nw_error=['netstat','echo','systat','discard']
    srv_ad=['ldap','sql_net']
    for i in range(df.shape[0]):
        if df['service'][i] in srv_ftp:
            df['service']='File Transfer Services'
        elif df['service'][i] in srv_http:
            df['service']='Application/web Services'
        elif df['service'][i] in srv_other:
            df['service']='Others/legacy Services'
        elif df['service'][i] in srv_ras:
            df['service']='Remote Access Services'
        elif df['service'][i] in srv_msg:
            df['service']='Messaging Services'
        elif df['service'][i] in srv_nw_dns:
            df['service_category']='Network & Name Server Services'
        elif df['service'][i] in srv_nw_error:
            df['service']='Network Tshoot Error Services'
        else:
            df['service']='AD and DB Services'
            
    #Encode categorical Variables
    from sklearn.preprocessing import LabelEncoder
    le=LabelEncoder()
    cat_cols=df.select_dtypes(include='object').columns
    for col in cat_cols:
        df[col]=le.fit_transform(df[col])
    from sklearn.preprocessing import MinMaxScaler

    scaler = MinMaxScaler()

    df = scaler.fit_transform(df)
    
    df = pd.DataFrame(df)
    
    result=clf.predict(df)
    if result == 1:
        return "Normal"
    else:
        return "Attack"
    print(result)
    #return jsonify(data)







