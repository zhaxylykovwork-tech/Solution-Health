"""Create editable Draw.io, SVG, PNG and vector PDF from one explicit layout.

Requires Pillow and ReportLab. Use Windows Arial or DejaVu Sans on Linux.
"""
from pathlib import Path
from html import escape
import math
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
FONT = next(p for p in [Path('C:/Windows/Fonts/arial.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')] if p.exists())
pdfmetrics.registerFont(TTFont('Diagram', str(FONT)))

def box(key, x, y, w, h, lines, color='#e4efff'):
    return dict(key=key,x=x,y=y,w=w,h=h,lines=lines,color=color)

def arrow(a,b,pts,label,at,dashed=False):
    return dict(a=a,b=b,pts=pts,label=label,at=at,dashed=dashed)

def render(path,title,subtitle,nodes,edges,W,H,footnotes=(),lifelines=False):
    out=ROOT/path; out.parent.mkdir(parents=True,exist_ok=True)
    im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    pdf=canvas.Canvas(str(out.with_suffix('.pdf')),pagesize=(W,H)); pdf.setTitle(title)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',f'<rect width="{W}" height="{H}" fill="white"/>']
    mx=ET.Element('mxfile',host='app.diagrams.net'); dia=ET.SubElement(mx,'diagram',id=path.replace('/','-'),name=title)
    graph=ET.SubElement(dia,'mxGraphModel',grid='1',page='1',pageWidth=str(W),pageHeight=str(H)); rt=ET.SubElement(graph,'root')
    ET.SubElement(rt,'mxCell',id='0'); ET.SubElement(rt,'mxCell',id='1',parent='0')
    def text(x,y,s,size=21,color='#21324b'):
        f=ImageFont.truetype(str(FONT),size)
        d.text((x,y),s,font=f,fill=color)
        svg.append(f'<text x="{x}" y="{y+size}" font-family="Arial,DejaVu Sans,sans-serif" font-size="{size}" fill="{color}">{escape(s)}</text>')
        pdf.setFillColor(color); pdf.setFont('Diagram',size); pdf.drawString(x,H-y-size,s)
    def line(pts,color='#48617f',width=2,dash=False):
        if dash:
            for (x1,y1),(x2,y2) in zip(pts,pts[1:]):
                length=math.hypot(x2-x1,y2-y1)
                for start in range(0,int(length),14):
                    end=min(start+8,length)
                    d.line([(x1+(x2-x1)*start/length,y1+(y2-y1)*start/length),(x1+(x2-x1)*end/length,y1+(y2-y1)*end/length)],fill=color,width=width)
        else:
            d.line(pts,fill=color,width=width)
        points=' '.join(f'{x},{y}' for x,y in pts)
        svg.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="8 6"' if dash else '')+'/>')
        pdf.setStrokeColor(color); pdf.setLineWidth(width); pdf.setDash([8,6] if dash else [])
        p=pdf.beginPath();p.moveTo(pts[0][0],H-pts[0][1])
        for x,y in pts[1:]:p.lineTo(x,H-y)
        pdf.drawPath(p);pdf.setDash([])
    def rect(x,y,w,h,fill,stroke='#48617f'):
        d.rectangle((x,y,x+w,y+h),fill=fill,outline=stroke,width=2)
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        pdf.setFillColor(fill);pdf.setStrokeColor(stroke);pdf.rect(x,H-y-h,w,h,fill=1,stroke=1)
    def mxtext(key,x,y,w,h,value,size=20):
        cell=ET.SubElement(rt,'mxCell',id=key,value=value,style=f'text;html=0;whiteSpace=wrap;align=left;verticalAlign=top;fontSize={size};fontFamily=Arial;',vertex='1',parent='1')
        ET.SubElement(cell,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),**{'as':'geometry'})
    text(40,20,title,32);text(40,66,subtitle,20)
    mxtext('title',40,20,W-80,80,title+'\n'+subtitle,24)
    if lifelines:
        for n in nodes:
            x=n['x']+n['w']/2;y=n['y']+n['h']
            line([(x,y),(x,H-110)],dash=True)
            c=ET.SubElement(rt,'mxCell',id='life-'+n['key'],style='endArrow=none;dashed=1;strokeColor=#48617f;',edge='1',parent='1')
            g=ET.SubElement(c,'mxGeometry',relative='1',**{'as':'geometry'});ET.SubElement(g,'mxPoint',x=str(x),y=str(y),**{'as':'sourcePoint'});ET.SubElement(g,'mxPoint',x=str(x),y=str(H-110),**{'as':'targetPoint'})
    # Draw routes before boxes. Labels are white-backed to remain readable.
    for i,e in enumerate(edges):
        pts=e['pts'];line(pts,dash=e['dashed'])
        a,b=pts[-2],pts[-1];angle=math.atan2(b[1]-a[1],b[0]-a[0]);tri=[b,(b[0]-12*math.cos(angle-.4),b[1]-12*math.sin(angle-.4)),(b[0]-12*math.cos(angle+.4),b[1]-12*math.sin(angle+.4))]
        d.polygon(tri,fill='#48617f');svg.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in tri)+'" fill="#48617f"/>')
        pdf.setFillColor('#48617f');p=pdf.beginPath();p.moveTo(tri[0][0],H-tri[0][1]);p.lineTo(tri[1][0],H-tri[1][1]);p.lineTo(tri[2][0],H-tri[2][1]);p.close();pdf.drawPath(p,fill=1,stroke=0)
        c=ET.SubElement(rt,'mxCell',id=f'e{i}',style='edgeStyle=none;endArrow=block;strokeColor=#48617f;'+('dashed=1;' if e['dashed'] else ''),edge='1',parent='1')
        g=ET.SubElement(c,'mxGeometry',relative='1',**{'as':'geometry'});ET.SubElement(g,'mxPoint',x=str(pts[0][0]),y=str(pts[0][1]),**{'as':'sourcePoint'});ET.SubElement(g,'mxPoint',x=str(b[0]),y=str(b[1]),**{'as':'targetPoint'});arr=ET.SubElement(g,'Array',**{'as':'points'})
        for x,y in pts[1:-1]:ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
        lx,ly=e['at'];lab=e['label'];tw=d.textlength(lab,font=ImageFont.truetype(str(FONT),19))
        rect(lx-4,ly-1,tw+8,26,'white','white');text(lx,ly,lab,19);mxtext(f'el{i}',lx,ly,tw+10,28,lab,19)
    for n in nodes:
        x,y,w,h=n['x'],n['y'],n['w'],n['h'];rect(x,y,w,h,n['color'])
        for i,s in enumerate(n['lines']):
            assert d.textlength(s,font=ImageFont.truetype(str(FONT),20)) < w-24,(path,n['key'],s)
            text(x+12,y+12+i*27,s,20)
        assert len(n['lines'])*27+18 <= h,(path,n['key'])
        c=ET.SubElement(rt,'mxCell',id=n['key'],value='\n'.join(n['lines']),style=f'whiteSpace=wrap;html=0;fillColor={n["color"]};strokeColor=#48617f;fontSize=20;align=left;spacing=12;fontFamily=Arial;',vertex='1',parent='1')
        ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),**{'as':'geometry'})
    for i,s in enumerate(footnotes):
        y=H-75+i*26;text(40,y,s,19);mxtext(f'foot{i}',40,y,W-80,25,s,19)
    svg.append('</svg>');out.with_suffix('.svg').write_text('\n'.join(svg),encoding='utf8');im.save(out.with_suffix('.png'))
    pdf.showPage();pdf.save();ET.indent(mx);ET.ElementTree(mx).write(out.with_suffix('.drawio'),encoding='utf-8',xml_declaration=True)

def context():
    n=[box('patient',50,120,260,100,['Пациент','[Человек]'],'#f1f3f6'),box('app',600,120,300,100,['Мобильное приложение','[Внешний участник]']),box('idp',1250,120,300,100,['IdP [новая система]','OIDC / OAuth 2.0']),
       box('portal',50,380,300,100,['Веб-портал [существ.]','Перевод на общий API'],'#f1f3f6'),box('platform',600,380,400,160,['Мобильная платформа [новая]','[Центральная система]','Gateway/BFF, Saga,','платёжный адаптер']),box('lis',1450,380,350,120,['LIS [существующая]','Результаты / REST','Лаборант: просмотр'],'#f1f3f6'),
       box('schedule',50,700,300,120,['Расписание [существ.]','REST / врачебные слоты','Hold / Confirm / Cancel'],'#f1f3f6'),box('crm',600,700,300,120,['CRM [существующая]','Карточка / анализы','REST / read model'],'#f1f3f6'),box('policy',1100,700,300,120,['Полис-фасад [новый]','Read model ДМС','Свежесть / UNKNOWN']),box('adapter',1500,700,300,120,['LIS Integration [новый]','Захват / spool / outbox','Контроль полноты']),
       box('notify',50,1000,300,120,['Уведомления [существ.]','SMS / email / push','Внешние провайдеры'],'#f1f3f6'),box('psp',500,1000,300,120,['PSP [внешний существ.]','REST / оплата / статус','Возврат: контракт'],'#f1f3f6'),box('lab',950,1000,350,120,['Lab Reservation [новый]','Квоты забора биоматериала','Собственный календарь']),box('broker',1450,1000,350,120,['RabbitMQ [расширяется]','Async AMQP/TLS','Раздельные очереди']),box('onec',1100,1280,300,100,['1С: Полисы [существ.]','HTTP через адаптер'],'#f1f3f6')]
    e=[arrow('patient','app',[(310,170),(600,170)],'01 Использует',(360,140)),arrow('app','platform',[(750,220),(750,380)],'02 HTTPS API',(765,285)),arrow('app','idp',[(900,170),(1250,170)],'03 OIDC + PKCE',(965,140)),arrow('platform','idp',[(1000,420),(1130,420),(1130,260),(1400,260),(1400,220)],'04 JWKS / HTTPS',(1150,230)),arrow('platform','schedule',[(600,480),(450,480),(450,760),(350,760)],'05 REST',(360,720)),arrow('platform','crm',[(750,540),(750,700)],'06 REST',(765,600)),arrow('platform','policy',[(1000,500),(1250,500),(1250,700)],'07 REST',(1140,560)),arrow('policy','onec',[(1250,820),(1370,820),(1370,1230),(1250,1230),(1250,1280)],'08 HTTP',(1265,1245)),arrow('platform','psp',[(600,520),(400,520),(400,1060),(500,1060)],'09 REST',(405,1020)),arrow('platform','lab',[(1000,530),(1050,530),(1050,1000)],'10 REST',(1065,905)),arrow('adapter','lis',[(1650,700),(1650,500)],'11 REST polling',(1665,600)),arrow('adapter','broker',[(1650,820),(1650,1000)],'12 AMQP',(1665,905)),arrow('broker','crm',[(1450,1040),(1420,1040),(1420,870),(750,870),(750,820)],'13 Результаты / async',(800,840)),arrow('platform','broker',[(1000,410),(1180,410),(1180,330),(1850,330),(1850,1060),(1800,1060)],'14 Outbox / async',(1530,300)),arrow('broker','notify',[(1625,1120),(1625,1190),(200,1190),(200,1120)],'15 События / async',(530,1160)),arrow('notify','patient',[(50,1060),(20,1060),(20,170),(50,170)],'16 Доставка',(30,900)),arrow('portal','platform',[(350,430),(600,430)],'17 HTTPS API',(375,400))]
    render('Task2/context','Целевая C4 Level 1: мобильная платформа','Серый: существующее. Синий: новое / расширяемое. Стрелка: запрос или доставка по подписи.',n,e,1900,1500,['ID интеграций раскрыты в Task2/README.md. Приложение - программный участник, пациент - человек.','LIS владеет результатом, Lab Reservation - квотой; медицинские данные не передаются в push.'])

def flow():
    n=[box('lis',80,140,420,130,['1. Готовый результат в LIS','resultId / patientId / version','Точка начала гарантии'],'#f1f3f6'),box('capture',650,140,460,130,['2. REST capture / сверка','Страница изменений + overlap','API изменений надо согласовать']),box('spool',650,420,460,130,['3. Durable spool + outbox','Payload и cursor одним commit','Повтор захвата безопасен']),box('broker',650,700,460,130,['4. RabbitMQ quorum queues','Persistent + confirms + routing','Отдельные CRM / notify очереди']),box('crm',80,700,420,130,['5. CRM consumer','Inbox + version + upsert + outbox','Ack после commit']),box('app',80,1030,420,130,['6. Приложение читает CRM','REST через платформу / auth','Проверка patient и version']),box('dlq',1250,700,460,130,['DLQ / карантин / оператор','Transient retry: 1/5/30/120/300 с','Затем исправление и replay'],'#fff0cf'),box('push',650,1030,460,130,['7. Уведомления','ResultAvailable после commit','Push не содержит сам результат']),box('recon',1250,140,460,130,['Контроль полноты','LIS manifest ↔ spool ↔ CRM','Повторный захват пропусков'],'#fff0cf')]
    e=[arrow('lis','capture',[(500,200),(650,200)],'REST',(540,170)),arrow('capture','spool',[(880,270),(880,420)],'commit',(895,330)),arrow('spool','broker',[(880,550),(880,700)],'publish / retry',(895,610)),arrow('broker','crm',[(650,765),(500,765)],'async',(535,730)),arrow('crm','app',[(290,830),(290,1030)],'Доступен после commit',(310,915)),arrow('crm','push',[(500,800),(580,800),(580,1090),(650,1090)],'outbox → broker',(575,940)),arrow('broker','dlq',[(1110,765),(1250,765)],'ошибка',(1130,730)),arrow('dlq','spool',[(1480,700),(1480,485),(1110,485)],'контроль replay',(1220,455)),arrow('recon','capture',[(1250,200),(1110,200)],'сверка',(1140,170))]
    render('Task3.1/data-flow','LIS → приложение: восстановимая доставка','Блок-схема. Commit в источнике не равен доставке в CRM; push не равен просмотру пациентом.',n,e,1800,1320,['Отказ CRM не теряет outbox. Повтор после commit/ack безопасен по resultId/version.','Недоступный change API без полного manifest - блокер доказательства полноты.'])

def sequence(path,title,participants,messages,notes):
    W=1900;step=(W-100)/len(participants);n=[]
    for i,(key,label) in enumerate(participants):n.append(box(key,50+i*step,130,step-20,80,[label,'[Участник]']))
    centers={x['key']:x['x']+x['w']/2 for x in n};e=[]
    for i,(a,b,label,reply) in enumerate(messages):
        y=260+i*53;x1=centers[a];x2=centers[b];tw=pdfmetrics.stringWidth(label,'Diagram',19)
        lx=max(40,min((x1+x2-tw)/2,W-tw-40));e.append(arrow(a,b,[(x1,y),(x2,y)],label,(lx,y-27),reply))
    H=260+len(messages)*53+170
    render(path,title,'UML Sequence: сверху вниз. Сплошная стрелка - команда/запрос, пунктирная - ответ.',n,e,W,H,notes,lifelines=True)

def saga():
    sequence('Task3.2/success-sequence','Успех Saga: запись → ДМС → оплата → лаборатория',[('app','Приложение'),('saga','Платформа/Saga'),('sch','Расписание'),('pol','Полис-фасад'),('psp','PSP'),('lab','Lab Reservation'),('mq','RabbitMQ'),('not','Уведомления')],[
      ('app','saga','1 POST booking + Idempotency-Key',False),('saga','app','2 202 operationId; Saga и outbox committed',True),('saga','sch','3 HoldDoctor(sagaId:hold)',False),('sch','saga','4 doctorHoldId',True),('saga','pol','5 CheckCoverage(patient, service, date)',False),('pol','saga','6 VALID + fresh version; сумма определена',True),('saga','psp','7 Pay(merchantOperationId); intent уже committed',False),('psp','saga','8 CONFIRMED + paymentId',True),('saga','lab','9 HoldLab(sagaId:lab-hold)',False),('lab','saga','10 labReservationId',True),('saga','sch','11 ConfirmDoctor(holdId)',False),('sch','saga','12 confirmed',True),('saga','lab','13 ConfirmLab(labReservationId)',False),('lab','saga','14 confirmed',True),('saga','mq','15 COMPLETED + outbox; затем BookingConfirmed',False),('mq','not','16 Доставка события после publish confirm',False),('app','saga','17 GET operationId',False),('saga','app','18 COMPLETED + bookingId + labReservationId',True)],['Saga хранит состояние каждого шага. Неопределённый платёж сверяется, а не списывается заново.','Компенсации и переходы при отказах - Task3.2/README.md; схема показывает только успешный путь.'])

def policy():
    n=[box('app',80,170,350,120,['Мобильная платформа','[Соседняя система]','Проверка ДМС']),box('facade',650,170,480,180,['Полис-фасад [новая система]','[Центральная система]','Локальная read model / version','Общий бюджет 30 RPS в 1С','Circuit Breaker / single-flight']),box('onec',1350,170,350,120,['1С: Полисы [существ.]','[Соседняя система]','Источник истины']),box('operator',650,650,480,120,['Оператор ДМС [человек]','Ручная проверка UNKNOWN','Контролируемое обновление'],'#f1f3f6')]
    e=[arrow('app','facade',[(430,230),(650,230)],'HTTPS REST',(465,195)),arrow('facade','onec',[(1130,230),(1350,230)],'HTTP refresh',(1155,195)),arrow('onec','facade',[(1510,290),(1510,470),(900,470),(900,350)],'Изменения / версии по согласованному контракту',(950,435)),arrow('operator','facade',[(890,650),(890,350)],'HTTPS / аудит',(910,555))]
    render('Task4.1/policy-context','C4 Level 1: фасад разгружает 1С','Read model внутри фасада не показана отдельным контейнером. Потоки запросов и обновлений подписаны.',n,e,1800,940,['Свежее покрытие нужно для финансового решения; stale / null / timeout → UNKNOWN.','1С остаётся master полиса. Экспорт изменений требует согласования и реализации.'])

def auth():
    sequence('Task4.3/authentication','Аутентификация: OIDC Authorization Code + PKCE S256',[('app','Native app'),('browser','Системный браузер'),('idp','IdP'),('gateway','Gateway'),('backend','Backend')],[
      ('app','browser','1 Открыть authorize: state, nonce, code_challenge',False),('browser','idp','2 HTTPS authorize; вход пользователя',False),('idp','app','3 Redirect по зарегистрированной app link: code, state',True),('app','idp','4 HTTPS token: code + code_verifier; без client_secret',False),('idp','app','5 access token + rotated refresh token',True),('app','gateway','6 HTTPS API; Authorization: Bearer access_token',False),('gateway','idp','7 JWKS HTTPS при необходимости; cache ключей',False),('idp','gateway','8 Доверенные публичные ключи',True),('gateway','backend','9 Проверенный subject / scope; защищённый канал',False),('backend','gateway','10 Object authorization по patient binding; ответ',True),('gateway','app','11 Данные только текущего пациента; no-store',True)],['Gateway проверяет подпись/iss/aud/exp, backend - права на объект. ID token не применяется как API token.','Refresh в Keychain/Keystore, access в памяти. Logout отзывает refresh-семейство.'])

if __name__=='__main__':
    context();flow();saga();policy();auth()
