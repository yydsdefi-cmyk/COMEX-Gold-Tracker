"""Report-period freshness. A fresh weekly run must not hide a missing daily run."""
from datetime import datetime,timedelta
from .core import MYT,parse_time

RECOVERY_HOURS=4


def expected_period(kind,now):
    local=now.astimezone(MYT)
    if kind not in ('daily','weekly'):raise ValueError('Unknown report kind')
    day=local.date();hour=8 if kind=='daily' else 10
    if kind=='daily':
        if local.hour<hour:day-=timedelta(days=1)
    else:
        days=(local.weekday()-5)%7
        day-=timedelta(days=days)
        if days==0 and local.hour<hour:day-=timedelta(days=7)
    return datetime(day.year,day.month,day.day,hour,tzinfo=MYT)


def period_state(kind,report_date,generated_at,now):
    target=expected_period(kind,now)
    if generated_at and parse_time(generated_at)>now+timedelta(minutes=5):return 'CLOCK'
    if report_date and report_date>target.date().isoformat():return 'EARLY'
    if report_date==target.date().isoformat():return 'CURRENT'
    return 'PENDING' if now<target+timedelta(hours=RECOVERY_HOURS) else 'OVERDUE'


# Browser equivalent uses UTC getters after a fixed MYT +8h shift. It never uses
# the reader's device timezone, a fetch timestamp, or the other report's clock.
CLOCK_JS=r'''
(()=>{
const H=3600000,D=24*H;
function expected(kind,now){
 if(!['daily','weekly'].includes(kind))throw Error('Unknown report kind');
 const local=new Date(now+8*H),hour=kind==='daily'?8:10;
 let day=Date.UTC(local.getUTCFullYear(),local.getUTCMonth(),local.getUTCDate());
 if(kind==='daily'){if(local.getUTCHours()<hour)day-=D;}
 else{const days=(local.getUTCDay()+1)%7;day-=days*D;if(days===0&&local.getUTCHours()<hour)day-=7*D;}
 return {date:new Date(day).toISOString().slice(0,10),at:day+(hour-8)*H};
}
function assess(kind,date,generated,now){
 const target=expected(kind,now);
 const state=generated&&Date.parse(generated)>now+5*60000?'CLOCK':date&&date>target.date?'EARLY':date===target.date?'CURRENT':now<target.at+4*H?'PENDING':'OVERDUE';
 return {state,expected_date:target.date};
}
function update(){
 for(const el of document.querySelectorAll('.report-clock')){
  const d=el.dataset,r=assess(d.kind,d.reportDate,d.generated,Date.now());el.dataset.state=r.state;
  const name=d.kind==='daily'?'晨报':'周报',prefix=name+' · MYT应有日期 '+r.expected_date+' · ';
  const text={CURRENT:'本期报告已发布；来源质量另列。',PENDING:'本期尚未发布，可能正在排队或补跑；请查看Actions。',OVERDUE:'⚠ 本期仍未发布，已超过4小时补跑窗口；请检查Actions。',EARLY:'当前显示较后日期的手动报告；到目标时刻须重新核对。',CLOCK:'⚠ 生成时间晚于设备时钟；请核对设备时间。'};
  el.textContent=prefix+text[r.state];
 }
}
window.MarketReportClock={expected,assess};update();setInterval(update,60000);
})();
'''
