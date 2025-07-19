-- return base df to train models (no directors and just first genre returned)
with averages as(
    select t.startyear,
    avg(r.averagerating) as averagerating,
    avg(r.numvotes) as numvotes
    from titles t
    left join ratings r on t.title_id = r.title_id
    group by 1
)
select
  t.title_id, t.titletype, t.primarytitle ,
  max(t.isadult) as isadult, max(t.startyear) as startyear, max(t.runtimeminutes) as runtimeminutes,
  case
    when max(r.averagerating) is null then max(a.averagerating)
    else max(r.averagerating)
  end as averagerating,
  case
    when max(r.numvotes) is null then max(a.numvotes)
    else max(r.numvotes)
  end as numvotes,
  min(genre_name) as genre_name
from titles t
left join ratings r on t.title_id = r.title_id
left join titles_genres tg on t.title_id = tg.title_id
left join averages a on t.startyear = a.startyear
group by 1,2,3
