from BaseMessage import GetBaseMessage
import re
from IPMessage import IPMessage
from DomainMessage import DomainMessage
from index import app
from exts import db
from models import BaseInfo,IPInfo,DomainInfo
import ImportToRedis
import redis
import  get_message
from XSSBug.XSSCheck import GetXSS
'''
获取baseinfo ->MySQL
 ip->获取ipinfo->MySQL
 domain->获取domaininfo->MySQL
页面url深度遍历 ->从redis里读取->bugscan->MySQL
    未设置外键，用程序来保证逻辑的正确性
'''
def SZheConsole(url,redispool):
    baseinfo=GetBaseMessage(url,redispool)
    pattern = re.compile('^\d+\.\d+\.\d+\.\d+$')
    if pattern.findall(url):
        boolcheck=True
        ipinfo=IPMessage(url)
    else:
        boolcheck=False
        domaininfo=DomainMessage(url,redispool)
    try:
        with app.app_context():
            info=BaseInfo(url=url,boolcheck=boolcheck,status=baseinfo.GetStatus(),title=baseinfo.GetTitle(),date=baseinfo.GetDate(),responseheader=baseinfo.GetResponseHeader(),
                                    Server=baseinfo.GetFinger(),portserver=baseinfo.PortScan(),sendir=baseinfo.SenDir())
            db.session.add(info)
            db.session.flush()
            if boolcheck:
                db.session.add(IPInfo(baseinfoid=info.id,bindingdomain=ipinfo.GetBindingIP(),sitestation=ipinfo.GetSiteStation(),CMessage=ipinfo.CScanConsole(),
                                      ipaddr=ipinfo.FindIpAdd()))
            else:
                db.session.add(DomainInfo(baseinfoid=info.id,subdomain=domaininfo.GetSubDomain(),whois=domaininfo.GetWhoisMessage(),bindingip=domaininfo.GetBindingIP(),
                                          sitestation=domaininfo.GetSiteStation(),recordinfo=domaininfo.GetRecordInfo(),domainaddr=domaininfo.FindDomainAdd()))
            db.session.commit()
    except Exception as e:
        print(e)
        pass

if __name__=='__main__':
    redispool = redis.Redis(connection_pool=ImportToRedis.redisPool)
    # SZheConsole('www.taobao.com',redispool)
    GetXSS("http://leettime.net/xsslab1/chalg1.php?name=1",redispool)
    # print(get_message.SubDomainBurst("www.taobao.com",redispool))